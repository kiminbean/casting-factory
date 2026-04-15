/*
 * Conveyor Belt Controller v5.0.0 — Serial Bridge (V6 Architecture)
 *
 * New V6 policy: ESP32 는 USB Serial 로 Jetson (Image Publisher) 와만 통신.
 * WiFi/MQTT 를 완전히 제거하고 단순화.
 *
 * 시나리오:
 *   1) 주물이 카메라 앞 센서2(TOF2) 에 감지되면 컨베이어 자동 정지
 *   2) ESP32 → Jetson: "STOPPED\n" 송신
 *   3) Jetson 이 이미지 촬영 완료 후 "RUN\n" 송신
 *   4) ESP32 → 컨베이어 ON, 4초 타이머 시작
 *   5) 4초 경과 → 컨베이어 OFF + "DONE\n" 송신, IDLE 복귀
 *
 * Serial 프로토콜 (Jetson ↔ ESP32, 115200 baud, ASCII line CR+LF 종료)
 *   Host→ESP32:
 *     "RUN\n"        RUN 요청 (STOPPED 상태일 때만 유효)
 *     "PING\n"       Health check — "PONG\n" 응답
 *     "STATUS\n"     현재 상태 1회 송신
 *   ESP32→Host:
 *     "STOPPED\n"    센서2 감지 → 정지 완료 (촬영 요청)
 *     "STARTED\n"    RUN 수신 후 모터 ON 완료
 *     "DONE\n"       4초 경과 후 자동 정지
 *     "PONG\n"       PING 응답
 *     "STATE:<name>\n"  현재 상태 (STATUS 요청 응답 또는 변경 시)
 *     "SENSOR1:<cm>\n"  (옵션) TOF1 거리 디버깅
 *     "SENSOR2:<cm>\n"  (옵션) TOF2 거리 디버깅
 *
 * Hardware (기존 v4.0 과 동일 배선):
 *   Motor: JGB37-555 12V DC via L298N (ENA=25, IN1=26, IN2=27)
 *   Sensor2 (카메라 앞): TOF250 Taidacent, White→GPIO17 (UART2 RX) @ 9600 ASCII
 *   Sensor1 (진입 감지, 옵션): TOF250, White→GPIO16 (UART1 RX) @ 9600 ASCII
 *     ※ 센서1 은 감지 이벤트 송신만 (상태기 영향 없음)
 *
 * Build: Arduino IDE / arduino-cli with ESP32 core 3.x
 *   FQBN: esp32:esp32:esp32
 *   baud: 115200 (Jetson Serial)
 */

#include <HardwareSerial.h>

// === Pin Definitions ===
static const int PIN_MOTOR_ENA = 25;
static const int PIN_MOTOR_IN1 = 26;
static const int PIN_MOTOR_IN2 = 27;
static const int PIN_TOF1_RX   = 16;  // 센서1 (진입) - 선택 사용
static const int PIN_TOF2_RX   = 17;  // 센서2 (카메라 앞) - 주 트리거

// === Serial / TOF baud ===
static const long HOST_BAUD = 115200; // Jetson ↔ ESP32
static const long TOF_BAUD  = 9600;   // TOF250 Taidacent

// === Motion parameters ===
static const int MOTOR_SPEED_PWM    = 200;   // 0..255 (약 ~78%)
static const uint32_t RUN_DURATION_MS = 4000; // 4초 구동 후 자동 정지
static const uint16_t DETECT_DISTANCE_CM = 15;  // 센서2 감지 임계 (cm)

// === Heartbeat (옵션) ===
static const uint32_t HEARTBEAT_MS = 0; // 0 = 비활성. 양수면 STATE 주기 송신

// === Sensor objects ===
HardwareSerial TOF1(1);  // UART1
HardwareSerial TOF2(2);  // UART2

// === State machine ===
enum State { IDLE, STOPPED, RUNNING };
State state = IDLE;
uint32_t runStartMs = 0;
uint32_t lastHeartbeatMs = 0;

