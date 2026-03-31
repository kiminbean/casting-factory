from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Equipment, TransportRequest
from app.schemas.schemas import (
    EquipmentResponse,
    TransportRequestCreate,
    TransportRequestResponse,
    TransportStatusUpdate,
)

router = APIRouter(prefix="/api/logistics", tags=["logistics"])


@router.get("/transports", response_model=List[TransportRequestResponse])
async def list_transports(db: Session = Depends(get_db)):
    """Return all transport requests sorted by request time descending."""
    transports = (
        db.query(TransportRequest)
        .order_by(TransportRequest.requested_at.desc())
        .all()
    )
    return transports


@router.post("/transports", response_model=TransportRequestResponse, status_code=201)
async def create_transport(
    payload: TransportRequestCreate, db: Session = Depends(get_db)
):
    """Create a new transport request."""
    transport = TransportRequest(**payload.model_dump())
    db.add(transport)
    db.commit()
    db.refresh(transport)
    return transport


@router.patch("/transports/{transport_id}/status", response_model=TransportRequestResponse)
async def update_transport_status(
    transport_id: str,
    payload: TransportStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the status of an existing transport request."""
    transport = db.query(TransportRequest).filter(TransportRequest.id == transport_id).first()
    if not transport:
        raise HTTPException(status_code=404, detail=f"Transport {transport_id} not found")

    transport.status = payload.status
    if payload.assigned_amr_id is not None:
        transport.assigned_amr_id = payload.assigned_amr_id
    if payload.failure_reason is not None:
        transport.failure_reason = payload.failure_reason

    db.commit()
    db.refresh(transport)
    return transport


@router.get("/equipment/amr", response_model=List[EquipmentResponse])
async def get_amr_status(db: Session = Depends(get_db)):
    """Return status of all AMR (Autonomous Mobile Robot) units."""
    amrs = (
        db.query(Equipment)
        .filter(Equipment.type == "amr")
        .order_by(Equipment.id)
        .all()
    )
    return amrs
