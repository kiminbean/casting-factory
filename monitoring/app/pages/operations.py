"""운영 관리 (Operations) 페이지 — Confluence 32342045 v59 핑크 GUI 4건 통합.

본 페이지는 팀장 지시 (2026-04-19) 의 핑크 표시 GUI 항목들을 한 페이지에 깔끔히 모아둔다.

  - #3 패턴 등록 — 발주 ID + 위치 (1~6) 입력 → POST /api/production/patterns
  - #5 생산 시작 — 패턴 등록 후에만 활성 → POST /api/production/start
  - #4 후처리 요구사항 — 선택 item 의 필요 후처리 + 진행 상태 표시
  - #6 검사 요약 — 발주별 양품/불량/미검사 카운트

레이아웃:
  ┌───────────────── 상단: 발주 선택 + 패턴 등록 + 생산 시작 (#3, #5) ──────┐
  │  [발주 목록 ▼]   패턴 위치 [1-6 ▼]   [패턴 등록]   [생산 시작]        │
  └──────────────────────────────────────────────────────────────────────────┘
  ┌──── 좌측: 선택 발주의 item 목록 (#4) ────┬── 우측: 검사 요약 (#6) ──┐
  │  item_id │ cur_stat │ res │ defective?  │  ord │ total │ GP │ DP   │
  │  ...                                     │  ...                    │
  └──────────────────────────────────────────┴──────────────────────────┘
"""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient


