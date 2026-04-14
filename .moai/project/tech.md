# 기술 스택

> **Last updated**: 2026-04-14 (V6 아키텍처 결정 추가)

## 0. V6 아키텍처 (2026-04-14)

| 항목 | 값 |
|---|---|
| Interface Service | FastAPI :8000 (HTTP, Admin/Customer 용) |
| **Management Service** | **gRPC :50051 (Factory Operator PC PyQt 직결)** |
| 프로토콜 | Protocol Buffers — `backend/management/proto/management.proto` |
| Python gRPC | grpcio 1.66, grpcio-tools 1.66, protobuf 5.28 |
| 서버 진입 | `backend/management/server.py` |
| 클라이언트 | `monitoring/app/management_client.py` |
| 설계 문서 | `docs/management_service_design.md` |

이유: Interface Service 장애/AWS 이관 중에도 공장 가동 유지 (SPOF 제거).

## 1. 프론트엔드 (Next.js 웹)

| 기술 | 버전 | 용도 |
|---|---|---|
| Next.js | 16.2.1 | App Router 프레임워크 (`next dev -H 0.0.0.0`) |
| React | 19.2.4 | UI 런타임 |
| TypeScript | ~5 | 타입 시스템 (`tsconfig.json`) |
| Tailwind CSS | 4 | 유틸리티 CSS |
| @tailwindcss/postcss | 4 | PostCSS 통합 |
| Three.js | 0.183.2 | WebGL 3D 엔진 |
| @react-three/fiber | 9.5.0 | React ↔ Three 바인딩 |
| @react-three/drei | 10.7.7 | R3F 헬퍼 |
| Recharts | 3.8.1 | SVG 차트 (`next/dynamic`, `ssr: false`) |
| Lucide React | 1.7.0 | 아이콘 SVG |
| date-fns | 4.1.0 | 날짜 포맷 |
| clsx | 2.1.1 | className 조합 |
| ESLint | 9 | 린트 (`eslint-config-next 16.2.1`) |

**주의**: 루트 `AGENTS.md` 경고 — "이것은 네가 아는 Next.js 가 아니다. 수정 전 `node_modules/next/dist/docs/` 를 반드시 읽을 것. deprecation notice 주의."

## 2. 백엔드 (FastAPI)

| 기술 | 버전 | 용도 | 활성 상태 |
|---|---|---|---|
| Python | 3.11+ | 런타임 | ✓ |
| FastAPI | 0.115.0 | REST + WebSocket | ✓ |
| Uvicorn[standard] | 0.30.0 | ASGI 서버 | ✓ |
| SQLAlchemy | 2.0.35 | ORM (sync) | ✓ |
| Pydantic | 2.9.0 | 스키마 검증 | ✓ |
| psycopg[binary] | 3.2.3 | PostgreSQL 드라이버 (sync) | ✓ |
| python-multipart | 0.0.9 | form-data | ✓ |
| websockets | 13.0 | WS (uvicorn deps) | ✓ |
| asyncpg | 0.29.0 | async PG 드라이버 | 예약 (미사용) |
| alembic | 1.13.3 | 스키마 마이그레이션 | 예약 (현재 SQL 파일로 대체) |
| asyncio-mqtt | 0.16.2 | MQTT | 예약 (미사용) |
| redis | 5.1.1 | 캐시/pub-sub | 예약 (미사용) |

## 3. 데이터베이스 (2026-04-09 PostgreSQL 16 전환 완료)

### 메인 DB

| 항목 | 값 |
|---|---|
| 엔진 | PostgreSQL 16.13 (Homebrew `postgresql@16`) |
| 기본 호스트 | 127.0.0.1:5432 |
| LAN 공유 호스트 | 192.168.0.16:5432 (`pg_hba.conf` 에 `192.168.0.0/24` scram-sha-256) |
| 데이터베이스 | `casting_factory_dev` |
| 사용자 | `casting_factory` |
| 접속 문자열 | `backend/.env.local` 의 `DATABASE_URL` (gitignored, 600 권한) |
| 드라이버 | `postgresql+psycopg://` (sync) |
| 연결 풀 | pool_size=10, max_overflow=20, pre_ping, recycle 1800 |
| 서비스 관리 | `brew services start\|stop\|restart postgresql@16` |
| 설정 파일 | `/opt/homebrew/var/postgresql@16/postgresql.conf`, `pg_hba.conf` |

### DB 단일화 정책 (2026-04-14)

- **PostgreSQL 단독**. SQLite 폴백 완전 제거.
- `DATABASE_URL` 미설정 시 `database.py` 가 즉시 `RuntimeError` 발생 (fail-fast)
- `database.py:_load_env_local()` 이 stdlib 로 `.env.local` 파싱
- `main.py lifespan` 은 `create_all + idempotent seed` 만 수행

