#!/usr/bin/env python3
"""주물공장 PyQt5 모니터링 앱 진입점.

실행:
    cd monitoring
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python main.py

환경 변수:
    CASTING_API_HOST, CASTING_API_PORT  (기본: 192.168.0.16:8000)
    CASTING_MQTT_HOST, CASTING_MQTT_PORT (기본: 192.168.0.16:1883)
"""
from __future__ import annotations

import logging
import os
import sys

from PyQt5.QtWidgets import QApplication

# monitoring/ 를 sys.path 에 추가해서 app.* import 가능하게
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from app.main_window import MainWindow  # noqa: E402
from config import APP_NAME  # noqa: E402


def _load_stylesheet(app: QApplication) -> None:
    qss_path = os.path.join(_BASE_DIR, "resources", "styles.qss")
    if os.path.exists(qss_path):
        with open(qss_path, encoding="utf-8") as fp:
            app.setStyleSheet(fp.read())


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    _load_stylesheet(app)

    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
