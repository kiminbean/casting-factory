"""2D 공장 맵 위젯 — 실제 공장 레이아웃 기반.

5개 구역: Postprocessing, Outbound, Storage, Charging, Casting
장비: 컨베이어, Cobot A/B, AMR 3대, Melting Furnace, Mold, Patterns
"""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QPointF, QRectF, QTimer, Qt
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QStyleOptionGraphicsItem,
    QWidget,
)

# ---------------------------------------------------------------------------
# 씬 크기 (이미지 비율 ~1300x650)
# ---------------------------------------------------------------------------
SCENE_W = 1300
SCENE_H = 700

# ---------------------------------------------------------------------------
# 색상
# ---------------------------------------------------------------------------
BG_COLOR = "#e8e8e8"           # 전체 배경
ZONE_BG = QColor(160, 180, 210, 140)   # 구역 배경 (반투명 파란)
ZONE_BORDER = QColor(60, 70, 110)      # 구역 파선 테두리
LABEL_BG = "#ffd700"           # 노란 라벨
LABEL_TEXT = "#000000"
EQUIP_BG = "#ffffff"           # 장비 흰색 배경
CONVEYOR_COLOR = "#228b22"     # 컨베이어 초록
RED_BLOCK = "#ff3300"          # 빨간 사각형
MOLD_COLOR = "#b0d4f1"         # 하늘색 몰드
AMR_COLOR = "#e6c619"          # AMR 노란색
CHARGING_BG = QColor(200, 200, 200)
OUTBOUND_GRAD_TOP = "#d0d0d0"
OUTBOUND_GRAD_BOT = "#a0a0a0"
WORKER_COLOR = "#333333"

# AMR 상태 색상
STATUS_COLORS: dict[str, dict[str, str]] = {
    "active": {"dot": "#4ade80", "border": "#22c55e"},
    "idle": {"dot": "#9ca3af", "border": "#6b7280"},
    "warning": {"dot": "#fbbf24", "border": "#f59e0b"},
    "error": {"dot": "#f87171", "border": "#ef4444"},
    "charging": {"dot": "#60a5fa", "border": "#60a5fa"},
}


def _status_key(raw: str) -> str:
    s = (raw or "").lower()
    mapping = {
        "running": "active", "active": "active", "completed": "active",
        "idle": "idle", "waiting": "idle",
        "warning": "warning", "maintenance": "warning",
        "error": "error", "alarm": "error",
        "charging": "charging",
    }
    return mapping.get(s, "idle")


# ---------------------------------------------------------------------------
# Helper: 노란 라벨
# ---------------------------------------------------------------------------
def _add_label(scene: QGraphicsScene, x: float, y: float, text: str,
               font_size: int = 9, bg: str = LABEL_BG) -> None:
    font = QFont("Sans", font_size, QFont.Bold)
    txt = QGraphicsSimpleTextItem(text)
    txt.setFont(font)
    txt.setBrush(QBrush(QColor(LABEL_TEXT)))
    tr = txt.boundingRect()
    pad_x, pad_y = 6, 3
    rect = QGraphicsRectItem(x, y, tr.width() + pad_x * 2, tr.height() + pad_y * 2)
    rect.setBrush(QBrush(QColor(bg)))
    rect.setPen(QPen(QColor("#333333"), 1))
    rect.setZValue(10)
    scene.addItem(rect)
    txt.setPos(x + pad_x, y + pad_y)
    txt.setZValue(11)
    scene.addItem(txt)


# ---------------------------------------------------------------------------
# Helper: 흰색 박스 + 텍스트
# ---------------------------------------------------------------------------
def _add_box(scene: QGraphicsScene, x: float, y: float, w: float, h: float,
             text: str, font_size: int = 9, bg: str = EQUIP_BG,
             border: str = "#333333") -> QGraphicsRectItem:
    rect = QGraphicsRectItem(x, y, w, h)
    rect.setBrush(QBrush(QColor(bg)))
    rect.setPen(QPen(QColor(border), 1))
    rect.setZValue(10)
    scene.addItem(rect)
    if text:
        font = QFont("Sans", font_size)
        txt = QGraphicsSimpleTextItem(text)
        txt.setFont(font)
        txt.setBrush(QBrush(QColor("#000000")))
        tr = txt.boundingRect()
        txt.setPos(x + (w - tr.width()) / 2, y + (h - tr.height()) / 2)
        txt.setZValue(11)
        scene.addItem(txt)
    return rect


