"""Management Service gRPC 클라이언트 (Factory Operator PC 용).

V6 아키텍처 규정:
- PyQt 는 Interface Service(FastAPI :8000) 대신 Management Service(gRPC :50051) 직결
- Interface Service 장애/AWS 이관 시에도 공장 가동 유지
- 기존 api_client.py(HTTP) 는 WebSocket 수신과 비-Mgmt 조회용 (Phase 8 까지 점진 축소)

환경 변수:
    MANAGEMENT_GRPC_HOST   기본 localhost
    MANAGEMENT_GRPC_PORT   기본 50051
    MANAGEMENT_GRPC_TIMEOUT 기본 5.0 (초)

호출은 동기. PyQt GUI 스레드 차단을 피하려면 QThread / QThreadPool 워커에서 호출.

@MX:NOTE: Phase 4 산출물. schedule.py [▶ 생산 시작] 버튼이 본 클라이언트의 start_production 호출.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Iterator

import grpc

# protoc 산출물 (monitoring/app/generated/, Makefile: monitoring/scripts/gen_proto.sh)
from app.generated import management_pb2, management_pb2_grpc

logger = logging.getLogger(__name__)

HOST = os.environ.get("MANAGEMENT_GRPC_HOST", "localhost")
PORT = int(os.environ.get("MANAGEMENT_GRPC_PORT", "50051"))
TIMEOUT = float(os.environ.get("MANAGEMENT_GRPC_TIMEOUT", "5.0"))


# ---------- 사용자 친화 DTO (proto 타입 직접 노출 회피) ----------

@dataclass
class WorkOrderInfo:
    """StartProduction 응답 1건 — UI 에 표시하기 좋은 dict-like."""
    id: int
    order_id: str
    qty: int
    status: str           # QUE / PROC / SUCC / FAIL
    plan_start_iso: str   # ISO 8601 또는 "" (없음)


_STATUS_CODE = {1: "QUE", 2: "PROC", 3: "SUCC", 4: "FAIL"}
_STAGE_CODE = {
    1: "QUE", 2: "MM", 3: "DM", 4: "TR_PP",
    5: "PP", 6: "IP", 7: "TR_LD", 8: "SH",
}


def _wo_from_proto(proto_wo) -> WorkOrderInfo:
    return WorkOrderInfo(
        id=proto_wo.id,
        order_id=proto_wo.order_id,
        qty=proto_wo.qty,
        status=_STATUS_CODE.get(proto_wo.status, "UNSPECIFIED"),
        plan_start_iso=proto_wo.plan_start.iso8601 if proto_wo.plan_start else "",
    )


class ManagementClient:
    """Management Service 호출 래퍼.

    사용 예:
        client = ManagementClient()
        wos = client.start_production(["ORD-2026-006"])
        for wo in wos:
            print(wo.id, wo.order_id, wo.qty, wo.status)
    """

    def __init__(self, host: str = HOST, port: int = PORT, timeout: float = TIMEOUT) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._stub = management_pb2_grpc.ManagementServiceStub(self._channel)

    @property
    def endpoint(self) -> str:
        return f"{self._host}:{self._port}"

    def health(self) -> bool:
        """Mgmt Service 연결 가능 여부."""
        try:
            self._stub.Health(management_pb2.Empty(), timeout=2.0)
            return True
        except grpc.RpcError as e:
            logger.warning("Management health check failed: %s", e)
            return False

    def start_production(self, order_ids: list[str]) -> list[WorkOrderInfo]:
        """승인 주문들을 생산 개시. WorkOrderInfo 리스트 반환.

        Raises:
            grpc.RpcError: 서버 에러/연결 실패 등 (호출자가 try/except 처리)
            ValueError: 빈 order_ids (서버에서 INVALID_ARGUMENT 응답)
        """
        if not order_ids:
            raise ValueError("order_ids 가 비어있습니다")
        req = management_pb2.StartProductionRequest(order_ids=order_ids)
        resp = self._stub.StartProduction(req, timeout=self._timeout)
        return [_wo_from_proto(wo) for wo in resp.work_orders]

    def list_items(self, order_id: str | None = None, limit: int = 100):
        """현재 활성 item 목록. proto Item 메시지 그대로 반환."""
        req = management_pb2.ListItemsRequest(order_id=order_id or "", limit=limit)
        resp = self._stub.ListItems(req, timeout=self._timeout)
        return list(resp.items)

    def watch_items(self, order_id: str | None = None) -> Iterator:
        """Server streaming. 무한 루프 — 별도 QThread 에서 소비."""
        req = management_pb2.WatchItemsRequest(order_id=order_id or "")
        return self._stub.WatchItems(req)

    @staticmethod
    def stage_code_to_label(code: int) -> str:
        """proto enum 정수 → 코드 문자열 (UI 매핑용)."""
        return _STAGE_CODE.get(code, "UNSPECIFIED")

    def close(self) -> None:
        self._channel.close()
