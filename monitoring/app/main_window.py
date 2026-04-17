"""QMainWindow - 좌측 사이드바 + 우측 스택 레이아웃."""
from __future__ import annotations

from typing import Any

from datetime import datetime

from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.api_client import ApiClient
from app.mqtt_worker import MqttThread, MqttWorker, mqtt_enabled
from app.pages.dashboard import DashboardPage
from app.pages.logistics import LogisticsPage
from app.pages.map import FactoryMapPage
from app.pages.production import ProductionPage
from app.pages.quality import QualityPage
from app.pages.schedule import SchedulePage
from app.widgets.alert_widgets import ToastNotification, _normalize_level
from app.ws_worker import WebSocketWorker
from config import APP_NAME, APP_VERSION, AMR_POLL_INTERVAL, REFRESH_INTERVAL_MS


NAV_ITEMS: list[tuple[str, str]] = [
    ("dashboard", "대시보드"),
    ("map", "공장 맵"),
    ("production", "생산 모니터링"),
    ("schedule", "생산 계획"),
    ("quality", "품질 검사"),
    ("logistics", "물류 / 이송"),
]


class MainWindow(QMainWindow):
    """모니터링 앱 메인 윈도우."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
        self.resize(1400, 900)

        self._api = ApiClient()
        self._mqtt_worker: MqttWorker | None = None
        self._mqtt_thread: MqttThread | None = None
        self._amr_thread = None

        self._build_ui()
        self._start_refresh_timer()
        self._start_websocket()
        self._start_mqtt()
        self._start_amr_status()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 좌측 사이드바
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        self._sidebar = sidebar
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        logo = QLabel("주물공장 모니터링")
        logo.setObjectName("sidebarLogo")
        logo.setAlignment(Qt.AlignCenter)
        side_layout.addWidget(logo)

        self._nav = QListWidget()
        self._nav.setObjectName("sidebarNav")
        for _, label in NAV_ITEMS:
            self._nav.addItem(QListWidgetItem(label))
        self._nav.currentRowChanged.connect(self._on_nav_changed)
        side_layout.addWidget(self._nav, stretch=1)

        version_lbl = QLabel(f"v{APP_VERSION}")
        version_lbl.setObjectName("sidebarVersion")
        version_lbl.setAlignment(Qt.AlignCenter)
        side_layout.addWidget(version_lbl)

        root.addWidget(sidebar)

        # 사이드바 토글 바 (얇은 수직 버튼)
        self._sidebar_toggle = QToolButton()
        self._sidebar_toggle.setObjectName("sidebarToggle")
        self._sidebar_toggle.setCheckable(False)
        self._sidebar_toggle.setText("◀")
        self._sidebar_toggle.setToolTip("사이드바 숨기기/보이기 (Ctrl+B)")
        self._sidebar_toggle.setFixedWidth(16)
        self._sidebar_toggle.setCursor(Qt.PointingHandCursor)
        self._sidebar_toggle.setAutoRaise(True)
        self._sidebar_toggle.setStyleSheet(
            "QToolButton#sidebarToggle {"
            " background-color: #e5e7eb; color: #374151;"
            " border: none; border-right: 1px solid #d1d5db;"
            " font-size: 11px; padding: 0; }"
            "QToolButton#sidebarToggle:hover { background-color: #d1d5db; }"
        )
        self._sidebar_toggle.clicked.connect(self._toggle_sidebar)
        root.addWidget(self._sidebar_toggle)

        # 우측 스택 (NAV_ITEMS 순서와 반드시 일치)
        self._stack = QStackedWidget()
        self._dashboard = DashboardPage(self._api)
        self._map = FactoryMapPage(self._api)
        self._production = ProductionPage(self._api)
        self._schedule = SchedulePage(self._api)
        self._quality = QualityPage(self._api)
        self._logistics = LogisticsPage(self._api)

        for page in (
            self._dashboard,
            self._map,
            self._production,
            self._schedule,
            self._quality,
            self._logistics,
        ):
            self._stack.addWidget(page)

        root.addWidget(self._stack, stretch=1)

        # 상태바
        status = QStatusBar()
        self.setStatusBar(status)

        # 좌측: 버전 안내
        hint = QLabel(f"v{APP_VERSION}  ·  F11 전체화면")
        hint.setStyleSheet("color: #9ca3af; padding: 0 10px;")
        status.addWidget(hint)

        # 우측: 시계 + 연결 상태
        self._clock_label = QLabel("--:--:--")
        self._clock_label.setStyleSheet(
            "color: #111827; font-family: 'Menlo', 'Consolas', 'Courier New', monospace;"
            "font-weight: bold; padding: 0 14px;"
        )
        status.addPermanentWidget(self._clock_label)

        self._ws_status_label = QLabel("WS: disconnected")
        self._ws_status_label.setStyleSheet("color: #9ca3af; padding: 0 10px;")
        status.addPermanentWidget(self._ws_status_label)
        self._mqtt_status_label = QLabel("MQTT: disabled")
        self._mqtt_status_label.setStyleSheet("color: #9ca3af; padding: 0 10px;")
        status.addPermanentWidget(self._mqtt_status_label)

        # 시계 타이머 (1초)
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start()
        self._update_clock()

        # 전체화면 단축키 F11
        self._fullscreen_action = QAction("전체화면 토글", self)
        self._fullscreen_action.setShortcut(QKeySequence("F11"))
        self._fullscreen_action.triggered.connect(self._toggle_fullscreen)
        self.addAction(self._fullscreen_action)

        # ESC 로 전체화면 해제
        self._exit_fs_action = QAction("전체화면 나가기", self)
        self._exit_fs_action.setShortcut(QKeySequence("Escape"))
        self._exit_fs_action.triggered.connect(self._exit_fullscreen)
        self.addAction(self._exit_fs_action)

        # 알림 중복 방지 (같은 critical 5초 내 재발행 차단)
        self._seen_alerts: set[str] = set()

        # 사이드바 토글 단축키 Ctrl+B
        self._toggle_sidebar_action = QAction("사이드바 토글", self)
        self._toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        self._toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        self.addAction(self._toggle_sidebar_action)

        # 페이지 단축키 Ctrl+1..6
        for i in range(len(NAV_ITEMS)):
            action = QAction(f"Page {i + 1}", self)
            action.setShortcut(QKeySequence(f"Ctrl+{i + 1}"))
            action.triggered.connect(lambda _=False, idx=i: self._nav.setCurrentRow(idx))
            self.addAction(action)

        # 첫 페이지 선택
        self._nav.setCurrentRow(0)

    def _on_nav_changed(self, row: int) -> None:
        if 0 <= row < self._stack.count():
            self._stack.setCurrentIndex(row)

    def _toggle_sidebar(self) -> None:
        """좌측 사이드바 표시/숨김 토글."""
        visible = self._sidebar.isVisible()
        self._sidebar.setVisible(not visible)
        self._sidebar_toggle.setText("▶" if visible else "◀")
        self._sidebar_toggle.setToolTip(
            "사이드바 보이기 (Ctrl+B)" if visible else "사이드바 숨기기 (Ctrl+B)"
        )

    # ---------- 주기 갱신 ----------
    def _start_refresh_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(REFRESH_INTERVAL_MS)
        self._timer.timeout.connect(self._refresh_current_page)
        self._timer.start()

    def _refresh_current_page(self) -> None:
        # 이전 refresh 가 아직 진행 중이면 중복 실행 방지 (메인 스레드 큐 폭주 방지)
        if getattr(self, "_refreshing", False):
            return
        page = self._stack.currentWidget()
        if not hasattr(page, "refresh"):
            return
        self._refreshing = True
        try:
            page.refresh()
        finally:
            self._refreshing = False

    # ---------- WebSocket (V6 Phase 8: 환경변수로 비활성화 가능) ----------
    def _start_websocket(self) -> None:
        # CASTING_WS_ENABLED=0 (기본 0) 이면 ws_worker 미기동.
        # alerts/items 실시간은 gRPC stream(WatchAlerts/WatchItems) 로 대체.
        import os as _os
        if _os.environ.get("CASTING_WS_ENABLED", "0") not in ("1", "true", "yes"):
            self._ws_status_label.setText("WS: V6 disabled (gRPC streaming 사용)")
            self._start_alert_stream()
            return
        self._ws_thread = QThread()
        self._ws_worker = WebSocketWorker()
        self._ws_worker.moveToThread(self._ws_thread)
        self._ws_thread.started.connect(self._ws_worker.run)
        self._ws_worker.connection_state.connect(self._on_ws_state)
        self._ws_worker.message_received.connect(self._on_ws_message)
        self._ws_thread.start()
        self._start_alert_stream()

    # ---------- gRPC AlertStreamWorker (V6 Phase 8) ----------
    def _start_alert_stream(self) -> None:
        try:
            from app.workers.alert_stream_worker import AlertStreamWorker, AlertStreamThread
        except ImportError:
            return
        # severity_filter=None → 모든 severity 수신 (critical/warning/info).
        # critical 은 main_window 에서 모달, 그 외는 토스트.
        self._alert_worker = AlertStreamWorker(severity_filter=None)
        self._alert_worker.alert_event.connect(self._on_alert_event)
        self._alert_worker.connection_state.connect(self._on_alert_conn_state)
        self._alert_thread = AlertStreamThread(self._alert_worker)
        self._alert_thread.start()

    def _on_alert_event(self, alert_id: str, severity: str, error_code: str,
                        message: str, equipment_id: str, zone: str, at_iso: str) -> None:
        """gRPC alert → severity 별 차별 표시.

        - critical: QMessageBox.critical (모달, 사용자 ack 필요)
        - warning/info/etc: 우상단 토스트 (5초 자동 사라짐)

        critical 모달 폭주 방지: 같은 alert_id 는 1회만 표시 (set 캐시).

        @MX:NOTE: AlertStreamWorker.pyqtSignal 의 슬롯. WebSocket 단종 대체 채널 (V6 Phase 8).
        @MX:REASON: critical 은 사용자 ack 보장 필요 (자동 사라짐 토스트로는 누락 가능).
        """
        import logging as _lg
        _lg.getLogger(__name__).info(
            "gRPC alert 수신: id=%s sev=%s code=%s msg=%s",
            alert_id[:24], severity, error_code, message[:50],
        )

        title_prefix = {"critical": "🚨 CRITICAL", "warning": "⚠ WARNING", "info": "ℹ INFO"}
        title = f"{title_prefix.get(severity, severity.upper())} {error_code or zone or ''}".strip()
        body = message or alert_id
        if equipment_id:
            body = f"{body}\n설비: {equipment_id}"

        if (severity or "").lower() == "critical":
            # 폭주 방지 — 같은 alert_id 는 모달 1회만
            if not hasattr(self, "_shown_critical_alerts"):
                self._shown_critical_alerts = set()
            if alert_id in self._shown_critical_alerts:
                return
            self._shown_critical_alerts.add(alert_id)
            # 캐시 크기 cap (오래된 것 정리)
            if len(self._shown_critical_alerts) > 200:
                self._shown_critical_alerts = set(list(self._shown_critical_alerts)[-100:])

            box = QMessageBox(self)
            box.setIcon(QMessageBox.Critical)
            box.setWindowTitle(title)
            box.setText(body)
            if at_iso:
                box.setInformativeText(f"발생 시각: {at_iso[:19].replace('T', ' ')}\nID: {alert_id}")
            box.setStandardButtons(QMessageBox.Ok)
            # 중요: 메인 GUI 스레드에서 호출되므로 exec_() 로 모달 처리
            box.exec_()
            return

        # critical 외: 기존 토스트
        self.show_toast(severity, title, body)

    def _on_alert_conn_state(self, connected: bool) -> None:
        # AlertStream 연결 상태는 ws_status_label 우측에 작은 표시 (옵션)
        pass

    def _update_clock(self) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._clock_label.setText(now)

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _exit_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()

    def show_toast(self, level: str, title: str, message: str) -> None:
        """우상단 토스트 알림 (5초 자동 사라짐)."""
        toast = ToastNotification(self, level, title, message)
        toast.show()

    def _maybe_show_toast_for_alert(self, alert: dict[str, Any]) -> None:
        """critical/error 레벨 알림이면 토스트 표시 (중복 방지)."""
        level = _normalize_level(str(alert.get("level", "")))
        if level not in ("critical", "error"):
            return
        key = f"{alert.get('id', '')}-{alert.get('message', '')[:50]}"
        if key in self._seen_alerts:
            return
        self._seen_alerts.add(key)
        # 간단한 LRU: 최대 50개 유지
        if len(self._seen_alerts) > 50:
            self._seen_alerts.clear()
        self.show_toast(
            level=level,
            title=str(alert.get("source", "시스템")),
            message=str(alert.get("message", "")),
        )

    def _on_ws_state(self, connected: bool) -> None:
        if connected:
            self._ws_status_label.setText("WS: connected")
            self._ws_status_label.setStyleSheet(
                "color: #16a34a; font-weight: bold; padding: 0 10px;"
            )
        else:
            self._ws_status_label.setText("WS: disconnected")
            self._ws_status_label.setStyleSheet(
                "color: #9ca3af; padding: 0 10px;"
            )

    def _on_ws_message(self, payload: dict[str, Any]) -> None:
        # SPEC-AMR-001: handoff.ack 메시지는 페이지 무관 전역 처리 (토스트 + 상태바)
        if payload.get("type") == "handoff.ack":
            self._on_handoff_ack(payload)

        # 현재 보이는 페이지에만 전달 (보이지 않는 페이지가 HTTP 재조회로 메인 스레드 막는 것 방지).
        # 비가시 페이지의 데이터는 나중에 사용자가 해당 탭으로 이동할 때 타이머/초기 refresh 로 갱신됨.
        page = self._stack.currentWidget()
        if page is not None and hasattr(page, "handle_ws_message"):
            page.handle_ws_message(payload)

    def _on_handoff_ack(self, payload: dict[str, Any]) -> None:
        """후처리존 인수인계 ACK 이벤트 — 상태바 메시지 + 로그.

        SPEC-AMR-001 FR-AMR-01-06: WebSocket `handoff.ack` 수신 시 Factory
        Operator 에게 AMR 해제 사실을 즉시 알린다.
        """
        task_id = payload.get("task_id") or "-"
        amr_id = payload.get("amr_id") or "-"
        zone = payload.get("zone") or "postprocessing"
        orphan = bool(payload.get("orphan"))
        source = payload.get("source") or "unknown"

        if orphan:
            msg = f"⚠ handoff.ack (orphan) — zone={zone} source={source}"
        else:
            msg = f"✓ handoff.ack — {zone}: task={task_id} amr={amr_id} (source={source})"

        logger.info("WS handoff.ack: %s", msg)
        if hasattr(self, "statusBar"):
            self.statusBar().showMessage(msg, 8000)  # 8초 노출

    # ---------- MQTT ----------
    def _start_mqtt(self) -> None:
        if not mqtt_enabled():
            self._mqtt_status_label.setText("MQTT: disabled")
            return
        try:
            self._mqtt_worker = MqttWorker()
            self._mqtt_worker.connection_state.connect(self._on_mqtt_state)
            self._mqtt_worker.message_received.connect(self._on_mqtt_message)
            self._mqtt_thread = MqttThread(self._mqtt_worker)
            self._mqtt_thread.start()
            self._mqtt_status_label.setText("MQTT: connecting...")
        except Exception as exc:  # noqa: BLE001
            self._mqtt_status_label.setText(f"MQTT: error {exc}")

    def _on_mqtt_state(self, connected: bool) -> None:
        if connected:
            self._mqtt_status_label.setText("MQTT: connected")
            self._mqtt_status_label.setStyleSheet(
                "color: #16a34a; font-weight: bold; padding: 0 10px;"
            )
        else:
            self._mqtt_status_label.setText("MQTT: disconnected")
            self._mqtt_status_label.setStyleSheet(
                "color: #9ca3af; padding: 0 10px;"
            )

    def _on_mqtt_message(self, topic: str, payload: dict[str, Any]) -> None:
        # 모든 페이지에 전달 (현재는 Dashboard만 처리)
        for page in (
            self._dashboard,
            self._map,
            self._production,
            self._schedule,
            self._quality,
            self._logistics,
        ):
            if hasattr(page, "handle_mqtt_message"):
                page.handle_mqtt_message(topic, payload)

    # ---------- AMR 실시간 배터리 (gRPC → Management Service) ----------
    def _start_amr_status(self) -> None:
        try:
            from app.workers.amr_status_worker import (
                AmrStatusThread,
                AmrStatusWorker,
            )
        except ImportError:
            return
        self._amr_worker = AmrStatusWorker(poll_interval=AMR_POLL_INTERVAL)
        self._amr_worker.status_updated.connect(self._on_amr_status)
        self._amr_thread = AmrStatusThread(self._amr_worker)
        self._amr_thread.start()

    def _on_amr_status(self, amr_list: list) -> None:
        """AMR 실시간 데이터를 logistics 페이지에 직접 반영."""
        self._logistics.update_amr_live(amr_list)

    # ---------- 종료 ----------
    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        try:
            self._ws_worker.stop()
            self._ws_thread.quit()
            self._ws_thread.wait(2000)
        except Exception:  # noqa: BLE001
            pass
        if self._mqtt_thread is not None:
            try:
                self._mqtt_thread.shutdown()
            except Exception:  # noqa: BLE001
                pass
        if self._amr_thread is not None:
            try:
                self._amr_thread.shutdown()
            except Exception:  # noqa: BLE001
                pass
        super().closeEvent(event)
