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

        # 시뮬레이션 시작
        self._sim = _SimController(self)
        self._sim.start()

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
# Simulation — 주물 이동 시뮬레이션
# ===================================================================

# 주요 좌표 상수
_POS = {
    "mold": (927, 480),
    "cast_wait": (970, 320),
    "amr1_home": (562, 527),
    "amr2_home": (672, 527),
    "amr3_home": (782, 527),
    "cast_pickup": (870, 320),
    "unload_worker": (90, 170),
    "pp_worker": (160, 155),
    "conv_left": (230, 117),
    "conv_right": (490, 117),
    "conv_wait": (560, 117),
    "conv_pickup": (600, 245),
    "putaway": (310, 430),
    "rack": (95, 530),
    "rack_pickup": (200, 530),
    "outbound": (1165, 125),
    # 통로 웨이포인트 (zone 밖)
    "corridor_top": (450, 250),
    "corridor_right": (850, 250),
    "corridor_left": (90, 250),
    "corridor_mid": (600, 250),
    "corridor_bottom_left": (450, 430),
    "corridor_outbound_r": (1050, 250),
    "corridor_outbound_up": (1165, 250),
    "corridor_storage_bot": (450, 530),
    "corridor_charge_exit_1": (562, 440),
    "corridor_charge_exit_2": (672, 440),
    "corridor_charge_exit_3": (782, 440),
}

CASTING_COLOR = "#9333ea"  # 보라색
CASTING_RADIUS = 8
SIM_SPEED = 2.5  # px per tick
SIM_TICK_MS = 50  # 50ms = 20Hz


def _move_toward(cx: float, cy: float, tx: float, ty: float,
                 speed: float) -> tuple[float, float, bool]:
    """(cx,cy)에서 (tx,ty)를 향해 speed만큼 이동. 도착하면 arrived=True."""
    dx, dy = tx - cx, ty - cy
    dist = (dx * dx + dy * dy) ** 0.5
    if dist <= speed:
        return tx, ty, True
    ratio = speed / dist
    return cx + dx * ratio, cy + dy * ratio, False


class _CastingItem:
    """보라색 원형 주물 — 20Hz 깜빡임."""

    def __init__(self, scene: QGraphicsScene, x: float, y: float) -> None:
        r = CASTING_RADIUS
        self._ellipse = QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
        self._ellipse.setBrush(QBrush(QColor(CASTING_COLOR)))
        self._ellipse.setPen(QPen(QColor("#7c22ce"), 2))
        self._ellipse.setZValue(60)
        self._ellipse.setPos(x, y)
        scene.addItem(self._ellipse)
        self._visible = True
        self._scene = scene

    def move_to(self, x: float, y: float) -> None:
        self._ellipse.setPos(x, y)

    def pos(self) -> tuple[float, float]:
        p = self._ellipse.pos()
        return p.x(), p.y()

    def toggle_blink(self) -> None:
        self._visible = not self._visible
        self._ellipse.setOpacity(1.0 if self._visible else 0.3)

    def remove(self) -> None:
        self._scene.removeItem(self._ellipse)

    def show(self) -> None:
        self._ellipse.setVisible(True)

    def hide(self) -> None:
        self._ellipse.setVisible(False)


class _SimAMR:
    """시뮬레이션 전용 AMR 마커."""

    def __init__(self, scene: QGraphicsScene, label: str,
                 x: float, y: float) -> None:
        self._marker = QGraphicsRectItem(-20, -12, 40, 24)
        self._marker.setBrush(QBrush(QColor(AMR_COLOR)))
        self._marker.setPen(QPen(QColor("#b8a000"), 2))
        self._marker.setZValue(55)
        self._marker.setPos(x, y)
        scene.addItem(self._marker)

        txt = QGraphicsSimpleTextItem(label, self._marker)
        txt.setFont(QFont("Sans", 7, QFont.Bold))
        txt.setBrush(QBrush(QColor("#111111")))
        tr = txt.boundingRect()
        txt.setPos(-tr.width() / 2, -tr.height() / 2)

        self._scene = scene
        self._x, self._y = x, y
        self._waypoints: list[tuple[float, float]] = []
        self._cargo: _CastingItem | None = None

    def pos(self) -> tuple[float, float]:
        return self._x, self._y

    def set_waypoints(self, wps: list[tuple[float, float]]) -> None:
        self._waypoints = list(wps)

    def attach_cargo(self, item: _CastingItem) -> None:
        self._cargo = item

    def detach_cargo(self) -> _CastingItem | None:
        c = self._cargo
        self._cargo = None
        return c

    def tick(self, speed: float) -> bool:
        """한 프레임 이동. 모든 waypoint 도착 시 True 반환."""
        if not self._waypoints:
            return True
        tx, ty = self._waypoints[0]
        self._x, self._y, arrived = _move_toward(self._x, self._y, tx, ty, speed)
        self._marker.setPos(self._x, self._y)
        if self._cargo:
            self._cargo.move_to(self._x, self._y)
        if arrived:
            self._waypoints.pop(0)
        return not self._waypoints


