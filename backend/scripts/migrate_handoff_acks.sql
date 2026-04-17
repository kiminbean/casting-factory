-- SPEC-AMR-001: 후처리존 인수인계 확인 이벤트 테이블 + transport_tasks 상태 확장
-- 실행: psql $DATABASE_URL -f backend/scripts/migrate_handoff_acks.sql
-- 2026-04-17, 멱등 실행 가능
--
-- 변경:
--   1. handoff_acks TimescaleDB hypertable 신규 (SR-AMR-02 감사 추적)
--   2. transport_tasks.status 에 'waiting_handoff_ack', 'handoff_complete' 값 추가
--      (String 컬럼이므로 enum ALTER 불필요, 애플리케이션 레이어에서 정의)
--
-- 참고: transport_tasks.id 가 String PK 이므로 handoff_acks.task_id 도 VARCHAR 로 정의

BEGIN;

-- 1. handoff_acks 테이블 생성 (멱등)
CREATE TABLE IF NOT EXISTS handoff_acks (
    id BIGSERIAL,
    task_id VARCHAR REFERENCES transport_tasks(id) ON DELETE SET NULL,
    zone TEXT NOT NULL,
    amr_id TEXT,
    ack_source TEXT NOT NULL,                   -- 'esp32_button' | 'debug_endpoint' | 'gui_override'(향후)
    operator_id TEXT,                           -- 향후 auth 연동용
    button_device_id TEXT,                      -- 'ESP-CONVEYOR-01'
    orphan_ack BOOLEAN NOT NULL DEFAULT FALSE,
    idempotency_key TEXT,                       -- '(source_device, event_ts_millis)' 해시
    metadata JSONB,
    ack_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, ack_at)                    -- hypertable 필수: 시간 컬럼 PK 포함
);

-- 2. TimescaleDB hypertable 변환 (이미 hypertable 이면 noop)
SELECT create_hypertable(
    'handoff_acks',
    'ack_at',
    if_not_exists => TRUE,
    migrate_data => TRUE
);

-- 3. 인덱스 (멱등)
CREATE INDEX IF NOT EXISTS idx_handoff_acks_zone_ack_at ON handoff_acks (zone, ack_at DESC);
CREATE INDEX IF NOT EXISTS idx_handoff_acks_task_id ON handoff_acks (task_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_handoff_acks_idempotency
    ON handoff_acks (idempotency_key, ack_at)
    WHERE idempotency_key IS NOT NULL;

-- 4. 압축 정책 (다른 hypertable 와 동일: 30일)
ALTER TABLE handoff_acks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'zone'
);

-- add_compression_policy 는 이미 있으면 오류 → 존재 확인 후 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.jobs
        WHERE hypertable_name = 'handoff_acks' AND proc_name = 'policy_compression'
    ) THEN
        PERFORM add_compression_policy('handoff_acks', INTERVAL '30 days');
    END IF;
END $$;

COMMIT;

-- 확인 쿼리 (수동 실행):
-- SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'handoff_acks';
-- SELECT indexname FROM pg_indexes WHERE tablename = 'handoff_acks';
