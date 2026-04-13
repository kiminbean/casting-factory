# 모듈 카탈로그

> **Last updated**: 2026-04-13

## 1. Next.js 프론트엔드 (`src/`)

### 1.1 App Routes (`src/app/`)

| Route | 파일 | 사용자 | 역할 |
|-------|------|--------|------|
| `/` | `page.tsx` | 관리자 | 통합 대시보드 (KPI, 알림, 3D 맵) |
| `/orders` | `orders/page.tsx` | 관리자 | 주문 관리 (목록, 상태변경, 견적, 스케줄링) |
| `/production` | `production/page.tsx` | 관리자 | 생산 모니터링 (8단계 공정, 차트) |
| `/quality` | `quality/page.tsx` | 관리자 | 품질 검사 (검사기록, 불량률, 분류기) |
| `/admin` | `admin/page.tsx` | 관리자 | 관리자 설정 |
| `/admin/login` | `admin/login/page.tsx` | 관리자 | 관리자 로그인 |
| `/customer` | `customer/page.tsx` | 고객 | 온라인 발주 (5단계 스텝 위저드) |
| `/customer/lookup` | `customer/lookup/page.tsx` | 고객 | 주문 조회 (이메일 기반) |
| `/customer/orders` | `customer/orders/page.tsx` | 고객 | 내 주문 목록 |

### 1.2 Components (`src/components/`)

| 컴포넌트 | 역할 | 의존성 |
|---------|------|--------|
| `AdminShell.tsx` | 관리자 레이아웃 (사이드바+헤더) | Sidebar, Header |
| `Sidebar.tsx` | 좌측 네비게이션 바 | next/link, lucide-react |
| `Header.tsx` | 상단 헤더 (알림 배지) | next/navigation |
| `SmartCastHeader.tsx` | 고객용 헤더 (로고) | SmartCastLogo |
| `SmartCastLogo.tsx` | SVG 로고 컴포넌트 | — |
| `FactoryMap.tsx` | 2D 공장 맵 | FactoryMapEditor, FactoryMap3D |
| `FactoryMap3D.tsx` | 3D 맵 래퍼 (dynamic import) | next/dynamic |
| `FactoryMap3DCanvas.tsx` | Three.js 3D 씬 | @react-three/fiber, drei, THREE |
| `FactoryMapEditor.tsx` | 맵 편집기 | lucide-react |
| `charts/WeeklyProductionChart.tsx` | 주간 생산량 차트 | recharts |
| `charts/DefectRateChart.tsx` | 불량률 차트 | recharts |
| `charts/ProductionVsDefectsChart.tsx` | 생산-불량 비교 | recharts |
| `charts/DefectTypeDistChart.tsx` | 불량 유형 분포 | recharts |

### 1.3 Library (`src/lib/`)

| 파일 | 역할 |
|------|------|
| `types.ts` | 전체 TypeScript 타입 정의 (Order, Equipment, Alert 등) |
| `api.ts` | REST API 클라이언트 (apiFetch + snake→camel 변환) |
| `mock-data.ts` | 개발용 목업 데이터 |
| `utils.ts` | 유틸리티 함수 |

### 1.4 Config Files

| 파일 | 역할 |
|------|------|
| `next.config.ts` | API proxy rewrite, allowedDevOrigins |
| `tsconfig.json` | TypeScript 설정 (`@/` path alias) |
| `package.json` | v3.4.0, npm scripts (dev, build, lint) |

---

## 2. FastAPI 백엔드 (`backend/`)

### 2.1 Core (`backend/app/`)

| 파일 | 역할 |
|------|------|
| `main.py` | FastAPI 앱 생성, 라우터 등록, lifespan (seed) |
| `database.py` | SQLAlchemy engine/session, PG/SQLite 분기, `.env.local` 로드 |
| `seed.py` | 초기 시드 데이터 (제품, 하중등급, 데모 주문 등) |

### 2.2 Routes (`backend/app/routes/`)

| 파일 | Prefix | 엔드포인트 수 | 역할 |
|------|--------|-------------|------|
| `orders.py` | `/api/orders`, `/api/products`, `/api/load-classes` | 8 | 주문 CRUD, 제품/하중등급 마스터 |
| `production.py` | `/api/production` | 4 | 공정 단계, 메트릭, 설비 |
| `quality.py` | `/api/quality` | 4 | 검사 기록, 통계, 기준, 분류기 |
| `logistics.py` | `/api/logistics` | 6 | 이송작업, 창고, 출고 주문 |
| `alerts.py` | `/api` | 3 | 알림, 대시보드 통계 |
| `schedule.py` | `/api/production/schedule` | 5 | 우선순위 계산, 생산 시작, 작업 관리 |
| `websocket.py` | `/ws` | 1 | 실시간 대시보드 WebSocket |

