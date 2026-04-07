"""2D 공장 맵 위젯 (Next.js FactoryMap.tsx 레이아웃 재현).

3x3 그리드의 9개 구역을 어두운 배경 위에 표시한다.
참고: src/components/FactoryMap.tsx
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PyQt5.QtCore import QPointF, QRectF, QTimer, Qt
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
)
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


# 그리드 차원 (FactoryMap.tsx 와 동일)
CELL_W = 220
CELL_H = 140
GAP = 18
PADDING = 32
GRID_COLS = 3
GRID_ROWS = 3

FLOOR_W = GRID_COLS * CELL_W + (GRID_COLS - 1) * GAP + PADDING * 2
FLOOR_H = GRID_ROWS * CELL_H + (GRID_ROWS - 1) * GAP + PADDING * 2


# 상태별 색상 (FactoryMap.tsx zoneColor)
STATUS_COLORS: dict[str, dict[str, str]] = {
    "active": {
        "top": "#4b5563",
        "shadow": "#374151",
        "border": "#22c55e",
        "dot": "#4ade80",
        "label": "가동",
    },
    "idle": {
        "top": "#3d4452",
        "shadow": "#2d3340",
        "border": "#6b7280",
        "dot": "#9ca3af",
        "label": "대기",
    },
    "warning": {
        "top": "#4b4020",
        "shadow": "#3a3010",
        "border": "#f59e0b",
        "dot": "#fbbf24",
        "label": "경고",
    },
    "error": {
        "top": "#4b2020",
        "shadow": "#3a1010",
        "border": "#ef4444",
        "dot": "#f87171",
        "label": "오류",
    },
    "charging": {
        "top": "#203040",
        "shadow": "#102030",
        "border": "#60a5fa",
        "dot": "#60a5fa",
        "label": "충전",
    },
}


def _status_key(raw: str) -> str:
    s = (raw or "").lower()
    mapping = {
        "running": "active",
        "active": "active",
        "completed": "active",
        "idle": "idle",
        "waiting": "idle",
        "warning": "warning",
        "maintenance": "warning",
        "error": "error",
        "alarm": "error",
        "charging": "charging",
    }
    return mapping.get(s, "idle")


@dataclass(frozen=True)
class ZoneDef:
    zone_id: str
    name: str
    col: int
    row: int
    default_status: str
    equipment_label: str = ""
    detail: str = ""


# FactoryMap.tsx 의 ZONES 와 동일
ZONES: list[ZoneDef] = [
    ZoneDef("raw-material", "원자재 보관", 1, 1, "active", "", "주석 합금 234kg 보유"),
    ZoneDef("melting", "용해 구역", 2, 1, "active", "FRN-001", "용해로 720°C 유지"),
    ZoneDef("mold", "주형 구역", 3, 1, "idle", "MLD-001", "다음 배치 대기"),
    ZoneDef("casting", "주조 구역", 1, 2, "active", "ARM-001", "COBOT 작업 중 120개/h"),
    ZoneDef("cooling", "냉각 구역", 2, 2, "active", "CVR-001", "냉각 컨베이어 45°C"),
    ZoneDef("demolding", "탈형 구역", 3, 2, "warning", "ARM-002", "탈형 불량 감지"),
    ZoneDef("post-process", "후처리 구역", 1, 3, "active", "ARM-003", "버르 제거 85개/h"),
    ZoneDef("inspection", "검사 구역", 2, 3, "active", "CAM-001", "비전 검사 불량률 1.2%"),
    ZoneDef("loading", "적재 / 출고", 3, 3, "idle", "SRT-001", "팔레트 3개 대기"),
]


def _cell_pos(col: int, row: int) -> tuple[float, float]:
    """1-based col/row -> 좌상단 픽셀 좌표."""
    x = PADDING + (col - 1) * (CELL_W + GAP)
    y = PADDING + (row - 1) * (CELL_H + GAP)
    return x, y


class ZoneBlockItem(QGraphicsItem):
    """3D 스타일 플랫폼 블록 - paint() 로 직접 렌더."""

    SHADOW_OFFSET = 8

    def __init__(self, zone: ZoneDef) -> None:
        super().__init__()
        self._zone = zone
        self._status = zone.default_status
        self._title_font = QFont("Helvetica Neue", 12, QFont.Bold)
        self._sub_font = QFont("Helvetica Neue", 9)
        self._meta_font = QFont("Helvetica Neue", 8)
        self.setToolTip(f"{zone.name}\n{zone.detail}")

    def set_status(self, status: str, detail: str | None = None) -> None:
        self._status = _status_key(status)
        if detail:
            self.setToolTip(f"{self._zone.name}\n{detail}")
        self.update()

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(0, 0, CELL_W, CELL_H + self.SHADOW_OFFSET)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ARG002
        c = STATUS_COLORS.get(self._status, STATUS_COLORS["idle"])

        # 그림자 (하단 4px 오프셋)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(c["shadow"])))
        painter.drawRoundedRect(0, self.SHADOW_OFFSET, CELL_W, CELL_H, 6, 6)

        # 상단 플레이트
        painter.setBrush(QBrush(QColor(c["top"])))
        painter.setPen(QPen(QColor(c["border"]), 2))
        painter.drawRoundedRect(0, 0, CELL_W, CELL_H, 6, 6)

        # 상단 라벨 영역
        # 상태 dot + 제목
        dot_x, dot_y = 14, 16
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(c["dot"])))
        painter.drawEllipse(dot_x, dot_y, 8, 8)

        # 제목 텍스트
        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(self._title_font)
        painter.drawText(dot_x + 14, dot_y + 8, self._zone.name)

        # 상태 라벨 (우측 상단)
        painter.setFont(self._meta_font)
        painter.setPen(QPen(QColor(c["dot"])))
        status_label = c["label"]
        text_w = painter.fontMetrics().horizontalAdvance(status_label)
        painter.drawText(CELL_W - text_w - 14, dot_y + 8, status_label)

        # 상세 내용
        if self._zone.equipment_label:
            painter.setPen(QPen(QColor("#d1d5db")))
            painter.setFont(self._sub_font)
            painter.drawText(14, 50, f"설비: {self._zone.equipment_label}")

        if self._zone.detail:
            painter.setPen(QPen(QColor("#9ca3af")))
            painter.setFont(self._meta_font)
            painter.drawText(14, 70, self._zone.detail)


class FactoryMapScene(QGraphicsScene):
    """FactoryMap.tsx 3x3 레이아웃을 재현하는 씬.

    v0.6: AMR 마커 이동 애니메이션 + 경로 선 표시.
    """

    ANIMATION_INTERVAL_MS = 30
    ANIMATION_STEP = 0.12  # 프레임당 보간 비율 (0~1)

    def __init__(self) -> None:
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("#111827")))
        self.setSceneRect(0, 0, FLOOR_W, FLOOR_H)

        self._zone_items: dict[str, ZoneBlockItem] = {}
        # amr_id -> dict(marker, label, trail, current QPointF, target QPointF, status)
        self._amr_state: dict[str, dict[str, Any]] = {}

        self._draw_floor()
        self._draw_zones()

        # 애니메이션 타이머
        self._anim_timer = QTimer()
        self._anim_timer.setInterval(self.ANIMATION_INTERVAL_MS)
        self._anim_timer.timeout.connect(self._tick_animation)
        self._anim_timer.start()

    def _draw_floor(self) -> None:
        # 바닥 패널 (grid 점 패턴)
        floor_rect = QGraphicsRectItem(0, 0, FLOOR_W, FLOOR_H)
        floor_rect.setBrush(QBrush(QColor("#0b1120")))
        floor_rect.setPen(QPen(QColor("#1f2937"), 2))
        floor_rect.setZValue(-100)
        self.addItem(floor_rect)

        # 점 그리드
        dot_pen = QPen(QColor("#1f2937"), 2)
        for x in range(PADDING, FLOOR_W - PADDING, 40):
            for y in range(PADDING, FLOOR_H - PADDING, 40):
                dot = self.addEllipse(x - 1, y - 1, 2, 2, dot_pen, QBrush(QColor("#1f2937")))
                dot.setZValue(-90)

    def _draw_zones(self) -> None:
        for zone in ZONES:
            item = ZoneBlockItem(zone)
            x, y = _cell_pos(zone.col, zone.row)
            item.setPos(x, y)
            self.addItem(item)
            self._zone_items[zone.zone_id] = item

        self._draw_process_flow()

    def _draw_process_flow(self) -> None:
        """공정 흐름 화살표: raw → melting → mold → casting → cooling → demolding → post → inspection → loading."""
        flow_order = [
            "raw-material", "melting", "mold",
            "casting", "cooling", "demolding",
            "post-process", "inspection", "loading",
        ]

        pen = QPen(QColor("#4ade80"), 2)
        pen.setStyle(Qt.DashLine)

        # 각 zone 의 중심 좌표 계산
        centers: dict[str, tuple[float, float]] = {}
        for zone in ZONES:
            x, y = _cell_pos(zone.col, zone.row)
            centers[zone.zone_id] = (x + CELL_W / 2, y + CELL_H / 2)

        # 인접한 공정 사이 화살표 (거리가 너무 멀면 skip)
        for i in range(len(flow_order) - 1):
            src_id = flow_order[i]
            dst_id = flow_order[i + 1]
            src = centers.get(src_id)
            dst = centers.get(dst_id)
            if not src or not dst:
                continue
            # 3x3 행 전환 시 점프가 크므로 인접 셀만 화살표 그리기
            line = self.addLine(src[0], src[1], dst[0], dst[1], pen)
            line.setZValue(-5)

    # ---- 실시간 갱신 ----
    def update_equipment(self, equipment: list[dict[str, Any]]) -> None:
        """설비 API 응답을 받아 zone 상태와 AMR 마커 갱신."""
        # 설비 ID -> zone 매핑
        eq_to_zone: dict[str, str] = {}
        for zone in ZONES:
            if zone.equipment_label:
                eq_to_zone[zone.equipment_label] = zone.zone_id

        amrs: list[dict[str, Any]] = []

        for eq in equipment:
            eq_id = str(eq.get("id", ""))
            eq_type = str(eq.get("type", ""))
            status = str(eq.get("status", ""))

            if eq_type == "amr":
                amrs.append(eq)
                continue

            zone_id = eq_to_zone.get(eq_id)
            if not zone_id:
                continue
            item = self._zone_items.get(zone_id)
            if item:
                detail = f"{eq.get('name', eq_id)} · {status}"
                item.set_status(status, detail=detail)

        self._update_amr_markers(amrs)

    def _update_amr_markers(self, amrs: list[dict[str, Any]]) -> None:
        """AMR 마커 갱신 - 새 target 위치 계산, 애니메이션은 _tick_animation 이 처리."""
        seen: set[str] = set()
        aisle_y_top = 260   # 이송 구역 시작 y
        aisle_y_bot = FLOOR_H - 50  # 출고장 위쪽
        aisle_x_min = PADDING + 20
        aisle_x_max = FLOOR_W - PADDING - 60

        for idx, amr in enumerate(amrs):
            amr_id = str(amr.get("id", ""))
            if not amr_id:
                continue
            seen.add(amr_id)

            status = str(amr.get("status", ""))
            status_key = _status_key(status)
            color = STATUS_COLORS.get(status_key, STATUS_COLORS["idle"])["dot"]

            # 좌표 매핑: equipment pos_x/y (meter) 를 scene 좌표로 변환
            pos_x_m = amr.get("pos_x")
            pos_y_m = amr.get("pos_y")
            if pos_x_m is not None and pos_y_m is not None:
                # 공장 크기 가정: 32m x 12m → FLOOR_W x FLOOR_H 영역으로 매핑
                target_x = PADDING + (float(pos_x_m) / 32.0) * (FLOOR_W - PADDING * 2)
                target_y = PADDING + (float(pos_y_m) / 12.0) * (FLOOR_H - PADDING * 2)
                # 이송 구역 내로 clamp
                target_x = max(aisle_x_min, min(aisle_x_max, target_x))
                target_y = max(aisle_y_top, min(aisle_y_bot, target_y))
            elif status_key == "charging":
                target_x = aisle_x_min + 20
                target_y = aisle_y_bot + 4
            elif status_key == "idle":
                target_x = aisle_x_max - 80
                target_y = aisle_y_top + 20 + idx * 20
            else:
                span = aisle_x_max - aisle_x_min - 40
                target_x = aisle_x_min + 40 + (idx * 180) % span
                target_y = aisle_y_top + 40

            state = self._amr_state.get(amr_id)
            if state is None:
                # 신규 AMR - 초기 위치에서 바로 시작
                marker = QGraphicsRectItem(-18, -10, 36, 20)
                marker.setPen(QPen(QColor("#e5e7eb"), 1.5))
                marker.setZValue(50)
                self.addItem(marker)

                label = QGraphicsSimpleTextItem(amr_id, marker)
                label.setFont(QFont("Helvetica Neue", 7, QFont.Bold))
                label.setBrush(QBrush(QColor("#111827")))
                rect = label.boundingRect()
                label.setPos(-rect.width() / 2, -rect.height() / 2)

                # 경로 선 (trail)
                trail_pen = QPen(QColor(color), 2, Qt.DashLine)
                trail = self.addLine(target_x, target_y, target_x, target_y, trail_pen)
                trail.setZValue(40)

                marker.setPos(target_x, target_y)
                self._amr_state[amr_id] = {
                    "marker": marker,
                    "label": label,
                    "trail": trail,
                    "current": QPointF(target_x, target_y),
                    "target": QPointF(target_x, target_y),
                    "status": status,
                    "status_key": status_key,
                    "color": color,
                    "data": amr,
                }
            else:
                # 기존 AMR - target만 갱신 (애니메이션으로 이동)
                state["target"] = QPointF(target_x, target_y)
                state["status"] = status
                state["status_key"] = status_key
                state["color"] = color
                state["data"] = amr

                # 마커 색상 갱신
                marker = state["marker"]
                marker.setBrush(QBrush(QColor(color)))

                # 경로 선 색상 갱신
                trail = state["trail"]
                trail_pen = trail.pen()
                trail_pen.setColor(QColor(color))
                trail.setPen(trail_pen)

            # 툴팁 / 색상
            state = self._amr_state[amr_id]
            state["marker"].setBrush(QBrush(QColor(color)))
            battery = amr.get("battery")
            tooltip = f"{amr_id}\nstatus: {status}"
            if battery is not None:
                tooltip += f"\nbattery: {battery}%"
            state["marker"].setToolTip(tooltip)

        # 사라진 AMR 제거
        for amr_id in list(self._amr_state.keys()):
            if amr_id not in seen:
                st = self._amr_state.pop(amr_id)
                self.removeItem(st["marker"])
                self.removeItem(st["trail"])

    def _tick_animation(self) -> None:
        """마커를 target 방향으로 부드럽게 이동."""
        if not self._amr_state:
            return

        for state in self._amr_state.values():
            current: QPointF = state["current"]
            target: QPointF = state["target"]
            dx = target.x() - current.x()
            dy = target.y() - current.y()
            dist_sq = dx * dx + dy * dy
            if dist_sq < 0.25:
                # 도착
                continue

            # 보간: step 비율로 이동
            new_x = current.x() + dx * self.ANIMATION_STEP
            new_y = current.y() + dy * self.ANIMATION_STEP
            state["current"] = QPointF(new_x, new_y)
            state["marker"].setPos(new_x, new_y)

            # trail: 출발(이전)선→현재
            trail = state["trail"]
            trail.setLine(new_x - dx, new_y - dy, new_x, new_y)


class FactoryMapView(QGraphicsView):
    """공장 맵 뷰 - 드래그/줌/리사이즈 대응."""

    def __init__(self) -> None:
        super().__init__()
        self._scene = FactoryMapScene()
        self.setScene(self._scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QBrush(QColor("#111827")))
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
    """대시보드용 축소 공장 맵 - 드래그/줌 비활성화, fit-to-view 고정."""

    def __init__(self) -> None:
        super().__init__()
        self.setDragMode(QGraphicsView.NoDrag)
        self.setInteractive(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumHeight(220)
        self.setMaximumHeight(260)

    def wheelEvent(self, event) -> None:  # noqa: N802
        # 미니맵은 휠 이벤트 무시
        event.ignore()


__all__ = [
    "FactoryMapView",
    "MiniFactoryMapView",
    "FactoryMapScene",
    "ZoneBlockItem",
    "STATUS_COLORS",
]
