"""FastAPI 백엔드 REST 클라이언트.

동기 requests 기반. UI 스레드를 블록하지 않도록 QThread worker 에서 호출할 것.
"""
from __future__ import annotations

import logging
from typing import Any

import requests

from config import API_BASE_URL

logger = logging.getLogger(__name__)


class ApiClient:
    """FastAPI REST 엔드포인트 호출 래퍼."""

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = 5.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    def _get(self, path: str) -> Any:
        url = f"{self._base}{path}"
        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.error("GET %s failed: %s", url, exc)
            return None

    # === Dashboard ===
    def get_dashboard_stats(self) -> dict[str, Any] | None:
        return self._get("/api/dashboard/stats")

    def get_alerts(self) -> list[dict[str, Any]] | None:
        return self._get("/api/alerts")

    # === Production ===
    def get_production_metrics(self) -> list[dict[str, Any]] | None:
        return self._get("/api/production/metrics")

    def get_equipment(self) -> list[dict[str, Any]] | None:
        return self._get("/api/production/equipment")

    def get_process_stages(self) -> list[dict[str, Any]] | None:
        return self._get("/api/production/stages")

    # === Quality ===
    def get_quality_inspections(self) -> list[dict[str, Any]] | None:
        return self._get("/api/quality/inspections")

    def get_defect_stats(self) -> dict[str, Any] | None:
        # FastAPI 라우트: /api/quality/stats
        return self._get("/api/quality/stats")

    # === Logistics ===
    def get_transport_tasks(self) -> list[dict[str, Any]] | None:
        return self._get("/api/logistics/tasks")

    def get_amr_status(self) -> list[dict[str, Any]] | None:
        # AMR 엔드포인트는 Phase 3 AMR 통합 전까지는 transport task 에서 파생
        tasks = self._get("/api/logistics/tasks") or []
        amr_map: dict[str, dict[str, Any]] = {}
        for task in tasks:
            amr_id = task.get("assigned_robot") or task.get("amr")
            if not amr_id:
                continue
            if amr_id not in amr_map:
                amr_map[amr_id] = {
                    "id": amr_id,
                    "status": task.get("status", "-"),
                    "battery": 0,
                    "location": task.get("current_location", "-"),
                    "current_task": task.get("id", "-"),
                }
        return list(amr_map.values())
