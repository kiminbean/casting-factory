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
    QStackedWidget,
    QStatusBar,
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
from app.widgets.alert_widgets import ToastNotification, _normalize_level
from app.ws_worker import WebSocketWorker
from config import APP_NAME, APP_VERSION, REFRESH_INTERVAL_MS


NAV_ITEMS: list[tuple[str, str]] = [
    ("dashboard", "대시보드"),
    ("map", "공장 맵"),
    ("production", "생산 모니터링"),
    ("quality", "품질 검사"),
    ("logistics", "물류 / 이송"),
]


class MainWindow(QMainWindow):
    """모니터링 앱 메인 윈도우."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1400, 900)

        self._api = ApiClient()
        self._mqtt_worker: MqttWorker | None = None
        self._mqtt_thread: MqttThread | None = None

        self._build_ui()
        self._start_refresh_timer()
        self._start_websocket()
        self._start_mqtt()

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

        # 우측 스택
        self._stack = QStackedWidget()
        self._dashboard = DashboardPage(self._api)
        self._map = FactoryMapPage(self._api)
        self._production = ProductionPage(self._api)
        self._quality = QualityPage(self._api)
        self._logistics = LogisticsPage(self._api)

        for page in (
            self._dashboard,
            self._map,
            self._production,
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
        status.addPermanentWidget(self._ws_status_label)
        self._mqtt_status_label = QLabel("MQTT: disabled")
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

        # 페이지 단축키 Ctrl+1..5
        for i in range(5):
            action = QAction(f"Page {i + 1}", self)
            action.setShortcut(QKeySequence(f"Ctrl+{i + 1}"))
            action.triggered.connect(lambda _=False, idx=i: self._nav.setCurrentRow(idx))
            self.addAction(action)

        # 첫 페이지 선택
        self._nav.setCurrentRow(0)

    def _on_nav_changed(self, row: int) -> None:
        if 0 <= row < self._stack.count():
            self._stack.setCurrentIndex(row)

    # ---------- 주기 갱신 ----------
    def _start_refresh_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(REFRESH_INTERVAL_MS)
        self._timer.timeout.connect(self._refresh_current_page)
        self._timer.start()

    def _refresh_current_page(self) -> None:
        page = self._stack.currentWidget()
        if hasattr(page, "refresh"):
            page.refresh()

    # ---------- WebSocket ----------
    def _start_websocket(self) -> None:
        self._ws_thread = QThread()
        self._ws_worker = WebSocketWorker()
        self._ws_worker.moveToThread(self._ws_thread)
        self._ws_thread.started.connect(self._ws_worker.run)
        self._ws_worker.connection_state.connect(self._on_ws_state)
        self._ws_worker.message_received.connect(self._on_ws_message)
        self._ws_thread.start()

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
        text = "WS: connected" if connected else "WS: disconnected"
        self._ws_status_label.setText(text)

    def _on_ws_message(self, payload: dict[str, Any]) -> None:
        # 모든 페이지에 브로드캐스트 (각자 타입 필터링)
        for page in (
            self._dashboard,
            self._map,
            self._production,
            self._quality,
            self._logistics,
        ):
            if hasattr(page, "handle_ws_message"):
                page.handle_ws_message(payload)

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
        text = "MQTT: connected" if connected else "MQTT: disconnected"
        self._mqtt_status_label.setText(text)

    def _on_mqtt_message(self, topic: str, payload: dict[str, Any]) -> None:
        # 모든 페이지에 전달 (현재는 Dashboard만 처리)
        for page in (
            self._dashboard,
            self._map,
            self._production,
            self._quality,
            self._logistics,
        ):
            if hasattr(page, "handle_mqtt_message"):
                page.handle_mqtt_message(topic, payload)

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
        super().closeEvent(event)
