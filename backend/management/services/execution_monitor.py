"""Execution Monitor — Item 상태 변경을 감지해 gRPC 스트림으로 송출.

V6 아키텍처 Phase 3 산출물.

전략:
- 1초 간격 DB 스냅샷 대조 (in-memory cache vs 현재 cur_stage)
- 변경된 item 만 ItemEvent 로 yield
- 신규 추가된 item (cache 에 없던 id) 도 이벤트로 emit (stage=현재값)
- 현재 사용 가능한 인덱스만 사용 (items.id, items.order_id) — order_id 컬럼 인덱스 존재

추후 LISTEN/NOTIFY 또는 Debezium 등으로 교체 가능.

@MX:NOTE: 다중 클라이언트 동시 구독 시 현재는 각 연결마다 독립 polling.
        클라이언트 100+ 명 단계가 오면 server-side 단일 polling + pub/sub 으로 리팩토링.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import select

from app.models.models import Item
from db_session import SessionLocal

import management_pb2  # type: ignore  # backend/management/ 가 sys.path 에 들어있음

logger = logging.getLogger(__name__)


# proto enum 매핑 (string → int)
_STAGE_TO_ENUM = {
    "QUE": 1, "MM": 2, "DM": 3, "TR_PP": 4,
    "PP": 5, "IP": 6, "TR_LD": 7, "SH": 8,
}


def _stage_enum(stage: str | None) -> int:
    return _STAGE_TO_ENUM.get(stage or "QUE", 0)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExecutionMonitor:
    """진행 중 Item 상태를 감시하고 gRPC 클라이언트에 ItemEvent 를 푸시.

    poll_interval_sec 마다 DB 를 읽고, 직전 스냅샷과 다른 item 만 이벤트 송출.
    클라이언트 연결 종료 시 generator 를 그냥 끝내면 server.py 가 정리한다.
    """

    def __init__(self, poll_interval_sec: float = 1.0) -> None:
        self._interval = poll_interval_sec

    def stream(self, order_filter: str | None) -> Iterator:
        """gRPC server streaming 본체. proto ItemEvent 를 무한히 yield.

        클라이언트가 연결을 끊으면 다음 yield 시점에 BrokenPipe 발생 →
        server.py 의 context.is_active() 체크에서 break 처리됨.
        """
        snapshot: dict[int, str] = {}  # item_id → cur_stage 직전 스냅샷
        first_pass = True

        while True:
            try:
                changes, snapshot = self._diff_snapshot(snapshot, order_filter, first_pass)
                first_pass = False
                for item_id, stage, robot in changes:
                    yield management_pb2.ItemEvent(
                        item_id=item_id,
                        stage=_stage_enum(stage),
                        robot_id=robot or "",
                        message="",
                        at=management_pb2.Timestamp(iso8601=_now_iso()),
                    )
            except Exception as exc:  # noqa: BLE001
                logger.exception("ExecutionMonitor.stream poll error: %s", exc)
                # 일시 오류 시 재시도. 영구 문제(예: DB 다운)는 다음 polling 시 또 잡힘.

            time.sleep(self._interval)

    def _diff_snapshot(
        self,
        prev: dict[int, str],
        order_filter: str | None,
        first_pass: bool,
    ) -> tuple[list[tuple[int, str, str | None]], dict[int, str]]:
        """현재 DB 상태를 가져와 prev 와 대조, 변경분 + 새 스냅샷을 돌려준다.

        first_pass=True 인 경우 모든 현재 item 을 이벤트로 emit (구독 직후 초기 상태 sync).
        그 이후는 stage 가 바뀐 item 만 emit.
        """
        changes: list[tuple[int, str, str | None]] = []
        new_snapshot: dict[int, str] = {}

        with SessionLocal() as db:
            stmt = select(Item.id, Item.cur_stage, Item.curr_res)
            if order_filter:
                stmt = stmt.where(Item.order_id == order_filter)
            for row in db.execute(stmt).all():
                item_id, stage, robot = int(row[0]), str(row[1] or "QUE"), row[2]
                new_snapshot[item_id] = stage
                if first_pass:
                    changes.append((item_id, stage, robot))
                    continue
                old = prev.get(item_id)
                if old != stage:
                    changes.append((item_id, stage, robot))

        return changes, new_snapshot
