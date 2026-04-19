# SPEC-RC522-001 · Deep Research (Phase 0.5)

**작성**: 2026-04-18 · kisoo
**목적**: RC522 안정성 회귀 테스트 스위트 설계 전에 현재 펌웨어·브릿지·기존 SPEC 을 읽어 팩트 축적. 구현 없음, 읽기 전용.

---

## 1. v1.5.1 통합 펌웨어 — RFID 루프 상세

**파일**: `firmware/conveyor_v5_serial/conveyor_v5_serial.ino`
**버전**: 1.5.1 (BOOT 문자열 L673 `BOOT:conveyor_v5_serial 1.5.1`)
**빌드 산출물**: `firmware/conveyor_v5_serial/build/` (gitignored)

### 1.1 VSPI 고정 배선 (L59-65)

```
SCK  = GPIO 18    MISO = GPIO 19
MOSI = GPIO 23    SS   = GPIO 5
RST  = GPIO 22
```

`RFID_SPI_NAME = "VSPI"` 상수(L60) 는 이벤트/로그에만 사용. SPI 버스 자체는 ESP32 기본 VSPI.

### 1.2 v1.5.1 fix 핵심 — healthcheck 제거 (L314-333 `pollRfid()`)

v1.5.0 에서 2 초 주기로 `rfid.PCD_ReadRegister(MFRC522::VersionReg)` 를 호출해 리더 생존 확인을 했는데, 이 레지스터 접근이 바로 다음 루프의 `PICC_IsNewCardPresent()` 를 방해해 카드 감지율이 0 에 가까웠다.

현재 코드(L324-326)에 주석으로 박제:

```cpp
// v1.5.1: 주기 VersionReg healthcheck 제거 (카드 감지 간섭 의심).
// RC522 가 PICC_IsNewCardPresent 자체로 상태 확인되므로 별도 헬스체크 불필요.
// 필요 시 에러 누적 후 재초기화 로직 추후 추가.
```

관련 상수 `RFID_HEALTHCHECK_MS = 2000` (L85) 는 아직 파일에 남아 있으나 **어느 코드 경로에서도 사용되지 않는다** (사문화 상수). 이 SPEC 은 해당 상수 삭제를 **out-of-scope** 로 둔다 (SPEC 범위 보호용 근거).

### 1.3 RFID 루프 전체 흐름 (L314-368)

1. `rfidReaderReady` false → `RFID_REINIT_MS (3000 ms)` 지나면 `initRfid()` 재시도. 성공 시 VersionReg 1회만 읽어 버전 확인 후 `rfid_reader ready` 이벤트 발행.
2. `PICC_IsNewCardPresent() && PICC_ReadCardSerial()` 성공 시:
   - UID 문자열화 (`uidToString`, L177-186).
   - `readNdefFromCard()` 로 페이지 4~15 (48 바이트) 까지 4 페이지씩 3회 `MIFARE_Read()`.
   - `parseNdefText()` (L192-224) — NDEF TLV `0x03 [len] 0xD1 ...` 시그니처 탐색 → Text 레코드 (`type == 'T'`) 페이로드 추출.
3. **UID 이벤트는 NDEF 파싱 성공/실패와 무관하게 항상 발행** (L350-356). NDEF 파싱은 best-effort.
4. 동일 카드 연속 재인식 방지: `lastRfidUid` 비교. 카드 제거 감지(`RFID_TAG_HOLD_MS = 700 ms`) 시 `rfid_clear` 이벤트(L266-274).

### 1.4 Serial JSON 이벤트 shape (브릿지가 소비)

```jsonc
// 리더 준비 완료
{"event":"rfid_reader","status":"ready","spi":"VSPI","ss":5,"rst":22,"version":"0x92"}

// 카드 태깅
{"event":"rfid_tag","uid":"04:2D:EE:4A:B6:21:91","type":"MIFARE Ultralight or Ultralight C","text":"order_1_item_20260417_2"}

// 카드 제거
{"event":"rfid_clear","uid":"04:2D:EE:4A:B6:21:91"}

// 간단 토큰 (디버깅/브릿지용)
RFID_UID:04:2D:EE:4A:B6:21:91
RFID_TEXT:order_1_item_20260417_2
```

JSON escape (L249-264) 는 따옴표/백슬래시/제어문자 안전 처리. NDEF Text 가 UTF-8 이 아니면 제어문자(< 0x20) 는 **드롭**되고 이벤트는 여전히 발행됨 (파싱은 byte 단위, 깨진 UTF-8 멀티바이트는 그대로 통과할 수 있음 → 하네스가 감안해야 함).

### 1.5 baudrate

