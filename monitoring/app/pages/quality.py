"""품질 검사 모니터링 페이지."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.pages.dashboard import KpiCard


class QualityPage(QWidget):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._kpis: dict[str, KpiCard] = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("품질 검사")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(14)
        metrics = [
            ("total", "검사 수", "건"),
            ("ok", "합격", "건"),
            ("ng", "불합격", "건"),
            ("rate", "불량률", "%"),
        ]
        for col, (key, label, unit) in enumerate(metrics):
            card = KpiCard(label, unit=unit)
            self._kpis[key] = card
            kpi_grid.addWidget(card, 0, col)
        layout.addLayout(kpi_grid)

        section = QLabel("최근 검사 이력")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["검사 시각", "제품", "결과", "불량 유형", "담당자", "비고"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table, stretch=1)

    def refresh(self) -> None:
        stats = self._api.get_defect_stats()
        if stats:
            self._kpis["total"].update_value(stats.get("total", 0))
            self._kpis["ok"].update_value(stats.get("ok", 0))
            self._kpis["ng"].update_value(stats.get("ng", 0))
            self._kpis["rate"].update_value(f"{stats.get('defect_rate', 0):.1f}")

        inspections = self._api.get_quality_inspections() or []
        self._table.setRowCount(len(inspections))
        for row, item in enumerate(inspections[:200]):
            self._table.setItem(row, 0, QTableWidgetItem(str(item.get("inspected_at", ""))))
            self._table.setItem(row, 1, QTableWidgetItem(str(item.get("product", ""))))
            result = str(item.get("result", ""))
            result_item = QTableWidgetItem(result)
            result_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 2, result_item)
            self._table.setItem(row, 3, QTableWidgetItem(str(item.get("defect_type", ""))))
            self._table.setItem(row, 4, QTableWidgetItem(str(item.get("inspector", ""))))
            self._table.setItem(row, 5, QTableWidgetItem(str(item.get("note", ""))))

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        if payload.get("type") in ("quality_update", "inspection_completed"):
            self.refresh()
