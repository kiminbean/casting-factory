/*
 * Conveyor Belt Controller v5.0 — Serial Bridge (V6 Architecture)
 * Base: conveyor_controller v4.0.0 (성숙한 TOF 센서 로직·anti-crosstalk 재사용)
 *
 * v4.0 → v5.0 주요 변경점:
 *   1) WiFi/MQTT 기본 비활성 (#define ENABLE_WIFI_MQTT 0).
 *      Jetson Image Publisher 와 **USB Serial** (/dev/ttyUSB0 @ 115200) 로만 통신.
 *   2) ST_STOPPED 의 5초 타임아웃 자동 탈출 제거.
 *      → Jetson 의 "RUN\n" (또는 camera_ok/inspect_done) 수신 시에만 POST_RUN 진입.
 *   3) Serial 프로토콜 토큰 추가 (기존 JSON event 는 그대로 유지, 디버깅 용):
 *        ESP → Jetson: BOOT / STOPPED / STARTED / DONE / PONG / STATE:<name>
 *        Jetson → ESP: RUN / STOP / PING / STATUS / camera_ok / inspect_done
 *
 * v4.0 과 동일하게 유지:
 *   - TOF250 (Taidacent) x2 ASCII @ 9600: TOF1=GPIO16 (진입), TOF2=GPIO17 (카메라 앞)
 *   - Motor L298N: ENA=GPIO25 (PWM), IN1=GPIO26, IN2=GPIO27
 *   - Debounce (DEBOUNCE_MS=500ms), Anti-crosstalk gating (raw2 && !raw1),
 *     MIN_RUN_MS=1000ms (motor start 후 TOF2 false trigger 차단)
 *
 * State flow:
 *   IDLE → (TOF1 감지) → RUNNING
 *        → (TOF2 감지, MIN_RUN_MS 경과 후) → STOPPED + "STOPPED\n" TX
 *        → (Jetson "RUN\n" RX) → POST_RUN + "STARTED\n" TX
 *        → (POST_RUN_MS=4000ms 경과) → CLEARING + "DONE\n" TX
 *        → (TOF2 clear) → IDLE
 */

#include <HardwareSerial.h>

// === Feature flags ===
#define ENABLE_WIFI_MQTT 0   // v5.0 기본 꺼둠. 1 로 바꾸면 v4.0 동작 (config.h 필요)

#if ENABLE_WIFI_MQTT
  #include <WiFi.h>
  #include "ESP32MQTTClient.h"
  #include "config.h"
  ESP32MQTTClient mqttClient;
  bool mqttConnected = false;
  unsigned long lastHeartbeat = 0;
#endif

// === Pin Definitions (v4.0 동일) ===
static const int PIN_MOTOR_ENA = 25;
static const int PIN_MOTOR_IN1 = 26;
static const int PIN_MOTOR_IN2 = 27;
static const int PIN_TOF1_RX   = 16;
static const int PIN_TOF2_RX   = 17;

// === Config (v4.0 동일) ===
static const long TOF_BAUD = 9600;
static const int  DETECT_MIN_MM = 1;
static const int  DETECT_MAX_MM = 30;
static const int  MOTOR_SPEED   = 180;
static const unsigned long POST_RUN_MS     = 4000;  // v5: 사용자 요구 4초
static const unsigned long CLEAR_TIMEOUT_MS = 5000;
static const unsigned long REPORT_MS       = 300;
static const unsigned long DEBOUNCE_MS     = 500;
static const unsigned long MIN_RUN_MS      = 1000;

// v5: STOPPED 탈출은 Jetson RUN 수신에만 의존 (타임아웃 자동 탈출 제거)
// 안전 타임아웃이 필요하면 아래를 양수로 (0 = 무한 대기).
static const unsigned long STOP_WAIT_TIMEOUT_MS = 0;

// === States ===
enum State { ST_IDLE, ST_RUNNING, ST_STOPPED, ST_POST_RUN, ST_CLEARING };
const char* ST_NAME[] = {"IDLE", "RUNNING", "STOPPED", "POST_RUN", "CLEARING"};

// === Globals ===
HardwareSerial tof1(1);
HardwareSerial tof2(2);

State state = ST_IDLE;
unsigned long stateStart = 0;
unsigned long lastReport = 0;

int dist1 = -1, dist2 = -1;
bool det1 = false, det2 = false;
bool raw1 = false, raw2 = false;
unsigned long det1Start = 0, det2Start = 0;
int objCount = 0;

bool visionResultReceived = false;
String visionResult = "";

String buf1 = "";
String buf2 = "";

// === Forward decls ===
void sendStatus();
void handleCommand(const String& cmd, const String& source);

