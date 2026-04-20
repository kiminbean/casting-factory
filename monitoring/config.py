"""Monitoring 앱 전역 설정.

V6 canonical 아키텍처 (2026-04-20 Phase D):
    PyQt(Monitoring Service) → Management Service (TCP/gRPC :50051)
    MQTT 직접 구독 경로는 Phase D 에서 제거됨. 컨베이어/비전 상태는 Management 스트림으로 수신.

환경변수 기반 오버라이드:
    CASTING_API_HOST - FastAPI 서버 IP (기본: 192.168.0.16)   ← api_client.py 레거시용 (Phase A-2 에서 제거)
    CASTING_API_PORT - FastAPI 포트 (기본: 8000)              ← 동일
"""
from __future__ import annotations

import os


# NOTE: V6 canonical 아키텍처상 PyQt(Monitoring Service) 는 Management Service 에만 TCP(gRPC)로 연결된다.
# API_HOST / API_PORT / API_BASE_URL 은 아직 api_client.py 가 7개 페이지의 legacy 조회에 사용하므로 잠정 유지.
# Phase A-2 (Interface proxy 도입 후) 에서 전체 제거 예정.
API_HOST: str = os.environ.get("CASTING_API_HOST", "192.168.0.16")
API_PORT: int = int(os.environ.get("CASTING_API_PORT", "8000"))
API_BASE_URL: str = f"http://{API_HOST}:{API_PORT}"

APP_NAME: str = "주물공장 모니터링"
APP_VERSION: str = "1.0.0"

REFRESH_INTERVAL_MS: int = 8000

# AMR 상태 폴링 간격 (PyQt → gRPC → Management Service)
# SSH 접속 설정은 backend/.env.local 의 MGMT_AMR_*_HOST 참조
AMR_POLL_INTERVAL: float = float(os.environ.get("AMR_POLL_INTERVAL", "10"))
