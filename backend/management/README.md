# Management Service (gRPC :50051)

V6 아키텍처의 공장 관제 핵심. FastAPI(Interface Service)와 **별도 프로세스**로 동작하며, Factory Operator PC(PyQt)가 직접 gRPC 로 호출한다.

## 왜 분리했나

- Interface Service 장애 시에도 공장 가동 지속 (SPOF 제거)
- Interface Service AWS 이관 시 현장 PC 설정 변경 없이 공장 운영 유지

상세 설계: [`docs/management_service_design.md`](../../docs/management_service_design.md)

## 빠른 시작

```bash
cd backend/management
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
make proto        # protoc 실행
make run          # server.py 실행 (:50051)
```

## 포함 모듈

| 파일 | 역할 | 상태 |
|---|---|---|
| `server.py` | gRPC 서버 진입점 | 스켈레톤 |
| `proto/management.proto` | API 계약 | 초안 확정 |
| `services/task_manager.py` | 주문 → Task DAG 분해 | 스켈레톤 |
| `services/task_allocator.py` | 로봇 배정 스코어링 | 스켈레톤 |
| `services/traffic_manager.py` | AMR 경로 계획 | 스켈레톤 |
| `services/robot_executor.py` | ROS2/MQTT 지령 | 스켈레톤 |
| `services/execution_monitor.py` | 감시·이벤트 스트림 | 스켈레톤 |

## 환경 변수

| 변수 | 기본값 | 용도 |
|---|---|---|
| `MANAGEMENT_GRPC_HOST` | `0.0.0.0` | 바인딩 주소 |
| `MANAGEMENT_GRPC_PORT` | `50051` | 포트 |
| `MANAGEMENT_DB_URL` | (미설정) | SQLAlchemy URL, Interface Service 와 동일 |

## 클라이언트 예시

PyQt: [`monitoring/app/management_client.py`](../../monitoring/app/management_client.py)

```python
from app.management_client import ManagementClient

c = ManagementClient()                  # :50051
jobs = c.start_production(["ORD-045"])  # 동기 호출
for evt in c.watch_tasks():             # server streaming
    print(evt.task_id, evt.status)
```
