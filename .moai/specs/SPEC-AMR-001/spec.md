# SPEC-AMR-001: 후처리존 주물 인수인계 확인 버튼 (SR-AMR-01 + SR-AMR-02)

## Overview
AMR이 주물을 후처리존에 물리적으로 도착시킨 후, 후처리 작업자가 주물을 하역하고 컨베이어 패널의 A접점 푸시 버튼을 눌러 "인수인계 완료"를 명시적으로 신호하기 전까지 AMR을 대기시켜 작업자-로봇 간 안전한 핸드오프를 보장한다. 버튼 입력은 ESP32 → Jetson → Management Service(gRPC) → DB 체인을 따라 전파되고 AMR FSM이 다음 작업으로 전환된다. 작업자가 실제로 수령했음을 시스템이 알 수 있어야 하며, 센서 오인식이나 타임아웃이 아닌 인간 확인을 완료 신호로 사용한다.

## Requirements Source
- SR-AMR-01: 후처리존 인수인계 확인 (신규 도출) — AMR이 후처리존에 도착한 후 작업자의 명시적 확인 없이는 다음 작업을 수행하지 않는다
- SR-AMR-02: 인수인계 이벤트 감사 추적 (신규 도출) — 모든 핸드오프 확인 이벤트는 시간, 작업자, 대상 AMR/주문과 함께 영구 기록된다

## Tech Stack
- Firmware: ESP32 (conveyor_v5_serial v1.3.0, Arduino 프레임워크, GP33 INPUT_PULLUP)
- Serial Bridge: Jetson Orin NX `jetson_publisher/` Python 3.12, pyserial 3.5
- RPC Layer: gRPC (grpcio 1.59, protobuf) + Management Service (`backend/management/` Python 3.12)
- Persistence: PostgreSQL 16 + TimescaleDB (`100.107.120.14:5432/smartcast_robotics`), SQLAlchemy 2.0 async
- FSM: `backend/management/fsm/` AMR 상태 머신 (기존 구조 확장)
- Monitoring: FastAPI WebSocket + PyQt5 Factory Operator UI (기존 채널)

## Functional Requirements

### FR-AMR-01-01: ESP32 버튼 입력 처리
- EARS: When the postproc-zone A-contact push button is released after a valid press, the ESP32 SHALL emit a `HANDOFF_ACK` token and a JSON event over USB Serial within 100 ms.
- GP33 핀 `INPUT_PULLUP` 사용 (RTC GPIO, strapping-safe). 직접 배선(버튼→ESP32 동일 패널)이므로 외부 풀업 불필요.
- 디바운스: 50 ms. rising edge(버튼 release) 기준 1회 이벤트 발생. 500 ms 이내 연타는 단일 이벤트로 병합.
- 출력 포맷:
  - JSON (stdout): `{"event":"handoff_ack","zone":"postprocessing","ts":<millis>}`
  - 토큰 라인: `HANDOFF_ACK` (Jetson 브릿지 정규식 파서용)
- 기존 컨베이어 상태 머신(TOF/모터)과 완전 독립 — 버튼 로직은 TOF250 판독이나 모터 PWM 제어에 영향을 주지 않는다.

### FR-AMR-01-02: Jetson Serial 브릿지 전달
- EARS: When the Jetson bridge receives a `HANDOFF_ACK` token from the ESP32 serial stream, the system SHALL invoke `ReportHandoffAck` gRPC RPC on Management Service with the source device ID, zone, and event timestamp.
- `jetson_publisher/` 내 Serial 파서에 `HANDOFF_ACK` 토큰 핸들러 추가. 기존 USB Serial 115200 채널(ImagePublisher와 공유) 재사용.
- gRPC 클라이언트 호출 실패 시: 최근 32개 이벤트를 메모리 버퍼에 보관하고 지수 백오프(1s, 2s, 4s, ..., 최대 60s)로 재시도. 60초 초과 시 warning 로그 후 폐기.
- 이벤트 중복 방지: ESP32 `ts` (millis) + `source_device`를 조합한 idempotency key로 사용.

