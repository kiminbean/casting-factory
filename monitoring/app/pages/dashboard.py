"""대시보드 페이지 - KPI 카드 + 주간 차트 + 최근 주문 + 실시간 알림."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.widgets.alert_widgets import AlertListItem
from app.widgets.charts import WeeklyProductionChart
from app.widgets.conveyor_card import ConveyorCard
from app.widgets.factory_map import MiniFactoryMapView


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
    """대시보드 페이지 - KPI + 주간 차트 + 주문 테이블 + 알림."""

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._kpi_cards: dict[str, KpiCard] = {}
        self._build_ui()
        self.refresh()

        # 미니맵 전용 빠른 타이머 (AMR 애니메이션용)
        self._fast_map_timer = QTimer(self)
        self._fast_map_timer.setInterval(500)
        self._fast_map_timer.timeout.connect(self._refresh_mini_map)
        self._fast_map_timer.start()

    def _refresh_mini_map(self) -> None:
        equipment = self._api.get_equipment_raw() or []
        self._mini_map.update_equipment(equipment)

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
            ("oee", "설비 가동률", "%"),
            ("active_orders", "진행 주문", "건"),
        ]
        for idx, (key, title_text, unit) in enumerate(kpi_items):
            card = KpiCard(title_text, unit=unit)
            self._kpi_cards[key] = card
            kpi_grid.addWidget(card, 0, idx)
        layout.addLayout(kpi_grid)

        # 컨베이어 상태 카드 (MQTT 실시간) - 가로 배치
        conveyor_label = QLabel("컨베이어 실시간 상태")
        conveyor_label.setObjectName("sectionTitle")
        layout.addWidget(conveyor_label)

        self._conveyor_row = QHBoxLayout()
        self._conveyor_row.setSpacing(14)
        self._conveyor_cards: dict[str, ConveyorCard] = {}
        # 기본 1대 카드 미리 생성
        default_card = ConveyorCard("1")
        self._conveyor_cards["1"] = default_card
        self._conveyor_row.addWidget(default_card, stretch=1)
        self._conveyor_row.addStretch()

        conveyor_container = QWidget()
        conveyor_container.setLayout(self._conveyor_row)
        layout.addWidget(conveyor_container)

        # 중단 Row 1: 공장 미니맵 (풀와이드)
        map_container = QFrame()
        map_container.setObjectName("tableCard")
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(12, 10, 12, 12)
        map_layout.setSpacing(6)

        map_title = QLabel("공장 현황 맵")
        map_title.setObjectName("sectionTitle")
        map_layout.addWidget(map_title)

        self._mini_map = MiniFactoryMapView()
        map_layout.addWidget(self._mini_map)

        layout.addWidget(map_container, stretch=2)

        # 중단 Row 2: 주간 차트 + 최근 주문 (가로 분할)
        middle_row = QHBoxLayout()
        middle_row.setSpacing(14)

        self._weekly_chart = WeeklyProductionChart()
        self._weekly_chart.setMinimumHeight(240)
        middle_row.addWidget(self._weekly_chart, stretch=3)

        # 최근 주문 테이블
        orders_container = QFrame()
        orders_container.setObjectName("tableCard")
        orders_layout = QVBoxLayout(orders_container)
        orders_layout.setContentsMargins(12, 10, 12, 12)
        orders_layout.setSpacing(8)

        orders_title = QLabel("최근 주문")
        orders_title.setObjectName("sectionTitle")
        orders_layout.addWidget(orders_title)

        self._orders_table = QTableWidget(0, 4)
        self._orders_table.setHorizontalHeaderLabels(
            ["고객사", "금액", "납기", "상태"]
        )
        self._orders_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self._orders_table.verticalHeader().setVisible(False)
        self._orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        orders_layout.addWidget(self._orders_table)

        middle_row.addWidget(orders_container, stretch=2)
        layout.addLayout(middle_row, stretch=2)

        # 알림 목록 (하단) - severity 아이콘/색상 위젯
        alert_title = QLabel("실시간 알림")
        alert_title.setObjectName("sectionTitle")
        layout.addWidget(alert_title)

        self._alert_scroll = QScrollArea()
        self._alert_scroll.setObjectName("alertScroll")
        self._alert_scroll.setWidgetResizable(True)
        self._alert_scroll.setFrameShape(QFrame.NoFrame)
        self._alert_scroll.setMaximumHeight(200)

        self._alert_container = QWidget()
        self._alert_layout = QVBoxLayout(self._alert_container)
        self._alert_layout.setContentsMargins(0, 0, 0, 0)
        self._alert_layout.setSpacing(6)
        self._alert_layout.addStretch()

        self._alert_scroll.setWidget(self._alert_container)
        layout.addWidget(self._alert_scroll)

    def refresh(self) -> None:
        """REST API 에서 최신 데이터 갱신."""
        stats = self._api.get_dashboard_stats()
        if stats:
            self._kpi_cards["production_rate"].update_value(
                stats.get("today_production", 0)
            )
            self._kpi_cards["defect_rate"].update_value(
                f"{stats.get('defect_rate', 0):.1f}"
            )
            self._kpi_cards["oee"].update_value(
                f"{stats.get('equipment_utilization', stats.get('oee', 0)):.1f}"
            )
            self._kpi_cards["active_orders"].update_value(
                stats.get("active_orders", stats.get("pending_orders", 0))
            )

        # 공장 미니맵
        equipment = self._api.get_equipment_raw() or []
        self._mini_map.update_equipment(equipment)

        # 주간 차트
        weekly = self._api.get_weekly_production()
        self._weekly_chart.update_data(weekly)

        # 최근 주문 테이블
        orders = self._api.get_recent_orders()
        self._update_orders_table(orders)

        # 알림
        alerts = self._api.get_alerts() or []
        self._rebuild_alerts(alerts[:20])
        self._emit_critical_alerts(alerts)

    def _emit_critical_alerts(self, alerts: list[dict[str, Any]]) -> None:
        """critical/error 알림을 MainWindow 토스트로 전달."""
        # MainWindow 인스턴스 찾기 (tree 위로 탐색)
        win = self.window()
        show_toast = getattr(win, "_maybe_show_toast_for_alert", None)
        if show_toast is None:
            return
        for alert in alerts[:5]:  # 최근 5개만
            show_toast(alert)

    def _rebuild_alerts(self, alerts: list[dict[str, Any]]) -> None:
        # 기존 항목 제거 (마지막 stretch 제외)
        while self._alert_layout.count() > 1:
            item = self._alert_layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        # 새 항목 추가
        for alert in alerts:
            widget = AlertListItem(alert)
            self._alert_layout.insertWidget(self._alert_layout.count() - 1, widget)

    def _update_orders_table(self, orders: list[dict[str, Any]]) -> None:
        self._orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self._orders_table.setItem(
                row, 0, QTableWidgetItem(str(order.get("customer", "-")))
            )
            amount = order.get("amount", 0) or 0
            try:
                amt_str = f"₩{int(amount):,}"
            except (TypeError, ValueError):
                amt_str = str(amount)
            self._orders_table.setItem(row, 1, QTableWidgetItem(amt_str))
            self._orders_table.setItem(
                row, 2, QTableWidgetItem(str(order.get("due_date", "")))
            )
            status_item = QTableWidgetItem(str(order.get("status", "")))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._orders_table.setItem(row, 3, status_item)

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        """WebSocket 실시간 이벤트 수신 처리."""
        if payload.get("type") in (
            "dashboard_update",
            "order_update",
            "production_update",
        ):
            self.refresh()

    def handle_mqtt_message(self, topic: str, payload: dict[str, Any]) -> None:
        """MQTT 메시지 수신 - 컨베이어 카드 실시간 갱신."""
        # topic 예: conveyor/1/status
        parts = topic.split("/")
        if len(parts) < 2:
            return
        if parts[0] != "conveyor":
            return
        conveyor_id = parts[1]
        subtype = parts[2] if len(parts) > 2 else ""

        card = self._conveyor_cards.get(conveyor_id)
        if card is None:
            card = ConveyorCard(conveyor_id)
            self._conveyor_cards[conveyor_id] = card
            # stretch 앞에 삽입 (마지막 stretch 제외)
            idx = self._conveyor_row.count() - 1
            self._conveyor_row.insertWidget(idx, card, stretch=1)

        if subtype == "status":
            card.update_from_payload(payload)
            card.set_online(True)
        elif subtype == "heartbeat":
            value = str(payload.get("value", "")).lower()
            card.set_online(value == "online" or "alive" in payload)
            if value == "offline":
                card.mark_offline()
        elif subtype == "event":
            # entry / exit / cycle_done 등
            card.set_online(True)

    @staticmethod
    def _format_alert(alert: dict[str, Any]) -> str:
        level = alert.get("level", "info").upper()
        ts = alert.get("created_at", "")
        msg = alert.get("message", "")
        return f"[{level}] {ts}  {msg}"
