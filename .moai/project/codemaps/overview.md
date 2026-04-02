# 아키텍처 개요

## 시스템 구성

주물공장 관제 시스템은 3개의 독립 레이어로 구성된 풀스택 모노레포 아키텍처:

```
┌─────────────────────────────────────────────────┐
│  Frontend (Next.js 16 + React 19)               │
│  - App Router SPA                               │
│  - Three.js 3D Viewer                           │
│  - Recharts Dashboard                           │
├─────────────────────────────────────────────────┤
│  Backend (FastAPI + SQLAlchemy)                  │
│  - REST API (주문/생산/품질/물류/알림)           │
│  - WebSocket (실시간 상태 갱신)                  │
│  - SQLite DB (시드 데이터)                       │
├─────────────────────────────────────────────────┤
│  3D Pipeline (Blender)                          │
│  - factory_scene.py → GLB export                │
│  - CAD 원본 (STEP/STL)                          │
└─────────────────────────────────────────────────┘
```

## 디자인 패턴

- **프론트엔드**: Component-based SPA, Dynamic Import (SSR 비활성화), Admin Shell 레이아웃 패턴
- **백엔드**: Repository 패턴 (Routes → Models → DB), Lifespan 이벤트 기반 초기화
- **3D**: Blender Python 스크립트 → GLB 정적 에셋 → React Three Fiber 렌더링

## 시스템 경계

| 경계 | 프로토콜 | 설명 |
|------|----------|------|
| Frontend ↔ Backend | HTTP REST / WebSocket | JSON 페이로드 |
| Frontend ↔ 3D Asset | 파일 시스템 (public/) | GLB 로드 |
| Blender ↔ public/ | 오프라인 익스포트 | GLB 생성 |
| Backend ↔ SQLite | SQLAlchemy ORM | 파일 기반 DB |

## 현재 한계

- 프론트엔드가 Mock 데이터를 직접 참조하여 백엔드 API 미연동
- SQLite 리셋 전략으로 인해 데이터 영속성 없음
- 테스트 코드 부재
- 인증/권한 시스템 미구현
