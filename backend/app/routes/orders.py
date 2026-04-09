from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import LoadClass, Order, OrderDetail, Product
from app.schemas.schemas import (
    LoadClassResponse,
    OrderCreate,
    OrderDetailCreate,
    OrderDetailResponse,
    OrderResponse,
    OrderStatusUpdate,
    OrderUpdate,
    ProductResponse,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])
products_router = APIRouter(prefix="/api/products", tags=["products"])
load_classes_router = APIRouter(prefix="/api/load-classes", tags=["load-classes"])


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@router.get("", response_model=List[OrderResponse])
async def list_orders(
    db: Session = Depends(get_db),
    email: Optional[str] = Query(
        None, description="이메일 정확 일치 필터 (/customer/lookup 에서 사용)"
    ),
):
    """주문 목록 (생성일 역순). email 파라미터 주면 해당 이메일 주문만 반환."""
    query = db.query(Order)
    if email:
        # 공백 제거 + 대소문자 무시 비교
        normalized = email.strip().lower()
        query = query.filter(func.lower(Order.email) == normalized)
    return query.order_by(Order.created_at.desc()).all()


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """새 주문 생성."""
    existing = db.query(Order).filter(Order.id == payload.id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Order {payload.id} already exists")
    order = Order(**payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    """주문 상태 변경."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    order.status = payload.status
    order.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
):
    """주문 필드 부분 수정 (견적 금액, 확정 납기, 비고)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


# ---------------------------------------------------------------------------
# Order Details (품목 상세)
# ---------------------------------------------------------------------------

@router.get("/{order_id}/details", response_model=List[OrderDetailResponse])
async def get_order_details(order_id: str, db: Session = Depends(get_db)):
    """특정 주문의 품목 상세 목록 반환."""
    # 주문 존재 여부 확인
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    details = (
        db.query(OrderDetail)
        .filter(OrderDetail.order_id == order_id)
        .all()
    )
    return details


@router.post("/{order_id}/details", response_model=OrderDetailResponse, status_code=201)
async def add_order_detail(
    order_id: str,
    payload: OrderDetailCreate,
    db: Session = Depends(get_db),
):
    """주문에 품목 상세 추가."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    # payload의 order_id를 경로 파라미터로 덮어쓰기
    data = payload.model_dump()
    data["order_id"] = order_id
    detail = OrderDetail(**data)
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail


# ---------------------------------------------------------------------------
# Products (제품 마스터)
# ---------------------------------------------------------------------------

@products_router.get("", response_model=List[ProductResponse])
async def list_products(db: Session = Depends(get_db)):
    """전체 제품 목록 반환. JSON 컬럼은 ProductResponse.from_orm_model 에서 파싱."""
    products = db.query(Product).order_by(Product.name).all()
    return [ProductResponse.from_orm_model(p) for p in products]


# ---------------------------------------------------------------------------
# Load classes (EN 124 하중 등급 마스터)
# ---------------------------------------------------------------------------

@load_classes_router.get("", response_model=List[LoadClassResponse])
async def list_load_classes(db: Session = Depends(get_db)):
    """EN 124 하중 등급 마스터 전체 (display_order 오름차순)."""
    return db.query(LoadClass).order_by(LoadClass.display_order).all()
