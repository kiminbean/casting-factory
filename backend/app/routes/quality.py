"""Quality router — smartcast schema.

엔드포인트:
  GET  /api/quality/inspections           insp_task_txn 목록 (필터: ord_id, item_id)
  GET  /api/quality/summary               핑크 GUI #6: 발주별 GP/DP/미검사 요약
  GET  /api/quality/summary/{ord_id}      특정 발주 요약
  POST /api/quality/inspections/{txn}/result  검사 결과 업데이트 (AI service 콜백)
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InspTaskTxn, Item, Ord
from app.schemas.schemas import InspectionSummary, InspTaskTxnOut

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.get("/inspections", response_model=List[InspTaskTxnOut])
def list_inspections(
    ord_id: Optional[int] = None,
    item_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[InspTaskTxnOut]:
    q = db.query(InspTaskTxn)
    if item_id is not None:
        q = q.filter(InspTaskTxn.item_id == item_id)
    if ord_id is not None:
        q = q.join(Item, Item.item_id == InspTaskTxn.item_id).filter(Item.ord_id == ord_id)
    return [
        InspTaskTxnOut.model_validate(t)
        for t in q.order_by(desc(InspTaskTxn.req_at)).limit(200).all()
    ]


@router.get("/summary", response_model=List[InspectionSummary])
def inspection_summary_all(db: Session = Depends(get_db)) -> List[InspectionSummary]:
    """Pink GUI #6: 발주별 검사 요약.

    각 ord_id 의 item 총수 / 검사 완료 / 양품(GP) / 불량(DP) / 미검사 카운트.
    """
    return _build_summaries(db, ord_id=None)


@router.get("/summary/{ord_id}", response_model=InspectionSummary)
def inspection_summary_one(ord_id: int, db: Session = Depends(get_db)) -> InspectionSummary:
    rows = _build_summaries(db, ord_id=ord_id)
    if not rows:
        if not db.get(Ord, ord_id):
            raise HTTPException(404, f"ord_id={ord_id} not found")
        return InspectionSummary(
            ord_id=ord_id,
            total_items=0, inspected=0, good_count=0, defective_count=0, pending_count=0,
        )
    return rows[0]


def _build_summaries(db: Session, ord_id: Optional[int]) -> List[InspectionSummary]:
    """Item count + inspection result count grouped by ord_id."""
    base = (
        db.query(
            Item.ord_id.label("ord_id"),
            func.count(Item.item_id).label("total_items"),
            func.count(InspTaskTxn.txn_id).filter(InspTaskTxn.result.isnot(None)).label("inspected"),
            func.count(InspTaskTxn.txn_id).filter(InspTaskTxn.result.is_(True)).label("good_count"),
            func.count(InspTaskTxn.txn_id).filter(InspTaskTxn.result.is_(False)).label("defective_count"),
        )
        .outerjoin(InspTaskTxn, InspTaskTxn.item_id == Item.item_id)
        .group_by(Item.ord_id)
    )
    if ord_id is not None:
        base = base.filter(Item.ord_id == ord_id)
    out: List[InspectionSummary] = []
    for r in base.all():
        pending = max(0, (r.total_items or 0) - (r.inspected or 0))
        out.append(InspectionSummary(
            ord_id=r.ord_id,
            total_items=r.total_items or 0,
            inspected=r.inspected or 0,
            good_count=r.good_count or 0,
            defective_count=r.defective_count or 0,
            pending_count=pending,
        ))
    return out


@router.post("/inspections/{txn_id}/result", response_model=InspTaskTxnOut)
def update_inspection_result(
    txn_id: int,
    result: bool = Query(..., description="True=GP, False=DP"),
    db: Session = Depends(get_db),
) -> InspTaskTxnOut:
    """AI 검사 결과 업데이트. item.is_defective 도 동시 갱신."""
    txn = db.get(InspTaskTxn, txn_id)
    if not txn:
        raise HTTPException(404, f"insp_task_txn={txn_id} not found")
    txn.result = result
    txn.txn_stat = "SUCC"
    if txn.item_id:
        item = db.get(Item, txn.item_id)
        if item:
            item.is_defective = not result  # GP=False (불량 아님), DP=True (불량)
    db.commit()
    db.refresh(txn)
    return InspTaskTxnOut.model_validate(txn)
