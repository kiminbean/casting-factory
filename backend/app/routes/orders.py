"""Orders router — smartcast schema.

엔드포인트:
  POST   /api/orders                    발주 생성 (ord + ord_detail + ord_pp_map + RCVD txn/stat)
  GET    /api/orders                    발주 목록 (관리자 조회)
  GET    /api/orders/{ord_id}           발주 단건 (detail + pp_options + latest_stat)
  GET    /api/orders/lookup?email=...   고객 발주 조회 (핑크 GUI #1)
  POST   /api/orders/{ord_id}/status    발주 상태 전이 (RCVD→APPR→...)

  GET    /api/products                  표준 제품 목록 (카테고리/옵션 join)
  GET    /api/categories                카테고리 마스터
  GET    /api/pp-options                후처리 마스터
  GET    /api/equip-load-spec           하중 등급별 정밀 제어 수치 (legacy load_classes 대체)
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import (
    Category,
    EquipLoadSpec,
    Ord,
    OrdDetail,
    OrdPpMap,
    OrdStat,
    OrdTxn,
    PpOption,
    Product,
    UserAccount,
)
from app.schemas.schemas import (
    CategoryOut,
    OrdCreate,
    OrdFull,
    OrdStatOut,
    PpOptionOut,
    ProductOut,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])
products_router = APIRouter(prefix="/api", tags=["products"])
load_classes_router = APIRouter(prefix="/api", tags=["load-classes"])


# -------------------------------------------------------------------------
# helpers
# -------------------------------------------------------------------------

def _to_full(db: Session, ord_obj: Ord) -> OrdFull:
    """Ord ORM → OrdFull (detail + pp_options + latest_stat)."""
    pp_options = (
        db.query(PpOption)
        .join(OrdPpMap, OrdPpMap.pp_id == PpOption.pp_id)
        .filter(OrdPpMap.ord_id == ord_obj.ord_id)
        .all()
    )
    latest_stat = (
        db.query(OrdStat)
        .filter(OrdStat.ord_id == ord_obj.ord_id)
        .order_by(desc(OrdStat.updated_at))
        .first()
    )
    return OrdFull(
        ord_id=ord_obj.ord_id,
        user_id=ord_obj.user_id,
        created_at=ord_obj.created_at,
        detail=ord_obj.detail,
        pp_options=[PpOptionOut.model_validate(p) for p in pp_options],
        latest_stat=latest_stat.ord_stat if latest_stat else "RCVD",
    )


# -------------------------------------------------------------------------
# Order CRUD
# -------------------------------------------------------------------------

@router.post("", response_model=OrdFull, status_code=201)
def create_order(payload: OrdCreate, db: Session = Depends(get_db)) -> OrdFull:
    """발주 생성 — 고객 측 폼.

    Pink GUI #2: 비고란 제거됨 (OrdDetailIn 에 비고 필드 없음).
    """
    user = db.get(UserAccount, payload.user_id)
    if not user:
        raise HTTPException(404, f"user_id={payload.user_id} not found")

    new_ord = Ord(user_id=payload.user_id)
    db.add(new_ord)
    db.flush()  # ord_id 확보

    detail = OrdDetail(ord_id=new_ord.ord_id, **payload.detail.model_dump(exclude_none=True))
    db.add(detail)

    for pp_id in payload.pp_ids:
        db.add(OrdPpMap(ord_id=new_ord.ord_id, pp_id=pp_id))

    # 초기 상태 RCVD (txn + stat 동시 INSERT)
    db.add(OrdTxn(ord_id=new_ord.ord_id, txn_type="RCVD"))
    db.add(OrdStat(ord_id=new_ord.ord_id, user_id=payload.user_id, ord_stat="RCVD"))
    db.commit()
    db.refresh(new_ord)
    return _to_full(db, new_ord)


@router.get("", response_model=List[OrdFull])
def list_orders(db: Session = Depends(get_db)) -> List[OrdFull]:
    """발주 목록 — 관리자용."""
    rows = db.query(Ord).options(selectinload(Ord.detail)).order_by(desc(Ord.created_at)).all()
    return [_to_full(db, o) for o in rows]


@router.get("/lookup", response_model=List[OrdFull])
def lookup_orders_by_email(
    email: str = Query(..., min_length=1), db: Session = Depends(get_db)
) -> List[OrdFull]:
    """이메일로 고객 발주 조회.

    Pink GUI #1: 결과 비어있어도 200 + 빈 배열로 반환
    (frontend 에서 빈 배열 → "발주 기록 없음" 표시 + 다음 페이지 차단).
    """
    user = db.query(UserAccount).filter(UserAccount.email == email).first()
    if not user:
        return []
    rows = (
        db.query(Ord)
        .options(selectinload(Ord.detail))
        .filter(Ord.user_id == user.user_id)
        .order_by(desc(Ord.created_at))
        .all()
    )
    return [_to_full(db, o) for o in rows]


@router.get("/{ord_id}", response_model=OrdFull)
def get_order(ord_id: int, db: Session = Depends(get_db)) -> OrdFull:
    o = db.get(Ord, ord_id)
    if not o:
        raise HTTPException(404, f"ord_id={ord_id} not found")
    return _to_full(db, o)


@router.post("/{ord_id}/status", response_model=OrdStatOut)
def update_order_status(
    ord_id: int,
    new_stat: str = Query(..., description="RCVD/APPR/MFG/DONE/SHIP/COMP/REJT/CNCL"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> OrdStatOut:
    """발주 상태 전이 (관리자)."""
    o = db.get(Ord, ord_id)
    if not o:
        raise HTTPException(404, f"ord_id={ord_id} not found")
    valid = {"RCVD", "APPR", "MFG", "DONE", "SHIP", "COMP", "REJT", "CNCL"}
    if new_stat not in valid:
        raise HTTPException(400, f"invalid status: {new_stat}")
    stat = OrdStat(ord_id=ord_id, user_id=user_id, ord_stat=new_stat)
    db.add(stat)
    db.commit()
    db.refresh(stat)
    return OrdStatOut.model_validate(stat)


# -------------------------------------------------------------------------
# Product / Category / PpOption / EquipLoadSpec
# -------------------------------------------------------------------------

@products_router.get("/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)) -> List[ProductOut]:
    return [ProductOut.model_validate(p) for p in db.query(Product).all()]


@products_router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> List[CategoryOut]:
    return [CategoryOut.model_validate(c) for c in db.query(Category).all()]


@products_router.get("/pp-options", response_model=List[PpOptionOut])
def list_pp_options(db: Session = Depends(get_db)) -> List[PpOptionOut]:
    return [PpOptionOut.model_validate(p) for p in db.query(PpOption).all()]


@load_classes_router.get("/equip-load-spec", tags=["load-classes"])
def list_load_specs(db: Session = Depends(get_db)) -> list[dict]:
    """legacy /api/load-classes 의 후속. 하중 등급별 정밀 제어 수치 반환."""
    rows = db.query(EquipLoadSpec).all()
    return [
        {
            "load_spec_id": r.load_spec_id,
            "load_class": r.load_class,
            "press_f": float(r.press_f) if r.press_f is not None else None,
            "press_t": float(r.press_t) if r.press_t is not None else None,
            "tol_val": float(r.tol_val) if r.tol_val is not None else None,
        }
        for r in rows
    ]
