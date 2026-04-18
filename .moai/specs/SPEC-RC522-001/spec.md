---
id: SPEC-RC522-001
version: 0.1.0
status: draft
created: 2026-04-18
updated: 2026-04-18
author: kisoo
priority: medium
issue_number: 0
---

# SPEC-RC522-001: RC522 Stability Regression Test Suite

## HISTORY

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | 2026-04-18 | kisoo | 최초 드래프트 — v1.5.1 RC522 카드 감지 버그 회귀 방지를 위한 3축(자동 회귀 / 수동 체크리스트 / healthcheck 재도입 기준) 스위트 정의 |

## Overview

v1.5.1 (`dd4c4eb`) 에서 수정된 RC522 카드 감지 실패 버그 — 주기 `PCD_ReadRegister(VersionReg)` healthcheck 가 `PICC_IsNewCardPresent()` 를 간섭하던 이슈 — 가 향후 펌웨어 변경에서 다시 발생하지 않도록, **conveyor v5 ESP32 통합 펌웨어** 의 RFID 서브시스템에 대한 반복 실행 가능한 회귀 테스트 프로토콜을 수립한다.

스위트는 세 축으로 구성된다.

1. **자동 회귀 (Jetson HW-in-loop)** — `jetson-conveyor` (Tailscale `100.77.62.67`) 의 `/dev/ttyUSB0` 에서 통합 펌웨어 Serial 로그를 파싱하고, 연속 탭 N 회 동안 UID + NDEF Text 이벤트를 타임박스 내에 방출하는지 검증. "card lost" 회귀 0 건을 통과 조건으로 한다.
2. **수동 하드웨어 체크리스트** — 배선·전원·탭 시퀀스를 10 분 이내에 실행 가능한 형태로 문서화. **Mac USB 브라운아웃** 제약(L298N inrush → Mac USB 5 V 공급 저하 → ESP32 리셋) 을 명시적으로 반영하여, 모터 동반 테스트는 Jetson 또는 외부 12 V 서플라이에서만 수행한다는 절대 규칙을 포함한다.
3. **healthcheck 재도입 기준** — 미래에 주기 `VersionReg` healthcheck 를 다시 켜려는 시도가 있을 때 **먼저 만족해야 하는 공식 acceptance gate** 를 SPEC 계약으로 박제. 계약: "healthcheck 가 켜진 상태에서 100 탭 윈도우 `PICC_IsNewCardPresent` 성공률 ≥ 99 % 를 유지해야만 재도입을 허용한다."

## Requirements Source

- 메모리 `feedback_rc522_healthcheck_bug` — v1.5.1 근본 원인 분석 박제.
- 메모리 `feedback_motor_brownout_mac_usb` — Mac USB 브라운아웃 HARD 제약.
- 메모리 `project_jetson_pipeline` / `reference_jetson_ssh` — Jetson SSH 원격 접속 경로 확정.
- SPEC-AMR-001 L159 — "기존 conveyor_v5_serial 동작 회귀 테스트 통과" acceptance 의 RFID 구현 세부화.
- 커밋 `dd4c4eb` (v1.5.1) — 수정 범위와 실기기 측정치 (30 초 6 회 감지 성공).

## Tech Stack

- 테스트 호스트: Jetson Orin NX (Ubuntu, Tailscale `100.77.62.67`), Python 3 stdlib + `pyserial` 3.5.
- 대상 펌웨어: `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` **v1.5.1** (수정 없음, 블랙박스 검증).
- 보조 스케치: `firmware/rc522_standalone_test/rc522_standalone_test.ino` — healthy baseline 유지. (선택) report mode 카운터가 필요하면 수정.
- 포트: `/dev/ttyUSB0 @ 115200 bps` (`esp_bridge.py` 와 동일). 테스트 실행 중 `jetson_publisher` / `esp_bridge` 프로세스는 **반드시 중지**.
- 대상 언어: Python 3.11+ (stdlib + `pyserial`). 추가 의존성 없음.

## Functional Requirements

본 SPEC 은 요구사항을 **최대 5 개로 캡** 한다 (research.md §7 결정). 모든 요구사항은 EARS 문법을 따른다.

