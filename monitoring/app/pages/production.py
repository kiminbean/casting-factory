"""생산 모니터링 페이지 - 제어/게이지 + 차트 + 테이블 (v0.3)."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
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


# 주문/아이템 진행 테이블 컬럼 순서와 일치해야 함
ITEM_STAGE_COLUMNS: list[str] = ["대기", "주탕", "탈형", "후처리", "검사", "적재"]

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
        # item_id → 현재 stage 코드 in-memory 캐시 (gRPC 스트림으로 갱신).
        # _refresh_item_progress 가 폴링으로 채울 때도 동일 캐시 사용.
        self._item_stage_cache: dict[int, str] = {}
        # PyQt 라벨(대기/주탕/탈형/...) → V6 stage 코드 매핑
        # CONFLUENCE 결정: 대기=QUE, 주탕=MM, 탈형=DM, 후처리=PP, 검사=IP, 적재=TR_LD/SH
        self._label_to_codes: dict[str, set[str]] = {
            "대기": {"QUE"},
            "주탕": {"MM"},
            "탈형": {"DM"},
            "후처리": {"PP", "TR_PP"},  # 이송 중도 후처리 단계로 표시
            "검사": {"IP"},
            "적재": {"TR_LD", "SH"},
        }
        self._build_ui()
        self.refresh()
        self._start_item_stream()

    # ---------- gRPC stream 통합 (V6 Phase 3) ----------
    def _start_item_stream(self) -> None:
        """Management Service WatchItems 구독 시작 (별도 QThread)."""
        try:
            from app.workers.item_stream_worker import ItemStreamWorker, ItemStreamThread
        except ImportError:
            # gRPC 의존 미설치 환경이면 조용히 폴링만 사용
            return
        self._stream_worker = ItemStreamWorker(order_filter=None)
        self._stream_worker.item_event.connect(self._on_item_event)
        self._stream_thread = ItemStreamThread(self._stream_worker)
        self._stream_thread.start()

    def _on_item_event(self, item_id: int, stage_code: str, robot_id: str, at_iso: str) -> None:
        """gRPC 스트림 콜백 (메인 스레드 실행). 캐시 + 행 1개만 즉시 갱신.

        @MX:NOTE: ItemStreamWorker.pyqtSignal 의 슬롯. 메인 스레드에서 호출되므로 GUI 직접 조작 안전.
                    행 단위 부분 갱신만 수행 — 전체 refresh 비용 회피.
        """
        prev = self._item_stage_cache.get(item_id)
        self._item_stage_cache[item_id] = stage_code
        if prev != stage_code:
            # stage 변경 → 해당 item 행만 다시 그림
            self._update_item_row(item_id, stage_code)

    def _update_item_row(self, item_id: int, stage_code: str) -> None:
        """item_progress_table 에서 해당 item_id 행을 찾아 마커 위치 이동."""
        if not hasattr(self, "_item_progress_table"):
            return
        # Item 컬럼(index 2) 에 "I-{id}" 형태로 표시되도록 _refresh_item_progress 에서 보장
        target = f"I-{item_id}"
        for row in range(self._item_progress_table.rowCount()):
            cell = self._item_progress_table.item(row, 2)
            if cell and cell.text() == target:
                self._render_item_row_stage(row, stage_code)
                return

    # ---------- gRPC ListItems → 폴링 데이터 소스 ----------
    def _fetch_items_via_grpc(self) -> list[dict[str, Any]] | None:
        """gRPC list_items 로 모든 Item 가져와 mock 형식으로 정규화.

        반환: [{order_id, product, item, stage}, ...]
        실패하면 None 반환 (호출자가 mock fallback).
        """
        try:
            from app.management_client import ManagementClient
        except ImportError:
            return None
        client = None
        try:
            client = ManagementClient()
            items = client.list_items(limit=200)
        except Exception:  # noqa: BLE001
            return None
        finally:
            if client is not None:
                client.close()

        # gRPC stage enum int → 한국어 라벨 (UI 컬럼명)
        STAGE_INT_TO_LABEL = {
            1: "대기", 2: "주탕", 3: "탈형", 4: "후처리",
            5: "후처리", 6: "검사", 7: "적재", 8: "적재",
        }
        rows: list[dict[str, Any]] = []
        for it in items:
            rows.append({
                "order_id": it.order_id,
                "product": "-",  # Phase 3 범위 외, Phase 5에서 product join
                "item": f"I-{it.id}",
                "stage": STAGE_INT_TO_LABEL.get(int(it.cur_stage), "대기"),
            })
        return rows

    def _render_item_row_stage(self, row: int, stage_code: str) -> None:
        """단일 행의 stage 마커를 코드 기준으로 다시 그림 (gRPC 이벤트용)."""
        # V6 코드 → PyQt 한국어 컬럼 인덱스
        code_to_label = {
            "QUE": "대기", "MM": "주탕", "DM": "탈형",
            "PP": "후처리", "TR_PP": "후처리",
            "IP": "검사", "TR_LD": "적재", "SH": "적재",
        }
        target_label = code_to_label.get(stage_code, "대기")
        try:
            current_idx = ITEM_STAGE_COLUMNS.index(target_label)
        except ValueError:
            return

        current_color = QColor("#2563eb")
        done_color = QColor("#9ca3af")
        bold = QFont()
        bold.setBold(True)

        for col_offset in range(len(ITEM_STAGE_COLUMNS)):
            col = 3 + col_offset
            if col_offset < current_idx:
                cell = QTableWidgetItem("✓")
                cell.setForeground(QBrush(done_color))
            elif col_offset == current_idx:
                cell = QTableWidgetItem("●")
                cell.setForeground(QBrush(current_color))
                cell.setFont(bold)
            else:
                cell = QTableWidgetItem("")
            cell.setTextAlignment(Qt.AlignCenter)
            self._item_progress_table.setItem(row, col, cell)

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

        self._stages_table = QTableWidget(0, 3)
        self._stages_table.setHorizontalHeaderLabels(
            ["단계", "상태", "담당 설비"]
        )
        self._stages_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self._stages_table.verticalHeader().setVisible(False)
        self._stages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._stages_table.setAlternatingRowColors(True)
        self._stages_table.setMaximumHeight(220)
        layout.addWidget(self._stages_table)

        # 주문 → 제품 개당 실시간 위치 테이블
        item_label = QLabel("주문별 제품 실시간 위치")
        item_label.setObjectName("sectionTitle")
        layout.addWidget(item_label)

        item_columns = ["주문", "제품", "Item"] + ITEM_STAGE_COLUMNS
        self._item_progress_table = QTableWidget(0, len(item_columns))
        self._item_progress_table.setHorizontalHeaderLabels(item_columns)
        header = self._item_progress_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 제품명 열만 가변
        self._item_progress_table.verticalHeader().setVisible(False)
        self._item_progress_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._item_progress_table.setAlternatingRowColors(True)
        self._item_progress_table.setMaximumHeight(260)
        layout.addWidget(self._item_progress_table)

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

        # 주문 → 제품 개당 실시간 위치
        self._refresh_item_progress()

        # 공정 단계
        stages = self._api.get_process_stages() or []
        self._stages_table.setRowCount(len(stages))
        for row, stage in enumerate(stages):
            self._stages_table.setItem(row, 0, QTableWidgetItem(str(stage.get("name", ""))))
            status_item = QTableWidgetItem(str(stage.get("status", "")))
            status_item.setTextAlignment(Qt.AlignCenter)
            self._stages_table.setItem(row, 1, status_item)
            self._stages_table.setItem(
                row, 2, QTableWidgetItem(str(stage.get("equipment", "")))
            )

    def _refresh_item_progress(self) -> None:
        """주문 → Item 단위 실시간 공정 위치 테이블 갱신.

        각 행은 1개 item, 컬럼은 [주문, 제품, Item, 대기, 주탕, 탈형, 후처리, 검사, 적재].
        현재 단계 셀은 ●(파랑), 통과한 단계 셀은 ✓(회색)으로 표시.

        V6 Phase 3+: gRPC ListItems 우선 사용. 실패 시 mock fallback.
        """
        rows = self._fetch_items_via_grpc() or self._api.get_order_item_progress() or []
        # 주문 ID → Item 자연 정렬
        rows = sorted(rows, key=lambda r: (str(r.get("order_id", "")), str(r.get("item", ""))))

        self._item_progress_table.setRowCount(len(rows))
        current_color = QColor("#2563eb")  # 파랑 - 현재 단계
        done_color = QColor("#9ca3af")     # 회색 - 완료된 단계
        bold = QFont()
        bold.setBold(True)

        for row, info in enumerate(rows):
            order_id = str(info.get("order_id", ""))
            product = str(info.get("product", ""))
            item_id = str(info.get("item", ""))
            stage = str(info.get("stage", "대기"))

            # 좌측 3개 메타 컬럼
            self._item_progress_table.setItem(row, 0, QTableWidgetItem(order_id))
            self._item_progress_table.setItem(row, 1, QTableWidgetItem(product))
            item_cell = QTableWidgetItem(item_id)
            item_cell.setFont(bold)
            item_cell.setTextAlignment(Qt.AlignCenter)
            self._item_progress_table.setItem(row, 2, item_cell)

            # 단계 컬럼: 현재 ●, 통과한 단계 ✓
            current_idx = (
                ITEM_STAGE_COLUMNS.index(stage)
                if stage in ITEM_STAGE_COLUMNS
                else 0
            )
            for col_offset in range(len(ITEM_STAGE_COLUMNS)):
                col = 3 + col_offset
                if col_offset < current_idx:
                    cell = QTableWidgetItem("✓")
                    cell.setForeground(QBrush(done_color))
                elif col_offset == current_idx:
                    cell = QTableWidgetItem("●")
                    cell.setForeground(QBrush(current_color))
                    cell.setFont(bold)
                else:
                    cell = QTableWidgetItem("")
                cell.setTextAlignment(Qt.AlignCenter)
                self._item_progress_table.setItem(row, col, cell)

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
