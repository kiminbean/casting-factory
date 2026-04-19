"""SQLAlchemy ORM 모델 — schema 'smartcast' (Confluence page 32342045 v59 기준).

설계 참조:
- https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32342045
- 27 테이블 (이다예 owner, 2026-04-18 v59)
- 책임 분리 패턴: master + transaction (txn) + state (stat) + log

주요 변경점 (legacy → v2):
- orders        → ord  (master) + ord_detail (1:1)
- products      → product
- items         → item
- equipment     → res (마스터) + equip (생산 설비) + trans (이송 설비)
- transport_tasks → trans_task_txn + trans_stat + trans_err_log
- inspection_records → insp_task_txn

@MX:ANCHOR: smartcast schema 모델 — 외부 API 계약의 출처. 추가/제거 시 acceptance.md 동기 필요.
@MX:REASON: ord/item/res 분리 구조는 설계 회의(Confluence 32342045 v59 + 인라인 코멘트 8건)에서 결정됨.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

# 모든 신규 테이블이 사용할 schema
SCHEMA = "smartcast"


# =====================
# USER
# =====================

class UserAccount(Base):
    """사용자 정보 (customer/admin/operator/fms)."""
    __tablename__ = "user_account"
    __table_args__ = (
        CheckConstraint("role IN ('customer', 'admin', 'operator', 'fms')", name="chk_user_role"),
        {"schema": SCHEMA},
    )

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    co_nm = Column(String, nullable=False)
    user_nm = Column(String, nullable=False)
    role = Column(String)
    phone = Column(String)
    email = Column(String, nullable=False, unique=True)
    password = Column(String)


# =====================
# ORDER
# =====================

class Ord(Base):
    """발주 마스터 (1:1 ord_detail)."""
    __tablename__ = "ord"
    __table_args__ = ({"schema": SCHEMA},)

    ord_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.user_account.user_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("UserAccount")
    detail = relationship("OrdDetail", uselist=False, back_populates="ord", cascade="all, delete-orphan")
    pp_maps = relationship("OrdPpMap", back_populates="ord", cascade="all, delete-orphan")
    txns = relationship("OrdTxn", back_populates="ord", cascade="all, delete-orphan")
    stats = relationship("OrdStat", back_populates="ord", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="ord", cascade="all, delete-orphan")


class OrdDetail(Base):
    """발주 상세 (1:1 with ord)."""
    __tablename__ = "ord_detail"
    __table_args__ = ({"schema": SCHEMA},)

    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), primary_key=True)
    prod_id = Column(Integer, ForeignKey(f"{SCHEMA}.product.prod_id"))
    diameter = Column(Numeric)
    thickness = Column(Numeric)
    material = Column(String(30))
    load_class = Column(String(20))
    qty = Column(Integer)
    final_price = Column(Numeric)
    due_date = Column(Date)
    ship_addr = Column(String)

    ord = relationship("Ord", back_populates="detail")
    product = relationship("Product")


class OrdPpMap(Base):
    """발주↔후처리 N:M 매핑."""
    __tablename__ = "ord_pp_map"
    __table_args__ = ({"schema": SCHEMA},)

    map_id = Column(Integer, primary_key=True, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), nullable=False)
    pp_id = Column(Integer, ForeignKey(f"{SCHEMA}.pp_options.pp_id"), nullable=False)

    ord = relationship("Ord", back_populates="pp_maps")
    pp_option = relationship("PpOption")


class OrdTxn(Base):
    """발주 비즈니스 트랜잭션 (RCVD/APPR/CNCL/REJT)."""
    __tablename__ = "ord_txn"
    __table_args__ = (
        CheckConstraint("txn_type IN ('RCVD', 'APPR', 'CNCL', 'REJT')", name="chk_ord_txn_type"),
        {"schema": SCHEMA},
    )

    txn_id = Column(Integer, primary_key=True, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), nullable=False)
    txn_type = Column(String, server_default="RCVD")
    txn_at = Column(DateTime, server_default=func.now())

    ord = relationship("Ord", back_populates="txns")


class OrdStat(Base):
    """발주 상태 (RCVD→APPR→MFG→DONE→SHIP→COMP, 또는 REJT/CNCL)."""
    __tablename__ = "ord_stat"
    __table_args__ = (
        CheckConstraint(
            "ord_stat IN ('RCVD','APPR','MFG','DONE','SHIP','COMP','REJT','CNCL')",
            name="chk_ord_stat_value",
        ),
        {"schema": SCHEMA},
    )

    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), nullable=False)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.user_account.user_id"))
    ord_stat = Column(String)
    updated_at = Column(DateTime, server_default=func.now())

    ord = relationship("Ord", back_populates="stats")
    user = relationship("UserAccount")


class OrdLog(Base):
    """발주 상태 전이 로그."""
    __tablename__ = "ord_log"
    __table_args__ = ({"schema": SCHEMA},)

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), nullable=False)
    prev_stat = Column(String)
    new_stat = Column(String)
    changed_by = Column(Integer, ForeignKey(f"{SCHEMA}.user_account.user_id"))
    logged_at = Column(DateTime, server_default=func.now())


# =====================
# 표준 제품 마스터
# =====================

class Category(Base):
    """제품 카테고리 (CMH/RMH/EMH)."""
    __tablename__ = "category"
    __table_args__ = (
        CheckConstraint("cate_cd IN ('CMH', 'RMH', 'EMH')", name="chk_cate_cd"),
        {"schema": SCHEMA},
    )

    cate_cd = Column(String, primary_key=True)
    cate_nm = Column(String, nullable=False, unique=True)


class Product(Base):
    """표준 주조 제품."""
    __tablename__ = "product"
    __table_args__ = ({"schema": SCHEMA},)

    prod_id = Column(Integer, primary_key=True, autoincrement=True)
    cate_cd = Column(String, ForeignKey(f"{SCHEMA}.category.cate_cd"), nullable=False)
    base_price = Column(Numeric, nullable=False)
    img_url = Column(String(400))

    category = relationship("Category")
    options = relationship("ProductOption", back_populates="product", cascade="all, delete-orphan")


class ProductOption(Base):
    """제품별 옵션 (재질/하중등급)."""
    __tablename__ = "product_option"
    __table_args__ = ({"schema": SCHEMA},)

    prod_opt_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_id = Column(Integer, ForeignKey(f"{SCHEMA}.product.prod_id"))
    mat_type = Column(String(20))
    load_class = Column(String(20))

    product = relationship("Product", back_populates="options")


class PpOption(Base):
    """후처리 옵션 마스터."""
    __tablename__ = "pp_options"
    __table_args__ = ({"schema": SCHEMA},)

    pp_id = Column(Integer, primary_key=True, autoincrement=True)
    pp_nm = Column(String, unique=True)
    extra_cost = Column(Numeric)


# =====================
# OPERATOR (zone, pattern)
# =====================

class Zone(Base):
    """공정 6구역 (CAST/PP/INSP/STRG/SHIP/CHG)."""
    __tablename__ = "zone"
    __table_args__ = (
        CheckConstraint(
            "zone_nm IN ('CAST', 'PP', 'INSP', 'STRG', 'SHIP', 'CHG')",
            name="chk_zone_nm",
        ),
        {"schema": SCHEMA},
    )

    zone_id = Column(Integer, primary_key=True, autoincrement=True)
    zone_nm = Column(String, unique=True)


class Pattern(Base):
    """패턴 위치 (1-6번, 발주 1:1)."""
    __tablename__ = "pattern"
    __table_args__ = (
        CheckConstraint("ptn_loc BETWEEN 1 AND 6", name="chk_ptn_loc_range"),
        {"schema": SCHEMA},
    )

    ptn_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), primary_key=True)
    ptn_loc = Column(Integer)


# =====================
# 설비 마스터 (res, equip, trans)
# =====================

class Res(Base):
    """전체 설비 마스터 (RA/CONV/AMR)."""
    __tablename__ = "res"
    __table_args__ = (
        CheckConstraint("res_type IN ('RA', 'CONV', 'AMR')", name="chk_res_type"),
        {"schema": SCHEMA},
    )

    res_id = Column(String(10), primary_key=True)
    res_type = Column(String)
    model_nm = Column(String, nullable=False)


class Equip(Base):
    """생산 설비 (RA, CONV) — zone에 배치."""
    __tablename__ = "equip"
    __table_args__ = ({"schema": SCHEMA},)

    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"), primary_key=True)
    zone_id = Column(Integer, ForeignKey(f"{SCHEMA}.zone.zone_id"))

    res = relationship("Res")
    zone = relationship("Zone")


class EquipLoadSpec(Base):
    """하중 등급별 정밀 제어 수치."""
    __tablename__ = "equip_load_spec"
    __table_args__ = ({"schema": SCHEMA},)

    load_spec_id = Column(Integer, primary_key=True, autoincrement=True)
    load_class = Column(String(20))
    press_f = Column(Numeric(10, 2))
    press_t = Column(Numeric(5, 2))
    tol_val = Column(Numeric(5, 2))


class Trans(Base):
    """이송 자원 (AMR)."""
    __tablename__ = "trans"
    __table_args__ = ({"schema": SCHEMA},)

    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"), primary_key=True)
    slot_count = Column(Integer)
    max_load_kg = Column(Numeric)

    res = relationship("Res")


# =====================
# FMS — Item (재고/공정 stat)
# =====================

class Item(Base):
    """생산된 모든 아이템의 실시간 공정 단계 + 불량 여부.

    cur_stat: 12개 라벨 (MM/POUR/DM/PP/ToINSP/INSP/PA/PICK/SHIP/ToPP/ToSTRG/ToSHIP)
    cur_res: 점유 자원 ID (PP 상태 시 NULL)
    is_defective: NULL=미검사, TRUE=불량, FALSE=양품
    """
    __tablename__ = "item"
    __table_args__ = ({"schema": SCHEMA},)

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), nullable=False)
    equip_task_type = Column(String(10))
    trans_task_type = Column(String(10))
    cur_stat = Column(String(10))
    cur_res = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"))
    is_defective = Column(Boolean)
    updated_at = Column(DateTime, server_default=func.now())

    ord = relationship("Ord", back_populates="items")
    res = relationship("Res")


# =====================
# Location State (chg/strg/ship)
# =====================

class ChgLocationStat(Base):
    """충전 구역 (1x3) 위치 상태."""
    __tablename__ = "chg_location_stat"
    __table_args__ = (
        CheckConstraint(
            "status IN ('empty', 'occupied', 'reserved')",
            name="chk_chg_loc_status",
        ),
        {"schema": SCHEMA},
    )

    loc_id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(Integer, ForeignKey(f"{SCHEMA}.zone.zone_id"))
    res_id = Column(String, ForeignKey(f"{SCHEMA}.res.res_id"))
    loc_row = Column(Integer)
    loc_col = Column(Integer)
    status = Column(String)
    stored_at = Column(DateTime, server_default=func.now())


class StrgLocationStat(Base):
    """적재 구역 (3x6, 18칸) 위치 상태."""
    __tablename__ = "strg_location_stat"
    __table_args__ = (
        CheckConstraint(
            "status IN ('empty', 'occupied', 'reserved')",
            name="chk_strg_loc_status",
        ),
        CheckConstraint(
            "(item_id IS NOT NULL AND status = 'occupied') "
            "OR (item_id IS NULL AND status IN ('empty', 'reserved'))",
            name="chk_strg_item_status",
        ),
        {"schema": SCHEMA},
    )

    loc_id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(Integer, ForeignKey(f"{SCHEMA}.zone.zone_id"))
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    loc_row = Column(Integer)
    loc_col = Column(Integer)
    status = Column(String)
    stored_at = Column(DateTime, server_default=func.now())


class ShipLocationStat(Base):
    """출고 구역 (1x5) 위치 상태."""
    __tablename__ = "ship_location_stat"
    __table_args__ = (
        CheckConstraint(
            "status IN ('empty', 'occupied', 'reserved')",
            name="chk_ship_loc_status",
        ),
        {"schema": SCHEMA},
    )

    loc_id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(Integer, ForeignKey(f"{SCHEMA}.zone.zone_id"))
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"))
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    loc_row = Column(Integer)
    loc_col = Column(Integer)
    status = Column(String)
    stored_at = Column(DateTime, server_default=func.now())


# =====================
# OPERATOR — pp_task_txn
# =====================

class PpTaskTxn(Base):
    """후처리 작업 트랜잭션."""
    __tablename__ = "pp_task_txn"
    __table_args__ = (
        CheckConstraint("txn_stat IN ('QUE', 'PROC', 'SUCC', 'FAIL')", name="chk_pp_txn_stat"),
        {"schema": SCHEMA},
    )

    txn_id = Column(Integer, primary_key=True, autoincrement=True)
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"), nullable=False)
    map_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord_pp_map.map_id"))
    pp_nm = Column(String)
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    operator_id = Column(Integer, ForeignKey(f"{SCHEMA}.user_account.user_id"))
    txn_stat = Column(String)
    req_at = Column(DateTime, server_default=func.now())
    start_at = Column(DateTime)
    end_at = Column(DateTime)


# =====================
# 생산 설비 (equip_task_txn / equip_stat / equip_err_log)
# =====================

class EquipTaskTxn(Base):
    """생산 설비 작업지시 트랜잭션 (RA/CONV)."""
    __tablename__ = "equip_task_txn"
    __table_args__ = (
        CheckConstraint("txn_stat IN ('QUE', 'PROC', 'SUCC', 'FAIL')", name="chk_equip_txn_stat"),
        {"schema": SCHEMA},
    )

    txn_id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"))
    task_type = Column(String)
    txn_stat = Column(String)
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    strg_loc_id = Column(Integer, ForeignKey(f"{SCHEMA}.strg_location_stat.loc_id"))
    ship_loc_id = Column(Integer, ForeignKey(f"{SCHEMA}.ship_location_stat.loc_id"))
    req_at = Column(DateTime, server_default=func.now())
    start_at = Column(DateTime)
    end_at = Column(DateTime)


class EquipStat(Base):
    """생산 설비 실시간 상태."""
    __tablename__ = "equip_stat"
    __table_args__ = ({"schema": SCHEMA},)

    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"), nullable=False)
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    txn_type = Column(String)
    cur_stat = Column(String)
    updated_at = Column(DateTime, server_default=func.now())
    err_msg = Column(String)


class EquipErrLog(Base):
    """생산 설비 에러 로그."""
    __tablename__ = "equip_err_log"
    __table_args__ = ({"schema": SCHEMA},)

    err_id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"))
    task_txn_id = Column(Integer, ForeignKey(f"{SCHEMA}.equip_task_txn.txn_id"))
    failed_stat = Column(String)
    err_msg = Column(String)
    occured_at = Column(DateTime, server_default=func.now())


# =====================
# 이동 설비 (trans_task_txn / trans_stat / trans_err_log)
# =====================

class TransTaskTxn(Base):
    """AMR 이송 작업 트랜잭션."""
    __tablename__ = "trans_task_txn"
    __table_args__ = (
        CheckConstraint("txn_stat IN ('QUE', 'PROC', 'SUCC', 'FAIL')", name="chk_trans_txn_stat"),
        {"schema": SCHEMA},
    )

    trans_task_txn_id = Column(Integer, primary_key=True, autoincrement=True)
    trans_id = Column(String, ForeignKey(f"{SCHEMA}.trans.res_id"))
    task_type = Column(String)
    txn_stat = Column(String)
    chg_loc_id = Column(Integer, ForeignKey(f"{SCHEMA}.chg_location_stat.loc_id"))
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    ord_id = Column(Integer, ForeignKey(f"{SCHEMA}.ord.ord_id"))
    req_at = Column(DateTime, server_default=func.now())
    start_at = Column(DateTime)
    end_at = Column(DateTime)


class TransStat(Base):
    """AMR 실시간 상태 (배터리 포함)."""
    __tablename__ = "trans_stat"
    __table_args__ = ({"schema": SCHEMA},)

    res_id = Column(String, ForeignKey(f"{SCHEMA}.trans.res_id"), primary_key=True)
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    cur_stat = Column(String)
    battery_pct = Column(Integer)
    cur_zone_type = Column(String)
    updated_at = Column(DateTime, server_default=func.now())


class TransErrLog(Base):
    """AMR 에러 로그 (배터리 포함)."""
    __tablename__ = "trans_err_log"
    __table_args__ = ({"schema": SCHEMA},)

    err_id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"))
    task_txn_id = Column(Integer, ForeignKey(f"{SCHEMA}.trans_task_txn.trans_task_txn_id"))
    failed_stat = Column(String)
    err_msg = Column(String)
    battery_pct = Column(Integer)
    occured_at = Column(DateTime, server_default=func.now())


# =====================
# 품질 검사 (insp_task_txn)
# =====================

class InspTaskTxn(Base):
    """품질 검사 작업 트랜잭션 (CONV1 + AI)."""
    __tablename__ = "insp_task_txn"
    __table_args__ = (
        CheckConstraint("txn_stat IN ('QUE', 'PROC', 'SUCC', 'FAIL')", name="chk_insp_txn_stat"),
        {"schema": SCHEMA},
    )

    txn_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey(f"{SCHEMA}.item.item_id"))
    res_id = Column(String(10), ForeignKey(f"{SCHEMA}.res.res_id"))
    txn_stat = Column(String)
    result = Column(Boolean)  # NULL=미검사, FALSE=DP, TRUE=GP
    req_at = Column(DateTime, server_default=func.now())
    start_at = Column(DateTime)
    end_at = Column(DateTime)
