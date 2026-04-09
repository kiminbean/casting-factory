# 데이터 흐름

> **Last updated**: 2026-04-09 (PG 전환 + api.ts 활성화 상태 반영)

## 1. 핵심 요청 흐름: 관리자 주문 관리

```
[관리자 브라우저 /orders]
 │   page.tsx (962줄): 주문 탭 클릭, 상세 조회, 생산 승인
 │
 ├── (1) 주문 목록 로드
 │    └─> useEffect → fetchOrders() [src/lib/api.ts]
 │         └─> apiFetch<Order[]>("/api/orders")
 │              └─> fetch(`${API_BASE}/api/orders`)
 │                    │  API_BASE = ""  (next.config.ts rewrite 경유)
 │                    ▼
 │              [Next.js rewrites: /api/:path* → http://localhost:8000/api/:path*]
 │                    ▼
 │              [FastAPI /api/orders]
 │                    │  routes/orders.py:29 list_orders(db)
 │                    ▼
 │              db.query(Order).order_by(Order.created_at.desc()).all()
 │                    │  SQLAlchemy → PostgreSQL 16
 │                    ▼
 │              [PostgreSQL 16: orders 테이블]
 │                    ▲
 │                    │  OrderResponse (Pydantic)
 │                    │  JSON (snake_case)
 │                    ▲
 │              [convertKeys 재귀 snake→camel] in api.ts
 │              [Order[] 반환 (camelCase)]
 │                    ▲
 │        setOrders(data) → 리스트 렌더
 │
 ├── (2) 주문 상태 변경 (승인)
 │    └─> updateOrderStatus(id, "approved")
 │         └─> PATCH /api/orders/{id}/status  (body: { status: "approved" })
 │              └─> orders.py:49 update_order_status
 │                    └─> 상태 갱신 + db.commit()
 │
 └── (3) 생산 승인 → 생산 개시
      └─> startProduction([order_ids])
           └─> POST /api/production/schedule/start
                └─> schedule.py:316
                     ├─> calculate 우선순위 (7요소)
                     ├─> INSERT ProductionJob
                     ├─> UPDATE Order.status = "in_production"
                     └─> return ProductionJob[]
```

## 2. 고객 발주 흐름 (api.ts 우회)

```
[고객 브라우저 /customer]
 │   page.tsx (1222줄): 4단계 발주 폼
 │   ├─ Step 1: 제품 선택 (하드코딩 PRODUCTS 배열, D450/D600/D800/GRATING)
 │   ├─ Step 2: 사양 선택 (diameter/thickness/material/loadClass/postProcessing/quantity)
 │   ├─ Step 3: 고객 정보 (company/name/phone/email/address)
 │   └─ Step 4: 확인 → 제출
 │
 ├── (1) 주문 생성  (직접 fetch, api.ts 미경유)
 │    └─> fetch("/api/orders", { method: "POST", body: JSON.stringify({snake_case}) })
 │         ▼
 │    [FastAPI POST /api/orders] orders.py:36 create_order
 │         ├─ OrderCreate Pydantic 검증
 │         ├─ 중복 체크 (id 조회) → 있으면 409
 │         └─ db.add(Order); db.commit(); db.refresh()
 │
 └── (2) 품목 상세 추가
      └─> fetch(`/api/orders/${orderId}/details`, { method: "POST", body: {...} })
           ▼
      [orders.py:103 add_order_detail]
           └─> OrderDetail INSERT
```

## 3. PyQt5 모니터링 데이터 수집 흐름

