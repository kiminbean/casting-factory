from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Equipment, ProcessStage, ProductionMetric
from app.schemas.schemas import (
    EquipmentResponse,
    EquipmentStatusUpdate,
    ProcessStageResponse,
    ProductionMetricResponse,
)

router = APIRouter(prefix="/api/production", tags=["production"])


@router.get("/stages", response_model=List[ProcessStageResponse])
async def get_process_stages(db: Session = Depends(get_db)):
    """Return all process stages in order."""
    stages = db.query(ProcessStage).order_by(ProcessStage.id).all()
    return stages


@router.get("/equipment", response_model=List[EquipmentResponse])
async def get_equipment(db: Session = Depends(get_db)):
    """Return all equipment."""
    equipment = db.query(Equipment).order_by(Equipment.id).all()
    return equipment


@router.patch("/equipment/{equipment_id}/status", response_model=EquipmentResponse)
async def update_equipment_status(
    equipment_id: str,
    payload: EquipmentStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the operational status of a piece of equipment."""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
    equipment.status = payload.status
    db.commit()
    db.refresh(equipment)
    return equipment


@router.get("/metrics", response_model=List[ProductionMetricResponse])
async def get_production_metrics(db: Session = Depends(get_db)):
    """Return all production metrics ordered by date."""
    metrics = db.query(ProductionMetric).order_by(ProductionMetric.date).all()
    return metrics
