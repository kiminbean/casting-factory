# Implementation Plan: SPEC-API-001

## 작업 분해

### Task 1: API 클라이언트 모듈 생성
**파일**: `src/lib/api.ts` (신규)
- fetch 기반 API 클라이언트 함수 작성
- 기본 URL: `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"`
- snake_case → camelCase 자동 변환 유틸리티
- 타입 안전한 API 함수들:
  - `fetchDashboardStats(): Promise<DashboardStats>`
  - `fetchAlerts(): Promise<Alert[]>`
  - `fetchEquipment(): Promise<Equipment[]>`
  - `fetchOrders(): Promise<Order[]>`
  - `fetchProductionMetrics(): Promise<ProductionMetric[]>`

### Task 2: 백엔드 누락 API 추가
**파일**: `backend/app/routes/production.py` (수정)
- `GET /api/production/metrics` — ProductionMetric 목록 반환
  - 이미 모델/스키마 존재 (ProductionMetric, ProductionMetricResponse)
  - 라우트만 추가 필요

**파일**: `backend/app/routes/alerts.py` (확인)
- `GET /api/dashboard/stats` — 이미 존재, 확인만
- Equipment 목록 API 존재 여부 확인 → 없으면 추가

### Task 3: 대시보드 페이지 API 연동
**파일**: `src/app/page.tsx` (수정)
- Mock import 제거 → API 호출로 교체
- useState + useEffect 패턴으로 데이터 로드
- 로딩 스켈레톤 UI 추가
- 에러 상태 처리

### Task 4: 차트 컴포넌트 props 전환
**파일**: `src/components/charts/WeeklyProductionChart.tsx` (수정)
- Mock 데이터 직접 참조를 props로 전환
- 부모(page.tsx)에서 API 데이터를 props로 전달

### Task 5: FactoryMap 컴포넌트 props 전환
**파일**: `src/components/FactoryMap.tsx` (수정)
- 내부 Mock 참조가 있다면 props로 전환

## 의존성 관계

```
Task 2 (백엔드 API) ─┐
                      ├─→ Task 3 (페이지 연동) → Task 4, 5 (컴포넌트 전환)
Task 1 (API 클라이언트) ─┘
```

Task 1과 Task 2는 병렬 실행 가능. Task 3은 1, 2 완료 후 진행.

## 위험 및 대응

| 위험 | 확률 | 대응 |
|------|------|------|
| camelCase 변환 누락 | 중간 | 유닛 테스트로 변환 로직 검증 |
| 백엔드 서버 미실행 시 프론트엔드 에러 | 높음 | 에러 UI + 개발 시 환경변수로 Mock fallback 옵션 |
| 날짜 포맷 불일치 | 낮음 | Backend ISO 8601 → Frontend formatDate 유지 |

## 기술 스택 (추가 없음)

기존 의존성만 사용. 새 라이브러리 설치 불필요.
- fetch API (내장)
- React useState/useEffect (내장)
