# Conveyor v5.0 — Serial Bridge Firmware

V6 새 아키텍처에 맞춘 **ESP32 Serial 전용** 펌웨어. WiFi/MQTT 제거.

## 흐름

```
[주물이 센서2 도달]
   ↓ (TOF2 ≤ 15cm)
모터 정지 → "STOPPED\n" TX
   ↓
[Jetson 촬영 완료]
   ↓ "RUN\n" RX
모터 ON → "STARTED\n" TX
   ↓ 4초 타이머
모터 OFF → "DONE\n" TX → IDLE
```

## Serial 프로토콜

| 방향 | 메시지 | 의미 |
|---|---|---|
| ESP → Jetson | `BOOT:conveyor_v5_serial 1.0.0` | 부팅 완료 |
| ESP → Jetson | `STATE:IDLE / STOPPED / RUNNING` | 상태 전이 |
| ESP → Jetson | `STOPPED` | 센서2 감지 → 정지 완료 (촬영 요청) |
| ESP → Jetson | `STARTED` | RUN 수신 → 모터 ON 완료 |
| ESP → Jetson | `DONE` | 4초 경과 자동 정지 |
| ESP → Jetson | `PONG` | PING 응답 |
| Jetson → ESP | `RUN\n` | 모터 구동 (4초) |
| Jetson → ESP | `STOP\n` | 즉시 정지 (비상) |
| Jetson → ESP | `PING\n` | Health check |
| Jetson → ESP | `STATUS\n` | 현재 상태 요청 |

## 파라미터 (상단 `const` 로 조정)

- `MOTOR_SPEED_PWM = 200` — 0~255
- `RUN_DURATION_MS = 4000` — 4초
- `DETECT_DISTANCE_CM = 15` — 센서2 임계
- `HEARTBEAT_MS = 0` — 0 = 비활성

## 빌드 & 업로드 (arduino-cli)

Jetson 또는 개발 Mac 에서 arduino-cli 로 바로 업로드 가능.

```bash
arduino-cli core install esp32:esp32
cd firmware/conveyor_v5_serial
arduino-cli compile --fqbn esp32:esp32:esp32 .
arduino-cli upload --fqbn esp32:esp32:esp32 -p /dev/ttyUSB0 .

# Jetson 에서 원격 업로드:
# scp firmware/conveyor_v5_serial/*.ino jetson@100.77.62.67:/tmp/
# ssh jetson@100.77.62.67 "arduino-cli ..."
```

## 검증 (아두이노 업로드 후)

```bash
# Jetson 에서
python3 -c "
import serial, time
s = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
time.sleep(1.5)
s.reset_input_buffer()

# 부팅 라인 수신
print(s.read(200))

# PING/PONG
s.write(b'PING\n')
print(s.readline())

# 센서2 수동 차단 후
# → STOPPED\n 수신 확인
# 이후
s.write(b'RUN\n')  # 4초 구동
print(s.readline())  # STARTED
# 4초 후 DONE
"
```

## v4.0 대비 변경점

- ❌ WiFi (라이브러리 + 코드) 제거
- ❌ MQTT (ESP32MQTTClient) 제거
- ❌ vision/1/result 구독 로직 제거
- ✅ Serial 양방향 프로토콜 신설
- ✅ 상태기 단순화 (IDLE/STOPPED/RUNNING 3개)
- ✅ 정지 시간 고정 제거 (Jetson 이 RUN 보낼 때까지 대기)
