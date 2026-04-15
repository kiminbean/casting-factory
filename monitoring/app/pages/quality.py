"""품질 검사 모니터링 페이지 v0.5.

구성:
  1. KPI 4개 (조건부 색상 적용)
  2. 카메라 라이브 뷰 + 분류 다이얼 (가로 분할)
  3. TOP3 불량 배지 + 검사 기준 참조 패널
  4. 차트 3개 (불량률 추이 / 불량 분포 / 생산량 vs 불량)
  5. 검사 이력 테이블
"""
from __future__ import annotations

import logging
import os
from typing import Any

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.pages.dashboard import KpiCard
from app.widgets.camera_view import CameraLiveView
from app.widgets.charts import (
    DefectRateChart,
    DefectTypeDistChart,
    ProductionVsDefectsChart,
)
from app.widgets.defect_panels import InspectionStandardsPanel, TopDefectsPanel
from app.widgets.sorter_dial import SorterCard


logger = logging.getLogger(__name__)

# Stage A — Jetson 실시간 프레임 polling
_LIVE_CAMERA_ID = os.environ.get("MGMT_IP_CAMERA_ID", "CAM-INSP-01")
_FRAME_POLL_MS = int(os.environ.get("MGMT_LIVE_FRAME_POLL_MS", "1000"))