### FR-AMR-01-03: gRPC 계약 정의
- EARS: When Management Service receives a `ReportHandoffAck` RPC, the system SHALL persist the event, attempt to release a waiting AMR task, and return a response indicating outcome within 300 ms.
- `management.proto` 신규 RPC:
  ```proto
  message HandoffAckEvent {
    string source_device = 1;                    // "ESP-CONVEYOR-01"
    string zone = 2;                             // "postprocessing"
    google.protobuf.Timestamp occurred_at = 3;
  }
  message HandoffAckResponse {
    bool accepted = 1;
    string task_id = 2;                          // 해제된 태스크 ID (없으면 빈 문자열)
    string amr_id = 3;                           // 해제된 AMR ID (없으면 빈 문자열)
    string reason = 4;                           // "released" | "orphan_no_waiting_task" | "error"
  }
  rpc ReportHandoffAck(HandoffAckEvent) returns (HandoffAckResponse);
  ```
- 프로토 재생성: `monitoring/scripts/gen_proto.sh` (absolute import → relative import sed 패치 유지).

### FR-AMR-01-04: DB 영속화 (TimescaleDB)
- EARS: When a handoff ACK event arrives at Management Service, the system SHALL insert one row into `handoff_acks` hypertable including task linkage, orphan flag, and metadata.
- 매 이벤트 = 1 row. task_id가 null이면 `orphan_ack=true`로 기록 (경고 로그 동반, FSM 변경 없음).
- 타임스탬프는 gRPC `occurred_at` 기준으로 저장 (네트워크/큐잉 지연 보정).
- 주요 조회 패턴: (zone, ack_at DESC) 인덱스로 최근 이벤트 조회, (task_id) 인덱스로 특정 주문 추적.

### FR-AMR-01-05: AMR FSM 전환
- EARS: When a handoff ACK is accepted and a FIFO-ordered waiting task is found, the system SHALL transition the task from `WAITING_HANDOFF_ACK` to `HANDOFF_COMPLETE` and trigger the next-task dispatcher.
- 신규 FSM 상태 2개 (기존 전송 흐름 중간 삽입):
  - `ARRIVED_POSTPROC` — AMR이 후처리존 도착 보고 즉시 진입
  - `WAITING_HANDOFF_ACK` — `ARRIVED_POSTPROC`에서 자동 전이, 핸드오프 ACK을 무기한 대기
  - `HANDOFF_COMPLETE` — ACK 수신 시 전이. 기존 next-task 할당 로직과 연결됨
- 대기 중 태스크 선택: `SELECT ... FROM transport_tasks WHERE zone='postprocessing' AND status='WAITING_HANDOFF_ACK' ORDER BY arrived_at ASC LIMIT 1` (FIFO).
- 대기 태스크 부재 시: orphan 처리 (FR-AMR-01-04). FSM 변경 없음, gRPC 응답 `orphan_no_waiting_task` 반환.

### FR-AMR-01-06: Monitoring WebSocket 브로드캐스트
- EARS: When an AMR is released by a handoff ACK, the Management Service SHALL broadcast a `handoff.ack` WebSocket message to all subscribed Factory Operator clients within 200 ms.
- 기존 WebSocket 채널 (`/ws/monitoring`) 재사용. 새 메시지 타입 `handoff.ack` 추가.
- 페이로드: `{ "type": "handoff.ack", "task_id": "...", "amr_id": "...", "zone": "postprocessing", "ack_at": "...", "orphan": false }`
- PyQt5 Factory Operator UI에서 수신 시: 대기 중 AMR 목록에서 해당 AMR 제거 + 토스트 알림 표시.

### FR-AMR-01-07: Simulation Affordances (HW-less Testing)
- EARS: When a developer triggers any of three simulation entry points, the system SHALL reproduce the full happy-path downstream chain (DB insert → FSM transition → WebSocket broadcast) identically to a physical button press.
- 물리 버튼 없이 키보드/터미널만으로 전체 파이프라인을 재현하기 위한 3개 주입 지점:

