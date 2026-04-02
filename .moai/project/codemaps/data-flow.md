# 데이터 흐름

## 현재 데이터 흐름 (Mock 모드)

```
[사용자 브라우저]
    │
    ▼
[Next.js App Router]
    │
    ├─ page.tsx (대시보드)
    │   ├─ import mockDashboardStats ← lib/mock-data.ts
    │   ├─ import mockAlerts          ← lib/mock-data.ts
    │   ├─ import mockEquipment       ← lib/mock-data.ts
    │   └─ import mockOrders          ← lib/mock-data.ts
    │
    ├─ FactoryMap (2D)
    │   └─ mockEquipment → SVG 렌더링
    │
    ├─ FactoryMap3D (3D)
    │   └─ public/factory-map2.glb → Three.js 씬
    │
    └─ Charts (Recharts)
        └─ mock-data → 차트 데이터
```

## 목표 데이터 흐름 (API 연동 후)

```
[사용자 브라우저]
    │
    ▼
[Next.js App Router]
    │
    ├─ REST API 호출 ──────────────────┐
    │                                   ▼
    │                          [FastAPI Backend]
    │                               │
    │                               ├─ Routes (orders, production, ...)
    │                               │   └─ get_db() → SessionLocal
    │                               │       └─ SQLAlchemy Query
    │                               │           └─ SQLite DB
    │                               │
    │                               └─ Pydantic Schema 검증
    │                                   └─ JSON 응답
    │
    ├─ WebSocket 연결 ─────────────────┐
    │                                   ▼
    │                          [WebSocket Handler]
    │                               └─ 실시간 설비 상태/알림 푸시
    │
    └─ 3D Asset 로드
        └─ public/factory-map2.glb (정적)
```

## 백엔드 요청 라이프사이클

```
HTTP 요청
    │
    ▼
FastAPI Router
    │
    ├─ Pydantic 입력 검증
    │
    ├─ get_db() 의존성 주입
    │   └─ SessionLocal() → SQLAlchemy Session
    │
    ├─ ORM 쿼리 실행
    │   └─ models.py → SQLite
    │
    ├─ Pydantic 응답 직렬화
    │   └─ schemas.py → JSON
    │
    └─ Session.close()
```

## 상태 관리

- **프론트엔드**: 현재 상태 관리 라이브러리 없음 (직접 import). 향후 React Query 또는 SWR 도입 예상
- **백엔드**: Stateless REST API. 세션 상태는 SQLite에 저장
- **WebSocket**: 서버 → 클라이언트 단방향 푸시 (설비 상태 변경 이벤트)
