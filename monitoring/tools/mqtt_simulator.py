#!/usr/bin/env python3
"""MQTT 브로커에 가상 ESP32 컨베이어 메시지를 발행하는 시뮬레이터.

용도:
    PyQt5 모니터링 앱이 구독 중인 토픽에 실제 ESP32 없이도
    현실적인 상태 변화를 주기적으로 발행해서 UI 동작을 검증.

사용:
    # 터미널 1: mosquitto 실행
    mosquitto

    # 터미널 2: 모니터링 앱 (MQTT 활성화)
    CASTING_MQTT_ENABLED=1 python main.py

    # 터미널 3: 시뮬레이터
    python tools/mqtt_simulator.py
"""
from __future__ import annotations

import json
import random
import sys
import time

import paho.mqtt.client as mqtt


BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883


def publish(client: mqtt.Client, topic: str, payload: dict | str, retain: bool = False) -> None:
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    client.publish(topic, payload, retain=retain)


def simulate_conveyor_cycle(client: mqtt.Client, conveyor_id: int) -> None:
    """하나의 컨베이어 사이클을 10초에 걸쳐 발행.

    idle → running(TOF1 감지) → stopped(TOF2 감지) → post_run → clearing → idle
    """
    topic_status = f"conveyor/{conveyor_id}/status"
    topic_event = f"conveyor/{conveyor_id}/event"

    def status(state, motor, tof1_mm, tof1_det, tof2_mm, tof2_det, count):
        publish(client, topic_status, {
            "state": state,
            "motor": motor,
            "tof1": {"mm": tof1_mm, "det": tof1_det},
            "tof2": {"mm": tof2_mm, "det": tof2_det},
            "count": count,
        })

    # 시작 카운트 랜덤
    count = random.randint(10, 50)

    # 1. idle (대기)
    status("idle", False, 200, False, 200, False, count)
    time.sleep(0.5)

    # 2. TOF1 감지 → running
    publish(client, topic_event, {"event": "entry", "dist": 45})
    status("running", True, 45, True, 200, False, count)
    time.sleep(2.0)

    # 이동 중 (TOF1 벗어남)
    status("running", True, 200, False, 200, False, count)
    time.sleep(1.5)

    # 3. TOF2 감지 → stopped
    publish(client, topic_event, {"event": "exit", "dist": 42})
    status("stopped", False, 200, False, 42, True, count)
    time.sleep(3.0)  # 검사 대기 (실제는 5초)

    # 4. post_run
    count += 1
    publish(client, topic_event, {"event": "post_start", "count": count})
    status("post_run", True, 200, False, 42, True, count)
    time.sleep(2.0)

    # 5. clearing
    status("clearing", True, 200, False, 200, False, count)
    time.sleep(0.5)

    # 6. 사이클 완료 → idle
    publish(client, topic_event, {"event": "cycle_done", "count": count})
    status("idle", False, 200, False, 200, False, count)


def main() -> int:
    print(f"Connecting to {BROKER_HOST}:{BROKER_PORT}...")
    client = mqtt.Client(
        client_id="conveyor_simulator",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()
    time.sleep(0.3)

    # 초기 heartbeat (retained)
    for cid in [1, 2]:
        publish(client, f"conveyor/{cid}/heartbeat", "online", retain=True)
    print("Published heartbeat")

    cycle_num = 0
    try:
        while True:
            cycle_num += 1
            print(f"\n=== Cycle #{cycle_num} - Conveyor 1 ===")
            simulate_conveyor_cycle(client, 1)
            time.sleep(1.0)

            # Vision 결과 (홀수 사이클 = ok, 5의 배수 = ng)
            if cycle_num % 5 == 0:
                vision = {"result": "ng", "product_id": f"M500-{cycle_num:04d}",
                          "confidence": 87.2, "defect_type": "기공"}
                print(f"Vision NG: {vision}")
                publish(client, "vision/1/result", vision)
                # 알람 발행
                publish(client, "factory/alarm", {
                    "level": "warning",
                    "source": "CAM-001",
                    "message": f"불량 감지: 기공 (M500-{cycle_num:04d})",
                })
            else:
                publish(client, "vision/1/result", {"result": "ok"})

            time.sleep(2.0)
    except KeyboardInterrupt:
        print("\nStopping...")
        for cid in [1, 2]:
            publish(client, f"conveyor/{cid}/heartbeat", "offline", retain=True)
        time.sleep(0.3)
        client.loop_stop()
        client.disconnect()
        return 0


if __name__ == "__main__":
    sys.exit(main())
