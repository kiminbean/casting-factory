"""물류/이송 모니터링 페이지 - AMR 상태 + 이송 작업."""
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


class LogisticsPage(QWidget):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("물류 / 이송")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # AMR 상태
        amr_label = QLabel("AMR 상태")
        amr_label.setObjectName("sectionTitle")
        layout.addWidget(amr_label)

        self._amr_table = QTableWidget(0, 5)
        self._amr_table.setHorizontalHeaderLabels(
            ["AMR ID", "상태", "배터리", "현재 위치", "현재 작업"]
        )
        self._amr_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._amr_table.verticalHeader().setVisible(False)
        self._amr_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._amr_table)

        # 이송 작업
        task_label = QLabel("이송 작업 목록")
        task_label.setObjectName("sectionTitle")
        layout.addWidget(task_label)

        self._task_table = QTableWidget(0, 6)
        self._task_table.setHorizontalHeaderLabels(
            ["작업 ID", "유형", "출발지", "도착지", "담당 AMR", "상태"]
        )
        self._task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._task_table.verticalHeader().setVisible(False)
        self._task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._task_table, stretch=1)

    def refresh(self) -> None:
        amrs = self._api.get_amr_status() or []
        self._amr_table.setRowCount(len(amrs))
        for row, amr in enumerate(amrs):
            self._amr_table.setItem(row, 0, QTableWidgetItem(str(amr.get("id", ""))))
            status_item = QTableWidgetItem(str(amr.get("status", "")))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._amr_table.setItem(row, 1, status_item)
            self._amr_table.setItem(row, 2, QTableWidgetItem(f"{amr.get('battery', 0)}%"))
            self._amr_table.setItem(row, 3, QTableWidgetItem(str(amr.get("location", ""))))
            self._amr_table.setItem(row, 4, QTableWidgetItem(str(amr.get("current_task", ""))))

        tasks = self._api.get_transport_tasks() or []
        self._task_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks[:200]):
            self._task_table.setItem(row, 0, QTableWidgetItem(str(task.get("id", ""))))
            self._task_table.setItem(row, 1, QTableWidgetItem(str(task.get("type", ""))))
            self._task_table.setItem(row, 2, QTableWidgetItem(str(task.get("from", ""))))
            self._task_table.setItem(row, 3, QTableWidgetItem(str(task.get("to", ""))))
            self._task_table.setItem(row, 4, QTableWidgetItem(str(task.get("amr", ""))))
            status_item = QTableWidgetItem(str(task.get("status", "")))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._task_table.setItem(row, 5, status_item)

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        if payload.get("type") in ("amr_update", "transport_task_update"):
            self.refresh()
