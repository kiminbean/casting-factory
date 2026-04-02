# 진입점

## 애플리케이션 진입점

### 프론트엔드
| 진입점 | 파일 | 트리거 |
|--------|------|--------|
| 메인 페이지 | `src/app/page.tsx` | `/` 라우트 접근 |
| 루트 레이아웃 | `src/app/layout.tsx` | 모든 페이지 렌더링 시 |

### 백엔드
| 진입점 | 파일 | 트리거 |
|--------|------|--------|
| FastAPI 앱 | `backend/app/main.py` | `uvicorn app.main:app` 실행 |
| DB 초기화 | `backend/app/main.py:lifespan()` | 앱 시작 시 자동 |
| 시드 데이터 | `backend/app/seed.py:seed_database()` | lifespan 내 호출 |

### 3D 파이프라인
| 진입점 | 파일 | 트리거 |
|--------|------|--------|
| 씬 생성 | `blender/factory_scene.py` | Blender에서 수동 실행 |

## API 라우트 진입점

| 메서드 | 경로 | 라우터 | 설명 |
|--------|------|--------|------|
| GET | /health | main.py | 헬스체크 |
| * | /orders/* | orders.py | 주문 CRUD |
| * | /products/* | orders.py | 제품 조회 |
| * | /production/* | production.py | 생산 로그/상태 |
| * | /quality/* | quality.py | 검사 결과 |
| * | /logistics/* | logistics.py | 이송/창고 |
| * | /alerts/* | alerts.py | 알림 관리 |
| WS | /ws | websocket.py | 실시간 데이터 |

## 빌드/개발 스크립트

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | Next.js 개발 서버 (포트 3000) |
| `npm run build` | 프로덕션 빌드 |
| `npm run start` | 프로덕션 서버 |
| `npm run lint` | ESLint 실행 |
| `uvicorn app.main:app --reload` | FastAPI 개발 서버 (포트 8000) |