# ---------------------------------------------------------------------------
# Helper: 원형 Cobot
# ---------------------------------------------------------------------------
def _add_cobot(scene: QGraphicsScene, cx: float, cy: float, r: float,
               label: str) -> None:
    ellipse = QGraphicsEllipseItem(cx - r, cy - r, r * 2, r * 2)
    ellipse.setBrush(QBrush(QColor(EQUIP_BG)))
    ellipse.setPen(QPen(QColor("#333333"), 2))
    ellipse.setZValue(10)
    scene.addItem(ellipse)
    font = QFont("Sans", 18, QFont.Bold)
    txt = QGraphicsSimpleTextItem(label)
    txt.setFont(font)
    txt.setBrush(QBrush(QColor("#000000")))
    tr = txt.boundingRect()
    txt.setPos(cx - tr.width() / 2, cy - tr.height() / 2)
    txt.setZValue(11)
    scene.addItem(txt)


# ---------------------------------------------------------------------------
# Helper: 스틱맨 작업자
# ---------------------------------------------------------------------------
def _add_worker(scene: QGraphicsScene, cx: float, base_y: float,
                label: str) -> None:
    pen = QPen(QColor(WORKER_COLOR), 2)
    head_r = 8
    # head
    head = QGraphicsEllipseItem(cx - head_r, base_y, head_r * 2, head_r * 2)
    head.setPen(pen)
    head.setBrush(QBrush(QColor("#ffffff")))
    head.setZValue(12)
    scene.addItem(head)
    # body
    body = scene.addLine(cx, base_y + head_r * 2, cx, base_y + head_r * 2 + 25, pen)
    body.setZValue(12)
    # arms
    arms = scene.addLine(cx - 12, base_y + head_r * 2 + 10,
                         cx + 12, base_y + head_r * 2 + 10, pen)
    arms.setZValue(12)
    # legs
    scene.addLine(cx, base_y + head_r * 2 + 25,
                  cx - 10, base_y + head_r * 2 + 40, pen).setZValue(12)
    scene.addLine(cx, base_y + head_r * 2 + 25,
                  cx + 10, base_y + head_r * 2 + 40, pen).setZValue(12)
    # label
    font = QFont("Sans", 7)
    txt = QGraphicsSimpleTextItem(label)
    txt.setFont(font)
    txt.setBrush(QBrush(QColor("#000000")))
    tr = txt.boundingRect()
    txt.setPos(cx - tr.width() / 2, base_y + head_r * 2 + 44)
    txt.setZValue(12)
    scene.addItem(txt)


# ---------------------------------------------------------------------------
# Helper: 구역 (파선 테두리 + 반투명 배경 + 제목)
# ---------------------------------------------------------------------------
def _add_zone(scene: QGraphicsScene, x: float, y: float, w: float, h: float,
              title: str) -> None:
    rect = QGraphicsRectItem(x, y, w, h)
    rect.setBrush(QBrush(ZONE_BG))
    pen = QPen(ZONE_BORDER, 2, Qt.DashLine)
    rect.setPen(pen)
    rect.setZValue(1)
    scene.addItem(rect)
    # 제목 라벨 (상단 중앙)
    font = QFont("Sans", 10)
    txt = QGraphicsSimpleTextItem(title)
    txt.setFont(font)
    txt.setBrush(QBrush(QColor("#000000")))
    tr = txt.boundingRect()
    # 흰색 배경 + 테두리
    pad = 4
    lbl_rect = QGraphicsRectItem(
        x + (w - tr.width()) / 2 - pad, y - tr.height() / 2 - pad / 2,
        tr.width() + pad * 2, tr.height() + pad,
    )
    lbl_rect.setBrush(QBrush(QColor("#ffffff")))
    lbl_rect.setPen(QPen(QColor("#333333"), 1))
    lbl_rect.setZValue(2)
    scene.addItem(lbl_rect)
    txt.setPos(x + (w - tr.width()) / 2, y - tr.height() / 2 - pad / 2 + 1)
    txt.setZValue(3)
    scene.addItem(txt)


