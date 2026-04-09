# 의존성 그래프

> **Last updated**: 2026-04-09

## 1. 외부 의존성

### 1.1 프론트엔드 (`package.json` v3.4.0)

| 패키지 | 버전 | 용도 |
|---|---|---|
| next | 16.2.1 | App Router 프레임워크 |
| react / react-dom | 19.2.4 | UI 런타임 |
| three | ^0.183.2 | WebGL 3D 엔진 |
| @react-three/fiber | ^9.5.0 | React + Three.js 바인딩 |
| @react-three/drei | ^10.7.7 | R3F 헬퍼 |
| @types/three | ^0.183.1 | Three.js 타입 |
| recharts | ^3.8.1 | SVG 차트 |
| lucide-react | ^1.7.0 | 아이콘 SVG |
| clsx | ^2.1.1 | className 유틸 |
| date-fns | ^4.1.0 | 날짜 포맷/연산 |
| tailwindcss | ^4 | 유틸리티 CSS |
| @tailwindcss/postcss | ^4 | PostCSS 통합 |
| typescript | ^5 | 타입 시스템 (dev) |
| eslint / eslint-config-next | 9 / 16.2.1 | 린트 (dev) |

### 1.2 백엔드 (`backend/requirements.txt`)

| 패키지 | 버전 | 용도 | 실제 사용 |
|---|---|---|---|
| fastapi | 0.115.0 | 웹 프레임워크 | ✓ |
| uvicorn[standard] | 0.30.0 | ASGI 서버 | ✓ |
| sqlalchemy | 2.0.35 | ORM | ✓ |
| pydantic | 2.9.0 | 데이터 검증 | ✓ |
| python-multipart | 0.0.9 | form-data 파싱 | ✓ |
| websockets | 13.0 | WebSocket (uvicorn 서브덱) | ✓ |
| psycopg[binary] | 3.2.3 | PostgreSQL 드라이버 (sync) | ✓ |
| asyncpg | 0.29.0 | PG async 드라이버 | 미사용 (예약) |
| alembic | 1.13.3 | 마이그레이션 | 미사용 (SQL 파일로 대체) |
| asyncio-mqtt | 0.16.2 | MQTT 클라이언트 | 미사용 (예약) |
| redis | 5.1.1 | 캐시 | 미사용 (예약) |

### 1.3 모니터링 (PyQt5, 추정)

- PyQt5
- requests
- websocket-client
- paho-mqtt (optional, `CASTING_MQTT_ENABLED=1` 시 활성화)

### 1.4 펌웨어

- Arduino ESP32 core 3.3.7
- ESP32MQTTClient 라이브러리
- Taidacent TOF250 센서 (ASCII UART 9600)

## 2. 내부 모듈 의존성

### 2.1 프론트 (`src/`)

```
app/layout.tsx (RootLayout)
 └─> components/AdminShell.tsx
      ├─> components/Header.tsx
      ├─> components/Sidebar.tsx
      └─> (children: 각 route)

app/page.tsx (관리자 포털 허브)
 └─> lucide-react + lib/utils

app/orders/page.tsx (962줄)
 ├─> lib/api.ts (fetchOrders, updateOrderStatus, startProduction, calculatePriority)
 ├─> lib/types.ts (Order, OrderStatus, PriorityResult 등)
 ├─> lib/utils.ts (orderStatusMap, formatDate, formatCurrency)
 └─> lucide-react

app/quality/page.tsx (610줄)
 ├─> lib/api.ts (fetchInspections, fetchQualityStats, fetchInspectionStandards, fetchSorterLogs)
 ├─> lib/types.ts
 ├─> lib/utils.ts
 └─> next/dynamic (recharts SSR 비활성화)

app/production/page.tsx (928줄)
 ├─> lib/api.ts (fetchProcessStages, fetchProductionMetrics, fetchEquipment)
 └─> lib/types.ts

app/customer/layout.tsx (passthrough HTML)
 └─> app/customer/page.tsx (1222줄)
      ├─> (api.ts 우회) fetch POST /api/orders, /details 직접 호출
      ├─> 로컬 interface Product + PRODUCTS 하드코딩
      └─> POST_PROCESSING_OPTIONS 하드코딩

app/customer/orders/page.tsx (439줄)
 ├─> lib/api.ts (fetchOrders, fetchOrderDetails)
 └─> lib/types.ts, lib/utils.ts
```

### 2.2 백엔드 (`backend/app/`)

