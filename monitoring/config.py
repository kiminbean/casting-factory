"""Monitoring 앱 전역 설정.

환경변수 기반 오버라이드 지원:
    CASTING_API_HOST - FastAPI 서버 IP (기본: 192.168.0.16)
    CASTING_API_PORT - FastAPI 포트 (기본: 8000)
    CASTING_MQTT_HOST - MQTT 브로커 IP (기본: 192.168.0.16)
    CASTING_MQTT_PORT - MQTT 포트 (기본: 1883)
"""
from __future__ import annotations

import os


API_HOST: str = os.environ.get("CASTING_API_HOST", "192.168.0.16")
API_PORT: int = int(os.environ.get("CASTING_API_PORT", "8000"))
API_BASE_URL: str = f"http://{API_HOST}:{API_PORT}"
WS_URL: str = f"ws://{API_HOST}:{API_PORT}/ws/dashboard"

MQTT_HOST: str = os.environ.get("CASTING_MQTT_HOST", "192.168.0.16")
MQTT_PORT: int = int(os.environ.get("CASTING_MQTT_PORT", "1883"))
MQTT_TOPICS: tuple[str, ...] = (
    "conveyor/+/status",
    "conveyor/+/event",
    "vision/+/result",
    "cobot/+/status",
    "amr/+/position",
    "factory/alarm",
)

APP_NAME: str = "주물공장 모니터링"
APP_VERSION: str = "1.0.0"

REFRESH_INTERVAL_MS: int = 3000
