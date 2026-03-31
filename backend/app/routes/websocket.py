import asyncio
import json
import random
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import SessionLocal
from app.models.models import Alert, Equipment, Order, ProcessStage, ProductionMetric

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

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
    """Query the database and build a dashboard stats payload."""
    db = SessionLocal()
    try:
        total_orders = db.query(Order).count()
        active_statuses = ["pending", "approved", "in_production", "reviewing"]
        active_orders = db.query(Order).filter(Order.status.in_(active_statuses)).count()

        equipment_total = db.query(Equipment).count()
        equipment_running = db.query(Equipment).filter(Equipment.status == "running").count()

        pending_transports = 0
        try:
            from app.models.models import TransportRequest
            pending_transports = (
                db.query(TransportRequest)
                .filter(TransportRequest.status.in_(["requested", "assigned", "moving_to_dest"]))
                .count()
            )
        except Exception:
            pass

        active_alerts = db.query(Alert).filter(Alert.acknowledged == False).count()

        latest_metric = (
            db.query(ProductionMetric)
            .order_by(ProductionMetric.date.desc())
            .first()
        )
        today_production = latest_metric.production if latest_metric else 0
        defect_rate = latest_metric.defect_rate if latest_metric else 0.0

        return {
            "type": "dashboard_stats",
            "data": {
                "total_orders": total_orders,
                "active_orders": active_orders,
                "equipment_running": equipment_running,
                "equipment_total": equipment_total,
                "pending_transports": pending_transports,
                "active_alerts": active_alerts,
                "today_production": today_production,
                "defect_rate": defect_rate,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


def _get_production_update() -> dict:
    """Build a simulated production update payload with slight random variation."""
    db = SessionLocal()
    try:
        stages = db.query(ProcessStage).order_by(ProcessStage.id).all()
        stage_data = []
        for stage in stages:
            # Simulate small progress changes for running stages
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
                "equipment_id": stage.equipment_id,
                "order_id": stage.order_id,
                "job_id": stage.job_id,
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
    """Build an alert update payload with unacknowledged alerts."""
    db = SessionLocal()
    try:
        unacked = db.query(Alert).filter(Alert.acknowledged == False).order_by(Alert.timestamp.desc()).all()
        alert_data = [
            {
                "id": a.id,
                "type": a.type,
                "severity": a.severity,
                "message": a.message,
                "zone": a.zone,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
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

    # Send initial dashboard stats immediately on connection
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

            # Broadcast production stage update every 5 seconds
            production_msg = _get_production_update()
            await manager.broadcast(production_msg)

            # Broadcast dashboard stats every 10 seconds (every 2 ticks)
            if tick % 2 == 0:
                stats_msg = _get_dashboard_stats()
                await manager.broadcast(stats_msg)

            # Broadcast alert update every 15 seconds (every 3 ticks)
            if tick % 3 == 0:
                alert_msg = _get_alert_update()
                await manager.broadcast(alert_msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
