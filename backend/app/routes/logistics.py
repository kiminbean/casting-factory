from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import OutboundOrder, TransportTask, WarehouseRack
from app.schemas.schemas import (
    OutboundOrderResponse,
    TransportStatusUpdate,
    TransportTaskCreate,
    TransportTaskResponse,
    WarehouseRackResponse,
)

router = APIRouter(prefix="/api/logistics", tags=["logistics"])


# ---------------------------------------------------------------------------
# Transport Tasks (이송 작업)
# ---------------------------------------------------------------------------

@router.get("/tasks", response_model=List[TransportTaskResponse])
async def list_transport_tasks(db: Session = Depends(get_db)):
    """전체 이송 작업 목록을 요청 시각 역순으로 반환."""
    tasks = (
        db.query(TransportTask)
        .order_by(TransportTask.requested_at.desc())
        .all()
    )
    return tasks


@router.post("/tasks", response_model=TransportTaskResponse, status_code=201)
async def create_transport_task(
    payload: TransportTaskCreate, db: Session = Depends(get_db)
):
    """새 이송 작업 생성."""
    existing = db.query(TransportTask).filter(TransportTask.id == payload.id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"TransportTask {payload.id} already exists")
    task = TransportTask(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/status", response_model=TransportTaskResponse)
async def update_transport_task_status(
    task_id: str,
    payload: TransportStatusUpdate,
    db: Session = Depends(get_db),
):
    """이송 작업 상태 변경 및 배정 로봇 업데이트."""
    task = db.query(TransportTask).filter(TransportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"TransportTask {task_id} not found")

    task.status = payload.status
    if payload.assigned_robot_id is not None:
        task.assigned_robot_id = payload.assigned_robot_id

    db.commit()
    db.refresh(task)
    return task


# ---------------------------------------------------------------------------
# Warehouse (창고 랙)
# ---------------------------------------------------------------------------

@router.get("/warehouse", response_model=List[WarehouseRackResponse])
async def list_warehouse_racks(db: Session = Depends(get_db)):
    """전체 창고 랙 목록 반환."""
    racks = db.query(WarehouseRack).order_by(WarehouseRack.zone, WarehouseRack.rack_number).all()
    return racks


# ---------------------------------------------------------------------------
# Outbound Orders (출고 지시)
# ---------------------------------------------------------------------------

@router.get("/outbound-orders", response_model=List[OutboundOrderResponse])
async def list_outbound_orders(db: Session = Depends(get_db)):
    """전체 출고 지시서 목록을 생성일 역순으로 반환."""
    orders = (
        db.query(OutboundOrder)
        .order_by(OutboundOrder.created_at.desc())
        .all()
    )
    return orders


@router.patch("/outbound-orders/{order_id}/complete", response_model=OutboundOrderResponse)
async def complete_outbound_order(order_id: str, db: Session = Depends(get_db)):
    """출고 지시서를 완료 처리."""
    order = db.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"OutboundOrder {order_id} not found")
    order.completed = True
    db.commit()
    db.refresh(order)
    return order
