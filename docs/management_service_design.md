# Management Service 설계 (V6 아키텍처)

> 작성: 2026-04-14 · 버전: 0.1 (초안)
> 기반 문서: `docs/fms_architecture_v2.html`, v6 아키텍처 이미지

---

## 1. 배경 및 결정 사항

### 1.1 문제 진술

기존 casting-factory 아키텍처는 FastAPI 백엔드가 Interface Service + Management Service 역할을 **한 프로세스에서 겸임**하고 있었다. 이 경우 아래 리스크가 존재한다.

| 리스크 | 영향 |
|---|---|
| FastAPI 프로세스 다운 | 공장 가동 즉시 정지 (SPOF) |
| FastAPI AWS 이관 중 | 현장 PyQt 클라이언트 접속 설정 변경 + 공장 일시 정지 |
| UI 프로토콜과 HW 프로토콜의 혼재 | 인증/방화벽/스케일링 정책 수립 난해 |

### 1.2 결정 (2026-04-14 팀 합의)

| 항목 | 결정 |
|---|---|
| Management Service 독립 프로세스화 | **확정** |
| 프로토콜 | **gRPC (Protocol Buffers)** |
| 포트 | **50051** |
| 네트워크 | 공장 내부망 전용 (외부 노출 금지) |
| PyQt (Factory Operator PC) 연결 | **Management Service 직결** (Interface Service 경유 금지) |
| Admin / Customer PC | Interface Service(FastAPI HTTP) 유지 |
| DB | Interface Service 와 동일 DB 공유 (PostgreSQL 16 + TimescaleDB **단독**, SQLite 폴백 제거 2026-04-14) |

### 1.3 배치 구조

```
공장 내부망 (Tailscale / LAN)                  AWS 또는 온프레미스
───────────────────────────                   ──────────────────
Factory Operator PC (PyQt)                    Admin / Customer PC
      │                                             │
      │ gRPC :50051                                 │ HTTPS :443
      ▼                                             ▼
┌──────────────────────────┐              ┌─────────────────────┐
│ Management Service        │ ◀─ gRPC ──▶  │ Interface Service   │
│ (관제 두뇌 · HW 제어)      │              │ (FastAPI · 외부 API) │
└────────┬─────────────────┘              └──────────┬──────────┘
         │                                            │
         └─────────── 공유 DB (PostgreSQL) ───────────┘

         │
         ├─ ROS2 DDS → Manufacturing / Stacking / Transport
         └─ MQTT     → HW Control (ESP32 Conveyor 등)
```

---

## 2. gRPC API 정의

`backend/management/proto/management.proto` 참조.

### 2.1 서비스 메서드 요약

| RPC | 유형 | 용도 | 소비자 |
|---|---|---|---|
| StartProduction | unary | 주문 → 생산 Job + Task 분해 | PyQt [▶ 생산 시작] |
| ListTasks | unary | 진행 중 Task 조회 | PyQt 테이블 갱신 |
| AllocateTask | unary | 로봇 배정 스코어링 | 내부 또는 재배정 요청 |
| PlanRoute | unary | AMR 경로 계획 | 내부 (Executor) |
| ExecuteCommand | unary | ROS2/MQTT 지령 송출 | 내부 |
| WatchTasks | **server streaming** | Task 상태 실시간 푸시 | PyQt 실시간 UI |
| Health | unary | 헬스체크 | 로드밸런서 / systemd |

### 2.2 주요 메시지

- `ProductionJob` — id, order_id, priority_rank, status, tasks[]
- `Task` — id, item_id (A-1 등), stage (대기/주탕/…), required_robot_type, assigned_robot_id
- `TaskEvent` — 스트리밍 이벤트 (id, status, robot_id, message, at)

---

## 3. 내부 모듈 (5개)

모두 `backend/management/services/` 에 위치.

