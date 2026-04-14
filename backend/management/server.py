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
        self.robot_executor = RobotExecutor()
        self.execution_monitor = ExecutionMonitor()

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

    # ---------- Health ----------
    def Health(self, request, context):
        return management_pb2.Empty()


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


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    management_pb2_grpc.add_ManagementServiceServicer_to_server(
        ManagementServicer(), server
    )
    management_pb2_grpc.add_ImagePublisherServiceServicer_to_server(
        ImagePublisherServicer(), server
    )
    bind_addr = f"{HOST}:{PORT}"
    server.add_insecure_port(bind_addr)
    server.start()
    logger.info("Management Service listening on %s", bind_addr)

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
