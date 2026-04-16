"""AMR Transport State Machine — 운송 작업 상태 추적.

10개 상태를 event-driven 으로 전이:
  IDLE → MOVE_TO_SOURCE → AT_SOURCE → LOADING → LOAD_COMPLETED
       → MOVE_TO_DEST → AT_DESTINATION → UNLOADING → UNLOAD_COMPLETED → IDLE
  임의 상태 → FAILED (에러/타임아웃)
  FAILED → IDLE (리셋)

In-memory 저장. 서버 재시작 시 모든 AMR 은 IDLE 로 초기화.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import IntEnum

logger = logging.getLogger(__name__)


class TaskState(IntEnum):
    """Proto AmrTaskState enum 과 1:1 매핑."""
    UNSPECIFIED      = 0
    IDLE             = 1
    MOVE_TO_SOURCE   = 2
    AT_SOURCE        = 3
    LOADING          = 4
    LOAD_COMPLETED   = 5
    MOVE_TO_DEST     = 6
    AT_DESTINATION   = 7
    UNLOADING        = 8
    UNLOAD_COMPLETED = 9
    FAILED           = 10


# display label (한국어)
TASK_STATE_LABELS: dict[TaskState, str] = {
    TaskState.UNSPECIFIED:      "-",
    TaskState.IDLE:             "대기",
    TaskState.MOVE_TO_SOURCE:   "출발지 이동",
    TaskState.AT_SOURCE:        "출발지 도착",
    TaskState.LOADING:          "상차",
    TaskState.LOAD_COMPLETED:   "상차 완료",
    TaskState.MOVE_TO_DEST:     "도착지 이동",
    TaskState.AT_DESTINATION:   "도착지 도착",
    TaskState.UNLOADING:        "하차중",
    TaskState.UNLOAD_COMPLETED: "하차 완료",
    TaskState.FAILED:           "실패",
}


# valid transitions: current_state → set of allowed next states
_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.IDLE:             {TaskState.MOVE_TO_SOURCE, TaskState.FAILED},
    TaskState.MOVE_TO_SOURCE:   {TaskState.AT_SOURCE, TaskState.FAILED},
    TaskState.AT_SOURCE:        {TaskState.LOADING, TaskState.FAILED},
    TaskState.LOADING:          {TaskState.LOAD_COMPLETED, TaskState.FAILED},
    TaskState.LOAD_COMPLETED:   {TaskState.MOVE_TO_DEST, TaskState.FAILED},
    TaskState.MOVE_TO_DEST:     {TaskState.AT_DESTINATION, TaskState.FAILED},
    TaskState.AT_DESTINATION:   {TaskState.UNLOADING, TaskState.FAILED},
    TaskState.UNLOADING:        {TaskState.UNLOAD_COMPLETED, TaskState.FAILED},
    TaskState.UNLOAD_COMPLETED: {TaskState.IDLE, TaskState.FAILED},
    TaskState.FAILED:           {TaskState.IDLE},
}


@dataclass
class AmrContext:
    """AMR 한 대의 운송 상태 컨텍스트."""
    state: TaskState = TaskState.IDLE
    task_id: str = ""
    loaded_item: str = ""
    updated_at: float = field(default_factory=time.monotonic)


class AmrStateMachine:
    """AMR fleet 전체의 상태 머신. Thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._robots: dict[str, AmrContext] = {}

    def register(self, robot_id: str) -> None:
        """AMR 등록. 이미 등록된 경우 무시."""
        with self._lock:
            if robot_id not in self._robots:
                self._robots[robot_id] = AmrContext()
                logger.info("AmrStateMachine: %s 등록 (IDLE)", robot_id)

    def get(self, robot_id: str) -> AmrContext:
        """현재 상태 조회. 미등록 시 기본 IDLE 반환."""
        with self._lock:
            return self._robots.get(robot_id, AmrContext())

    def get_all(self) -> dict[str, AmrContext]:
        """전체 AMR 상태 스냅샷."""
        with self._lock:
            return dict(self._robots)

    def transition(
        self,
        robot_id: str,
        new_state: TaskState,
        task_id: str | None = None,
        loaded_item: str | None = None,
    ) -> bool:
        """상태 전이 시도. 유효하면 True, 무효하면 False."""
        with self._lock:
            ctx = self._robots.get(robot_id)
            if ctx is None:
                ctx = AmrContext()
                self._robots[robot_id] = ctx

            allowed = _TRANSITIONS.get(ctx.state, set())
            if new_state not in allowed:
                logger.warning(
                    "AmrStateMachine: %s 무효 전이 %s → %s (허용: %s)",
                    robot_id, ctx.state.name, new_state.name,
                    [s.name for s in allowed],
                )
                return False

            old = ctx.state.name
            ctx.state = new_state
            ctx.updated_at = time.monotonic()

            if task_id is not None:
                ctx.task_id = task_id
            if loaded_item is not None:
                ctx.loaded_item = loaded_item

            # IDLE 복귀 시 작업 정보 초기화
            if new_state == TaskState.IDLE:
                ctx.task_id = ""
                ctx.loaded_item = ""

            logger.info(
                "AmrStateMachine: %s %s → %s (task=%s, item=%s)",
                robot_id, old, new_state.name, ctx.task_id, ctx.loaded_item,
            )
            return True

    def force_reset(self, robot_id: str) -> None:
        """강제 IDLE 리셋 (비상 정지 등)."""
        with self._lock:
            ctx = self._robots.get(robot_id)
            if ctx is not None:
                old = ctx.state.name
                ctx.state = TaskState.IDLE
                ctx.task_id = ""
                ctx.loaded_item = ""
                ctx.updated_at = time.monotonic()
                logger.warning("AmrStateMachine: %s 강제 리셋 %s → IDLE", robot_id, old)
