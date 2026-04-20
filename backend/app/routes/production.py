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

import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from datetime import datetime, timedelta

from sqlalchemy import func

from app.clients.management import ManagementClient, ManagementUnavailable
from app.database import get_db

logger = logging.getLogger("app.production")

# SPEC-C2 §11.2: Feature flag 는 모듈 import 시점에 상수로 고정.
# Flip 하려면 모든 uvicorn worker 재시작 필수 (per-request env read 금지 — worker race 방지).
_PROXY_START_PRODUCTION = os.environ.get(
    "INTERFACE_PROXY_START_PRODUCTION", "0"
) in ("1", "true", "True", "yes")
logger.info(
    "[INTERFACE-PROXY] start_production proxy = %s (flag pinned at module import)",
    "ON" if _PROXY_START_PRODUCTION else "OFF (legacy DB-direct)",
)
from app.models import (
    Equip,
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
    Zone,
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

def _start_production_legacy(payload: ProductionStartRequest, db: Session) -> dict:
    """Legacy DB-direct 경로 (feature flag OFF 기본값). 2주 유예 후 제거 예정."""
    ord_obj = db.get(Ord, payload.ord_id)
    if not ord_obj:
        raise HTTPException(404, f"ord_id={payload.ord_id} not found")
    if not db.get(Pattern, payload.ord_id):
        raise HTTPException(
            400,
            f"pattern for ord_id={payload.ord_id} not registered. "
            "Register pattern first (핑크 GUI #3) before starting production.",
        )
    db.add(OrdStat(ord_id=payload.ord_id, ord_stat="MFG"))
    new_item = Item(
        ord_id=payload.ord_id,
        equip_task_type="MM",
        trans_task_type=None,
        cur_stat="QUE",
        cur_res="RA1",
    )
    db.add(new_item)
    db.flush()
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


def _start_production_proxy(payload: ProductionStartRequest) -> dict:
    """Management gRPC proxy 경로 (feature flag ON). SPEC-C2 Iteration 3."""
    try:
        result = ManagementClient.get().start_production(payload.ord_id)
    except ValueError as exc:
        msg = str(exc)
        # task_manager 의 "not found" 는 404, "not registered" 는 400 으로 매핑
        if "not found" in msg:
            raise HTTPException(404, msg)
        raise HTTPException(400, msg)
    except ManagementUnavailable as exc:
        raise HTTPException(
            503, f"Management Service unavailable: {exc}"
        )
    return {
        "ord_id": result.ord_id,
        "item_id": result.item_id,
        "equip_task_txn_id": result.equip_task_txn_id,
        "message": result.message,
    }


@router.post("/start")
def start_production(payload: ProductionStartRequest, db: Session = Depends(get_db)) -> dict:
    """발주 생산 시작 — V6 canonical Phase C-2.

    INTERFACE_PROXY_START_PRODUCTION=1 (모듈 import 시점 고정) 이면 Management
    gRPC proxy, 아니면 legacy DB-direct 경로. 응답 shape 은 두 경로 동일.

    선행 조건: pattern 등록 완료 (핑크 GUI #3).
    """
    if _PROXY_START_PRODUCTION:
        return _start_production_proxy(payload)
    return _start_production_legacy(payload, db)


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

# -------------------------------------------------------------------------
# Legacy compat — PyQt/Next.js 가 호출하는 추가 endpoint
# -------------------------------------------------------------------------

@router.get("/equipment")
def list_equipment(db: Session = Depends(get_db)) -> list[dict]:
    """legacy /api/production/equipment 호환. res + equip_stat 최신 합치기."""
    out: list[dict] = []
    res_rows = db.query(Res).all()
    for r in res_rows:
        latest = (
            db.query(EquipStat)
            .filter(EquipStat.res_id == r.res_id)
            .order_by(desc(EquipStat.updated_at))
            .first()
        )
        zone_id = None
        e = db.get(Equip, r.res_id)
        if e:
            zone_id = e.zone_id
        out.append({
            "res_id": r.res_id,
            "res_type": r.res_type,
            "model_nm": r.model_nm,
            "zone_id": zone_id,
            "cur_stat": latest.cur_stat if latest else None,
            "err_msg": latest.err_msg if latest else None,
            "updated_at": latest.updated_at.isoformat() if (latest and latest.updated_at) else None,
        })
    return out


@router.get("/stages")
def list_stages(db: Session = Depends(get_db)) -> list[dict]:
    """legacy /api/production/stages 호환. zone 별 진행중 item 수."""
    out: list[dict] = []
    for z in db.query(Zone).order_by(Zone.zone_id).all():
        # 단순화: 해당 zone 의 res 에 점유된 item 수
        in_progress = (
            db.query(func.count(Item.item_id))
            .filter(Item.cur_stat.in_(["MM", "POUR", "DM", "PP", "INSP", "PA", "PICK", "SHIP", "ToINSP"]))
            .scalar()
            or 0
        )
        out.append({
            "zone_id": z.zone_id,
            "zone_nm": z.zone_nm,
            "in_progress_count": in_progress,
        })
    return out


@router.get("/metrics")
def production_metrics(db: Session = Depends(get_db)) -> list[dict]:
    """legacy /api/production/metrics 호환. 최근 7 일간 일별 item 생성 수."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    out: list[dict] = []
    for d_offset in range(6, -1, -1):
        day = today - timedelta(days=d_offset)
        nxt = day + timedelta(days=1)
        produced = (
            db.query(func.count(Item.item_id))
            .filter(Item.updated_at >= day, Item.updated_at < nxt)
            .scalar()
            or 0
        )
        out.append({
            "date": day.date().isoformat(),
            "produced": produced,
        })
    return out


@router.get("/order-item-progress")
def order_item_progress(db: Session = Depends(get_db)) -> list[dict]:
    """발주별 item 진행 상태 분포 (Next.js / PyQt 차트용)."""
    out: list[dict] = []
    for o in db.query(Ord).all():
        items = db.query(Item).filter(Item.ord_id == o.ord_id).all()
        stat_counts: dict[str, int] = {}
        for it in items:
            key = it.cur_stat or "UNKNOWN"
            stat_counts[key] = stat_counts.get(key, 0) + 1
        out.append({
            "ord_id": o.ord_id,
            "total_items": len(items),
            "by_stat": stat_counts,
        })
    return out


@router.get("/hourly")
def production_hourly(hours: int = 24, db: Session = Depends(get_db)) -> list[dict]:
    """시간대별 생산 — TimescaleDB 있으면 hypertable, 없으면 date_trunc 폴백."""
    from app.services.timescale import hourly_item_production

    return hourly_item_production(db, hours=hours)


@router.get("/weekly")
def production_weekly(weeks: int = 8, db: Session = Depends(get_db)) -> list[dict]:
    """주간 생산 카운트."""
    from app.services.timescale import weekly_item_production

    return weekly_item_production(db, weeks=weeks)


@router.get("/temperature")
def production_temperature() -> list[dict]:
    """legacy 온도 이력 — 센서 미연동, 빈 배열 (Phase H 별도 작업)."""
    return []


@router.get("/live")
def production_live_parameters() -> list[dict]:
    """legacy 실시간 공정 변수 — 센서 미연동, 빈 배열."""
    return []


@router.get("/parameter-history")
def production_parameter_history() -> list[dict]:
    """legacy 공정 변수 이력 — 빈 배열."""
    return []


# -------------------------------------------------------------------------
# RA cur_stat 진행 (Confluence 32342045 open inline comment 대응)
# -------------------------------------------------------------------------

@router.post("/equip-tasks/{txn_id}/advance")
def advance_equip_task(txn_id: int, db: Session = Depends(get_db)) -> dict:
    """equip_task_txn 의 다음 cur_stat 으로 진행 + equip_stat 레코드 INSERT.

    task_type 별 하드코딩 시퀀스는 backend/app/constants/ra_task_stat.py 참조.
    RA: MV_SRC → GRASP → MV_DEST → RELEASE → RETURN → IDLE
    POUR 은 POURING 단계 삽입.
    CONV: ON / OFF / ERR.

    시퀀스 종료 시 (IDLE 반환) txn_stat 을 SUCC 로 자동 전환.
    """
    from app.constants import next_state  # local import to keep top lean

    txn = db.get(EquipTaskTxn, txn_id)
    if not txn:
        raise HTTPException(404, f"equip_task_txn={txn_id} not found")
    if not txn.res_id:
        raise HTTPException(400, "res_id not assigned yet; cannot advance")

    # 최신 cur_stat 조회
    latest = (
        db.query(EquipStat)
        .filter(EquipStat.res_id == txn.res_id)
        .order_by(desc(EquipStat.updated_at))
        .first()
    )
    cur = latest.cur_stat if latest else None
    nxt = next_state(txn.task_type or "", cur)
    if nxt is None:
        raise HTTPException(400, f"no sequence defined for task_type={txn.task_type!r}")

    # equip_stat INSERT
    new_stat = EquipStat(
        res_id=txn.res_id,
        item_id=txn.item_id,
        txn_type=txn.task_type,
        cur_stat=nxt,
    )
    db.add(new_stat)

    # IDLE 도달 시 txn 완료 처리
    if nxt == "IDLE" and txn.txn_stat not in ("SUCC", "FAIL"):
        txn.txn_stat = "SUCC"

    db.commit()
    db.refresh(new_stat)
    return {
        "txn_id": txn_id,
        "res_id": txn.res_id,
        "task_type": txn.task_type,
        "prev_stat": cur,
        "new_stat": nxt,
        "txn_stat": txn.txn_stat,
    }


# -------------------------------------------------------------------------
# Schedule (legacy /api/production/schedule/*) — scheduler 미구현 stub
# -------------------------------------------------------------------------

@router.get("/schedule/jobs")
def production_schedule_jobs() -> list[dict]:
    """legacy — equip_task_txn 스케줄러 별도 구현 전까지 빈 배열."""
    return []


@router.post("/schedule/calculate")
def production_schedule_calculate() -> dict:
    return {"recalculated": 0, "message": "scheduler not yet implemented under smartcast schema"}


@router.post("/schedule/start")
def production_schedule_start() -> dict:
    return {"started": 0, "message": "use POST /api/production/start per ord_id"}


@router.get("/schedule/priority-log")
def production_schedule_priority_log() -> list[dict]:
    return []


# -------------------------------------------------------------------------
# Pink GUI #4
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
