"""공장 맵 페이지 - 2D 탑다운 실시간 위치 뷰."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.widgets.factory_map import FactoryMapView, STATUS_COLORS


class LegendBadge(QFrame):
    """상태 범례 배지."""

    def __init__(self, label: str, color: str) -> None:
        super().__init__()
        self.setObjectName("legendBadge")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 12, 4)
        layout.setSpacing(8)

        dot = QLabel()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet(
            f"background-color: {color}; border-radius: 6px; border: 1px solid #00000020;"
        )
        layout.addWidget(dot)

        text = QLabel(label)
        text.setStyleSheet("color: #374151; font-size: 12px;")
        layout.addWidget(text)


class FactoryMapPage(QWidget):
    """공장 맵 페이지."""

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._build_ui()
        self.refresh()

        # AMR 위치는 빠른 주기로 갱신 (애니메이션 부드럽게)
        self._fast_timer = QTimer(self)
        self._fast_timer.setInterval(500)
        self._fast_timer.timeout.connect(self.refresh)
        self._fast_timer.start()

    def _build_ui(self) -> None:
        # 맵 페이지는 다크 테마
        self.setStyleSheet(
            "QWidget { background-color: #0f172a; }"
            "QLabel { color: #e5e7eb; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # 제목
        header_row = QHBoxLayout()
        title = QLabel("공장 맵")
        title.setStyleSheet("color: #f9fafb; font-size: 22px; font-weight: bold;")
        header_row.addWidget(title)
        header_row.addStretch()

        hint = QLabel("드래그로 이동 · Ctrl + 휠로 확대")
        hint.setStyleSheet("color: #9ca3af; font-size: 11px;")
        header_row.addWidget(hint)
        layout.addLayout(header_row)

        # 범례
        legend_row = QHBoxLayout()
        legend_row.setSpacing(6)
        legend_items = [
            ("active", "가동"),
            ("idle", "대기"),
            ("warning", "경고"),
            ("error", "오류"),
            ("charging", "충전"),
        ]
        for status, label in legend_items:
            color = STATUS_COLORS[status]["dot"]
            legend_row.addWidget(LegendBadge(label, color))
        legend_row.addStretch()
        layout.addLayout(legend_row)

        # 맵
        self._map = FactoryMapView()
        self._map.setObjectName("factoryMapView")
        self._map.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self._map, stretch=1)

    def refresh(self) -> None:
        # 공장 맵은 raw equipment 데이터 (pos_x, pos_y, type) 가 필요
        equipment = self._api.get_equipment_raw() or []
        self._map.update_equipment(equipment)

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        msg_type = payload.get("type", "")
        if msg_type in (
            "equipment_update",
            "amr_update",
            "equipment_position",
        ):
            self.refresh()