### DB GUI

- **DBeaver Community** (26.0.2, `/Applications/DBeaver.app`, `brew install --cask dbeaver-community`)
- TablePlus / pgAdmin 4 / Postico 는 사용하지 않음 (사용자 선호, 메모리 기록)

### 마이그레이션 도구

| 파일 | 역할 | 실행 |
|---|---|---|
| `backend/scripts/migrate_products_front_truth.sql` | Product 스키마 확장 + PRD-*→D* 재매핑 | 멱등 |
| `backend/scripts/migrate_load_classes.sql` | EN 124 하중 등급 테이블 생성 | 멱등 |

Alembic 은 requirements.txt 에 있지만 아직 활용하지 않음. 마이그레이션 규모가 작아 SQL 파일 + Python 스크립트로 충분.

## 4. 모니터링 앱 (PyQt5)

| 기술 | 용도 |
|---|---|
| PyQt5 | 데스크톱 GUI 프레임워크 |
| requests | 동기 HTTP 클라이언트 |
| websocket-client | WebSocket 클라이언트 (`QThread` 안) |
| paho-mqtt | MQTT 클라이언트 (optional, `CASTING_MQTT_ENABLED=1`) |

환경변수:
- `CASTING_API_HOST=192.168.0.16:8000` (기본)
- `CASTING_DATA_MODE=normal|fallback|mock_only` (기본: fallback)
- `CASTING_MQTT_ENABLED=1` (optional)

## 5. 펌웨어 (ESP32)

| 기술 | 버전 | 용도 |
|---|---|---|
| Arduino ESP32 core | 3.3.7 | 보드 지원 |
| ESP32MQTTClient | - | MQTT 클라이언트 |
| arduino-cli | 1.4.1 | 빌드/업로드 CLI |

하드웨어:
- ESP32-WROOM32
- L298N 모터 드라이버
- TOF250 레이저 거리 센서 × 2 (ASCII UART 9600, I2C 아님)
- JGB37-555 DC 기어 모터

## 6. 3D 파이프라인 (Blender)

| 도구 | 용도 |
|---|---|
| Blender | 3D 공장 모델링 (오프라인) |
| Python (Blender 내부) | `blender/factory_scene.py` |
| GLB/glTF | 3D 포맷 → `public/factory-map2.glb` |
| STEP/STL | CAD 원본 (MyCobot280 등) |

## 7. 운영 / DevOps

| 항목 | 도구 | 용도 |
|---|---|---|
| Cron | macOS **launchd** | 매일 09:07 Confluence 동기화 |
| 스케줄러 plist | `~/Library/LaunchAgents/com.casting-factory.confluence-sync.plist` | launchd 등록 |
| 비밀 저장 | **macOS Keychain** (`security add-generic-password`) | Atlassian API token |
| 버전 관리 | Git + GitHub | `kiminbean/casting-factory` |
| 문서 동기화 | `scripts/sync_confluence_facts.py` (stdlib only) | Confluence v2 API → markdown |
| LAN 공유 | `postgresql.conf listen_addresses='*'` + `pg_hba.conf scram-sha-256` | 192.168.0.0/24 |
| 패키지 관리 | Homebrew, npm, pip, arduino-cli | 계층별 |

## 8. 개발 환경

| 항목 | 설정 |
|---|---|
| OS | macOS (Apple Silicon, M1 MacBook Pro) |
| Shell | zsh |
| Node.js 패키지 매니저 | npm |
| Python 환경 | venv (`backend/venv/`) |
| Python 버전 | 3.14.2 (dev), 3.11+ 호환 |
| Tailwind CSS | PostCSS + Tailwind 4 |
| 폰트 | Inter (Google Fonts, `next/font`) |
| 에디터 | (사용자 자유) |

## 9. 주요 실행 명령

```bash
# 프론트 (LAN 노출)
npm install
npm run dev                                  # → http://localhost:3000 + http://192.168.0.16:3000

# 백엔드
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# PyQt5 모니터링
cd monitoring && python main.py

# ESP32 펌웨어
cd firmware/conveyor_controller
arduino-cli compile --fqbn esp32:esp32:esp32 .
arduino-cli upload --fqbn esp32:esp32:esp32 -p /dev/cu.usbserial-0001 .

# Confluence 수동 실행
python3 scripts/sync_confluence_facts.py --dry-run
python3 scripts/sync_confluence_facts.py --init-snapshot  # 최초 1회
python3 scripts/sync_confluence_facts.py

# launchd 관리
launchctl load   ~/Library/LaunchAgents/com.casting-factory.confluence-sync.plist
launchctl list | grep casting-factory
launchctl start  com.casting-factory.confluence-sync  # 즉시 실행

# PostgreSQL 서비스
brew services start postgresql@16
brew services restart postgresql@16
psql postgresql://casting_factory@127.0.0.1:5432/casting_factory_dev  # 로컬 접속

# DB 마이그레이션 (일회성)
cd backend
source venv/bin/activate
psql $DATABASE_URL -f scripts/migrate_products_front_truth.sql
psql $DATABASE_URL -f scripts/migrate_load_classes.sql
```

