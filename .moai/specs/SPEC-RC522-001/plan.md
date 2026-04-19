# SPEC-RC522-001 · Implementation Plan

**대상 SPEC**: `.moai/specs/SPEC-RC522-001/spec.md` (v0.1.0)
**모드**: Plan phase 출력물. 실제 코드 작성은 Run phase (`/moai run SPEC-RC522-001`) 에서 수행.
**메서돌로지**: `quality.yaml` 의 `development_mode` 값을 따른다 (casting-factory 는 DDD 또는 TDD, 확인 후 Run 시 Skill 선택).

---

## 1. Task Decomposition

우선순위 라벨: **High / Medium / Low** (시간 예측 없음).

### Task 1 (High) · 하네스 본체 뼈대

- 파일: `scripts/test_rc522_regression.py` **[NEW]**
- 내용: CLI 인자 정의 + Serial open + 라인 리더 루프 + dataclass 기반 리포트 스키마.
- 입력 플래그 (초안, Run phase 에서 조정 가능):
  - `--port` (기본 `/dev/ttyUSB0`)
  - `--baud` (기본 `115200`)
  - `--taps` (기본 `100`, REQ-RC522-002)
  - `--timeout` (기본 `300` 초 = 5 분, REQ-RC522-002)
  - `--uid-threshold` (기본 `99.0` %)
  - `--ndef-threshold` (기본 `95.0` %)
  - `--ndef-expected` (`1`/`0`, 기본 `1` — REQ-RC522-003 skip 조건)
  - `--healthcheck-expected` (`on`/`off`, 기본 `off` — REQ-RC522-004)
  - `--report <path>` (선택, JSON 출력 파일)
  - `--log-level` (`INFO` 기본)
- exit code: 0=pass, 1=regression, 2=operational error (예: port open 실패).
- DoD: `--help` 출력이 acceptance scenario 에서 설명한 모든 플래그를 보여준다.

### Task 2 (High) · 이벤트 파서 및 집계

- 같은 파일. 파서 대상 라인 (research.md §3.1, 펌웨어 L449-464, L350-363):
  - `{"event":"rfid_reader", ...}` — healthcheck 플래그 / version 추출 (REQ-RC522-004).
  - `{"event":"rfid_tag", "uid":..., "type":..., "text":...}` — UID / NDEF 집계.
  - `{"event":"rfid_clear", ...}` — 탭 경계 구분.
  - `BOOT:conveyor_v5_serial 1.5.X` — firmware_version 추출 및 **런타임 중 재발생 시 `firmware_crashed: true`** (REQ-RC522-002).
  - `RFID_UID:` / `RFID_TEXT:` — 폴백 검증용 (JSON 파싱 실패 시에만 참조).
- `RegressionReport` dataclass (MX:ANCHOR 후보) 필드: `total_taps, successful_uid_reads, ndef_parse_successes, ndef_decode_failures, missed_reads, healthcheck_state, firmware_version, firmware_crashed, run_duration_seconds, exit_code, failure_category (Optional)`.
- 집계 단위 = **"탭 1 회"**. 정의: `rfid_tag` 이벤트가 `lastUid != currentUid` 또는 직전 `rfid_clear` 이후 첫 수신일 때 +1.

### Task 3 (High) · Mac 브라운아웃 가드

- 구현 위치: Serial open 직전. `platform.system()` + port pattern 검사.
- Mac 이면:
  - 모터 커맨드 송신 메서드를 no-op stub 으로 교체.
  - `stderr` 에 붉은 경고 출력 (ANSI 없음 — stdlib only): `"[WARN] Mac host detected. Motor commands disabled (ref: feedback_motor_brownout_mac_usb). Read-only sniff mode."`.
- Jetson 이면: 가드 off, 모터 커맨드 허용.

### Task 4 (High) · healthcheck 재도입 감지

- REQ-RC522-004 의 두 가지 탐지 방법 구현:
  1. `rfid_reader` JSON 의 선택적 `healthcheck` 키 파싱 (펌웨어가 미래에 추가한다고 가정).
  2. CLI `--healthcheck-expected on` 이 주어졌는데 UID 성공률이 99 % 미만 → `failure_category = "healthcheck_regression"` 설정 + 리포트에 `dd4c4eb` 참조 문자열 삽입.
- DoD: 테스트 dry-run 시 `--healthcheck-expected on --uid-threshold 99` 와 인위적으로 만들어진 UID 90 % 스트림을 주입했을 때 exit 1 + 정확한 failure_category.

### Task 5 (Medium) · 오프라인/dry-run 모드

