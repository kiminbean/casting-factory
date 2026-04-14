# 프로젝트 구조

> **Last updated**: 2026-04-09

## 아키텍처 패턴

**4-runtime 모노레포**: Next.js 웹 + FastAPI 백엔드 + PyQt5 Factory PC 앱 + ESP32 펌웨어가 동일 저장소에 공존. 각 런타임은 독립 배포 단위이며, 백엔드 HTTP / WebSocket / MQTT 를 통해 통신.

## 전체 디렉터리 트리

```
casting-factory/
├── AGENTS.md                       # "Next.js 16 은 네가 아는 Next.js가 아니다" 경고
├── CLAUDE.md                       # @AGENTS.md + Confluence Facts Index
├── README.md
├── package.json                    # v3.4.0, Next 16.2.1 / React 19.2.4
├── next.config.ts                  # allowedDevOrigins, /api 리라이트 → :8000
├── tsconfig.json / eslint.config.mjs / postcss.config.mjs
│
├── src/                            # Next.js 16 App Router 프론트엔드
│   ├── app/
│   │   ├── layout.tsx              # RootLayout + AdminShell 래핑
│   │   ├── page.tsx                # 관리자 포털 허브 (카드 2개)
│   │   ├── globals.css
│   │   ├── customer/               # 고객 전용 영역 (별도 layout.tsx)
│   │   │   ├── layout.tsx          # 자체 HTML/헤더/푸터, AdminShell 패스스루
│   │   │   ├── page.tsx (1222줄)   # 4단계 발주 폼 + fetch POST
│   │   │   └── orders/page.tsx     # 주문 조회 타임라인
│   │   ├── orders/page.tsx (962줄) # 관리자 주문 관리 + 생산 승인
│   │   ├── quality/page.tsx (610줄)# 관리자 품질 관리
│   │   └── production/page.tsx     # (Sidebar 미링크, 직접 URL 전용)
│   ├── components/
│   │   ├── AdminShell.tsx          # pathname.startsWith("/customer") → 패스스루
│   │   ├── Header.tsx              # 상단 타이틀 맵, 1초 시계, 알림 뱃지
│   │   ├── Sidebar.tsx             # 관리자 네비 (주문/품질 2개 링크)
│   │   ├── FactoryMap.tsx (1485줄) # 2D 공장 맵
│   │   ├── FactoryMap3D.tsx        # Three.js 3D 뷰어
│   │   ├── FactoryMap3DCanvas.tsx  # R3F Canvas 래퍼
│   │   ├── FactoryMapEditor.tsx    # 3D 배치 편집
│   │   └── charts/                 # 4개 recharts 차트
│   └── lib/
│       ├── api.ts                  # fetch 래퍼 + snake→camel + 20+ 함수
│       ├── types.ts (362줄)        # 전체 도메인 타입
│       ├── utils.ts                # 상태 라벨/색상 맵, 포맷터
│       └── mock-data.ts (575줄)    # 구 mock 데이터 (일부 레거시)
│
├── backend/                        # 두 서비스 분리: Interface(FastAPI) + Management(gRPC)
│   ├── management/                 # ★ V6 신규: Management Service (gRPC :50051)
│   │   ├── server.py               # gRPC 서버 진입점
│   │   ├── proto/management.proto  # API 계약 (Protocol Buffers)
│   │   ├── services/               # Task Mgr / Allocator / Traffic / Executor / Monitor
│   │   ├── requirements.txt        # grpcio, grpcio-tools, protobuf
│   │   ├── Makefile                # `make proto`, `make run`
│   │   └── README.md
│   ├── .env.local                  # DATABASE_URL (gitignored, 600 권한). PG 필수.
│   ├── requirements.txt            # fastapi/sqlalchemy/psycopg/alembic/asyncpg/redis/asyncio-mqtt
│   ├── venv/                       # Python 가상환경
│   ├── app/
│   │   ├── main.py                 # FastAPI 앱, lifespan, 8 라우터 등록
│   │   ├── database.py             # engine, _load_env_local(), SessionLocal, get_db
│   │   ├── seed.py (457줄)         # 14개 _seed_* (count>0 skip)
│   │   ├── models/
│   │   │   └── models.py           # 17개 ORM 클래스 (Product, LoadClass, Order 등)
│   │   ├── schemas/
│   │   │   └── schemas.py (615줄)  # Pydantic v2, ProductResponse.from_orm_model
│   │   └── routes/
│   │       ├── orders.py           # router + products_router + load_classes_router
│   │       ├── production.py       # /api/production stages/metrics/equipment
│   │       ├── quality.py          # /api/quality inspections/stats/standards/sorter
│   │       ├── logistics.py        # /api/logistics tasks/warehouse/outbound
│   │       ├── alerts.py           # /api alerts + /api/dashboard/stats
│   │       ├── schedule.py (420줄) # 7요소 가중 우선순위 엔진
│   │       └── websocket.py        # /ws/dashboard 5초 tick 브로드캐스트
│   └── scripts/
│       ├── migrate_products_front_truth.sql  # Product 스키마 확장 + PRD-*→D*
│       └── migrate_load_classes.sql          # EN 124 하중 등급 6개
│
├── monitoring/                     # PyQt5 Factory PC 앱 (Python 3.12)
│   ├── main.py                     # QApplication 진입점
│   ├── config.py                   # CASTING_API_HOST 기본값
│   ├── scripts/gen_proto.sh        # ★ V6: backend/management/proto → app/generated 컴파일
│   └── app/
│       ├── main_window.py          # MainWindow, 6 NAV_ITEMS, WS/Alert/Item 워커 브리지
│       ├── api_client.py (493줄)   # HTTP + 404 캐시 + mock fallback (잔여 조회용)
│       ├── ws_worker.py            # websocket-client (V6: CASTING_WS_ENABLED=0 기본 비활성)
│       ├── mqtt_worker.py          # paho-mqtt (optional)
│       ├── mock_data.py            # 백엔드 404 시 폴백
│       ├── management_client.py    # ★ V6: gRPC :50051 클라이언트 (StartProduction/ListItems/Watch*)
│       ├── generated/              # ★ V6: protoc 산출물 (management_pb2*.py)
│       ├── workers/                # ★ V6 신규 QThread 워커
│       │   ├── item_stream_worker.py    # WatchItems gRPC stream
│       │   └── alert_stream_worker.py   # WatchAlerts gRPC stream → 토스트
│       ├── pages/                  # 6 페이지 (dashboard/map/production/
│       │                           #          schedule/quality/logistics)
│       ├── widgets/                # 10개 (Kpi/Conveyor/Amr/FactoryMap/
│       │                           #      WarehouseRack/Gauges/Charts/
│       │                           #      Alert/Camera/Defect/SorterDial)
│       └── tools/
│           └── mqtt_simulator.py   # 브로커 시뮬레이터 (개발용)
│
├── firmware/                       # ESP32 Arduino
│   ├── conveyor_controller/        # v4.0.0 MQTT 연동
│   │   ├── conveyor_controller.ino (470줄)
│   │   ├── config.h / config.example.h
│   │   ├── MQTT_SETUP.md
│   │   └── wiring_diagram.{html,svg,png}
│   ├── motor_test/                 # L298N 단독 테스트
│   ├── tof_protocol_scan/          # TOF250 프로토콜 판명 (ASCII UART 9600)
│   └── i2c_scan/                   # I2C 스캔
│
├── scripts/                        # 루트 운영 스크립트
│   └── sync_confluence_facts.py    # launchd 매일 09:07, READ-ONLY, 자동 git commit
│
├── docs/                           # 프로젝트 문서
│   ├── CONFLUENCE_FACTS.md (1035줄)# Confluence 22 페이지 자동 동기화
│   ├── .confluence_snapshot.json   # 버전 캐시 (gitignored)
│   ├── POSTGRES_MIGRATION.md
│   ├── DB_데이터_리스트.md
│   ├── GUI_페이지_리스트.md
│   ├── architecture/               # 12개 컴포넌트 설계 HTML (Confluence V4)
│   ├── system_overview.html
│   ├── architecture.html
│   ├── task_manager_summary.html
│   ├── task_allocator_summary.html
│   ├── fleet_traffic_summary.html
│   ├── fleet_traffic_management.html
│   └── GUI_Confluence_Wiki.md
│
├── blender/                        # 3D 에셋 파이프라인
│   ├── factory_scene.py            # Blender Python → public/factory-map2.glb
│   ├── MyCobot280.step / .stl      # CAD 원본
│   └── 기타 CAD 자산
│
├── public/                         # Next.js 정적 에셋
│   ├── factory-map2.glb            # 공장 3D 모델
│   └── 기타 아이콘/이미지
│
├── .moai/                          # MoAI 프로젝트 문서
│   ├── config/config.yaml
│   └── project/
│       ├── product.md              # 이 파일의 형제
│       ├── structure.md            # ← 현재 파일
│       ├── tech.md
│       └── codemaps/               # 5개 아키텍처 문서 (재생성됨 2026-04-09)
│
└── logs/                           # gitignored
    └── confluence_sync.log         # launchd 로그
```

