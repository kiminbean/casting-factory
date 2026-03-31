from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Alert, Equipment, Order, ProductionMetric
from app.schemas.schemas import AlertResponse, DashboardStats

router = APIRouter(prefix="/api", tags=["alerts", "dashboard"])


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(db: Session = Depends(get_db)):
    """전체 알람 목록을 시각 역순으로 반환."""
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()
    return alerts


@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """알람을 확인 처리."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert


# ---------------------------------------------------------------------------
# Dashboard Stats
# ---------------------------------------------------------------------------

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """대시보드 통계 — 생산 목표 달성률, 가동 로봇, 미처리 주문 등."""
    # 미처리 주문 건수
    pending_statuses = ["pending", "reviewing", "approved"]
    pending_orders = db.query(Order).filter(Order.status.in_(pending_statuses)).count()

    # 금일 알람 수 (미확인)
    today_alarms = db.query(Alert).filter(Alert.acknowledged == False).count()  # noqa: E712

    # 설비 가동률 및 로봇 수
    equipment_total = db.query(Equipment).count()
    equipment_running = db.query(Equipment).filter(Equipment.status == "running").count()
    equipment_utilization = (
        round(equipment_running / equipment_total * 100, 1) if equipment_total > 0 else 0.0
    )

    # 가동 중 로봇(AMR) 수
    active_robots = (
        db.query(Equipment)
        .filter(Equipment.type == "amr", Equipment.status == "running")
        .count()
    )

    # 최신 생산 지표
    latest_metric = (
        db.query(ProductionMetric)
        .order_by(ProductionMetric.date.desc())
        .first()
    )
    today_production = latest_metric.production if latest_metric else 0
    defect_rate = latest_metric.defect_rate if latest_metric else 0.0

    # 금일 완료 주문
    completed_today = db.query(Order).filter(Order.status == "completed").count()

    # 생산 목표 달성률 (생산량 / 목표량 * 100, 목표량 100 기준 임시)
    production_goal = 100
    production_goal_rate = round(today_production / production_goal * 100, 1) if production_goal > 0 else 0.0

    return DashboardStats(
        production_goal_rate=production_goal_rate,
        active_robots=active_robots,
        pending_orders=pending_orders,
        today_alarms=today_alarms,
        today_production=today_production,
        defect_rate=defect_rate,
        equipment_utilization=equipment_utilization,
        completed_today=completed_today,
    )
