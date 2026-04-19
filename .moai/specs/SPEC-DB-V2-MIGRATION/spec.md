---
id: SPEC-DB-V2-MIGRATION
version: 0.1.0
status: implemented
created: 2026-04-19
updated: 2026-04-19
author: kisoo
priority: high
---

# SPEC-DB-V2-MIGRATION: smartcast schema 정착 + legacy 호환 레이어

## HISTORY

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | 2026-04-19 | kisoo | 최초 — Confluence 32342045 v59 기반 신규 schema 적용 + legacy compat 어댑터 |

## Overview

이다예 owner Confluence 페이지 [DB Schema and ERD v59 (32342045)](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32342045) (2026-04-18) 의 신규 ERD 를 코드베이스 전반에 정착. 기존 legacy schema (orders/items/equipment/alerts 등 21 테이블) 는 smartcast schema 의 신규 27 테이블로 대체되며, 레거시 코드와의 호환을 위한 어댑터 레이어를 추가한다.

## Requirements Source

- Confluence 32342045 v59 — 27 테이블 DDL + DBML + 인라인 코멘트 8건
- 팀장 지시 (2026-04-19) — "테이블 만들어서 넣어주세요" + 핑크 GUI 6건
- 메모리 `feedback_db_postgresql_only` — PG 단독 정책 유지

## Functional Requirements

### REQ-DBV2-001 (ubiquitous) — schema 격리

The system SHALL isolate the new 27 tables under a dedicated PostgreSQL schema `smartcast` while preserving the legacy `public` schema intact.

- 선택 근거: `team2` role 이 `CREATEDB` 권한 부재 → 별도 DB 대신 schema 격리로 대응
- 모든 SQLAlchemy 모델은 `__table_args__ = {"schema": "smartcast"}` 지정
- `DATABASE_URL` 에 `?options=-csearch_path%3Dsmartcast,public` 추가로 자동 경로 해석

### REQ-DBV2-002 (event-driven) — 27 테이블 DDL

WHEN `backend/scripts/create_tables_v2.sql` 을 psql 로 실행하면, the system SHALL create 27 tables + `equip_load_spec` (선택) under `smartcast` schema with correct constraints and references.

- 포함: user_account / ord + ord_detail + ord_pp_map + ord_txn + ord_stat + ord_log
- 포함: category / product / product_option / pp_options / pattern / zone
- 포함: res / equip / equip_load_spec / trans / item
- 포함: chg_location_stat / strg_location_stat / ship_location_stat
- 포함: pp_task_txn / equip_task_txn / equip_stat / equip_err_log
- 포함: trans_task_txn / trans_stat / trans_err_log / insp_task_txn

### REQ-DBV2-003 (ubiquitous) — legacy compat 어댑터

The backend SHALL expose legacy-equivalent REST endpoints that derive responses from the new schema (e.g., `/api/dashboard/stats`, `/api/production/equipment`, `/api/quality/stats`, `/api/logistics/warehouse`).

- 빈 시계열 데이터(hourly/weekly/temperature/trend 등) 는 빈 배열 반환 — 충돌 없이 페이지 렌더만 보장
- `OrdFull` 응답에 `user_*` denormalized 필드 추가 → Next.js 어댑터가 legacy `Order` shape 생성

### REQ-DBV2-004 (event-driven) — Next.js 어댑터

WHEN Next.js admin/customer 페이지가 `fetchOrders()` / `fetchOrdersByEmail()` / `fetchOrderDetails()` / `updateOrderStatus()` 를 호출하면, `src/lib/api.ts` 의 어댑터 SHALL transform smartcast response → legacy `Order`/`OrderDetail`/`OrderStatus` shape.

- `ORD_STAT_TO_LEGACY`: RCVD→pending / APPR→approved / MFG→in_production / DONE→production_completed / SHIP→shipping_ready / COMP→completed / REJT·CNCL→rejected
- `id` 는 `"ord_{n}"` 형태로 변환 (기존 code 가 string 기대)

### REQ-DBV2-005 (unwanted-behavior) — legacy 테이블 보존

IF 신규 schema 적용 중 legacy `public` 스키마의 테이블 데이터가 삭제된다면, the migration SHALL be considered failed and rolled back using the pre-migration backup (`backups/db/smartcast_robotics_20260419_112714.dump`).

- 2026-04-19 백업: 72 MB DB, 21 테이블, pg_dump custom format, SHA256 검증 완료
- 복원: `PGPASSWORD='...' pg_restore -h ... -U team2 -d smartcast_robotics --clean --if-exists -j 4 backups/db/smartcast_robotics_20260419_112714.dump`

