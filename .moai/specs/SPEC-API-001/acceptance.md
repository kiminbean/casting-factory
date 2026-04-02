# Acceptance Criteria: SPEC-API-001

## AC-1: API 클라이언트 정상 동작

**Given** 백엔드 서버가 `localhost:8000`에서 실행 중일 때
**When** `fetchDashboardStats()`를 호출하면
**Then** DashboardStats 타입의 객체가 camelCase 필드명으로 반환되어야 한다

## AC-2: 대시보드 데이터 로드

**Given** 프론트엔드와 백엔드가 모두 실행 중일 때
**When** 브라우저에서 `/` (대시보드)에 접근하면
**Then** 요약 카드 4종(생산 목표 달성률, 가동 로봇, 미처리 주문, 금일 알람)에 백엔드 데이터가 표시되어야 한다

## AC-3: 로딩 상태 표시

**Given** 백엔드 서버가 실행 중이고 응답 지연이 있을 때
**When** 대시보드 페이지를 로드하면
**Then** 데이터 로드 완료 전까지 스켈레톤/로딩 UI가 표시되어야 한다

## AC-4: 에러 처리

**Given** 백엔드 서버가 실행되지 않을 때
**When** 대시보드 페이지를 로드하면
**Then** 에러 메시지가 표시되고 페이지가 크래시되지 않아야 한다

## AC-5: 알림 목록 연동

**Given** 백엔드에 Alert 데이터가 있을 때
**When** 대시보드 페이지를 로드하면
**Then** 실시간 알림 피드에 백엔드 데이터가 심각도 순으로 표시되어야 한다

## AC-6: 주문 테이블 연동

**Given** 백엔드에 Order 데이터가 있을 때
**When** 대시보드 페이지를 로드하면
**Then** 최근 주문 테이블에 최근 5건의 주문이 표시되어야 한다

## AC-7: 차트 데이터 연동

**Given** 백엔드에 ProductionMetric 데이터가 있을 때
**When** 대시보드 페이지를 로드하면
**Then** 주간 생산 추이 차트에 백엔드 데이터가 표시되어야 한다

## AC-8: snake_case → camelCase 변환

**Given** 백엔드 응답이 `{"production_goal_rate": 85.5}` 형식일 때
**When** API 클라이언트를 통해 데이터를 수신하면
**Then** `{productionGoalRate: 85.5}` 형식으로 변환되어야 한다

## 품질 기준

- 백엔드 서버 없이도 빌드(`npm run build`)가 성공해야 한다
- API 에러 시 UI가 graceful하게 처리되어야 한다
- Mock 데이터 파일(`mock-data.ts`)은 삭제하지 않고 유지 (다른 페이지에서 사용 가능)