## 10. API 엔드포인트 구조 (31 REST + 1 WS)

| 라우터 | prefix | 파일 | 주요 기능 |
|---|---|---|---|
| orders | `/api/orders` | `routes/orders.py` | 주문 CRUD, 상세, 상태 |
| products_router | `/api/products` | `routes/orders.py` | 제품 마스터 (JSON 파싱) |
| **load_classes_router** (신규) | `/api/load-classes` | `routes/orders.py` | EN 124 하중 등급 6종 |
| production | `/api/production` | `routes/production.py` | stages/metrics/equipment |
| schedule | `/api/production/schedule` | `routes/schedule.py` | 7요소 우선순위 계산 + jobs + priority-log |
| quality | `/api/quality` | `routes/quality.py` | inspections/stats/standards/sorter-logs |
| logistics | `/api/logistics` | `routes/logistics.py` | tasks/warehouse/outbound-orders |
| alerts | `/api` | `routes/alerts.py` | alerts + dashboard/stats |
| websocket | `/ws` | `routes/websocket.py` | `/ws/dashboard` 5초 tick |
| health | `/health` | `main.py` | 헬스체크 |

상세 메서드·경로는 `.moai/project/codemaps/entry-points.md` 참조.

## 11. 주요 설계 결정 사항

1. **프론트가 products source of truth** (2026-04-09): `src/app/customer/page.tsx PRODUCTS` 배열 → DB `products` 테이블 1:1 매칭 스키마 확장. 프론트는 하드코딩 유지, DB 는 조회/FK 용도.
2. **ID 체계**: `D450`, `D600`, `D800`, `GRATING`, 하중 등급 `A15~F900`. 기존 `PRD-001~005` 는 모두 정리 완료 (order_details 재매핑 포함).
3. **PostgreSQL 16 전환** (2026-04-09): 운영 PG 도입. SQLite 폴백 (2026-04-14 완전 제거).
4. **DB 서버 재지정 예정** (2026-04-16 전후): 개인 Mac → 전용 서버. `pg_dump/pg_restore` 이관 예정. 연결 문자열 한 줄만 수정하면 됨.
5. **UI 분리 정책**: 실시간 5 페이지는 PyQt5, 관리자 2 + 고객 2 = 웹 4 페이지만. Confluence 17956894 결정 근거.
6. **Confluence READ-ONLY**: addinedute space (homepage 753829) 하부 페이지 쓰기 금지. GET 만 허용. launchd 매일 09:07 자동 동기화.
7. **App Router + "use client"**: 데이터 페이지는 모두 클라이언트 컴포넌트. SSR 없음.
8. **JSON 컬럼 전략**: diameter_options, thickness_options, materials 등은 `TEXT` 컬럼에 JSON 문자열로 저장 + `ProductResponse.from_orm_model()` 이 파싱. SQLite 폴백 호환 잔재이나 PG 단독 전환 후에도 유지(코드 영향 최소화). 향후 `jsonb` 마이그레이션 검토 가능.
9. **FK 최소화**: order_details.order_id, production_jobs.order_id 만 FK. 나머지는 soft-link.
10. **CORS `allow_origins=["*"]`**: 개발 전용. 운영 전 제한 필요.
11. **WebSocket 이 DB 직접 mutate**: 시뮬레이션 데모 목적. 실 장비 연동 시 분리 필요.
12. **TimescaleDB 미사용**: 하이퍼테이블 필요 시점 (`production_metrics` 등) 에 별도 도입 예정. 현재 row 수 미미.

## 12. 학습·참조 자료

| 리소스 | 용도 |
|---|---|
| `docs/CONFLUENCE_FACTS.md` | Confluence 22 페이지 전량 수집본 (자동 동기화) |
| `docs/architecture/` | 12 컴포넌트 설계 HTML (Confluence V4) |
| `docs/POSTGRES_MIGRATION.md` | PG 마이그레이션 기록 |
| `AGENTS.md` | Next.js 16 주의사항 |
| `CLAUDE.md` | Confluence Facts Index, 자동 동기화 설명, READ-ONLY 정책 |
| `.moai/project/codemaps/` | 5개 아키텍처 문서 (overview/modules/dependencies/entry-points/data-flow) |
