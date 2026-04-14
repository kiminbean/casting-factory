"""adapters.select_adapter() prefix 라우터 단위 테스트.

V6 통신 행렬 준수 검증:
- AMR-* / ARM-* → ros2 어댑터
- CONV-* / ESP-* → mqtt 어댑터
- 그 외 → unknown
"""
import pytest

from services.adapters import select_adapter


@pytest.mark.parametrize("robot_id, expected", [
    # ROS2 (AMR/Cobot)
    ("AMR-001", "ros2"),
    ("AMR-002", "ros2"),
    ("amr-001", "ros2"),  # case insensitive
    ("ARM-001", "ros2"),
    ("ARM-LEFT", "ros2"),
    # MQTT (ESP32)
    ("CONV-001", "mqtt"),
    ("CONV-CONVEYOR-MAIN", "mqtt"),
    ("ESP-001", "mqtt"),
    ("esp-002", "mqtt"),
    # Unknown
    ("ROBOT-001", "unknown"),
    ("UNKNOWN-X", "unknown"),
    ("CAMERA-01", "unknown"),
    ("", "unknown"),
])
def test_select_adapter_routing(robot_id, expected):
    assert select_adapter(robot_id) == expected


def test_v6_communication_matrix_no_overlap():
    """ROS2 와 MQTT 채널이 동일 robot_id 로 겹치지 않음 검증."""
    samples = ["AMR-001", "ARM-001", "CONV-001", "ESP-001"]
    routes = {select_adapter(r) for r in samples}
    # 정확히 2개 채널만 사용
    assert routes == {"ros2", "mqtt"}
