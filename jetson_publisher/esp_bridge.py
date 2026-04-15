"""ESP32 Serial Bridge — Jetson ↔ Conveyor 펌웨어(v5) 이벤트 중계.

V6 아키텍처 (2026-04-15 업데이트):
    [ESP32 conveyor v5] --USB Serial 115200 ASCII-- [Jetson publisher]

본 모듈은 publisher.py 와 **같은 프로세스** 내 별도 스레드로 실행.
- RX(ESP→Jetson): STATE/STOPPED/STARTED/DONE/PONG/SENSOR* 등 라인 파싱
- TX(Jetson→ESP): RUN/STOP/PING/STATUS 등 명령 송신
- 핵심 이벤트: "STOPPED" 수신 → (지연 INSPECTION_DELAY_MS) → "RUN\\n" 송신
    · 지연 동안 publisher 가 적어도 1 프레임을 서버로 push 완료한다는 가정
    · 2 fps 기준 기본 500 ms + 여유 → 기본 700 ms
- 재연결: Serial 끊기면 10s backoff

환경변수:
    ESP_BRIDGE_ENABLED           기본 0 (opt-in). 1 이면 스레드 기동
    ESP_BRIDGE_PORT              기본 /dev/ttyUSB0
    ESP_BRIDGE_BAUD              기본 115200
    ESP_BRIDGE_AUTO_RUN          기본 1 (STOPPED 시 자동 RUN 송신). 0 이면 로그만
    ESP_BRIDGE_INSPECTION_DELAY_MS  기본 700 (STOPPED 후 RUN 까지 대기)

@MX:NOTE STOPPED 순간의 "정확한 한 프레임" 보장이 필요하면 publisher 와 이벤트 동기
        메커니즘(threading.Event) 을 추가하세요. 현재 MVP 는 시간 기반 지연으로 단순화.
@MX:WARN publisher 가 /dev/ttyUSB0 을 쓰지 않음 (카메라는 /dev/video0). 충돌 없음.
"""
from __future__ import annotations

import logging
import os
import threading
import time

log = logging.getLogger("jetson.esp_bridge")


class EspBridge:
    """ESP32 serial 브리지 스레드."""

    def __init__(
        self,
        shutdown_event: threading.Event,
        port: str = "/dev/ttyUSB0",
        baud: int = 115200,
        auto_run: bool = True,
        inspection_delay_ms: int = 700,
        reconnect_sec: float = 10.0,
    ) -> None:
        self._shutdown = shutdown_event
        self._port = port
        self._baud = baud
        self._auto_run = auto_run
        self._inspection_delay = inspection_delay_ms / 1000.0
        self._reconnect = reconnect_sec
        self._thread = threading.Thread(
            target=self._run, name="esp-bridge", daemon=True
        )

    @classmethod
    def from_env(cls, shutdown_event: threading.Event) -> "EspBridge":
        return cls(
            shutdown_event=shutdown_event,
            port=os.environ.get("ESP_BRIDGE_PORT", "/dev/ttyUSB0"),
            baud=int(os.environ.get("ESP_BRIDGE_BAUD", "115200")),
            auto_run=os.environ.get("ESP_BRIDGE_AUTO_RUN", "1") in ("1", "true", "yes"),
            inspection_delay_ms=int(os.environ.get("ESP_BRIDGE_INSPECTION_DELAY_MS", "700")),
        )

    def start(self) -> None:
        if self._thread.is_alive():
            return
        log.info("EspBridge 시작: port=%s baud=%d auto_run=%s delay=%.2fs",
                 self._port, self._baud, self._auto_run, self._inspection_delay)
        self._thread.start()

    # ---------- internal ----------
    def _run(self) -> None:
        try:
            import serial  # lazy
        except ImportError:
            log.error("pyserial 미설치. `pip install pyserial` 필요")
            return

        while not self._shutdown.is_set():
            ser = None
            try:
                ser = serial.Serial(self._port, self._baud, timeout=0.5)
                # ESP32 DTR 토글에 의한 reset 대기 + 부팅 라인 버림
                time.sleep(1.5)
                ser.reset_input_buffer()
                log.info("EspBridge connected to %s @ %d", self._port, self._baud)
                self._session(ser)
            except Exception as e:  # noqa: BLE001
                if self._shutdown.is_set():
                    break
                log.warning("EspBridge serial 오류: %s (재연결 %.1fs)", e, self._reconnect)
                self._shutdown.wait(self._reconnect)
            finally:
                if ser is not None:
                    try:
                        ser.close()
                    except Exception:  # noqa: BLE001
                        pass
        log.info("EspBridge stopped")

    def _session(self, ser) -> None:
        """개방된 serial 세션에서 라인 단위 이벤트 처리."""
        buf = bytearray()
        while not self._shutdown.is_set():
            chunk = ser.read(64)
            if chunk:
                buf += chunk
                while b"\n" in buf:
                    line_b, _, rest = buf.partition(b"\n")
                    buf = bytearray(rest)
                    line = line_b.decode(errors="replace").strip()
                    if line:
                        self._handle_line(ser, line)

    def _handle_line(self, ser, line: str) -> None:
        if line == "STOPPED":
            log.info("ESP → STOPPED (inspection trigger)")
            if self._auto_run:
                # publisher 가 현재 프레임을 서버로 push 할 시간 부여
                time.sleep(self._inspection_delay)
                try:
                    ser.write(b"RUN\n")
                    ser.flush()
                    log.info("Jetson → RUN (after %.2fs delay)", self._inspection_delay)
                except Exception as e:  # noqa: BLE001
                    log.warning("RUN 송신 실패: %s", e)
            else:
                log.info("auto_run=0, STOPPED 대기만 (수동 RUN 필요)")
        elif line == "STARTED":
            log.info("ESP → STARTED (motor on)")
        elif line == "DONE":
            log.info("ESP → DONE (motor off after 4s)")
        elif line.startswith("BOOT:"):
            log.info("ESP bootup: %s", line)
        elif line.startswith("STATE:"):
            log.debug("ESP state: %s", line)
        elif line.startswith("PONG"):
            log.debug("ESP pong")
        elif line.startswith("ERR:"):
            log.warning("ESP error: %s", line)
        else:
            log.debug("ESP line: %s", line)
