"""Dev-only debug router — smartcast schema (SPEC-AMR-001 시뮬 통합).

신규 schema 에서 handoff_acks 테이블은 trans_task_txn 으로 흡수됐다.
시퀀서가 ToPP task 를 MV_DEST → WAIT_HANDOFF 로 정지시켜둔 상태에서,
이 endpoint 가 호출되면 가장 오래된 WAIT_HANDOFF AMR 을 풀어 다음 단계
(WAIT_DLD → SUCC) 로 진행시킨다.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TransStat, TransTaskTxn

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.post("/handoff-ack")
def simulate_handoff_ack(db: Session = Depends(get_db)) -> dict:
    """SPEC-AMR-001 핸드오프 ACK 시뮬.

    가장 오래된 WAIT_HANDOFF 상태의 ToPP trans_task_txn 을 풀어준다.
    실제 사용처: 후처리 작업자가 컨베이어 패널의 A접점 푸시 버튼을 누르는 행위 대체.
    """
    # 가장 오래된 ToPP/PROC 중 trans_stat.cur_stat=WAIT_HANDOFF 1건 픽업
    candidates = (
        db.query(TransTaskTxn)
        .filter(TransTaskTxn.task_type == "ToPP", TransTaskTxn.txn_stat == "PROC")
        .order_by(TransTaskTxn.req_at.asc())
        .all()
    )
    target = None
    target_stat = None
    for t in candidates:
        if not t.trans_id:
            continue
        s = db.get(TransStat, t.trans_id)
        if s and s.cur_stat == "WAIT_HANDOFF":
            target = t
            target_stat = s
            break

    if target is None:
        return {
            "released": False,
            "orphan": True,
            "task_id": None,
            "amr_id": None,
            "reason": "no WAIT_HANDOFF task found (시퀀서 미가동 또는 모든 ToPP 이미 ACK 됨)",
        }

    # cur_stat 을 WAIT_DLD 로 풀어줌 → 다음 polling 에서 SUCC 로 진행
    target_stat.cur_stat = "WAIT_DLD"
    target_stat.updated_at = datetime.now()
    db.commit()
    return {
        "released": True,
        "orphan": False,
        "task_id": target.trans_task_txn_id,
        "amr_id": target.trans_id,
        "item_id": target.item_id,
        "ord_id": target.ord_id,
        "reason": f"WAIT_HANDOFF → WAIT_DLD 전환 (시퀀서가 다음 polling 에 SUCC 처리)",
    }