// === TOF line parsers (ASCII NNN\r\n) ===
String tof1Buf, tof2Buf;

bool tryParseTof(HardwareSerial& port, String& buf, int& outCm) {
  while (port.available()) {
    char c = (char)port.read();
    if (c == '\n' || c == '\r') {
      if (buf.length() > 0) {
        outCm = buf.toInt();
        buf = "";
        return true;
      }
    } else if (isDigit(c) && buf.length() < 6) {
      buf += c;
    } else {
      buf = ""; // noise reset
    }
  }
  return false;
}

// === Motor control ===
void motorSet(bool on) {
  digitalWrite(PIN_MOTOR_IN1, on ? HIGH : LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_ENA, on ? MOTOR_SPEED_PWM : 0);
}

// === State transitions ===
const char* stateName(State s) {
  switch (s) {
    case IDLE:    return "IDLE";
    case STOPPED: return "STOPPED";
    case RUNNING: return "RUNNING";
  }
  return "?";
}

void enterState(State s) {
  state = s;
  Serial.print("STATE:");
  Serial.println(stateName(s));
}

// === Command handling (Jetson → ESP32) ===
String cmdBuf;

void handleCommand(const String& cmd) {
  if (cmd == "PING") {
    Serial.println("PONG");
  } else if (cmd == "STATUS") {
    Serial.print("STATE:");
    Serial.println(stateName(state));
  } else if (cmd == "RUN") {
    if (state == STOPPED || state == IDLE) {
      motorSet(true);
      runStartMs = millis();
      enterState(RUNNING);
      Serial.println("STARTED");
    } else {
      Serial.println("ERR:already_running");
    }
  } else if (cmd == "STOP") {
    motorSet(false);
    enterState(IDLE);
  } else if (cmd.length() > 0) {
    Serial.print("ERR:unknown_cmd:");
    Serial.println(cmd);
  }
}

// === Setup ===
void setup() {
  pinMode(PIN_MOTOR_ENA, OUTPUT);
  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  motorSet(false);

  Serial.begin(HOST_BAUD);
  TOF1.begin(TOF_BAUD, SERIAL_8N1, PIN_TOF1_RX, -1);
  TOF2.begin(TOF_BAUD, SERIAL_8N1, PIN_TOF2_RX, -1);

  delay(100);
  Serial.println();
  Serial.println("BOOT:conveyor_v5_serial 1.0.0");
  enterState(IDLE);
}

// === Main loop ===
void loop() {
  // 1) Command from Jetson
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmdBuf.length() > 0) {
        handleCommand(cmdBuf);
        cmdBuf = "";
      }
    } else if (cmdBuf.length() < 32) {
      cmdBuf += c;
    } else {
      cmdBuf = ""; // overflow
    }
  }

  // 2) Sensor polling
  int d1 = -1, d2 = -1;
  bool got1 = tryParseTof(TOF1, tof1Buf, d1);
  bool got2 = tryParseTof(TOF2, tof2Buf, d2);

  // 3) State machine
  uint32_t now = millis();
  switch (state) {
    case IDLE:
    case RUNNING:
      // RUNNING 중 센서2 감지 → 정지 (카메라 앞 도착)
      if (got2 && d2 > 0 && d2 <= DETECT_DISTANCE_CM) {
        motorSet(false);
        enterState(STOPPED);
        Serial.println("STOPPED");
      } else if (state == RUNNING && (now - runStartMs) >= RUN_DURATION_MS) {
        // 4초 타임아웃 — 자동 정지
        motorSet(false);
        enterState(IDLE);
        Serial.println("DONE");
      }
      break;
    case STOPPED:
      // Jetson 의 RUN 명령을 기다림 (handleCommand 에서 처리)
      break;
  }

  // 4) Heartbeat (옵션)
  if (HEARTBEAT_MS > 0 && (now - lastHeartbeatMs) >= HEARTBEAT_MS) {
    lastHeartbeatMs = now;
    Serial.print("HB:");
    Serial.println(stateName(state));
  }

  delay(5); // 200Hz 루프
}
