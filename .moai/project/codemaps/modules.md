# 모듈 카탈로그

> **Last updated**: 2026-04-09

## 1. Next.js 프론트엔드 (`src/`)

### 1.1 페이지 (App Router)

| 라우트 | 파일 | 역할 | 사이드바 노출 |
|---|---|---|---|
| `/` | `src/app/page.tsx` | 관리자 포털 허브 (카드 2개 + PyQt5 안내) | ✓ |
| `/orders` | `src/app/orders/page.tsx` (962줄) | 주문 관리 (탭/상세/견적/생산 승인) | ✓ |
| `/quality` | `src/app/quality/page.tsx` (610줄) | 품질 검사 (검사/통계/기준/sorter) | ✓ |
| `/production` | `src/app/production/page.tsx` (928줄) | 공정·설비·지표 (Sidebar 미링크, 직접 URL 전용) | ✗ |
| `/customer` | `src/app/customer/layout.tsx` + `page.tsx` (1222줄) | 고객 발주 포털 (자체 HTML 레이아웃, 4단계 폼, PRODUCTS 하드코딩) | ✗ (별도 배포 대상) |
| `/customer/orders` | `src/app/customer/orders/page.tsx` (439줄) | 고객 주문 조회 (6단계 상태 타임라인) | ✗ |

### 1.2 루트 레이아웃 / 쉘

| 파일 | 역할 |
|---|---|
| `src/app/layout.tsx` | HTML shell, Inter 폰트, `<AdminShell>` 래핑, `lang="ko"` |
| `src/components/AdminShell.tsx` | `pathname.startsWith("/customer")` → passthrough, 그 외 Sidebar+Header |
| `src/components/Sidebar.tsx` | 관리자 네비 (주문·품질 2개 링크, 주석에 UI 분리 정책 명시) |
| `src/components/Header.tsx` | 상단바 (`/`, `/orders`, `/quality` 타이틀 맵, 1초 시계, 알림 뱃지 하드코딩) |

### 1.3 시각화 컴포넌트

| 컴포넌트 | 역할 | 파일 |
|---|---|---|
| FactoryMap | 2D 공장 레이아웃 (1485줄) | `src/components/FactoryMap.tsx` |
| FactoryMap3D | Three.js 3D 뷰어 | `src/components/FactoryMap3D.tsx` |
| FactoryMap3DCanvas | R3F Canvas 래퍼 | `src/components/FactoryMap3DCanvas.tsx` |
| FactoryMapEditor | 3D 배치 편집기 | `src/components/FactoryMapEditor.tsx` |

### 1.4 차트 (recharts, dynamic ssr:false)

- `src/components/charts/WeeklyProductionChart.tsx`
- `src/components/charts/ProductionVsDefectsChart.tsx`
- `src/components/charts/DefectRateChart.tsx`
- `src/components/charts/DefectTypeDistChart.tsx`

### 1.5 공용 라이브러리 (`src/lib/`)

| 파일 | 역할 |
|---|---|
| `api.ts` | `apiFetch<T>` + `convertKeys` (snake→camel) + 20+ fetch 함수. `API_BASE = NEXT_PUBLIC_API_URL ?? ""` (빈 문자열 → Next rewrite) |
| `types.ts` (362줄) | Order, OrderStatus(7), Product, Equipment, Alert, ProcessStageData(8), TransportTask(10), PriorityResult, ProductionJob 등 전체 camelCase 도메인 타입 |
| `utils.ts` | orderStatusMap, processStatusMap, equipmentStatusMap, transportStatusMap, formatDate, formatCurrency |
| `mock-data.ts` (575줄) | 구 mock 데이터 (현재 실사용처는 api.ts fetch, 일부 레거시 가능성 있음) |

**주의**: `lib/types.ts` 의 `Product` 인터페이스는 구식 (id/name/category/basePrice/optionPricing/designImageUrl/model3dPath). 최근 확장된 백엔드 `ProductResponse` 필드 (spec, priceRange, diameterOptions, thicknessOptions, materials, loadClassRange) 미반영. `customer/page.tsx` 는 자체 로컬 `interface Product` 정의 사용.

**주의**: `api.ts` 에 `fetchProducts()` / `fetchLoadClasses()` 함수는 **아직 없음**. 신규 `/api/products`, `/api/load-classes` 엔드포인트는 만들어져 있지만 프론트에서 호출하지 않음.

## 2. FastAPI 백엔드 (`backend/app/`)

### 2.1 애플리케이션 코어

