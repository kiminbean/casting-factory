# 데이터 흐름

> **Last updated**: 2026-04-13 (주문 스텝 재배치, PG 전환 상태 반영)

## 1. 핵심 요청 흐름: 고객 온라인 발주

```mermaid
sequenceDiagram
    actor C as 고객 (브라우저)
    participant NX as Next.js :3000
    participant RW as Rewrite Proxy
    participant FA as FastAPI :8000
    participant PY as Pydantic
    participant SA as SQLAlchemy
    participant DB as PostgreSQL

    Note over C,NX: Step 1: 주문자 정보 입력
    Note over C,NX: Step 2: 제품 선택
    Note over C,NX: Step 3: 사양 입력
    Note over C,NX: Step 4: 견적 확인

    C->>NX: "주문 제출" 클릭 (Step 4→5)
    NX->>NX: validateStep() + 금액 계산
    NX->>RW: POST /api/orders {JSON}
    RW->>FA: POST /api/orders
    FA->>PY: OrderCreate 검증
    PY-->>FA: OK
    FA->>SA: Order(**data)
    SA->>DB: INSERT INTO orders
    DB-->>SA: OK
    SA-->>FA: refresh
    FA-->>NX: 201 + OrderResponse

    NX->>RW: POST /api/orders/{id}/details
    RW->>FA: POST /api/orders/{id}/details
    FA->>PY: OrderDetailCreate 검증
    FA->>SA: OrderDetail(**data)
    SA->>DB: INSERT INTO order_details
    DB-->>FA: OK
    FA-->>NX: 201 + OrderDetailResponse

    NX->>C: Step 5 주문 완료 화면
```

### 데이터 변환 체인

```
[React State (camelCase)]
    │ formData.contactPerson → customer_name
    │ formData.companyName → company_name
    │ formData.phone → contact
    ▼
[fetch() JSON Body (snake_case)]
    │ Next.js Rewrite: /api/* → localhost:8000/api/*
    ▼
[FastAPI Route Handler]
    │ Pydantic OrderCreate.model_dump()
    ▼
[SQLAlchemy Model]
    │ Order(**payload) → db.add() → db.commit()
    ▼
[PostgreSQL Row]
    orders.customer_name, orders.company_name, orders.contact
```

## 2. 관리자 주문 관리 흐름

```mermaid
sequenceDiagram
    actor A as 관리자
    participant OPage as /orders
    participant API as api.ts
    participant FA as FastAPI
    participant DB as PostgreSQL

    A->>OPage: 주문 관리 페이지 접속
    OPage->>API: fetchOrders()
    API->>FA: GET /api/orders
    FA->>DB: SELECT * FROM orders ORDER BY created_at DESC
    DB-->>FA: rows
    FA-->>API: OrderResponse[] (snake_case)
    API->>API: convertKeys() snake→camel
    API-->>OPage: Order[] (camelCase)
    OPage->>A: 주문 목록 렌더링

    A->>OPage: 상태 변경 (승인)
    OPage->>API: updateOrderStatus(id, "approved")
    API->>FA: PATCH /api/orders/{id}/status
    FA->>DB: UPDATE orders SET status='approved'
    DB-->>FA: OK
    FA-->>OPage: 갱신된 Order
```

## 3. 실시간 대시보드 흐름

```mermaid
flowchart LR
    subgraph Backend ["Backend (FastAPI)"]
        WS_ROUTE["/ws/dashboard<br>5초 interval tick"]
        DB[(PostgreSQL)]
        REST["REST API<br>GET /api/*"]
    end

    subgraph Clients ["Clients"]
        WEB[Next.js 대시보드]
        PYQT[PyQt5 모니터링]
    end

    DB -->|SELECT| WS_ROUTE
    DB -->|SELECT| REST
    WS_ROUTE -->|WebSocket push<br>공정·알림·통계| WEB
    WS_ROUTE -->|WebSocket push| PYQT
    REST -->|HTTP Response| WEB
    REST -->|HTTP Response| PYQT
```

> **참고**: 현재 WebSocket은 MQTT 브리지가 아니라, 서버 내부에서 5초마다
> DB를 조회하여 공정 진행·알림·대시보드 통계를 클라이언트로 push하는 구조.
> MQTT 브리지는 `asyncio-mqtt` 의존성이 등록되어 있으나 Phase 2 이후 구현 예정.

## 4. 생산 스케줄링 흐름

```mermaid
flowchart TD
    A[관리자: 주문 선택] --> B[POST /api/production/schedule/calculate]
    B --> C{우선순위 엔진<br>7요소 가중 평가}
    C --> D[PriorityResult 반환<br>점수 + 순위]
    D --> E[관리자: 순위 확인/조정]
    E --> F[POST /api/production/schedule/start]
    F --> G[ProductionJob 생성<br>status=queued]
    G --> H[Order.status → in_production]
    H --> I[공정 시작<br>ProcessStage 업데이트]
```

## 5. 품질 검사 흐름

```
검사 장비 → InspectionRecord INSERT
    │
    ├─ result=pass → SorterLog (정방향) → 포장 스테이션
    │
    └─ result=fail → SorterLog (역방향) → 재작업 라인
         │
         └─ defect_type, defect_detail 기록

통계 집계: GET /api/quality/stats
    → total, passed, failed, defect_rate, defect_types,
      defect_type_codes, inspector_stats
```

## 6. 물류/출고 흐름

```mermaid
flowchart LR
    A[생산 완료] --> B[TransportTask 생성<br>status=unassigned]
    B --> C{AMR 배정}
    C --> D[status=in_progress<br>assigned_robot_id 기록]
    D --> E[WarehouseRack 입고<br>status=occupied]
    E --> F[OutboundOrder 생성]
    F --> G[출고 처리<br>completed=true]
    G --> H[Order.status → shipping_ready<br>shipped_at 자동 기록]
```

## 7. 데이터 소유권 매트릭스

| 도메인 | 생성(Write) | 조회(Read) |
|--------|------------|-----------|
| 주문 (orders) | 고객 웹 (`/customer`) | 관리자 웹 (`/orders`), PyQt5 |
| 주문 상세 (order_details) | 고객 웹 (`/customer`) | 관리자 웹 (`/orders`) |
| 공정 (process_stages) | 시드 / PyQt5 공정 | 관리자 웹 (`/production`), PyQt5 |
| 설비 (equipment) | 시드 / IoT | 관리자 웹 (`/`), PyQt5 |
| 알림 (alerts) | 시드 / IoT / 백엔드 | 관리자 웹 (`/`), PyQt5 |
| 검사 (inspection_records) | 검사 장비 / 시드 | 관리자 웹 (`/quality`), PyQt5 |
| 이송 (transport_tasks) | 관리자 웹 / 시드 | 관리자 웹 (`/logistics`), PyQt5 |
| 창고 (warehouse_racks) | 시드 / 이송 완료 | 관리자 웹 (`/logistics`), PyQt5 |
| 출고 (outbound_orders) | 시드 / 관리자 | 관리자 웹 (`/logistics`) |
| 생산 작업 (production_jobs) | 스케줄러 | 관리자 웹 (`/orders`), PyQt5 |
| 생산 통계 (production_metrics) | 시드 / 집계 | 관리자 웹 (`/production`) |
