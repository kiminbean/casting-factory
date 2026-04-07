"""QMainWindow - 좌측 사이드바 + 우측 스택 레이아웃."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtWidgets import (
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
from app.pages.dashboard import DashboardPage
from app.pages.logistics import LogisticsPage
from app.pages.production import ProductionPage
from app.pages.quality import QualityPage
from app.ws_worker import WebSocketWorker
from config import APP_NAME, APP_VERSION, REFRESH_INTERVAL_MS


NAV_ITEMS: list[tuple[str, str]] = [
    ("dashboard", "대시보드"),
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
        self._build_ui()
        self._start_refresh_timer()
        self._start_websocket()

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
        self._production = ProductionPage(self._api)
        self._quality = QualityPage(self._api)
        self._logistics = LogisticsPage(self._api)

        for page in (self._dashboard, self._production, self._quality, self._logistics):
            self._stack.addWidget(page)

        root.addWidget(self._stack, stretch=1)

        # 상태바
        status = QStatusBar()
        self.setStatusBar(status)
        self._ws_status_label = QLabel("WS: disconnected")
        status.addPermanentWidget(self._ws_status_label)

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

    def _on_ws_state(self, connected: bool) -> None:
        text = "WS: connected" if connected else "WS: disconnected"
        self._ws_status_label.setText(text)

    def _on_ws_message(self, payload: dict[str, Any]) -> None:
        # 모든 페이지에 브로드캐스트 (각자 타입 필터링)
        for page in (
            self._dashboard,
            self._production,
            self._quality,
            self._logistics,
        ):
            if hasattr(page, "handle_ws_message"):
                page.handle_ws_message(payload)

    # ---------- 종료 ----------
    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        try:
            self._ws_worker.stop()
            self._ws_thread.quit()
            self._ws_thread.wait(2000)
        except Exception:  # noqa: BLE001
            pass
        super().closeEvent(event)