- 실기기 없이도 파서를 검증하도록 `--replay <logfile>` 옵션 추가. Serial 대신 파일에서 라인 읽음.
- 사유: Mac 에서도 파서 로직 단위 테스트 가능해야 Run phase 에서 DDD/TDD 사이클 돌릴 수 있다.
- `jetson_publisher/tests/test_esp_bridge.py` 의 FakeSerial 패턴을 참고하되 코드 복사는 지양 (경계 유지).

### Task 6 (Medium) · 수동 체크리스트 문서

- 파일: `docs/testing/rc522_regression_checklist.md` **[NEW]**
- 한국어. 10 분 이내 실행 가능한 선형 체크리스트.
- 섹션:
  1. 사전 조건 (ssh 접속, 브릿지 중지, 카드 준비)
  2. 배선 확인 (VSPI 핀 매핑 표 — research.md §1.1 재사용)
  3. 전원 체크 (Jetson 직결 or 외부 12 V; **Mac 연결 금지** HARD 표시)
  4. 하네스 실행 명령
  5. 탭 시퀀스 (100 회 표준 / 5 분 이내)
  6. 통과 조건 판정 (리포트 JSON 필드별 기대값)
  7. 실패 시 대응 (BOOT 재발행 시 배선 재확인, 로그 첨부해서 이슈 등록)
- 판정 부분은 acceptance.md 와 크로스 링크.

### Task 7 (Medium) · 독립 스케치 report mode (선택)

- 파일: `firmware/rc522_standalone_test/rc522_standalone_test.ino` **[MODIFY? — 조건부]**
- 현재 스케치는 카드당 `delay(3000)` cooldown 후 "NDEF 못 찾음" 외 집계 없음.
- 필요 시점: 자동 하네스가 통합 펌웨어에서 예측 불가 이슈가 발견되어 격리 재현이 필요할 때.
- 개정 안:
  - 전역 카운터 `totalTaps`, `ndefSuccess` 추가.
  - Serial 명령 `REPORT` 수신 시 현재까지 카운트를 한 줄 JSON 으로 출력.
  - 기존 로직 변경 없음 (스니펫 원형 유지).
- **Plan 단계 결정**: Task 7 은 *보류*. Run phase Phase 2.1 (ANALYZE) 에서 "자동 하네스만으로 충분한가?" 를 재검토하고, 불필요하면 삭제. 결정 기준은 "v1.5.1 통합 펌웨어 상 이슈 재현 능력이 자동 하네스만으로 보장되는가".

### Task 8 (Low) · Skill / MoAI 연동

- SPEC 의 MX Tag Plan (spec.md) 을 Run phase 에서 실제 주석으로 삽입.
- `.moai/specs/SPEC-RC522-001/progress.md` 자동 생성 — run phase 가 Re-planning Gate 조건 체크 시 사용.

### Task 9 (Low) · 문서 교차 참조 업데이트

- `SPEC-AMR-001/spec.md` acceptance L159 에 "(see SPEC-RC522-001)" 주석 스타일로 cross-reference 를 남기는 것이 바람직하지만 **Plan 단계에서는 제안만**. 기존 SPEC 파일 수정은 Run phase 에서 사용자 확인 후 실행.

---

## 2. File List

### New files

1. `scripts/test_rc522_regression.py` — 하네스 본체. stdlib + pyserial only.
2. `docs/testing/rc522_regression_checklist.md` — 수동 체크리스트 (한국어).
3. `docs/testing/` — 디렉토리 자체가 신규.
4. `.moai/specs/SPEC-RC522-001/progress.md` — Run phase 생성 (Plan phase 에서는 skeleton 만 상정).

### Modified files (조건부)

1. `firmware/rc522_standalone_test/rc522_standalone_test.ino` — Task 7 결정에 따라. 현재 계획: **건드리지 않음**.

### Read-only references (수정 금지)

1. `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` (v1.5.1) — 특히 L314-368 (`pollRfid`), L230-244 (`readNdefFromCard`), L192-224 (`parseNdefText`), L673 (BOOT), L324-326 (v1.5.1 주석).
2. `jetson_publisher/esp_bridge.py` — 이벤트 shape 합의는 이 파일과 동기. L162-210 (`_handle_line`) 이 소비 라인 권위.
3. `jetson_publisher/tests/test_esp_bridge.py` L19-40 — FakeSerial 패턴 참고 (복사 아님).

---

## 3. Technical Approach

### 3.1 Serial 수신 루프 모델

