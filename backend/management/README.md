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
| `services/traffic_manager.py` | AMR 경로 계획 (Waypoint+Dijkstra+Backtrack Yield) | ✅ Phase 6 완료 |
| `services/robot_executor.py` | ROS2/MQTT 지령 | 스켈레톤 |
| `services/execution_monitor.py` | 감시·이벤트 스트림 | 스켈레톤 |

## 환경 변수

| 변수 | 기본값 | 용도 |
|---|---|---|
| `MANAGEMENT_GRPC_HOST` | `0.0.0.0` | gRPC 바인딩 주소 |
| `MANAGEMENT_GRPC_PORT` | `50051` | gRPC 포트 |
| `MGMT_MQTT_HOST` | `localhost` | MQTT 브로커 (Robot Executor publish 용) |
| `MGMT_MQTT_PORT` | `1883` | MQTT 포트 |
| `MGMT_MQTT_QOS` | `1` | publish QoS |
| `MGMT_MQTT_CLIENT_ID` | `casting-mgmt-executor` | MQTT client id |

DATABASE_URL 은 `backend/.env.local` 에서 자동 로딩 (Interface Service 와 공유).

## V6 통신 채널 (어댑터 라우팅)

`robot_id` prefix 가 단일 진실. `services/adapters/` 하위에서 분기:

| robot_id prefix | 어댑터 | 채널 | 대상 |
|---|---|---|---|
| `AMR-*` | `ros2_adapter` | 🟢 ROS2 DDS | Transport (RPi4) |
| `ARM-*` | `ros2_adapter` | 🟢 ROS2 DDS | Manufacturing/Stacking (RPi5) |
| `CONV-*` | `mqtt_adapter` | 🔵 MQTT | HW Control Service (ESP32 컨베이어) |
| `ESP-*` | `mqtt_adapter` | 🔵 MQTT | HW Control Service (기타 ESP32) |
| 그 외 | `unknown` | (거부) | `unknown_robot_prefix` 에러 |

### MQTT (ESP32) 토픽 표준

| 방향 | Topic | 비고 |
|---|---|---|
| Server → ESP32 | `casting/esp/{robot_id}/cmd` | V6 표준 |
| ESP32 → Server | `casting/esp/{robot_id}/status` | (구독자 별도 구현 예정) |
| ESP32 → Server | `casting/esp/{robot_id}/event` | 이벤트 단발 |
| 레거시 호환 (옵션) | `conveyor/{robot_id}/cmd` | `MGMT_MQTT_LEGACY_CONVEYOR=1` 시 동시 publish |

Payload (JSON):
```json
{ "command": "start", "item_id": 200, "robot_id": "ESP-001",
  "issued_at": "2026-04-14T...", "payload": {"rate_hz": 5} }
```

### ROS2 토픽 / 액션 표준 (배포 시점에 활성)

| 대상 | Endpoint | 메시지 |
|---|---|---|
| AMR navigate | Action `/{robot_id}/navigate_to_pose` | `nav2_msgs/NavigateToPose` |
| ARM move | Action `/{robot_id}/move_to` (custom) | `casting_msgs/MoveTo` (TBD) |
| 일반 명령 | Topic `/{robot_id}/cmd` | `std_msgs/String` (JSON payload) |

활성화: `MGMT_ROS2_ENABLED=1` + Ubuntu 24.04 + ROS2 Jazzy + `rclpy` 설치.

### Image Publishing (Jetson → Server)

| Endpoint | 프로토콜 | 메시지 |
|---|---|---|
| `ImagePublisherService/PublishFrames` | gRPC client streaming :50051 | `ImageFrame` (camera_id, encoding, width, height, data, sequence) |

이미지 수신은 `services/image_sink.py` 의 글로벌 `sink` 가 카메라별 최신 1프레임 보관.

## 클라이언트 예시

PyQt: [`monitoring/app/management_client.py`](../../monitoring/app/management_client.py)

```python
from app.management_client import ManagementClient

c = ManagementClient()                  # :50051
jobs = c.start_production(["ORD-045"])  # 동기 호출
for evt in c.watch_tasks():             # server streaming
    print(evt.task_id, evt.status)
```
