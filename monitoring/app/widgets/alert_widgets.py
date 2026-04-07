"""알림 관련 위젯 (v0.8).

1. AlertListItem - severity 아이콘 + 색상 + pulse 인디케이터
2. ToastNotification - critical 알람 토스트 팝업 (5초 자동 사라짐)
"""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


LEVEL_STYLE = {
    "critical": {"icon": "●", "color": "#ef4444", "bg": "#fee2e2", "label": "긴급"},
    "error":    {"icon": "●", "color": "#ef4444", "bg": "#fee2e2", "label": "오류"},
    "warning":  {"icon": "▲", "color": "#f59e0b", "bg": "#fef3c7", "label": "경고"},
    "info":     {"icon": "ℹ", "color": "#3b82f6", "bg": "#dbeafe", "label": "정보"},
    "success":  {"icon": "✓", "color": "#10b981", "bg": "#d1fae5", "label": "완료"},
}


def _normalize_level(raw: str) -> str:
    s = (raw or "").lower()
    if s in ("critical", "fatal"):
        return "critical"
    if s in ("error", "danger"):
        return "error"
    if s in ("warn", "warning"):
        return "warning"
    if s in ("success", "ok"):
        return "success"
    return "info"


class AlertListItem(QFrame):
    """개별 알림 항목 - 아이콘 + 메시지 + 시각."""

    def __init__(self, alert: dict[str, Any]) -> None:
        super().__init__()
        self.setObjectName("alertItem")
        level = _normalize_level(str(alert.get("level", "info")))
        style = LEVEL_STYLE[level]

        self.setStyleSheet(
            "#alertItem {"
            f"  background-color: {style['bg']};"
            f"  border-left: 4px solid {style['color']};"
            "  border-radius: 4px;"
            "}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(10)

        icon = QLabel(style["icon"])
        icon.setStyleSheet(
            f"color: {style['color']}; font-size: 15px; font-weight: bold;"
            "background: transparent; border: none;"
        )
        icon.setFixedWidth(18)
        layout.addWidget(icon)

        # 본문 (레벨 라벨 + 메시지)
        body = QVBoxLayout()
        body.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(6)
        level_badge = QLabel(style["label"])
        level_badge.setStyleSheet(
            f"color: {style['color']};"
            "font-size: 10px; font-weight: bold;"
            "background: transparent; border: none;"
        )
        top.addWidget(level_badge)

        source = alert.get("source", "")
        if source:
            src_label = QLabel(f"· {source}")
            src_label.setStyleSheet(
                "color: #6b7280; font-size: 10px; background: transparent; border: none;"
            )
            top.addWidget(src_label)
        top.addStretch()

        ts = alert.get("created_at", "")
        if ts:
            ts_label = QLabel(str(ts))
            ts_label.setStyleSheet(
                "color: #9ca3af; font-size: 10px; background: transparent; border: none;"
            )
            top.addWidget(ts_label)
        body.addLayout(top)

        msg = QLabel(str(alert.get("message", "")))
        msg.setStyleSheet(
            "color: #111827; font-size: 12px; background: transparent; border: none;"
        )
        msg.setWordWrap(True)
        body.addWidget(msg)

        layout.addLayout(body, stretch=1)


class ToastNotification(QWidget):
    """우상단에 뜨는 알람 토스트 (5초 자동 fadeout).

    생성 즉시 부모 윈도우 우상단에 표시되며, 타이머 종료 시 페이드아웃 후 삭제.
    """

    FADE_IN_MS = 250
    DISPLAY_MS = 5000
    FADE_OUT_MS = 400

    def __init__(self, parent: QWidget, level: str, title: str, message: str) -> None:
        super().__init__(parent)
        level_key = _normalize_level(level)
        style = LEVEL_STYLE[level_key]

        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        container = QFrame(self)
        container.setObjectName("toast")
        container.setStyleSheet(
            "#toast {"
            "  background-color: #111827;"
            f"  border-left: 5px solid {style['color']};"
            "  border-radius: 8px;"
            "}"
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(14, 12, 18, 12)
        layout.setSpacing(12)

        icon = QLabel(style["icon"])
        icon.setStyleSheet(
            f"color: {style['color']}; font-size: 20px; font-weight: bold; background: transparent;"
        )
        icon.setFixedWidth(26)
        layout.addWidget(icon)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)

        title_label = QLabel(f"{style['label']} · {title}")
        title_label.setStyleSheet(
            f"color: {style['color']}; font-size: 11px; font-weight: bold; background: transparent;"
        )
        text_box.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setStyleSheet(
            "color: #f9fafb; font-size: 13px; background: transparent;"
        )
        msg_label.setWordWrap(True)
        msg_label.setMinimumWidth(260)
        msg_label.setMaximumWidth(340)
        text_box.addWidget(msg_label)

        layout.addLayout(text_box, stretch=1)

        self.adjustSize()

        # 부모 우상단에 고정
        self._position_top_right()

        # 페이드인
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in.setDuration(self.FADE_IN_MS)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_in.start()

        # 자동 페이드아웃
        QTimer.singleShot(self.DISPLAY_MS, self._start_fade_out)

    def _position_top_right(self) -> None:
        parent = self.parent()
        if parent is None:
            return
        parent_geom = parent.geometry()
        x = parent_geom.width() - self.width() - 20
        y = 70  # 헤더 아래 여백
        self.move(x, y)

    def _start_fade_out(self) -> None:
        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out.setDuration(self.FADE_OUT_MS)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out.finished.connect(self.deleteLater)
        self._fade_out.start()


__all__ = [
    "AlertListItem",
    "ToastNotification",
    "LEVEL_STYLE",
    "_normalize_level",
]