# ===================================================================
# FactoryMapScene
# ===================================================================
class FactoryMapScene(QGraphicsScene):
    """공장 레이아웃 씬 — 이미지 기반 5구역 배치."""

    ANIMATION_INTERVAL_MS = 30
    ANIMATION_STEP = 0.12

    def __init__(self) -> None:
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor(BG_COLOR)))
        self.setSceneRect(0, 0, SCENE_W, SCENE_H)
        self._amr_state: dict[str, dict[str, Any]] = {}

        self._draw_all()

        self._anim_timer = QTimer()
        self._anim_timer.setInterval(self.ANIMATION_INTERVAL_MS)
        self._anim_timer.timeout.connect(self._tick_animation)
        self._anim_timer.start()

    # ------------------------------------------------------------------
    # 전체 그리기
    # ------------------------------------------------------------------
    def _draw_all(self) -> None:
        # 전체 외곽선
        outer = QGraphicsRectItem(5, 5, SCENE_W - 10, SCENE_H - 10)
        outer.setPen(QPen(QColor("#333333"), 2))
        outer.setBrush(QBrush(Qt.NoBrush))
        outer.setZValue(0)
        self.addItem(outer)

        self._draw_postprocessing_zone()
        self._draw_outbound_zone()
        self._draw_storage_zone()
        self._draw_charging_zone()
        self._draw_casting_zone()

    # ------------------------------------------------------------------
    # 1) Postprocessing zone (좌상단)
    # ------------------------------------------------------------------
    def _draw_postprocessing_zone(self) -> None:
        zx, zy, zw, zh = 20, 25, 680, 210
        _add_zone(self, zx, zy, zw, zh, "Postprocessing zone")

        # Worker 구역 (회색 박스)
        wx, wy, ww, wh = 40, 65, 160, 150
        worker_box = QGraphicsRectItem(wx, wy, ww, wh)
        worker_box.setBrush(QBrush(QColor("#c8c8c8")))
        worker_box.setPen(QPen(QColor("#999999"), 1))
        worker_box.setZValue(5)
        self.addItem(worker_box)

        _add_worker(self, 90, 75, "Unloading\nWorker")
        _add_worker(self, 160, 75, "Postprocessing\nWorker")

        # 컨베이어 (초록 직사각형)
        conv = QGraphicsRectItem(220, 95, 280, 45)
        conv.setBrush(QBrush(QColor(CONVEYOR_COLOR)))
        conv.setPen(QPen(QColor("#1a6b1a"), 2))
        conv.setZValue(10)
        self.addItem(conv)

        # Conveyor Waiting Zone 라벨
        _add_label(self, 520, 85, "Conveyor\nWaiting\nZone")

    # ------------------------------------------------------------------
    # 2) Outbound zone (우상단)
    # ------------------------------------------------------------------
    def _draw_outbound_zone(self) -> None:
        zx, zy, zw, zh = 1050, 25, 230, 190
        _add_zone(self, zx, zy, zw, zh, "Outbound zone")

        # 은색 그라데이션 사각형
        grad_rect = QGraphicsRectItem(1070, 55, 190, 140)
        gradient = QLinearGradient(1070, 55, 1260, 195)
        gradient.setColorAt(0, QColor(OUTBOUND_GRAD_TOP))
        gradient.setColorAt(1, QColor(OUTBOUND_GRAD_BOT))
        grad_rect.setBrush(QBrush(gradient))
        grad_rect.setPen(QPen(QColor("#888888"), 1))
        grad_rect.setZValue(10)
        self.addItem(grad_rect)

    # ------------------------------------------------------------------
    # 3) Storage zone (좌하단)
    # ------------------------------------------------------------------
    def _draw_storage_zone(self) -> None:
        zx, zy, zw, zh = 20, 280, 420, 345
        _add_zone(self, zx, zy, zw, zh, "Storage zone")

        # Defect Box
        _add_box(self, 45, 320, 80, 50, "Defect\nBox", 8)

        # 빨간 사각형 (불량품)
        red1 = QGraphicsRectItem(145, 370, 55, 40)
        red1.setBrush(QBrush(QColor(RED_BLOCK)))
        red1.setPen(QPen(QColor("#cc0000"), 1))
        red1.setZValue(10)
        self.addItem(red1)

        # Outbound Waiting Zone
        _add_label(self, 255, 310, "Outbound\nWaiting\nZone")

        # Putaway Waiting Zone
        _add_label(self, 275, 400, "Putaway\nWaiting\nZone")

        # Cobot B
        _add_cobot(self, 170, 450, 35, "B")

        # Good product storage rack (호 모양 — 간략화: 큰 반원)
        path = QPainterPath()
        path.moveTo(45, 560)
        path.cubicTo(45, 480, 145, 480, 145, 560)
        path_item = self.addPath(path, QPen(QColor("#333333"), 2),
                                 QBrush(QColor("#ffffff")))
        path_item.setZValue(10)

        # Good product storage rack 라벨
        font = QFont("Sans", 7)
        rack_txt = QGraphicsSimpleTextItem("Good product\nstorage rack")
        rack_txt.setFont(font)
        rack_txt.setBrush(QBrush(QColor("#000000")))
        rack_txt.setPos(50, 565)
        rack_txt.setZValue(11)
        self.addItem(rack_txt)

    # ------------------------------------------------------------------
    # 4) Charging zone (중앙 하단)
    # ------------------------------------------------------------------
    def _draw_charging_zone(self) -> None:
        zx, zy, zw, zh = 480, 440, 380, 175
        _add_zone(self, zx, zy, zw, zh, "Charging zone")

        # 충전 스테이션 배경 (회색)
        station = QGraphicsRectItem(500, 470, 340, 125)
        station.setBrush(QBrush(CHARGING_BG))
        station.setPen(QPen(QColor("#999999"), 1))
        station.setZValue(5)
        self.addItem(station)

        # AMR 3대 (노란 사각형)
        amr_w, amr_h = 95, 75
        amr_y = 490
        for i, ax in enumerate([515, 625, 735]):
            amr_rect = QGraphicsRectItem(ax, amr_y, amr_w, amr_h)
            amr_rect.setBrush(QBrush(QColor(AMR_COLOR)))
            amr_rect.setPen(QPen(QColor("#b8a000"), 1))
            amr_rect.setZValue(10)
            self.addItem(amr_rect)
            font = QFont("Sans", 11, QFont.Bold)
            txt = QGraphicsSimpleTextItem("Amr")
            txt.setFont(font)
            txt.setBrush(QBrush(QColor("#000000")))
            tr = txt.boundingRect()
            txt.setPos(ax + (amr_w - tr.width()) / 2,
                       amr_y + (amr_h - tr.height()) / 2)
            txt.setZValue(11)
            self.addItem(txt)

    # ------------------------------------------------------------------
    # 5) Casting zone (우측, 세로)
    # ------------------------------------------------------------------
    def _draw_casting_zone(self) -> None:
        zx, zy, zw, zh = 900, 250, 380, 375
        _add_zone(self, zx, zy, zw, zh, "Casting zone")

        # Casting Waiting Zone (노란 라벨)
        _add_label(self, 940, 280, "Casting\nWaiting\nZone")

        # Melting Furnace (파란 테두리 박스)
        _add_box(self, 1190, 275, 75, 50, "Melting\nFurnace", 8,
                 bg="#dce8f5", border="#6688aa")

        # Mold (하늘색 세로 직사각형)
        mold = QGraphicsRectItem(910, 430, 35, 100)
        mold.setBrush(QBrush(QColor(MOLD_COLOR)))
        mold.setPen(QPen(QColor("#7799bb"), 1))
        mold.setZValue(10)
        self.addItem(mold)
        mold_txt = QGraphicsSimpleTextItem("Mold")
        mold_txt.setFont(QFont("Sans", 7))
        mold_txt.setBrush(QBrush(QColor("#000000")))
        mold_txt.setPos(912, 470)
        mold_txt.setZValue(11)
        mold_txt.setRotation(90)
        self.addItem(mold_txt)

        # Cobot A
        _add_cobot(self, 1080, 430, 30, "A")

        # 빨간 사각형 (주조물)
        red2 = QGraphicsRectItem(1140, 410, 45, 50)
        red2.setBrush(QBrush(QColor(RED_BLOCK)))
        red2.setPen(QPen(QColor("#cc0000"), 1))
        red2.setZValue(10)
        self.addItem(red2)

        # 작은 원 2개 (소형 장비)
        for cy in [395, 445]:
            sm = QGraphicsEllipseItem(1000 - 8, cy - 8, 16, 16)
            sm.setBrush(QBrush(QColor("#ffffff")))
            sm.setPen(QPen(QColor("#333333"), 1))
            sm.setZValue(10)
            self.addItem(sm)

        # Patterns (작은 박스 3개 + 라벨)
        for py in [500, 530, 560]:
            _add_box(self, 1130, py, 50, 22, "", 7)
        patterns_txt = QGraphicsSimpleTextItem("Patterns")
        patterns_txt.setFont(QFont("Sans", 8))
        patterns_txt.setBrush(QBrush(QColor("#000000")))
        patterns_txt.setPos(1195, 535)
        patterns_txt.setZValue(11)
        self.addItem(patterns_txt)

    # ------------------------------------------------------------------
    # AMR 실시간 갱신 (기존 로직 유지)
    # ------------------------------------------------------------------
    def update_equipment(self, equipment: list[dict[str, Any]]) -> None:
        amrs = [eq for eq in equipment if str(eq.get("type", "")) == "amr"]
        self._update_amr_markers(amrs)

    def _update_amr_markers(self, amrs: list[dict[str, Any]]) -> None:
        seen: set[str] = set()
        # Charging zone 좌표 기준
        charge_x_start, charge_y = 560, 520
        charge_spacing = 110

        for idx, amr in enumerate(amrs):
            amr_id = str(amr.get("id", ""))
            if not amr_id:
                continue
            seen.add(amr_id)

            status = str(amr.get("status", ""))
            status_key = _status_key(status)
            color_info = STATUS_COLORS.get(status_key, STATUS_COLORS["idle"])
            color = color_info["dot"]

            pos_x_m = amr.get("pos_x")
            pos_y_m = amr.get("pos_y")
            if pos_x_m is not None and pos_y_m is not None:
                target_x = 50 + (float(pos_x_m) / 32.0) * (SCENE_W - 100)
                target_y = 50 + (float(pos_y_m) / 12.0) * (SCENE_H - 100)
            else:
                target_x = charge_x_start + idx * charge_spacing
                target_y = charge_y

            state = self._amr_state.get(amr_id)
            if state is None:
                marker = QGraphicsRectItem(-20, -12, 40, 24)
                marker.setBrush(QBrush(QColor(color)))
                marker.setPen(QPen(QColor(color_info["border"]), 2))
                marker.setZValue(50)
                self.addItem(marker)

                label = QGraphicsSimpleTextItem(amr_id, marker)
                label.setFont(QFont("Sans", 7, QFont.Bold))
                label.setBrush(QBrush(QColor("#111111")))
                lr = label.boundingRect()
                label.setPos(-lr.width() / 2, -lr.height() / 2)

                trail = self.addLine(target_x, target_y, target_x, target_y,
                                     QPen(QColor(color), 2, Qt.DashLine))
                trail.setZValue(40)

                marker.setPos(target_x, target_y)
                self._amr_state[amr_id] = {
                    "marker": marker, "label": label, "trail": trail,
                    "current": QPointF(target_x, target_y),
                    "target": QPointF(target_x, target_y),
                    "color": color, "data": amr,
                }
            else:
                state["target"] = QPointF(target_x, target_y)
                state["color"] = color
                state["data"] = amr
                state["marker"].setBrush(QBrush(QColor(color)))
                tp = state["trail"].pen()
                tp.setColor(QColor(color))
                state["trail"].setPen(tp)

            st = self._amr_state[amr_id]
            battery = amr.get("battery")
            tooltip = f"{amr_id}\nstatus: {status}"
            if battery is not None:
                tooltip += f"\nbattery: {battery}%"
            st["marker"].setToolTip(tooltip)

        for amr_id in list(self._amr_state.keys()):
            if amr_id not in seen:
                st = self._amr_state.pop(amr_id)
                self.removeItem(st["marker"])
                self.removeItem(st["trail"])

    def _tick_animation(self) -> None:
        for state in self._amr_state.values():
            current: QPointF = state["current"]
            target: QPointF = state["target"]
            dx = target.x() - current.x()
            dy = target.y() - current.y()
            if dx * dx + dy * dy < 0.25:
                continue
            new_x = current.x() + dx * self.ANIMATION_STEP
            new_y = current.y() + dy * self.ANIMATION_STEP
            state["current"] = QPointF(new_x, new_y)
            state["marker"].setPos(new_x, new_y)
            state["trail"].setLine(new_x - dx, new_y - dy, new_x, new_y)


# ===================================================================
# Views (기존 로직 유지)
# ===================================================================
class FactoryMapView(QGraphicsView):
    """공장 맵 뷰 — 드래그/줌/리사이즈."""

    def __init__(self) -> None:
        super().__init__()
        self._scene = FactoryMapScene()
        self.setScene(self._scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QBrush(QColor(BG_COLOR)))
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def fit(self) -> None:
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.fit()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.fit()

    def wheelEvent(self, event) -> None:  # noqa: N802
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)

    def update_equipment(self, equipment: list[dict[str, Any]]) -> None:
        self._scene.update_equipment(equipment)


class MiniFactoryMapView(FactoryMapView):
    """대시보드용 축소 맵."""

    def __init__(self) -> None:
        super().__init__()
        self.setDragMode(QGraphicsView.NoDrag)
        self.setInteractive(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumHeight(300)
        self.setMaximumHeight(600)

    def wheelEvent(self, event) -> None:  # noqa: N802
        event.ignore()


__all__ = [
    "FactoryMapView",
    "MiniFactoryMapView",
    "FactoryMapScene",
    "STATUS_COLORS",
]
