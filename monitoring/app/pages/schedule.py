"""생산 계획 페이지 — 우선순위 계산 + 순서 확정.

웹의 "생산 승인" 버튼으로 주문이 in_production 상태로 전환되면
ProductionJob 레코드가 생성되어 이 페이지의 풀에 들어온다.

워크플로:
    1. 승인 주문 풀(approved + in_production) 조회
    2. 다중 선택 → "우선순위 계산" 버튼
    3. 7요소 가중 점수 결과 표시 (상단 테이블)
    4. (향후) 수동 순서 조정 + 사유 입력 + PriorityLog 기록
    5. (향후) 생산 개시 확정 → 자원 배정

@MX:NOTE: 2026-04-08 웹에서 이관된 기능. 기존 src/app/production/schedule 페이지 삭제.
"""
from __future__ import annotations

from typing import Any

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.pages.dashboard import KpiCard


# ---------- 표시용 상수 ----------

STATUS_LABEL = {
    "approved": "승인 대기",
    "in_production": "생산 승인",
}

STATUS_COLOR = {
    "approved": "#fef3c7",    # amber 100
    "in_production": "#dbeafe", # blue 100
}

DELAY_RISK_LABEL = {
    "high": "높음",
    "medium": "보통",
    "low": "낮음",
}

DELAY_RISK_COLOR = {
    "high": "#ef4444",
    "medium": "#f59e0b",
    "low": "#10b981",
}


def _format_currency(value: Any) -> str:
    try:
        num = float(value or 0)
    except (TypeError, ValueError):
        return "-"
    return f"₩{int(num):,}"


def _format_date(value: str | None) -> str:
    if not value:
        return "-"
    # ISO-8601 또는 YYYY-MM-DD 모두 허용 — 앞 10자만 사용
    return value[:10]


# ---------- 페이지 본체 ----------

