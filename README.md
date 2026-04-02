# 주물공장 생산 관제 시스템 (Casting Factory MES)

주물(캐스팅) 스마트 공장의 실시간 생산 관제 대시보드. 용해~분류 전체 공정 모니터링, 주문 관리, 품질 검사, 물류/이송, 3D 공장 맵을 통합 관리한다.

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 프론트엔드 | Next.js 16 + React 19 + TypeScript |
| UI | Tailwind CSS 4 + Recharts + Lucide Icons |
| 3D | Three.js + @react-three/fiber + drei |
| 백엔드 | FastAPI + SQLAlchemy + Pydantic |
| DB | SQLite |
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

### 프론트엔드

```bash
npm install
npm run dev
```

프론트엔드: http://localhost:3000

## 프로젝트 구조

```
casting-factory/
├── src/                    # Next.js 프론트엔드
│   ├── app/                # App Router 페이지
│   ├── components/         # React 컴포넌트 (대시보드, 3D 맵, 차트)
│   └── lib/                # 타입, API 클라이언트, 유틸리티
├── backend/                # FastAPI 백엔드
│   └── app/                # 라우터, 모델, 스키마, 시드 데이터
├── blender/                # 3D 에셋 (Blender 스크립트, CAD 파일)
├── public/                 # 정적 파일 (GLB 모델, 이미지)
└── docs/                   # 프로젝트 문서
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
