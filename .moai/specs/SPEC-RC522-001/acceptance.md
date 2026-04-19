# SPEC-RC522-001 · Acceptance Criteria

**대상 SPEC**: `spec.md` v0.1.0
**형식**: Given / When / Then
**판정 권위**: 아래 시나리오 결과가 Run phase 의 통과 기준이며, main 병합 전 필수 검증.

---

## 1. 주요 시나리오 (3 건 — spec.md acceptance summary 와 1:1 대응)

### AC-1 · Happy Path — v1.5.1 펌웨어 100 탭 성공

- **Given**
  - `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` v1.5.1 이 ESP32 에 플래시되어 있고,
  - ESP32 가 Jetson (`jetson-conveyor`, Tailscale `100.77.62.67`) 의 `/dev/ttyUSB0` 에 연결,
  - Jetson 호스트에서 `jetson_publisher` / `esp_bridge` 프로세스가 **중지 상태**,
  - 알려진 MIFARE Ultralight 테스트 카드 1 장 (NDEF Text 레코드 포함, 예: `order_1_item_20260417_2`) 이 준비됨.
- **When**
  - 운영자가 Jetson 에서 `python3 scripts/test_rc522_regression.py --taps 100 --timeout 300 --report /tmp/rc522.json` 실행,
  - 5 분 이내에 동일 카드로 100 회 탭 수행.
- **Then**
  - 프로세스 exit code = 0,
  - `/tmp/rc522.json` 의 `total_taps` == 100,
  - `successful_uid_reads` ≥ 99 (REQ-RC522-002 의 99 % 임계),
  - `ndef_parse_successes` ≥ 95 (REQ-RC522-003 의 95 % 임계),
  - `firmware_crashed` == `false`,
  - `failure_category` == `null`,
  - `healthcheck_state` == `"off"` (v1.5.1 기본),
  - stdout 에 동일 JSON 한 줄이 출력됨.

### AC-2 · Healthcheck Regression Block

- **Given**
  - 누군가 (또는 Run phase 자체) 가 **시험적으로** `pollRfid()` 에 `PCD_ReadRegister(VersionReg)` healthcheck 를 재도입한 실험 빌드(`1.5.2-experimental` 라고 가정) 를 ESP32 에 플래시,
  - 그 외 조건은 AC-1 과 동일,
  - 하네스를 `--healthcheck-expected on --uid-threshold 99` 옵션으로 실행.
- **When**
  - 운영자가 동일 카드 100 회 탭 수행,
  - 실측 UID 감지율이 99 % 미만 (예: 85 회 성공 / 15 회 miss) 로 떨어짐.
- **Then**
  - 프로세스 exit code = 1,
  - 리포트 JSON 의 `failure_category` == `"healthcheck_regression"`,
  - 리포트 JSON 어딘가 (예: `notes` 또는 `failure_detail` 필드) 에 문자열 `"regression reference: dd4c4eb"` 가 포함,
  - `healthcheck_state` == `"on"` 로 기록,
  - stderr 에 `"v1.5.1 fix may have been reverted"` 류의 경고가 출력됨.

### AC-3 · Mac 호스트 Read-Only Sniff

- **Given**
  - 개발자가 Mac (Darwin) 노트북에 ESP32 를 USB-serial 어댑터로 연결하려 시도,
  - 포트 경로가 macOS 패턴 (예: `/dev/cu.usbserial-0001`).
- **When**
  - 개발자가 `python3 scripts/test_rc522_regression.py --port /dev/cu.usbserial-0001 --taps 50` 실행.
- **Then**
  - 하네스가 Serial port 는 정상 open 하되,
  - stderr 에 정확히 한 줄 경고: `"[WARN] Mac host detected. Motor commands disabled (ref: feedback_motor_brownout_mac_usb). Read-only sniff mode."`,
  - 모터 관련 커맨드 (`RUN`, `STOP`, `start`, `reset`, `sim_entry`, `sim_exit`) **어느 것도 serial 에 write 되지 않음** (하네스 내부 송신 버퍼 기록으로 검증 가능),
  - 운영자가 수동으로 카드를 탭하면 하네스는 RFID 이벤트를 정상 집계하고 리포트를 발행,
  - L298N 이 기동되지 않으므로 ESP32 가 리셋되지 않음 (BOOT 라인 1회만 관측).

