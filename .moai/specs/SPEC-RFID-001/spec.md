# SPEC-RFID-001: RFID 태그 스캔 수신 · 저장 · Item 바인딩

## Overview
HW Control Service(ESP32 + RC522) 가 주물 바닥 RFID 태그를 읽어 Vision Control Service(Jetson)
에게 Serial 로 전달하고, Jetson 은 이를 Management Service(gRPC :50051) 로 전송한다.
Management Service 는 수신한 페이로드(`order_{ord_id}_item_{YYYYMMDD}_{seq}`) 를 파싱하여
**`rfid_scan_log`** append-only 테이블에 저장하고, 기존 `item` 행과 바인딩한다.

본 SPEC 는 SPEC-AMR-001(handoff 체인) 과 병렬로 "RFID → Item 추적 체인" 을 완성한다.

## Requirements Source
- SR-RFID-01: HW 이벤트 수집 — ESP32/Jetson 에서 발생한 RFID 스캔을 유실 없이 서버에 저장
- SR-RFID-02: Item 추적 — 스캔된 태그가 어느 order/item 인지 파싱하여 연결
- SR-RFID-03: 이력 감사 — 모든 스캔 이벤트(정상·오스캔·미매칭) 를 시간 역순 조회 가능

## Tech Stack
- Firmware: ESP32 (RC522 via SPI) + conveyor_v5_serial 펌웨어
- Jetson: Python 3.12 Serial 브릿지 → gRPC client (`ReportRfidScan`)
- RPC Layer: gRPC (grpcio 1.59, protobuf) — 기존 `ManagementService` 서비스에 RPC 추가
- Persistence: PostgreSQL 16 + TimescaleDB (`100.107.120.14:5432/smartcast_robotics`)
  - 신규 테이블 `rfid_scan_log` (public schema — handoff_acks 와 같은 레벨)
- Parser: Python stdlib `re` — payload 정규식 매칭 (의존 없음)

## Functional Requirements

### FR-RFID-01: gRPC 수신 RPC
- EARS: When the Management Service receives a `ReportRfidScan(RfidScanEvent)` request,
  it SHALL respond within 500 ms with `RfidScanAck{accepted, item_id, parse_status}`.
- proto 메시지 스키마는 아래 **Data Contracts** 참조.
- 호출자: Jetson(기본) · 테스트 CLI · PyQt 시뮬레이터(선택)
- 실패 조건: `reader_id` 공란 → `INVALID_ARGUMENT`

### FR-RFID-02: Payload 파서
- EARS: When the service receives a payload, it SHALL attempt to parse it with the regex
  `^order_(?P<ord>\d+)_item_(?P<date>\d{8})_(?P<seq>\d+)$`.
- 성공 시 `parse_status = "ok"` + `ord_id`, `item_key` 추출
- 실패 시 `parse_status = "bad_format"` — DB 에 raw 저장만 (관측 목적)

### FR-RFID-03: Item 바인딩
- EARS: When parsing succeeds, the service SHALL look up `item` by
  `(ord_id, date, seq)` composite. If found, store `item_id` on the log row.
- 매칭 실패 시 `parse_status = "unknown_item"` (format 은 OK 였으나 DB 에 해당 item 이 없음)
- 본 SPEC 는 `item.rfid_tag` 컬럼 추가 는 보류(Scope 외). 바인딩은 `rfid_scan_log.item_id` 로만.

### FR-RFID-04: Idempotency
- EARS: When the same `idempotency_key` is received twice within 24 hours,
  the service SHALL return the original `RfidScanAck` without creating a new row.
- `idempotency_key` 은 Jetson 측에서 `{reader_id}:{scanned_at_millis}` 로 생성 권장.
- DB 레벨 UNIQUE INDEX 로 강제 (handoff_acks 동일 패턴).

### FR-RFID-05: 이력 저장 (append-only)
- EARS: The service SHALL insert every scan event (including parse failures) into
  `rfid_scan_log` before returning the ack.
