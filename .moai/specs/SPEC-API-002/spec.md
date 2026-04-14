# SPEC-API-002: 전체 페이지 Mock → REST API 전환 + 주문 관리 API 연동

## Overview
대시보드(/) 페이지는 SPEC-API-001에서 API 연동 완료. 나머지 5개 페이지(/orders, /production, /quality, /logistics, /customer/orders)를 mock-data.ts에서 FastAPI REST API 호출로 전환하고, 주문 승인/반려/수정 기능의 백엔드 API를 연동한다.

## Tech Stack
- Frontend: Next.js 16 App Router + TypeScript
- Backend: FastAPI 0.115 + SQLAlchemy 2.0 + PostgreSQL 16 (2026-04-14 SQLite 폴백 제거됨)
- API Proxy: next.config.ts rewrites /api/* → localhost:8000/api/*
- 기존 패턴: src/lib/api.ts (apiFetch + snake_case→camelCase 변환)

## Requirements

### SR-API-02-01: api.ts API 함수 확장
- EARS: When the frontend needs to call backend endpoints, the system SHALL provide typed API functions in src/lib/api.ts
- 추가할 함수:
  - fetchProcessStages() → GET /api/production/stages
  - fetchQualityStats() → GET /api/quality/stats
  - fetchInspections() → GET /api/quality/inspections
  - fetchInspectionStandards() → GET /api/quality/standards
  - fetchSorterLogs() → GET /api/quality/sorter-logs
  - fetchTransportTasks() → GET /api/logistics/tasks
  - fetchWarehouseRacks() → GET /api/logistics/warehouse
  - fetchOutboundOrders() → GET /api/logistics/outbound-orders
  - fetchOrderDetails(orderId) → GET /api/orders/{id}/details
  - updateOrderStatus(orderId, status) → PATCH /api/orders/{id}/status
  - updateOrder(orderId, data) → PATCH /api/orders/{id}
  - fetchHourlyProduction() → GET /api/production/metrics (최근 24시간)

### SR-API-02-02: /production 페이지 API 연동
- EARS: When an admin opens /production, the system SHALL load process stages, equipment, and hourly metrics from the API
- mockProcessStages → fetchProcessStages()
- mockEquipment → fetchEquipment() (이미 존재)
- mockHourlyProduction → fetchProductionMetrics() (일별 지표 재사용)
- 로딩 스켈레톤 UI + 에러 처리

### SR-API-02-03: /orders 페이지 API 연동
- EARS: When an admin opens /orders, the system SHALL load orders from the API and support status changes
- mockOrders → fetchOrders()
- mockOrderDetails → fetchOrderDetails(orderId)
- 승인 버튼 → updateOrderStatus(id, "approved")
- 반려 버튼 → updateOrderStatus(id, "rejected")
- 로딩 스켈레톤 UI + 에러 처리

### SR-API-02-04: /quality 페이지 API 연동
- EARS: When an admin opens /quality, the system SHALL load inspection records and statistics from the API
- mockInspections → fetchInspections()
- mockDefectTypeStats → fetchQualityStats() (서버에서 집계)
- mockSorterLogs → fetchSorterLogs()
- mockInspectionStandards → fetchInspectionStandards()
- 로딩 스켈레톤 UI + 에러 처리

### SR-API-02-05: /logistics 페이지 API 연동
- EARS: When an admin opens /logistics, the system SHALL load transport tasks, warehouse racks, and outbound orders from the API
- mockTransports → fetchTransportTasks()
- mockEquipment (AMR) → fetchEquipment() (이미 존재)
- mockWarehouseRacks → fetchWarehouseRacks()
- mockOutboundOrders → fetchOutboundOrders()
- 로딩 스켈레톤 UI + 에러 처리

### SR-API-02-06: /customer/orders 페이지 API 연동
- EARS: When a customer opens /customer/orders, the system SHALL load their orders from the API
- mockOrders → fetchOrders()
- mockOrderDetails → fetchOrderDetails(orderId)
- 로딩 스켈레톤 UI + 에러 처리

### SR-API-02-07: 백엔드 주문 수정 API 추가
- EARS: When an admin edits order fields, the system SHALL persist changes via PATCH /api/orders/{id}
- 수정 가능 필드: total_amount (견적 금액), confirmed_delivery (확정 납기), notes (비고)
- OrderUpdate Pydantic 스키마 추가
- 기존 orders.py 라우터에 엔드포인트 추가

## Acceptance Criteria
- [x] api.ts에 12개 API 함수 추가 완료
- [x] /production 페이지 mock 제거 → API 호출 전환
- [x] /orders 페이지 mock 제거 → API 호출 전환 + 승인/반려 버튼 동작
- [x] /quality 페이지 mock 제거 → API 호출 전환
- [x] /logistics 페이지 mock 제거 → API 호출 전환
- [x] /customer/orders 페이지 mock 제거 → API 호출 전환
- [x] PATCH /api/orders/{id} 백엔드 엔드포인트 동작
- [x] 모든 페이지 로딩 스켈레톤 + 에러 처리 표시
- [x] 기존 대시보드 API 연동 정상 유지 (회귀 없음)
- [x] Next.js 빌드 통과 (TypeScript 오류 없음)

## Technical Approach
1. api.ts에 누락된 API 함수 일괄 추가 (기존 apiFetch 패턴 활용)
2. 백엔드 PATCH /api/orders/{id} 엔드포인트 추가
3. 각 페이지를 "use client" → useState/useEffect 패턴으로 전환
4. 대시보드 page.tsx의 스켈레톤/에러 패턴을 동일하게 적용
5. mock-data.ts import 제거 (단, 파일 자체는 유지 — 다른 곳에서 참조 가능)

## Phase Plan
- Phase 1: api.ts 확장 + 백엔드 PATCH API (기반 작업)
- Phase 2: 5개 페이지 순차 전환 (/orders → /production → /quality → /logistics → /customer/orders)
- Phase 3: 통합 검증

## Changelog
- v1.0 (2026-04-02): 초기 작성
- v1.1 (2026-04-02): 전체 구현 완료 — api.ts 12개 함수 추가, 5개 페이지 API 전환, 백엔드 PATCH API 추가, 빌드 검증 통과