## 모듈 의존 관계

### Frontend → Backend
```
src/app/**/page.tsx
  └─> src/lib/api.ts (apiFetch + convertKeys)
       └─> fetch(`${API_BASE}/api/...`)
            └─> next.config.ts rewrites → http://localhost:8000/api/*
                 └─> backend/app/routes/*
                      └─> backend/app/models/models.py
                           └─> backend/app/database.py (PostgreSQL 16)
```

### Monitoring → Backend
```
monitoring/main.py
  └─> app/main_window.py
       ├─> app/api_client.py (requests HTTP → FastAPI :8000)
       ├─> app/ws_worker.py (websocket-client → /ws/dashboard)
       └─> app/mqtt_worker.py (paho-mqtt → broker :1883, optional)
```

### Firmware → Backend (간접)
```
firmware/conveyor_controller/conveyor_controller.ino
  ├─> HardwareSerial (TOF250 ASCII UART 9600)
  ├─> WiFi
  └─> ESP32MQTTClient → MQTT broker
       └─> 백엔드 or 모니터링 앱이 구독
```

### Confluence Sync Pipeline
```
launchd (매일 09:07)
  └─> scripts/sync_confluence_facts.py
       ├─> macOS Keychain (Atlassian token)
       ├─> Confluence REST API v2 (GET only)
       ├─> docs/CONFLUENCE_FACTS.md 섹션 덮어쓰기 (CURATED 블록 보존)
       └─> git add + commit
```