- USB Serial = **115200** (Arduino Serial + Jetson `/dev/ttyUSB0`). L653 `Serial.begin(115200)`.
- TOF1/TOF2 = 9600 ASCII (독립).

---

## 2. 독립 테스트 스케치 — healthy case baseline

**파일**: `firmware/rc522_standalone_test/rc522_standalone_test.ino` (95 줄)
**커밋**: `dd4c4eb` (v1.5.1) 에서 추가 — "사용자 제공 원본 스니펫"

### 2.1 유효성

- VSPI 기본 배선 (SS=5, RST=22) 그대로 사용.
- `SPI.begin() / mfrc522.PCD_Init()` 무인자 호출 → v1.5.1 통합 펌웨어와 동일 초기화 절차.
- NDEF 파서는 **사실상 동일 로직** (L13-50). 단, 통합 쪽은 `parseNdefText` 가 버퍼 범위 검사를 더 엄격히(`maxLen`, `textLen <= 0` 등) 한다.
- 카드 한번 감지 후 `delay(3000)` 로 명시적 cooldown — 실기기에서 "카드를 제거하세요" 루프를 시각적으로 확인하기 쉽다.

### 2.2 v1.5.1 검증 시 측정치 (커밋 `dd4c4eb` 본문)

- 독립 스니펫: 8회 감지, NDEF Text `order_1_item_20260417_2` 파싱 성공.
- v1.5.0 통합 펌웨어: 0회 감지 (healthcheck 간섭).
- v1.5.1 수정 후 통합 펌웨어: **30 초간 6회 감지** (원격 Jetson `100.77.62.67` `/dev/ttyUSB0` 경유).

### 2.3 SPEC 내 역할

독립 스케치는 여전히 **healthy baseline** 으로 유효. 이 SPEC 은 독립 스케치를 **선택적 수정 후보**로 둔다 — "report mode (횟수 카운터 + 최종 집계 Serial print)" 추가가 하네스를 단순화하면 고려. 불필요하면 건드리지 않는다.

---

## 3. Jetson Serial 브릿지

**파일**: `jetson_publisher/esp_bridge.py` (292 줄)
**테스트**: `jetson_publisher/tests/test_esp_bridge.py` (97 줄) — mock serial 단위 테스트

### 3.1 브릿지가 **소비**하는 라인 (L162-210 `_handle_line`)

| 라인 | 동작 |
|------|------|
| `STOPPED` | `INSPECTION_DELAY_MS` 지연 후 `RUN\n` TX (auto_run on) |
| `STARTED` | INFO 로그 |
| `DONE` | INFO 로그 |
| `BOOT:…` | INFO 로그 |
| `STATE:…` | DEBUG 로그 |
| `PONG` | DEBUG 로그 |
| `ERR:…` | WARN 로그 |
| `HANDOFF_ACK` | gRPC `ReportHandoffAck` 전송 (SPEC-AMR-001) |

**주의 (하네스 설계에 직결)**:

- 브릿지는 `rfid_tag` / `rfid_reader` / `rfid_clear` **JSON 이벤트를 파싱하지 않는다** (`else: log.debug("ESP line: %s", line)`, L210).
- `RFID_UID:` / `RFID_TEXT:` 토큰 라인도 브릿지가 파싱하지 않는다 (현재까지 소비자 없음).
- 즉, **RFID 는 Serial stream 에 실리지만 gRPC/DB 까지 전파되는 경로는 아직 없다**. 이 SPEC 의 하네스는 **동일 `/dev/ttyUSB0` 스트림을 브릿지와 공유하지 않는 별도 프로세스**여야 하거나, HW-in-loop 테스트 전용으로 브릿지 **중지 상태**에서 수행해야 한다.
- 결정: 하네스는 **pyserial 로 `/dev/ttyUSB0` 을 직접 open** 한다 (publisher/esp_bridge 가 동시에 열면 충돌). 테스트 실행 전 `systemctl stop jetson-publisher` 혹은 수동 프로세스 종료를 operator checklist 에 명시할 것.

### 3.2 baudrate 확정

`ESP_BRIDGE_BAUD=115200` 기본, `ESP_BRIDGE_PORT=/dev/ttyUSB0` (L97-98). 하네스도 이 값 그대로.

### 3.3 기존 테스트 — mock FakeSerial 패턴

`tests/test_esp_bridge.py` 는 `FakeSerial` 클래스를 사용해 실기기 없이 `_handle_line` 을 단위 검증한다. 하네스 설계 시 **오프라인 / dry-run 모드**를 이 패턴으로 구현하면 Mac 에서도 logic test 는 돌릴 수 있다 (FR 에서 요구한 Mac USB 브라운아웃 가드와 연결).

