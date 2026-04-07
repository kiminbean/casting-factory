"""MQTT 구독 워커 (QThread 기반).

paho-mqtt 를 사용해 공장 내 장비(ESP32 컨베이어, Jetson Vision, Cobot, AMR)의
실시간 상태를 구독하고 Qt signal 로 UI 스레드에 전달.

토픽 네임스페이스 (firmware/conveyor_controller/MQTT_SETUP.md 참조):
  conveyor/+/status     - ESP32 상태 JSON (300ms)
  conveyor/+/event      - entry / exit / cycle_done
  conveyor/+/heartbeat  - online / offline (retained)
  vision/+/result       - 검사 결과 ok/ng
  cobot/+/status        - Cobot 상태
  amr/+/position        - AMR 위치
  factory/alarm         - 전체 알람

환경 변수:
  CASTING_MQTT_ENABLED  - "1" 이면 활성화 (기본: 비활성화)
  CASTING_MQTT_HOST     - 브로커 호스트 (기본: 192.168.0.16)
  CASTING_MQTT_PORT     - 브로커 포트 (기본: 1883)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from config import MQTT_HOST, MQTT_PORT, MQTT_TOPICS

try:
    import paho.mqtt.client as mqtt  # type: ignore[import-not-found]
    _HAS_PAHO = True
except Exception:  # noqa: BLE001
    _HAS_PAHO = False


logger = logging.getLogger(__name__)


def mqtt_enabled() -> bool:
    """환경 변수로 MQTT 활성화 여부 판단."""
    return os.environ.get("CASTING_MQTT_ENABLED", "0") in ("1", "true", "yes")


class MqttWorker(QObject):
    """MQTT 구독 워커.

    Signals:
        connection_state(bool): True = connected
        message_received(str topic, dict payload)
    """

    connection_state = pyqtSignal(bool)
    message_received = pyqtSignal(str, dict)

    def __init__(
        self,
        host: str = MQTT_HOST,
        port: int = MQTT_PORT,
        client_id: str = "monitoring_client",
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._client_id = client_id
        self._client: Any = None
        self._running = False

    def start(self) -> None:
        if not _HAS_PAHO:
            logger.warning("paho-mqtt not installed, MQTT disabled")
            return

        self._running = True
        self._client = mqtt.Client(
            client_id=self._client_id,
            clean_session=True,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,  # type: ignore[attr-defined]
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        try:
            logger.info("Connecting to MQTT broker %s:%s", self._host, self._port)
            self._client.connect_async(self._host, self._port, keepalive=30)
            self._client.loop_start()
        except Exception as exc:  # noqa: BLE001
            logger.error("MQTT connect_async failed: %s", exc)
            self.connection_state.emit(False)

    def stop(self) -> None:
        self._running = False
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:  # noqa: BLE001
                pass

    # --- callbacks ---
    def _on_connect(self, client, userdata, flags, rc, properties=None) -> None:  # noqa: ARG002
        if rc == 0:
            logger.info("MQTT connected to %s:%s", self._host, self._port)
            self.connection_state.emit(True)
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                logger.info("  subscribed: %s", topic)
        else:
            logger.warning("MQTT connect failed rc=%s", rc)
            self.connection_state.emit(False)

    def _on_disconnect(self, client, userdata, flags, rc=None, properties=None) -> None:  # noqa: ARG002
        logger.info("MQTT disconnected rc=%s", rc)
        self.connection_state.emit(False)

    def _on_message(self, client, userdata, msg) -> None:  # noqa: ARG002
        topic = str(msg.topic)
        try:
            text = msg.payload.decode("utf-8", errors="replace").strip()
        except Exception:  # noqa: BLE001
            return

        # 단순 텍스트 (heartbeat 등) 도 dict 로 감싸서 전달
        if text.startswith("{") and text.endswith("}"):
            try:
                payload = json.loads(text)
                if not isinstance(payload, dict):
                    payload = {"value": payload}
            except json.JSONDecodeError:
                payload = {"raw": text}
        else:
            payload = {"value": text}

        self.message_received.emit(topic, payload)


class MqttThread(QThread):
    """MqttWorker 를 감싼 QThread - UI 스레드와 분리 실행."""

    def __init__(self, worker: MqttWorker) -> None:
        super().__init__()
        self._worker = worker
        self._worker.moveToThread(self)

    def run(self) -> None:
        self._worker.start()
        self.exec_()

    def shutdown(self) -> None:
        self._worker.stop()
        self.quit()
        self.wait(2000)


__all__ = ["MqttWorker", "MqttThread", "mqtt_enabled"]