### REQ-RC522-001 (ubiquitous) — 구조화된 실행 리포트

The regression harness SHALL emit a structured pass/fail report per test run identifying at least the following fields: `total_taps`, `successful_uid_reads`, `ndef_parse_successes`, `missed_reads`, `healthcheck_state` (`on` | `off`), `firmware_version` (BOOT 라인에서 추출), `run_duration_seconds`, `exit_code`.

- 리포트는 stdout 에 **JSON 한 줄** 으로 출력되어야 하고, `--report <path>` 옵션이 주어지면 동일 JSON 을 파일에도 기록한다.
- 판정 규칙:
  - UID 성공률 ≥ 99 % (100-탭 윈도우) → `pass`
  - NDEF 성공률 ≥ 95 % (100-탭 윈도우) → `pass`
  - 위 둘 중 하나라도 미달 → exit code 1, `failure_category` 필드 채움.

### REQ-RC522-002 (event-driven) — 100-탭 윈도우 UID 감지율

WHEN the operator taps a known MIFARE card N ≥ 100 consecutive times within a configurable timebox T (default 5 minutes) on the deployed v1.5.1 firmware, the automated harness SHALL report UID detection success rate ≥ **99 %** over any rolling 100-tap window, AND exit with code 0.

- "1 회 탭" 의 정의: 동일 UID 가 `RFID_TAG_HOLD_MS` (700 ms, 펌웨어 L86) 이내에 연속 들어오면 1 회로만 집계. 카드 제거 → 재접근 시 `rfid_clear` 이벤트 후 새로 카운트.
- UID 감지 판정은 **`{"event":"rfid_tag", ...}` JSON 이벤트 수신**을 기준으로 한다. 보조로 `RFID_UID:` 토큰 라인을 cross-check 해도 된다.
- 펌웨어 크래시(BOOT 라인 재출력) 가 1회라도 관측되면 **즉시 실패** 로 집계하고 `firmware_crashed: true` 를 리포트에 기록.

### REQ-RC522-003 (event-driven) — NDEF Text 파싱 성공률

WHEN a NDEF Text record is present on the tapped card AND the card UID is successfully detected (REQ-RC522-002 충족), the harness SHALL verify the Jetson-visible JSON event contains a non-empty `ndef_text` (펌웨어 JSON key `text`) field for ≥ **95 %** of successful UID detections.

- 근거: 펌웨어는 NDEF 파싱이 실패해도 UID 이벤트는 발행한다(`conveyor_v5_serial.ino` L344-363). NDEF 는 설계상 best-effort 이므로 임계값을 UID 보다 낮게 잡는다.
- NDEF 없는 테스트 카드 사용 시: `--ndef-expected=0` 플래그로 이 요구사항을 자동으로 skip. 단, 해당 실행의 리포트는 skip 사유를 명시적으로 기록해야 한다.
- UTF-8 디코딩 실패(부분 깨짐) 는 harness 가 직접 UTF-8 로 decode 해 보고, 실패하면 `ndef_decode_failures` 카운터로 분리 집계 (성공/실패 어느 쪽에도 집계하지 않음).

### REQ-RC522-004 (unwanted-behavior) — healthcheck 재도입 회귀 차단

IF a firmware change re-introduces the periodic `PCD_ReadRegister(VersionReg)` healthcheck (감지 방법: ① `RFID_HEALTHCHECK_MS` 상수가 `pollRfid()` 안에서 **실제로 사용**되거나 ② 런타임에 BOOT 라인 / `rfid_reader` 이벤트가 `"healthcheck":"on"` 플래그를 포함) AND the 100-tap UID detection rate drops below **99 %**, THEN the harness SHALL fail the run with exit code 1 AND emit a regression alert with `failure_category: "healthcheck_regression"` in the report, including a reference to the v1.5.1 root cause commit `dd4c4eb`.

- 하네스는 healthcheck 상태를 **두 가지 방법**으로 추정한다.
  1. **런타임 탐지**: BOOT 라인 또는 `rfid_reader` 이벤트 JSON 에 `healthcheck` 필드가 있으면 그 값 사용.
  2. **정적 `--healthcheck-expected={on|off}` 플래그**: 운영자가 현재 빌드 상태를 명시. 미지정 시 `off` 로 가정 (v1.5.1 기본).
