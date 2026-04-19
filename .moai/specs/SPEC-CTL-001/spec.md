# SPEC-CTL-001: 생산 스케줄링 모듈 (SR-CTL-04 + SR-CTL-05)

> **📌 Schema Migration Note (2026-04-19)**: smartcast schema 적용 후 본 SPEC 의
> 데이터 모델은 변경됨. `production_jobs` 는 `equip_task_txn` 으로, `priority_change_logs`
> 는 별도 테이블 없음 (필요 시 ord_log 활용). FMS 자동 시퀀서 도입으로 일부 수동
> 우선순위 조정은 `equip_task_txn.req_at` 순서 (FIFO) 로 단순화됨.
> 매핑 표 / endpoint 호환은 [SPEC-DB-V2-MIGRATION](../SPEC-DB-V2-MIGRATION/spec.md) 참조.

## Overview
관리자가 승인된 주문 중 생산 가능한 항목을 선택하여 우선순위를 자동 계산하고, 수동 조정 후 실제 공정에 할당하여 생산을 개시하는 모듈.

## Requirements Source
- SR-CTL-04: 생산 개시
- SR-CTL-05: 우선순위 계산

## Tech Stack
- Backend: FastAPI + SQLAlchemy (기존 패턴)
- Frontend: Next.js 16 App Router + TypeScript + Tailwind CSS
- Priority Algorithm: 가중 점수제 (Weighted Scoring, 서버사이드)

## Functional Requirements

### FR-CTL-04-01: 승인 주문 목록 표시
- EARS: When an admin opens /production/schedule, the system SHALL display all orders with status "approved" including estimated completion, delay risk, and ready status.
- 각 주문에 표시: 주문번호, 회사명, 제품명, 수량, 납기일, 예상완료일, 지연위험도(high/medium/low), 착수가능여부(ready/not_ready)
- 착수 불가 주문: 시각적 경고 (빨간 테두리 + 사유 표시), 선택 시 확인 모달

### FR-CTL-04-02: 다중 주문 선택 + 우선순위 계산
- EARS: When an admin selects one or more approved orders and clicks "우선순위 계산", the system SHALL call the priority API and display ranked results with scoring breakdown and recommendation reasons.
- 체크박스 다중 선택 → "우선순위 계산" 버튼 → POST /api/production/schedule/calculate
- 결과: 순위별 카드 (점수, 사유, 주요 요인 강조)

### FR-CTL-04-03: 수동 우선순위 조정
- EARS: When an admin manually reorders the priority list, the system SHALL record the change with timestamp and reason.
- 드래그 앤 드롭 또는 ↑↓ 버튼으로 순서 변경
- 변경 시 사유 입력 모달 (필수)
- 변경 이력: POST /api/production/schedule/priority-log

### FR-CTL-04-04: 생산 개시 (배치 상태 전환)
- EARS: When an admin confirms production start, the system SHALL change all selected orders from "approved" to "in_production" and create ProductionJob records.
- "생산 시작" 버튼 → 확인 모달 → POST /api/production/schedule/start
- 각 주문에 ProductionJob 레코드 생성 (공정 할당)
- 주문 상태: approved → in_production 일괄 전환

### FR-CTL-05-01: 우선순위 자동 계산 알고리즘
- EARS: When the system calculates priority, it SHALL consider delivery deadline, process availability, bottleneck status, equipment availability, customer importance, quantity efficiency, and setup change cost.

**가중 점수 테이블 (총 100점):**

| 요소 | 가중치 | 산출 방식 |
|------|--------|----------|
| 납기일 긴급도 | 25점 | D-day 기준. <=3일: 25, <=7일: 20, <=14일: 15, <=30일: 10, >30일: 5 |
| 착수 가능 여부 | 20점 | 전 공정 idle + 설비 가동 가능: 20, 일부 가능: 10, 불가: 0 |
| 주문 체류 시간 | 15점 | 승인 후 경과일. >=7일: 15, >=3일: 10, >=1일: 5, <1일: 2 |
| 지연 위험도 | 15점 | 예상완료일 > 납기일: 15(위험), 예상완료일 근접: 10, 여유: 5 |
| 고객 중요도 | 10점 | 주문 금액 상위 20%: 10, 중간: 6, 하위: 3 |
| 수량 효율 | 10점 | 50개 이하: 10, 100개 이하: 7, 200개 이하: 4, 초과: 2 |
| 세팅 변경 비용 | 5점 | 직전 작업과 동일 제품/재질: 5, 유사: 3, 상이: 0 |

**추천 사유 생성 규칙:**
- 최고 가중 요소 2-3개를 사유로 조합
- 예: "납기일 3일 이내 임박 + 전 공정 착수 가능 + 고객 중요도 높음"

### FR-CTL-05-02: 착수 가능 여부 판정
- EARS: When evaluating readiness, the system SHALL check process stage availability, equipment status, and mark non-ready orders with specific blocking reasons.
- 판정 기준:
  1. 공정 단계 중 "running" 상태가 없는 라인 존재
  2. 주요 설비(furnace, mold_press) 중 idle/running 상태인 것 존재
  3. AMR이 1대 이상 가용 (idle 또는 charging > 50%)
- 차단 사유: "용해로 가동 중", "조형기 정비 중", "AMR 전체 사용 불가" 등

## Data Models

### ProductionJob
```
id: String (PK, "JOB-YYYY-NNN")
order_id: String (FK → orders.id)
priority_score: Float
priority_rank: Integer
assigned_stage: String (현재 할당 공정)
status: String (queued/running/completed/cancelled)
estimated_completion: String (ISO datetime)
started_at: String (ISO datetime)
completed_at: String (nullable)
created_at: String (ISO datetime)
```

### PriorityChangeLog
```
id: Integer (PK, autoincrement)
order_id: String
old_rank: Integer
new_rank: Integer
reason: String (사유)
changed_by: String (기본: "admin")
changed_at: String (ISO datetime)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/production/schedule/calculate | 선택 주문 우선순위 계산 |
| POST | /api/production/schedule/start | 생산 개시 (배치 상태 전환) |
| GET | /api/production/schedule/jobs | 생산 작업 목록 조회 |
| POST | /api/production/schedule/priority-log | 우선순위 변경 이력 기록 |
| GET | /api/production/schedule/priority-log/{order_id} | 특정 주문 변경 이력 조회 |

## Acceptance Criteria
- [x] 승인 주문 목록에 예상완료일/지연위험도/착수가능 표시
- [x] 다중 선택 → 우선순위 자동 계산 + 사유 표시
- [x] 수동 순서 변경 + 사유 입력 + 이력 기록
- [x] 생산 개시 → approved→in_production 상태 전환 + ProductionJob 생성
- [x] 착수 불가 주문 경고 표시
- [x] 백엔드 5개 API 엔드포인트 정상 동작
- [x] Next.js 빌드 통과 (TypeScript 오류 0개)

## Changelog
- v1.0 (2026-04-02): 초기 작성
- v1.1 (2026-04-02): 전체 구현 완료 — 백엔드 스케줄링 모듈 + 프론트엔드 /production/schedule 페이지 + 사이드바 메뉴 + 빌드 검증 통과