class OperationsPage(QWidget):
    """4 pink GUI 항목 통합 운영 페이지."""

    refresh_requested = pyqtSignal()

    def __init__(self, api: ApiClient, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._api = api
        self._patterns: dict[int, int] = {}  # ord_id → ptn_loc
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ---- 상단: 발주 선택 + 패턴 등록 + 생산 시작 (Pink #3 + #5) ----
        ctrl_box = QGroupBox("발주 운영 (패턴 등록 → 생산 시작)")
        grid = QGridLayout(ctrl_box)
        grid.setSpacing(8)

        grid.addWidget(QLabel("발주:"), 0, 0)
        self._ord_combo = QComboBox()
        self._ord_combo.setMinimumWidth(280)
        self._ord_combo.currentIndexChanged.connect(self._on_ord_selected)
        grid.addWidget(self._ord_combo, 0, 1)

        grid.addWidget(QLabel("패턴 위치 (1-6):"), 0, 2)
        self._loc_spin = QSpinBox()
        self._loc_spin.setRange(1, 6)
        grid.addWidget(self._loc_spin, 0, 3)

        self._btn_pattern = QPushButton("패턴 등록")
        self._btn_pattern.clicked.connect(self._on_register_pattern)
        grid.addWidget(self._btn_pattern, 0, 4)

        self._btn_start = QPushButton("생산 시작")
        self._btn_start.clicked.connect(self._on_start_production)
        grid.addWidget(self._btn_start, 0, 5)
        self._btn_start.setEnabled(False)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #444; font-size: 12px;")
        grid.addWidget(self._status_label, 1, 0, 1, 6)

        root.addWidget(ctrl_box)

        # ---- 본문: item 목록 (#4) + 검사 요약 (#6) ----
        body = QHBoxLayout()
        body.setSpacing(12)

        # Pink #4 — item 별 후처리 요구사항
        items_box = QGroupBox("선택 발주의 item 목록 + 필요 후처리")
        items_v = QVBoxLayout(items_box)
        self._items_table = QTableWidget(0, 5)
        self._items_table.setHorizontalHeaderLabels(["item_id", "cur_stat", "res", "is_defective", "필요 후처리"])
        self._items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._items_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        items_v.addWidget(self._items_table)

        body.addWidget(items_box, 2)

        # Pink #6 — 검사 요약
        sum_box = QGroupBox("발주별 검사 요약 (양품 / 불량 / 미검사)")
        sum_v = QVBoxLayout(sum_box)
        self._summary_table = QTableWidget(0, 5)
        self._summary_table.setHorizontalHeaderLabels(["ord_id", "total", "GP", "DP", "미검사"])
        self._summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        sum_v.addWidget(self._summary_table)
        body.addWidget(sum_box, 1)

        root.addLayout(body)

        # ---- 시계열 mini-summary (hourly 생산 + err_log trend) ----
        ts_box = QGroupBox("최근 24h 시계열 (TimescaleDB 검출 자동 분기)")
        ts_v = QHBoxLayout(ts_box)
        self._ts_hourly = QLabel("hourly 생산: -")
        self._ts_hourly.setStyleSheet("font-size: 12px; color: #1f2937;")
        ts_v.addWidget(self._ts_hourly, stretch=1)
        self._ts_err = QLabel("err_log trend: -")
        self._ts_err.setStyleSheet("font-size: 12px; color: #1f2937;")
        ts_v.addWidget(self._ts_err, stretch=1)
        self._ts_badge = QLabel("TS: -")
        self._ts_badge.setStyleSheet(
            "font-size: 11px; padding: 2px 8px; border-radius: 4px;"
            " background: #e5e7eb; color: #374151;"
        )
        ts_v.addWidget(self._ts_badge, stretch=0)
        root.addWidget(ts_box)

        # ---- 하단: SPEC-AMR-001 핸드오프 ACK 패널 ----
        handoff_box = QGroupBox("SPEC-AMR-001 핸드오프 ACK (운영자 확인)")
        handoff_v = QHBoxLayout(handoff_box)
        handoff_info = QLabel(
            "후처리존(ToPP) 도착 AMR 이 WAIT_HANDOFF 로 정지하면 가장 오래된 1건을 풀어줍니다.\n"
            "(시퀀서가 활성(FMS_AUTOPLAY=1)일 때만 ToPP 가 자동으로 WAIT_HANDOFF 상태에 도달합니다.)"
        )
        handoff_info.setWordWrap(True)
        handoff_info.setStyleSheet("color: #555; font-size: 12px;")
        handoff_v.addWidget(handoff_info, stretch=2)
        self._btn_handoff = QPushButton("🔔 후처리 ACK 발행")
        self._btn_handoff.setStyleSheet(
            "QPushButton { background:#dc2626; color:white; padding:8px 16px;"
            " font-weight:bold; border-radius:6px; }"
            "QPushButton:hover { background:#b91c1c; }"
            "QPushButton:disabled { background:#9ca3af; }"
        )
        self._btn_handoff.clicked.connect(self._on_handoff_ack)
        handoff_v.addWidget(self._btn_handoff, stretch=0)
        self._handoff_result = QLabel("")
        self._handoff_result.setWordWrap(True)
        self._handoff_result.setStyleSheet("color: #16a34a; font-size: 12px;")
        handoff_v.addWidget(self._handoff_result, stretch=2)
        root.addWidget(handoff_box)

        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.refresh)
        root.addWidget(refresh_btn, alignment=Qt.AlignRight)

    # ------------------------------------------------------------------
    # Refresh / data load
    # ------------------------------------------------------------------

    @pyqtSlot()
    def refresh(self) -> None:
        """발주 목록 + 패턴 + 검사 요약 재조회."""
        try:
            orders = self._api.get_smartcast_orders() or []
            patterns = self._api.get_patterns() or []
            summary = self._api.get_inspection_summary() or []
        except Exception as exc:  # noqa: BLE001
            self._status_label.setText(f"백엔드 조회 실패: {exc}")
            return

        self._patterns = {int(p["ptn_id"]): int(p["ptn_loc"]) for p in patterns}

        # 발주 콤보 갱신
        self._ord_combo.blockSignals(True)
        self._ord_combo.clear()
        for o in orders:
            ord_id = o.get("ord_id")
            user_id = o.get("user_id")
            stat = o.get("latest_stat", "RCVD")
            label = f"ord_{ord_id}  (user={user_id}, {stat})"
            self._ord_combo.addItem(label, userData=ord_id)
        self._ord_combo.blockSignals(False)
        if self._ord_combo.count() > 0:
            self._ord_combo.setCurrentIndex(0)
            self._on_ord_selected()

        # 검사 요약 테이블
        self._summary_table.setRowCount(len(summary))
        for row, s in enumerate(summary):
            cells = [
                str(s.get("ord_id", "")),
                str(s.get("total_items", 0)),
                str(s.get("good_count", 0)),
                str(s.get("defective_count", 0)),
                str(s.get("pending_count", 0)),
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self._summary_table.setItem(row, col, item)

        # 시계열 mini-summary (PyQt 기본 위젯만, 별도 charts lib 없이 텍스트 요약)
        try:
            ds = self._api.get_dashboard_stats_v2() or {}
            ts_enabled = ds.get("timescaledb_enabled", False)
            self._ts_badge.setText("TimescaleDB: ON" if ts_enabled else "TimescaleDB: OFF (date_trunc 폴백)")
            self._ts_badge.setStyleSheet(
                "font-size: 11px; padding: 2px 8px; border-radius: 4px;"
                + (" background: #16a34a; color: white;" if ts_enabled else " background: #e5e7eb; color: #374151;")
            )
        except Exception:
            self._ts_badge.setText("TS: ?")

        try:
            hourly = self._api.get_hourly_production_v2(hours=24) or []
            total_h = sum(int(h.get("produced", 0)) for h in hourly)
            peak = max((int(h.get("produced", 0)) for h in hourly), default=0)
            self._ts_hourly.setText(
                f"hourly 생산 (24h): 합계 {total_h} 개 / 시간대 {len(hourly)}개 / 피크 {peak} 개"
            )
        except Exception as exc:  # noqa: BLE001
            self._ts_hourly.setText(f"hourly 조회 실패: {exc}")

        try:
            trend = self._api.get_err_log_trend(hours=24) or []
            equip_total = sum(int(t.get("count", 0)) for t in trend if t.get("source") == "equip")
            trans_total = sum(int(t.get("count", 0)) for t in trend if t.get("source") == "trans")
            self._ts_err.setText(
                f"err_log (24h): equip {equip_total} 건 / trans {trans_total} 건"
            )
        except Exception as exc:  # noqa: BLE001
            self._ts_err.setText(f"err_log 조회 실패: {exc}")

    # ------------------------------------------------------------------
    # Slot handlers
    # ------------------------------------------------------------------

    def _current_ord_id(self) -> int | None:
        idx = self._ord_combo.currentIndex()
        if idx < 0:
            return None
        ord_id = self._ord_combo.itemData(idx)
        return int(ord_id) if ord_id is not None else None

    @pyqtSlot()
    def _on_ord_selected(self) -> None:
        ord_id = self._current_ord_id()
        if ord_id is None:
            return

        # 패턴 등록 여부에 따라 생산 시작 버튼 활성/비활성
        registered = ord_id in self._patterns
        self._btn_start.setEnabled(registered)
        if registered:
            self._loc_spin.setValue(self._patterns[ord_id])
            self._status_label.setText(
                f"발주 {ord_id}: 패턴 위치 {self._patterns[ord_id]} 등록됨 → 생산 시작 가능."
            )
        else:
            self._status_label.setText(
                f"발주 {ord_id}: 패턴 미등록. 위치 선택 후 [패턴 등록] 클릭 필요."
            )

        # item 목록 + 필요 후처리 (Pink #4)
        items = self._api.get_smartcast_items(ord_id=ord_id) or []
        self._items_table.setRowCount(len(items))
        for row, it in enumerate(items):
            item_id = int(it.get("item_id"))
            pp_label = self._format_pp_requirements(item_id)
            cells = [
                str(item_id),
                str(it.get("cur_stat", "")),
                str(it.get("cur_res", "") or ""),
                self._format_defective(it.get("is_defective")),
                pp_label,
            ]
            for col, val in enumerate(cells):
                qi = QTableWidgetItem(val)
                qi.setTextAlignment(Qt.AlignCenter)
                self._items_table.setItem(row, col, qi)

    def _format_defective(self, value: Any) -> str:
        if value is None:
            return "미검사"
        return "불량 (DP)" if value else "양품 (GP)"

    def _format_pp_requirements(self, item_id: int) -> str:
        try:
            data = self._api.get_item_pp_requirements(item_id)
        except Exception:
            return "조회 실패"
        if not data:
            return "-"
        opts = data.get("pp_options", [])
        statuses = {t.get("pp_nm"): t.get("txn_stat") for t in data.get("pp_task_status", [])}
        if not opts:
            return "후처리 없음"
        return ", ".join(f"{o['pp_nm']}[{statuses.get(o['pp_nm'], 'QUE')}]" for o in opts)

    @pyqtSlot()
    def _on_register_pattern(self) -> None:
        ord_id = self._current_ord_id()
        if ord_id is None:
            QMessageBox.warning(self, "발주 선택", "먼저 발주를 선택하세요.")
            return
        loc = self._loc_spin.value()
        try:
            self._api.register_pattern(ord_id, loc)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "패턴 등록 실패", str(exc))
            return
        QMessageBox.information(self, "패턴 등록", f"발주 {ord_id} → 패턴 위치 {loc} 등록 완료.")
        self.refresh()

    @pyqtSlot()
    def _on_start_production(self) -> None:
        ord_id = self._current_ord_id()
        if ord_id is None:
            return
        try:
            result = self._api.start_production(ord_id)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "생산 시작 실패", str(exc))
            return
        msg = (result or {}).get("message", "Started.")
        QMessageBox.information(self, "생산 시작", f"발주 {ord_id}\n{msg}")
        self.refresh()

    @pyqtSlot()
    def _on_handoff_ack(self) -> None:
        """SPEC-AMR-001 핸드오프 ACK — WAIT_HANDOFF AMR 1건 풀기."""
        try:
            data = self._api.post_handoff_ack() or {}
        except Exception as exc:  # noqa: BLE001
            self._handoff_result.setStyleSheet("color: #dc2626; font-size: 12px;")
            self._handoff_result.setText(f"❌ 호출 실패: {exc}")
            return
        if data.get("released"):
            self._handoff_result.setStyleSheet("color: #16a34a; font-size: 12px;")
            self._handoff_result.setText(
                f"✓ release: task={data.get('task_id')} amr={data.get('amr_id')} "
                f"item={data.get('item_id')} ord={data.get('ord_id')}"
            )
        else:
            self._handoff_result.setStyleSheet("color: #d97706; font-size: 12px;")
            self._handoff_result.setText(
                f"⚠ orphan: {data.get('reason', '대기 중인 핸드오프 없음')}"
            )
