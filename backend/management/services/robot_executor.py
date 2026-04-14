"""Robot Executor — Management Service ↔ HW 계층 지령 송출.

이미지 V6 기준:
- Manufacturing / Stacking / Transport Service: 🟢 ROS2 DDS (nav2, MoveIt)
- HW Control Service (ESP32 컨베이어): 🔵 MQTT

따라서 이 모듈은 두 가지 백엔드를 동시에 지원한다.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RobotExecutor:
    """명령을 적절한 채널(ROS2 action / MQTT publish)로 송출.

    TODO:
    - ROS2 Python Client 초기화 (rclpy)
    - MQTT 클라이언트 (paho-mqtt) — conveyor/+/cmd 토픽
    - command 라우팅:
        navigate(pose)  → ROS2 NavigateToPose Action → AMR
        pick(item)      → ROS2 MoveIt Action         → Cobot
        place(slot)     → ROS2 MoveIt Action         → Cobot
        belt_speed(v)   → MQTT publish               → ESP32
    - ack/nack 처리, 실패 시 Execution Monitor 에 통지
    """

    def dispatch(
        self,
        item_id: int,
        robot_id: str,
        command: str,
        payload: bytes,
    ) -> tuple[bool, str]:
        logger.info(
            "Dispatch %s to %s: item=%s (%d bytes)",
            command, robot_id, item_id, len(payload),
        )
        # TODO: 실제 ROS2 / MQTT 송출
        return (False, "not_implemented")
