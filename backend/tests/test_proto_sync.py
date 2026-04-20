"""SPEC-C2 §12.2 — proto stub 동기화 검증 (CI 게이트).

backend/management/management_pb2.py 와 jetson_publisher/generated/management_pb2.py 가
동일 descriptor 를 가지는지 확인. Phase D-1 에서 확립된 규약.
"""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_pb2_module(path: Path, alias: str):
    """서로 다른 위치의 management_pb2.py 를 충돌 없이 로드."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(alias, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def test_proto_stubs_synced():
    """management_pb2.py 두 복사본의 descriptor 일치."""
    b_path = ROOT / "backend" / "management" / "management_pb2.py"
    j_path = ROOT / "jetson_publisher" / "generated" / "management_pb2.py"
    assert b_path.exists(), b_path
    assert j_path.exists(), j_path

    b_mod = _load_pb2_module(b_path, "_spec_c2_backend_mgmt_pb2")
    j_mod = _load_pb2_module(j_path, "_spec_c2_jetson_pb2")
    assert b_mod.DESCRIPTOR.serialized_pb == j_mod.DESCRIPTOR.serialized_pb, (
        "proto stubs diverged — run 'make proto' in backend/management + "
        "cp to jetson_publisher/generated/"
    )