- `serial.Serial(port, baud, timeout=0.5)` non-blocking 읽기.
- 라인 분리: `b"\n"` 기준 `bytearray` partition (esp_bridge.py L150-160 패턴과 동일 전략).
- 각 라인에 대해 다음 순서로 판정:
  1. `BOOT:` 접두사 → firmware_version 기록 / 2 회차부터 `firmware_crashed=True`.
  2. 첫 글자가 `{` 이면 `json.loads` 시도. 실패 시 `malformed_json_lines` 카운터 +1 하고 raw 저장 (debug log).
  3. JSON 의 `event` 필드로 분기 (`rfid_reader`, `rfid_tag`, `rfid_clear`, 기타).
  4. 그 외 ASCII 토큰 (`RFID_UID:` 등) 은 보조 채널 — UID 를 JSON 이벤트로부터 얻지 못했을 때만 사용.

### 3.2 100-탭 롤링 윈도우

- 가장 단순한 구현: `collections.deque(maxlen=100)` 에 탭별 `TapResult(uid_ok: bool, ndef_ok: Optional[bool])` 을 저장.
- `total_taps` 가 100 회를 돌파하는 순간부터 윈도우 평가가 활성화된다. 100 회 미만은 `failure_category: "insufficient_taps"` 로 실패 처리 (REQ-RC522-002 가 최소 100 을 요구).

### 3.3 종료 조건

- (a) `--taps` 카운트 달성, (b) `--timeout` 초과, (c) SIGINT 중 가장 먼저 발생하는 조건.
- SIGINT 시에도 지금까지 수집한 데이터로 리포트를 출력 (exit 2 — operational).

### 3.4 리포트 JSON 예시 (권위 없음, 초안)

```json
{
  "firmware_version": "conveyor_v5_serial 1.5.1",
  "total_taps": 100,
  "successful_uid_reads": 100,
  "ndef_parse_successes": 98,
  "ndef_decode_failures": 1,
  "missed_reads": 0,
  "healthcheck_state": "off",
  "firmware_crashed": false,
  "run_duration_seconds": 238.4,
  "exit_code": 0,
  "failure_category": null,
  "host": "jetson-conveyor",
  "python": "3.10.12",
  "pyserial": "3.5",
  "run_started_at": "2026-04-18T12:34:00Z"
}
```

### 3.5 테스트 시나리오 대칭

- acceptance.md 의 3 개 주요 시나리오 + edge case 들이 **하네스 단위 테스트**로도 존재해야 한다 (Run phase TDD 사이클). 오프라인 `--replay` 로 fixture 입력을 주입해 파서 로직만 검증 가능.

---

## 4. Risks

### 4.1 Mac USB 브라운아웃 (HARD)

- 메모리 `feedback_motor_brownout_mac_usb`.
- 완화: REQ-RC522-005 가 런타임 refuse. 체크리스트에서도 명시. `@MX:WARN` 으로 코드 주석 박제.
- 잔여 위험: 운영자가 Jetson 이라고 주장하는 Mac VM/도커 환경. → 체크리스트에서 `uname -a` 출력 확인 단계 추가로 완화.

### 4.2 SPI 버스 ↔ TOF UART 간 cross-talk / EMI

- 핀 겹침은 없음 (research.md §8 확인). 하지만 PCB 공통 GND 노이즈로 RC522 RF 가 악영향을 받을 가능성 이론적으로 존재.
- 완화: 하네스가 TOF 이벤트(진입/퇴장 JSON) 도 함께 수신하므로, RFID 감지가 특정 TOF 이벤트와 시간적으로 겹쳐 실패하면 리포트에 `correlated_with_tof: true` 플래그 추가 (Run phase option).
- Plan 결정: 1차 MVP 는 correlation 분석 생략. edge case (acceptance) 에만 언급.

### 4.3 TOF IR emitter RF 간섭

- TOF250 은 1 kHz 변조 IR 이며 13.56 MHz RC522 에 직접적 스펙트럼 겹침은 없다. 다만 펄스 전류가 전원 레일을 흔들 수 있음.
- 완화: 전원 독립 (외부 12 V motor supply vs 5 V logic) 을 체크리스트 배선 섹션에 명시.

### 4.4 포트 점유 충돌

- `jetson-publisher` 서비스가 돌아가는 상태면 `/dev/ttyUSB0` 이 이미 열려 있어 하네스가 open 실패 → `OSError`.
- 완화: 체크리스트 사전 조건에 `sudo systemctl stop jetson-publisher` (실제 서비스 이름은 운영자 확인) 혹은 `pkill -f publisher.py` 명시. 하네스는 open 실패 시 exit 2 + 명확한 에러 메시지.

### 4.5 카드 불량 / 카드 1종에 과의존