class _SimController:
    """공정 시뮬레이션 컨트롤러 — step 기반 FSM."""

    def __init__(self, scene: FactoryMapScene) -> None:
        self._scene = scene
        self._step = 0
        self._tick_count = 0
        self._wait_ticks = 0
        self._blink_counter = 0

        # 시뮬레이션 전용 AMR 3대
        self._amr1 = _SimAMR(scene, "AMR-1", *_POS["amr1_home"])
        self._amr2 = _SimAMR(scene, "AMR-2", *_POS["amr2_home"])
        self._amr3 = _SimAMR(scene, "AMR-3", *_POS["amr3_home"])

        # 주물 목록
        self._castings: list[_CastingItem] = []
        self._current: _CastingItem | None = None
        self._rack_count = 0  # rack에 쌓인 주물 수
        self._outbound_items: list[_CastingItem] = []

        self._timer = QTimer()
        self._timer.setInterval(SIM_TICK_MS)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        self._step = 0
        self._timer.start()

    def _new_casting(self, x: float, y: float) -> _CastingItem:
        c = _CastingItem(self._scene, x, y)
        self._castings.append(c)
        return c

    def _tick(self) -> None:
        self._tick_count += 1

        # 20Hz 깜빡임 (50ms tick = 자동 20Hz)
        self._blink_counter += 1
        if self._blink_counter >= 1:
            self._blink_counter = 0
            for c in self._castings:
                c.toggle_blink()

        # 대기 중이면 카운트다운
        if self._wait_ticks > 0:
            self._wait_ticks -= 1
            return

        # step FSM
        if self._step == 0:
            self._step_0_create_casting()
        elif self._step == 1:
            self._step_1_casting_to_wait()
        elif self._step == 2:
            self._step_2_amr1_to_casting()
        elif self._step == 3:
            self._step_3_load_and_move_to_pp()
        elif self._step == 4:
            self._step_4_unload_at_pp()
        elif self._step == 5:
            self._step_5_move_to_conveyor()
        elif self._step == 6:
            self._step_6_conveyor_transport()
        elif self._step == 7:
            self._step_7_wait_at_conv_end()
        elif self._step == 8:
            self._step_8_to_conv_wait()
        elif self._step == 9:
            self._step_9_amr3_pickup()
        elif self._step == 10:
            self._step_10_amr3_to_putaway()
        elif self._step == 11:
            self._step_11_to_rack()
        elif self._step == 12:
            self._step_12_check_rack_full()
        elif self._step == 13:
            self._step_13_amr3_load_from_rack()
        elif self._step == 14:
            self._step_14_amr3_to_outbound()
        elif self._step == 15:
            self._step_15_unload_outbound()
        elif self._step == 16:
            self._step_16_amr3_return()
        elif self._step == 17:
            self._step_17_reset()

    # --- Step 0: Mold에서 주물 생성 ---
    def _step_0_create_casting(self) -> None:
        self._current = self._new_casting(*_POS["mold"])
        self._wait_ticks = int(2000 / SIM_TICK_MS)  # 2초 대기
        self._step = 1
        # AMR-001 출발 (동시에)
        self._amr1.set_waypoints([
            _POS["corridor_charge_exit_1"],
            (850, 440), (850, 320),
            _POS["cast_pickup"],
        ])
        # AMR-002 미리 Conveyor Waiting Zone 쪽으로 (나중에 필요)

    # --- Step 1: 주물 → Casting Waiting Zone ---
    def _step_1_casting_to_wait(self) -> None:
        if self._current is None:
            self._step = 2
            return
        cx, cy = self._current.pos()
        tx, ty = _POS["cast_wait"]
        nx, ny, arrived = _move_toward(cx, cy, tx, ty, SIM_SPEED)
        self._current.move_to(nx, ny)
        # AMR-001도 동시 이동
        self._amr1.tick(SIM_SPEED)
        if arrived:
            self._step = 2

    # --- Step 2: AMR-001이 Casting 도착 대기 ---
    def _step_2_amr1_to_casting(self) -> None:
        done = self._amr1.tick(SIM_SPEED)
        if done:
            # 주물을 AMR에 로드
            if self._current:
                self._current.move_to(*self._amr1.pos())
                self._amr1.attach_cargo(self._current)
            # AMR-001 경로: Casting → Unloading Worker (zone 밖 통로)
            self._amr1.set_waypoints([
                (850, 250),
                (700, 250),
                (200, 250),
                (90, 250),
                _POS["unload_worker"],
            ])
            self._step = 3

    # --- Step 3: AMR-001+주물 → Unloading Worker ---
    def _step_3_load_and_move_to_pp(self) -> None:
        done = self._amr1.tick(SIM_SPEED)
        if done:
            self._step = 4

    # --- Step 4: Unloading Worker에서 하차 → AMR-001 복귀 ---
    def _step_4_unload_at_pp(self) -> None:
        cargo = self._amr1.detach_cargo()
        if cargo:
            cargo.move_to(*_POS["unload_worker"])
        # AMR-001 Charging으로 복귀
        self._amr1.set_waypoints([
            (90, 250), (450, 250), (562, 440), _POS["amr1_home"],
        ])
        self._step = 5

    # --- Step 5: 주물 → Postprocessing Worker → 컨베이어 왼쪽 ---
    def _step_5_move_to_conveyor(self) -> None:
        self._amr1.tick(SIM_SPEED)  # AMR-001 복귀 (백그라운드)
        if self._current is None:
            self._step = 6
            return
        cx, cy = self._current.pos()
        tx, ty = _POS["conv_left"]
        # 먼저 pp_worker로 → 그 다음 conv_left로
        if cy > 130:
            # pp_worker로 이동
            nx, ny, arrived = _move_toward(cx, cy, 160, 130, SIM_SPEED)
            self._current.move_to(nx, ny)
        else:
            nx, ny, arrived = _move_toward(cx, cy, tx, ty, SIM_SPEED)
            self._current.move_to(nx, ny)
            if arrived:
                self._step = 6

    # --- Step 6: 컨베이어 위 좌→우 수평 이동 ---
    def _step_6_conveyor_transport(self) -> None:
        self._amr1.tick(SIM_SPEED)  # AMR-001 복귀 계속
        if self._current is None:
            self._step = 7
            return
        cx, cy = self._current.pos()
        tx, ty = _POS["conv_right"]
        nx, ny, arrived = _move_toward(cx, cy, tx, ty, SIM_SPEED * 0.6)
        self._current.move_to(nx, ny)
        if arrived:
            self._wait_ticks = int(3000 / SIM_TICK_MS)  # 3초 대기
            self._step = 7
            # AMR-002 출발 → Conveyor Waiting Zone
            self._amr2.set_waypoints([
                _POS["corridor_charge_exit_2"],
                (672, 250), _POS["conv_pickup"],
            ])

    # --- Step 7: 컨베이어 끝에서 3초 대기 ---
    def _step_7_wait_at_conv_end(self) -> None:
        self._amr2.tick(SIM_SPEED)  # AMR-002 이동
        # wait_ticks 가 0이면 자동으로 다음 step
        self._step = 8

    # --- Step 8: Conveyor Waiting Zone으로 이동 ---
    def _step_8_to_conv_wait(self) -> None:
        self._amr2.tick(SIM_SPEED)
        if self._current is None:
            self._step = 9
            return
        cx, cy = self._current.pos()
        tx, ty = _POS["conv_wait"]
        nx, ny, arrived = _move_toward(cx, cy, tx, ty, SIM_SPEED)
        self._current.move_to(nx, ny)
        if arrived:
            # 주물을 AMR-002 위치로 이동 (대기 중인 AMR 근처)
            self._current.move_to(*_POS["conv_pickup"])
            self._step = 9

    # --- Step 9: AMR-003 출발 → Conveyor Pickup ---
    def _step_9_amr3_pickup(self) -> None:
        # AMR-002 도착 확인
        amr2_done = self._amr2.tick(SIM_SPEED)
        if not amr2_done:
            return
        # AMR-003 출발
        self._amr3.set_waypoints([
            _POS["corridor_charge_exit_3"],
            (782, 250), _POS["conv_pickup"],
        ])
        self._step = 10
        # AMR-002 복귀
        self._amr2.set_waypoints([
            (672, 250), (672, 440), _POS["amr2_home"],
        ])

    # --- Step 10: AMR-003 → Putaway Waiting Zone ---
    def _step_10_amr3_to_putaway(self) -> None:
        self._amr2.tick(SIM_SPEED)  # AMR-002 복귀
        done = self._amr3.tick(SIM_SPEED)
        if done:
            # 주물 탑재
            if self._current:
                self._amr3.attach_cargo(self._current)
            self._amr3.set_waypoints([
                (600, 250), (450, 250), (450, 430), _POS["putaway"],
            ])
            self._step = 11

    # --- Step 11: 주물 → Good product storage rack ---
    def _step_11_to_rack(self) -> None:
        self._amr2.tick(SIM_SPEED)
        done = self._amr3.tick(SIM_SPEED)
        if done:
            # 하차
            cargo = self._amr3.detach_cargo()
            if cargo:
                cargo.move_to(*_POS["putaway"])
                self._current = cargo
            # AMR-003 대기 (rack 근처)
            self._amr3.set_waypoints([
                (310, 530), _POS["rack_pickup"],
            ])
            self._step = 12

    # --- Step 12: 주물이 rack으로 천천히 이동 + rack 카운트 ---
    def _step_12_check_rack_full(self) -> None:
        self._amr3.tick(SIM_SPEED * 0.5)
        if self._current is None:
            self._step = 13
            return
        cx, cy = self._current.pos()
        tx, ty = _POS["rack"]
        nx, ny, arrived = _move_toward(cx, cy, tx, ty, SIM_SPEED * 0.4)
        self._current.move_to(nx, ny)
        if arrived:
            self._rack_count += 1
            self._current.hide()
            self._current = None
            if self._rack_count < 2:
                # 2번째 주물을 위해 새 사이클 시작 (빠른 생성)
                c2 = self._new_casting(*_POS["rack"])
                c2.hide()
                self._rack_count = 2  # 즉시 2개로
            self._step = 13

    # --- Step 13: AMR-003이 rack에서 주물 2개 로드 ---
    def _step_13_amr3_load_from_rack(self) -> None:
        done = self._amr3.tick(SIM_SPEED)
        if done:
            # 주물 2개 생성 (시각적)
            c1 = self._new_casting(*self._amr3.pos())
            c2 = self._new_casting(self._amr3.pos()[0] + 5, self._amr3.pos()[1] + 5)
            self._amr3.attach_cargo(c1)
            self._outbound_items = [c1, c2]
            self._amr3.set_waypoints([
                _POS["rack_pickup"],
                _POS["corridor_storage_bot"],
                _POS["corridor_top"],
                _POS["corridor_right"],
                _POS["corridor_outbound_r"],
                _POS["corridor_outbound_up"],
                _POS["outbound"],
            ])
            self._step = 14

    # --- Step 14: AMR-003 → Outbound ---
    def _step_14_amr3_to_outbound(self) -> None:
        done = self._amr3.tick(SIM_SPEED)
        # c2도 따라감
        if len(self._outbound_items) > 1:
            ax, ay = self._amr3.pos()
            self._outbound_items[1].move_to(ax + 5, ay + 5)
        if done:
            self._step = 15

    # --- Step 15: Outbound에서 하차 ---
    def _step_15_unload_outbound(self) -> None:
        cargo = self._amr3.detach_cargo()
        # 주물 2개를 Outbound zone에 배치
        ox, oy = _POS["outbound"]
        for i, c in enumerate(self._outbound_items):
            c.move_to(ox - 15 + i * 20, oy)
        self._wait_ticks = int(1000 / SIM_TICK_MS)  # 1초
        # AMR-003 Charging으로 복귀
        self._amr3.set_waypoints([
            _POS["corridor_outbound_up"],
            _POS["corridor_outbound_r"],
            (782, 250), (782, 440), _POS["amr3_home"],
        ])
        self._step = 16

    # --- Step 16: AMR-003 복귀 ---
    def _step_16_amr3_return(self) -> None:
        done = self._amr3.tick(SIM_SPEED)
        if done:
            self._step = 17

    # --- Step 17: 리셋 → 반복 ---
    def _step_17_reset(self) -> None:
        # 기존 주물 모두 제거
        for c in self._castings:
            c.remove()
        self._castings.clear()
        self._outbound_items.clear()
        self._current = None
        self._rack_count = 0
        self._wait_ticks = int(2000 / SIM_TICK_MS)  # 2초 대기 후 반복
        self._step = 0


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
