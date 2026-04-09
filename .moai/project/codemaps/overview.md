# 아키텍처 개요

> **Last updated**: 2026-04-09 (PostgreSQL 16 마이그레이션 + products/load_classes 재정리 반영)

## 시스템 구성

주물공장 관제 시스템은 **4개 독립 런타임**으로 구성된 모노레포:

```
┌────────────────────────────────────────────────────────────────┐
│  Web Frontend (Next.js 16.2.1 + React 19.2.4)                  │
│  ├─ 관리자 포털 /   /orders   /quality  (Sidebar 2개)          │
│  ├─ 고객 포털 /customer (별도 layout.tsx, 4단계 발주 폼)       │
│  └─ /production, /customer/orders (직접 URL)                    │
├────────────────────────────────────────────────────────────────┤
│  Backend API (FastAPI 0.115 + SQLAlchemy 2.0 + Pydantic v2)    │
│  ├─ REST: 31개 엔드포인트 (7개 라우터)                          │
│  ├─ WebSocket: /ws/dashboard (5초 tick, 브로드캐스트)          │
│  └─ PostgreSQL 16 (127.0.0.1:5432, .env.local)                 │
├────────────────────────────────────────────────────────────────┤
│  Factory PC Monitoring (PyQt5 데스크톱)                         │
│  ├─ 6개 페이지 (dashboard/map/production/schedule/quality/     │
│  │              logistics)                                      │
│  ├─ HTTP (requests) + WebSocket (websocket-client)             │
│  └─ MQTT (paho-mqtt, optional) — vision/AMR 이벤트             │
├────────────────────────────────────────────────────────────────┤
│  ESP32 Firmware (Arduino, v4.0.0)                               │
│  ├─ conveyor_controller: L298N + TOF250×2 상태머신             │
│  ├─ WiFi + ESP32MQTTClient → broker                            │
│  └─ vision/1/result MQTT 구독                                   │
└────────────────────────────────────────────────────────────────┘
```

## 핵심 아키텍처 결정 사항

### 1. DB: PostgreSQL 16 (2026-04-09 전환 완료)

- **기본 DB**: PostgreSQL 16 (Homebrew `postgresql@16`)
- **접속**: `backend/.env.local` 의 `DATABASE_URL` (git ignored)
- **폴백**: SQLite (`backend/casting_factory.db`) — `DATABASE_URL` 미설정 시 자동 폴백
- **현재 접속**: `postgresql+psycopg://casting_factory@127.0.0.1:5432/casting_factory_dev`
- **LAN 공유**: `192.168.0.0/24` 에서 `scram-sha-256` 로 접속 허용 (2026-04-16 전후 전용 DB 서버로 이관 예정)
- **DB GUI**: DBeaver Community 전용

### 2. UI 분리 정책 (2026-04-08 결정, Confluence 17956894)

실시간 모니터링 5개 페이지는 **Next.js 웹에서 제거**하고 **PyQt5 Factory PC 앱으로 이관**:

| 역할 | 위치 |
|---|---|
| 주문 관리, 품질 관리 | Next.js 웹 (`src/app/orders`, `src/app/quality`) |
| 고객 발주 · 고객 주문 조회 | Next.js 웹 (`src/app/customer/**`) |
| 대시보드 · 공장 맵 · 생산 모니터링 · 생산 계획 · 물류 · 품질 모니터링 | PyQt5 (`monitoring/app/pages/`) |

Sidebar (`src/components/Sidebar.tsx`) 는 관리자 영역에서 2개 링크만 노출. `/production` 페이지는 파일이 존재하나 Sidebar 에서 링크 제거됨.

### 3. Products / LoadClass 단일화 (2026-04-09)

- **source of truth**: `src/app/customer/page.tsx` 의 `PRODUCTS` 하드코딩 배열 (4개)
- **DB products**: 프론트와 1:1 매칭 스키마로 확장 (category_label, spec, price_range, diameter_options_json, thickness_options_json, materials_json, load_class_range 컬럼 추가)
- **ID 체계**: `D450`, `D600`, `D800`, `GRATING` (기존 `PRD-001~005` 는 모두 제거, `order_details.product_id` 도 재매핑 완료)
- **LoadClass 마스터**: 신규 테이블 `load_classes` (EN 124 6등급: A15/B125/C250/D400/E600/F900, 톤수·용도 저장)
- **프론트는 여전히 하드코딩 사용** (1주일 후 DB 서버 이관 후 API 연동 전환 예정)

### 4. Confluence 읽기 전용 정책

- `scripts/sync_confluence_facts.py` + launchd `com.casting-factory.confluence-sync` (매일 09:07)
- `docs/CONFLUENCE_FACTS.md` 를 Confluence v2 API 에서 자동 동기화 (in-place 덮어쓰기 + 자동 git commit)
- **addinedute space (homepage 753829) 하부 페이지 쓰기 금지** — GET 만 허용, PUT/POST/DELETE 는 사용자 명시 허락 필수

### 5. Confluence V4 4-레이어 (설계 문서)

```
Interface Layer    → Next.js (웹) + PyQt5 (Factory PC)
Control Layer      → FastAPI (backend/)
Execution Layer    → (미구현) FMS — docs/architecture/ 07-12 컴포넌트 설계만 존재
Equipment Layer    → ESP32 (firmware/) + AMR (별도 레포)
```

## 주요 기술 스택

| 계층 | 스택 |
|---|---|
| Frontend | Next.js 16.2.1, React 19.2.4, TypeScript 5, Tailwind 4, lucide-react, recharts, three.js + @react-three/fiber |
| Backend | Python 3.11+, FastAPI 0.115, SQLAlchemy 2.0.35, Pydantic 2.9, psycopg 3.2, uvicorn |
| Database | PostgreSQL 16 (Homebrew), SQLite (dev fallback) |
| Monitoring | PyQt5, requests, websocket-client, paho-mqtt (optional) |
| Firmware | Arduino ESP32 core 3.3.7, ESP32MQTTClient |
| Ops | launchd (daily cron), macOS Keychain (API token), DBeaver (DB GUI) |

## 제품 카탈로그 (프론트 기준)

| id | name | category | 하중 범위 | 기준가 |
|---|---|---|---|---|
| D450 | 맨홀 뚜껑 KS D-450 | manhole | B125 ~ D400 (12.5 ~ 40톤) | 50,000 - 70,000원 |
| D600 | 맨홀 뚜껑 KS D-600 | manhole | B125 ~ F900 (12.5 ~ 90톤) | 75,000 - 100,000원 |
| D800 | 맨홀 뚜껑 KS D-800 | manhole | C250 ~ F900 (25 ~ 90톤) | 110,000 - 140,000원 |
| GRATING | 배수구 그레이팅 500x300 | grating | B125 ~ C250 (12.5 ~ 25톤) | 30,000 - 45,000원 |

## 운영 상태 (2026-04-09 기준)

| 서비스 | 상태 | 접속 |
|---|---|---|
| PostgreSQL 16 | brew services started | 127.0.0.1:5432, LAN 192.168.0.16:5432 |
| FastAPI | uvicorn 127.0.0.1:8000 | 로컬 + LAN rewrite |
| Next.js dev | 0.0.0.0:3000 | 192.168.0.16:3000 (LAN) |
| launchd confluence sync | 등록 완료 | 매일 09:07 |
| DBeaver Community | /Applications | 수동 실행 |

## 다음 참조

- 상세 모듈 목록 → `modules.md`
- 의존성 그래프 → `dependencies.md`
- 엔트리 포인트 → `entry-points.md`
- 데이터 흐름 → `data-flow.md`
