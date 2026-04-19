from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import InspectionRecord, InspectionStandard, SorterLog
from app.schemas.schemas import (
    InspectionRecordResponse,
    InspectionStandardResponse,
    QualityStats,
    SorterLogResponse,
)

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.get("/inspections", response_model=List[InspectionRecordResponse])
async def list_inspections(db: Session = Depends(get_db)):
    """전체 검사 기록을 검사 시각 역순으로 반환."""
    records = (
        db.query(InspectionRecord)
        .order_by(InspectionRecord.inspected_at.desc())
        .all()
    )
    return records


@router.get("/stats", response_model=QualityStats)
async def get_quality_stats(db: Session = Depends(get_db)):
    """품질 통계(합격/불합격, 불량률, 불량 유형별 건수) 반환."""
    records = db.query(InspectionRecord).all()
    total = len(records)
    passed = sum(1 for r in records if r.result == "pass")
    failed = total - passed
    defect_rate = round((failed / total * 100), 2) if total > 0 else 0.0

    defect_types: dict = {}
    defect_type_codes: dict = {}
    inspector_stats: dict = {}

    for record in records:
        if record.result == "fail":
            if record.defect_type:
                defect_types[record.defect_type] = defect_types.get(record.defect_type, 0) + 1
            if record.defect_type_code:
                defect_type_codes[record.defect_type_code] = (
                    defect_type_codes.get(record.defect_type_code, 0) + 1
                )
        if record.inspector_id:
            if record.inspector_id not in inspector_stats:
                inspector_stats[record.inspector_id] = {"total": 0, "passed": 0, "failed": 0}
            inspector_stats[record.inspector_id]["total"] += 1
            if record.result == "pass":
                inspector_stats[record.inspector_id]["passed"] += 1
            else:
                inspector_stats[record.inspector_id]["failed"] += 1

    return QualityStats(
        total=total,
        passed=passed,
        failed=failed,
        defect_rate=defect_rate,
        defect_types=defect_types,
        defect_type_codes=defect_type_codes,
        inspector_stats=inspector_stats,
    )


@router.get("/standards", response_model=List[InspectionStandardResponse])
async def list_inspection_standards(db: Session = Depends(get_db)):
    """전체 검사 기준 목록 반환."""
    standards = db.query(InspectionStandard).all()
    return standards


@router.get("/sorter-logs", response_model=List[SorterLogResponse])
async def list_sorter_logs(db: Session = Depends(get_db)):
    """전체 분류기 로그 목록 반환."""
    logs = db.query(SorterLog).order_by(SorterLog.id.desc()).all()
    return logs
