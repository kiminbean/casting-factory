# 데이터 흐름

> **Last updated**: 2026-04-17 (SPEC-AMR-001 후처리존 핸드오프 ACK 흐름 추가)

## 0. V6 핵심 흐름: Factory PC PyQt → Management Service gRPC

```mermaid
sequenceDiagram
    actor U as Factory Operator
    participant Q as PyQt5 (Python 3.12)
    participant MC as ManagementClient
    participant MS as Management Service<br>(gRPC :50051)
    participant TM as TaskManager
    participant DB as PostgreSQL<br>100.107.120.14:5432
    participant EM as ExecutionMonitor<br>(BG thread)

    Note over U,Q: 생산 계획 페이지 [▶ 생산 시작] 클릭
    Q->>MC: start_production([order_ids])
    MC->>MS: gRPC StartProduction(order_ids)
    MS->>TM: start_production()
    TM->>DB: SELECT orders WHERE status='approved'
    TM->>DB: INSERT work_orders, items×qty
    TM->>DB: UPDATE orders.status='in_production'
    DB-->>TM: OK
    TM-->>MS: List[WorkOrder]
    MS-->>MC: StartProductionResponse
    MC-->>Q: List[WorkOrderInfo]
    Q->>U: 메시지박스 "N건 WorkOrder 생성, M items"

    Note over EM,DB: 별도 thread 1초 polling
    EM->>DB: SELECT items (snapshot diff)
    EM->>DB: INSERT alerts (SLA 위반 시)

    Note over Q,MS: 동시: WatchItems / WatchAlerts streaming
    Q->>MS: WatchItems(order_id) + WatchAlerts(severity)
    MS-->>Q: stream ItemEvent (1초 내)
    MS-->>Q: stream AlertEvent (1초 내)
    Q->>U: 셀 마커 이동 + 토스트 알림
```

## 0.1 V6 HW 통신 채널 (Adapter 라우팅)

```mermaid
flowchart LR
    EX[ExecuteCommand RPC] --> RT{robot_id prefix}
    RT -->|AMR-* / ARM-*| ROS[ros2_adapter<br>MGMT_ROS2_ENABLED=1<br>RPi 배포 시]
    RT -->|CONV-* / ESP-*| MQTT[mqtt_adapter<br>casting/esp/&#123;id&#125;/cmd]
    RT -->|UNKNOWN| ERR[unknown_robot_prefix<br>거부]

    ROS -->|nav2 Action| AMR[AMR/Cobot RPi]
    MQTT -->|paho-mqtt :1883| ESP[ESP32 펌웨어]

    IMG[Image Publisher<br>Jetson] -->|PublishFrames<br>gRPC client stream| SINK[image_sink<br>최신 1프레임 메모리]
```

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

## 6.1 후처리존 인수인계 ACK (SPEC-AMR-001, 2026-04-17)

AMR 이 postproc zone 에 도착한 후, 작업자가 주물을 하역하고 컨베이어 ESP32 의
A접점 푸시 버튼을 누르기 전까지 AMR 은 다음 TASK 로 진행하지 않는다. 버튼
이벤트는 다음 체인으로 전파되어 DB 에 영구 기록된다.

```mermaid
sequenceDiagram
    actor W as 후처리 작업자
    participant BTN as A접점 푸시 버튼<br>(GP33 INPUT_PULLUP)
    participant ESP as ESP32 conveyor v1.4.0
    participant JP as Jetson esp_bridge<br>(pyserial + grpc)
    participant MS as Management Service<br>(gRPC :50051)
    participant DB as PostgreSQL<br>handoff_acks
    participant FSM as AMR FSM<br>(in-memory)
    participant FA as FastAPI<br>(WS broker)
    participant UI as Next.js / PyQt5

    W->>BTN: 주물 하역 후 버튼 press
    BTN->>ESP: LOW (INPUT_PULLUP)
    ESP->>ESP: 디바운스 50ms + rising edge
    ESP->>JP: Serial: "HANDOFF_ACK\n" + JSON
    JP->>JP: 큐 적재 (deque maxlen=32)
    JP->>MS: gRPC ReportHandoffAck
    MS->>FSM: find_waiting_amr_at_zone("postprocessing")
    MS->>DB: INSERT handoff_acks (idempotency_key)
    MS->>DB: UPDATE transport_tasks SET status='handoff_complete'
    MS->>FSM: confirm_handoff<br>AT_DESTINATION → UNLOAD_COMPLETED
    MS->>FA: HTTP POST /api/debug/_notify/handoff-ack
    FA->>UI: WebSocket {type:"handoff.ack"}
    MS-->>JP: HandoffAckResponse(task_id, amr_id, reason)
    UI->>W: 상태바 토스트 / 대시보드 갱신
```

**시뮬레이션 경로 (HW 없이 테스트)**:
- **ESP32**: Serial Monitor 에서 `sim_ack` → 실제 버튼과 동일 이벤트
- **Backend**: `curl -X POST /api/debug/handoff-ack` → DB + WS 직접 트리거
- **Next.js DEV**: 우하단 "🔴 SIM Handoff ACK" 버튼 (`NODE_ENV=development` 전용)

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
| 핸드오프 ACK (handoff_acks) | ESP32 버튼 / Mgmt gRPC / debug REST | 관리자 웹 (/api/debug/handoff-acks/recent), PyQt5 (WS) |
