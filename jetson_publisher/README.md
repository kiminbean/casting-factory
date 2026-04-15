# Jetson Image Publisher (V6 Image Publishing Service)

Jetson Orin NX 16GB 에서 USB 카메라 프레임을 Management Server(:50051) 로 gRPC client streaming 으로 push 한다.

## 구조

```
jetson_publisher/
├── publisher.py                 # 메인 실행 파일
├── requirements.txt             # grpcio / protobuf / numpy
├── env.example                  # 환경변수 템플릿
├── generated/                   # protoc 산출물 (monitoring/ 에서 복사)
│   ├── management_pb2.py
│   └── management_pb2_grpc.py
├── systemd/
│   └── casting-image-publisher.service
├── deploy.sh                    # 로컬 Mac → Jetson rsync
└── README.md
```

## 배포 (로컬 Mac → Jetson)

1회 설치:
```bash
bash jetson_publisher/deploy.sh --install
# → /home/jetson/casting-image-publisher/ 로 rsync + apt python3-opencv + systemd enable
```

이후 코드 변경만 동기화:
```bash
bash jetson_publisher/deploy.sh
ssh jetson@100.77.62.67 'sudo systemctl restart casting-image-publisher'
```

## Jetson 측 설정

```bash
# 1회만 — env 파일 수정
ssh jetson@100.77.62.67
cd ~/casting-image-publisher
nano env
#   MANAGEMENT_GRPC_HOST=<Mgmt Server Tailscale IP>
#   JETSON_CAMERA_ID=CAM-INSP-01 (또는 원하는 ID)

sudo systemctl start casting-image-publisher
sudo journalctl -u casting-image-publisher -f
```

## proto 재생성 시

`backend/management/proto/management.proto` 변경 후:
```bash
# 1) 서버측 재생성
cd backend/management && make proto
# 2) monitoring 재생성 (relative import 패치 포함)
cd ../../monitoring && bash scripts/gen_proto.sh
# 3) jetson_publisher 로 복사
cp monitoring/app/generated/management_pb2.py        jetson_publisher/generated/
cp monitoring/app/generated/management_pb2_grpc.py   jetson_publisher/generated/
# 4) Jetson 에 재배포
bash jetson_publisher/deploy.sh
```

## 로컬 Mac 테스트 (E2E용 FaceTime/USB 웹캠)

```bash
cd jetson_publisher
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt opencv-python
export MANAGEMENT_GRPC_HOST=127.0.0.1
export JETSON_CAMERA_ID=CAM-INSP-MAC
python3 publisher.py
```

Management Server(:50051) 가 기동 중이어야 하며, `image_sink.stats()` 로 수신 확인 가능.
