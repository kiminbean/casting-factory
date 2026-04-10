# SmartCast Robotics — 주물공장 생산 관제 시스템

> **Version**: v3.5.0 — SmartCast Robotics 랜딩 + 주문 파이프라인 6단계 + 원격 DB 이관

주물(캐스팅) 스마트 공장의 실시간 생산 관제 시스템. 8단계 주물 공정(용해~분류) 모니터링, 주문 관리(접수~출고~완료), 품질 검사, 물류/이송, 3D 공장 맵을 통합 관리한다.

## 빠른 시작 (다른 PC 에서 실행)

> 상세 설치 가이드: [docs/SETUP.md](docs/SETUP.md)

### 사전 요구

- **Node.js 20+** (v23 권장)
- **Python 3.11+**
- **Tailscale** (DB 서버 접근용, VPN)
- **Git**

### 1. 소스 코드 클론

```bash
git clone https://github.com/kiminbean/casting-factory.git
cd casting-factory
```

### 2. 프론트엔드 설치 및 실행

```bash
# 프로젝트 루트 디렉터리에서 실행 (casting-factory/)
cd casting-factory
npm install

# .env.local 생성 (관리자 비밀번호)
echo 'NEXT_PUBLIC_ADMIN_PASSWORD=admin1234' > .env.local

# 개발 서버 실행 (LAN 에서도 접근 가능)
npm run dev
```

프론트엔드: http://localhost:3000

### 3. 백엔드 설치 및 실행 (별도 터미널)

```bash
# 프로젝트 루트에서 backend/ 디렉터리로 이동
cd casting-factory/backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env.local 생성 (원격 DB 접속 — 비밀번호는 관리자에게 문의)
cat > .env.local << 'EOF'
DATABASE_URL=postgresql+psycopg://team2:<비밀번호>@100.107.120.14:5432/smartcast_robotics
EOF

# 개발 서버 실행
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

백엔드: http://localhost:8000

### 4. 동작 확인

- http://localhost:3000/ — SmartCast Robotics 랜딩 페이지 (3 버튼)
- http://localhost:3000/admin/login — 관리자 로그인 (비밀번호: `admin1234`)
- http://localhost:3000/customer — 고객 발주 포털
- http://localhost:8000/health — 백엔드 헬스체크
- http://localhost:8000/api/orders — 주문 목록 (JSON)

---

## 아키텍처 개요

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js 16.2 + React 19.2)    │  ← npm run dev (포트 3000)
│  관리자 + 고객 포털                       │
├─────────────────────────────────────────┤
│  Backend (FastAPI + SQLAlchemy 2.0)      │  ← uvicorn (포트 8000)
│  REST 31 + WebSocket 1                   │
├─────────────────────────────────────────┤
│  DB Server (PostgreSQL 16)               │  ← Tailscale 100.107.120.14:5432
│  Ubuntu 24.04, DB: smartcast_robotics    │
├─────────────────────────────────────────┤
│  Factory PC (PyQt5 데스크톱, 선택)       │  ← python main.py
│  실시간 모니터링 6페이지                  │
├─────────────────────────────────────────┤
│  ESP32 Firmware (Arduino, 선택)          │  ← conveyor_controller v4.0
│  컨베이어 + TOF250 + MQTT               │
└─────────────────────────────────────────┘
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
├── monitoring/             # PyQt5 관제 모니터링 데스크톱 앱
├── firmware/               # ESP32 컨베이어 컨트롤러 (v4.0 MQTT)
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

## 라이선스

Private Repository — SmartCast Robotics