### 2.3 Models (`backend/app/models/models.py`)

| 모델 | 테이블 | 도메인 |
|------|--------|--------|
| `Order` | orders | 주문 관리 |
| `OrderDetail` | order_details | 주문 품목 상세 |
| `Product` | products | 제품 마스터 |
| `LoadClass` | load_classes | 하중 등급 마스터 |
| `ProcessStage` | process_stages | 공정 단계 |
| `Equipment` | equipment | 설비 정보 |
| `Alert` | alerts | 알림 |
| `InspectionRecord` | inspection_records | 검사 기록 |
| `InspectionStandard` | inspection_standards | 검사 기준 |
| `SorterLog` | sorter_logs | 분류기 로그 |
| `TransportTask` | transport_tasks | 이송 작업 |
| `WarehouseRack` | warehouse_racks | 창고 랙 |
| `OutboundOrder` | outbound_orders | 출고 주문 |
| `ProductionMetric` | production_metrics | 생산 통계 |
| `ProductionJob` | production_jobs | 생산 작업 |
| `PriorityChangeLog` | priority_change_logs | 우선순위 변경 이력 |

### 2.4 Schemas (`backend/app/schemas/schemas.py`)

Pydantic v2 모델. `Create` (입력), `Response` (출력), `Update` (부분 수정) 패턴.

---

## 3. PyQt5 모니터링 (`monitoring/`)

### 3.1 Core

| 파일 | 역할 |
|------|------|
| `main.py` | 앱 진입점, QApplication 생성 |
| `config.py` | API/WS/MQTT URL 설정 |
| `app/main_window.py` | QMainWindow — 페이지 스택 관리 |
| `app/api_client.py` | REST API 동기 클라이언트 |
| `app/ws_worker.py` | WebSocket QThread 워커 |
| `app/mqtt_worker.py` | MQTT QThread 워커 |
| `app/mock_data.py` | 오프라인 목업 데이터 |

### 3.2 Pages (`monitoring/app/pages/`)

| 파일 | 클래스 | 역할 |
|------|--------|------|
| `dashboard.py` | `DashboardPage` | 통합 대시보드 (KPI 카드, 차트) |
| `production.py` | `ProductionPage` | 생산 공정 모니터링 |
| `quality.py` | `QualityPage` | 품질 검사 모니터링 |
| `logistics.py` | `LogisticsPage` | 물류/이송 모니터링 |
| `map.py` | `FactoryMapPage` | 2D 공장 맵 |
| `schedule.py` | `SchedulePage` | 생산 스케줄링 |

### 3.3 Widgets (`monitoring/app/widgets/`)

| 파일 | 주요 위젯 | 역할 |
|------|----------|------|
| `gauges.py` | ArcGauge, DonutGauge, StatusIndicator | 반원/도넛 게이지 |
| `charts.py` | 7개 차트 클래스 | PyQtChart 기반 차트 |
| `factory_map.py` | FactoryMapWidget | 2D 공장 지도 |
| `amr_card.py` | AMR 상태 카드 | AMR 로봇 상태 표시 |
| `conveyor_card.py` | 컨베이어 카드 | 컨베이어 상태 표시 |
| `camera_view.py` | 카메라 뷰 | 비전 카메라 피드 |
| `sorter_dial.py` | 분류기 다이얼 | 각도/방향 표시 |
| `defect_panels.py` | 불량 패널 | 불량 정보 표시 |
| `alert_widgets.py` | 알림 위젯 | 실시간 알림 |
| `warehouse_rack.py` | 창고 랙 위젯 | 재고 시각화 |

---

## 4. 기타 모듈

### 4.1 Firmware (`firmware/`)

| 파일 | 역할 |
|------|------|
| `conveyor_controller/` | ESP32 + L298N + TOF250 컨베이어 제어 펌웨어 |

### 4.2 Blender (`blender/`)

| 파일 | 역할 |
|------|------|
| `factory_scene.py` | Blender 공장 씬 생성 스크립트 |

### 4.3 Scripts (`scripts/`)

| 파일 | 역할 |
|------|------|
| `sync_confluence_facts.py` | Confluence → `docs/CONFLUENCE_FACTS.md` 자동 동기화 |