| 파일 | 역할 |
|---|---|
| `main.py` | FastAPI 앱 + CORS(`*`) + 8 라우터 include + lifespan (SQLite일 때만 DB 파일 삭제·재시드, PG일 때는 create_all + idempotent seed) |
| `database.py` | `_load_env_local()` (stdlib), `DATABASE_URL` 환경변수 or SQLite 폴백, engine factory (PG: pool_size=10, pre_ping, recycle 1800) |
| `models/models.py` | 17개 SQLAlchemy ORM 클래스 |
| `schemas/schemas.py` (615줄) | Pydantic v2 Create/Update/Response 스키마. `ProductResponse.from_orm_model()` 이 `*_json` TEXT 컬럼을 list/dict 로 파싱 |
| `seed.py` (457줄) | 14개 `_seed_*` 함수 (모두 `count>0` skip 멱등) |

### 2.2 API 라우터 (`routes/`)

| 라우터 | prefix | 파일 | 엔드포인트 수 | 주요 기능 |
|---|---|---|---|---|
| orders.router | `/api/orders` | `orders.py` | 6 | 주문 CRUD + 상세 + 상태 |
| products_router | `/api/products` | `orders.py` | 1 | 제품 마스터 (JSON 파싱) |
| load_classes_router | `/api/load-classes` | `orders.py` | 1 | EN 124 하중 등급 마스터 |
| production.router | `/api/production` | `production.py` | 4 | stages/metrics/equipment |
| schedule | `/api/production/schedule` | `schedule.py` | 6 | 7요소 우선순위 + jobs + priority-log |
| quality.router | `/api/quality` | `quality.py` | 4 | inspections/stats/standards/sorter-logs |
| logistics.router | `/api/logistics` | `logistics.py` | 6 | tasks/warehouse/outbound-orders |
| alerts.router | `/api` | `alerts.py` | 3 | alerts + acknowledge + dashboard/stats |
| websocket.router | `/ws` | `websocket.py` | 1 (WS) | `/ws/dashboard` 5초 tick |

**총 HTTP 엔드포인트**: 31개 + WebSocket 1개

### 2.3 데이터 모델 (17 테이블)

| # | 클래스 | 테이블 | PK | FK 관계 |
|---|---|---|---|---|
| 1 | Order | orders | id(varchar) | ← order_details, production_jobs |
| 2 | OrderDetail | order_details | id(varchar) | → orders |
| 3 | Product | products | id(varchar: D450/D600/D800/GRATING) | 독립 |
| 4 | **LoadClass** (신규 2026-04-09) | load_classes | code(varchar) | 독립 |
| 5 | ProcessStage | process_stages | id(int autoinc) | 독립 (id 참조) |
| 6 | Equipment | equipment | id(varchar) | 독립 |
| 7 | Alert | alerts | id(varchar) | 독립 |
| 8 | InspectionRecord | inspection_records | id(varchar) | 독립 (id 참조) |
| 9 | InspectionStandard | inspection_standards | id(int autoinc) | 독립 |
| 10 | SorterLog | sorter_logs | id(int autoinc) | 독립 |
| 11 | TransportTask | transport_tasks | id(varchar) | 독립 |
| 12 | WarehouseRack | warehouse_racks | id(varchar) | 독립 |
| 13 | OutboundOrder | outbound_orders | id(varchar) | 독립 |
| 14 | ProductionMetric | production_metrics | id(int autoinc) | 독립 |
| 15 | ProductionJob | production_jobs | id(varchar) | → orders |
| 16 | PriorityChangeLog | priority_change_logs | id(int autoinc) | 독립 (order_id 참조) |

FK 제약은 2개뿐 (`order_details.order_id`, `production_jobs.order_id`). 나머지는 ID 문자열 soft-link.

**최근 확장 (2026-04-09)**:
- `Product` 컬럼 추가: `category_label`, `spec`, `price_range`, `base_price`, `diameter_options_json` (TEXT), `thickness_options_json` (TEXT), `materials_json` (TEXT), `load_class_range`, `option_pricing_json`, `design_image_url`, `model_3d_path`
- `LoadClass` 신규: `code`, `load_tons`, `use_case`, `display_order`

### 2.4 데이터 마이그레이션 스크립트 (`backend/scripts/`)

| 파일 | 실행 시점 | 역할 |
|---|---|---|
| `migrate_sqlite_to_pg.py` | 2026-04-09 일회성 | SQLite → PG 14 테이블 161 rows 이관 + sequence reset |
| `migrate_products_front_truth.sql` | 2026-04-09 일회성 (멱등) | Product 컬럼 7개 추가 + order_details.product_id 재매핑 (PRD-* → D*) + 5→4 rows |
| `migrate_load_classes.sql` | 2026-04-09 일회성 (멱등) | load_classes 테이블 생성 + 6 row INSERT |

