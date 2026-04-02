# 기술 스택

## 프론트엔드

| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 16.2.1 | App Router 기반 풀스택 프레임워크 |
| React | 19.2.4 | UI 컴포넌트 라이브러리 |
| TypeScript | 5.x | 타입 안전성 |
| Tailwind CSS | 4.x | 유틸리티 기반 스타일링 |
| Three.js | 0.183.2 | 3D 렌더링 엔진 |
| @react-three/fiber | 9.5.0 | React Three.js 바인딩 |
| @react-three/drei | 10.7.7 | Three.js 헬퍼 컴포넌트 |
| Recharts | 3.8.1 | 차트/그래프 라이브러리 |
| Lucide React | 1.7.0 | 아이콘 라이브러리 |
| date-fns | 4.1.0 | 날짜 포맷팅 |
| clsx | 2.1.1 | 조건부 클래스명 유틸리티 |

## 백엔드

| 기술 | 버전 | 용도 |
|------|------|------|
| FastAPI | 0.115.0 | REST API + WebSocket 서버 |
| Uvicorn | 0.30.0 | ASGI 서버 |
| SQLAlchemy | 2.0.35 | ORM (SQLite 연동) |
| Pydantic | 2.9.0 | 요청/응답 스키마 검증 |
| websockets | 13.0 | WebSocket 실시간 통신 |
| python-multipart | 0.0.9 | 파일 업로드 지원 |

## 데이터베이스

- **SQLite** — 경량 파일 기반 DB (개발/프로토타입용)
- 앱 시작 시 기존 DB 삭제 후 재생성 (스키마 변경 대응)
- 시드 데이터 자동 삽입 (`seed.py`)

## 3D 파이프라인

| 도구 | 용도 |
|------|------|
| Blender | 3D 공장 모델링, GLB 익스포트 |
| GLB/glTF | 3D 모델 전송 포맷 |
| STEP/STL | 로봇팔(MyCobot280) CAD 원본 |

## 개발 환경

| 항목 | 설정 |
|------|------|
| Node.js 패키지 매니저 | npm |
| Python 환경 | venv (backend/venv) |
| 린터 | ESLint 9 (eslint-config-next) |
| CSS 처리 | PostCSS + Tailwind CSS 4 |
| 폰트 | Inter (Google Fonts, next/font) |

## 주요 실행 명령

```bash
# 프론트엔드 개발 서버
npm run dev

# 백엔드 개발 서버
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# 프로덕션 빌드
npm run build && npm run start
```

## API 엔드포인트 구조

| 도메인 | 라우터 | 경로 접두사 |
|--------|--------|------------|
| 주문 | orders.py | /orders, /products |
| 생산 | production.py | /production |
| 품질 | quality.py | /quality |
| 물류 | logistics.py | /logistics |
| 알림 | alerts.py | /alerts |
| 실시간 | websocket.py | /ws |
| 헬스체크 | main.py | /health |

## 주요 설계 결정

1. **Mock 데이터 우선**: 프론트엔드는 `mock-data.ts`로 독립 개발, 백엔드 API 연동은 추후 진행
2. **App Router (Next.js 16)**: 최신 Next.js 16의 App Router + React 19 사용
3. **SQLite 리셋 전략**: 개발 단계에서 스키마 변경 시 DB 자동 삭제/재생성
4. **3D 에셋 분리**: Blender 소스와 빌드 결과물(GLB)을 별도 관리
5. **WebSocket 실시간**: REST API와 함께 WebSocket으로 설비 상태 실시간 푸시
6. **LAN 접근 허용**: `allowedDevOrigins`로 로컬 네트워크 디바이스 접근 지원