| 모듈 | 파일 | 상태 | 책임 |
|---|---|---|---|
| Task Manager | task_manager.py | 스켈레톤 | 주문 → item → Task DAG 분해 (item당 10 Task) |
| Task Allocator | task_allocator.py | 스켈레톤 | 거리·capability·배터리 스코어링으로 로봇 배정 |
| Traffic Manager | traffic_manager.py | 스켈레톤 | Waypoint/Edge 경로 계획 + Backtrack Yield |
| Robot Executor | robot_executor.py | 스켈레톤 | ROS2 Action Client + MQTT publish |
| Execution Monitor | execution_monitor.py | 스켈레톤 | 타임아웃·재시도·이벤트 스트리밍 |

---

## 4. 디렉터리 구조

```
backend/
├── app/                          ← Interface Service (기존 FastAPI)
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── schemas/
│
├── management/                   ← Management Service (신규)
│   ├── server.py                 ← gRPC 서버 진입점
│   ├── proto/
│   │   └── management.proto
│   ├── services/
│   │   ├── task_manager.py
│   │   ├── task_allocator.py
│   │   ├── traffic_manager.py
│   │   ├── robot_executor.py
│   │   └── execution_monitor.py
│   ├── requirements.txt
│   └── Makefile
│
└── casting_factory.db

monitoring/
└── app/
    ├── management_client.py      ← PyQt gRPC client (신규)
    ├── generated/                ← protoc 산출물 (git ignore)
    │   ├── management_pb2.py
    │   └── management_pb2_grpc.py
    ├── api_client.py             ← 기존 HTTP 클라이언트 (WebSocket + 레거시 조회 전용으로 축소)
    └── pages/
```

---

## 5. 실행 방법

### 5.1 Management Service 기동

```bash
cd backend/management
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# proto 컴파일 (management_pb2.py, management_pb2_grpc.py 생성)
make proto

# 실행
MANAGEMENT_GRPC_PORT=50051 python server.py
```

systemd 서비스 파일 예시 (`/etc/systemd/system/casting-management.service`):

```ini
[Unit]
Description=Casting Factory Management Service (gRPC)
After=network.target

[Service]
WorkingDirectory=/opt/casting-factory/backend/management
ExecStart=/opt/casting-factory/backend/management/venv/bin/python server.py
Environment="MANAGEMENT_GRPC_PORT=50051"
Environment="MANAGEMENT_DB_URL=postgresql+psycopg://..."
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 5.2 PyQt 클라이언트 측

```bash
cd monitoring
source venv/bin/activate

# 서버 쪽 proto 를 공유 (symlink 또는 복사) 후 컴파일
mkdir -p app/generated
python -m grpc_tools.protoc \
  -I ../backend/management/proto \
  --python_out=app/generated \
  --grpc_python_out=app/generated \
  ../backend/management/proto/management.proto

MANAGEMENT_GRPC_HOST=localhost python main.py
```

---

## 6. PyQt 쪽 이관 계획

### 6.1 기존 api_client.py 재정의

| 기능 | 현재 | 이후 |
|---|---|---|
| 주문 조회 | HTTP GET | **Management gRPC ListOrders** (신규 RPC 필요) |
| 승인 주문 풀 | HTTP GET /api/production/schedule/approved | **Management gRPC ListTasks** |
| 생산 시작 | HTTP POST /api/production/schedule/start | **Management gRPC StartProduction** |
| 실시간 상태 | WebSocket /ws/dashboard | **Management gRPC WatchTasks (streaming)** |
| 품질 검사 이력 | HTTP GET /api/quality/inspections | Interface Service 유지 또는 Management 이전 |

> **WebSocket 제거**는 2단계 권장. 먼저 gRPC WatchTasks 를 병행 동작시킨 뒤 검증 완료 시 WebSocket 단종.

### 6.2 QThread + gRPC 통합 패턴

```python
# app/workers/management_worker.py
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from app.management_client import ManagementClient

class TaskStreamWorker(QObject):
    event_received = pyqtSignal(object)  # TaskEvent

    def __init__(self, client: ManagementClient, order_id: str | None):
        super().__init__()
        self._client = client
        self._order_id = order_id

    def run(self):
        for event in self._client.watch_tasks(self._order_id):
            self.event_received.emit(event)
