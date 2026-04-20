# 주물공장 모니터링 앱 (PyQt5)

주물공장 관제 시스템의 **모니터링 전용 데스크톱 앱**. 현장 관제실에서 실행되며, FastAPI 백엔드를 통해 대시보드 / 생산 모니터링 / 품질 검사 / 물류 이송을 실시간으로 표시한다.

> 배경: Confluence 페이지 `관제 기술조사인가..?` (ID 17956894) 에서 결정한 UI 분리 정책에 따라 기존 Next.js 웹 대시보드에서 모니터링 영역만 분리한 것.

## 역할 분리

| 대상 | 앱 | 담당 화면 |
|------|-----|----------|
| 관리자 (사무실) | Next.js 웹 | 생산 계획, 주문 관리, 품질 관리, 입출고 내역 |
| 관제실 (현장) | **PyQt5 (이 앱)** | 대시보드, 생산 모니터링, 품질 검사, 물류 이송 |
| 고객 | Next.js 웹 (`/customer`) | 주문 등록, 배송 조회 |

## 기술 스택

- Python 3.11+ (Apple Silicon 은 3.12 고정 — PyQt5/grpcio 휠 호환)
- PyQt5 5.15
- grpcio (V6 canonical: Management Service 직결 TCP :50051)
- requests (legacy REST — Phase C 까지 잠정 유지)
- paho-mqtt (Phase D 에서 제거 예정)

## 설치

```bash
cd monitoring
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 실행

```bash
# 기본 (API 서버 192.168.0.16:8000 에 접속)
python main.py

# 다른 호스트 지정
CASTING_API_HOST=192.168.0.50 CASTING_API_PORT=8000 python main.py

# 로컬 개발
CASTING_API_HOST=127.0.0.1 python main.py
```

## 디렉토리 구조

```
monitoring/
├── main.py                # QApplication 진입점
├── config.py              # 엔드포인트 설정
├── requirements.txt
├── README.md
├── app/
│   ├── main_window.py     # QMainWindow (사이드바 + 스택)
│   ├── management_client.py # Management Service gRPC stub (V6 canonical)
│   ├── api_client.py      # FastAPI REST 호출 (legacy, Phase C 까지)
│   └── pages/
│       ├── dashboard.py   # KPI 카드 + 알림
│       ├── production.py  # 공정 / 설비 상태
│       ├── quality.py     # 검사 이력 / 불량 통계
│       └── logistics.py   # AMR / 이송 작업
└── resources/
    └── styles.qss         # Qt 스타일시트
```

## 통신

### REST
- `GET /api/dashboard/stats` - KPI 요약
- `GET /api/alerts` - 알림
- `GET /api/production/metrics`, `/equipment`, `/stages`
- `GET /api/quality/inspections`, `/defect-stats`
- `GET /api/logistics/tasks`, `/amr`

### WebSocket
- `ws://<api>:<port>/ws/dashboard` - 실시간 이벤트 broadcast
- 이벤트 타입: `dashboard_update`, `production_update`, `equipment_update`, `quality_update`, `amr_update`, `transport_task_update`

### MQTT (Phase 1+)
- `conveyor/+/status`, `conveyor/+/event`
- `vision/+/result`
- `cobot/+/status`
- `amr/+/position`
- `factory/alarm`

## 주기 갱신

- 타이머 3초 간격으로 현재 보이는 페이지만 REST 재조회
- WebSocket 이벤트 수신 시 해당 페이지만 즉시 갱신
- 네트워크 장애 시 3초 후 WebSocket 자동 재연결

## 로드맵

- **v0.1.0** (현재): 4개 페이지 골격, REST + WebSocket 연동
- **v0.2.0**: MQTT 직접 구독 추가 (ESP32 컨베이어 실시간 상태)
- **v0.3.0**: 차트 위젯 (PyQtChart) 추가, 3D 맵 뷰어 연동
- **v0.4.0**: 알람 팝업, 사운드 알림, 에러 조치 버튼
- **v1.0.0**: 배포 패키징 (PyInstaller), 관제실 고정 레이아웃
