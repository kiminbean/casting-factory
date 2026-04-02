# Research: Frontend-Backend API Integration

## 현재 상태 분석

### 프론트엔드 (Mock 데이터 패턴)

**src/lib/mock-data.ts**에서 다음 Mock 데이터를 직접 export:
- `mockOrders: Order[]` — 주문 목록 (5건)
- `mockOrderDetails: OrderDetail[]` — 주문 상세 품목
- `mockProducts: Product[]` — 제품 마스터
- `mockProcessStages: ProcessStageData[]` — 8단계 공정 상태
- `mockEquipment: Equipment[]` — 설비 목록 (15+ 대)
- `mockTransportTasks: TransportTask[]` — 이송 작업
- `mockInspectionRecords: InspectionRecord[]` — 검사 기록
- `mockAlerts: Alert[]` — 알림 목록
- `mockDashboardStats: DashboardStats` — 대시보드 요약 통계
- `mockProductionMetrics: ProductionMetric[]` — 일별 생산 통계
- `mockHourlyProduction: HourlyProduction[]` — 시간별 생산
- `mockDefectTypeStats: DefectTypeStat[]` — 불량 유형 분포
- `mockMonthlyProduction: MonthlyProductionSummary[]` — 월별 생산
- `mockWarehouseRacks: WarehouseRack[]` — 창고 랙
- `mockOutboundOrders: OutboundOrder[]` — 출고 주문
- `mockInspectionStandards: InspectionStandard[]` — 검사 기준
- `mockSorterLogs: SorterLog[]` — 분류기 로그

**사용 패턴 (page.tsx)**:
```typescript
import { mockDashboardStats, mockAlerts, mockEquipment, mockOrders } from "@/lib/mock-data";
// 직접 변수 참조 (API 호출 없음)
const stats = mockDashboardStats;
const sortedAlerts = [...mockAlerts].sort(...);
const recentOrders = mockOrders.slice(0, 5);
```

### 백엔드 (FastAPI API 구조)

**API 접두사**: 모두 `/api/` 하위

| 라우터 | 접두사 | 주요 엔드포인트 |
|--------|--------|----------------|
| orders.py | `/api/orders` | GET /, POST /, PATCH /{id}/status, GET /{id}/details, POST /{id}/details |
| orders.py | `/api/products` | GET / |
| production.py | `/api/production` | (공정 단계 조회) |
| quality.py | `/api/quality` | (검사 기록 조회, 통계) |
| logistics.py | `/api/logistics` | (이송 작업, 창고, 출고) |
| alerts.py | `/api/alerts` | GET /, PATCH /{id}/acknowledge |
| alerts.py | `/api/dashboard` | GET /stats |
| websocket.py | `/ws` | WebSocket 연결 |

### 타입 매핑 (Frontend ↔ Backend 필드명)

**주요 차이점 (camelCase ↔ snake_case)**:
- `customerId` ↔ `customer_id`
- `companyName` ↔ `company_name`
- `totalAmount` ↔ `total_amount`
- `requestedDelivery` ↔ `requested_delivery`
- `createdAt` ↔ `created_at`
- `productionGoalRate` ↔ `production_goal_rate`
- `activeRobots` ↔ `active_robots`

Backend Pydantic 스키마는 `from_attributes=True` 설정으로 ORM 모델에서 자동 변환.
하지만 **JSON 응답은 snake_case**로 전달됨 → 프론트엔드에서 camelCase 변환 필요.

### DashboardStats 필드 매핑

| Frontend (types.ts) | Backend (schemas.py) |
|---------------------|---------------------|
| productionGoalRate | production_goal_rate |
| activeRobots | active_robots |
| pendingOrders | pending_orders |
| todayAlarms | today_alarms |
| todayProduction | today_production |
| defectRate | defect_rate |
| equipmentUtilization | equipment_utilization |
| completedToday | completed_today |

### 누락된 백엔드 API

프론트엔드 Mock 데이터 중 백엔드에 대응 API가 없는 항목:
- `HourlyProduction` — 시간별 생산 통계 API 없음
- `DefectTypeStat` — 불량 유형 분포 API 없음 (quality에 통합 가능)
- `MonthlyProductionSummary` — 월별 생산 요약 API 없음
- `ProductionMetric` — 일별 생산 지표 조회 API 확인 필요

## 위험 요소 및 제약 사항

1. **camelCase/snake_case 변환**: 프론트엔드 types.ts가 camelCase, Backend JSON이 snake_case → API 클라이언트 레이어에서 변환 필수
2. **날짜 포맷**: Backend는 `datetime` 객체를 ISO 8601로 직렬화, Frontend는 string 타입으로 기대
3. **DashboardStats 통합 API**: 단일 /api/dashboard/stats 엔드포인트로 여러 테이블 조인 → 성능 고려
4. **차트 데이터 API**: HourlyProduction, DefectTypeStat 등은 백엔드에 아직 없음
5. **WebSocket 연동**: 실시간 데이터 갱신은 REST API 연동 후 별도 단계로 진행 권장

## 구현 접근법 권장

1. `src/lib/api.ts` — API 클라이언트 모듈 생성 (fetch wrapper + camelCase 변환)
2. 대시보드 페이지(page.tsx)를 Client Component + useEffect/useState로 전환
3. Mock 데이터를 API 호출로 단계적 교체
4. 백엔드에 누락된 차트 API 추가 (production_metrics, quality_stats)
5. 에러 핸들링 + 로딩 상태 UI 추가
