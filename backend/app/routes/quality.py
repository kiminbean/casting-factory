from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import InspectionRecord
from app.schemas.schemas import InspectionRecordCreate, InspectionRecordResponse, QualityStats

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.get("/inspections", response_model=List[InspectionRecordResponse])
async def list_inspections(db: Session = Depends(get_db)):
    """Return all inspection records sorted by inspection time descending."""
    records = (
        db.query(InspectionRecord)
        .order_by(InspectionRecord.inspected_at.desc())
        .all()
    )
    return records


@router.post("/inspections", response_model=InspectionRecordResponse, status_code=201)
async def create_inspection(
    payload: InspectionRecordCreate, db: Session = Depends(get_db)
):
    """Create a new inspection record."""
    record = InspectionRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/stats", response_model=QualityStats)
async def get_quality_stats(db: Session = Depends(get_db)):
    """Return aggregated quality statistics."""
    records = db.query(InspectionRecord).all()
    total = len(records)
    passed = sum(1 for r in records if r.result == "pass")
    failed = total - passed
    defect_rate = round((failed / total * 100), 2) if total > 0 else 0.0

    defect_types: dict = {}
    for record in records:
        if record.result == "fail" and record.defect_type:
            defect_types[record.defect_type] = defect_types.get(record.defect_type, 0) + 1

    return QualityStats(
        total=total,
        passed=passed,
        failed=failed,
        defect_rate=defect_rate,
        defect_types=defect_types,
    )
