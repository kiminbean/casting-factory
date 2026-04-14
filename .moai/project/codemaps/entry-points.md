# 엔트리 포인트

> **Last updated**: 2026-04-13

## 1. 애플리케이션 진입점

### 1.1 Next.js Web App

| 진입점 | 파일 | 실행 방법 |
|--------|------|----------|
| 루트 레이아웃 | `src/app/layout.tsx` | `npm run dev` → localhost:3000 |
| 대시보드 | `src/app/page.tsx` | `/` |
| 주문 관리 | `src/app/orders/page.tsx` | `/orders` |
| 생산 모니터링 | `src/app/production/page.tsx` | `/production` |
| 품질 검사 | `src/app/quality/page.tsx` | `/quality` |
| 관리자 설정 | `src/app/admin/page.tsx` | `/admin` |
| 관리자 로그인 | `src/app/admin/login/page.tsx` | `/admin/login` |
| 고객 발주 | `src/app/customer/page.tsx` | `/customer` |
| 주문 조회 | `src/app/customer/lookup/page.tsx` | `/customer/lookup` |
| 내 주문 목록 | `src/app/customer/orders/page.tsx` | `/customer/orders` |

### 1.2 FastAPI Backend

| 진입점 | 파일 | 실행 방법 |
|--------|------|----------|
| FastAPI app | `backend/app/main.py:33` | `uvicorn app.main:app --port 8000 --reload` |
| Health check | `backend/app/main.py:63` | `GET /health` |

### 1.3 PyQt5 Monitoring App

| 진입점 | 파일 | 실행 방법 |
|--------|------|----------|
| QApplication | `monitoring/main.py` | `python monitoring/main.py` |
| MainWindow | `monitoring/app/main_window.py:46` | MainWindow 클래스 |

### 1.4 Scripts

| 진입점 | 파일 | 실행 방법 |
|--------|------|----------|
| Confluence 동기화 | `scripts/sync_confluence_facts.py` | `python3 scripts/sync_confluence_facts.py` |

## 2. REST API 엔드포인트 전체 목록 (30개)

### 2.1 Orders (`/api/orders`) — 6개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/orders` | `list_orders()` | orders.py:30 |
| POST | `/api/orders` | `create_order()` | orders.py:46 |
| PATCH | `/api/orders/{id}/status` | `update_order_status()` | orders.py:59 |
| PATCH | `/api/orders/{id}` | `update_order()` | orders.py:83 |
| GET | `/api/orders/{id}/details` | `get_order_details()` | orders.py:105 |
| POST | `/api/orders/{id}/details` | `add_order_detail()` | orders.py:120 |

### 2.2 Products (`/api/products`) — 1개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/products` | `list_products()` | orders.py:144 |

### 2.3 Load Classes (`/api/load-classes`) — 1개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/load-classes` | `list_load_classes()` | orders.py:155 |

### 2.4 Production (`/api/production`) — 4개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/production/stages` | `list_stages()` | production.py:30 |
| PATCH | `/api/production/stages/{id}` | `update_stage()` | production.py:37 |
| GET | `/api/production/metrics` | `list_metrics()` | production.py:57 |
| GET | `/api/production/equipment` | `list_equipment()` | production.py:64 |

### 2.5 Quality (`/api/quality`) — 4개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/quality/inspections` | `list_inspections()` | quality.py:18 |
| GET | `/api/quality/stats` | `quality_stats()` | quality.py:29 |
| GET | `/api/quality/standards` | `list_standards()` | quality.py:70 |
| GET | `/api/quality/sorter-logs` | `list_sorter_logs()` | quality.py:77 |

### 2.6 Logistics (`/api/logistics`) — 6개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/logistics/tasks` | `list_tasks()` | logistics.py:23 |
| POST | `/api/logistics/tasks` | `create_task()` | logistics.py:34 |
| PATCH | `/api/logistics/tasks/{id}/status` | `update_task_status()` | logistics.py:49 |
| GET | `/api/logistics/warehouse` | `list_warehouse()` | logistics.py:73 |
| GET | `/api/logistics/outbound-orders` | `list_outbound()` | logistics.py:84 |
| PATCH | `/api/logistics/outbound-orders/{id}/complete` | `complete_outbound()` | logistics.py:95 |

### 2.7 Alerts & Dashboard (`/api`) — 3개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| GET | `/api/alerts` | `list_alerts()` | alerts.py:17 |
| PATCH | `/api/alerts/{id}/acknowledge` | `acknowledge_alert()` | alerts.py:24 |
| GET | `/api/dashboard/stats` | `dashboard_stats()` | alerts.py:40 |

### 2.8 Schedule (`/api/production/schedule`) — 5개

| Method | Path | 함수 | 파일:라인 |
|--------|------|------|----------|
| POST | `/api/production/schedule/calculate` | `calculate_priority()` | schedule.py:217 |
| POST | `/api/production/schedule/start` | `start_production()` | schedule.py:316 |
| GET | `/api/production/schedule/jobs` | `list_jobs()` | schedule.py:384 |
| POST | `/api/production/schedule/priority-log` | `create_log()` | schedule.py:391 |
| GET | `/api/production/schedule/priority-log/{id}` | `get_log()` | schedule.py:411 |

### 2.9 WebSocket — 1개

| Protocol | Path | 파일:라인 |
|----------|------|----------|
| WS | `/ws/dashboard` | websocket.py:178 |

## 3. npm Scripts

| Script | 명령 | 용도 |
|--------|------|------|
| `dev` | `next dev -H 0.0.0.0` | 개발 서버 (LAN 접속 허용) |
| `build` | `next build` | 프로덕션 빌드 |
| `start` | `next start` | 프로덕션 실행 |
| `lint` | `eslint` | 린팅 |
