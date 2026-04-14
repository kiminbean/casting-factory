"""MQTT 어댑터 — ESP32 (HW Control Service) 전용.

V6 정책 (2026-04-14):
- ESP32 는 micro-ROS 부담 회피 위해 MQTT 사용
- 본 어댑터는 ROS2 와는 **별개 채널**. AMR/Cobot 통신은 절대 본 어댑터로 가지 않음.
- robot_id 가 'CONV-' / 'ESP-' 로 시작하는 경우만 라우팅됨

토픽 표준:
- 지령:    casting/esp/{robot_id}/cmd
- 상태:    casting/esp/{robot_id}/status   (ESP32 → Server, 본 어댑터는 publish-only)
- 이벤트: casting/esp/{robot_id}/event

기존 펌웨어 호환성:
- conveyor_controller(`firmware/conveyor_controller/MQTT_SETUP.md`) 의 토픽도 publish 가능 (별도 prefix 'conveyor/' 사용)
- 본 어댑터는 V6 표준 (`casting/esp/`) 우선, 펌웨어 호환 토픽은 옵션

@MX:NOTE: Image Publishing Service ↔ ESP32 직접 통신은 본 서버에 의존하지 않음 (HW 계층 내부).
@MX:WARN: paho-mqtt loop_start 는 백그라운드 스레드 사용 — close() 호출 필수.
"""
from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MQTT_HOST = os.environ.get("MGMT_MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MGMT_MQTT_PORT", "1883"))
MQTT_QOS = int(os.environ.get("MGMT_MQTT_QOS", "1"))
MQTT_CLIENT_ID = os.environ.get("MGMT_MQTT_CLIENT_ID", "casting-mgmt-esp")
# 펌웨어 레거시 토픽 호환 (firmware/conveyor_controller/)
MQTT_LEGACY_TOPIC = os.environ.get("MGMT_MQTT_LEGACY_CONVEYOR", "0") in ("1", "true", "yes")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MqttAdapter:
    """ESP32 (HW Control Service) 전용 MQTT publisher.

    AMR/Cobot 통신은 절대 본 어댑터로 가지 않는다 (ROS2 어댑터 사용).
    """

    name = "mqtt"

    def __init__(self) -> None:
        self._client = None  # type: ignore[var-annotated]
        self._lock = threading.Lock()
        self._connected = False
        self._connect()

    def _connect(self) -> None:
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            logger.warning("MqttAdapter: paho-mqtt 미설치 — publish 비활성화")
            return
        try:
            client = mqtt.Client(
                client_id=MQTT_CLIENT_ID,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            )
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
            client.loop_start()
            self._client = client
            self._connected = True
            logger.info("MqttAdapter (ESP32) connected → %s:%s", MQTT_HOST, MQTT_PORT)
        except Exception as exc:  # noqa: BLE001
            logger.warning("MqttAdapter 연결 실패: %s — dispatch 시 재시도", exc)
            self._client = None
            self._connected = False

    def _ensure_connected(self) -> bool:
        with self._lock:
            if self._connected and self._client is not None:
                return True
            self._connect()
            return self._connected

    @staticmethod
    def _topic(robot_id: str) -> str:
        """V6 표준 토픽. 레거시 호환이 필요하면 conveyor/{id}/cmd 도 publish."""
        return f"casting/esp/{robot_id}/cmd"

    def dispatch(self, item_id: int, robot_id: str, command: str,
                 payload: bytes) -> tuple[bool, str]:
        if not robot_id:
            return (False, "robot_id 비어있음")
        if not command:
            return (False, "command 비어있음")
        if not self._ensure_connected():
            return (False, f"mqtt_not_connected ({MQTT_HOST}:{MQTT_PORT})")

        msg = {
            "command": command,
            "item_id": item_id,
            "robot_id": robot_id,
            "issued_at": _now_iso(),
        }
        if payload:
            try:
                msg["payload"] = json.loads(payload.decode("utf-8"))
            except Exception:  # noqa: BLE001
                msg["payload_size"] = len(payload)

        body = json.dumps(msg, ensure_ascii=False).encode("utf-8")
        topic = self._topic(robot_id)
        try:
            assert self._client is not None
            info = self._client.publish(topic, body, qos=MQTT_QOS)
            if info.rc != 0:
                return (False, f"mqtt_publish_rc={info.rc}")

            # 레거시 conveyor 펌웨어 호환 (옵션)
            if MQTT_LEGACY_TOPIC and robot_id.upper().startswith("CONV-"):
                self._client.publish(f"conveyor/{robot_id}/cmd", body, qos=MQTT_QOS)

            logger.info("MqttAdapter publish %s: cmd=%s item=%s", topic, command, item_id)
            return (True, f"mqtt_published {topic} mid={info.mid}")
        except Exception as exc:  # noqa: BLE001
            self._connected = False
            logger.exception("MqttAdapter publish 예외: %s", exc)
            return (False, f"mqtt_error: {exc}")

    def close(self) -> None:
        with self._lock:
            if self._client is not None:
                try:
                    self._client.loop_stop()
                    self._client.disconnect()
                except Exception:  # noqa: BLE001
                    pass
                self._client = None
                self._connected = False
