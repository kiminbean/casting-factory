# 엔트리 포인트

> **Last updated**: 2026-04-09

## 1. 애플리케이션 진입점

| 계층 | 진입 파일 | 기동 명령 | 포트/주소 |
|---|---|---|---|
| Next.js dev | `src/app/layout.tsx` + `src/app/page.tsx` | `npm run dev` (`next dev -H 0.0.0.0`) | `0.0.0.0:3000` (LAN 노출) |
| Next.js prod | 동일 | `npm run build && npm start` | 3000 |
| 고객 포털 | `src/app/customer/layout.tsx` | Next 내부 라우트 `/customer` | 3000 |
| FastAPI | `backend/app/main.py:33` (`app = FastAPI(...)`) | `uvicorn app.main:app --host 127.0.0.1 --port 8000` | 8000 |
| FastAPI lifespan | `backend/app/main.py:17 lifespan()` | 앱 기동 시 자동 실행 | — |
| DB 초기화 | lifespan 내 `Base.metadata.create_all` + `seed_database(db)` | 자동 | — |
| WebSocket | `backend/app/routes/websocket.py:178 websocket_endpoint` | `/ws/dashboard` 경로 | 8000 |
| PyQt5 모니터링 | `monitoring/main.py` → `monitoring/app/main_window.py:MainWindow` | `cd monitoring && python main.py` | 데스크톱 앱 |
| PostgreSQL 16 | — | `brew services start postgresql@16` | 127.0.0.1:5432 + LAN 192.168.0.16:5432 |

## 2. 운영 스크립트 진입점

| 스크립트 | 파일 | 실행 방법 | 주기 |
|---|---|---|---|
| Confluence 동기화 | `scripts/sync_confluence_facts.py` | launchd or `python3 scripts/sync_confluence_facts.py [--dry-run\|--init-snapshot]` | 매일 09:07 (launchd) |
| launchd plist | `~/Library/LaunchAgents/com.casting-factory.confluence-sync.plist` | `launchctl load\|unload\|start <label>` | — |
| SQLite → PG 이관 | `backend/scripts/migrate_sqlite_to_pg.py` | `python scripts/migrate_sqlite_to_pg.py` | 일회성 (2026-04-09 완료) |
| Product 스키마 확장 | `backend/scripts/migrate_products_front_truth.sql` | `psql $DATABASE_URL -f ...` | 일회성 (멱등) |
| LoadClass 생성 | `backend/scripts/migrate_load_classes.sql` | `psql $DATABASE_URL -f ...` | 일회성 (멱등) |

## 3. REST API 엔드포인트 (31개 + 1 WS)

### 주문 (orders.py)

| Method | Path | 용도 |
|---|---|---|
| GET | `/api/orders` | 주문 목록 (created_at desc) |
| POST | `/api/orders` | 주문 생성 (409 on duplicate) |
| PATCH | `/api/orders/{order_id}` | 주문 부분 수정 |
| PATCH | `/api/orders/{order_id}/status` | 상태 변경 |
| GET | `/api/orders/{order_id}/details` | 품목 상세 목록 |
| POST | `/api/orders/{order_id}/details` | 품목 상세 추가 |

### 제품 마스터 (orders.py)

| Method | Path | 용도 |
|---|---|---|
| GET | `/api/products` | 제품 목록 (JSON 파싱) |
| GET | `/api/load-classes` | EN 124 하중 등급 6종 (display_order 순) |

### 생산 (production.py, schedule.py)

| Method | Path | 용도 |
|---|---|---|
| GET | `/api/production/stages` | 공정 단계 목록 |
| PATCH | `/api/production/stages/{stage_id}` | 공정 부분 업데이트 |
| GET | `/api/production/metrics` | 일별 생산 지표 |
| GET | `/api/production/equipment` | 설비 목록 |
| POST | `/api/production/schedule/calculate` | 7요소 우선순위 계산 |
| POST | `/api/production/schedule/start` | 생산 개시 + ProductionJob 생성 |
| GET | `/api/production/schedule/jobs` | ProductionJob 목록 |
| POST | `/api/production/schedule/priority-log` | 수동 우선순위 변경 로그 |
| GET | `/api/production/schedule/priority-log/{order_id}` | 변경 이력 |

### 품질 (quality.py)

| Method | Path | 용도 |
|---|---|---|
| GET | `/api/quality/inspections` | 검사 기록 (desc) |
| GET | `/api/quality/stats` | 합격/불량 집계 |
| GET | `/api/quality/standards` | 검사 기준 |
| GET | `/api/quality/sorter-logs` | 분류기 로그 |

### 물류 (logistics.py)

| Method | Path | 용도 |
|---|---|---|
| GET | `/api/logistics/tasks` | 이송 작업 (desc) |
| POST | `/api/logistics/tasks` | 이송 작업 생성 |
| PATCH | `/api/logistics/tasks/{task_id}/status` | 상태 + assigned_robot_id |
| GET | `/api/logistics/warehouse` | 창고 랙 목록 |
| GET | `/api/logistics/outbound-orders` | 출고 지시서 |
| PATCH | `/api/logistics/outbound-orders/{order_id}/complete` | 완료 처리 |

### 알림 / 대시보드 (alerts.py)

| Method | Path | 용도 |
|---|---|---|
| GET | `/api/alerts` | 알림 목록 (desc) |
| PATCH | `/api/alerts/{alert_id}/acknowledge` | 확인 처리 |
| GET | `/api/dashboard/stats` | 대시보드 종합 통계 |

### 시스템

| Method | Path | 용도 |
|---|---|---|
| GET | `/health` | 헬스체크 |
| WS | `/ws/dashboard` | 실시간 브로드캐스트 (5초 tick) |

## 4. 웹 라우트 (Next.js)

| Path | 파일 | 인증 | 사용자 |
|---|---|---|---|
| `/` | `src/app/page.tsx` | 없음 | 관리자 |
| `/orders` | `src/app/orders/page.tsx` | 없음 | 관리자 (주문 관리) |
| `/quality` | `src/app/quality/page.tsx` | 없음 | 관리자 (품질 관리) |
| `/production` | `src/app/production/page.tsx` | 없음 | 레거시 (Sidebar 미링크) |
| `/customer` | `src/app/customer/page.tsx` | 없음 | 고객 (발주 포털) |
| `/customer/orders` | `src/app/customer/orders/page.tsx` | 없음 | 고객 (주문 조회) |

## 5. 빌드/개발 명령

### 프론트엔드

```bash
npm install
npm run dev      # next dev -H 0.0.0.0 → 0.0.0.0:3000
npm run build    # 프로덕션 빌드
npm start        # 프로덕션 서버
npm run lint     # ESLint 9
```

### 백엔드

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 모니터링

```bash
cd monitoring
python main.py
# 환경변수:
#   CASTING_API_HOST=192.168.0.16:8000
#   CASTING_DATA_MODE=normal|fallback|mock_only  (기본: fallback)
#   CASTING_MQTT_ENABLED=1  (optional)
```

### 펌웨어

```bash
cd firmware/conveyor_controller
arduino-cli compile --fqbn esp32:esp32:esp32 .
arduino-cli upload --fqbn esp32:esp32:esp32 -p /dev/cu.usbserial-0001 .
```

## 6. DBeaver 접속

```
Type     : PostgreSQL
Host     : 192.168.0.16   (LAN) 또는 127.0.0.1 (로컬)
Port     : 5432
Database : casting_factory_dev
User     : casting_factory
Password : backend/.env.local 에서 확인 (git ignored)
```
