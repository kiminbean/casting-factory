"""ROS2 어댑터 — Manufacturing / Stacking / Transport Service 지령.

V6 정책 (2026-04-14):
- Server ↔ HW(RPi5/RPi4) 의 정식 채널은 ROS2 DDS
- 개발/배포 모두 Ubuntu 24.04 + ROS2 Jazzy 환경

활성화 방법:
1. `sudo apt install ros-jazzy-rclpy ros-jazzy-geometry-msgs ros-jazzy-nav2-msgs`
2. management Python venv 에 시스템 site-packages 사용 또는 source workspace
3. `MGMT_ROS2_ENABLED=1` 환경변수 설정

토픽/액션 표준:
- AMR (Transport):       Action /{robot_id}/navigate_to_pose  (nav2_msgs/NavigateToPose)
- ARM (Manufacturing/Stacking): Action /{robot_id}/move_to    (custom MoveTo Action)
- 추후 RPi 측 노드에서 .action 정의 후 동기화

@MX:WARN: import rclpy 는 lazy. 모듈 로드 시점 충돌 회피.
"""
from __future__ import annotations

import logging
import os
import threading
from typing import Any

logger = logging.getLogger(__name__)

ROS2_ENABLED = os.environ.get("MGMT_ROS2_ENABLED", "0") in ("1", "true", "yes")


class Ros2Adapter:
    """ROS2 publisher/action 어댑터.

    MGMT_ROS2_ENABLED=1 설정 시 rclpy 를 init 하고 DDS 통신 활성화.
    """

    name = "ros2"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rclpy = None  # type: ignore[var-annotated]
        self._node: Any = None
        self._publishers: dict[str, Any] = {}  # topic → Publisher

        if ROS2_ENABLED:
            self._init_rclpy()
        else:
            logger.info(
                "Ros2Adapter: MGMT_ROS2_ENABLED 미설정 — RPi 배포 환경에서만 활성화."
            )

    def _init_rclpy(self) -> None:
        try:
            import rclpy  # type: ignore[import-not-found]
            from rclpy.node import Node  # type: ignore[import-not-found]
            rclpy.init(args=None)
            self._rclpy = rclpy
            self._node = Node("casting_management_executor")
            logger.info("Ros2Adapter: rclpy 초기화 완료 (node=casting_management_executor)")
        except Exception as exc:  # noqa: BLE001
            logger.error("Ros2Adapter: rclpy 초기화 실패: %s", exc)
            self._rclpy = None

    def dispatch(self, item_id: int, robot_id: str, command: str,
                 payload: bytes) -> tuple[bool, str]:
        """ROS2 토픽/액션으로 지령 송출."""
        if not ROS2_ENABLED or self._rclpy is None or self._node is None:
            return (
                False,
                "ros2_not_available: MGMT_ROS2_ENABLED=1 + rclpy 환경 필요 "
                "(Ubuntu 24.04 + ROS2 Jazzy).",
            )

        # 실제 publish/action 로직 (RPi 배포 시 채움)
        # TODO: command 별 라우팅
        #   navigate → action client NavigateToPose
        #   pick/place → action client MoveTo
        #   start/stop → topic publisher std_msgs/Bool
        topic = f"/{robot_id}/cmd"
        try:
            from std_msgs.msg import String  # type: ignore[import-not-found]
            with self._lock:
                pub = self._publishers.get(topic)
                if pub is None:
                    pub = self._node.create_publisher(String, topic, 10)
                    self._publishers[topic] = pub
            msg = String()
            msg.data = payload.decode("utf-8", errors="replace") if payload else command
            pub.publish(msg)
            logger.info("Ros2Adapter publish %s: cmd=%s item=%s", topic, command, item_id)
            return (True, f"ros2_published {topic}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ros2Adapter dispatch 예외: %s", exc)
            return (False, f"ros2_error: {exc}")

    def close(self) -> None:
        if self._node is not None:
            try:
                self._node.destroy_node()
            except Exception:  # noqa: BLE001
                pass
        if self._rclpy is not None:
            try:
                self._rclpy.shutdown()
            except Exception:  # noqa: BLE001
                pass
        self._node = None
        self._rclpy = None
