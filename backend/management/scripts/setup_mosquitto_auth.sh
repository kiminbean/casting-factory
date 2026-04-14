#!/usr/bin/env bash
# Mosquitto 인증 + 익명 차단 설정 (V6 S-002).
#
# 사용:
#   bash backend/management/scripts/setup_mosquitto_auth.sh
#
# 산출물:
#   backend/management/mosquitto/mosquitto.conf
#   backend/management/mosquitto/passwd  (gitignored)
#
# 환경 변수:
#   MGMT_MQTT_USER  사용자명 (기본 casting)
#   MGMT_MQTT_PASS  비밀번호 (기본 랜덤 16자)
#   MGMT_MQTT_PORT  포트 (기본 1883)
#
# 실행 후 mosquitto 재시작:
#   pkill mosquitto; mosquitto -c backend/management/mosquitto/mosquitto.conf -d
set -euo pipefail

CONF_DIR="$(cd "$(dirname "$0")/.." && pwd)/mosquitto"
USER="${MGMT_MQTT_USER:-casting}"
PASS="${MGMT_MQTT_PASS:-$(openssl rand -base64 12)}"
PORT="${MGMT_MQTT_PORT:-1883}"

mkdir -p "$CONF_DIR"

# passwd 파일 생성 (mosquitto_passwd 사용)
PWFILE="$CONF_DIR/passwd"
if ! command -v mosquitto_passwd >/dev/null 2>&1; then
    echo "❌ mosquitto_passwd 없음. brew install mosquitto"
    exit 1
fi

echo "==> 사용자 등록: $USER"
mosquitto_passwd -c -b "$PWFILE" "$USER" "$PASS"
chmod 600 "$PWFILE"

# 설정 파일
cat > "$CONF_DIR/mosquitto.conf" <<EOF
# Casting Factory Management Service MQTT 브로커 (V6 S-002)
listener $PORT
allow_anonymous false
password_file $PWFILE
persistence false
log_dest stdout
log_type warning
log_type error
EOF

echo ""
echo "==> 설정 완료:"
echo "  config:  $CONF_DIR/mosquitto.conf"
echo "  passwd:  $PWFILE"
echo ""
echo "==> 다음 단계:"
echo "  1) mosquitto 재시작:"
echo "     pkill -f 'mosquitto' 2>/dev/null"
echo "     mosquitto -c $CONF_DIR/mosquitto.conf -d"
echo ""
echo "  2) Management Service 환경변수 설정:"
echo "     export MGMT_MQTT_USER=$USER"
echo "     export MGMT_MQTT_PASS='$PASS'"
echo "     python backend/management/server.py"
echo ""
echo "  3) ESP32 펌웨어에도 같은 user/pass 적용:"
echo "     PubSubClient.connect(client_id, '$USER', '...')"
echo ""
echo "==> 비밀번호 (1회 표시, 분실 시 재발급):"
echo "  $PASS"
