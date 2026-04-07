# 주물공장 생산 관제 시스템 (Casting Factory MES)

> **Version**: v3.4.0 — UI 분리 (웹 관리자 + PyQt5 모니터링)

주물(캐스팅) 스마트 공장의 실시간 생산 관제 시스템. 용해~분류 전체 공정 모니터링, 주문 관리, 품질 검사, 물류/이송, 3D 공장 맵을 통합 관리한다.

## UI 분리 정책

| 영역 | 앱 | 화면 |
|------|-----|------|
| 관리자 (웹) | Next.js 16 `http://<host>:3000` | 생산 계획, 주문 관리, 품질 관리, 입출고 내역 |
| 관제실 (데스크톱) | **PyQt5 `monitoring/`** | 대시보드, 생산 모니터링, 품질 검사, 물류 이송 |
| 고객 (웹) | Next.js `/customer` | 주문 등록, 배송 조회 |

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 프론트엔드 | Next.js 16 + React 19 + TypeScript |
| UI | Tailwind CSS 4 + Recharts + Lucide Icons |
| 3D | Three.js + @react-three/fiber + drei |
| 백엔드 | FastAPI + SQLAlchemy + Pydantic + asyncpg |
| DB | **PostgreSQL 16 + TimescaleDB** (Phase 1 부터) · SQLite (Phase 0 개발용) |
| 메시징 | MQTT (Mosquitto, ESP32) + WebSocket (UI) |
| 3D 에셋 | Blender → GLB |

## 시작하기

### 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

백엔드 서버: http://localhost:8000

### 프론트엔드 (관리자 웹)

```bash
npm install
npm run dev
```

관리자 웹: http://localhost:3000

### 모니터링 앱 (PyQt5 데스크톱)

```bash
cd monitoring
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

환경변수로 API 서버 지정 가능: `CASTING_API_HOST=192.168.0.16 python main.py`

## 프로젝트 구조

```
casting-factory/
├── src/                    # Next.js 관리자 웹
│   ├── app/                # App Router 페이지 (생산계획/주문/품질/입출고)
│   ├── components/
│   └── lib/
├── monitoring/             # PyQt5 관제 모니터링 데스크톱 앱
│   ├── main.py
│   ├── config.py
│   ├── app/                # main_window, api_client, ws_worker, pages/*
│   └── resources/          # styles.qss
├── backend/                # FastAPI (공유 백엔드)
│   └── app/                # 라우터, 모델, 스키마, WebSocket
├── firmware/               # ESP32 펌웨어 (컨베이어 v4.0 MQTT)
├── blender/                # 3D 에셋 (Blender 스크립트, CAD 파일)
├── public/                 # 정적 파일 (GLB 모델, 이미지)
└── docs/                   # 프로젝트 문서 (architecture.html, POSTGRES_MIGRATION.md 등)
```

## 주요 기능

- **통합 대시보드**: 생산 KPI 카드, 실시간 알림, 주간 생산 차트, 주문 테이블
- **3D 공장 맵**: Three.js 기반 실시간 공장 뷰어 (편집 모드 지원)
- **주문 관리**: 접수~완료 상태 추적, 품목 상세
- **생산 모니터링**: 8단계 공정 상태 (용해~분류)
- **품질 검사**: 비전 검사 결과, 불량률 차트
- **물류/이송**: AMR 이송 태스크, 창고 관리

## API 엔드포인트

| 경로 | 설명 |
|------|------|
| GET /api/dashboard/stats | 대시보드 통계 |
| GET /api/orders | 주문 목록 |
| GET /api/production/stages | 공정 단계 |
| GET /api/production/metrics | 생산 지표 |
| GET /api/production/equipment | 설비 목록 |
| GET /api/quality | 품질 검사 |
| GET /api/logistics | 물류/이송 |
| GET /api/alerts | 알림 |
| WS /ws | WebSocket 실시간 |
