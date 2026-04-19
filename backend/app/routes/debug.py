"""Dev-only debug router — smartcast schema (SPEC-AMR-001 시뮬 stub).

레거시 handoff_acks 테이블은 신규 schema 에서 trans_task_txn 으로 흡수됐다.
이 stub 은 dev UI 의 "SIM Handoff ACK" 버튼이 깨지지 않도록 응답만 유지한다.
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.post("/handoff-ack")
async def simulate_handoff_ack() -> dict:
    """SPEC-AMR-001 호환 stub. trans_task_txn 정식 구현 전까지 응답만 반환."""
    return {
        "released": False,
        "orphan": True,
        "task_id": None,
        "amr_id": None,
        "reason": "smartcast schema migration in progress; handoff sim disabled.",
    }
