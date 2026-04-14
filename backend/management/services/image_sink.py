"""Image Sink — Image Publisher → Management Service 수신 처리.

V6 정책 (2026-04-14):
- HW Image Publishing Service (Jetson) 가 본 endpoint 로 frame 스트림 publish
- 프로토콜: gRPC client streaming (proto: ImageFrame stream → ImageAck)
- ROS2 image transport 보다 가볍고, schema 가 명확

저장 정책 (Phase 5.2 단순 버전):
- 메모리 상 latest_frame[camera_id] dict 만 유지 (최신 1장)
- 디스크/Redis 저장은 추후 (예: S3, MinIO, /var/lib/casting/frames/)
- AI Service 가 본 모듈에서 latest 를 가져가 추론

@MX:NOTE: 동시 다중 카메라 streaming 지원 (gRPC ThreadPool 워커마다 독립 스트림).
@MX:WARN: 이미지가 큰 경우 메모리 누수 주의 — latest 1장만 보관, 이전 것 GC.
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ImageSink:
    """카메라별 최신 프레임을 메모리에 보관."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._latest: dict[str, dict] = {}
        # 카메라별 통계
        self._stats: dict[str, dict] = {}

    def push(self, camera_id: str, encoding: str, width: int, height: int,
             data: bytes, sequence: int, captured_at_iso: str) -> None:
        """클라이언트 streaming 한 프레임 1장 처리."""
        with self._lock:
            self._latest[camera_id] = {
                "encoding": encoding,
                "width": width,
                "height": height,
                "size": len(data),
                "sequence": sequence,
                "captured_at": captured_at_iso,
                "received_at": datetime.now(timezone.utc).isoformat(),
                "data": data,  # 실제 바이트 (AI Service 등에서 사용)
            }
            stats = self._stats.setdefault(camera_id, {"count": 0, "bytes": 0})
            stats["count"] += 1
            stats["bytes"] += len(data)

    def latest(self, camera_id: str) -> dict | None:
        with self._lock:
            return self._latest.get(camera_id)

    def stats(self) -> dict[str, dict]:
        with self._lock:
            return {k: dict(v) for k, v in self._stats.items()}


# 전역 싱글톤 (모든 servicer 가 공유)
sink = ImageSink()