- 테스트 카드가 악화되면 NDEF 95 % 가 무너질 수 있다.
- 완화: 체크리스트에 "독립 스케치로 baseline 확인" 단계 포함 → healthy baseline 에서도 낮으면 카드 교체. 하네스는 baseline 실행을 강제하지 않음 (운영자 재량).

### 4.6 Jetson 시계 드리프트

- `timeout` 판정 및 `run_started_at` 기록에 영향. 일반 운영 NTP 동기 가정.
- 완화: `time.monotonic()` 을 duration 측정에 사용 (월타임에 의존하지 않음).

### 4.7 펌웨어 버전 혼동

- `BOOT:conveyor_v5_serial 1.5.1` 문자열이 미래에 포맷이 바뀌면 파서가 깨짐.
- 완화: regex `^BOOT:conveyor_v5_serial\s+(\S+)$` 로 느슨하게 매치. 매치 실패 시 `firmware_version = "unknown"` 이지만 테스트는 계속 (경고만).

---

## 5. Verification Gate (Plan → Run)

Run phase 진입 전 이 계약들이 모두 문서로 박제되었는지 재확인.

- [ ] spec.md EARS 5 개가 모두 측정 가능한 출력 기반(리포트 JSON 필드) 으로 쓰여 있다.
- [ ] acceptance.md 3 주요 + edge case 시나리오가 Given/When/Then 으로 있다.
- [ ] research.md 에 파일·라인 레퍼런스가 모두 실재 함 (위 Read-only references 와 일치).
- [ ] 메모리 2 건 (`feedback_rc522_healthcheck_bug`, `feedback_motor_brownout_mac_usb`) 이 명시적으로 REQ 에 매핑됨.
- [ ] Exclusions 에 "펌웨어 수정 금지" 가 들어가 있다 (Run phase scope 보호).

---

## 5.5. Plan-Phase 결정사항 (2026-04-18 승인)

Plan phase 종료 시점 orchestrator ↔ 사용자(kisoo) 간 확정된 기본값. Run phase 는 이 기본값을 전제로 시작하되, 실기기 조사 결과에 따라 조정할 수 있다.

| 항목 | 기본값 | 근거 / Run phase 확인 사항 |
|------|--------|---------------------------|
| Jetson `jetson_publisher` / `esp_bridge` 실행 방식 | **수동 런칭 가정** (systemd 유닛 없음) | Run Task 6 체크리스트에 "작업 시작 전 Jetson 에 SSH 접속해 `pgrep -af jetson_publisher` 로 PID 확인 후 수동 kill" 절차를 기본 기재. Run 단계에서 `ssh jetson-conveyor systemctl list-units 'jetson*'` 로 재확인하고, systemd 유닛이 존재하면 체크리스트에 `systemctl stop` 명령을 추가한다. |
| `firmware/rc522_standalone_test/rc522_standalone_test.ino` 수정 | **Deferred** (Task 7 유지) | 스탠드얼론 스케치는 healthy baseline 기록 목적이므로 이번 SPEC 에서는 수정하지 않는다. 통합 펌웨어(`conveyor_v5_serial.ino` v1.5.1) 만 회귀 검증 대상. 후속 SPEC 에서 필요 시 report mode 추가. |
| NDEF 테스트 카드 재고 | **메인 NDEF 카드 1종만 보유** (`order_1_item_20260417_2` 유형) | AC-E2 (no-NDEF) / AC-E3 (UTF-8 깨짐) 는 **Run phase 에서 deferred 로 표시**. 카드 확보 후 별도 회귀 SPEC 또는 이 SPEC 의 v0.2 에서 커버. 메인 시나리오 AC-1 ~ AC-3 은 현재 카드로 실행 가능. |

## 6. References

- `.moai/specs/SPEC-RC522-001/spec.md`
- `.moai/specs/SPEC-RC522-001/research.md`
- `.moai/specs/SPEC-RC522-001/acceptance.md`
- `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` L59-65, L85-86, L177-224, L230-244, L314-368, L449-467, L673
- `firmware/rc522_standalone_test/rc522_standalone_test.ino` (전체)
- `jetson_publisher/esp_bridge.py` L93-104, L150-210
- `jetson_publisher/tests/test_esp_bridge.py` L19-40
- Git 커밋 `dd4c4eb` (v1.5.1), `5a84fc8` (v1.5.0)
- 메모리 `feedback_rc522_healthcheck_bug`, `feedback_motor_brownout_mac_usb`, `reference_jetson_ssh`, `project_jetson_pipeline`

---

*이 plan.md 는 SPEC-RC522-001 의 Run phase 가 참조하는 단일 작업 분해 출처다. 구현 세부는 Run phase 에서 결정되며 이 파일은 비침습적으로 업데이트된다.*
