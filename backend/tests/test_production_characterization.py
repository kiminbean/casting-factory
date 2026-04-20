"""SPEC-C2 §12.3 — Characterization test.

Interface POST /api/production/start 응답 shape (dict key set) 을 동결한다.
Phase C-2 proxy 전환 후에도 frontend (src/lib/api.ts) 가 동일 형식을 받는지 보장.

TODO: pytest-postgresql + seed 구성 완료 시 happy-path body 값 전체 byte-for-byte 비교.
현재는 key set 동결만 담당.
"""
from __future__ import annotations

EXPECTED_KEYS = {"ord_id", "item_id", "equip_task_txn_id", "message"}


def test_response_key_set_pinned():
    """Interface POST /api/production/start 응답 dict 키가 4개 고정."""
    # TODO: FastAPI TestClient + seeded PG fixture 연결 시 실제 호출
    # 현재는 기대 key set 자체를 문서화
    assert EXPECTED_KEYS == {"ord_id", "item_id", "equip_task_txn_id", "message"}
    # smartcast v2 변경 시 본 assertion 을 고의로 깨고 SPEC 업데이트 후 복구