class SchedulePage(QWidget):
    """생산 계획 — 우선순위 계산 UI.

    상단: KPI 카드 (승인 대기 수, 생산 승인 수, 금일 계산 수)
    중앙: 좌측 주문 풀 테이블 (다중 선택) + 우측 계산 결과 테이블
    하단: 액션 버튼 (계산 / 선택 해제 / 새로고침)
    """

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self._api = api
        self._kpi_cards: dict[str, KpiCard] = {}
        self._orders: list[dict[str, Any]] = []
        self._priority_results: list[dict[str, Any]] = []
        self._calculation_count: int = 0  # 세션 내 계산 횟수

        self._build_ui()
        self.refresh()

    # ================================================================
    # UI 구성
    # ================================================================

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # 페이지 제목
        title = QLabel("생산 계획 — 우선순위 계산")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        subtitle = QLabel(
            "웹에서 '생산 승인'된 주문의 우선순위를 7요소 가중 점수제(100점 만점)로 계산합니다. "
            "좌측에서 주문을 선택하고 '우선순위 계산' 버튼을 누르세요."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6b7280; font-size: 12px;")
        root.addWidget(subtitle)

        # KPI 카드 (3개)
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        kpi_items = [
            ("approved_count", "승인 대기", "건"),
            ("in_production_count", "생산 승인", "건"),
            ("calc_count", "금일 계산", "회"),
        ]
        for key, label, unit in kpi_items:
            card = KpiCard(label, unit=unit)
            self._kpi_cards[key] = card
            kpi_row.addWidget(card, stretch=1)
        root.addLayout(kpi_row)

        # 주문 풀 + 결과 2열 레이아웃
        split_layout = QHBoxLayout()
        split_layout.setSpacing(14)

        # ---------- 좌측: 승인 주문 풀 ----------
        left_panel = self._build_orders_panel()
        split_layout.addWidget(left_panel, stretch=1)

        # ---------- 우측: 우선순위 결과 ----------
        right_panel = self._build_results_panel()
        split_layout.addWidget(right_panel, stretch=1)

        root.addLayout(split_layout, stretch=1)

        # 하단 액션 버튼
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self._calc_btn = QPushButton("⚙ 우선순위 계산")
        self._calc_btn.setObjectName("primaryButton")
        self._calc_btn.setMinimumHeight(42)
        self._calc_btn.clicked.connect(self._on_calculate)
        self._calc_btn.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; "
            "font-weight: 700; font-size: 14px; border-radius: 8px; "
            "padding: 10px 20px; } "
            "QPushButton:hover { background-color: #1d4ed8; } "
            "QPushButton:disabled { background-color: #9ca3af; }"
        )
        action_row.addWidget(self._calc_btn)

        self._clear_btn = QPushButton("선택 해제")
        self._clear_btn.setMinimumHeight(42)
        self._clear_btn.clicked.connect(self._on_clear_selection)
        self._clear_btn.setStyleSheet(
            "QPushButton { background-color: #f3f4f6; color: #374151; "
            "font-weight: 600; font-size: 13px; border: 1px solid #d1d5db; "
            "border-radius: 8px; padding: 10px 18px; } "
            "QPushButton:hover { background-color: #e5e7eb; }"
        )
        action_row.addWidget(self._clear_btn)

        action_row.addStretch()

        self._refresh_btn = QPushButton("↻ 새로고침")
        self._refresh_btn.setMinimumHeight(42)
        self._refresh_btn.clicked.connect(self.refresh)
        self._refresh_btn.setStyleSheet(
            "QPushButton { background-color: #f3f4f6; color: #374151; "
            "font-weight: 600; font-size: 13px; border: 1px solid #d1d5db; "
            "border-radius: 8px; padding: 10px 18px; } "
            "QPushButton:hover { background-color: #e5e7eb; }"
        )
        action_row.addWidget(self._refresh_btn)

        root.addLayout(action_row)

    def _build_orders_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("card")
        panel.setStyleSheet(
            "#card { background-color: white; border: 1px solid #e5e7eb; "
            "border-radius: 10px; }"
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QLabel("📋 승인 주문 풀")
        header.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #1f2937;"
        )
        layout.addWidget(header)

        hint = QLabel("Ctrl/Shift 다중 선택 · 계산할 주문을 체크하세요")
        hint.setStyleSheet("font-size: 11px; color: #9ca3af;")
        layout.addWidget(hint)

        self._orders_table = QTableWidget(0, 5)
        self._orders_table.setHorizontalHeaderLabels(
            ["주문 ID", "회사명", "납기", "금액", "상태"]
        )
        self._orders_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._orders_table.setSelectionMode(QAbstractItemView.MultiSelection)
        self._orders_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._orders_table.verticalHeader().setVisible(False)
        self._orders_table.setAlternatingRowColors(True)
        self._orders_table.setStyleSheet(
            "QTableWidget { gridline-color: #e5e7eb; font-size: 12px; "
            "selection-background-color: #dbeafe; selection-color: #1e40af; } "
            "QHeaderView::section { background-color: #f9fafb; color: #374151; "
            "font-weight: 600; padding: 8px; border: none; "
            "border-bottom: 1px solid #e5e7eb; }"
        )
        header_view = self._orders_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self._orders_table, stretch=1)

        self._orders_count_lbl = QLabel("총 0건")
        self._orders_count_lbl.setStyleSheet(
            "font-size: 11px; color: #6b7280;"
        )
        layout.addWidget(self._orders_count_lbl)

        return panel

    def _build_results_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("card")
        panel.setStyleSheet(
            "#card { background-color: white; border: 1px solid #e5e7eb; "
            "border-radius: 10px; }"
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QLabel("🏆 우선순위 계산 결과")
        header.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #1f2937;"
        )
        layout.addWidget(header)

        hint = QLabel("7요소 가중 점수 (납기 25 · 착수 20 · 체류 15 · 지연 15 · 고객 10 · 수량 10 · 세팅 5)")
        hint.setWordWrap(True)
        hint.setStyleSheet("font-size: 11px; color: #9ca3af;")
        layout.addWidget(hint)

        self._results_table = QTableWidget(0, 6)
        self._results_table.setHorizontalHeaderLabels(
            ["순위", "주문 ID", "회사명", "총점", "지연위험", "착수"]
        )
        self._results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._results_table.verticalHeader().setVisible(False)
        self._results_table.setAlternatingRowColors(True)
        self._results_table.setStyleSheet(
            "QTableWidget { gridline-color: #e5e7eb; font-size: 12px; "
            "selection-background-color: #fef3c7; selection-color: #92400e; } "
            "QHeaderView::section { background-color: #f9fafb; color: #374151; "
            "font-weight: 600; padding: 8px; border: none; "
            "border-bottom: 1px solid #e5e7eb; }"
        )
        header_view = self._results_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self._results_table.itemSelectionChanged.connect(self._on_result_selected)
        layout.addWidget(self._results_table, stretch=1)

        # 선택된 결과의 상세 (추천 사유 등)
        self._reason_label = QLabel("결과 행을 선택하면 추천 사유가 표시됩니다.")
        self._reason_label.setWordWrap(True)
        self._reason_label.setStyleSheet(
            "font-size: 12px; color: #4b5563; background-color: #f9fafb; "
            "padding: 10px 12px; border-radius: 6px; border: 1px solid #e5e7eb;"
        )
        self._reason_label.setMinimumHeight(60)
        layout.addWidget(self._reason_label)

        return panel

    # ================================================================
    # 데이터 로드 / 렌더
    # ================================================================

    def refresh(self) -> None:
        """주문 풀 + KPI 갱신."""
        self._orders = self._api.get_approved_and_running_orders()
        self._render_orders_table()
        self._update_kpis()

    def _render_orders_table(self) -> None:
        self._orders_table.setRowCount(0)
        for idx, order in enumerate(self._orders):
            self._orders_table.insertRow(idx)

            id_item = QTableWidgetItem(str(order.get("id", "")))
            id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self._orders_table.setItem(idx, 0, id_item)

            self._orders_table.setItem(
                idx, 1, QTableWidgetItem(str(order.get("company_name", "-")))
            )

            due_item = QTableWidgetItem(_format_date(order.get("requested_delivery")))
            due_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self._orders_table.setItem(idx, 2, due_item)

            amount_item = QTableWidgetItem(_format_currency(order.get("total_amount")))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._orders_table.setItem(idx, 3, amount_item)

            status = str(order.get("status", ""))
            label = STATUS_LABEL.get(status, status)
            status_item = QTableWidgetItem(label)
            status_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            color = STATUS_COLOR.get(status, "#f3f4f6")
            status_item.setBackground(QColor(color))
            self._orders_table.setItem(idx, 4, status_item)

        self._orders_count_lbl.setText(f"총 {len(self._orders)}건")

    def _update_kpis(self) -> None:
        approved = sum(1 for o in self._orders if o.get("status") == "approved")
        in_prod = sum(1 for o in self._orders if o.get("status") == "in_production")
        self._kpi_cards["approved_count"].update_value(approved)
        self._kpi_cards["in_production_count"].update_value(in_prod)
        self._kpi_cards["calc_count"].update_value(self._calculation_count)

    # ================================================================
    # 액션: 우선순위 계산
    # ================================================================

    def _get_selected_order_ids(self) -> list[str]:
        """다중 선택된 행의 주문 ID 리스트."""
        selected_rows: set[int] = set()
        for item in self._orders_table.selectedItems():
            selected_rows.add(item.row())

        ids: list[str] = []
        for row in sorted(selected_rows):
            id_item = self._orders_table.item(row, 0)
            if id_item and id_item.text():
                ids.append(id_item.text())
        return ids

    def _on_calculate(self) -> None:
        order_ids = self._get_selected_order_ids()
        if not order_ids:
            QMessageBox.information(
                self,
                "주문 선택 필요",
                "우선순위를 계산할 주문을 좌측 풀에서 1건 이상 선택하세요.\n"
                "(Ctrl/Shift 다중 선택)",
            )
            return

        # 백엔드 호출 (실패 시 예외)
        try:
            self._calc_btn.setEnabled(False)
            self._calc_btn.setText("⏳ 계산 중...")
            response = self._api.calculate_priority(order_ids)
        except requests.RequestException as exc:
            QMessageBox.critical(
                self,
                "우선순위 계산 실패",
                f"백엔드 API 호출 실패:\n{exc}\n\n"
                f"백엔드 서버가 실행 중인지 확인하세요.",
            )
            return
        finally:
            self._calc_btn.setEnabled(True)
            self._calc_btn.setText("⚙ 우선순위 계산")

        results = response.get("results", []) if isinstance(response, dict) else []
        if not results:
            QMessageBox.warning(
                self,
                "계산 결과 없음",
                "백엔드가 빈 결과를 반환했습니다. 선택한 주문이 'approved' 상태인지 확인하세요.",
            )
            return

        self._priority_results = results
        self._calculation_count += 1
        self._render_results_table()
        self._update_kpis()

    def _render_results_table(self) -> None:
        self._results_table.setRowCount(0)
        self._reason_label.setText("결과 행을 선택하면 추천 사유가 표시됩니다.")

        # backend 응답 정렬: rank 오름차순 기대. 보조 정렬로 total_score desc.
        sorted_results = sorted(
            self._priority_results,
            key=lambda r: (r.get("rank", 999), -float(r.get("total_score", 0))),
        )

        for idx, result in enumerate(sorted_results):
            self._results_table.insertRow(idx)

            rank_item = QTableWidgetItem(f"#{result.get('rank', idx + 1)}")
            rank_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            if idx == 0:
                rank_item.setBackground(QColor("#fef3c7"))  # 1위 하이라이트
                rank_item.setForeground(QColor("#92400e"))
            self._results_table.setItem(idx, 0, rank_item)

            id_item = QTableWidgetItem(str(result.get("order_id", "-")))
            id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self._results_table.setItem(idx, 1, id_item)

            self._results_table.setItem(
                idx, 2, QTableWidgetItem(str(result.get("company_name", "-")))
            )

            score = result.get("total_score", 0)
            score_item = QTableWidgetItem(f"{score:.1f} / 100")
            score_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self._results_table.setItem(idx, 3, score_item)

            delay = str(result.get("delay_risk", "low"))
            delay_item = QTableWidgetItem(DELAY_RISK_LABEL.get(delay, delay))
            delay_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            delay_item.setForeground(QColor(DELAY_RISK_COLOR.get(delay, "#9ca3af")))
            self._results_table.setItem(idx, 4, delay_item)

            ready = result.get("ready_status", "")
            ready_item = QTableWidgetItem(
                "✓ 가능" if ready == "ready" else "✗ 불가"
            )
            ready_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            ready_item.setForeground(
                QColor("#10b981" if ready == "ready" else "#ef4444")
            )
            self._results_table.setItem(idx, 5, ready_item)

    def _on_result_selected(self) -> None:
        rows = self._results_table.selectionModel().selectedRows()
        if not rows:
            return
        row_idx = rows[0].row()
        if row_idx >= len(self._priority_results):
            return

        # 정렬 기준으로 가져오기 (render와 동일 방식)
        sorted_results = sorted(
            self._priority_results,
            key=lambda r: (r.get("rank", 999), -float(r.get("total_score", 0))),
        )
        result = sorted_results[row_idx]

        reason = result.get("recommendation_reason", "추천 사유 없음")
        blocking = result.get("blocking_reasons", [])
        factors = result.get("factors", [])

        parts: list[str] = [f"📌 추천 사유: {reason}"]
        if factors:
            factor_texts = [
                f"{f.get('name', '-')} {f.get('score', 0):.1f}/{f.get('max_score', 0)}"
                for f in factors
            ]
            parts.append("• 세부 점수: " + " · ".join(factor_texts))
        if blocking:
            parts.append("⚠ 착수 제약: " + ", ".join(blocking))

        self._reason_label.setText("\n".join(parts))

    def _on_clear_selection(self) -> None:
        self._orders_table.clearSelection()

    # ================================================================
    # WebSocket / MQTT 브로드캐스트 (선택적)
    # ================================================================

    def handle_ws_message(self, payload: dict[str, Any]) -> None:
        """WS로 주문 상태 변경 알림이 오면 자동 새로고침."""
        event_type = str(payload.get("type", "")).lower() if payload else ""
        if event_type in ("order_update", "order_status_changed", "production_approved"):
            self.refresh()
