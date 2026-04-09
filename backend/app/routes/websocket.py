import asyncio
import json
import random
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import SessionLocal
from app.models.models import Alert, Equipment, Order, ProcessStage, ProductionMetric, TransportTask

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """활성 WebSocket 연결 관리 및 브로드캐스트."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, default=str))
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


def _get_dashboard_stats() -> dict:
    """DB 조회 후 대시보드 통계 페이로드 생성."""
    db = SessionLocal()
    try:
        pending_statuses = ["pending", "approved"]
        pending_orders = db.query(Order).filter(Order.status.in_(pending_statuses)).count()

        equipment_total = db.query(Equipment).count()
        equipment_running = db.query(Equipment).filter(Equipment.status == "running").count()
        equipment_utilization = (
            round(equipment_running / equipment_total * 100, 1) if equipment_total > 0 else 0.0
        )

        active_robots = (
            db.query(Equipment)
            .filter(Equipment.type == "amr", Equipment.status == "running")
            .count()
        )

        today_alarms = db.query(Alert).filter(Alert.acknowledged == False).count()  # noqa: E712

        latest_metric = (
            db.query(ProductionMetric)
            .order_by(ProductionMetric.date.desc())
            .first()
        )
        today_production = latest_metric.production if latest_metric else 0
        defect_rate = latest_metric.defect_rate if latest_metric else 0.0

        completed_today = db.query(Order).filter(Order.status == "completed").count()

        production_goal = 100
        production_goal_rate = (
            round(today_production / production_goal * 100, 1) if production_goal > 0 else 0.0
        )

        return {
            "type": "dashboard_stats",
            "data": {
                "production_goal_rate": production_goal_rate,
                "active_robots": active_robots,
                "pending_orders": pending_orders,
                "today_alarms": today_alarms,
                "today_production": today_production,
                "defect_rate": defect_rate,
                "equipment_utilization": equipment_utilization,
                "completed_today": completed_today,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


def _get_production_update() -> dict:
    """공정 단계 진행 시뮬레이션 페이로드 생성."""
    db = SessionLocal()
    try:
        stages = db.query(ProcessStage).order_by(ProcessStage.id).all()
        stage_data = []
        for stage in stages:
            # running 상태에서 미세 진행률 변동 시뮬레이션
            if stage.status == "running" and stage.progress < 100:
                stage.progress = min(stage.progress + random.randint(0, 3), 100)
                if stage.temperature is not None and stage.target_temperature is not None:
                    delta = (stage.target_temperature - stage.temperature) * 0.05
                    stage.temperature = round(stage.temperature + delta + random.uniform(-5, 5), 1)
            stage_data.append({
                "id": stage.id,
                "stage": stage.stage,
                "label": stage.label,
                "status": stage.status,
                "temperature": stage.temperature,
                "target_temperature": stage.target_temperature,
                "progress": stage.progress,
                "start_time": stage.start_time,
                "estimated_end": stage.estimated_end,
                "equipment_id": stage.equipment_id,
                "order_id": stage.order_id,
                "job_id": stage.job_id,
                "pressure": stage.pressure,
                "pour_angle": stage.pour_angle,
                "heating_power": stage.heating_power,
                "cooling_progress": stage.cooling_progress,
            })
        db.commit()
        return {
            "type": "production_update",
            "data": stage_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


def _get_alert_update() -> dict:
    """미확인 알람 페이로드 생성."""
    db = SessionLocal()
    try:
        unacked = (
            db.query(Alert)
            .filter(Alert.acknowledged == False)  # noqa: E712
            .order_by(Alert.timestamp.desc())
            .all()
        )
        alert_data = [
            {
                "id": a.id,
                "equipment_id": a.equipment_id,
                "type": a.type,
                "severity": a.severity,
                "error_code": a.error_code,
                "message": a.message,
                "abnormal_value": a.abnormal_value,
                "zone": a.zone,
                "timestamp": a.timestamp if a.timestamp else None,
                "acknowledged": a.acknowledged,
            }
            for a in unacked
        ]
        return {
            "type": "alert_update",
            "data": alert_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    # 연결 직후 초기 데이터 전송
    try:
        initial_stats = _get_dashboard_stats()
        await manager.send_personal(initial_stats, websocket)

        alert_update = _get_alert_update()
        await manager.send_personal(alert_update, websocket)
    except Exception:
        pass

    tick = 0
    try:
        while True:
            await asyncio.sleep(5)
            tick += 1

            # 5초마다 공정 진행 업데이트 브로드캐스트
            production_msg = _get_production_update()
            await manager.broadcast(production_msg)

            # 10초마다 대시보드 통계 브로드캐스트
            if tick % 2 == 0:
                stats_msg = _get_dashboard_stats()
                await manager.broadcast(stats_msg)

            # 15초마다 알람 업데이트 브로드캐스트
            if tick % 3 == 0:
                alert_msg = _get_alert_update()
                await manager.broadcast(alert_msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
