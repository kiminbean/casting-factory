/*
 * Conveyor Belt Controller - ESP32 DevKitC V4
 * v3.0.0 - TOF250 ASCII UART protocol
 *
 * Hardware:
 *   - Motor: JGB37-555 DC12V 167RPM (via L298N motor driver)
 *   - Sensors: TOF250 (Taidacent) x2 - ASCII UART @ 9600 baud
 *   - MCU: ESP32 DevKitC V4
 *
 * Sensor wiring (only White TX needed):
 *   TOF1 White -> GPIO16 (UART1 RX)
 *   TOF2 White -> GPIO17 (UART2 RX)
 *   Both: Red -> 3.3V, Black -> GND
 *   Yellow, Blue, Green: NOT CONNECTED
 *
 * Sensor output: ASCII "NNN\r\n" format (e.g. "18\r\n")
 *
 * Motor wiring (L298N):
 *   ENA -> GPIO25 (PWM)
 *   IN1 -> GPIO26
 *   IN2 -> GPIO27
 *
 * State flow:
 *   IDLE -> (TOF1 detect) -> RUNNING
 *        -> (TOF2 detect) -> STOPPED (5s)
 *        -> POST_RUN (2s)
 *        -> CLEARING (until TOF2 clear)
 *        -> IDLE
 */

#include <HardwareSerial.h>

// === Pin Definitions ===
static const int PIN_MOTOR_ENA = 25;
static const int PIN_MOTOR_IN1 = 26;
static const int PIN_MOTOR_IN2 = 27;
static const int PIN_TOF1_RX   = 16;  // Sensor 1 White wire
static const int PIN_TOF2_RX   = 17;  // Sensor 2 White wire

// === Config ===
static const long TOF_BAUD = 9600;   // TOF250 Taidacent baud rate
static const int  DETECT_MIN_MM = 1;   // 1mm 이상이면 감지
static const int  DETECT_MAX_MM = 30;  // 3cm 이내만 감지 (실제 주물은 4-8mm)
static const int  MOTOR_SPEED   = 180;
static const unsigned long STOP_WAIT_MS    = 5000;  // 센서2 감지 후 대기
static const unsigned long POST_RUN_MS     = 4000;  // 후처리 모터 구동 시간
static const unsigned long CLEAR_TIMEOUT_MS = 5000;
static const unsigned long REPORT_MS       = 300;
static const unsigned long DEBOUNCE_MS     = 500;

// Anti-crosstalk: Minimum motor run time before TOF2 can trigger exit.
// Two TOF250 sensors mounted close together cross-talk on 940nm IR.
// This blocks false TOF2 detection within MIN_RUN_MS after motor start.
static const unsigned long MIN_RUN_MS = 1000;  // 1초

// === States ===
enum State { ST_IDLE, ST_RUNNING, ST_STOPPED, ST_POST_RUN, ST_CLEARING };
const char* ST_NAME[] = {"idle", "running", "stopped", "post_run", "clearing"};

// === Globals ===
HardwareSerial tof1(1);
HardwareSerial tof2(2);

State state = ST_IDLE;
unsigned long stateStart = 0;
unsigned long lastReport = 0;

int dist1 = -1, dist2 = -1;
bool det1 = false, det2 = false;      // debounced
bool raw1 = false, raw2 = false;      // instant
unsigned long det1Start = 0, det2Start = 0;
int objCount = 0;

// ASCII parsing buffers
String buf1 = "";
String buf2 = "";

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

// === TOF250 ASCII Parser ===
// Reads bytes, accumulates into buffer until \r or \n, then parses int
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
      if (buffer.length() > 10) buffer = "";  // safety
    } else {
      // ignore non-digit non-terminator chars (e.g., unit text)
    }
  }
  return result;
}

// === Sensor Reading with Debounce ===
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

  // Debounce TOF1
  if (raw1) {
    if (det1Start == 0) det1Start = now;
    if (now - det1Start >= DEBOUNCE_MS) det1 = true;
  } else {
    det1Start = 0;
    det1 = false;
  }

  // Debounce TOF2 with anti-crosstalk gating:
  // TOF1 IR emitter saturates TOF2 receiver when TOF1 sees an object,
  // making TOF2 falsely report ~5mm. Ignore TOF2 raw signal whenever
  // TOF1 raw is also active. Object only counts when it has cleared TOF1.
  bool raw2_valid = raw2 && !raw1;
  if (raw2_valid) {
    if (det2Start == 0) det2Start = now;
    if (now - det2Start >= DEBOUNCE_MS) det2 = true;
  } else {
    det2Start = 0;
    det2 = false;
  }
}

