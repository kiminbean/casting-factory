# SmartCast Robotics — 주물공장 생산 관제 시스템

> **Version**: v3.6.0 — V6 canonical 정합 (Phase A–SPEC-C3) · SPEC-RFID-001 Wave 2 append-only 로그

주물(캐스팅) 스마트 공장의 실시간 생산 관제 시스템. 8단계 주물 공정(용해~분류) 모니터링, 주문 관리(접수~출고~완료), 품질 검사, 물류/이송, 3D 공장 맵을 통합 관리한다.

## 빠른 시작 (다른 PC 에서 실행)

> 상세 설치 가이드: [docs/SETUP.md](docs/SETUP.md) · 배포 런북: [docs/DEPLOY-phase-a-to-c3.md](docs/DEPLOY-phase-a-to-c3.md)

### 사전 요구

| 항목 | 버전 | 비고 |
|---|---|---|
| **Node.js** | 20+ (v23 권장) | 프론트엔드 (Next.js 16) |
| **Python** | **3.12 권장** | PyQt5/grpcio 는 Apple Silicon 3.14 휠 없음 (macOS 필수), 그 외 3.11+ 가능 |
| **Tailscale** | 최신 | DB 서버(100.107.120.14) / Jetson(100.77.62.67) VPN 접근 |
| **Git** | 2.30+ | — |

### 1. 소스 코드 클론

```bash
git clone https://github.com/kiminbean/casting-factory.git
cd casting-factory
```

### 2. 프론트엔드 설치 및 실행 (Next.js `:3000`)

```bash
# 프로젝트 루트 디렉터리 (casting-factory/)
npm install

# .env.local 생성 (관리자 비밀번호)
echo 'NEXT_PUBLIC_ADMIN_PASSWORD=admin1234' > .env.local

# 개발 서버 실행 (LAN 에서도 접근 가능 — next.config.ts 의 allowedDevOrigins 참고)
npm run dev
```

프론트엔드: http://localhost:3000

### 3. 백엔드 — Interface Service (FastAPI `:8000`)

관리자/고객 웹페이지가 호출하는 HTTP API. 별도 터미널에서 실행:

```bash
cd casting-factory/backend
python3 -m venv venv
source venv/bin/activate                        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env.local 생성 (원격 DB 접속 — 비밀번호는 관리자에게 문의)
cat > .env.local << 'EOF'
DATABASE_URL=postgresql+psycopg://team2:<비밀번호>@100.107.120.14:5432/smartcast_robotics?options=-c%20search_path%3Dsmartcast%2Cpublic
EOF

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interface Service: http://localhost:8000

### 4. 백엔드 — Management Service (gRPC `:50051`)

PyQt 관제 모니터링이 직결하는 gRPC 서비스. **PyQt 를 쓰지 않으면 생략 가능**하지만 생산시작/실시간 스트림 기능을 쓰려면 필수. 또 다른 터미널에서:

```bash
cd casting-factory/backend/management
python3.12 -m venv venv                         # Python 3.12 필수
source venv/bin/activate
pip install -r requirements.txt                 # grpcio, paramiko, psycopg 등
make proto                                       # management_pb2*.py 생성 (최초 1회)

# .env.local 로 backend/.env.local DATABASE_URL 공유됨
python server.py
```

Management Service: gRPC `localhost:50051` · 검증:

```bash
curl http://localhost:8000/api/management/health
# → {"status":"ok","service":"management","grpc":"localhost:50051"}
```

### 5. PyQt 관제 모니터링 (Factory Operator PC)

실시간 공정/주문/AMR/품질 대시보드. 생산시작·핸드오프 ACK 등 공장 운영 UX 포함. Management Service(`:50051`)가 기동 중이어야 대부분 기능이 동작.

```bash
cd casting-factory/monitoring
python3.12 -m venv venv                         # Python 3.12 (PyQt5 휠 호환)
source venv/bin/activate
pip install -r requirements.txt                 # PyQt5, grpcio, paho-mqtt 없음

# Management Service 의 proto 를 PyQt 쪽으로 복사 + 컴파일
bash scripts/gen_proto.sh                        # app/generated/management_pb2*.py 생성

