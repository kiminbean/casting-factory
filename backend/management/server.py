"""Management Service gRPC 서버 (port 50051).

공장 가동 SPOF 제거 목적으로 FastAPI(Interface Service)와 독립 프로세스로 실행된다.
Factory Operator PC(PyQt)가 직접 gRPC 로 호출하며, Interface Service 장애/이관 시에도
공장 운영이 중단되지 않는다.

실행:
    cd backend/management
    python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/management.proto
    python server.py

환경 변수:
    MANAGEMENT_GRPC_HOST  기본 0.0.0.0
    MANAGEMENT_GRPC_PORT  기본 50051
    MANAGEMENT_DB_URL     SQLAlchemy URL (Interface Service 와 동일 DB 공유)

@MX:ANCHOR: V6 Phase 1~8 의 단일 진입점. ManagementServicer + ImagePublisherServicer 등록.
        모든 PyQt gRPC 호출이 본 서버를 통과 — 변경 시 호환성 영향 큼.
@MX:REASON: 5개 service 모듈 + 2개 servicer 의 wiring 책임. RPC 추가 시 servicer 메서드 + proto 동시 갱신 필요.
"""
from __future__ import annotations

import logging
import os
import signal
import sys
from concurrent import futures

import grpc

# `python server.py` 로 직접 실행 가능하도록 sys.path 보장
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_THIS_DIR)  # backend/ — app.models 접근용
for p in (_THIS_DIR, _BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# protoc 로 생성된 모듈 (Makefile: make proto)
import management_pb2  # type: ignore  # noqa: E402
import management_pb2_grpc  # type: ignore  # noqa: E402

from services.task_manager import TaskManager  # noqa: E402
from services.task_allocator import TaskAllocator  # noqa: E402
from services.traffic_manager import TrafficManager  # noqa: E402
from services.robot_executor import RobotExecutor  # noqa: E402
from services.execution_monitor import ExecutionMonitor  # noqa: E402
from services.image_sink import sink as image_sink  # noqa: E402
from services.image_forwarder import ForwarderConfig, ImageForwarder  # noqa: E402
from services.ai_client import AIServerConfig, AIUploader  # noqa: E402
from services.amr_battery import AmrBatteryService  # noqa: E402
from services.amr_state_machine import AmrStateMachine  # noqa: E402

logger = logging.getLogger(__name__)

HOST = os.environ.get("MANAGEMENT_GRPC_HOST", "0.0.0.0")
PORT = int(os.environ.get("MANAGEMENT_GRPC_PORT", "50051"))


class ManagementServicer(management_pb2_grpc.ManagementServiceServicer):
    """gRPC servicer — 5개 내부 모듈을 조율한다.

    실제 비즈니스 로직은 services/ 하위 모듈에 분리되어 있다.
    """

    def __init__(self) -> None:
        self.task_manager = TaskManager()
        self.task_allocator = TaskAllocator()
        self.traffic_manager = TrafficManager()
        # V6 AI 학습 데이터 브리지: Jetson → image_sink → forwarder → AI Server SSH 업로드
        self.image_forwarder = _build_image_forwarder()
        self.execution_monitor = ExecutionMonitor(
            image_forwarder=self.image_forwarder,
        )
        # AMR 배터리 폴링 (SSH → pinkylib)
        self.amr_battery = AmrBatteryService()
        self.amr_battery.start()
        # AMR 운송 상태 머신
        self.amr_state_machine = AmrStateMachine()
        for s in self.amr_battery.get_all():
            self.amr_state_machine.register(s.id)
        # RobotExecutor 에 state_machine 주입
        self.robot_executor = RobotExecutor(state_machine=self.amr_state_machine)

    # ---------- Task Manager ----------
    def StartProduction(self, request, context):
        try:
            wos = self.task_manager.start_production(list(request.order_ids))
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return management_pb2.StartProductionResponse()

        proto_wos = [_work_order_to_proto(wo) for wo in wos]
        return management_pb2.StartProductionResponse(work_orders=proto_wos)

    def ListItems(self, request, context):
        stage_filter = (
            management_pb2.ItemStage.Name(request.stage_filter).replace("ITEM_STAGE_", "")
            if request.stage_filter
            else None
        )
        items = self.task_manager.list_items(
            order_id=request.order_id or None,
            stage=stage_filter if stage_filter and stage_filter != "UNSPECIFIED" else None,
            limit=request.limit or 100,
        )
        return management_pb2.ListItemsResponse(
            items=[_item_to_proto(it) for it in items]
        )

    # ---------- Task Allocator ----------
    def AllocateItem(self, request, context):
        result = self.task_allocator.allocate(request.item_id)
        return management_pb2.AllocateResponse(
            item_id=request.item_id,
            chosen_robot_id=result.robot_id,
            score=result.score,
            rationale=result.rationale,
        )

    # ---------- Traffic Manager ----------
    def PlanRoute(self, request, context):
        # priority 가 RoutePoint.waypoint_id 자리에 임시로 들어올 가능성 회피 — 별도 메타 없으니
        # 단순 plan_with_yield 를 호출 (priority=5 기본). 향후 PlanRouteRequest 에 priority 필드 추가.
        plan = self.traffic_manager.plan_with_yield(
            robot_id=request.robot_id,
            priority=5,
            start=(request.start.x, request.start.y),
            goal=(request.goal.x, request.goal.y),
        )
        proto_points = [
            management_pb2.RoutePoint(x=x, y=y, waypoint_id=wid)
            for (x, y, wid) in plan.points
        ]
        return management_pb2.PlanRouteResponse(
            path=proto_points,
            reserved_edges=plan.reserved_edges,
            estimated_duration_sec=plan.duration_sec,
        )

    # ---------- Robot Executor ----------
    def ExecuteCommand(self, request, context):
        accepted, reason = self.robot_executor.dispatch(
            item_id=request.item_id,
            robot_id=request.robot_id,
            command=request.command,
            payload=request.payload,
        )
        return management_pb2.ExecuteCommandResponse(accepted=accepted, reason=reason)

    # ---------- Execution Monitor (Server Streaming) ----------
    def WatchItems(self, request, context):
        order_filter = request.order_id or None
        for event in self.execution_monitor.stream(order_filter):
            if context.is_active() is False:
                break
            yield event

    def WatchAlerts(self, request, context):
        sev = request.severity_filter or None
        for event in self.execution_monitor.stream_alerts(sev):
            if context.is_active() is False:
                break
            yield event

    # ---------- Robot Status ----------
    def GetRobotStatus(self, request, context):
        entries = []
        for s in self.amr_battery.get_all():
            ctx = self.amr_state_machine.get(s.id)
            entries.append(management_pb2.RobotStatusEntry(
                id=s.id,
                type=management_pb2.ROBOT_TYPE_AMR,
                host=s.host,
                status=s.status,
                battery=s.battery,
                voltage=s.voltage,
                location=s.location,
                task_state=ctx.state.value,
                task_id=ctx.task_id,
                loaded_item=ctx.loaded_item,
            ))
        return management_pb2.GetRobotStatusResponse(robots=entries)

    # ---------- AMR State Transition ----------
    def TransitionAmrState(self, request, context):
        from services.amr_state_machine import TaskState
        try:
            new_state = TaskState(request.new_state)
        except ValueError:
            return management_pb2.TransitionAmrStateResponse(
                accepted=False,
                reason=f"invalid_state: {request.new_state}",
            )
        ok = self.amr_state_machine.transition(
            robot_id=request.robot_id,
            new_state=new_state,
            task_id=request.task_id or None,
            loaded_item=request.loaded_item or None,
        )
        if ok:
            return management_pb2.TransitionAmrStateResponse(
                accepted=True,
                reason=f"{request.robot_id} → {new_state.name}",
            )
        ctx = self.amr_state_machine.get(request.robot_id)
        return management_pb2.TransitionAmrStateResponse(
            accepted=False,
            reason=f"invalid_transition: {ctx.state.name} → {new_state.name}",
        )

    # ---------- Health ----------
    def Health(self, request, context):
        return management_pb2.Empty()

    # ---------- Camera Frames Streaming (Stage B) ----------
    def WatchCameraFrames(self, request, context):
        """image_sink condvar 기반 pub/sub. Jetson push 즉시 yield."""
        cam = request.camera_id or ""
        if not cam:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("camera_id required")
            return
        last_seq = int(request.after_sequence)
        logger.info("WatchCameraFrames subscriber camera=%s after_seq=%d",
                    cam, last_seq)
        while context.is_active():
            frame = image_sink.wait_new(cam, last_seq, timeout=10.0)
            if frame is None:
                continue  # keepalive timeout — 루프 재진입, 클라 여전히 살아있으면 OK
            last_seq = int(frame.get("sequence", 0))
            yield self._frame_to_response(cam, frame)
        logger.info("WatchCameraFrames subscriber closed camera=%s", cam)

    @staticmethod
    def _frame_to_response(cam: str, frame: dict):
        return management_pb2.CameraFrameResponse(
            available=True,
            camera_id=cam,
            encoding=frame.get("encoding", ""),
            width=int(frame.get("width", 0) or 0),
            height=int(frame.get("height", 0) or 0),
            data=frame.get("data", b""),
            sequence=int(frame.get("sequence", 0) or 0),
            captured_at=management_pb2.Timestamp(
                iso8601=frame.get("captured_at", "") or ""
            ),
            received_at=management_pb2.Timestamp(
                iso8601=frame.get("received_at", "") or ""
            ),
        )


# ---------- ORM → proto 변환 헬퍼 ----------

_STAGE_NAME_TO_ENUM = {
    "QUE": 1, "MM": 2, "DM": 3, "TR_PP": 4,
    "PP": 5, "IP": 6, "TR_LD": 7, "SH": 8,
}

_WO_STATUS_TO_ENUM = {"QUE": 1, "PROC": 2, "SUCC": 3, "FAIL": 4}


def _ts(iso_str):
    return management_pb2.Timestamp(iso8601=iso_str or "")


def _item_to_proto(item):
    return management_pb2.Item(
        id=item.id,
        order_id=item.order_id or "",
        cur_stage=_STAGE_NAME_TO_ENUM.get(item.cur_stage or "QUE", 0),
        curr_res=item.curr_res or "",
        insp_id=item.insp_id or 0,
        mfg_at=_ts(item.mfg_at),
    )


def _work_order_to_proto(wo):
    return management_pb2.WorkOrder(
        id=wo.id,
        order_id=wo.order_id or "",
        pattern_id=wo.pattern_id or "",
        qty=wo.qty or 0,
        status=_WO_STATUS_TO_ENUM.get(wo.status or "QUE", 0),
        plan_start=_ts(wo.plan_start),
        act_start=_ts(wo.act_start),
        act_end=_ts(wo.act_end),
    )


class ImagePublisherServicer(management_pb2_grpc.ImagePublisherServiceServicer):
    """HW Image Publishing Service (Jetson) → Server.

    gRPC client streaming. 클라이언트가 ImageFrame 을 연속 보내고, 서버는 마지막 ack 1번 응답.
    """

    def PublishFrames(self, request_iterator, context):
        last_seq = 0
        count = 0
        for frame in request_iterator:
            try:
                image_sink.push(
                    camera_id=frame.camera_id,
                    encoding=frame.encoding,
                    width=frame.width,
                    height=frame.height,
                    data=frame.data,
                    sequence=frame.sequence,
                    captured_at_iso=frame.captured_at.iso8601 if frame.HasField("captured_at") else "",
                )
                last_seq = frame.sequence
                count += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception("ImagePublisher push 실패: %s", exc)
        logger.info("ImagePublisher 스트림 종료: %d frames, last_seq=%d", count, last_seq)
        return management_pb2.ImageAck(
            sequence=last_seq, accepted=True,
            message=f"received {count} frames",
        )


def _build_image_forwarder():
    """ImageForwarder 를 구성. AI Server 설정이 없으면 None 반환 → 훅 비활성."""
    ai_cfg = AIServerConfig.from_env()
    if not ai_cfg.enabled:
        logger.info("image_forwarder 비활성: AI Server 환경변수 미설정")
        return None
    fwd = ImageForwarder(
        config=ForwarderConfig.from_env(),
        sink_latest=image_sink.latest,
        uploader=AIUploader(ai_cfg),
    )
    fwd.start()
    logger.info("image_forwarder 활성: spool=%s batch=%.1fs",
                fwd.cfg.spool_dir, fwd.cfg.batch_interval_sec)
    return fwd


def _load_tls_credentials():
    """V6 S-001: mTLS 환경변수 활성 시 ssl_server_credentials 반환, 아니면 None.

    환경변수:
        MGMT_GRPC_TLS_ENABLED  = 1 면 활성
        MGMT_TLS_CERT_DIR      = cert 디렉터리 (기본 ./certs/)
        MGMT_TLS_SERVER_KEY    = 서버 private key 경로 (기본 ${CERT_DIR}/server.key)
        MGMT_TLS_SERVER_CRT    = 서버 cert 경로 (기본 ${CERT_DIR}/server.crt)
        MGMT_TLS_CA_CRT        = CA cert (클라이언트 검증용, 기본 ${CERT_DIR}/ca.crt)
        MGMT_TLS_REQUIRE_CLIENT_CERT = 1 면 mTLS, 0 이면 server-only TLS (기본 1)
    """
    if os.environ.get("MGMT_GRPC_TLS_ENABLED", "0") not in ("1", "true", "yes"):
        return None
    cert_dir = os.environ.get(
        "MGMT_TLS_CERT_DIR",
        os.path.join(_THIS_DIR, "certs"),
    )
    key_path = os.environ.get("MGMT_TLS_SERVER_KEY", os.path.join(cert_dir, "server.key"))
    crt_path = os.environ.get("MGMT_TLS_SERVER_CRT", os.path.join(cert_dir, "server.crt"))
    ca_path = os.environ.get("MGMT_TLS_CA_CRT", os.path.join(cert_dir, "ca.crt"))

    for p in (key_path, crt_path, ca_path):
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"mTLS 활성화됐으나 cert 파일 없음: {p}\n"
                "scripts/gen_certs.sh 를 먼저 실행하세요."
            )

    with open(key_path, "rb") as f:
        server_key = f.read()
    with open(crt_path, "rb") as f:
        server_crt = f.read()
    with open(ca_path, "rb") as f:
        ca_crt = f.read()

    require_client = os.environ.get("MGMT_TLS_REQUIRE_CLIENT_CERT", "1") in ("1", "true", "yes")
    creds = grpc.ssl_server_credentials(
        [(server_key, server_crt)],
        root_certificates=ca_crt,
        require_client_auth=require_client,
    )
    logger.info(
        "mTLS 활성: cert_dir=%s require_client_auth=%s", cert_dir, require_client,
    )
    return creds