// === State Machine ===
void setState(State s) {
  Serial.printf("{\"event\":\"state\",\"to\":\"%s\"}\n", ST_NAME[s]);
  state = s;
  stateStart = millis();
}

void update() {
  unsigned long elapsed = millis() - stateStart;

  switch (state) {
    case ST_IDLE:
      if (det1) {
        motorOn();
        Serial.printf("{\"event\":\"entry\",\"dist\":%d}\n", dist1);
        setState(ST_RUNNING);
      }
      break;

    case ST_RUNNING:
      // Anti-crosstalk: ignore TOF2 detection during minimum run window
      if (elapsed < MIN_RUN_MS) {
        // wait for object to physically travel from TOF1 to TOF2
        break;
      }
      if (det2) {
        motorOff();
        Serial.printf("{\"event\":\"exit\",\"dist\":%d}\n", dist2);
        setState(ST_STOPPED);
      }
      break;

    case ST_STOPPED:
      if (elapsed >= STOP_WAIT_MS) {
        objCount++;
        motorOn();
        Serial.printf("{\"event\":\"post_start\",\"count\":%d}\n", objCount);
        setState(ST_POST_RUN);
      }
      break;

    case ST_POST_RUN:
      if (elapsed >= POST_RUN_MS) {
        Serial.printf("{\"event\":\"post_done\",\"tof2_det\":%s}\n",
                      det2 ? "true" : "false");
        setState(ST_CLEARING);
      }
      break;

    case ST_CLEARING:
      if (!det2) {
        motorOff();
        Serial.printf("{\"event\":\"cycle_done\",\"count\":%d}\n", objCount);
        raw1 = raw2 = false;
        det1 = det2 = false;
        det1Start = det2Start = 0;
        setState(ST_IDLE);
      } else if (elapsed >= CLEAR_TIMEOUT_MS) {
        motorOff();
        Serial.println("{\"event\":\"clear_timeout\",\"warn\":\"tof2_stuck\"}");
        raw1 = raw2 = false;
        det1 = det2 = false;
        det1Start = det2Start = 0;
        setState(ST_IDLE);
      }
      break;
  }
}

// === Serial Commands ===
void processCmd() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd == "start")        { motorOn(); setState(ST_RUNNING); }
  else if (cmd == "stop")    { motorOff(); setState(ST_IDLE); }
  else if (cmd == "reset")   {
    motorOff();
    objCount = 0;
    raw1 = raw2 = false;
    det1 = det2 = false;
    det1Start = det2Start = 0;
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
  else if (cmd == "status") { sendStatus(); }
}

void sendStatus() {
  bool motorRunning = digitalRead(PIN_MOTOR_IN1) || digitalRead(PIN_MOTOR_IN2);
  Serial.printf(
    "{\"state\":\"%s\",\"elapsed\":%lu,\"motor\":%s,"
    "\"range\":{\"min\":%d,\"max\":%d},"
    "\"tof1\":{\"mm\":%d,\"det\":%s},"
    "\"tof2\":{\"mm\":%d,\"det\":%s},"
    "\"count\":%d}\n",
    ST_NAME[state], millis() - stateStart,
    motorRunning ? "true" : "false",
    DETECT_MIN_MM, DETECT_MAX_MM,
    dist1, det1 ? "true" : "false",
    dist2, det2 ? "true" : "false",
    objCount
  );
}

// === Setup & Loop ===
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  // TOF250 sensors @ 9600 baud ASCII
  tof1.begin(TOF_BAUD, SERIAL_8N1, PIN_TOF1_RX, -1);
  tof2.begin(TOF_BAUD, SERIAL_8N1, PIN_TOF2_RX, -1);

  // Motor driver
  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcAttach(PIN_MOTOR_ENA, 1000, 8);
  ledcWrite(PIN_MOTOR_ENA, 0);

  delay(500);
  Serial.println("{\"boot\":\"conveyor_v3.0\",\"tof1\":16,\"tof2\":17,\"baud\":9600,\"proto\":\"ASCII\"}");
  stateStart = millis();
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
