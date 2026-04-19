"""Logistics router — smartcast schema.

엔드포인트:
  GET  /api/logistics/trans-tasks       trans_task_txn 목록
  GET  /api/logistics/trans-stats       AMR 별 최신 상태 (배터리 포함)
  GET  /api/logistics/locations         3개 location stat (chg/strg/ship)
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ChgLocationStat,
    ShipLocationStat,
    StrgLocationStat,
    Trans,
    TransStat,
    TransTaskTxn,
)
from app.schemas.schemas import TransStatOut, TransTaskTxnOut

router = APIRouter(prefix="/api/logistics", tags=["logistics"])


@router.get("/trans-tasks", response_model=List[TransTaskTxnOut])
def list_trans_tasks(
    trans_id: Optional[str] = None, db: Session = Depends(get_db)
) -> List[TransTaskTxnOut]:
    q = db.query(TransTaskTxn)
    if trans_id:
        q = q.filter(TransTaskTxn.trans_id == trans_id)
    return [
        TransTaskTxnOut.model_validate(t)
        for t in q.order_by(desc(TransTaskTxn.req_at)).limit(100).all()
    ]


@router.get("/trans-stats", response_model=List[TransStatOut])
def list_trans_stats(db: Session = Depends(get_db)) -> List[TransStatOut]:
    """모든 AMR 의 최신 상태."""
    out: List[TransStatOut] = []
    for t in db.query(Trans).all():
        s = db.get(TransStat, t.res_id)
        if s:
            out.append(TransStatOut.model_validate(s))
    return out


@router.get("/locations")
def list_locations(db: Session = Depends(get_db)) -> dict:
    """3개 location stat 통합 응답 (chg / strg / ship)."""
    return {
        "chg": [
            {
                "loc_id": r.loc_id,
                "row": r.loc_row,
                "col": r.loc_col,
                "status": r.status,
                "res_id": r.res_id,
            }
            for r in db.query(ChgLocationStat).order_by(ChgLocationStat.loc_row, ChgLocationStat.loc_col).all()
        ],
        "strg": [
            {
                "loc_id": r.loc_id,
                "row": r.loc_row,
                "col": r.loc_col,
                "status": r.status,
                "item_id": r.item_id,
            }
            for r in db.query(StrgLocationStat).order_by(StrgLocationStat.loc_row, StrgLocationStat.loc_col).all()
        ],
        "ship": [
            {
                "loc_id": r.loc_id,
                "row": r.loc_row,
                "col": r.loc_col,
                "status": r.status,
                "ord_id": r.ord_id,
                "item_id": r.item_id,
            }
            for r in db.query(ShipLocationStat).order_by(ShipLocationStat.loc_row, ShipLocationStat.loc_col).all()
        ],
    }
