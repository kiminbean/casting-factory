"""Traffic Manager — AMR 경로 계획 + 충돌 회피.

설계 근거: docs/fleet_traffic_management.html (Waypoint/Edge + Backtrack Yield).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RoutePlan:
    points: list  # list of proto RoutePoint
    reserved_edges: list[str] = field(default_factory=list)
    duration_sec: float = 0.0


class TrafficManager:
    """1m x 2m 맵 + 0.12m AMR 3대 용 Waypoint-Edge 경로 플래너.

    TODO:
    - Waypoint 그래프 로딩 (YAML or DB)
    - Dijkstra 최단 경로
    - Edge 예약 테이블 (시간 창 단위)
    - Backtrack Yield: 교차 충돌 시 낮은 priority_rank 가 양보
    """

    def plan(self, robot_id: str, start: tuple[float, float],
             goal: tuple[float, float]) -> RoutePlan:
        raise NotImplementedError("TrafficManager.plan: 미구현")
