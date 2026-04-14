# 아키텍처 개요

> **Last updated**: 2026-04-13 (주문 플로우 스텝 재배치, monitoring UI 최적화 반영)

## 시스템 구성

SmartCast Robotics 주물 스마트 공장 관제 시스템. 주문 접수→생산→품질검사→물류→출고 전 공정을 웹 대시보드 + 데스크톱 모니터링으로 관제한다.

## Architecture Pattern

**3-Tier Layered + Proxy Gateway**

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer                                      │
│  ┌────────────────────┐  ┌─────────────────────────────┐ │
│  │  Next.js 16 Web    │  │  PyQt5 Desktop Monitoring   │ │
│  │  React 19 · TS     │  │  Python 3.11+               │ │
│  │  localhost:3000     │  │  native desktop app         │ │
│  └─────────┬──────────┘  └──────────┬──────────────────┘ │
│            │ /api/* rewrite         │ HTTP + WebSocket    │
├────────────┼────────────────────────┼────────────────────┤
│  Business Logic Layer                                    │
│  ┌─────────▼────────────────────────▼──────────────────┐ │
│  │  FastAPI 0.115 Backend (Uvicorn ASGI)               │ │
│  │  SQLAlchemy 2.0 ORM · Pydantic v2 · CORS           │ │
│  │  localhost:8000                                     │ │
│  └───────────────────────┬─────────────────────────────┘ │
├──────────────────────────┼───────────────────────────────┤
│  Data Layer              │                               │
│  ┌───────────────────────▼─────────────────────────────┐ │
│  │  PostgreSQL 16 + TimescaleDB (단독)                  │ │
│  │  100.107.120.14:5432 / smartcast_robotics            │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 기술 스택

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Next.js (Turbopack) | 16.2.1 | SSR/CSR 웹 앱 |
| Frontend | React | 19.2.4 | UI 컴포넌트 |
| Frontend | Three.js + R3F | 0.183 | 3D 공장 맵 |
| Frontend | Recharts | 3.8 | 차트/시각화 |
| Frontend | Tailwind CSS | 4.x | 스타일링 |
| Frontend | Lucide React | 1.7 | 아이콘 |
| Backend | FastAPI | 0.115 | REST API + WebSocket |
| Backend | SQLAlchemy | 2.0.35 | ORM |
| Backend | Pydantic | 2.9 | 요청/응답 검증 |
| Backend | Uvicorn | 0.30 | ASGI 서버 |
| Backend | psycopg | 3.2.3 | PostgreSQL 드라이버 |
| Database | PostgreSQL | 16 | 운영 DB |
| Database | TimescaleDB | ext | 시계열 데이터 |
| Monitoring | PyQt5 | 5.15.11 | 데스크톱 GUI |
| Monitoring | PyQtChart | 5.15.7 | 데스크톱 차트 |
| IoT | asyncio-mqtt | 0.16.2 | MQTT 센서 데이터 |
| IoT | websocket-client | 1.8 | 실시간 대시보드 |
| Infra | Redis | 5.1.1 | 캐시 / pub-sub |

## 모듈 인벤토리

| Module | Directory | 책임 | 파일 수 |
|--------|-----------|------|--------|
| Web Frontend | `src/` | 관리자 대시보드 + 고객 주문 UI | ~20 |
| Backend API | `backend/` | REST API, 비즈니스 로직, DB | ~12 |
| Desktop Monitor | `monitoring/` | 실시간 공장 모니터링 (PyQt5) | ~25 |
| Firmware | `firmware/` | ESP32 컨베이어 제어 | ~3 |
| 3D Assets | `blender/` | Blender 공장 씬 | ~1 |
| Scripts | `scripts/` | Confluence 동기화 등 | ~1 |
| Docs | `docs/` | 팩트 문서, 아키텍처 보고서 | ~5 |

## 핵심 설계 결정

1. **Proxy Pattern**: `next.config.ts` rewrites로 `/api/*` → `localhost:8000/api/*` 프록시 (CORS 우회, 단일 도메인)
2. **Key Convention Bridge**: `src/lib/api.ts`의 `convertKeys()` — 백엔드 snake_case ↔ 프론트 camelCase 자동 변환
3. **Client-Side ID Generation**: 주문 ID(`ORD-YYYYMMDD-XXXX`), 고객 ID(`CUST-XXXXXX`)를 클라이언트에서 생성
4. **Dual UI Strategy**: 웹(관리자+고객)과 데스크톱(공장 운영자)으로 사용자 분리
5. **PG 단독 정책 (2026-04-14)**: `DATABASE_URL` 미설정 시 fail-fast (이전 SQLite 폴백 제거)
6. **Seed on Startup**: FastAPI lifespan에서 `seed_database()` 호출 — 개발 환경 초기 데이터 자동 주입
7. **Step-First Customer UX**: 주문 폼 5단계 (주문자정보→제품선택→사양입력→견적확인→주문완료)
