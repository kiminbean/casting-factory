"""SPEC-C2 §12.1 — TaskManager smartcast v2 단위 테스트.

pytest-postgresql ephemeral PG fixture 로 격리 실행. SQLite/in-memory 금지
(2026-04-14 policy).

TODO (Phase C-2 완료 조건 §13 DoD):
- pytest-postgresql 설치 + conftest.py 에 postgresql_proc fixture 구성
- smartcast schema 마이그레이션 스크립트 (backend/scripts/create_tables_v2.sql) 적용
- seed 함수: ord + pattern 1건 사전 주입

현재 상태: skeleton. 실제 PG fixture 연결은 후속 작업 (CI 워크플로우 신규).
"""
from __future__ import annotations

import pytest

from services.task_manager import StartProductionResult, TaskManager, TaskManagerError


@pytest.fixture
def task_manager() -> TaskManager:
    return TaskManager()


# ---------- 실패 경로 (PG 불필요) ----------

def test_start_production_single_zero_raises(task_manager):
    with pytest.raises(TaskManagerError, match="invalid ord_id"):
        task_manager.start_production_single(0)


def test_start_production_single_negative_raises(task_manager):
    with pytest.raises(TaskManagerError, match="invalid ord_id"):
        task_manager.start_production_single(-1)


def test_start_production_batch_empty_iter(task_manager):
    assert task_manager.start_production_batch([]) == []


def test_start_production_batch_all_invalid_skipped(task_manager):
    # "abc", "" 모두 int 변환 실패 → skip → 빈 리스트
    assert task_manager.start_production_batch(["abc", ""]) == []


# ---------- 해피 경로 (PG 필요 · skip when fixture unavailable) ----------

@pytest.mark.skip(reason="pytest-postgresql fixture 설정 대기 (CI 워크플로우 신규)")
def test_start_production_single_happy(task_manager, postgresql_with_smartcast_seed):
    """정상 흐름: Ord+Pattern 등록 후 task_manager 호출 → OrdStat/Item/EquipTaskTxn 3건 INSERT."""
    ord_id = 42
    result = task_manager.start_production_single(ord_id)
    assert isinstance(result, StartProductionResult)
    assert result.ord_id == ord_id
    assert result.item_id > 0
    assert result.equip_task_txn_id > 0
    assert "RA1/MM" in result.message


@pytest.mark.skip(reason="pytest-postgresql fixture 설정 대기")
def test_start_production_single_ord_not_found(task_manager, postgresql_smartcast_empty):
    with pytest.raises(TaskManagerError, match="not found"):
        task_manager.start_production_single(999999)


@pytest.mark.skip(reason="pytest-postgresql fixture 설정 대기")
def test_start_production_single_pattern_missing(task_manager, postgresql_ord_without_pattern):
    with pytest.raises(TaskManagerError, match="pattern for ord_id=.* not registered"):
        task_manager.start_production_single(100)