## Acceptance Summary

1. **Schema 격리**: `SELECT schema_name FROM information_schema.schemata` 에 `smartcast` 존재, `\dt smartcast.*` 에 29 테이블 출력.
2. **DDL 적용**: `backend/scripts/create_tables_v2.sql` 실행 후 0 에러 + 10 인덱스 생성.
3. **Seed 완료**: category 3 / pp_options 4 / zone 6 / res 6 / equip 4 / trans 2 / chg 3 / strg 18 / ship 5 / user 3 행 존재.
4. **E2E API**: 발주 생성 → 패턴 등록 → 생산 시작 → item 조회 → 검사 summary 까지 28 endpoint 정상 응답.
5. **Pink GUI 6건**: 
   - #1 `/customer/lookup` 빈 결과 차단 ✓
   - #2 발주 폼 비고란 부재 ✓
   - #3·#5 PyQt OperationsPage 패턴 등록 + 생산 시작 ✓
   - #4 OperationsPage 후처리 요구사항 표시 ✓
   - #6 OperationsPage 양품/불량 summary ✓
6. **Legacy compat**: `/api/dashboard/stats`, `/api/production/equipment`, `/api/quality/stats` 등 레거시 endpoint 200 응답.

## Exclusions (What NOT to Build)

- **SQLite 지원 재도입** — 2026-04-14 정책 유지 (feedback_db_postgresql_only).
- **RA cur_stat 완전 시퀀서** — 본 SPEC 에 상수만 정의 (Phase E). 자동 진행 로봇 컨트롤은 별도 SPEC.
- **hypertable/TimescaleDB** — 2026-04-19 현재 `timescaledb` extension 미설치. 시계열 집계 엔드포인트는 빈 배열 반환으로 스텁 유지.
- **legacy SPEC 전면 재작성** — SPEC-AMR-001 / SPEC-API-001 / SPEC-API-002 / SPEC-CTL-001 / SPEC-CASTING-001 / SPEC-ORD-001 본문은 **이력 보존** 원칙으로 유지. 각 파일 상단에 migration 배너만 추가.
- **Pydantic model_nm 명시 변경** — `_ORM` 베이스의 `protected_namespaces=()` 처리로 충분.
- **PyQt 레거시 페이지 UI 재설계** — 데이터 로딩 경로만 신규 API 로 전환; UI 레이아웃 개선은 별도 SPEC.

## Delta Markers (Brownfield)

| 마커 | 대상 | 비고 |
|------|------|------|
| `[EXISTING]` | `backend/app/models/models.py` @ legacy 19 클래스 | → `models_legacy.py` 로 이관 보존 |
| `[EXISTING]` | `backend/app/schemas/schemas.py` @ legacy Pydantic | → `schemas_legacy.py` 보존 |
| `[EXISTING]` | `backend/app/routes/*.py` | → `routes/legacy/*.py` 보존, 같은 이름 신규 구현 |
| `[NEW]` | `backend/scripts/{create_tables_v2,seed_masters_v2}.sql` | DDL + seed 산출물 |
| `[NEW]` | `backend/app/routes/dashboard.py` | `/api/dashboard/stats` derive endpoint |
| `[NEW]` | `monitoring/app/pages/operations.py` | 4 핑크 GUI 통합 단일 페이지 |
| `[MODIFY]` | `src/lib/api.ts` | smartcast → legacy shape 어댑터 |
| `[MODIFY]` | `src/app/customer/lookup/page.tsx` | 핑크 GUI #1 — 빈 결과 차단 |

## Non-Functional Requirements

### 실행 환경

- 백엔드: Python 3.11 + FastAPI 0.115 + SQLAlchemy 2.0 + psycopg 3.2
- PostgreSQL 16.13 (Ubuntu LTS) @ Tailscale `100.107.120.14:5432/smartcast_robotics`, role `team2`

### 성능

- Schema 격리는 쿼리 플래너 비용 증가 없음 (search_path 만 추가)
- legacy compat 엔드포인트는 최대 3건 JOIN 이내로 유지 (N+1 쿼리 방지)

### 관측성

- `main.py` lifespan 에서 seed idempotent 보장 로깅
- `websocket.py` 는 5초 polling → DB 스냅샷 broadcast (random mock 제거)

### 호환성

- Next.js 16 + React 19 + TypeScript 5 (no change)
- PyQt5 5.15 (no change) — api_client 에 smartcast 메서드 8개 추가만 반영

