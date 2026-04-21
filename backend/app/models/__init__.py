"""smartcast schema 모델 export.

Confluence page 32342045 v59 (2026-04-18) 기준 27 테이블 + equip_load_spec.
Legacy 모델은 backend/app/models/models_legacy.py 에 보관.

SPEC-C3 (2026-04-20): Alert/HandoffAck/TransportTask 는 smartcast 스키마에 없으나
public 스키마의 legacy 테이블이 여전히 사용 중이므로 re-export. Management 의
execution_monitor + ReportHandoffAck 가 정상 기동하도록 허용.
"""
from app.models.models import (
    SCHEMA,
    Category,
    ChgLocationStat,
    Equip,
    EquipErrLog,
    EquipLoadSpec,
    EquipStat,
    EquipTaskTxn,
    InspTaskTxn,
    Item,
    Ord,
    OrdDetail,
    OrdLog,
    OrdPpMap,
    OrdStat,
    OrdTxn,
    Pattern,
    PpOption,
    PpTaskTxn,
    Product,
    ProductOption,
    Res,
    ShipLocationStat,
    StrgLocationStat,
    Trans,
    TransErrLog,
    TransStat,
    TransTaskTxn,
    UserAccount,
    Zone,
)

# SPEC-C3: Management 전용 public-schema 테이블 (3개만 선별)
# models_legacy.py 전체 import 시 legacy Item/Order 가 smartcast 와 Base.metadata 충돌.
from app.models.models_mgmt import (
    Alert,
    HandoffAck,
    RfidScanLog,
    TransportTask,
)

__all__ = [
    "SCHEMA",
    "Category",
    "ChgLocationStat",
    "Equip",
    "EquipErrLog",
    "EquipLoadSpec",
    "EquipStat",
    "EquipTaskTxn",
    "InspTaskTxn",
    "Item",
    "Ord",
    "OrdDetail",
    "OrdLog",
    "OrdPpMap",
    "OrdStat",
    "OrdTxn",
    "Pattern",
    "PpOption",
    "PpTaskTxn",
    "Product",
    "ProductOption",
    "Res",
    "ShipLocationStat",
    "StrgLocationStat",
    "Trans",
    "TransErrLog",
    "TransStat",
    "TransTaskTxn",
    "UserAccount",
    "Zone",
    # SPEC-C3 legacy re-exports
    "Alert",
    "HandoffAck",
    "RfidScanLog",
    "TransportTask",
]