## 3. PyQt5 모니터링 앱 (`monitoring/`)

### 3.1 코어

| 모듈 | 파일 | 역할 |
|---|---|---|
| 진입점 | `monitoring/main.py` | QApplication, QSS 로드, MainWindow 실행 |
| 설정 | `monitoring/config.py` | `CASTING_API_HOST=192.168.0.16:8000` 기본, WS URL, MQTT 토픽 |
| 메인 윈도우 | `monitoring/app/main_window.py` | 좌 사이드바 + QStackedWidget, 6 NAV_ITEMS, 3초 refresh timer, WS + MQTT 워커 브리지, Ctrl+1..6 / F11 |

### 3.2 페이지 (`monitoring/app/pages/`)

| 페이지 | 파일 | 라인 |
|---|---|---|
| 대시보드 | `dashboard.py` | 314 |
| 공장 맵 | `map.py` | 113 |
| 생산 모니터링 | `production.py` | 235 |
| 생산 계획 | `schedule.py` | 529 |
| 품질 관리 | `quality.py` | 214 |
| 물류 관리 | `logistics.py` | 288 |

### 3.3 워커 / 위젯

| 워커 | 파일 | 역할 |
|---|---|---|
| API 클라이언트 | `monitoring/app/api_client.py` (493줄) | requests 기반 HTTP, `CASTING_DATA_MODE=fallback` 기본 (404 시 mock fallback) |
| WS 워커 | `monitoring/app/ws_worker.py` | websocket-client + QThread, 3초 자동 재연결 |
| MQTT 워커 | `monitoring/app/mqtt_worker.py` | paho-mqtt optional (`CASTING_MQTT_ENABLED=1`) |
| Mock | `monitoring/app/mock_data.py` | 404 시 폴백 데이터 |

**위젯 10개**: `monitoring/app/widgets/` — KpiCard, ConveyorCard, AmrCard, FactoryMap, WarehouseRack, Gauges, Charts, AlertWidgets, CameraView, DefectPanels, SorterDial

**도구**: `monitoring/app/tools/mqtt_simulator.py` — 브로커 시뮬레이터

## 4. ESP32 펌웨어 (`firmware/`)

| 스케치 | 파일 | 역할 |
|---|---|---|
| 메인 컨트롤러 v4.0.0 | `firmware/conveyor_controller/conveyor_controller.ino` (470줄) | L298N + TOF250×2 상태머신 (IDLE→RUNNING→STOPPED→POST_RUN→CLEARING), WiFi + MQTT, `vision/1/result` 구독 |
| 모터 테스트 | `firmware/motor_test/motor_test.ino` | L298N 단독 회전 테스트 |
| TOF 프로토콜 스캔 | `firmware/tof_protocol_scan/tof_protocol_scan.ino` | TOF250 프로토콜 판명용 (ASCII UART 9600) |
| I2C 스캔 | `firmware/i2c_scan/i2c_scan.ino` | I2C 주소 스캔 |

## 5. 운영 스크립트 (`scripts/`)

| 파일 | 역할 |
|---|---|
| `sync_confluence_facts.py` (373줄) | Confluence 22개 페이지 자동 동기화 (GET only). launchd 매일 09:07. macOS Keychain 토큰. CURATED 마커 보존. |
| `backend/scripts/*.sql` | DB 마이그레이션 SQL (상세는 2.4 참조) |
| `backend/scripts/migrate_sqlite_to_pg.py` | 일회성 데이터 이관 |

## 6. 문서 / 자산

| 경로 | 역할 |
|---|---|
| `docs/CONFLUENCE_FACTS.md` (1035줄) | Confluence 22개 페이지 전량 수집본 (launchd 자동 동기화) |
| `docs/architecture/` | 12개 컴포넌트 설계 HTML (Confluence V4 레이어 07~12 포함) |
| `docs/POSTGRES_MIGRATION.md` | PG 마이그레이션 기록 |
| `docs/DB_데이터_리스트.md`, `docs/GUI_페이지_리스트.md` | 한글 참조 문서 |
| `blender/factory_scene.py` | Blender Python 스크립트 → `public/factory-map2.glb` 생성 |
| `blender/*.step/*.stl` | CAD 원본 (MyCobot280 등) |
| `public/factory-map2.glb` | 공장 3D 에셋 |
| `.moai/project/` | MoAI 프로젝트 문서 (product.md, structure.md, tech.md, codemaps/) |
