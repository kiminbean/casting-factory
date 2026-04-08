"""FastAPI 백엔드 REST 클라이언트.

동기 requests 기반. UI 스레드를 블록하지 않도록 QThread worker 에서 호출할 것.

모드:
    - normal: FastAPI 호출, 실패 시 None
    - fallback (기본): FastAPI 호출, 실패/빈 응답 시 mock_data 로 대체
    - mock_only: 항상 mock_data 만 반환 (백엔드 없이 UI 데모용)

환경변수 CASTING_DATA_MODE 로 제어 (normal / fallback / mock_only)
"""
from __future__ import annotations

import logging
import os
from typing import Any

import requests

from app import mock_data
from config import API_BASE_URL

logger = logging.getLogger(__name__)

DATA_MODE: str = os.environ.get("CASTING_DATA_MODE", "fallback").lower()


class ApiClient:
    """FastAPI REST 엔드포인트 호출 래퍼 (mock fallback 지원)."""

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = 3.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._mock_only = DATA_MODE == "mock_only"
        self._fallback = DATA_MODE in ("fallback", "mock_only")
        self._dead_paths: set[str] = set()  # 404 엔드포인트 캐시

    # ----- core -----
    def _get(self, path: str, *, mock_value: Any = None) -> Any:
        """GET 요청. 실패/빈 응답 시 mock_value 반환 (fallback 모드일 때)."""
        if self._mock_only:
            return mock_value

        # 이전에 404 로 실패한 경로는 재시도하지 않음 (로그 스팸 방지)
        if path in self._dead_paths:
            return mock_value if self._fallback else None

        url = f"{self._base}{path}"
        try:
            response = self._session.get(url, timeout=self._timeout)
            if response.status_code == 404:
                # 해당 엔드포인트 미구현 - 조용히 mock 사용, 이후 호출은 스킵
                self._dead_paths.add(path)
                logger.info("Endpoint %s not available, using mock", path)
                return mock_value if self._fallback else None
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.warning("GET %s failed: %s", url, exc)
            return mock_value if self._fallback else None

        # 빈 응답이면 mock으로 대체 (fallback 모드)
        if self._fallback and (data is None or (isinstance(data, (list, dict)) and len(data) == 0)):
            logger.info("Empty response from %s, using mock", url)
            return mock_value
        return data

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        """POST 요청. 실패 시 예외 발생. mock_only 모드에선 None 반환.

        상태 변경 계열(생산 승인, 우선순위 계산 등)은 mock fallback 대신
        명시적으로 실패를 알려야 하므로 GET과 동작이 다름.
        """
        if self._mock_only:
            logger.info("mock_only mode — skipping POST %s", path)
            return None

        url = f"{self._base}{path}"
        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.error("POST %s failed: %s", url, exc)
            raise  # 호출자가 처리하도록 재전파

    def _patch(self, path: str, payload: dict[str, Any]) -> Any:
        """PATCH 요청. 실패 시 예외 발생."""
        if self._mock_only:
            return None

        url = f"{self._base}{path}"
        try:
            response = self._session.patch(
                url,
                json=payload,
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.error("PATCH %s failed: %s", url, exc)
            raise

    # ===== Dashboard =====
    def get_dashboard_stats(self) -> dict[str, Any] | None:
        data = self._get("/api/dashboard/stats", mock_value=mock_data.DASHBOARD_STATS)
        if isinstance(data, dict) and self._fallback:
            # 백엔드에 없는 필드를 mock 값으로 보충
            for key, value in mock_data.DASHBOARD_STATS.items():
                data.setdefault(key, value)
        return data

    def get_alerts(self) -> list[dict[str, Any]] | None:
        return self._get("/api/alerts", mock_value=mock_data.ALERTS)

    # ===== Production =====
    def get_production_metrics(self) -> list[dict[str, Any]] | None:
        return self._get("/api/production/metrics", mock_value=[])

    def get_equipment(self) -> list[dict[str, Any]] | None:
        data = self._get("/api/production/equipment", mock_value=mock_data.EQUIPMENT)
        # 필드 정규화: utilization 이 없으면 mock 기본값 사용
        if isinstance(data, list):
            normalized = []
            for item in data:
                normalized.append({
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "status": item.get("status", "-"),
                    "utilization": item.get("utilization") or self._calc_util(item),
                    "last_checked": item.get("last_maintenance", item.get("last_checked", "")),
                })
            return normalized
        return data

    def get_equipment_raw(self) -> list[dict[str, Any]] | None:
        """공장 맵용: 정규화 없이 pos_x/pos_y/type 포함한 raw equipment 반환."""
        data = self._get("/api/production/equipment", mock_value=None)
        if data:
            return data  # type: ignore[return-value]
        # mock 데이터에 좌표 추가 (mock_data 의 EQUIPMENT 에는 좌표가 없음)
        return self._mock_equipment_with_positions()

    @staticmethod
    def _mock_equipment_with_positions() -> list[dict[str, Any]]:
        """좌표가 포함된 mock equipment (공장 맵 데모용).

        AMR 좌표는 시간 기반 순환으로 이동 시뮬레이션.
        """
        import math
        import time

        t = time.time() * 0.15  # 느린 순환 속도

        # AMR-001 원형 순환
        amr1_x = 10 + 10 * (0.5 + 0.5 * math.sin(t))
        amr1_y = 5 + 2.5 * math.cos(t)

        # AMR-002 horizontal ping-pong
        amr2_x = 4 + 8 * (0.5 + 0.5 * math.sin(t * 0.7 + 1.2))
        amr2_y = 7

        # AMR-003 는 충전소 근처에서 정지
        amr3_x = 1
        amr3_y = 10

        return [
            {"id": "FRN-001", "name": "용해로 #1", "type": "furnace",
             "status": "running", "pos_x": 2, "pos_y": 1},
            {"id": "FRN-002", "name": "용해로 #2", "type": "furnace",
             "status": "idle", "pos_x": 4, "pos_y": 1},
            {"id": "MLD-001", "name": "조형기 #1", "type": "mold_press",
             "status": "running", "pos_x": 8, "pos_y": 1},
            {"id": "ARM-001", "name": "로봇암 #1 (주탕)", "type": "robot_arm",
             "status": "idle", "pos_x": 12, "pos_y": 2},
            {"id": "ARM-002", "name": "로봇암 #2 (탈형)", "type": "robot_arm",
             "status": "idle", "pos_x": 16, "pos_y": 2},
            {"id": "ARM-003", "name": "로봇암 #3 (후처리)", "type": "robot_arm",
             "status": "running", "pos_x": 20, "pos_y": 2},
            {"id": "CVR-001", "name": "컨베이어 #1", "type": "conveyor",
             "status": "running", "pos_x": 24, "pos_y": 3},
            {"id": "CAM-001", "name": "검사 카메라 #1", "type": "camera",
             "status": "running", "pos_x": 25, "pos_y": 3},
            {"id": "SRT-001", "name": "분류기 #1", "type": "sorter",
             "status": "running", "pos_x": 28, "pos_y": 3},
            {"id": "AMR-001", "name": "AMR #1", "type": "amr",
             "status": "running", "pos_x": amr1_x, "pos_y": amr1_y, "battery": 78},
            {"id": "AMR-002", "name": "AMR #2", "type": "amr",
             "status": "running", "pos_x": amr2_x, "pos_y": amr2_y, "battery": 64},
            {"id": "AMR-003", "name": "AMR #3", "type": "amr",
             "status": "charging", "pos_x": amr3_x, "pos_y": amr3_y, "battery": 12},
        ]

    def get_process_stages(self) -> list[dict[str, Any]] | None:
        data = self._get("/api/production/stages", mock_value=mock_data.PROCESS_STAGES)
        if isinstance(data, list):
            normalized = []
            for item in data:
                normalized.append({
                    "name": item.get("label", item.get("stage", "")),
                    "status": item.get("status", "-"),
                    "progress": item.get("progress", 0),
                    "started_at": item.get("start_time", "-") or "-",
                    "equipment": item.get("equipment_id", "-"),
                })
            return normalized
        return data

    # ===== Quality =====
    def get_quality_inspections(self) -> list[dict[str, Any]] | None:
        data = self._get("/api/quality/inspections", mock_value=mock_data.INSPECTIONS)
        if isinstance(data, list):
            normalized = []
            for item in data:
                normalized.append({
                    "inspected_at": item.get("inspected_at", item.get("timestamp", "")),
                    "product": item.get("product", item.get("product_name", "")),
                    "result": str(item.get("result", "")).upper(),
                    "defect_type": item.get("defect_type", "") or "",
                    "inspector": item.get("inspector", item.get("inspected_by", "")),
                    "note": item.get("note", item.get("comment", "")) or "",
                })
            return normalized
        return data

    def get_defect_stats(self) -> dict[str, Any] | None:
        data = self._get("/api/quality/stats", mock_value=mock_data.QUALITY_STATS)
        if isinstance(data, dict) and self._fallback:
            for key, value in mock_data.QUALITY_STATS.items():
                data.setdefault(key, value)
        return data

    # ===== Logistics =====
    def get_transport_tasks(self) -> list[dict[str, Any]] | None:
        data = self._get("/api/logistics/tasks", mock_value=mock_data.TRANSPORT_TASKS)
        if isinstance(data, list):
            normalized: list[dict[str, Any]] = []
            for item in data:
                normalized.append({
                    "id": item.get("id", item.get("task_id", "")),
                    "type": item.get("type", item.get("task_type", "")),
                    "priority": item.get("priority", "normal"),
                    "from": item.get("from", item.get("source", item.get("from_location", ""))),
                    "to": item.get("to", item.get("destination", item.get("to_location", ""))),
                    "amr": item.get("amr", item.get("assigned_robot", item.get("robot_id", ""))),
                    "status": item.get("status", "-"),
                    "cargo": item.get("cargo", item.get("loaded_item", "")),
                })
            return normalized
        return data

    def get_warehouse_racks(self) -> list[dict[str, Any]]:
        data = self._get("/api/logistics/warehouse", mock_value=mock_data.WAREHOUSE_RACKS)
        if isinstance(data, list) and data:
            return data  # type: ignore[return-value]
        return mock_data.WAREHOUSE_RACKS

    def get_outbound_orders(self) -> list[dict[str, Any]]:
        data = self._get("/api/logistics/outbound-orders", mock_value=mock_data.OUTBOUND_ORDERS)
        if isinstance(data, list) and data:
            normalized: list[dict[str, Any]] = []
            for item in data:
                normalized.append({
                    "id": item.get("id", item.get("order_id", "")),
                    "product": item.get("product", item.get("product_name", "")),
                    "qty": item.get("qty", item.get("quantity", 0)),
                    "customer": item.get("customer", item.get("destination", "")),
                    "policy": item.get("policy", "FIFO"),
                    "status": item.get("status", "pending"),
                })
            return normalized
        return mock_data.OUTBOUND_ORDERS

    # ===== Charts (v0.2) =====
    def get_weekly_production(self) -> list[dict[str, Any]]:
        return self._get("/api/production/weekly", mock_value=mock_data.WEEKLY_PRODUCTION) \
            or mock_data.WEEKLY_PRODUCTION

    def get_temperature_history(self) -> list[dict[str, Any]]:
        return self._get("/api/production/temperature", mock_value=mock_data.TEMPERATURE_HISTORY) \
            or mock_data.TEMPERATURE_HISTORY

    def get_hourly_production(self) -> list[dict[str, Any]]:
        return self._get("/api/production/hourly", mock_value=mock_data.HOURLY_PRODUCTION) \
            or mock_data.HOURLY_PRODUCTION

    def get_defect_rate_trend(self) -> list[dict[str, Any]]:
        return self._get("/api/quality/trend", mock_value=mock_data.DEFECT_RATE_TREND) \
            or mock_data.DEFECT_RATE_TREND

    def get_defect_type_dist(self) -> list[dict[str, Any]]:
        return self._get("/api/quality/defect-types", mock_value=mock_data.DEFECT_TYPE_DIST) \
            or mock_data.DEFECT_TYPE_DIST

    def get_production_vs_defects(self) -> list[dict[str, Any]]:
        return self._get("/api/quality/vs-defects", mock_value=mock_data.PRODUCTION_VS_DEFECTS) \
            or mock_data.PRODUCTION_VS_DEFECTS

    def get_vision_feed(self) -> dict[str, Any]:
        data = self._get("/api/quality/vision-feed", mock_value=mock_data.VISION_FEED)
        if isinstance(data, dict) and data:
            merged = dict(mock_data.VISION_FEED)
            merged.update(data)
            return merged
        return mock_data.VISION_FEED

    def get_sorter_state(self) -> dict[str, Any]:
        data = self._get("/api/quality/sorter", mock_value=mock_data.SORTER_STATE)
        if isinstance(data, dict) and data:
            merged = dict(mock_data.SORTER_STATE)
            merged.update(data)
            return merged
        return mock_data.SORTER_STATE

    def get_inspection_standards(self) -> list[dict[str, Any]]:
        data = self._get("/api/quality/standards", mock_value=mock_data.INSPECTION_STANDARDS)
        if isinstance(data, list) and data:
            normalized: list[dict[str, Any]] = []
            for item in data:
                normalized.append({
                    "product": item.get("product", item.get("product_name", "")),
                    "target": item.get("target", item.get("target_dimension", "-")),
                    "tolerance": item.get("tolerance", item.get("tolerance_range", "-")),
                    "threshold": item.get("threshold", item.get("decision_threshold", "-")),
                })
            return normalized
        return mock_data.INSPECTION_STANDARDS

    def get_process_parameter_history(self) -> list[dict[str, Any]]:
        """공정별 파라미터 이력 (8공정 × 여러 지표)."""
        data = self._get(
            "/api/production/parameter-history",
            mock_value=mock_data.PROCESS_PARAM_HISTORY,
        )
        if isinstance(data, list) and data:
            return data  # type: ignore[return-value]
        return mock_data.PROCESS_PARAM_HISTORY

    def get_live_parameters(self) -> dict[str, Any]:
        """실시간 공정 파라미터 (온도/압력/각도/냉각 진행)."""
        data = self._get("/api/production/live", mock_value=mock_data.LIVE_PARAMETERS)
        if isinstance(data, dict):
            merged = dict(mock_data.LIVE_PARAMETERS)
            merged.update(data)
            return merged
        return mock_data.LIVE_PARAMETERS

    def get_recent_orders(self) -> list[dict[str, Any]]:
        data = self._get("/api/orders", mock_value=mock_data.RECENT_ORDERS)
        if isinstance(data, list) and data:
            normalized: list[dict[str, Any]] = []
            for item in data[:10]:
                normalized.append({
                    "id": item.get("id", item.get("order_number", "")),
                    "customer": item.get("customer", item.get("customer_name", "")),
                    "amount": item.get("amount", item.get("total_price", 0)),
                    "due_date": item.get("due_date", item.get("delivery_date", "")),
                    "status": item.get("status", ""),
                })
            return normalized
        return mock_data.RECENT_ORDERS

    # ===== Production Scheduling (생산 계획) =====
    # Web에서 "생산 승인" 버튼을 누르면 in_production 상태 + ProductionJob 레코드 생성됨.
    # 그 이후 PyQt5 생산 계획 페이지에서 우선순위 계산/순서 조정/실제 착수를 수행한다.

    def get_production_jobs(self) -> list[dict[str, Any]]:
        """생산 작업 목록 조회 (웹에서 승인된 order로부터 생성된 ProductionJob들).

        Returns: ProductionJob 딕셔너리 리스트 (id, order_id, priority_score,
                 priority_rank, status, estimated_completion 등).
        """
        data = self._get("/api/production/schedule/jobs", mock_value=[])
        return data if isinstance(data, list) else []

    def get_approved_and_running_orders(self) -> list[dict[str, Any]]:
        """생산 계획 화면에서 볼 주문 목록.

        - approved: 생산 승인되지 않은 대기 주문 (참고용)
        - in_production: 승인 완료 → ProductionJob 존재, 우선순위 계산 대상

        Returns: 정규화된 주문 리스트 (id, company_name, total_amount,
                 requested_delivery, status 등).
        """
        data = self._get("/api/orders", mock_value=[])
        if not isinstance(data, list):
            return []

        target_statuses = {"approved", "in_production"}
        result: list[dict[str, Any]] = []
        for item in data:
            status = str(item.get("status", "")).lower()
            if status not in target_statuses:
                continue
            result.append({
                "id": item.get("id", ""),
                "company_name": item.get("company_name") or item.get("companyName") or "-",
                "customer_name": item.get("customer_name") or item.get("customerName") or "-",
                "total_amount": item.get("total_amount") or item.get("totalAmount") or 0,
                "requested_delivery": (
                    item.get("requested_delivery")
                    or item.get("requestedDelivery")
                    or ""
                ),
                "confirmed_delivery": (
                    item.get("confirmed_delivery")
                    or item.get("confirmedDelivery")
                    or ""
                ),
                "created_at": item.get("created_at") or item.get("createdAt") or "",
                "status": status,
            })
        return result

    def calculate_priority(self, order_ids: list[str]) -> dict[str, Any]:
        """선택 주문들의 우선순위를 계산 (dry-run, DB 상태 변경 없음).

        Args:
            order_ids: 계산 대상 주문 ID 리스트

        Returns:
            {"results": [PriorityResult, ...]} 형식. 각 PriorityResult는
            order_id, total_score, rank, factors, recommendation_reason,
            delay_risk, ready_status, blocking_reasons 등 포함.

        Raises:
            requests.RequestException: 네트워크/서버 에러 (UI에서 잡아서 표시)
        """
        result = self._post(
            "/api/production/schedule/calculate",
            {"order_ids": order_ids},
        )
        return result if isinstance(result, dict) else {"results": []}

    def create_priority_log(
        self,
        order_id: str,
        old_rank: int,
        new_rank: int,
        reason: str,
    ) -> dict[str, Any] | None:
        """우선순위 수동 변경 이력 기록."""
        return self._post(
            "/api/production/schedule/priority-log",
            {
                "order_id": order_id,
                "old_rank": old_rank,
                "new_rank": new_rank,
                "reason": reason,
            },
        )

    def get_amr_status(self) -> list[dict[str, Any]] | None:
        # 우선 전용 엔드포인트 시도, 없으면 equipment 에서 amr 타입만 추출
        equipment = self._get("/api/production/equipment", mock_value=None)
        if isinstance(equipment, list):
            amrs = [e for e in equipment if e.get("type") == "amr"]
            if amrs:
                return [
                    {
                        "id": amr.get("id", ""),
                        "status": amr.get("status", "-"),
                        "battery": amr.get("battery", 0) or 0,
                        "location": amr.get("install_location", "-"),
                        "current_task": "-",
                    }
                    for amr in amrs
                ]
        # fallback
        return mock_data.AMR_STATUS if self._fallback else None

    # ----- helpers -----
    @staticmethod
    def _calc_util(item: dict[str, Any]) -> int:
        """utilization 이 없을 때 status 로 유추."""
        status = str(item.get("status", "")).lower()
        if status == "running":
            return 85
        if status == "idle":
            return 20
        if status == "charging":
            return 0
        if status == "error":
            return 0
        return 50