---

## 4. SPEC-AMR-001 교차 참조

**파일**: `.moai/specs/SPEC-AMR-001/spec.md`

### 4.1 RFID 는 SPEC-AMR-001 out-of-scope (L191)

> "RC522 태그 기반 AMR-주문 자동 매칭 (별도 SPEC으로 분리)"

→ SPEC-RC522-001 이 그 "별도 SPEC" 과 혼동되면 안 된다. **이 SPEC 은 회귀 테스트 한정**, AMR-주문 자동 매칭은 또 다른 SPEC 으로 분리.

### 4.2 Wave 3 에서 ESP32 펌웨어 커밋이 RFID 와 섞여 있음

- Wave 3 `05f980f` 가 ESP32 GP33 버튼 추가 — RFID 는 이때 `v1.4.0`. NDEF 는 그 다음 `v1.5.0` `5a84fc8` 에서 추가, v1.5.1 `dd4c4eb` 은 healthcheck 제거 핫픽스.
- **회귀 테스트 단위 = v1.5.1 통합 펌웨어 전체** (RFID + TOF + 모터 + 버튼 공존). RFID 만 격리해서는 의미가 없다 (crosstalk / 전력 공유가 실제 이슈이기 때문).

### 4.3 Acceptance 가 언급하는 회귀 명시 (SPEC-AMR-001 L159)

> "ESP32 독립성: 버튼 누름이 컨베이어 TOF250 판독/모터 PWM 제어에 영향 주지 않음 (기존 conveyor_v5_serial 동작 회귀 테스트 통과)"

→ SPEC-RC522-001 이 **이 회귀 테스트의 RFID 부분을 구체화** 하는 역할로 자연 정착된다. 충돌 없음.

---

## 5. Confluence 및 기타 문서 크로스체크

- `docs/CONFLUENCE_FACTS.md` 전량 스캔 (Grep `RFID|RC522`) — RFID 관련 hit 는 L1958 "Scan Lane" 용어 정의 1건뿐. RC522 프로토콜이나 안정성에 대한 Confluence 팩트는 **현재 없음**. 따라서 이 SPEC 이 원천 문서가 된다 (Confluence 쓰기는 사용자 허락 필수 — 이번 SPEC 에서는 생성하지 않음).
- `docs/testing/` 디렉토리 **아직 없음** → 이 SPEC 이 최초 생성자.
- `scripts/` 는 이미 존재 (`sync_confluence_facts.py`), 새 스크립트 추가에 구조적 장애 없음.

---

## 6. 메모리에서 확인된 HARD 제약 (재인용)

이 SPEC 의 요구사항에 **반드시** 반영.

### 6.1 RC522 healthcheck 버그 (`feedback_rc522_healthcheck_bug`)

- 주기 `PCD_ReadRegister(VersionReg)` 읽기가 `PICC_IsNewCardPresent` 를 간섭.
- v1.5.1 에서 제거 확인.
- 재도입 시도는 이 회귀 스위트가 **반드시** 블록해야 한다 (REQ-RC522-004).

### 6.2 Motor brownout (Mac USB) (`feedback_motor_brownout_mac_usb`)

- L298N 기동 inrush 가 Mac USB 5 V 공급을 끌어내려 ESP32 가 리셋.
- **모터/풀펌웨어 테스트는 반드시 Jetson 또는 외부 12 V 서플라이**에서 수행.
- 하네스는 Mac 에서 실행될 때 모터를 구동하지 않도록 refuse 해야 함 (REQ-RC522-005).
- Mac 에서 **RFID 단독 테스트**는 이론상 가능(모터 구동 없이 `rc522_standalone_test` 만 플래시) 하지만 이 SPEC 은 단순화를 위해 "motor 가 포함된 v1.5.1 통합 펌웨어만 허용 환경 = Jetson" 원칙을 채택.

### 6.3 Jetson 원격 접속 (`reference_jetson_ssh`)

- `ssh jetson-conveyor` alias (Tailscale `100.77.62.67`), `/dev/ttyUSB0` 에 ESP32 연결.
- 하네스는 Jetson 호스트에서 직접 실행 가정. Mac 에서는 `ssh jetson-conveyor -- python3 scripts/test_rc522_regression.py …` 같은 원격 호출만 허용.

### 6.4 items seed mfg_at 규칙 (`feedback_seed_mfg_at`)

- 본 SPEC 과 직접 관련 없지만 테스트 수행 중 DB seed 를 건드릴 일이 있으면 `now() ±30 s` 제약을 기억할 것. → **이 SPEC 은 DB 미접근**. 언급만 하고 scope out.