**(a) ESP32 펌웨어: `sim_ack` Serial 커맨드**
- 기존 `sim_entry`/`sim_exit` 패턴을 따라 추가. Arduino IDE Serial Monitor(115200)에서 `sim_ack` 입력 시 실제 버튼 release와 동일한 `HANDOFF_ACK` 토큰 + JSON 이벤트 방출.
- JSON에 `"sim":true` 플래그 포함하여 추적 가능.
- ESP32가 연결돼 있고 버튼만 없는 상황에서 사용.

**(b) Backend 디버그 엔드포인트: `POST /api/debug/handoff-ack`**
- Interface Service (FastAPI, :8000) 에 dev-only 디버그 엔드포인트 추가.
- `APP_ENV=development` 환경변수가 있을 때만 라우터 등록, production에서는 자동 제거 (404 반환).
- Body: `{ "zone": "postprocessing", "source_device": "SIM-KEYBOARD" }`
- 내부적으로 Management Service `ReportHandoffAck` gRPC 호출. 실제 버튼과 동일한 downstream 흐름 실행.
- 전체 HW(ESP32+Jetson) 없이도 Backend+DB+UI 테스트 가능. 일상 개발의 기본 도구.

**(c) Next.js Dev-mode UI 버튼**
- 대시보드 상단에 `process.env.NODE_ENV === 'development'`일 때만 노출되는 "SIM Handoff ACK" 버튼.
- 클릭 시 `POST /api/debug/handoff-ack` 호출. 시각적으로 dev 모드임을 명확히 표시(빨간 테두리 등).
- E2E 데모·시연용.

- 3개 경로 모두 실제 버튼과 **완전히 동일한 downstream 체인**을 트리거해야 한다 — 별도 코드 경로 분기 금지(simulation flag는 tracing/metadata에만 사용).

## Data Models

### 신규 테이블: `handoff_acks` (TimescaleDB hypertable)
```sql
CREATE TABLE handoff_acks (
  id BIGSERIAL,
  task_id UUID REFERENCES transport_tasks(id),
  zone TEXT NOT NULL,
  amr_id TEXT,
  ack_source TEXT NOT NULL,        -- 'esp32_button' | 'gui_override' (future)
  operator_id TEXT,                -- 향후 auth 연동용
  button_device_id TEXT,           -- 'ESP-CONVEYOR-01'
  orphan_ack BOOLEAN DEFAULT FALSE,
  metadata JSONB,
  ack_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_hypertable('handoff_acks', 'ack_at');
CREATE INDEX ON handoff_acks (zone, ack_at DESC);
CREATE INDEX ON handoff_acks (task_id);
```

### 기존 테이블 수정: `transport_tasks.status` enum 확장
추가 값:
- `WAITING_HANDOFF_ACK` — AMR이 후처리존 도착 후 작업자 확인 대기 중
- `HANDOFF_COMPLETE` — 작업자 확인 수신, 다음 태스크 할당 대기 중

기존 값(`PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` 등)은 유지. 마이그레이션 스크립트에서 enum ALTER TYPE ADD VALUE로 추가.

### Proto Messages (management.proto)
```proto
message HandoffAckEvent {
  string source_device = 1;
  string zone = 2;
  google.protobuf.Timestamp occurred_at = 3;
}

message HandoffAckResponse {
  bool accepted = 1;
  string task_id = 2;
  string amr_id = 3;
  string reason = 4;    // "released" | "orphan_no_waiting_task" | "error"
}
```

## API / RPC

| Protocol | Method | Path/Name | Description |
|----------|--------|-----------|-------------|
| gRPC | unary | `ManagementService.ReportHandoffAck` | Jetson → Management. 버튼 이벤트 보고 및 AMR 태스크 해제 |
| WebSocket | broadcast | `/ws/monitoring` (message type: `handoff.ack`) | Management → PyQt 클라이언트. AMR 해제 알림 |

