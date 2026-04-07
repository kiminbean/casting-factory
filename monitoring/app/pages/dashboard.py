"""대시보드 페이지 - KPI 카드 + 실시간 알림."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient


class KpiCard(QFrame):
    """KPI 표시 카드."""

    def __init__(self, title: str, value: str = "-", unit: str = "") -> None:
        super().__init__()
        self.setObjectName("kpiCard")
        self.setFrameShape(QFrame.StyledPanel)

        self._title = QLabel(title)
        self._title.setObjectName("kpiTitle")

        self._value = QLabel(value)
        self._value.setObjectName("kpiValue")

        self._unit = QLabel(unit)
        self._unit.setObjectName("kpiUnit")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)
        layout.addWidget(self._title)

        bottom = QHBoxLayout()
        bottom.setSpacing(4)
        bottom.addWidget(self._value, alignment=Qt.AlignBottom)
        bottom.addWidget(self._unit, alignment=Qt.AlignBottom)
        bottom.addStretch()
        layout.addLayout(bottom)

    def update_value(self, value: str | int | float, unit: str = "") -> None:
        self._value.setText(str(value))
        if unit:
            self._unit.setText(unit)


class DashboardPage(QWidget):
    """대시보드 페이지 - 주요 KPI + 실시간 알림."""

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._kpi_cards: dict[str, KpiCard] = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 제목
        title = QLabel("대시보드")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # KPI 그리드 (4칸)
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(14)
        kpi_items = [
            ("production_rate", "생산량", "개"),
            ("defect_rate", "불량률", "%"),
            ("oee", "OEE", "%"),
            ("active_orders", "진행 주문", "건"),
        ]
        for idx, (key, title_text, unit) in enumerate(kpi_items):
            card = KpiCard(title_text, unit=unit)
            self._kpi_cards[key] = card
            kpi_grid.addWidget(card, 0, idx)
        layout.addLayout(kpi_grid)

        # 알림 목록
        alert_title = QLabel("실시간 알림")
        alert_title.setObjectName("sectionTitle")
        layout.addWidget(alert_title)

        self._alert_list = QListWidget()
        self._alert_list.setObjectName("alertList")
        layout.addWidget(self._alert_list, stretch=1)

    def refresh(self) -> None:
        """REST API 에서 최신 데이터 갱신."""
        stats = self._api.get_dashboard_stats()
        if stats:
            self._kpi_cards["production_rate"].update_value(stats.get("today_production", 0))
            self._kpi_cards["defect_rate"].update_value(
                f"{stats.get('defect_rate', 0):.1f}"
            )
            self._kpi_cards["oee"].update_value(f"{stats.get('oee', 0):.1f}")
            self._kpi_cards["active_orders"].update_value(stats.get("active_orders", 0))

        alerts = self._api.get_alerts()
        if alerts:
            self._alert_list.clear()
            for alert in alerts[:20]:
                item = QListWidgetItem(self._format_alert(alert))
                self._alert_list.addItem(item)

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        """WebSocket 실시간 이벤트 수신 처리."""
        if payload.get("type") == "dashboard_update":
            self.refresh()

    @staticmethod
    def _format_alert(alert: dict[str, Any]) -> str:
        level = alert.get("level", "info").upper()
        ts = alert.get("created_at", "")
        msg = alert.get("message", "")
        return f"[{level}] {ts}  {msg}"