```

---

## 7. Interface Service 쪽 이관 계획

FastAPI routes 는 점진적으로 **gRPC proxy** 로 축소된다.

```python
# backend/app/routes/schedule.py (이관 후)
from app.clients.management import get_management_client

@router.post("/start")
async def start_production(payload: StartRequest):
    client = get_management_client()
    resp = client.StartProduction(
        management_pb2.StartProductionRequest(order_ids=payload.order_ids)
    )
    return {"jobs": [MessageToDict(j) for j in resp.jobs]}
```

Interface Service 자체 로직은 **인증 / rate-limit / 외부 API 게이트웨이** 역할에 집중.

---

## 8. 마이그레이션 단계별 로드맵

| 단계 | 기간 | 산출 | 완료 조건 |
|---|---|---|---|
| **Phase 0 — 스캐폴드 (완료)** | 0.5일 | 본 문서 + proto + 스켈레톤 | 디렉터리 생성, proto 정의 |
| **Phase 1 — gRPC 서버 기동** | 1일 | Health RPC + Task Manager 기본 | `grpc_health_probe` 성공 |
| **Phase 2 — StartProduction 이전** | 1일 | `task_manager.start_production` 실구현 | PyQt → gRPC 로 생산 개시 성공 |
| **Phase 3 — WatchTasks 스트리밍** | 1일 | `execution_monitor.stream` 실구현 | PyQt 가 실시간 이벤트 수신 |
| **Phase 4 — Interface proxy** | 0.5일 | routes/schedule.py 가 gRPC client 로 동작 | Admin/Customer 영향 없음 확인 |
| **Phase 5 — Robot Executor + HW 연동** | ✅ 어댑터 분리 완료 (2026-04-14) | ros2_adapter (인터페이스) + mqtt_adapter (ESP32) + ImagePublisherService (gRPC streaming) | V6 통신 행렬 부합, RPi 배포 시 ROS2 활성화만 남음 |
| **Phase 6 — Traffic Manager 구현** | ✅ 완료 (2026-04-14) | 8 노드 / 8 edge Waypoint + Dijkstra + Edge time-window 예약 + Backtrack Yield (3단계 우회→대기) | 단위 테스트 5종 + gRPC PlanRoute E2E 통과 |
| **Phase 7 — Execution Monitor 고도화** | 1일 | 타임아웃·재시도·alerts 통합 | 장애 테스트 통과 |
| **Phase 8 — WebSocket 단종** | 0.5일 | PyQt 에서 ws_worker 제거 | gRPC streaming 만으로 UI 동작 |

총 예상 작업량: **약 9일 (1인 기준)**

---

## 9. 보안 / 운영 고려사항

| 항목 | 정책 |
|---|---|
| 네트워크 | 공장 내부망 전용. 외부 방화벽 50051 차단 |
| 인증 | 현 시점 insecure channel. 운영 전환 시 mTLS 도입 권장 |
| 로깅 | Python logging → journald → 집계 (loki/ELK) |
| 메트릭 | grpc-prometheus exporter (옵션) |
| 재기동 | systemd `Restart=on-failure`, 헬스체크 5초 주기 |
| 배포 | Interface Service 는 CD, Management Service 는 현장 수동 배포 (리스크 관리) |

---

## 10. 미결정 사항 (후속 논의 필요)

- [ ] Management 와 Interface 의 공유 DB 접근에서 **쓰기 경합 처리** 방식 (advisory lock vs. 서비스 책임 분리)
- [ ] PyQt 측 gRPC 연결 실패 시 **오프라인 모드** 동작 범위
- [ ] `ExecuteCommand.payload` 에 담을 JSON/Proto 스키마의 구체화
- [ ] ROS2 / MQTT 브릿지의 **세션 재사용** 전략 (rclpy 컨텍스트 공유)
- [ ] AI Service 가 생기면 Task Allocator 가 gRPC 로 호출할지, 내부 호출로 임베드할지

---

## 11. 변경 이력

| 일자 | 내용 |
|---|---|
| 2026-04-14 | 초안 작성 (gRPC:50051 결정 반영) |
