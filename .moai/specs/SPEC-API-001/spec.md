---
id: SPEC-API-001
version: "1.0.0"
status: completed
created: "2026-04-02"
updated: "2026-04-02"
author: kisoo
priority: high
issue_number: 0
---

# SPEC-API-001: 프론트엔드-백엔드 API 연동

> **📌 Schema Migration Note (2026-04-19)**: 본 SPEC 의 테이블/엔드포인트 명칭은
> **smartcast schema** (Confluence 32342045 v59) 적용 이후 변경됨. 신규 매핑은
> [SPEC-DB-V2-MIGRATION](../SPEC-DB-V2-MIGRATION/spec.md) 참조.
>
> | 기존 (public schema) | 신규 (smartcast schema) |
> |---|---|
> | `orders` / `order_details` | `ord` + `ord_detail` |
> | `products` | `product` + `product_option` + `category` |
> | `equipment` | `res` (마스터) + `equip` + `trans` |
> | `inspection_records` | `insp_task_txn` |
> | `transport_tasks` | `trans_task_txn` + `trans_stat` + `trans_err_log` |
> | `outbound_orders` | `ord_stat` (SHIP/COMP) + `ship_location_stat` |
> | `warehouse_racks` | `strg_location_stat` |
>
> 본문은 이력 보존을 위해 원형 유지. legacy compat endpoint 는
> `backend/app/routes/{dashboard,production,quality,logistics}.py` 가 derive 한다.

## HISTORY

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-02 | 1.0.0 | 초기 SPEC 생성 |
| 2026-04-02 | 1.1.0 | 구현 완료, sync 완료 |

## 개요

프론트엔드 대시보드의 Mock 데이터(`src/lib/mock-data.ts`)를 FastAPI 백엔드 REST API로 전환한다. API 클라이언트 레이어를 생성하고, 대시보드 페이지의 데이터를 실제 백엔드에서 로드하도록 변경한다.

## 요구사항 (EARS Format)

### R1: API 클라이언트 모듈 [Ubiquitous]
모든 백엔드 API 호출은 `src/lib/api.ts` 모듈을 통해 수행해야 한다.
- API 기본 URL 설정 (환경 변수 또는 기본값 `http://localhost:8000`)
- snake_case → camelCase 자동 변환
- 에러 응답 처리 (HTTP 4xx/5xx)
- TypeScript 타입 안전성 보장 (types.ts 타입 사용)

### R2: 대시보드 통계 연동 [Event-Driven]
대시보드 페이지 로드 시, `GET /api/dashboard/stats`에서 DashboardStats를 가져와 요약 카드 4종을 렌더링해야 한다.
- 로딩 상태 표시 (스켈레톤 UI)
- 에러 발생 시 에러 메시지 표시
- `mockDashboardStats` 대신 API 응답 사용

### R3: 알림 목록 연동 [Event-Driven]
대시보드 페이지 로드 시, `GET /api/alerts`에서 Alert 목록을 가져와 실시간 알림 피드를 렌더링해야 한다.
- 심각도 순 정렬 유지
- 장비 이름 조회를 위해 Equipment 데이터도 API에서 로드

### R4: 설비 목록 연동 [Event-Driven]
대시보드 페이지 로드 시, 설비 목록을 API에서 가져와 공장 레이아웃 맵과 알림의 장비명 참조에 사용해야 한다.

### R5: 주문 목록 연동 [Event-Driven]
대시보드 페이지 로드 시, `GET /api/orders`에서 최근 주문을 가져와 주문 테이블을 렌더링해야 한다.
- 최근 5건만 표시

### R6: 주간 생산 차트 연동 [Event-Driven]
대시보드 페이지 로드 시, 생산 지표 API에서 주간 데이터를 가져와 WeeklyProductionChart에 전달해야 한다.

### R7: 백엔드 차트 API 추가 [Unwanted]
프론트엔드에 필요한 차트 데이터 중 백엔드에 API가 없는 경우, 해당 API를 추가해야 한다.
- `GET /api/production/metrics` — 일별 생산 지표
- `GET /api/production/metrics/weekly` — 주간 생산 추이 (선택)

## 범위

### 포함
- API 클라이언트 모듈 (`src/lib/api.ts`) 생성
- 대시보드 페이지 (`src/app/page.tsx`) API 연동
- 필요 시 백엔드 누락 API 추가
- 로딩/에러 상태 UI

### 제외
- WebSocket 실시간 갱신 (별도 SPEC)
- 대시보드 이외 페이지 (주문관리, 생산모니터링 등)
- 인증/권한 시스템
- 프로덕션 배포 설정

## 기술 제약

- Next.js 16 App Router의 Client Component 사용 (`"use client"`)
- camelCase/snake_case 변환은 API 레이어에서 일괄 처리
- 백엔드 기본 포트: 8000, 프론트엔드 기본 포트: 3000
- CORS는 이미 전체 허용 설정 (`allow_origins=["*"]`)
