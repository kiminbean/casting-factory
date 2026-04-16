"""AMR 실시간 상태 워커 — SSH 경유 pinkylib 배터리 폴링.

AMR(Pinky Pro) RPi 에 SSH 접속 → pinkylib.Battery.battery_percentage() 호출.
I2C 접근에 sudo 필요.

시그널:
    status_updated(list[dict])  — [{id, host, battery, status, location}, …]
    connection_state(bool)      — 하나라도 연결 성공이면 True
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from PyQt5.QtCore import QObject, QThread, pyqtSignal

logger = logging.getLogger(__name__)

BATTERY_SCRIPT = """\
from pinkylib import Battery
import json
b = Battery()
v = b.get_voltage()
p = b.battery_percentage()
b.close()
print(json.dumps({"battery": p, "voltage": round(v, 3)}))
"""


@dataclass(frozen=True)
class AmrSshTarget:
    id: str
    host: str
    user: str
    password: str
    port: int = 22


class AmrStatusWorker(QObject):
    """SSH 기반 AMR 상태 폴링 워커."""

    status_updated = pyqtSignal(list)       # list[dict[str, Any]]
    connection_state = pyqtSignal(bool)

    def __init__(
        self,
        targets: list[AmrSshTarget],
        poll_interval: float = 10.0,
    ) -> None:
        super().__init__()
        self._targets = targets
        self._interval = poll_interval
        self._stop = False

    def request_stop(self) -> None:
        self._stop = True

    def run(self) -> None:
        try:
            import paramiko  # noqa: F401 — lazy
        except ImportError:
            logger.error("paramiko 미설치 — AMR 상태 폴링 불가")
            return

        logger.info(
            "AmrStatusWorker 시작: %d대, 간격 %.0fs",
            len(self._targets), self._interval,
        )
        any_connected = False

        while not self._stop:
            results: list[dict[str, Any]] = []
            connected = False

            for t in self._targets:
                data = self._poll_one(t)
                if data is not None:
                    connected = True
                    results.append({
                        "id": t.id,
                        "host": t.host,
                        "battery": data.get("battery", 0),
                        "voltage": data.get("voltage", 0),
                        "status": "running" if data.get("battery", 0) > 0 else "idle",
                        "location": "-",
                    })
                else:
                    results.append({
                        "id": t.id,
                        "host": t.host,
                        "battery": 0,
                        "status": "error",
                        "location": "-",
                    })

            if connected != any_connected:
                any_connected = connected
                self.connection_state.emit(connected)

            if results:
                self.status_updated.emit(results)

            # interruptible sleep
            deadline = time.monotonic() + self._interval
            while not self._stop and time.monotonic() < deadline:
                time.sleep(0.5)

        logger.info("AmrStatusWorker 종료")

    @staticmethod
    def _poll_one(target: AmrSshTarget) -> dict[str, Any] | None:
        import paramiko

        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect(
                hostname=target.host,
                port=target.port,
                username=target.user,
                password=target.password,
                timeout=5,
                look_for_keys=False,
                allow_agent=False,
            )
            # I2C requires sudo; use heredoc to avoid quote escaping issues
            cmd = "sudo -S python3 - <<'PY'\n" + BATTERY_SCRIPT + "PY\n"
            stdin, out, err = c.exec_command(cmd, timeout=15, get_pty=True)
            stdin.write(target.password + "\n")
            stdin.flush()

            stdout = out.read().decode().strip()
            # stdout may contain password echo + sudo prompt; take last line with JSON
            for line in reversed(stdout.splitlines()):
                line = line.strip()
                if line.startswith("{"):
                    return json.loads(line)

            logger.warning("AMR %s: no JSON in stdout: %s", target.id, stdout[-200:])
            return None
        except Exception as exc:  # noqa: BLE001
            logger.warning("AMR %s (%s) 폴링 실패: %s", target.id, target.host, exc)
            return None
        finally:
            c.close()


class AmrStatusThread(QThread):
    """AmrStatusWorker 를 구동하는 QThread 래퍼."""

    def __init__(self, worker: AmrStatusWorker, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._worker = worker
        self._worker.moveToThread(self)

    def run(self) -> None:
        self._worker.run()

    def shutdown(self) -> None:
        self._worker.request_stop()
        self.quit()
        self.wait(5000)