```
main.py
 ├─> database.py (DATABASE_URL, Base, SessionLocal, engine)
 ├─> seed.py
 │    └─> models/models.py (전체 모델 import)
 └─> routes/
      ├─> orders.py
      │    ├─> database.get_db
      │    ├─> models/models.py (Order, OrderDetail, Product, LoadClass)
      │    └─> schemas/schemas.py (OrderCreate/Response, ProductResponse, LoadClassResponse)
      ├─> production.py
      │    ├─> database.get_db
      │    ├─> models (ProcessStage, ProductionMetric, Equipment)
      │    └─> schemas
      ├─> schedule.py
      │    ├─> database.get_db
      │    ├─> models (Order, OrderDetail, ProductionJob, PriorityChangeLog, Equipment)
      │    └─> 7요소 가중 우선순위 엔진 (순수 Python)
      ├─> quality.py
      │    ├─> models (InspectionRecord, InspectionStandard, SorterLog)
      │    └─> schemas
      ├─> logistics.py
      │    ├─> models (TransportTask, WarehouseRack, OutboundOrder)
      │    └─> schemas
      ├─> alerts.py
      │    ├─> models (Alert + 기타 대시보드용)
      │    └─> schemas
      └─> websocket.py
           ├─> database.SessionLocal (Depends 미사용, 직접 세션)
           └─> models (ProcessStage, ProductionMetric, Alert)
```

**순환 의존성 없음**. `database` → `models` → `routes` → `main` 단방향.

### 2.3 모니터링 (`monitoring/app/`)

```
main.py
 └─> app/main_window.py (MainWindow)
      ├─> app/api_client.py (HTTP 요청)
      ├─> app/ws_worker.py (WebSocket QThread)
      ├─> app/mqtt_worker.py (MQTT QThread, optional)
      ├─> app/pages/dashboard.py  ─┐
      ├─> app/pages/map.py          │  모두 main_window 의 refresh timer 와
      ├─> app/pages/production.py   ├─ WS broadcast 를 받음
      ├─> app/pages/schedule.py     │  (handle_ws_message, handle_mqtt_message 훅)
      ├─> app/pages/quality.py      │
      ├─> app/pages/logistics.py  ──┘
      └─> app/widgets/* (KpiCard, FactoryMap, ...)
```

**주의**: `pages/schedule.py` 가 `pages/dashboard.KpiCard` 를 직접 import (페이지 간 얕은 결합). 실제 DB 접근은 없음 — 모두 `ApiClient` 로 HTTP 경유.

## 3. 런타임 경계 (서비스 간 통신)

```
┌─────────────────┐   HTTP (rewrite)    ┌──────────────┐    SQLAlchemy    ┌──────────────┐
│ Next.js (3000)  │ ──────────────────> │ FastAPI      │ ───────────────> │ PostgreSQL   │
│                 │ <──────────────────  │ (8000)       │ <─────────────── │ 16 (5432)    │
└─────────────────┘       JSON           └──────┬───────┘                  └──────────────┘
                                                 │
                                                 │ WebSocket broadcast
                                                 │ (5초 tick, dashboard_stats/production_update/alert_update)
                                                 ▼
                                         ┌──────────────┐
                                         │ PyQt5        │ (requests HTTP + websocket-client WS)
                                         │ monitoring   │
                                         │ (데스크톱)   │
                                         └──────┬───────┘
                                                 │
                                                 │ MQTT (optional, 192.168.0.16:1883)
                                                 ▼
                                         ┌──────────────┐
                                         │ ESP32        │ WiFi + ESP32MQTTClient
                                         │ conveyor     │ vision/1/result 구독
                                         │ firmware     │
                                         └──────────────┘
```

## 4. 운영 파이프라인

```
launchd (매일 09:07)
 └─> scripts/sync_confluence_facts.py
      ├─> macOS Keychain (Atlassian token)
      ├─> Confluence REST API v2 GET
      ├─> HTML → Markdown 변환 (stdlib HTMLParser)
      ├─> docs/CONFLUENCE_FACTS.md 섹션 덮어쓰기 (CURATED 블록 보존)
      └─> git add + commit (변경 감지 시)

blender/factory_scene.py (오프라인, 수동)
 └─> public/factory-map2.glb
      └─> src/components/FactoryMap3D.tsx 가 로드
```

## 5. 특이사항

- **고객 포털(`/customer`)이 `api.ts` 우회**: `fetch("/api/orders", ...)` 직접 호출. 다른 모든 프론트 페이지는 `apiFetch<T>()` 경유.
- **`lib/types.ts` 의 Product 구식**: 백엔드 확장 필드 미반영. 신규 `fetchProducts` / `fetchLoadClasses` 함수도 아직 추가되지 않음.
- **`requirements.txt` 의 `asyncpg/asyncio-mqtt/redis/alembic` 는 예약**: 현재 코드 내 import 없음. 향후 확장 대비.
- **`CORS allow_origins=["*"] + allow_credentials=True`**: 브라우저 표준상 동작 안 함. 개발 전용 설정.
- **FK 제약 최소화**: 2개만 (`order_details.order_id`, `production_jobs.order_id`). 나머지 참조는 문자열 soft-link.
- **WebSocket 이 DB 를 직접 mutate**: `_get_production_update()` 가 running stage 의 progress/temperature 를 랜덤 증분 후 `db.commit()`. 시뮬레이션 기반 데모 아키텍처.