## Open Questions (Run phase 에서 해결)

- **ord_stat SHIP 타임스탬프**: 레거시 `shippedAt` 을 legacy Order 어댑터에서 채우려면 별도 쿼리 필요 → 현재는 빈 문자열로 처리, 후속 PR 에서 보완.
- **RA task → cur_stat 시퀀스**: Confluence open inline comment 에서 언급됨. 하드코딩 상수로 시작하되, 추후 DB 저장 가능성 검토.
- **TimescaleDB 재설치**: 시계열 집계가 실제 필요해지면 TimescaleDB extension 재설치 + hypertable 변환 SPEC 별도 생성.

## 부록 A — 운영 매뉴얼 (PR #4~#7 누적)

### 환경변수

| 변수 | 기본 | 효과 |
|---|---|---|
| `DATABASE_URL` | (필수) | PostgreSQL 연결 (`?options=-csearch_path%3Dsmartcast,public` 옵션 권장) |
| `FMS_AUTOPLAY` | `0` | `1` 시 백엔드 lifespan 에서 시퀀서 백그라운드 task 가동 (실기 미연동 데모/테스트용) |
| `FMS_ERROR_RATE` | `0.0` | `0.0~1.0` 범위. task 단계마다 확률적 FAIL → equip/trans_err_log INSERT |
| `APP_ENV` | `development` | `development` 시 `/api/debug/*` 엔드포인트 노출 |

### 자동 시퀀서 워크플로우

`FMS_AUTOPLAY=1` 가동 시 시퀀서가 다음 체인으로 자동 진행:

```
ord 생성 → 패턴 등록 → POST /api/production/start
  → equip_task_txn(MM, QUE) 자동 생성
시퀀서 polling (2 초):
  MM (RA): MV_SRC → GRASP → MV_DEST → RELEASE → RETURN → IDLE → SUCC
  → POUR (RA) 자동 enqueue (워크플로우 체인)
  → DM (RA)
  → PP (RA) → ToINSP (CONV) 자동 enqueue
  ...
  → SHIP (RA) → IDLE → SUCC + ord_stat=COMP 자동 INSERT
```

### 핸드오프 ACK (SPEC-AMR-001)

`trans_task_txn(task_type='ToPP')` 가 PROC 진입 → MV_SRC → WAIT_LD → MV_DEST →
**WAIT_HANDOFF (정지)**. 운영자 ACK 호출 시 풀림:

```bash
# CLI 호출
curl -X POST http://localhost:8000/api/debug/handoff-ack
# 응답: {released, orphan, task_id, amr_id, item_id, ord_id, reason}
```

UI 호출 경로:
- Next.js `DevHandoffAckButton.tsx` (좌하단 fixed 버튼, dev mode 만)
- PyQt `OperationsPage` 의 "🔔 후처리 ACK 발행" 버튼

### TimescaleDB 자동 분기

백엔드는 부팅 시 `pg_extension` 검사. extension 존재 시 hypertable 쿼리, 없으면
`date_trunc` 폴백. 사용자는 별도 설정 불필요. 설치/제거 시 backend 재시작 필요.

영향 endpoint:
- `/api/dashboard/stats` 응답 필드 `timescaledb_enabled: bool`
- `/api/production/hourly?hours=N`
- `/api/production/weekly?weeks=N`
- `/api/quality/trend?hours=N`

설치 가이드: `backend/scripts/timescale_install_guide.md`

### 데모 시나리오 (전체 워크플로우 검증)

```bash
# 1. backend 시퀀서 가동 (오류 5% 주입)
export FMS_AUTOPLAY=1 FMS_ERROR_RATE=0.05
backend/venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

# 2. 신규 발주 생성
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"detail":{"qty":10,"final_price":1200000,"due_date":"2026-05-31"},"pp_ids":[1,2]}'

# 3. 패턴 등록 (생성된 ord_id 사용)
curl -X POST http://localhost:8000/api/production/patterns \
  -H "Content-Type: application/json" -d '{"ptn_id":1,"ptn_loc":3}'

# 4. 생산 시작
curl -X POST http://localhost:8000/api/production/start \
  -H "Content-Type: application/json" -d '{"ord_id":1}'

# 5. 진행 모니터링 (10~30초마다)
curl -s http://localhost:8000/api/production/items?ord_id=1 | jq

# 6. ToPP 도착 시 핸드오프 ACK
curl -X POST http://localhost:8000/api/debug/handoff-ack

# 7. 최종 검사 요약
curl -s http://localhost:8000/api/quality/summary | jq
```
