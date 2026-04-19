"""SPEC-AMR-001 FR-AMR-01-07: Simulation affordances (HW-less testing).

개발 환경 전용 디버그 엔드포인트. 물리 버튼이나 ESP32 없이도 전체 handoff ACK
downstream 체인(DB insert + AMR FSM 전이 + WebSocket 브로드캐스트)을 재현한다.

라우터 등록 조건: `APP_ENV == "development"` (main.py 에서 gating).
프로덕션 배포 시 자동으로 마운트되지 않으며, 호출 시 404 반환.

실제 버튼과 **동일한 downstream 로직**을 공유한다 — 별도 코드 경로 분기 금지
(simulation flag 는 감사 metadata 에만 기록).

@MX:NOTE: Management Service gRPC ReportHandoffAck 가 Wave 2 에서 구현되면
        이 엔드포인트가 gRPC 클라이언트 호출로 교체됨. 현재는 직접 DB insert +
        WebSocket 브로드캐스트 로 MVP 동작.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import HandoffAck, TransportTask

router = APIRouter(prefix="/api/debug", tags=["debug"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class HandoffAckRequest(BaseModel):
    zone: str = Field(default="postprocessing", description="대상 zone")
    source_device: str = Field(
        default="SIM-KEYBOARD",
        description="이벤트 소스 장치 ID. 실제 버튼은 ESP-CONVEYOR-01, SIM 은 SIM-KEYBOARD",
    )
    amr_id: Optional[str] = Field(default=None, description="override 용. 비워두면 FIFO 로 선택")


class HandoffAckResult(BaseModel):
    accepted: bool
    task_id: Optional[str]
    amr_id: Optional[str]
    zone: str
    orphan: bool
    reason: str
    ack_at: str


@router.post("/handoff-ack", response_model=HandoffAckResult)
async def simulate_handoff_ack(
    payload: HandoffAckRequest,
    db: Session = Depends(get_db),
) -> HandoffAckResult:
    """버튼 ACK 시뮬레이션.

    1. FIFO 로 `WAITING_HANDOFF_ACK` 상태의 transport_task 1 건 선택
    2. `HandoffAck` row insert (orphan 여부 포함)
    3. 매칭된 task 가 있으면 status 를 `handoff_complete` 로 전이
    4. WebSocket `handoff.ack` 브로드캐스트
    """
    # 1. FIFO 대기 태스크 조회
    waiting = (
        db.query(TransportTask)
        .filter(TransportTask.status == "waiting_handoff_ack")
        .order_by(TransportTask.requested_at.asc())
        .first()
    )

    now = datetime.now(timezone.utc)
    orphan = waiting is None
    task_id = waiting.id if waiting else None
    amr_id = payload.amr_id or (waiting.assigned_robot_id if waiting else None)
    reason = "released" if waiting else "orphan_no_waiting_task"

    # 2. 감사 로그 insert
    ack_row = HandoffAck(
        ack_at=now,
        task_id=task_id,
        zone=payload.zone,
        amr_id=amr_id,
        ack_source="debug_endpoint",
        button_device_id=payload.source_device,
        orphan_ack=orphan,
        idempotency_key=f"{payload.source_device}:{int(now.timestamp() * 1000)}:{uuid.uuid4().hex[:8]}",
        extra={"simulated": True, "via": "debug_endpoint"},
    )
    db.add(ack_row)

    # 3. FSM 전이 (orphan 이 아닐 때만)
    if waiting is not None:
        waiting.status = "handoff_complete"
        waiting.completed_at = now.isoformat()

    db.commit()

    # 4. WebSocket 브로드캐스트 (순환 import 회피 위해 지연 import)
    from app.routes.websocket import manager

    await manager.broadcast(
        {
            "type": "handoff.ack",
            "task_id": task_id or "",
            "amr_id": amr_id or "",
            "zone": payload.zone,
            "ack_at": now.isoformat(),
            "orphan": orphan,
            "source": "debug_endpoint",
        }
    )

    return HandoffAckResult(
        accepted=True,
        task_id=task_id,
        amr_id=amr_id,
        zone=payload.zone,
        orphan=orphan,
        reason=reason,
        ack_at=now.isoformat(),
    )


class HandoffNotifyRequest(BaseModel):
    """Management Service gRPC 핸들러 → FastAPI WebSocket 브리지.

    Mgmt Service 와 FastAPI 는 별도 프로세스이므로 gRPC 처리 후 PyQt/Next.js 로
    실시간 전파하려면 IPC 필요. 가장 간단한 방법으로 Mgmt 가 이 내부 엔드포인트에
    POST 하면 FastAPI ConnectionManager 가 WebSocket 으로 브로드캐스트한다.

    보안: localhost 전용 (CORS 로 막히진 않지만 관례상 내부 호출용).
    """
    task_id: str = ""
    amr_id: str = ""
    zone: str = "postprocessing"
    ack_at: str
    orphan: bool = False
    source: str = "management_grpc"


# dev 외에 prod 에서도 Mgmt 가 호출해야 하므로 public 내부 엔드포인트로 분리된 router 도 고려 가능.
# 현재는 debug.py 내에 함께 두되 prod 에선 별도 경로로 이관 예정.
@router.post("/_notify/handoff-ack")
async def notify_handoff_ack(payload: HandoffNotifyRequest):
    """Mgmt Service 가 호출 → WebSocket 브로드캐스트."""
    from app.routes.websocket import manager
    await manager.broadcast(
        {
            "type": "handoff.ack",
            "task_id": payload.task_id,
            "amr_id": payload.amr_id,
            "zone": payload.zone,
            "ack_at": payload.ack_at,
            "orphan": payload.orphan,
            "source": payload.source,
        }
    )
    return {"broadcast": True, "listeners": len(manager.active_connections)}


@router.get("/handoff-acks/recent")
async def recent_handoff_acks(limit: int = 20, db: Session = Depends(get_db)):
    """최근 ACK 이벤트 목록 (디버깅 보조)."""
    if limit > 200:
        raise HTTPException(status_code=400, detail="limit too large (max 200)")

    rows = (
        db.query(HandoffAck)
        .order_by(HandoffAck.ack_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "ack_at": r.ack_at.isoformat() if r.ack_at else None,
            "task_id": r.task_id,
            "zone": r.zone,
            "amr_id": r.amr_id,
            "ack_source": r.ack_source,
            "orphan_ack": r.orphan_ack,
            "button_device_id": r.button_device_id,
            "metadata": r.extra,
        }
        for r in rows
    ]
