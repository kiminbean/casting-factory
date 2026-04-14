"""pytest 공통 conftest — backend/management/ 모듈 import 가능하게 sys.path 보강."""
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_MGMT_DIR = os.path.dirname(_THIS_DIR)
_BACKEND_DIR = os.path.dirname(_MGMT_DIR)

for p in (_MGMT_DIR, _BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)