// === Motor Control ===
void motorOn() {
  digitalWrite(PIN_MOTOR_IN1, HIGH);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcWrite(PIN_MOTOR_ENA, MOTOR_SPEED);
}
void motorOff() {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcWrite(PIN_MOTOR_ENA, 0);
}

// === TOF250 ASCII Parser (v4.0 동일) ===
int parseTofLine(HardwareSerial& ss, String& buffer) {
  int result = -1;
  while (ss.available()) {
    char c = ss.read();
    if (c == '\r' || c == '\n') {
      if (buffer.length() > 0) {
        result = buffer.toInt();
        buffer = "";
      }
    } else if (isdigit(c)) {
      buffer += c;
      if (buffer.length() > 10) buffer = "";
    }
  }
  return result;
}

// === Sensor Reading (v4.0 anti-crosstalk 포함) ===
void readSensors() {
  unsigned long now = millis();

  int d1 = parseTofLine(tof1, buf1);
  if (d1 >= 0) {
    dist1 = d1;
    raw1 = (d1 >= DETECT_MIN_MM && d1 <= DETECT_MAX_MM);
  }

  int d2 = parseTofLine(tof2, buf2);
  if (d2 >= 0) {
    dist2 = d2;
    raw2 = (d2 >= DETECT_MIN_MM && d2 <= DETECT_MAX_MM);
  }

  if (raw1) {
    if (det1Start == 0) det1Start = now;
    if (now - det1Start >= DEBOUNCE_MS) det1 = true;
  } else {
    det1Start = 0;
    det1 = false;
  }

  // Anti-crosstalk: TOF1 active 중엔 TOF2 raw 무시 (v4.0 핵심)
  bool raw2_valid = raw2 && !raw1;
  if (raw2_valid) {
    if (det2Start == 0) det2Start = now;
    if (now - det2Start >= DEBOUNCE_MS) det2 = true;
  } else {
    det2Start = 0;
    det2 = false;
  }
}

// === Event publish (Serial + optional MQTT) ===
void publishJson(const String& json) {
  Serial.println(json);
#if ENABLE_WIFI_MQTT
  if (mqttConnected) mqttClient.publish(TOPIC_EVENT, json.c_str(), 0, false);
#endif
}

// v5 신규: Jetson bridge 가 파싱하는 간단 토큰 라인
void publishToken(const char* token) {
  Serial.println(token);
}

void setState(State s) {
  String msg = String("{\"event\":\"state\",\"to\":\"") + ST_NAME[s] + "\"}";
  publishJson(msg);
  // v5: Jetson bridge 가 인식하는 STATE:<NAME> 라인 추가
  Serial.print("STATE:");
  Serial.println(ST_NAME[s]);
  state = s;
  stateStart = millis();
}

// === State Machine ===
void update() {
  unsigned long elapsed = millis() - stateStart;

  switch (state) {
    case ST_IDLE:
      if (det1) {
        motorOn();
        publishJson(String("{\"event\":\"entry\",\"dist\":") + dist1 + "}");
        setState(ST_RUNNING);
      }
      break;

    case ST_RUNNING:
      if (elapsed < MIN_RUN_MS) break;
      if (det2) {
        motorOff();
        visionResultReceived = false;
        visionResult = "";
        publishJson(String("{\"event\":\"exit\",\"dist\":") + dist2
                    + ",\"inspection\":\"requested\"}");
        setState(ST_STOPPED);
        publishToken("STOPPED");  // ★ Jetson bridge 트리거
      }
      break;

    case ST_STOPPED:
      // v5: Jetson 의 RUN/camera_ok/inspect_done 수신 시에만 탈출
      if (visionResultReceived) {
        objCount++;
        motorOn();
        publishJson(String("{\"event\":\"post_start\",\"count\":") + objCount
                    + ",\"reason\":\"jetson_run\""
                    + ",\"result\":\"" + (visionResult.length() ? visionResult : "unknown") + "\"}");
        visionResultReceived = false;
        setState(ST_POST_RUN);
        publishToken("STARTED");  // ★ Jetson 에 모터 재시작 통지
      } else if (STOP_WAIT_TIMEOUT_MS > 0 && elapsed >= STOP_WAIT_TIMEOUT_MS) {
        // 안전 타임아웃 (기본 0 = 비활성)
        objCount++;
        motorOn();
        publishJson("{\"event\":\"post_start\",\"reason\":\"safety_timeout\"}");
        setState(ST_POST_RUN);
        publishToken("STARTED");
      }
      break;

    case ST_POST_RUN:
      if (elapsed >= POST_RUN_MS) {
        publishJson(String("{\"event\":\"post_done\",\"tof2_det\":")
                    + (det2 ? "true" : "false") + "}");
        publishToken("DONE");  // ★ 4초 구동 완료
        setState(ST_CLEARING);
      }
      break;

    case ST_CLEARING:
      if (!det2) {
        motorOff();
        publishJson(String("{\"event\":\"cycle_done\",\"count\":") + objCount + "}");
        raw1 = raw2 = false;
        det1 = det2 = false;
        det1Start = det2Start = 0;
        setState(ST_IDLE);
      } else if (elapsed >= CLEAR_TIMEOUT_MS) {
        motorOff();
        publishJson("{\"event\":\"clear_timeout\",\"warn\":\"tof2_stuck\"}");
        raw1 = raw2 = false;
        det1 = det2 = false;
        det1Start = det2Start = 0;
        setState(ST_IDLE);
      }
      break;
  }
}