## Acceptance Criteria
- [ ] Happy path: 후처리존에 AMR 도착 → `WAITING_HANDOFF_ACK` 전이 → 작업자 버튼 누름 → 500 ms 이내 `HANDOFF_COMPLETE` 전이 + 다음 태스크 할당
- [ ] DB 영속화: 버튼 이벤트당 `handoff_acks` 테이블에 1 row 생성, `task_id`/`zone`/`ack_at` 정상 기록
- [ ] Orphan 처리: 대기 AMR 없이 버튼 누름 → `orphan_ack=true` row 생성 + warning 로그 + gRPC 응답 `orphan_no_waiting_task`, FSM 상태 변경 없음
- [ ] Debounce: 500 ms 이내 연속 2회 버튼 입력 → ESP32가 단일 이벤트로 처리 (Serial 로그 1회, DB row 1개)
- [ ] FIFO 순서: 후처리존에 AMR 2대 가상 대기 상황에서 버튼 누름 → 가장 오래된 `arrived_at` 태스크 우선 해제
- [ ] 네트워크 복원성: Management Service 중단 상태에서 버튼 5회 누름 → Jetson 메모리 버퍼 유지 → Management 복구 시 지수 백오프로 5회 모두 재전송 성공
- [ ] 버퍼 한계: Management Service 60초 이상 중단 → 초과분 이벤트는 warning 로그 후 폐기 (버퍼 오버플로우 크래시 없음)
- [ ] WebSocket 브로드캐스트: `handoff.ack` 수신 후 200 ms 이내 PyQt 클라이언트가 토스트 표시 + 대기 목록에서 AMR 제거
- [ ] Idempotency: 동일 `(source_device, ts)` 조합 이벤트를 재전송해도 DB row 중복 생성되지 않음
- [ ] ESP32 독립성: 버튼 누름이 컨베이어 TOF250 판독/모터 PWM 제어에 영향 주지 않음 (기존 conveyor_v5_serial 동작 회귀 테스트 통과)
- [ ] ESP32 sim: Serial Monitor에서 `sim_ack` 입력 시 실제 버튼과 동일한 `HANDOFF_ACK` 토큰 + JSON 이벤트 발행 (`"sim":true` 플래그 포함)
- [ ] Backend debug: `APP_ENV=development` 환경에서 `POST /api/debug/handoff-ack` 호출 시 DB insert + FSM 전이 + WebSocket 브로드캐스트까지 실제와 동일하게 실행됨 (production 환경에서는 404 반환)
- [ ] UI sim: 개발 빌드에서 대시보드 "SIM Handoff ACK" 버튼 클릭 → 500ms 이내 WebSocket 수신 및 UI 반영 (production 빌드에는 버튼 미노출)

## Non-Functional Requirements

### 지연 시간
- 버튼 누름(release)부터 AMR 해제(gRPC 응답)까지 **end-to-end p95 < 500 ms**
  - ESP32 이벤트 방출: < 100 ms (디바운스 포함)
  - Jetson → Management gRPC: < 50 ms (LAN 내부)
  - DB insert + FSM 전이: < 150 ms
  - WebSocket 브로드캐스트: < 200 ms
- p99 < 1 초 (GC/쿼리 변동 허용 범위)

### 신뢰성
- Jetson 측 메모리 버퍼: 최근 32개 이벤트 보관, 지수 백오프 1s→60s
- Idempotency key: `(source_device, event_ts_millis)` — 재전송 시 DB 중복 방지
- gRPC 서버 재시작 중에도 버퍼링으로 무손실 전달 (60초 이내 복구 전제)
- DB 장애 시 Management Service는 gRPC 에러 반환 → Jetson 재시도 대상에 포함

### 감사 추적
- 모든 버튼 이벤트는 `handoff_acks`에 영구 기록 (orphan 포함)
- `button_device_id`로 어떤 ESP32가 발신했는지 추적 가능
- 향후 `operator_id` 필드 채움 시 누가 확인했는지 추적 가능 (auth 연동 시점)
- TimescaleDB 압축 정책: 30일 이후 자동 압축 (기존 hypertable 정책 재사용)

### 보안
- gRPC mTLS 기존 Management Service 설정 재사용 (S-002 인증 스킴)
- ESP32 Serial 링크는 물리적 보안 경계(공장 내부) 내 가정

