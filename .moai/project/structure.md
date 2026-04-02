# 프로젝트 구조

## 아키텍처 패턴

Monorepo 구조의 풀스택 애플리케이션. 프론트엔드(Next.js)와 백엔드(FastAPI)가 동일 저장소에 공존하며, Blender 3D 에셋 파이프라인이 별도 디렉토리로 관리된다.

```
casting-factory/
├── src/                          # Next.js 프론트엔드 소스
│   ├── app/                      # App Router 페이지
│   │   ├── layout.tsx            # 루트 레이아웃 (AdminShell 래핑)
│   │   ├── page.tsx              # 메인 대시보드 페이지
│   │   └── globals.css           # 글로벌 스타일
│   ├── components/               # React 컴포넌트
│   │   ├── AdminShell.tsx        # 사이드바+헤더 관리자 셸
│   │   ├── Header.tsx            # 상단 헤더
│   │   ├── Sidebar.tsx           # 좌측 사이드바 네비게이션
│   │   ├── FactoryMap.tsx        # 2D 공장 레이아웃 맵
│   │   ├── FactoryMap3D.tsx      # 3D 공장 맵 (Three.js)
│   │   ├── FactoryMap3DCanvas.tsx # 3D 캔버스 컨테이너
│   │   ├── FactoryMapEditor.tsx  # 3D 맵 편집 모드
│   │   └── charts/              # Recharts 차트 컴포넌트
│   │       ├── WeeklyProductionChart.tsx
│   │       ├── ProductionVsDefectsChart.tsx
│   │       ├── DefectRateChart.tsx
│   │       └── DefectTypeDistChart.tsx
│   └── lib/                      # 공유 유틸리티
│       ├── types.ts              # 전체 도메인 타입 정의
│       ├── mock-data.ts          # Mock 데이터 (개발용)
│       └── utils.ts              # 포맷팅, 상태맵 헬퍼
│
├── backend/                      # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py               # FastAPI 앱 엔트리포인트 (라우터 등록, CORS)
│   │   ├── database.py           # SQLAlchemy 엔진/세션 설정 (SQLite)
│   │   ├── seed.py               # 초기 시드 데이터 삽입
│   │   ├── models/
│   │   │   └── models.py         # SQLAlchemy ORM 모델
│   │   ├── schemas/
│   │   │   └── schemas.py        # Pydantic 응답 스키마
│   │   └── routes/               # API 라우터
│   │       ├── orders.py         # 주문 관리 API
│   │       ├── production.py     # 생산 모니터링 API
│   │       ├── quality.py        # 품질 검사 API
│   │       ├── logistics.py      # 물류/이송 API
│   │       ├── alerts.py         # 알림 API
│   │       └── websocket.py      # WebSocket 실시간 통신
│   ├── requirements.txt          # Python 의존성
│   └── casting_factory.db        # SQLite DB (자동 생성)
│
├── blender/                      # 3D 에셋 파이프라인
│   ├── factory_scene.py          # Blender Python 스크립트
│   ├── MyCobot280.step           # 로봇팔 CAD 모델
│   └── MyCobot280.stl            # 로봇팔 메시
│
├── public/                       # 정적 에셋
│   ├── factory-map2.glb          # 3D 공장 모델 (Blender 출력)
│   ├── factory-3d.png            # 3D 미리보기 이미지
│   └── factory-3d-map2.png       # 맵2 미리보기 이미지
│
├── docs/                         # 프로젝트 문서
│   ├── DB_데이터_리스트.md        # DB 스키마 문서
│   └── GUI_페이지_리스트.md       # GUI 페이지 목록
│
├── package.json                  # Node.js 의존성 및 스크립트
├── next.config.ts                # Next.js 설정 (allowedDevOrigins)
├── tsconfig.json                 # TypeScript 설정
├── postcss.config.mjs            # PostCSS (Tailwind)
├── eslint.config.mjs             # ESLint 설정
├── CLAUDE.md                     # AI 컨텍스트 (AGENTS.md 참조)
└── AGENTS.md                     # 프로젝트 AI 에이전트 규칙
```

## 모듈 관계

- `src/app/page.tsx` → `src/components/*` → `src/lib/mock-data.ts` → `src/lib/types.ts`
- `src/components/FactoryMap3D.tsx` → `public/factory-map2.glb` (Three.js GLB 로드)
- `backend/app/main.py` → `backend/app/routes/*` → `backend/app/models/` + `backend/app/schemas/`
- `blender/factory_scene.py` → (Blender 내 실행) → `public/*.glb` 출력

## 진입점

| 진입점 | 파일 | 설명 |
|--------|------|------|
| 프론트엔드 | `src/app/page.tsx` | Next.js App Router 메인 페이지 |
| 백엔드 | `backend/app/main.py` | FastAPI 앱 인스턴스 |
| 3D 에셋 | `blender/factory_scene.py` | Blender 3D 씬 생성 스크립트 |