# 환경변수 (기본값 사용 시 생략 가능)
export MANAGEMENT_GRPC_HOST=localhost
export MANAGEMENT_GRPC_PORT=50051
# FastAPI 호스트 (api_client.py legacy 호출용 — operations 페이지 일부)
export CASTING_API_HOST=127.0.0.1
export CASTING_API_PORT=8000

python main.py
```

**전제조건**: Interface `:8000` + Management `:50051` 모두 가동 중.

### 6. Jetson Orin NX (선택 — ESP32 컨베이어 제어용)

이미지 publishing + ESP32 Serial relay. 공장 현장 배포 시만 필요:

```bash
# 본인 PC 에서 원격 배포 (Tailscale SSH 필요)
bash jetson_publisher/deploy.sh --install
```

상세: [jetson_publisher/README.md](jetson_publisher/README.md)

### 7. 동작 확인

| URL / 명령 | 기대 |
|---|---|
| http://localhost:3000/ | SmartCast Robotics 랜딩 (3 버튼) |
| http://localhost:3000/admin/login | 관리자 로그인 (비밀번호 `admin1234`) |
| http://localhost:3000/customer | 고객 발주 포털 |
| http://localhost:8000/health | `{"status":"ok"}` |
| http://localhost:8000/api/orders | 주문 목록 JSON |
| http://localhost:8000/api/management/health | Management gRPC 왕복 확인 |
| PyQt 상태바 | `gRPC: ready` 표시 |
| PyQt schedule `[▶ 생산 시작]` | Management `StartProduction` 호출 성공 |

### 8. 환경변수 요약

| 변수 | 위치 | 기본 | 설명 |
|---|---|---|---|
| `NEXT_PUBLIC_ADMIN_PASSWORD` | 루트 `.env.local` | — | 관리자 로그인 (프론트) |
| `DATABASE_URL` | `backend/.env.local` | — | PostgreSQL (Interface + Management 공유). 권장 옵션: `?options=-c%20search_path%3Dsmartcast%2Cpublic` |
| `INTERFACE_PROXY_START_PRODUCTION` | `backend/` env | `0` | **1 이면 `/api/production/start` 를 Mgmt gRPC 로 proxy** · 모듈 import 시점 고정, flip 시 FastAPI worker 재시작 필수 (SPEC-C2) |
| `MANAGEMENT_GRPC_HOST` / `PORT` | Interface + PyQt | `localhost:50051` | Management 엔드포인트 |
| `MGMT_GRPC_TLS_ENABLED` | Management env | `0` | 1 이면 mTLS (`certs/` 필요) |
| `MGMT_ROS2_ENABLED` | Management env | `0` | 1 + rclpy 설치 시 실 ROS2 publish (Ubuntu Jazzy) |
| `FMS_AUTOPLAY` | Management env | `0` | 1 이면 FMS 자동 진행 시퀀서 기동 |
| `MGMT_COMMAND_STREAM_ENABLED` | Jetson env | `0` | 1 이면 `WatchConveyorCommands` 구독 (ESP32 Serial relay, Phase D-2) |
| `MGMT_COMMAND_SUBSCRIBER_ID` | Jetson env | `jetson-orin-nx-01` | `WatchConveyorCommands` 구독자 식별자 |
| `ESP_BRIDGE_ENABLED` / `ESP_BRIDGE_PORT` | Jetson env | `0` / `/dev/ttyUSB0` | Jetson → ESP32 Serial relay |
| `CASTING_API_HOST` / `PORT` | PyQt | `192.168.0.16:8000` | FastAPI legacy 호출 (Phase A-2 에서 제거 예정) |

---

## 아키텍처 개요 (V6 canonical)

```
┌──────────────────────────────────────────────────────────┐
│  Frontend (Next.js 16.2 + React 19.2)  [:3000]            │  npm run dev
│  관리자 + 고객 포털                                        │
├──────────────────────────────────────────────────────────┤
│  Interface Service (FastAPI + SQLAlchemy 2.0)  [:8000]    │  uvicorn
│  REST 31 + /api/management/health (gRPC proxy)            │
├──────────────────────────────────────────────────────────┤
│  Management Service (gRPC + proto)  [:50051]              │  python server.py
│  StartProduction · ListItems · WatchItems · WatchAlerts   │
│  WatchCameraFrames · WatchConveyorCommands (ESP32 relay)  │
│  GetRobotStatus · TransitionAmrState · PlanRoute          │
│  ReportHandoffAck (SPEC-AMR-001) · ReportRfidScan (RFID)  │
├──────────────────────────────────────────────────────────┤
│  DB Server (PostgreSQL 16 + TimescaleDB)                  │  Tailscale
│  100.107.120.14:5432 · smartcast_robotics                 │
├──────────────────────────────────────────────────────────┤
│  Factory PC (PyQt5)                                       │  python main.py
│  gRPC 직결 · 6페이지 모니터링 + 생산시작 · 핸드오프 ACK     │
├──────────────────────────────────────────────────────────┤
│  Jetson Orin NX (image publisher + ESP32 Serial relay)    │  systemd
│  Tailscale 100.77.62.67 · /dev/ttyUSB0 ↔ ESP32 v5         │
├──────────────────────────────────────────────────────────┤
│  ESP32 (conveyor_controller v5)                           │  Serial 115200
│  Jetson Serial 수신 · RC522 RFID · L298N 모터             │
└──────────────────────────────────────────────────────────┘
```

## UI 분리 정책

| 역할 | 앱 | 경로 / 실행 |
|---|---|---|
| 공개 랜딩 | Next.js 웹 | `/` (3 버튼: 관리자/주문하기/주문 조회) |
| 관리자 포털 | Next.js 웹 | `/admin` → `/orders`, `/quality` |
| 고객 발주 | Next.js 웹 | `/customer` (4단계 폼) |
| 고객 주문 조회 | Next.js 웹 | `/customer/lookup` → `/customer/orders?email=...` |
| 관제 모니터링 | PyQt5 데스크톱 | `cd monitoring && python main.py` |

## 주문 상태 파이프라인

```
접수 → 승인 → 생산 → 생산 완료 → 출고 → 완료
(pending  approved  in_production  production_completed  shipping_ready  completed)
```

| 상태 | 전환 주체 | 웹 액션 |
|---|---|---|
| 접수 (pending) | 고객 발주 | 승인 / 반려 버튼 |
| 승인 (approved) | 관리자 | 생산 승인 버튼 |
| 생산 (in_production) | 관리자 (생산 승인) | 없음 (PyQt5 공정 시스템이 DB 에 다음 전환) |
| 생산 완료 (production_completed) | PyQt5 공정 시스템 (DB 직접) | 출고 처리 버튼 |
| 출고 (shipping_ready) | 관리자 | 출고 완료 버튼 |
| 완료 (completed) | 관리자 | - |

## 기술 스택

| 레이어 | 기술 |
|---|---|
| 프론트엔드 | Next.js 16.2.1 + React 19.2.4 + TypeScript 5 |
| UI | Tailwind CSS 4 + Recharts + Lucide Icons |
| 3D | Three.js 0.183 + @react-three/fiber + drei |
| 백엔드 | FastAPI 0.115 + SQLAlchemy 2.0 + Pydantic 2.9 + psycopg 3.2 |
| DB | **PostgreSQL 16** (Tailscale 원격 서버) |
| 실시간 | WebSocket (FastAPI) + MQTT (ESP32, optional) |
| 3D 에셋 | Blender → GLB |
| 모니터링 | PyQt5 (데스크톱 전용) |

## 프로젝트 구조

```
casting-factory/
├── src/                    # Next.js 프론트엔드
│   ├── app/                # App Router (/, /admin, /orders, /quality, /customer)
│   ├── components/         # SmartCastLogo, SmartCastHeader, AdminShell, FactoryMap 등
│   └── lib/                # api.ts, types.ts, utils.ts
├── backend/                # FastAPI 백엔드
│   ├── app/                # main.py, database.py, models/, schemas/, routes/, seed.py
│   ├── scripts/            # DB 마이그레이션 SQL
│   └── .env.local          # DATABASE_URL (gitignored)
├── monitoring/             # PyQt5 관제 모니터링 데스크톱 앱 (gRPC 직결)
├── jetson_publisher/       # Jetson Orin NX (이미지 publish + ESP32 Serial relay)
├── firmware/               # ESP32 컨베이어 컨트롤러 (v5 Serial · MQTT 제거)
├── scripts/                # sync_confluence_facts.py (launchd 자동 동기화)
├── blender/                # 3D 에셋 (Blender 스크립트, CAD 파일)
├── public/                 # 정적 파일 (factory-map2.glb)
├── docs/                   # 프로젝트 문서
│   ├── SETUP.md            # 상세 설치 가이드
│   └── CONFLUENCE_FACTS.md # Confluence 22페이지 팩트 수집본
├── .env.local              # NEXT_PUBLIC_ADMIN_PASSWORD (gitignored)
├── CLAUDE.md               # AI 컨텍스트 (Confluence 목차 포함)
└── AGENTS.md               # Next.js 16 주의사항
```

## DB 접속 정보

| 항목 | 값 |
|---|---|
| Host | `100.107.120.14` (Tailscale VPN) |
| Port | `5432` |
| Database | `smartcast_robotics` |
| User | `team2` |
| Password | 관리자에게 문의 |

**DBeaver 로 접속**: 상세 가이드 → [docs/SETUP.md](docs/SETUP.md)

## API 엔드포인트 (주요)

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/health` | 헬스체크 |
| GET | `/api/orders` | 주문 목록 |
| GET | `/api/orders?email=xxx` | 이메일 필터 주문 조회 |
| PATCH | `/api/orders/{id}/status` | 주문 상태 변경 |
| GET | `/api/products` | 제품 마스터 (4종) |
| GET | `/api/load-classes` | EN 124 하중 등급 (6종) |
| GET | `/api/production/stages` | 공정 단계 |
| POST | `/api/production/schedule/start` | 생산 개시 |
| GET | `/api/quality/inspections` | 품질 검사 |
| GET | `/api/logistics/tasks` | 이송 작업 |
| GET | `/api/dashboard/stats` | 대시보드 통계 |
| WS | `/ws/dashboard` | 실시간 WebSocket |

