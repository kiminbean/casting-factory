from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Equipment, ProcessStage, ProductionMetric
from app.schemas.schemas import (
    EquipmentResponse,
    ProcessStageResponse,
    ProductionMetricResponse,
)

router = APIRouter(prefix="/api/production", tags=["production"])


class ProcessStageUpdate(BaseModel):
    """공정 단계 부분 업데이트용 스키마."""
    status: Optional[str] = None
    temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    progress: Optional[int] = None
    pressure: Optional[float] = None
    pour_angle: Optional[float] = None
    heating_power: Optional[float] = None
    cooling_progress: Optional[float] = None


@router.get("/stages", response_model=List[ProcessStageResponse])
async def get_process_stages(db: Session = Depends(get_db)):
    """전체 공정 단계 목록을 순서대로 반환."""
    stages = db.query(ProcessStage).order_by(ProcessStage.id).all()
    return stages


@router.patch("/stages/{stage_id}", response_model=ProcessStageResponse)
async def update_process_stage(
    stage_id: int,
    payload: ProcessStageUpdate,
    db: Session = Depends(get_db),
):
    """공정 단계의 상태/온도/진행률 등을 부분 업데이트."""
    stage = db.query(ProcessStage).filter(ProcessStage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail=f"ProcessStage {stage_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)

    db.commit()
    db.refresh(stage)
    return stage


@router.get("/metrics", response_model=List[ProductionMetricResponse])
async def get_production_metrics(db: Session = Depends(get_db)):
    """일별 생산 지표 목록을 날짜순으로 반환."""
    metrics = db.query(ProductionMetric).order_by(ProductionMetric.date).all()
    return metrics


@router.get("/equipment", response_model=List[EquipmentResponse])
async def get_equipment(db: Session = Depends(get_db)):
    """전체 설비 목록 반환."""
    equipment = db.query(Equipment).order_by(Equipment.id).all()
    return equipment
