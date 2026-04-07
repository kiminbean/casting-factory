"""FastAPI WebSocket 실시간 수신 worker (QThread).

/ws/dashboard 에 연결해서 broadcast 메시지를 Qt signal 로 UI 스레드에 전달.
"""
from __future__ import annotations

import json
import logging

from PyQt5.QtCore import QObject, QThread, pyqtSignal
import websocket  # websocket-client

from config import WS_URL

logger = logging.getLogger(__name__)


class WebSocketWorker(QObject):
    """WebSocket 메시지를 수신해서 Qt signal 로 방출."""

    message_received = pyqtSignal(dict)
    connection_state = pyqtSignal(bool)  # True = connected

    def __init__(self, url: str = WS_URL) -> None:
        super().__init__()
        self._url = url
        self._ws: websocket.WebSocketApp | None = None
        self._running = False

    def run(self) -> None:
        self._running = True
        while self._running:
            try:
                self._ws = websocket.WebSocketApp(
                    self._url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self._ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as exc:  # noqa: BLE001 - want to log anything
                logger.error("WebSocket loop error: %s", exc)
            if self._running:
                # 재연결 대기
                QThread.sleep(3)

    def stop(self) -> None:
        self._running = False
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:  # noqa: BLE001
                pass

    # --- callbacks ---
    def _on_open(self, ws: websocket.WebSocketApp) -> None:  # noqa: ARG002
        logger.info("WebSocket connected: %s", self._url)
        self.connection_state.emit(True)

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:  # noqa: ARG002
        try:
            payload = json.loads(message)
            if isinstance(payload, dict):
                self.message_received.emit(payload)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON payload: %s", message[:120])

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:  # noqa: ARG002
        logger.error("WebSocket error: %s", error)

    def _on_close(
        self,
        ws: websocket.WebSocketApp,  # noqa: ARG002
        status_code: int | None,
        msg: str | None,
    ) -> None:
        logger.info("WebSocket closed: %s %s", status_code, msg)
        self.connection_state.emit(False)