class QualityPage(QWidget):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._mgmt = None  # Stage A — lazy init ManagementClient
        self._kpis: dict[str, KpiCard] = {}
        self._last_frame_seq: int = -1
        self._build_ui()
        self.refresh()
        # Stage A — 실시간 프레임 1Hz 타이머
        self._frame_timer = QTimer(self)
        self._frame_timer.setInterval(_FRAME_POLL_MS)
        self._frame_timer.timeout.connect(self._poll_live_frame)
        self._frame_timer.start()

    def _ensure_mgmt_client(self):
        if self._mgmt is not None:
            return self._mgmt
        try:
            from app.management_client import ManagementClient
            self._mgmt = ManagementClient()
        except Exception:  # noqa: BLE001
            logger.exception("ManagementClient 생성 실패")
            return None
        return self._mgmt

    def _poll_live_frame(self) -> None:
        """1Hz — Management Server 에서 최신 프레임 가져와 카메라 뷰에 반영."""
        mgmt = self._ensure_mgmt_client()
        if mgmt is None:
            return
        try:
            frame = mgmt.get_latest_frame(_LIVE_CAMERA_ID)
        except Exception:  # noqa: BLE001
            logger.exception("get_latest_frame 실패")
            return
        if not frame:
            return  # 프레임 없으면 기존 시뮬레이션/프레임 유지
        seq = int(frame.get("sequence", 0))
        if seq == self._last_frame_seq:
            return  # 동일 seq 중복 업데이트 스킵
        self._last_frame_seq = seq
        self._camera.set_frame_bytes(
            data=frame.get("data", b""),
            encoding=frame.get("encoding", "jpeg"),
            sequence=seq,
            received_at=frame.get("received_at", ""),
        )

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("품질 검사")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ===== KPI 4 카드 =====
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(14)
        metrics = [
            ("total", "검사 수", "건"),
            ("ok", "합격", "건"),
            ("ng", "불합격", "건"),
            ("rate", "불량률", "%"),
        ]
        for col, (key, label, unit) in enumerate(metrics):
            card = KpiCard(label, unit=unit)
            self._kpis[key] = card
            kpi_grid.addWidget(card, 0, col)
        layout.addLayout(kpi_grid)

        # ===== 카메라 뷰 + 분류 다이얼 + TOP3 + 기준 =====
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        self._camera = CameraLiveView()
        top_row.addWidget(self._camera, stretch=3)

        self._sorter_card = SorterCard()
        top_row.addWidget(self._sorter_card, stretch=2)

        self._top_defects = TopDefectsPanel()
        top_row.addWidget(self._top_defects, stretch=2)

        self._standards = InspectionStandardsPanel()
        top_row.addWidget(self._standards, stretch=3)

        layout.addLayout(top_row, stretch=1)

        # ===== 차트 3개 =====
        chart_row = QHBoxLayout()
        chart_row.setSpacing(14)

        self._rate_chart = DefectRateChart()
        self._rate_chart.setMinimumHeight(220)
        chart_row.addWidget(self._rate_chart, stretch=2)

        self._pie_chart = DefectTypeDistChart()
        self._pie_chart.setMinimumHeight(220)
        chart_row.addWidget(self._pie_chart, stretch=1)

        self._vs_chart = ProductionVsDefectsChart()
        self._vs_chart.setMinimumHeight(220)
        chart_row.addWidget(self._vs_chart, stretch=2)

        layout.addLayout(chart_row, stretch=1)

        # ===== 검사 이력 테이블 =====
        section = QLabel("최근 검사 이력")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels(
            ["이미지", "검사 시각", "제품", "결과", "불량 유형", "담당자", "비고"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setMaximumHeight(220)
        layout.addWidget(self._table)

    def refresh(self) -> None:
        # KPI + 조건부 색상
        stats = self._api.get_defect_stats()
        if stats:
            total = stats.get("total", 0)
            ok = stats.get("ok", 0)
            ng = stats.get("ng", 0)
            rate = float(stats.get("defect_rate", 0))
            self._kpis["total"].update_value(total)
            self._kpis["ok"].update_value(ok)
            self._kpis["ng"].update_value(ng)
            self._kpis["rate"].update_value(f"{rate:.1f}")
            self._colorize_rate(rate)

        # 카메라 피드
        vision = self._api.get_vision_feed()
        if vision:
            self._camera.set_result(
                result=str(vision.get("result", "idle")),
                product_id=str(vision.get("product_id", "-")),
                confidence=float(vision.get("confidence", 0)),
                inspected_at=str(vision.get("inspected_at", "-")),
                defect_type=str(vision.get("defect_type", "")),
            )

        # 분류 다이얼
        sorter = self._api.get_sorter_state()
        if sorter:
            self._sorter_card.set_state(
                angle=sorter.get("angle"),
                direction=sorter.get("direction"),
                success=sorter.get("success"),
                count_good=sorter.get("count_good"),
                count_bad=sorter.get("count_bad"),
            )

        # TOP3 + 기준 + 차트
        defects = self._api.get_defect_type_dist()
        self._top_defects.update_data(defects)
        self._standards.update_data(self._api.get_inspection_standards())

        self._rate_chart.update_data(self._api.get_defect_rate_trend())
        self._pie_chart.update_data(defects)
        self._vs_chart.update_data(self._api.get_production_vs_defects())

        # 검사 이력 (이미지 플레이스홀더 컬럼 포함)
        inspections = self._api.get_quality_inspections() or []
        self._table.setRowCount(len(inspections))
        for row, item in enumerate(inspections[:200]):
            # 이미지 플레이스홀더 (결과에 따라 이모지 아이콘)
            result = str(item.get("result", ""))
            icon = "📷" if result == "OK" else ("⚠" if result == "NG" else "·")
            image_item = QTableWidgetItem(icon)
            image_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 0, image_item)

            self._table.setItem(row, 1, QTableWidgetItem(str(item.get("inspected_at", ""))))
            self._table.setItem(row, 2, QTableWidgetItem(str(item.get("product", ""))))

            result_item = QTableWidgetItem(result)
            result_item.setTextAlignment(Qt.AlignCenter)
            if result == "NG":
                result_item.setForeground(QColor("#dc2626"))
            elif result == "OK":
                result_item.setForeground(QColor("#059669"))
            self._table.setItem(row, 3, result_item)
            self._table.setItem(row, 4, QTableWidgetItem(str(item.get("defect_type", ""))))
            self._table.setItem(row, 5, QTableWidgetItem(str(item.get("inspector", ""))))
            self._table.setItem(row, 6, QTableWidgetItem(str(item.get("note", ""))))

    def _colorize_rate(self, rate: float) -> None:
        """불량률에 따른 KPI 카드 색상 (기준: 2% 미만 녹색, 5% 미만 주황, 초과 빨강)."""
        card = self._kpis["rate"]
        if rate < 2.0:
            color = "#10b981"
        elif rate < 5.0:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        card.setStyleSheet(
            f"#kpiCard {{ border: 2px solid {color}; }}"
            f"#kpiValue {{ color: {color}; }}"
        )

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        msg_type = payload.get("type", "")
        if msg_type in (
            "quality_update",
            "inspection_completed",
            "vision_result",
            "sorter_update",
        ):
            self.refresh()