## 주요 진입점 요약

| 계층 | 엔트리 파일 | 기동 명령 |
|---|---|---|
| Next.js dev | `src/app/layout.tsx` + `page.tsx` | `npm run dev` |
| FastAPI | `backend/app/main.py` | `uvicorn app.main:app` |
| PyQt5 | `monitoring/main.py` | `cd monitoring && python main.py` |
| ESP32 | `firmware/conveyor_controller/*.ino` | `arduino-cli upload` |
| Confluence sync | `scripts/sync_confluence_facts.py` | launchd (auto) |
| DB 마이그 (일회성) | `backend/scripts/*.{py,sql}` | `python` or `psql -f` |

상세 카탈로그는 `.moai/project/codemaps/entry-points.md` 참조.

## 순환 의존성

**없음**. `database → models → routes → main` 단방향. 프론트 `lib → app`, 모니터링 `main → main_window → workers/pages/widgets` 도 단방향.

## 레거시 / 정리 대상

- `src/lib/mock-data.ts` (575줄): 현재 실사용처 Grep 기준 미확인. 일부 레거시 추정.
- `src/lib/types.ts` 의 `Product` 인터페이스: 구식 (category_label, priceRange 등 미반영). `customer/page.tsx` 는 자체 로컬 정의 사용.
- `requirements.txt` 의 `asyncpg / asyncio-mqtt / redis / alembic`: 아직 코드 import 없음, 향후 예약.