---

## 2. Edge Cases — 자동 하네스가 명시적으로 처리

다음 edge case 들은 AC-1~3 외에 리포트 필드로 식별 가능해야 한다. 각 항목은 자동 exit code 결정에 영향을 준다 (별도 명시 없으면 pass 가능).

### AC-E1 · 카드 장시간 보유 (hold-over)

- **Given**: AC-1 의 환경.
- **When**: 운영자가 카드를 3 초 이상 리더 위에 계속 올려둠 (제거 없이).
- **Then**:
  - 하네스는 그 시점에 `rfid_tag` 이벤트 1 회만 집계 (`RFID_TAG_HOLD_MS = 700 ms` 보유 로직, 펌웨어 L339-345).
  - `total_taps` 증가는 다음에 카드를 뗐다가 다시 올렸을 때 발생.
  - 리포트의 `hold_over_events` 카운터 (있다면) 는 증가해도 된다. pass/fail 판정에는 영향 없음.

### AC-E2 · NDEF 없는 카드

- **Given**: NDEF Text 레코드가 **없는** MIFARE Ultralight 카드 (공카드 또는 다른 포맷).
- **When**: 하네스를 `--ndef-expected 0` 로 실행.
- **Then**:
  - REQ-RC522-003 (NDEF 95 %) 은 자동 skip.
  - 리포트에 `ndef_requirement_skipped: true` 명시.
  - UID 임계(99 %) 만 판정하여 pass/fail 결정.

### AC-E3 · NDEF 페이로드 UTF-8 손상

- **Given**: NDEF Text 에 UTF-8 아닌 바이트가 섞인 실험 카드.
- **When**: AC-1 과 동일 조건으로 실행.
- **Then**:
  - 해당 탭은 `successful_uid_reads` 에는 가산되지만,
  - `ndef_parse_successes` 에도 `ndef_parse_failures` 에도 가산되지 **않는다**. 대신 `ndef_decode_failures` 카운터에 +1.
  - `ndef_decode_failures` 가 전체 탭의 5 % 를 넘으면 warning 레벨 로그 (pass 는 유지, edge case 는 failure 로 자동 승격하지 않음).

### AC-E4 · SPI 버스 노이즈로 인한 간헐적 miss

- **Given**: AC-1 환경. 단, 실기기에서 간헐적으로 `PICC_IsNewCardPresent` 가 false 를 반환하여 `rfid_tag` 이벤트가 누락되는 상황을 가정 (운영자가 확인한 카드 탭인데 이벤트 미발행).
- **When**: 100 회 탭 중 예를 들어 2 회 누락 (`missed_reads` 기록).
- **Then**:
  - `successful_uid_reads` == 98, `missed_reads` == 2.
  - UID 성공률 98 / 100 = 98 % → **REQ-RC522-002 임계 99 % 미달 → exit 1**.
  - `failure_category` == `"uid_below_threshold"` (healthcheck_regression 과 구분).
  - 이 시나리오는 "임계값이 엄격함을 확인" 하는 테스트이기도 하다. 실제 운영에서는 operator 가 탭 누락 사유(카드 흔들림, 리더 각도) 를 점검해야 한다는 체크리스트 지시와 연결.

### AC-E5 · ESP32 런타임 리셋

- **Given**: 테스트 도중 (예: 50 회 시점) ESP32 가 전원 저하나 소프트웨어 크래시로 리셋되어 `BOOT:conveyor_v5_serial 1.5.1` 라인이 다시 출력됨.
- **When**: 하네스가 두 번째 BOOT 라인을 수신.
- **Then**:
  - `firmware_crashed` == `true` 로 플래그.
  - exit code = 1, `failure_category` == `"firmware_crash"`.
  - 리포트에 `first_crash_at_tap` 필드로 발생 시점 기록.
  - 연속 테스트가 불가능하므로 100 탭 미달이어도 즉시 종료 허용.