```
[Factory PC: monitoring/main.py]
 │
 ├── 초기화
 │    ├─> MainWindow 생성
 │    ├─> ApiClient 인스턴스화 (CASTING_API_HOST=192.168.0.16:8000)
 │    ├─> WSWorker QThread 시작 → ws://192.168.0.16:8000/ws/dashboard
 │    └─> MqttWorker QThread 시작 (optional)
 │
 ├── 3초 주기 refresh
 │    ├─> pages/dashboard: api.get_dashboard_stats(), api.get_alerts()
 │    ├─> pages/production: api.get_process_stages(), api.get_equipment()
 │    ├─> pages/quality: api.get_quality_stats(), api.get_inspections()
 │    ├─> pages/logistics: api.get_transport_tasks(), api.get_warehouse_racks()
 │    ├─> pages/schedule: api.get_production_jobs(), api.calculate_priority()
 │    │    │   ※ PyQt 은 직접 DB 접근하지 않고 모두 HTTP 경유
 │    │    ▼
 │    │   [FastAPI /api/*]
 │    │    │   404 or 빈 응답 시
 │    │    ▼
 │    │   [ApiClient fallback → mock_data.py]
 │    │    │
 │    │    ▼
 │    │   페이지 위젯 업데이트
 │
 ├── WebSocket 메시지 수신 (서버 push)
 │    └─> ws_worker.message_received signal
 │         └─> MainWindow._on_ws_message
 │              └─> 페이지별 handle_ws_message() 호출
 │                   └─> {dashboard_stats, production_update, alert_update}
 │
 └── MQTT 메시지 (optional)
      └─> vision/1/result → 품질 검사 결과
      └─> amr/status → AMR 위치·상태
```

## 4. 실시간 WebSocket 흐름

```
[FastAPI backend/app/routes/websocket.py]
 │
 ├── 연결 수립 (/ws/dashboard)
 │    ├─> ConnectionManager.connect(ws)
 │    ├─> 즉시 송신: dashboard_stats + alert_update (개인 메시지)
 │    └─> while True: asyncio.sleep(5)
 │         ├─ 매 tick (5초):
 │         │   └─ _get_production_update()
 │         │        ├─ running stage.progress += random
 │         │        ├─ temperature += random
 │         │        ├─ db.commit()  ← 서버가 DB 를 직접 mutate
 │         │        └─ broadcast("production_update")
 │         ├─ tick % 2 (10초):
 │         │   └─ broadcast("dashboard_stats")
 │         └─ tick % 3 (15초):
 │             └─ broadcast("alert_update")
 │
 ├── 구독자 (PyQt5 모니터링):
 │    └─ ws_worker.py → QThread 안에서 websocket-client run_forever
 │         ├─ on_message → pyqtSignal(dict)
 │         └─ MainWindow slot 에서 페이지 분배
 │
 └── 재연결:
      └─ 끊기면 3초 대기 후 재시도
```

## 5. DB 초기화 흐름 (앱 기동)

```
uvicorn app.main:app
 │
 ├── backend/app/main.py import
 │    └─> from app.database import Base, SessionLocal, engine
 │         └─> _load_env_local() 호출
 │              ├─> backend/.env.local 읽기
 │              └─> DATABASE_URL 환경변수 주입 (이미 있으면 스킵)
 │         └─> DATABASE_URL 확정 → engine 생성
 │              ├─ postgresql+psycopg:// → PG engine (pool_size=10)
 │              └─ sqlite:/// → SQLite engine (check_same_thread=False)
 │
 ├── lifespan() 시작
 │    ├─> if DATABASE_URL.startswith("sqlite") and os.path.exists(_DB_PATH):
 │    │     └─> engine.dispose() + os.remove(casting_factory.db)  [개발 편의]
 │    ├─> Base.metadata.create_all(bind=engine)  [테이블 없으면 생성]
 │    └─> seed_database(db)
 │         ├─> _seed_orders         (count>0 skip)
 │         ├─> _seed_order_details  (count>0 skip)
 │         ├─> _seed_products       (4개: D450/D600/D800/GRATING)
 │         ├─> _seed_load_classes   (6개: A15~F900)
 │         ├─> _seed_process_stages (8개)
 │         ├─> _seed_equipment      (12개)
 │         ├─> _seed_transport_tasks
 │         ├─> _seed_warehouse_racks (24개)
 │         ├─> _seed_outbound_orders
 │         ├─> _seed_inspection_records  (30개)
 │         ├─> _seed_inspection_standards
 │         ├─> _seed_sorter_logs
 │         ├─> _seed_alerts
 │         └─> _seed_production_metrics
 │
 └── uvicorn 요청 수신 준비 완료
```

