"""AMR 상태 카드 위젯 - 배터리 바 + 아이콘 + 현재 작업."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


STATUS_STYLE = {
    "running": {"bg": "#d1fae5", "border": "#10b981", "text": "#065f46", "label": "이송 중"},
    "idle": {"bg": "#f3f4f6", "border": "#9ca3af", "text": "#374151", "label": "대기"},
    "charging": {"bg": "#dbeafe", "border": "#3b82f6", "text": "#1e40af", "label": "충전 중"},
    "error": {"bg": "#fee2e2", "border": "#ef4444", "text": "#991b1b", "label": "오류"},
}


def _status_key(s: str) -> str:
    s = (s or "").lower()
    if s in ("running", "active", "busy", "moving"):
        return "running"
    if s == "charging":
        return "charging"
    if s in ("error", "fault", "alarm"):
        return "error"
    return "idle"


def _battery_color(level: int) -> str:
    if level >= 60:
        return "#10b981"  # green
    if level >= 30:
        return "#f59e0b"  # amber
    return "#ef4444"       # red


class AmrStatusCard(QFrame):
    """AMR 한 대의 상태 카드.

    표시 내용:
      - AMR ID + 상태 배지
      - 배터리 프로그레스 바 (20% 미만 빨강)
      - 속도, 위치
      - 현재 작업 ID + 적재 물품
    """

    def __init__(self, amr_id: str = "-") -> None:
        super().__init__()
        self.setObjectName("amrCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(170)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # 상단: ID + 상태 배지
        header = QHBoxLayout()
        header.setSpacing(8)

        self._id_label = QLabel(amr_id)
        self._id_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #111827;"
        )
        header.addWidget(self._id_label)

        header.addStretch()

        self._status_badge = QLabel("-")
        self._status_badge.setAlignment(Qt.AlignCenter)
        self._status_badge.setFixedHeight(22)
        self._status_badge.setContentsMargins(10, 0, 10, 0)
        header.addWidget(self._status_badge)

        layout.addLayout(header)

        # 배터리
        bat_row = QHBoxLayout()
        bat_row.setSpacing(8)
        bat_label = QLabel("배터리")
        bat_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        bat_label.setFixedWidth(46)
        bat_row.addWidget(bat_label)

        self._battery_bar = QProgressBar()
        self._battery_bar.setRange(0, 100)
        self._battery_bar.setValue(0)
        self._battery_bar.setTextVisible(True)
        self._battery_bar.setFormat("%p%")
        self._battery_bar.setFixedHeight(18)
        bat_row.addWidget(self._battery_bar, stretch=1)

        layout.addLayout(bat_row)

        # 정보 그리드 (속도 / 위치)
        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        self._speed_label = self._info_label("속도", "0.0 m/s")
        info_row.addWidget(self._speed_label, stretch=1)

        self._loc_label = self._info_label("위치", "-")
        info_row.addWidget(self._loc_label, stretch=2)

        layout.addLayout(info_row)

        # 현재 작업
        self._task_label = QLabel("현재 작업: -")
        self._task_label.setStyleSheet("color: #374151; font-size: 11px;")
        self._task_label.setWordWrap(True)
        layout.addWidget(self._task_label)

        layout.addStretch()
        self.update_from_dict({"id": amr_id})

    def _info_label(self, title: str, value: str) -> QWidget:
        box = QWidget()
        v = QVBoxLayout(box)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)

        t = QLabel(title)
        t.setStyleSheet("color: #9ca3af; font-size: 10px;")
        v.addWidget(t)

        val = QLabel(value)
        val.setObjectName("amrInfoValue")
        val.setStyleSheet("color: #111827; font-size: 12px; font-weight: 600;")
        v.addWidget(val)

        return box

    def update_from_dict(self, data: dict[str, Any]) -> None:
        amr_id = str(data.get("id", "-"))
        self._id_label.setText(amr_id)

        # 상태 배지
        status = _status_key(str(data.get("status", "idle")))
        style = STATUS_STYLE[status]
        self._status_badge.setText(style["label"])
        self._status_badge.setStyleSheet(
            f"background-color: {style['bg']};"
            f"color: {style['text']};"
            f"border: 1px solid {style['border']};"
            "border-radius: 11px;"
            "font-size: 10px;"
            "font-weight: bold;"
            "padding: 2px 10px;"
        )

        # 배터리
        try:
            battery = int(data.get("battery", 0) or 0)
        except (TypeError, ValueError):
            battery = 0
        self._battery_bar.setValue(battery)
        color = _battery_color(battery)
        self._battery_bar.setStyleSheet(
            "QProgressBar {"
            "  background-color: #f3f4f6;"
            "  border: 1px solid #e5e7eb;"
            "  border-radius: 9px;"
            "  text-align: center;"
            "  font-size: 10px;"
            "  font-weight: bold;"
            "  color: #111827;"
            "}"
            f"QProgressBar::chunk {{"
            f"  background-color: {color};"
            "  border-radius: 8px;"
            "}"
        )

        # 속도
        speed = data.get("speed", 0)
        try:
            speed_text = f"{float(speed):.1f} m/s"
        except (TypeError, ValueError):
            speed_text = "-"
        self._info_value(self._speed_label, speed_text)

        # 위치
        location = str(data.get("location", data.get("install_location", "-"))) or "-"
        self._info_value(self._loc_label, location)

        # 현재 작업
        task = data.get("current_task") or data.get("task_id") or "-"
        cargo = data.get("cargo") or data.get("loaded_item") or ""
        task_text = f"현재 작업: {task}"
        if cargo:
            task_text += f" ({cargo})"
        self._task_label.setText(task_text)

    @staticmethod
    def _info_value(container: QWidget, text: str) -> None:
        value = container.findChild(QLabel, "amrInfoValue")
        if value:
            value.setText(text)


__all__ = ["AmrStatusCard", "STATUS_STYLE"]
