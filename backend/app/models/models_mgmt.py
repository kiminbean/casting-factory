"""Management Service 전용 legacy public-schema 테이블 (SPEC-C3).

models_legacy.py 에서 필요한 3개 모델만 분리 import — 전체 import 시 legacy Item/Order 가
smartcast Item/Ord 와 Base.metadata 에서 충돌하는 문제 회피.

- Alert (public.alerts) — execution_monitor 의 SLA 타임아웃 기록
- TransportTask (public.transport_tasks) — SPEC-AMR-001 이송 작업
- HandoffAck (public.handoff_acks) — SPEC-AMR-001 후처리존 인수인계 이벤트

향후 smartcast 로 완전 이관 시 (SPEC-C5 가칭) 본 파일 제거 예정.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    """알림 (public.alerts)."""

    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    equipment_id = Column(String, nullable=True, default="")
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="info")
    error_code = Column(String, nullable=True, default="")
    message = Column(String, nullable=False)
    abnormal_value = Column(String, nullable=True, default="")
    zone = Column(String, nullable=True)
    timestamp = Column(String, nullable=False)
    resolved_at = Column(String, nullable=True)
    acknowledged = Column(Boolean, nullable=False, default=False)


class TransportTask(Base):
    """이송 작업 (public.transport_tasks)."""

    __tablename__ = "transport_tasks"

    id = Column(String, primary_key=True, index=True)
    from_name = Column(String, nullable=False)
    from_coord = Column(String, nullable=True, default="")
    to_name = Column(String, nullable=False)
    to_coord = Column(String, nullable=True, default="")
    item_id = Column(String, nullable=True, default="")
    item_name = Column(String, nullable=True, default="")
    quantity = Column(Integer, nullable=False, default=1)
    priority = Column(String, nullable=False, default="medium")
    status = Column(String, nullable=False, default="unassigned")
    assigned_robot_id = Column(String, nullable=True, default="")
    requested_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)


class HandoffAck(Base):
    """후처리존 인수인계 확인 이벤트 (public.handoff_acks) — SPEC-AMR-001.

    Management Service 가 ESP32 버튼 이벤트 수신 시 AMR FSM 전이와 함께 INSERT.
    TimescaleDB hypertable 화는 차후.
    """

    __tablename__ = "handoff_acks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ack_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, index=True)
    task_id = Column(
        String,
        ForeignKey("transport_tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    zone = Column(String, nullable=False, index=True)
    amr_id = Column(String, nullable=True)
    ack_source = Column(String, nullable=False)          # 'esp32_button' | 'debug_endpoint' | 'gui_override'
    operator_id = Column(String, nullable=True)
    button_device_id = Column(String, nullable=True)
    orphan_ack = Column(Boolean, nullable=False, default=False)
    idempotency_key = Column(String, nullable=True)
    extra = Column("metadata", JSONB, nullable=True)     # 'metadata' 충돌 회피
