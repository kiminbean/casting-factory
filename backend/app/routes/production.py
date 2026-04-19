"""Production router — smartcast schema.

엔드포인트:
  POST /api/production/patterns          패턴 등록 (핑크 GUI #3)
  GET  /api/production/patterns          모든 패턴
  GET  /api/production/patterns/{ord}    특정 발주의 패턴 위치
  POST /api/production/start             발주 생산 시작 (핑크 GUI #5)
                                          - 패턴 등록되지 않으면 400
                                          - ord_stat=MFG INSERT + equip_task_txn QUE 생성
  GET  /api/production/items             item 목록 (필터: ord_id)
  GET  /api/production/equip-tasks       equip_task_txn 목록
  GET  /api/production/equip-stats       equip_stat 최신 (res 별)
  GET  /api/production/items/{item}/pp   핑크 GUI #4: item 별 필요 후처리 + 진행상태
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    EquipStat,
    EquipTaskTxn,
    Item,
    Ord,
    OrdPpMap,
    OrdStat,
    Pattern,
    PpOption,
    PpTaskTxn,
    Res,
)
from app.schemas.schemas import (
    EquipStatOut,
    EquipTaskTxnOut,
    ItemOut,
    ItemPpRequirements,
    PatternIn,
    PatternOut,
    PpOptionOut,
    PpTaskTxnOut,
    ProductionStartRequest,
)

router = APIRouter(prefix="/api/production", tags=["production"])


# -------------------------------------------------------------------------
# Pattern (핑크 GUI #3)
# -------------------------------------------------------------------------

@router.post("/patterns", response_model=PatternOut, status_code=201)
def register_pattern(payload: PatternIn, db: Session = Depends(get_db)) -> PatternOut:
    """패턴 위치 등록 (1-6). 발주 1:1 — 동일 ord_id 재등록 시 UPDATE."""
    if not db.get(Ord, payload.ptn_id):
        raise HTTPException(404, f"ord_id={payload.ptn_id} not found")
    existing = db.get(Pattern, payload.ptn_id)
    if existing:
        existing.ptn_loc = payload.ptn_loc
    else:
        existing = Pattern(ptn_id=payload.ptn_id, ptn_loc=payload.ptn_loc)
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return PatternOut.model_validate(existing)


@router.get("/patterns", response_model=List[PatternOut])
def list_patterns(db: Session = Depends(get_db)) -> List[PatternOut]:
    return [PatternOut.model_validate(p) for p in db.query(Pattern).all()]


@router.get("/patterns/{ord_id}", response_model=PatternOut)
def get_pattern(ord_id: int, db: Session = Depends(get_db)) -> PatternOut:
    p = db.get(Pattern, ord_id)
    if not p:
        raise HTTPException(404, f"pattern for ord_id={ord_id} not registered")
    return PatternOut.model_validate(p)


# -------------------------------------------------------------------------
# Production Start (핑크 GUI #5)
# -------------------------------------------------------------------------

@router.post("/start")
def start_production(payload: ProductionStartRequest, db: Session = Depends(get_db)) -> dict:
    """발주 생산 시작.

    선행 조건: pattern 등록 완료. (Pink GUI #5: 패턴 등록 후에만 활성)
    동작:
      1. ord_stat MFG INSERT
      2. RA1 (CAST 구역) 에 MM task QUE 생성
      3. 첫 item INSERT (cur_stat='QUE', equip_task_type='MM')
    """
    ord_obj = db.get(Ord, payload.ord_id)
    if not ord_obj:
        raise HTTPException(404, f"ord_id={payload.ord_id} not found")
    if not db.get(Pattern, payload.ord_id):
        raise HTTPException(
            400,
            f"pattern for ord_id={payload.ord_id} not registered. "
            "Register pattern first (핑크 GUI #3) before starting production.",
        )

    # ord_stat → MFG
    db.add(OrdStat(ord_id=payload.ord_id, ord_stat="MFG"))

    # 첫 item 생성 (생산 라인 진입)
    new_item = Item(
        ord_id=payload.ord_id,
        equip_task_type="MM",
        trans_task_type=None,
        cur_stat="QUE",
        cur_res="RA1",
    )
    db.add(new_item)
    db.flush()

    # equip_task_txn QUE → RA1 / MM
    txn = EquipTaskTxn(
        res_id="RA1",
        task_type="MM",
        txn_stat="QUE",
        item_id=new_item.item_id,
    )
    db.add(txn)
    db.commit()
    db.refresh(new_item)
    db.refresh(txn)

    return {
        "ord_id": payload.ord_id,
        "item_id": new_item.item_id,
        "equip_task_txn_id": txn.txn_id,
        "message": "Production started: RA1/MM task queued.",
    }


# -------------------------------------------------------------------------
# Item / Equipment views
# -------------------------------------------------------------------------

@router.get("/items", response_model=List[ItemOut])
def list_items(
    ord_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[ItemOut]:
    q = db.query(Item)
    if ord_id is not None:
        q = q.filter(Item.ord_id == ord_id)
    return [ItemOut.model_validate(i) for i in q.order_by(desc(Item.updated_at)).all()]


@router.get("/equip-tasks", response_model=List[EquipTaskTxnOut])
def list_equip_tasks(
    res_id: Optional[str] = None, db: Session = Depends(get_db)
) -> List[EquipTaskTxnOut]:
    q = db.query(EquipTaskTxn)
    if res_id:
        q = q.filter(EquipTaskTxn.res_id == res_id)
    return [
        EquipTaskTxnOut.model_validate(t)
        for t in q.order_by(desc(EquipTaskTxn.req_at)).limit(100).all()
    ]


@router.get("/equip-stats", response_model=List[EquipStatOut])
def list_equip_stats(db: Session = Depends(get_db)) -> List[EquipStatOut]:
    """res별 가장 최근 equip_stat. 운영자 모니터링용."""
    # latest per res — subquery 단순화: 각 res 별 최신 1건
    res_ids = [r.res_id for r in db.query(Res).all()]
    out: List[EquipStatOut] = []
    for rid in res_ids:
        latest = (
            db.query(EquipStat)
            .filter(EquipStat.res_id == rid)
            .order_by(desc(EquipStat.updated_at))
            .first()
        )
        if latest:
            out.append(EquipStatOut.model_validate(latest))
    return out


# -------------------------------------------------------------------------
# Pink GUI #4 — item별 필요 후처리 표시
# -------------------------------------------------------------------------

@router.get("/items/{item_id}/pp", response_model=ItemPpRequirements)
def item_pp_requirements(item_id: int, db: Session = Depends(get_db)) -> ItemPpRequirements:
    """item 별 필요한 후처리 옵션 + pp_task_txn 진행상태."""
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(404, f"item_id={item_id} not found")
    pp_opts = (
        db.query(PpOption)
        .join(OrdPpMap, OrdPpMap.pp_id == PpOption.pp_id)
        .filter(OrdPpMap.ord_id == item.ord_id)
        .all()
    )
    txns = (
        db.query(PpTaskTxn)
        .filter(PpTaskTxn.item_id == item_id)
        .order_by(desc(PpTaskTxn.req_at))
        .all()
    )
    return ItemPpRequirements(
        item_id=item_id,
        ord_id=item.ord_id,
        pp_options=[PpOptionOut.model_validate(p) for p in pp_opts],
        pp_task_status=[PpTaskTxnOut.model_validate(t) for t in txns],
    )
