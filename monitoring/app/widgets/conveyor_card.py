"""컨베이어 상태 카드 - ESP32 v4.0 MQTT 페이로드 시각화.

토픽 conveyor/<id>/status 의 JSON:
    {"state":"running","motor":true,
     "tof1":{"mm":50,"det":true},
     "tof2":{"mm":150,"det":false},
     "count":3,
     "wifi":true,"mqtt":true}
"""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)


STATE_STYLE = {
    "idle":      {"bg": "#f3f4f6", "fg": "#374151", "bd": "#9ca3af", "label": "대기"},
    "running":   {"bg": "#d1fae5", "fg": "#065f46", "bd": "#10b981", "label": "이송 중"},
    "stopped":   {"bg": "#fef3c7", "fg": "#854d0e", "bd": "#f59e0b", "label": "검사 대기"},
    "post_run":  {"bg": "#dbeafe", "fg": "#1e40af", "bd": "#3b82f6", "label": "후처리"},
    "clearing":  {"bg": "#ede9fe", "fg": "#5b21b6", "bd": "#8b5cf6", "label": "배출 중"},
    "error":     {"bg": "#fee2e2", "fg": "#991b1b", "bd": "#ef4444", "label": "오류"},
    "offline":   {"bg": "#f3f4f6", "fg": "#6b7280", "bd": "#d1d5db", "label": "오프라인"},
}


def _sensor_color(mm: int, detected: bool) -> str:
    if detected:
        return "#10b981"
    if mm and mm > 0 and mm < 200:
        return "#6b7280"
    return "#d1d5db"


class ConveyorCard(QFrame):
    """컨베이어 상태 카드 한 대."""

    def __init__(self, conveyor_id: str) -> None:
        super().__init__()
        self.setObjectName("tableCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(180)

        self._conveyor_id = conveyor_id
        self._online = False

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # 상단: ID + 상태 배지
        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel(f"Conveyor #{conveyor_id}")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        header.addWidget(title)
        header.addStretch()

        self._connection_dot = QLabel("●")
        self._connection_dot.setStyleSheet("color: #d1d5db; font-size: 14px;")
        header.addWidget(self._connection_dot)

        self._state_badge = QLabel("offline")
        self._state_badge.setAlignment(Qt.AlignCenter)
        self._state_badge.setFixedHeight(22)
        header.addWidget(self._state_badge)

        root.addLayout(header)

        # 중단: 모터 + 카운트 (gridy)
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(2)

        motor_lbl = QLabel("모터")
        motor_lbl.setStyleSheet("color: #9ca3af; font-size: 10px;")
        self._motor_val = QLabel("-")
        self._motor_val.setStyleSheet("color: #111827; font-size: 14px; font-weight: bold;")
        grid.addWidget(motor_lbl, 0, 0)
        grid.addWidget(self._motor_val, 1, 0)

        count_lbl = QLabel("사이클")
        count_lbl.setStyleSheet("color: #9ca3af; font-size: 10px;")
        self._count_val = QLabel("0")
        self._count_val.setStyleSheet("color: #111827; font-size: 14px; font-weight: bold;")
        grid.addWidget(count_lbl, 0, 1)
        grid.addWidget(self._count_val, 1, 1)

        speed_lbl = QLabel("속도")
        speed_lbl.setStyleSheet("color: #9ca3af; font-size: 10px;")
        self._speed_val = QLabel("-")
        self._speed_val.setStyleSheet("color: #111827; font-size: 14px; font-weight: bold;")
        grid.addWidget(speed_lbl, 0, 2)
        grid.addWidget(self._speed_val, 1, 2)

        root.addLayout(grid)

        # 하단: TOF 센서 2개
        tof_row = QHBoxLayout()
        tof_row.setSpacing(14)

        self._tof1_label, self._tof1_value, self._tof1_dot = self._make_tof_row("TOF1 (입구)")
        tof_row.addLayout(self._tof1_label)

        self._tof2_label, self._tof2_value, self._tof2_dot = self._make_tof_row("TOF2 (출구)")
        tof_row.addLayout(self._tof2_label)

        root.addLayout(tof_row)
        root.addStretch()

        self._apply_state("offline")

    def _make_tof_row(self, name: str):
        layout = QVBoxLayout()
        layout.setSpacing(2)

        header = QHBoxLayout()
        header.setSpacing(4)

        dot = QLabel("●")
        dot.setStyleSheet("color: #d1d5db; font-size: 12px;")
        header.addWidget(dot)

        lbl = QLabel(name)
        lbl.setStyleSheet("color: #9ca3af; font-size: 10px;")
        header.addWidget(lbl)
        header.addStretch()

        layout.addLayout(header)

        value = QLabel("-")
        value.setStyleSheet("color: #374151; font-size: 13px; font-weight: 600;")
        layout.addWidget(value)

        return layout, value, dot

    def _apply_state(self, state: str) -> None:
        style = STATE_STYLE.get(state, STATE_STYLE["offline"])
        self._state_badge.setText(style["label"])
        self._state_badge.setStyleSheet(
            f"background-color: {style['bg']};"
            f"color: {style['fg']};"
            f"border: 1px solid {style['bd']};"
            "border-radius: 11px;"
            "font-size: 10px;"
            "font-weight: bold;"
            "padding: 2px 12px;"
        )

    def set_online(self, online: bool) -> None:
        self._online = online
        color = "#10b981" if online else "#d1d5db"
        self._connection_dot.setStyleSheet(f"color: {color}; font-size: 14px;")

    def update_from_payload(self, payload: dict[str, Any]) -> None:
        state = str(payload.get("state", "offline"))
        self._apply_state(state)

        # 모터
        motor = payload.get("motor")
        if isinstance(motor, dict):
            running = bool(motor.get("running"))
            speed = motor.get("speed", motor.get("spd", 0))
            direction = motor.get("dir", "")
        else:
            running = bool(motor)
            speed = payload.get("speed", 0)
            direction = ""

        self._motor_val.setText("ON" if running else "OFF")
        self._motor_val.setStyleSheet(
            f"color: {'#10b981' if running else '#6b7280'};"
            "font-size: 14px;"
            "font-weight: bold;"
        )
        speed_text = f"{speed}"
        if direction:
            speed_text += f" ({direction})"
        self._speed_val.setText(speed_text)

        # 카운트
        count = payload.get("count", 0)
        self._count_val.setText(str(count))

        # TOF1
        tof1 = payload.get("tof1", {})
        self._update_tof(self._tof1_value, self._tof1_dot, tof1)

        # TOF2
        tof2 = payload.get("tof2", {})
        self._update_tof(self._tof2_value, self._tof2_dot, tof2)

    @staticmethod
    def _update_tof(value_label: QLabel, dot_label: QLabel, tof: dict[str, Any]) -> None:
        mm = tof.get("mm", -1)
        det = bool(tof.get("det", False))
        try:
            mm_int = int(mm)
        except (TypeError, ValueError):
            mm_int = -1

        if mm_int < 0:
            value_label.setText("-- mm")
            dot_label.setStyleSheet("color: #d1d5db; font-size: 12px;")
            return

        value_label.setText(f"{mm_int} mm" + (" · 감지" if det else ""))
        dot_label.setStyleSheet(
            f"color: {_sensor_color(mm_int, det)}; font-size: 12px;"
        )

    def mark_offline(self) -> None:
        self._apply_state("offline")
        self.set_online(False)
        self._motor_val.setText("-")
        self._count_val.setText("0")
        self._speed_val.setText("-")


__all__ = ["ConveyorCard"]
