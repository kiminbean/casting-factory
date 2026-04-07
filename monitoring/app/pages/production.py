"""생산 모니터링 페이지 - 공정 단계 + 설비 상태."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient


class ProductionPage(QWidget):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("생산 모니터링")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # 공정 단계 테이블
        stages_label = QLabel("공정 단계")
        stages_label.setObjectName("sectionTitle")
        layout.addWidget(stages_label)

        self._stages_table = QTableWidget(0, 5)
        self._stages_table.setHorizontalHeaderLabels(
            ["단계", "상태", "진행률", "시작 시각", "담당 설비"]
        )
        self._stages_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self._stages_table.verticalHeader().setVisible(False)
        self._stages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._stages_table)

        # 설비 상태 테이블
        equip_label = QLabel("설비 상태")
        equip_label.setObjectName("sectionTitle")
        layout.addWidget(equip_label)

        self._equip_table = QTableWidget(0, 4)
        self._equip_table.setHorizontalHeaderLabels(
            ["설비명", "상태", "가동률", "마지막 점검"]
        )
        self._equip_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._equip_table.verticalHeader().setVisible(False)
        self._equip_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._equip_table)

    def refresh(self) -> None:
        stages = self._api.get_process_stages() or []
        self._stages_table.setRowCount(len(stages))
        for row, stage in enumerate(stages):
            self._stages_table.setItem(row, 0, QTableWidgetItem(str(stage.get("name", ""))))
            status_item = QTableWidgetItem(str(stage.get("status", "")))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._stages_table.setItem(row, 1, status_item)
            self._stages_table.setItem(
                row, 2, QTableWidgetItem(f"{stage.get('progress', 0)}%")
            )
            self._stages_table.setItem(
                row, 3, QTableWidgetItem(str(stage.get("started_at", "")))
            )
            self._stages_table.setItem(
                row, 4, QTableWidgetItem(str(stage.get("equipment", "")))
            )

        equipment = self._api.get_equipment() or []
        self._equip_table.setRowCount(len(equipment))
        for row, eq in enumerate(equipment):
            self._equip_table.setItem(row, 0, QTableWidgetItem(str(eq.get("name", ""))))
            self._equip_table.setItem(row, 1, QTableWidgetItem(str(eq.get("status", ""))))
            self._equip_table.setItem(
                row, 2, QTableWidgetItem(f"{eq.get('utilization', 0)}%")
            )
            self._equip_table.setItem(
                row, 3, QTableWidgetItem(str(eq.get("last_checked", "")))
            )

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        msg_type = payload.get("type", "")
        if msg_type in ("production_update", "equipment_update", "process_stage_update"):
            self.refresh()