- REQ-RC522-004 는 healthcheck 를 켜려는 개발자가 이 스위트를 **먼저** 돌리도록 강제하는 계약이며, 통과 없이 main 병합을 금지한다 (프로세스 차원, 기술적 강제는 별도 SPEC 에서).

### REQ-RC522-005 (state-driven) — Mac USB 브라운아웃 가드

WHILE the harness detects that it is running on a Mac host (`platform.system() == 'Darwin'`) AND the target serial port begins with `/dev/cu.usbserial` or `/dev/tty.usbserial` (macOS USB serial 패턴), the harness SHALL refuse to issue any motor-affecting command (`RUN`, `STOP`, `start`, `reset`, `sim_entry`, `sim_exit`) over Serial AND SHALL print a visible warning referencing memory `feedback_motor_brownout_mac_usb`, THEN continue in **read-only passive sniff mode** (RFID 이벤트 수신만 수행, 보고는 정상 발행).

- 근거: L298N inrush 로 Mac USB 5 V 가 떨어지면 ESP32 가 리셋되어 BOOT 라인 폭주 및 RFID 세션 초기화가 발생, 회귀 측정 자체가 오염된다.
- 읽기 전용 모드에서도 REQ-RC522-001/002/003 의 자동 탭 집계는 작동해야 한다 (operator 가 수동 탭, 하네스는 로그만 읽음).
- Jetson 호스트에서는 이 가드가 비활성 — 모든 커맨드 허용.

## Acceptance Summary

상세 Given/When/Then 시나리오는 `acceptance.md` 참조. 핵심 3 건 요약:

1. v1.5.1 펌웨어 + Jetson `/dev/ttyUSB0` + 5 분 내 100 탭 → 리포트에 UID 성공 ≥ 99, NDEF 매치 ≥ 95, 크래시 0, exit 0.
2. healthcheck 재도입 빌드 → UID 성공률 99 % 미만 시 exit 1 + `failure_category: "healthcheck_regression"` + `dd4c4eb` 참조.
3. Mac 호스트에서 실행 → 모터 커맨드 refuse + 경고 출력, read-only sniff 로 계속 진행.

## Exclusions (What NOT to Build)

- **Mac 호스트에서 L298N 모터 또는 전체 펌웨어 엔드-투-엔드 테스트** — 브라운아웃 HARD 제약. REQ-RC522-005 가 런타임에 이를 refuse.
- **GitHub Actions / 일반 CI 러너 통합** — 카드 탭은 물리 입력이라 자동화 불가. HW-in-loop 전용.
- **NDEF 스키마 변경** — 현재 `order_{N}_item_{YYYYMMDD}_{seq}` 포맷은 유지. 스키마 변경 SPEC 은 별도 생성.
- **SPEC-AMR-001 핸드오프 플로우 수정** — 이 SPEC 은 기존 AMR 플로우를 건드리지 않음.
- **RC522 태그 ↔ AMR-주문 자동 매칭 로직** — SPEC-AMR-001 L191 에서 이미 별도 SPEC 으로 분리 선언된 범위. 이 SPEC 에 포함 금지.
- **펌웨어 수정** (`conveyor_v5_serial.ino`) — 본 SPEC 은 v1.5.1 을 **블랙박스** 로 검증한다. 수정 필요가 발견되면 별도 SPEC 으로 분리.
- **PostgreSQL / TimescaleDB 접근** — 하네스는 DB 를 읽거나 쓰지 않는다. Serial ↔ stdout JSON 리포트만 다룬다.
- **Confluence 페이지 자동 생성/수정** — 메모리 `feedback_confluence_readonly` 준수. 문서는 로컬 Markdown 만 추가.

## MX Tag Plan

Plan phase 는 코드를 작성하지 않으므로 실제 tag 삽입은 Run phase (`/moai run SPEC-RC522-001`) 에서 수행. 대상·사유를 계약으로 박제한다.

