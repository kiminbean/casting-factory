#!/usr/bin/env bash
# monitoring/ 에서 Management Service proto 컴파일.
# proto 변경 시: bash scripts/gen_proto.sh
set -euo pipefail

cd "$(dirname "$0")/.."

python -m grpc_tools.protoc \
  -I ../backend/management/proto \
  --python_out=app/generated \
  --grpc_python_out=app/generated \
  ../backend/management/proto/management.proto

# protoc 가 만든 generated/management_pb2_grpc.py 의 top-level import 를
# 패키지 상대 import 로 패치 (Python 패키지 안에서 동작하도록).
GRPC_FILE="app/generated/management_pb2_grpc.py"
if grep -q "^import management_pb2 as management__pb2" "$GRPC_FILE"; then
    sed -i.bak 's/^import management_pb2 as management__pb2/from . import management_pb2 as management__pb2/' "$GRPC_FILE"
    rm -f "${GRPC_FILE}.bak"
fi

echo "✓ proto 컴파일 완료: app/generated/"
