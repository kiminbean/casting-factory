# 의존성 관계

## 프론트엔드 의존성 그래프

```
package.json (npm)
├── next@16.2.1 (프레임워크)
├── react@19.2.4 + react-dom@19.2.4
├── three@0.183.2 (3D 엔진)
│   ├── @react-three/fiber@9.5.0 (React 바인딩)
│   └── @react-three/drei@10.7.7 (헬퍼 컴포넌트)
├── recharts@3.8.1 (차트)
├── lucide-react@1.7.0 (아이콘)
├── date-fns@4.1.0 (날짜)
├── clsx@2.1.1 (클래스명)
└── devDependencies
    ├── typescript@5.x
    ├── tailwindcss@4.x + @tailwindcss/postcss
    └── eslint@9 + eslint-config-next
```

## 백엔드 의존성 그래프

```
requirements.txt (pip)
├── fastapi@0.115.0 (웹 프레임워크)
├── uvicorn[standard]@0.30.0 (ASGI 서버)
├── sqlalchemy@2.0.35 (ORM)
├── pydantic@2.9.0 (데이터 검증)
├── websockets@13.0 (WebSocket)
└── python-multipart@0.0.9 (파일 업로드)
```

## 내부 모듈 의존성

### 프론트엔드 (src/)
```
page.tsx
├── components/FactoryMap.tsx
├── components/charts/WeeklyProductionChart.tsx (dynamic import)
├── lib/mock-data.ts
│   └── lib/types.ts
└── lib/utils.ts

FactoryMap3DCanvas.tsx
├── FactoryMap3D.tsx
│   ├── three (GLB 로드)
│   └── @react-three/fiber + drei
└── FactoryMapEditor.tsx
    └── three (편집 기능)

AdminShell.tsx
├── Header.tsx
└── Sidebar.tsx
```

### 백엔드 (backend/app/)
```
main.py
├── database.py (engine, Base, SessionLocal)
├── seed.py
│   └── models/models.py
└── routes/
    ├── orders.py → models/ + schemas/ + database.get_db
    ├── production.py → models/ + schemas/ + database.get_db
    ├── quality.py → models/ + schemas/ + database.get_db
    ├── logistics.py → models/ + schemas/ + database.get_db
    ├── alerts.py → models/ + schemas/ + database.get_db
    └── websocket.py → models/ + database.get_db
```

## 외부 서비스 연동

현재 외부 서비스 연동 없음. SQLite 로컬 DB만 사용.
향후 예상 연동: PLC/센서 데이터 수집, AMR 제어 시스템, 비전 검사 시스템.
