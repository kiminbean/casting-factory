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

REFRESH_INTERVAL_MS: int = 8000

# AMR SSH 설정 (Pinky Pro, Tailscale)
# 형식: [(id, host, user, password, port), …]
AMR_TARGETS: list[tuple[str, str, str, str, int]] = [
    (
        os.environ.get("AMR_1_ID", "AMR-001"),
        os.environ.get("AMR_1_HOST", "100.115.21.107"),
        os.environ.get("AMR_1_USER", "pinky"),
        os.environ.get("AMR_1_PASS", "1"),
        int(os.environ.get("AMR_1_PORT", "22")),
    ),
    (
        os.environ.get("AMR_2_ID", "AMR-002"),
        os.environ.get("AMR_2_HOST", "100.100.103.96"),
        os.environ.get("AMR_2_USER", "pinky"),
        os.environ.get("AMR_2_PASS", "1"),
        int(os.environ.get("AMR_2_PORT", "22")),
    ),
    (
        os.environ.get("AMR_3_ID", "AMR-003"),
        os.environ.get("AMR_3_HOST", "100.87.221.81"),
        os.environ.get("AMR_3_USER", "pinky"),
        os.environ.get("AMR_3_PASS", "1"),
        int(os.environ.get("AMR_3_PORT", "22")),
    ),
]
AMR_POLL_INTERVAL: float = float(os.environ.get("AMR_POLL_INTERVAL", "10"))
