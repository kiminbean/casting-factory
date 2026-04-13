"""생산 모니터링 페이지 - 제어/게이지 + 차트 + 테이블 (v0.3)."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.widgets.charts import HourlyProductionChart, TemperatureChart
from app.widgets.gauges import (
    ArcGauge,
    CircularProgress,
    ControlPanel,
)


class ProductionPage(QWidget):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        title = QLabel("생산 모니터링")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # 상단 Row 1: 제어 패널 + 게이지 3개 + 냉각 원형
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        self._control_panel = ControlPanel()
        self._control_panel.e_stop.pressed_stop.connect(self._on_emergency_stop)
        self._control_panel.mode_toggle.toggled_changed.connect(self._on_mode_changed)
        top_row.addWidget(self._control_panel, stretch=1)

        # 게이지 컨테이너
        gauge_container = QFrame()
        gauge_container.setObjectName("gaugeCard")
        gauge_container.setFrameShape(QFrame.StyledPanel)
        gauge_layout = QVBoxLayout(gauge_container)
        gauge_layout.setContentsMargins(12, 8, 12, 8)
        gauge_layout.setSpacing(4)

        gauge_title = QLabel("실시간 공정 파라미터")
        gauge_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #111827; padding: 0 6px;"
        )
        gauge_layout.addWidget(gauge_title)

        gauge_row = QHBoxLayout()
        gauge_row.setSpacing(4)

        self._gauge_pressure = ArcGauge(
            title="성형 압력", unit="bar", minimum=0, maximum=150,
            warn_ratio=0.7, danger_ratio=0.9,
        )
        gauge_row.addWidget(self._gauge_pressure)

        self._gauge_angle = ArcGauge(
            title="주탕 각도", unit="deg", minimum=0, maximum=90,
            warn_ratio=0.75, danger_ratio=0.95,
        )
        gauge_row.addWidget(self._gauge_angle)

        self._gauge_power = ArcGauge(
            title="가열 출력", unit="%", minimum=0, maximum=100,
            warn_ratio=0.85, danger_ratio=0.95,
        )
        gauge_row.addWidget(self._gauge_power)

        gauge_layout.addLayout(gauge_row)
        top_row.addWidget(gauge_container, stretch=3)

        # 냉각 원형 프로그레스
        cooling_card = QFrame()
        cooling_card.setObjectName("gaugeCard")
        cooling_card.setFrameShape(QFrame.StyledPanel)
        cooling_layout = QVBoxLayout(cooling_card)
        cooling_layout.setContentsMargins(12, 12, 12, 12)

        self._cooling = CircularProgress(
            title="냉각 진행", subtitle="-", unit="%"
        )
        cooling_layout.addWidget(self._cooling)
        top_row.addWidget(cooling_card, stretch=1)

        layout.addLayout(top_row)

        # 중단 Row 2: 차트 2개 (가로 분할)
        chart_row = QHBoxLayout()
        chart_row.setSpacing(14)

        self._temp_chart = TemperatureChart()
        self._temp_chart.setMinimumHeight(220)
        chart_row.addWidget(self._temp_chart, stretch=1)

        self._hourly_chart = HourlyProductionChart()
        self._hourly_chart.setMinimumHeight(220)
        chart_row.addWidget(self._hourly_chart, stretch=1)

        layout.addLayout(chart_row, stretch=1)

        # 하단: 공정 단계 테이블
        stages_label = QLabel("공정 단계")
        stages_label.setObjectName("sectionTitle")
        layout.addWidget(stages_label)

        self._stages_table = QTableWidget(0, 5)
        self._stages_table.setHorizontalHeaderLabels(
            ["단계", "상태", "진행률", "시작 시각", "담당 설비"]
        )
        self._stages_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self._stages_table.verticalHeader().setVisible(False)
        self._stages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._stages_table.setAlternatingRowColors(True)
        self._stages_table.setMaximumHeight(220)
        layout.addWidget(self._stages_table)

        # 공정 파라미터 이력 테이블 (v0.8)
        param_label = QLabel("공정 파라미터 이력")
        param_label.setObjectName("sectionTitle")
        layout.addWidget(param_label)

        self._param_table = QTableWidget(0, 8)
        self._param_table.setHorizontalHeaderLabels(
            ["시각", "공정", "온도(°C)", "압력(bar)", "각도(°)", "출력(%)", "냉각률(%)", "진행률(%)"]
        )
        self._param_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._param_table.verticalHeader().setVisible(False)
        self._param_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._param_table.setAlternatingRowColors(True)
        layout.addWidget(self._param_table)

    def refresh(self) -> None:
        # 실시간 파라미터
        params = self._api.get_live_parameters()
        self._gauge_pressure.set_value(params.get("mold_pressure", 0))
        self._gauge_angle.set_value(params.get("pour_angle", 0))
        self._gauge_power.set_value(params.get("furnace_heating_power", 0))

        cooling_progress = params.get("cooling_progress", 0)
        current_t = params.get("cooling_current_temp", 0)
        target_t = params.get("cooling_target_temp", 25)
        remaining = params.get("cooling_remaining_min", 0)
        self._cooling.set_value(cooling_progress)
        self._cooling.set_subtitle(
            f"{current_t:.0f}°C → {target_t:.0f}°C · {remaining}분 남음"
        )

        # 차트
        self._temp_chart.update_data(self._api.get_temperature_history())
        self._hourly_chart.update_data(self._api.get_hourly_production())

        # 공정 파라미터 이력
        params_list = self._api.get_process_parameter_history() or []
        self._param_table.setRowCount(len(params_list))
        for row, p in enumerate(params_list):
            cells = [
                p.get("time", ""),
                p.get("stage", ""),
                p.get("temperature", "-"),
                p.get("pressure", "-"),
                p.get("angle", "-"),
                p.get("power", "-"),
                p.get("cooling", "-"),
                p.get("progress", "-"),
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(str(val))
                if col >= 2:
                    item.setTextAlignment(Qt.AlignCenter)
                self._param_table.setItem(row, col, item)

        # 공정 단계
        stages = self._api.get_process_stages() or []
        self._stages_table.setRowCount(len(stages))
        for row, stage in enumerate(stages):
            self._stages_table.setItem(row, 0, QTableWidgetItem(str(stage.get("name", ""))))
            status_item = QTableWidgetItem(str(stage.get("status", "")))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._stages_table.setItem(row, 1, status_item)
            self._stages_table.setItem(
                row, 2, QTableWidgetItem(f"{stage.get('progress', 0)}%")
            )
            self._stages_table.setItem(
                row, 3, QTableWidgetItem(str(stage.get("started_at", "")))
            )
            self._stages_table.setItem(
                row, 4, QTableWidgetItem(str(stage.get("equipment", "")))
            )

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        msg_type = payload.get("type", "")
        if msg_type in (
            "production_update",
            "equipment_update",
            "process_stage_update",
            "parameter_update",
        ):
            self.refresh()

    # ---- 제어 이벤트 ----
    def _on_emergency_stop(self) -> None:
        QMessageBox.warning(
            self,
            "비상 정지 (E-STOP)",
            "비상정지 버튼이 활성화되었습니다.\n\n"
            "모든 공정이 중단됩니다.\n"
            "서버에 정지 신호 전송 후 오퍼레이터 확인이 필요합니다.",
            QMessageBox.Ok,
        )
        # TODO: POST /api/production/emergency_stop

    def _on_mode_changed(self, auto: bool) -> None:
        mode = "AUTO" if auto else "MANUAL"
        # TODO: POST /api/production/mode { "mode": mode }
        # 현재는 UI 상태만 유지
        _ = mode
