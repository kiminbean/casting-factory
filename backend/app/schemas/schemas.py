"""Pydantic v2 스키마 — smartcast schema (Confluence 32342045 v59 기준).

신규 27 테이블에 대응하는 Request/Response 모델.
Legacy 모델은 backend/app/schemas/schemas_legacy.py 에 보관.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =====================
# Common
# =====================

class _ORM(BaseModel):
    """ORM mode 베이스. protected_namespaces=() 로 `model_nm` 필드 경고 무시."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# =====================
# USER
# =====================

class UserAccountBase(BaseModel):
    co_nm: str
    user_nm: str
    role: Optional[str] = None
    phone: Optional[str] = None
    email: str  # EmailStr 는 외부 dep 부담, str 로 가볍게


class UserAccountCreate(UserAccountBase):
    password: Optional[str] = None


class UserAccountOut(_ORM, UserAccountBase):
    user_id: int


# =====================
# CATEGORY / PRODUCT
# =====================

class CategoryOut(_ORM):
    cate_cd: str
    cate_nm: str


class ProductOut(_ORM):
    prod_id: int
    cate_cd: str
    base_price: Decimal
    img_url: Optional[str] = None


class ProductOptionOut(_ORM):
    prod_opt_id: int
    prod_id: int
    mat_type: Optional[str] = None
    load_class: Optional[str] = None


class PpOptionOut(_ORM):
    pp_id: int
    pp_nm: Optional[str] = None
    extra_cost: Optional[Decimal] = None


# =====================
# ORDER
# =====================

class OrdDetailIn(BaseModel):
    prod_id: Optional[int] = None
    diameter: Optional[Decimal] = None
    thickness: Optional[Decimal] = None
    material: Optional[str] = None
    load_class: Optional[str] = None
    qty: Optional[int] = None
    final_price: Optional[Decimal] = None
    due_date: Optional[date] = None
    ship_addr: Optional[str] = None


class OrdDetailOut(_ORM, OrdDetailIn):
    ord_id: int


class OrdCreate(BaseModel):
    """발주 생성 — 고객 측 발주 폼 (비고란 없음, 핑크 GUI #2)."""
    user_id: int
    detail: OrdDetailIn
    pp_ids: List[int] = Field(default_factory=list)


class OrdOut(_ORM):
    ord_id: int
    user_id: int
    created_at: Optional[datetime] = None


class OrdFull(OrdOut):
    """발주 + 상세 + 후처리 + 최신 상태 — 고객 조회용.

    user_* 필드는 user_account 에서 denormalize. Next.js/PyQt 가 발주 카드에
    회사명/담당자/연락처/이메일/주소를 바로 표시할 수 있게 한다.
    """
    detail: Optional[OrdDetailOut] = None
    pp_options: List[PpOptionOut] = Field(default_factory=list)
    latest_stat: Optional[str] = None

    # user_account denormalize (고객 조회·관리자 리스트에서 즉시 표시용)
    user_co_nm: Optional[str] = None
    user_nm: Optional[str] = None
    user_phone: Optional[str] = None
    user_email: Optional[str] = None


class OrdStatOut(_ORM):
    stat_id: int
    ord_id: int
    user_id: Optional[int] = None
    ord_stat: Optional[str] = None
    updated_at: Optional[datetime] = None


class OrdTxnOut(_ORM):
    txn_id: int
    ord_id: int
    txn_type: Optional[str] = None
    txn_at: Optional[datetime] = None


# =====================
# ZONE / RES / EQUIP / TRANS
# =====================

class ZoneOut(_ORM):
    zone_id: int
    zone_nm: Optional[str] = None


class ResOut(_ORM):
    res_id: str
    res_type: Optional[str] = None
    model_nm: str


class EquipOut(_ORM):
    res_id: str
    zone_id: Optional[int] = None


class TransOut(_ORM):
    res_id: str
    slot_count: Optional[int] = None
    max_load_kg: Optional[Decimal] = None


# =====================
# PATTERN (핑크 GUI #3)
# =====================

class PatternIn(BaseModel):
    """패턴 등록 — 발주 1:1, 위치 1-6."""
    ptn_id: int  # = ord_id
    ptn_loc: int = Field(ge=1, le=6)


class PatternOut(_ORM):
    ptn_id: int
    ptn_loc: int


# =====================
# ITEM
# =====================

class ItemOut(_ORM):
    item_id: int
    ord_id: int
    equip_task_type: Optional[str] = None
    trans_task_type: Optional[str] = None
    cur_stat: Optional[str] = None
    cur_res: Optional[str] = None
    is_defective: Optional[bool] = None
    updated_at: Optional[datetime] = None


# =====================
# TASK / STAT — equip / trans / pp / insp
# =====================

class EquipTaskTxnOut(_ORM):
    txn_id: int
    res_id: Optional[str] = None
    task_type: Optional[str] = None
    txn_stat: Optional[str] = None
    item_id: Optional[int] = None
    strg_loc_id: Optional[int] = None
    ship_loc_id: Optional[int] = None
    req_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class EquipStatOut(_ORM):
    stat_id: int
    res_id: str
    item_id: Optional[int] = None
    txn_type: Optional[str] = None
    cur_stat: Optional[str] = None
    updated_at: Optional[datetime] = None
    err_msg: Optional[str] = None


class TransTaskTxnOut(_ORM):
    trans_task_txn_id: int
    trans_id: Optional[str] = None
    task_type: Optional[str] = None
    txn_stat: Optional[str] = None
    chg_loc_id: Optional[int] = None
    item_id: Optional[int] = None
    ord_id: Optional[int] = None
    req_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class TransStatOut(_ORM):
    res_id: str
    item_id: Optional[int] = None
    cur_stat: Optional[str] = None
    battery_pct: Optional[int] = None
    cur_zone_type: Optional[str] = None
    updated_at: Optional[datetime] = None


class PpTaskTxnOut(_ORM):
    txn_id: int
    ord_id: int
    map_id: Optional[int] = None
    pp_nm: Optional[str] = None
    item_id: Optional[int] = None
    operator_id: Optional[int] = None
    txn_stat: Optional[str] = None
    req_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class InspTaskTxnOut(_ORM):
    txn_id: int
    item_id: Optional[int] = None
    res_id: Optional[str] = None
    txn_stat: Optional[str] = None
    result: Optional[bool] = None
    req_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


# =====================
# 핑크 GUI #6 — Inspection summary per ord
# =====================

class InspectionSummary(BaseModel):
    """발주별 검사 요약 — 핑크 GUI #6 (PyQt 양품/불량 페이지)."""
    ord_id: int
    total_items: int
    inspected: int
    good_count: int       # GP
    defective_count: int  # DP
    pending_count: int    # 미검사


# =====================
# 핑크 GUI #4 — PP requirements per item
# =====================

class ItemPpRequirements(BaseModel):
    """item별 필요 후처리 목록 — 핑크 GUI #4."""
    item_id: int
    ord_id: int
    pp_options: List[PpOptionOut] = Field(default_factory=list)
    pp_task_status: List[PpTaskTxnOut] = Field(default_factory=list)


# =====================
# 핑크 GUI #5 — 생산 시작 요청
# =====================

class ProductionStartRequest(BaseModel):
    """발주 생산 시작 — 패턴 등록 후에만 호출 가능."""
    ord_id: int