### AC-E6 · 펌웨어 버전 미스매치 (예: v1.5.0)

- **Given**: ESP32 에 **v1.5.0** (healthcheck 버그 있음) 이 플래시된 상태.
- **When**: 하네스를 `--healthcheck-expected off` 기본값으로 실행.
- **Then**:
  - 리포트 `firmware_version` 에 `conveyor_v5_serial 1.5.0` 기록.
  - UID 성공률이 ~0 % 에 가까움 → exit 1, `failure_category` == `"uid_below_threshold"`.
  - 리포트에 warning 필드: `firmware_version_below_1_5_1` == `true` (hint).
  - Run phase 에서 이 warning 을 주석/문서 수준에서 "v1.5.1 로 업그레이드 후 재시험 권고" 로 안내.

### AC-E7 · Serial port 점유 충돌

- **Given**: `jetson_publisher` 가 구동 중이어서 `/dev/ttyUSB0` 이 이미 열려 있음.
- **When**: 하네스 실행.
- **Then**:
  - port open 실패 → exit code = **2** (operational error, regression 과 구분),
  - stderr 에 `"Port already in use. Stop jetson_publisher / esp_bridge before running this suite."` 출력,
  - 리포트 JSON 은 `exit_code: 2`, 나머지 카운터는 `null`.

### AC-E8 · 탭 횟수 부족 / 타임아웃

- **Given**: AC-1 환경. 운영자가 실수로 20 회만 탭하고 5 분 타임아웃 도달.
- **When**: 하네스가 timeout 으로 종료.
- **Then**:
  - exit code = 1, `failure_category` == `"insufficient_taps"`,
  - `total_taps < 100` 이므로 REQ-RC522-002 충족 불가 → UID/NDEF 임계 판정 생략,
  - 리포트에 `timed_out: true`.

---

## 3. Definition of Done (Plan Phase 종료 기준)

Run phase 로 넘어가기 전 아래 모두 true.

- [x] spec.md 에 EARS 5 개 REQ 가 정의되어 있음.
- [x] 각 REQ 가 위 AC-1~3 및 edge case 중 하나 이상에 매핑됨.
- [x] 모든 주요/edge 시나리오가 **측정 가능한 리포트 필드**로 판정 가능 (주관 판단 없음).
- [x] Exclusions (spec.md) 와 본 acceptance 가 상호 충돌하지 않음. 특히 "펌웨어 수정 금지" 와 AC-E6 이 양립 — v1.5.0 을 플래시하는 것은 테스트 시나리오로만 허용, 펌웨어 코드 수정은 Run phase 에서도 scope 밖.
- [x] Mac 브라운아웃 가드 (REQ-RC522-005) 가 AC-3 로 명시적 테스트됨.
- [x] healthcheck 재도입 계약 (REQ-RC522-004) 가 AC-2 로 명시적 테스트됨.

## 4. Definition of Done (Run Phase 종료 기준 — 향후 참조)

Run phase 가 끝났을 때 판정될 항목 (미리 선언):

- [ ] `scripts/test_rc522_regression.py` 생성, stdlib + pyserial only, `--help` 정상 출력.
- [ ] `docs/testing/rc522_regression_checklist.md` 생성, 10 분 체크리스트 포함.
- [ ] Jetson 실기기에서 AC-1 1 회 통과 (evidence: 리포트 JSON 커밋 or SPEC 서브디렉토리에 첨부).
- [ ] 하네스 단위 테스트 (오프라인 `--replay` 기반) 가 AC-1/AC-2/AC-3/AC-E1~E8 을 커버 (TDD 또는 DDD 사이클 산출물).
- [ ] MX 태그 3종 (ANCHOR / WARN / NOTE) 이 spec.md MX Tag Plan 대로 주석에 존재.
- [ ] `progress.md` 가 Run phase 생성한 이력을 담고 있음.

---

*본 acceptance.md 는 SPEC-RC522-001 v0.1.0 의 계약 출처다. 시나리오 추가/수정 시 spec.md HISTORY 와 version 필드를 동시 갱신할 것.*