---

## 7. 기술 결정 요약

| 주제 | 결정 | 근거 |
|------|------|------|
| 하네스 호스트 | **Jetson (`jetson-conveyor`)** 전용. Mac 은 dry-run 만 | 브라운아웃 제약 + `/dev/ttyUSB0` 가 Jetson 에만 존재 |
| Serial 포트 | `/dev/ttyUSB0 @ 115200` | 펌웨어/브릿지와 동일 |
| 포트 공유 | 브릿지와 동시 open 불가 → **테스트 전 브릿지 중지** 를 체크리스트에 명시 | `esp_bridge.py` L128-134 `serial.Serial(port, baud)` 단독 open 전제 |
| 이벤트 소스 | **JSON `rfid_tag` / `rfid_clear` / `rfid_reader`** (ground truth) | 통합 펌웨어가 UID + NDEF 를 함께 싣는 유일한 라인 |
| 보조 이벤트 | `RFID_UID:` / `RFID_TEXT:` 토큰 라인 (검증용 cross-check) | 하네스가 JSON 파싱 실패 시 폴백 가능 |
| 측정 단위 | **100 탭 윈도우 기준 UID 성공률 %** | 커밋 `dd4c4eb` 가 "30초 6회" 로 환산 약 100 % 를 스모크로 사용 → 공식 기준은 99 % |
| NDEF 임계값 | **95 %** (best-effort 반영) | 펌웨어가 UID 이벤트는 항상 발행하고 NDEF 실패를 감수하는 설계 (L344-363) |
| 탭 감지 방식 | JSON `rfid_tag` UID 의 **hold window (≥ `RFID_TAG_HOLD_MS=700ms` 지속)** 를 1회 탭으로 계산. 같은 UID 를 700 ms 이내 재감지하면 카운트 증가 없음 | 펌웨어 L339-345 lastRfidUid 비교 로직 |
| 의존성 | 파이썬 표준 라이브러리 + **pyserial only** | `jetson_publisher/` 가 이미 pyserial 사용, 추가 의존 없음 |

---

## 8. 열린 질문 (이 SPEC 에서 해결 안 함)

- 카드 1장으로 100 회 탭할지, 여러 장을 섞을지 → **acceptance 에서는 "동일 카드 1장 100 회" 를 표준으로 채택**. 멀티카드 시나리오는 edge case 로만 언급.
- TOF IR 광이 RC522 RF 에 미치는 노이즈 영향 → 측정 대상(plan.md Risks 에 기록), 실측 전 정량 데이터 없음.
- SPI 버스가 TOF UART 와 완전 분리인지(핀 겹침 없음) 확인: L59-65 (SPI 18/19/23/5/22) vs L56-57 (TOF1 16, TOF2 17) — **핀 충돌 없음**. 노이즈는 PCB 수준 결합 문제.

---

## 9. 참고 파일 · 라인 인덱스

| 목적 | 파일 | 라인 |
|------|------|------|
| 통합 펌웨어 BOOT | `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` | 673 |
| VSPI 배선 상수 | 위 파일 | 59-65 |
| RFID 핸들러 설명 주석 (v1.5.1 제거 기록) | 위 파일 | 324-326 |
| `pollRfid()` 본체 | 위 파일 | 314-368 |
| `readNdefFromCard` | 위 파일 | 230-244 |
| `parseNdefText` | 위 파일 | 192-224 |
| `uidToString` | 위 파일 | 177-186 |
| `jsonEscape` | 위 파일 | 249-264 |
| 독립 스케치 | `firmware/rc522_standalone_test/rc522_standalone_test.ino` | 전체 |
| Jetson 브릿지 라인 핸들러 | `jetson_publisher/esp_bridge.py` | 162-210 |
| 브릿지 환경변수 기본값 | 위 파일 | 93-104 |
| 기존 브릿지 단위 테스트 패턴 | `jetson_publisher/tests/test_esp_bridge.py` | 19-40 |
| SPEC-AMR-001 RFID out-of-scope 선언 | `.moai/specs/SPEC-AMR-001/spec.md` | 191 |
| SPEC-AMR-001 회귀 acceptance | 위 파일 | 159 |
| v1.5.1 커밋 (healthcheck 제거) | git | `dd4c4eb` |
| v1.5.0 커밋 (NDEF 추가) | git | `5a84fc8` |

---

*이 문서는 SPEC-RC522-001 Plan Phase 0.5 산출물이다. spec.md / plan.md / acceptance.md 작성 시 이 research.md 를 단일 출처로 삼는다.*