- **@MX:ANCHOR** — 하네스의 최상위 dataclass (예: `RegressionReport`) 가 report loader / CLI / 향후 CI 스크립트 3 곳 이상에서 참조되면(fan_in ≥ 3) 적용. `@MX:REASON: 리포트 스키마는 외부 계약(CI gate, SPEC-AMR-001 회귀 참조)이므로 필드 추가는 요구사항 변경과 동등.`
- **@MX:WARN** — Mac USB 가드 분기 (REQ-RC522-005 구현부) 에 적용. `@MX:REASON: L298N brownout on Mac USB; motor tests require Jetson or external 12V supply. 근거 메모리: feedback_motor_brownout_mac_usb.`
- **@MX:NOTE** — 99 % UID 임계 상수 (예: `UID_SUCCESS_THRESHOLD_PCT = 99.0`) 에 적용. `@MX:REASON: 임계값은 v1.5.1 커밋 dd4c4eb 의 실측(30s / 6 taps / 0 미스) 및 acceptance REQ-RC522-002 계약에 의해 고정. 변경 시 acceptance.md 동기 업데이트 필요.`

(언어: `code_comments: ko` — `.moai/config/sections/language.yaml` 확인.)

## Delta Markers (Brownfield)

| 마커 | 대상 | 비고 |
|------|------|------|
| `[EXISTING]` | `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` @ v1.5.1 | 수정 금지. 회귀 스위트가 블랙박스로 검증 |
| `[EXISTING]` | `jetson_publisher/esp_bridge.py` | 수정 금지. 하네스 실행 중에는 **프로세스 중지** 가 체크리스트 조건 |
| `[NEW]` | `scripts/test_rc522_regression.py` | 하네스 본체 — stdlib + pyserial only |
| `[NEW]` | `docs/testing/rc522_regression_checklist.md` | 수동 운영자 체크리스트 (한국어) |
| `[NEW]` | `docs/testing/` 디렉토리 | 최초 생성 |
| `[MODIFY?]` | `firmware/rc522_standalone_test/rc522_standalone_test.ino` | 카운터/리포트 모드가 필요하다고 판단될 때만. 현재는 보류 |

## Non-Functional Requirements

### 실행 환경

- 기본 호스트: Jetson (`ssh jetson-conveyor`). 원격에서 하네스를 기동할 때 `nohup` / `tmux` 사용 권장 (10 분 이상 실행).
- 의존성 설치 명령 단일화: `pip install --user pyserial==3.5` (Jetson 에는 이미 설치되어 있을 가능성 높음).

### 성능

- 하네스 자체의 연산 오버헤드는 시리얼 수신 라인당 수십 마이크로초 수준이어야 하며, JSON 파싱 실패를 raw line 으로 dump 할 수 있어야 한다 (silent drop 금지).

### 관측성

- stdout 라이브 로그 + 최종 JSON 리포트 두 채널 출력. 로그 레벨은 `--log-level` 플래그로 조정 (`DEBUG`/`INFO`/`WARNING`).
- 리포트 JSON 은 재현을 위한 환경 정보도 포함: host, python 버전, pyserial 버전, firmware BOOT 라인 원문, run timestamp (UTC ISO-8601).

### 호환성

- Python 3.11+ (Jetson 기본 3.10+/Mac dev 3.12). pyserial 3.5 이상.
- 파이썬 표준 라이브러리 (`argparse`, `json`, `time`, `platform`, `datetime`, `pathlib`, `sys`) 외 **추가 의존성 금지**.

## Open Questions (Run phase 에서 해결)

- 기본 탭 카운트 100 이 오퍼레이터 체감 상 10 분 이내에 수행 가능한가? (Operator 시간 측정 필요. 기본값은 유지하고 10 분 초과 시 경고만 띄우는 방향으로 시작.)
- 멀티 카드(2 장 교차) 시나리오를 edge case 로 자동화할지, 수동 체크리스트에만 남길지? → 초안에서는 자동화 안 함 (REQ 범위 축소).
- 하네스 리포트 JSON 을 향후 `.moai/reports/rc522-regression-{DATE}/` 에 보관할지? → 본 SPEC 의 out-of-scope. 별도 operator 운영 결정.

## Change Log

- v0.1.0 (2026-04-18): 초안 작성. REQ 5 개 cap, 3-축 구성 (자동 / 수동 / healthcheck 재도입 계약) 확정.