def serve() -> None:
    # WatchItems + WatchAlerts + WatchCameraFrames 등 스트리밍이 워커 점유.
    # 다중 PyQt 클라이언트 + 내부 모니터링 대비 여유있게 32로 확장.
    # keepalive: 죽은 클라이언트(단절된 TCP) 를 빠르게 정리. 구독자 수 가볍게 유지.
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=32),
        options=[
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.min_ping_interval_without_data_ms", 20000),
            ("grpc.http2.max_pings_without_data", 0),
        ],
    )
    management_pb2_grpc.add_ManagementServiceServicer_to_server(
        ManagementServicer(), server
    )
    management_pb2_grpc.add_ImagePublisherServiceServicer_to_server(
        ImagePublisherServicer(), server
    )
    bind_addr = f"{HOST}:{PORT}"

    creds = _load_tls_credentials()
    if creds is not None:
        server.add_secure_port(bind_addr, creds)
        scheme = "TLS"
    else:
        server.add_insecure_port(bind_addr)
        scheme = "INSECURE (V6 S-001: MGMT_GRPC_TLS_ENABLED=1 권장)"

    server.start()
    logger.info("Management Service listening on %s [%s]", bind_addr, scheme)

    # Graceful shutdown
    def _stop(_signum, _frame):
        logger.info("Shutting down...")
        server.stop(grace=5)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    serve()