## Out of Scope
- RC522 태그 기반 AMR-주문 자동 매칭 (별도 SPEC으로 분리)
- 인수인계 ACK을 후처리존 외 다른 존(casting, inspection 등)으로 일반화
- GUI(PyQt) Supervisor Override 버튼 — 향후 `ack_source='gui_override'`를 위한 필드만 스키마에 예약
- `operator_id` 자동 채움 (auth/로그인 연동 필요, 별도 이니셔티브)
- ESP32 → Jetson Serial 링크 이중화 (단일 USB 전제)

## Open Questions
- `operator_id` 채움 방식과 타이밍: 공장 작업자 NFC 태그 리더 추가 도입 시점에 따라 결정 (현재 미정, 스키마에 nullable 컬럼만 확보)
- Supervisor Override 도입 시 동일 `handoff_acks` 테이블 재사용 vs 별도 감사 로그 분리 (향후 결정)

## Implementation Plan (Preview)
1. **ESP32 firmware update** (`firmware/conveyor_v5_serial/conveyor_v5_serial.ino`): GP33 `INPUT_PULLUP` 핀 설정, 50 ms 디바운스 + rising edge 검출 로직 추가, JSON + `HANDOFF_ACK` 토큰 이벤트 방출, `sim_ack` Serial 커맨드 추가. TOF/모터 루프에 영향 없음을 회귀 검증.
2. **wiring_diagram.html update** (`firmware/conveyor_controller/wiring_diagram.html`): 후처리존 A접점 푸시 버튼 섹션 추가, GP33 핀 표시, 배선 도표 갱신.
3. **SQL migration** (`backend/scripts/migrate_handoff_acks.sql` 신규): `handoff_acks` hypertable 생성, `transport_tasks.status` enum에 `WAITING_HANDOFF_ACK`/`HANDOFF_COMPLETE` 추가, 인덱스 생성. (이 프로젝트는 Alembic 대신 `backend/scripts/migrate_*.sql` 직접 실행 패턴 사용)
4. **management.proto regeneration** (`backend/management/proto/management.proto` + `monitoring/scripts/gen_proto.sh`): `HandoffAckEvent`/`HandoffAckResponse` 메시지 + `ReportHandoffAck` RPC 추가, 양측 stub 재생성.
5. **Management Service gRPC handler + FSM transition** (`backend/management/services/`, `backend/management/server.py`): `ReportHandoffAck` 구현, FIFO 쿼리, FSM 상태 전이 (`ARRIVED_POSTPROC` → `WAITING_HANDOFF_ACK` → `HANDOFF_COMPLETE`), orphan 분기, WebSocket 브로드캐스트 연동. (신규 `fsm/`·`handlers/` 디렉토리 대신 기존 `services/` 구조 확장)
6. **Jetson bridge Serial parser + gRPC client** (`jetson_publisher/esp_bridge.py`, `jetson_publisher/publisher.py`): `HANDOFF_ACK` 토큰 정규식 매처 추가, 메모리 버퍼(32) + 지수 백오프 재시도, idempotency key 생성.
7. **Monitoring WebSocket event + PyQt dashboard** (`monitoring/app/`): `handoff.ack` 메시지 타입 핸들러 추가, 대기 AMR 목록 업데이트 + 토스트 알림 컴포넌트 연결.
8. **Simulation affordances** (cross-layer): Backend FastAPI에 `POST /api/debug/handoff-ack` dev-only 라우터 추가 (`backend/app/routes/debug.py` 신규, `APP_ENV=development` gated). Next.js 대시보드 `src/components/` 에 DEV 전용 "SIM Handoff ACK" 버튼 추가 (`process.env.NODE_ENV==='development'` 조건 렌더).

## Changelog
- v1.1 (2026-04-17): FR-AMR-01-07 Simulation Affordances 추가 (ESP32 sim_ack / Backend debug endpoint / UI dev button), Implementation Plan 경로 교정 (alembic→scripts, handlers/fsm→services), 8번째 step 추가
- v1.0 (2026-04-17): 초기 작성 — EARS 6개 FR, handoff_acks hypertable, gRPC ReportHandoffAck, 7단계 구현 계획
