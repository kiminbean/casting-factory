"""창고 랙 그리드 위젯 (4행 × 6열).

구역(A/B)별 랙 점유 상태를 색상으로 표시.
각 셀 hover 시 상세 정보 팝업.
"""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


# 랙 셀 치수
CELL_W = 80
CELL_H = 50
GAP = 6
AISLE_GAP = 18  # A/B 구역 사이 통로
ROWS = 4
COLS_PER_ZONE = 3  # 구역당 열 수 (총 6열)


# 점유 상태별 색상
STATUS_COLORS = {
    "empty": {"fill": "#f3f4f6", "border": "#d1d5db", "text": "#6b7280"},
    "partial": {"fill": "#fef3c7", "border": "#f59e0b", "text": "#92400e"},
    "full": {"fill": "#d1fae5", "border": "#10b981", "text": "#065f46"},
    "reserved": {"fill": "#dbeafe", "border": "#3b82f6", "text": "#1e40af"},
    "locked": {"fill": "#fee2e2", "border": "#ef4444", "text": "#991b1b"},
}


class RackCell(QGraphicsRectItem):
    """랙 셀 아이템."""

    def __init__(self, rack_id: str, zone: str) -> None:
        super().__init__(0, 0, CELL_W, CELL_H)
        self._rack_id = rack_id
        self._zone = zone
        self._status = "empty"
        self._content = ""

        self._id_label = QGraphicsSimpleTextItem(rack_id, self)
        self._id_label.setFont(QFont("Helvetica Neue", 9, QFont.Bold))
        self._id_label.setPos(6, 4)

        self._content_label = QGraphicsSimpleTextItem("", self)
        self._content_label.setFont(QFont("Helvetica Neue", 8))
        self._content_label.setPos(6, 22)

        self.setAcceptHoverEvents(True)
        self._apply_status()

    def set_data(self, status: str, content: str = "", qty: int = 0) -> None:
        self._status = status
        self._content = content
        text = content[:10] if content else "-"
        if qty:
            text = f"{text}\n×{qty}"
        self._content_label.setText(text)
        self._apply_status()
        self.setToolTip(
            f"랙 {self._rack_id}\n"
            f"구역: {self._zone}\n"
            f"상태: {status}\n"
            f"내용: {content or '비어있음'}\n"
            f"수량: {qty}"
        )

    def _apply_status(self) -> None:
        colors = STATUS_COLORS.get(self._status, STATUS_COLORS["empty"])
        self.setBrush(QBrush(QColor(colors["fill"])))
        self.setPen(QPen(QColor(colors["border"]), 2))
        text_color = QColor(colors["text"])
        self._id_label.setBrush(QBrush(text_color))
        self._content_label.setBrush(QBrush(text_color))


class WarehouseRackScene(QGraphicsScene):
    """창고 랙 씬."""

    def __init__(self) -> None:
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("#ffffff")))

        # 전체 폭 계산
        zone_w = COLS_PER_ZONE * CELL_W + (COLS_PER_ZONE - 1) * GAP
        total_w = zone_w * 2 + AISLE_GAP + 40  # 40 = 좌우 여백
        total_h = ROWS * CELL_H + (ROWS - 1) * GAP + 50

        self.setSceneRect(0, 0, total_w, total_h)

        self._cells: dict[str, RackCell] = {}
        self._draw_zones()
        self._draw_cells()

    def _draw_zones(self) -> None:
        zone_w = COLS_PER_ZONE * CELL_W + (COLS_PER_ZONE - 1) * GAP

        # Zone A 라벨
        label_a = QGraphicsSimpleTextItem("A 구역")
        label_a.setFont(QFont("Helvetica Neue", 11, QFont.Bold))
        label_a.setBrush(QBrush(QColor("#374151")))
        label_a.setPos(20 + zone_w / 2 - 25, 4)
        self.addItem(label_a)

        # Zone B 라벨
        label_b = QGraphicsSimpleTextItem("B 구역")
        label_b.setFont(QFont("Helvetica Neue", 11, QFont.Bold))
        label_b.setBrush(QBrush(QColor("#374151")))
        label_b.setPos(20 + zone_w + AISLE_GAP + zone_w / 2 - 25, 4)
        self.addItem(label_b)

        # 통로 표시 (회색 점선)
        aisle_x = 20 + zone_w + AISLE_GAP / 2
        pen = QPen(QColor("#e5e7eb"), 1, Qt.DashLine)
        self.addLine(aisle_x, 30, aisle_x, 30 + ROWS * (CELL_H + GAP), pen)

    def _draw_cells(self) -> None:
        start_y = 26

        for row in range(ROWS):
            for zone_idx, zone in enumerate(["A", "B"]):
                for col in range(COLS_PER_ZONE):
                    rack_id = f"{zone}{row + 1}-{col + 1}"
                    cell = RackCell(rack_id, zone)
                    x = (
                        20
                        + zone_idx * (COLS_PER_ZONE * CELL_W + (COLS_PER_ZONE - 1) * GAP + AISLE_GAP)
                        + col * (CELL_W + GAP)
                    )
                    y = start_y + row * (CELL_H + GAP)
                    cell.setPos(x, y)
                    self.addItem(cell)
                    self._cells[rack_id] = cell

    def update_racks(self, racks: list[dict[str, Any]]) -> None:
        """racks: [{'id':'A1-1','status':'full','content':'맨홀뚜껑','qty':12}, ...]"""
        for rack in racks:
            rack_id = str(rack.get("id", ""))
            cell = self._cells.get(rack_id)
            if cell:
                cell.set_data(
                    status=str(rack.get("status", "empty")),
                    content=str(rack.get("content", "")),
                    qty=int(rack.get("qty", 0) or 0),
                )


class WarehouseRackWidget(QFrame):
    """창고 랙 뷰 + 범례."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("tableCard")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        title = QLabel("창고 랙 (4행 × 6열)")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self._scene = WarehouseRackScene()
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(QPainter.Antialiasing)
        self._view.setFrameShape(QFrame.NoFrame)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._view.setBackgroundBrush(QBrush(QColor("#ffffff")))
        layout.addWidget(self._view, stretch=1)

        # 범례
        legend_row = QHBoxLayout()
        legend_row.setSpacing(14)
        legend_items = [
            ("비어있음", STATUS_COLORS["empty"]["fill"], STATUS_COLORS["empty"]["border"]),
            ("부분점유", STATUS_COLORS["partial"]["fill"], STATUS_COLORS["partial"]["border"]),
            ("점유", STATUS_COLORS["full"]["fill"], STATUS_COLORS["full"]["border"]),
            ("예약", STATUS_COLORS["reserved"]["fill"], STATUS_COLORS["reserved"]["border"]),
            ("잠김", STATUS_COLORS["locked"]["fill"], STATUS_COLORS["locked"]["border"]),
        ]
        for label, fill, border in legend_items:
            item = _LegendItem(label, fill, border)
            legend_row.addWidget(item)
        legend_row.addStretch()
        layout.addLayout(legend_row)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._view.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._view.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def update_racks(self, racks: list[dict[str, Any]]) -> None:
        self._scene.update_racks(racks)


class _LegendItem(QWidget):
    def __init__(self, label: str, fill: str, border: str) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        swatch = QLabel()
        swatch.setFixedSize(14, 10)
        swatch.setStyleSheet(
            f"background-color: {fill}; border: 1.5px solid {border}; border-radius: 2px;"
        )
        layout.addWidget(swatch)

        txt = QLabel(label)
        txt.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(txt)