## 6. Confluence 문서 동기화 흐름 (launchd)

```
[매일 09:07, launchd: com.casting-factory.confluence-sync]
 │
 ├── scripts/sync_confluence_facts.py 실행
 │    ├─> macOS Keychain → Atlassian API token 조회
 │    │    (service: casting-factory-atlassian, account: kiminbean@gmail.com)
 │    ├─> docs/CONFLUENCE_FACTS.md 파싱 → 22개 page_id 추출
 │    ├─> docs/.confluence_snapshot.json 읽기 (버전 캐시)
 │    │
 │    └─> 각 page_id 에 대해:
 │         ├─> GET /wiki/api/v2/pages/{id}?body-format=storage
 │         ├─> version 비교 (캐시와 동일하면 skip)
 │         ├─> 변경 감지 시:
 │         │    ├─> HTML (storage) → Markdown 변환 (stdlib HTMLParser)
 │         │    ├─> CURATED 마커 블록 추출 보존
 │         │    └─> CONFLUENCE_FACTS.md 섹션 in-place 덮어쓰기
 │         └─> 신규 snapshot 저장
 │
 ├── 변경 감지 건수 > 0 이면:
 │    ├─> git add docs/CONFLUENCE_FACTS.md
 │    └─> git commit -m "chore(docs): Confluence 팩트 자동 동기화 (날짜)"
 │
 └── 로그: logs/confluence_sync.log (gitignored)
```

## 7. 제품 + 하중 등급 조회 흐름 (DBeaver)

```
[DBeaver: 192.168.0.16:5432]
 │
 ├── SELECT SQL 실행 (예: 제품 × 하중 JOIN)
 │    SELECT p.id, p.name, p.load_class_range,
 │           lc_min.load_tons AS min_tons,
 │           lc_max.load_tons AS max_tons
 │    FROM products p
 │    LEFT JOIN load_classes lc_min
 │      ON lc_min.code = split_part(p.load_class_range, ' ~ ', 1)
 │    LEFT JOIN load_classes lc_max
 │      ON lc_max.code = split_part(p.load_class_range, ' ~ ', 2);
 │
 └── 결과: 4개 제품 × (min_tons, max_tons, use_case)
```

## 8. 특이 사항 / 주의점

- **프론트는 PG 에 직접 접근하지 않음**. 반드시 FastAPI 경유.
- **WebSocket 서버가 DB 를 직접 mutate**: `_get_production_update()` 이 running stage 데이터를 시뮬레이션으로 증분. 실 장비 연동이 아님.
- **고객 포털만 api.ts 우회**: `customer/page.tsx` 의 fetch 호출 2곳이 직접 `/api/orders`, `/api/orders/{id}/details` 호출.
- **mock fallback**: PyQt5 ApiClient 가 404 응답을 `_dead_paths` 에 캐시해 재시도 방지 + mock_data.py 로 fallback. 이것은 PC 가 비연결 상태에서도 UI 가 죽지 않도록 한 것.
- **lifespan의 SQLite 파일 삭제 로직**: `DATABASE_URL.startswith("sqlite")` 가드로 PG 환경에서는 실행되지 않음. PG 데이터 유실 위험 없음.
- **NEXT_PUBLIC_API_URL 이 비어있으면** (기본) 동일 origin 으로 가고 `next.config.ts` 의 `rewrites()` 가 `/api/*` 를 `http://localhost:8000/api/*` 로 프록시함. LAN 공유 시에는 브라우저가 192.168.0.16:3000 → rewrite → 127.0.0.1:8000 으로 도달.