전체 31개 엔드포인트 → [.moai/project/codemaps/entry-points.md](.moai/project/codemaps/entry-points.md)

## 주요 SPEC 이력

| SPEC | 상태 | 요약 |
|---|---|---|
| **V6 canonical Phase A–D** | ✅ 머지 (2026-04-20) | PyQt WebSocket 제거 · ROS2 publisher → Management · Mgmt gRPC client · MQTT 제거 · Jetson subscriber + EspBridge |
| **SPEC-C2** | ✅ 머지 (Option A backward-compat) | Management TaskManager smartcast v2 이관 + Interface `/api/production/start` proxy 전환. `INTERFACE_PROXY_START_PRODUCTION` 플래그 |
| **SPEC-C3** | ✅ 머지 | Management 기동 복구 + smartcast Item 매핑. `models_mgmt.py` 로 legacy public-schema 3개 테이블 선별 re-export |
| **SPEC-AMR-001** | ✅ 머지 | ESP32 버튼 → Jetson → `ReportHandoffAck` gRPC → AMR FSM 해제 (Wave 1–4) |
| **SPEC-RFID-001 Wave 2** | 🟡 구현 진행 | RC522 → Jetson Serial → `ReportRfidScan` gRPC → `rfid_scan_log` append-only (item lookup 제외). [.moai/specs/SPEC-RFID-001/spec.md](.moai/specs/SPEC-RFID-001/spec.md) |
| **SPEC-RC522-001** | ✅ 머지 PR #2 | RC522 펌웨어 안정성 회귀 스위트. [docs/testing/rc522_regression_checklist.md](docs/testing/rc522_regression_checklist.md) |

배포 런북 → [docs/DEPLOY-phase-a-to-c3.md](docs/DEPLOY-phase-a-to-c3.md)
Management 설계 → [docs/management_service_design.md](docs/management_service_design.md)

## 라이선스

Private Repository — SmartCast Robotics