// === Command handler ===
void handleCommand(const String& cmd, const String& source) {
  // v5 신규/기존 호환 alias
  if (cmd == "RUN" || cmd == "run" || cmd == "camera_ok" || cmd == "inspect_done") {
    visionResult = "ok";
    visionResultReceived = true;
    Serial.printf("{\"ack\":\"run\",\"src\":\"%s\"}\n", source.c_str());
  }
  else if (cmd == "PING" || cmd == "ping") {
    publishToken("PONG");
  }
  else if (cmd == "STATUS" || cmd == "status") {
    sendStatus();
  }
  else if (cmd == "STOP" || cmd == "stop") {
    motorOff();
    setState(ST_IDLE);
  }
  else if (cmd == "start") {          // v4 호환 (수동 시작)
    motorOn(); setState(ST_RUNNING);
  }
  else if (cmd == "reset") {
    motorOff();
    objCount = 0;
    raw1 = raw2 = false;
    det1 = det2 = false;
    det1Start = det2Start = 0;
    visionResultReceived = false;
    visionResult = "";
    setState(ST_IDLE);
  }
  else if (cmd == "sim_entry") {
    raw1 = true; det1 = true; dist1 = 50;
    det1Start = millis() - DEBOUNCE_MS;
    Serial.println("{\"ack\":\"sim_entry\"}");
  }
  else if (cmd == "sim_exit") {
    raw2 = true; det2 = true; dist2 = 50;
    det2Start = millis() - DEBOUNCE_MS;
    Serial.println("{\"ack\":\"sim_exit\"}");
  }
  else if (cmd.length() > 0) {
    Serial.print("ERR:unknown_cmd:");
    Serial.println(cmd);
  }
}

// === Command parser (USB Serial only in v5) ===
String cmdBuf;
void processCmd() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmdBuf.length() > 0) {
        cmdBuf.trim();
        handleCommand(cmdBuf, "usb");
        cmdBuf = "";
      }
    } else if (cmdBuf.length() < 64) {
      cmdBuf += c;
    } else {
      cmdBuf = "";
    }
  }
}

void sendStatus() {
  bool motorRunning = digitalRead(PIN_MOTOR_IN1) || digitalRead(PIN_MOTOR_IN2);
  char buf[384];
  snprintf(buf, sizeof(buf),
    "{\"state\":\"%s\",\"elapsed\":%lu,\"motor\":%s,"
    "\"range\":{\"min\":%d,\"max\":%d},"
    "\"tof1\":{\"mm\":%d,\"det\":%s},"
    "\"tof2\":{\"mm\":%d,\"det\":%s},"
    "\"count\":%d}",
    ST_NAME[state], millis() - stateStart,
    motorRunning ? "true" : "false",
    DETECT_MIN_MM, DETECT_MAX_MM,
    dist1, det1 ? "true" : "false",
    dist2, det2 ? "true" : "false",
    objCount
  );
  Serial.println(buf);
}

// === Setup & Loop ===
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  tof1.begin(TOF_BAUD, SERIAL_8N1, PIN_TOF1_RX, -1);
  tof2.begin(TOF_BAUD, SERIAL_8N1, PIN_TOF2_RX, -1);

  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcAttach(PIN_MOTOR_ENA, 1000, 8);
  ledcWrite(PIN_MOTOR_ENA, 0);

  delay(500);
  Serial.println();
  Serial.println("BOOT:conveyor_v5_serial 1.1.0");
  publishJson("{\"boot\":\"conveyor_v5.0\",\"tof1\":16,\"tof2\":17,"
              "\"tof_baud\":9600,\"proto\":\"serial_only\"}");
  setState(ST_IDLE);

#if ENABLE_WIFI_MQTT
  // v4.0 스타일 WiFi/MQTT 는 필요 시 이 블록 활성화
#endif
}

void loop() {
  readSensors();
  update();
  processCmd();

  if (millis() - lastReport >= REPORT_MS) {
    lastReport = millis();
    sendStatus();
  }
}
