# 모듈 구조

## 프론트엔드 모듈

### app/ (페이지)
- `layout.tsx` — 루트 레이아웃, AdminShell 래핑, Inter 폰트 설정
- `page.tsx` — 메인 대시보드 (StatCard, FactoryMap, 알림 피드, 차트, 주문 테이블)

### components/ (UI 컴포넌트)
| 컴포넌트 | 역할 | 의존성 |
|----------|------|--------|
| AdminShell | 사이드바+헤더 래퍼 | Sidebar, Header |
| Sidebar | 좌측 네비게이션 메뉴 | lucide-react |
| Header | 상단 바 (알림, 프로필) | lucide-react |
| FactoryMap | 2D 공장 레이아웃 | mock-data, utils |
| FactoryMap3D | Three.js 3D 뷰어 | @react-three/fiber, drei |
| FactoryMap3DCanvas | 3D 캔버스 컨테이너 | FactoryMap3D |
| FactoryMapEditor | 3D 편집 모드 (복사/삭제) | Three.js |

### charts/ (차트)
| 차트 | 시각화 대상 |
|------|------------|
| WeeklyProductionChart | 주간 생산 추이 |
| ProductionVsDefectsChart | 생산량 vs 불량 비교 |
| DefectRateChart | 불량률 추이 |
| DefectTypeDistChart | 불량 유형 분포 |

### lib/ (공유 라이브러리)
| 파일 | 역할 |
|------|------|
| types.ts | 전체 도메인 타입 (Order, Equipment, Alert 등 30+ 타입) |
| mock-data.ts | 개발용 Mock 데이터 |
| utils.ts | 포맷팅(날짜/통화), 상태 레이블/색상 맵 |

## 백엔드 모듈

### routes/ (API 라우터)
| 라우터 | 도메인 | 주요 엔드포인트 |
|--------|--------|----------------|
| orders.py | 주문 관리 | CRUD /orders, /products |
| production.py | 생산 모니터링 | /production 로그/상태 |
| quality.py | 품질 검사 | /quality 검사 결과 |
| logistics.py | 물류/이송 | /logistics 태스크/창고 |
| alerts.py | 알림 | /alerts 알림 CRUD |
| websocket.py | 실시간 | /ws WebSocket 핸들러 |

### models/ (ORM)
- `models.py` — SQLAlchemy 모델 (Order, Equipment, Alert, ProductionLog 등)

### schemas/ (검증)
- `schemas.py` — Pydantic 요청/응답 스키마

### 기타
- `database.py` — SQLAlchemy 엔진, 세션 팩토리, `get_db()` 의존성
- `seed.py` — 초기 시드 데이터 (DB 생성 시 자동 실행)
- `main.py` — FastAPI 앱 인스턴스, 라우터 등록, CORS, lifespan

## Blender 모듈

- `factory_scene.py` — Blender Python API로 공장 3D 씬 생성
- `MyCobot280.step/stl` — 로봇팔 CAD 원본 (Blender에서 임포트)