- TimescaleDB 확장 존재 시 `create_hypertable('rfid_scan_log', 'scanned_at')` 적용.
- TimescaleDB 미설치 환경 fallback: 일반 테이블 + `(reader_id, scanned_at DESC)` 인덱스.

### FR-RFID-06: 조회 API (Scope 외 — 향후 확장)
- `WatchRfidScans` server streaming 또는 `ListRecentScans` unary 는 본 SPEC 범위 외.
- 현재는 PyQt 가 필요 시 DB 직결(또는 REST) 로 조회.

## Data Contracts

### proto 확장 (management.proto)
```proto
message RfidScanEvent {
  string    reader_id       = 1;   // 'ESP-CONV-01' 등
  string    zone            = 2;   // 'conveyor_in' | 'postprocessing' | ...
  string    raw_payload     = 3;   // 'order_1_item_20260417_1'
  Timestamp scanned_at      = 4;
  string    idempotency_key = 5;   // 'ESP-CONV-01:1713600000000' 권장
}

message RfidScanAck {
  bool   accepted    = 1;
  int64  item_id     = 2;   // 매칭된 item_id (0 = 미매칭)
  string parse_status = 3;  // 'ok' | 'bad_format' | 'unknown_item' | 'duplicate'
  string reason      = 4;   // human-readable (optional)
}

service ManagementService {
  // ... 기존 ...
  rpc ReportRfidScan(RfidScanEvent) returns (RfidScanAck);
}
```

### DB 스키마 (`rfid_scan_log`)
```sql
CREATE TABLE IF NOT EXISTS rfid_scan_log (
    id BIGSERIAL,
    scanned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reader_id TEXT NOT NULL,
    zone TEXT,
    raw_payload TEXT NOT NULL,
    ord_id TEXT,
    item_key TEXT,                   -- '20260417_1' (date_seq)
    item_id BIGINT,                  -- item 매칭 결과, NULL 가능
    parse_status TEXT NOT NULL,      -- 'ok' | 'bad_format' | 'unknown_item'
    idempotency_key TEXT,
    metadata JSONB,
    PRIMARY KEY (id, scanned_at)     -- hypertable 호환
);
CREATE INDEX ON rfid_scan_log (reader_id, scanned_at DESC);
CREATE INDEX ON rfid_scan_log (item_id, scanned_at DESC);
CREATE UNIQUE INDEX ON rfid_scan_log (idempotency_key) WHERE idempotency_key IS NOT NULL;
```

## Acceptance Criteria
1. `backend/scripts/migrate_rfid_scan_log.sql` 을 PG 에 적용하면 테이블/인덱스가 멱등 생성된다.
2. Management Service 가 재기동 후 `ReportRfidScan` RPC 를 응답한다 (Health 와 동급 smoke).
3. payload `order_1_item_20260417_1` 를 보내면 `parse_status='ok'` 또는 `'unknown_item'` 응답.
4. 동일 `idempotency_key` 재전송 시 `parse_status='duplicate'` 반환 + 중복 row 생성되지 않음.
5. `parse_status`, `reader_id`, `scanned_at`, `raw_payload` 가 모두 DB 에 저장된다 (append-only).
6. pytest smoke 최소 3건 (happy / bad_format / idempotency) 녹색.

## Out of Scope
- `item.rfid_tag` 컬럼 추가 및 UI 매핑 (후속 SPEC)
- Jetson 측 Serial → gRPC 브릿지 구현 (별도 repo)
- PyQt 에서 실시간 스캔 스트리밍 UI (`WatchRfidScans` stream)
- 오스캔/중복 태그 통계 대시보드

## Rollout Plan
1. SQL migration 적용 (`psql -f backend/scripts/migrate_rfid_scan_log.sql`)
2. proto 재생성 (`bash monitoring/scripts/gen_proto.sh` + backend 측)
3. Management Service 재기동 → Health + ReportRfidScan smoke
4. Jetson 브릿지는 본 SPEC 머지 후 별도 PR (브리지 repo)

---

Version: 1.0.0
Author: Inbean Kim
Created: 2026-04-20
Status: DRAFT
