import json
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from app.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ────────────────────────────────────────
# 1. 주문 관리 (Order Management)
# ────────────────────────────────────────

class Order(Base):
    """주문 정보 — types.ts Order 대응"""

    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    contact = Column(String, nullable=True, default="")
    shipping_address = Column(String, nullable=True, default="")
    total_amount = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="pending")
    requested_delivery = Column(String, nullable=True)
    confirmed_delivery = Column(String, nullable=True, default="")
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    notes = Column(String, nullable=True, default="")


class OrderDetail(Base):
    """주문 상세 품목 — types.ts OrderDetail 대응"""

    __tablename__ = "order_details"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    spec = Column(String, nullable=True, default="")
    material = Column(String, nullable=True, default="")
    post_processing = Column(String, nullable=True, default="")
    logo_data = Column(String, nullable=True, default="")
    unit_price = Column(Integer, nullable=False, default=0)
    subtotal = Column(Integer, nullable=False, default=0)


class Product(Base):
    """제품 마스터 — types.ts Product 대응"""

    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    base_price = Column(Integer, nullable=False, default=0)
    option_pricing_json = Column(Text, nullable=True, default="{}")
    design_image_url = Column(String, nullable=True, default="")
    model_3d_path = Column(String, nullable=True, default="")


# ────────────────────────────────────────
# 2. 생산 모니터링 (Production Monitoring)
# ────────────────────────────────────────

class ProcessStage(Base):
    """공정 단계 상태 — types.ts ProcessStageData 대응"""

    __tablename__ = "process_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage = Column(String, nullable=False)
    label = Column(String, nullable=False)
    status = Column(String, nullable=False, default="idle")
    temperature = Column(Float, nullable=True)
    target_temperature = Column(Float, nullable=True)
    progress = Column(Integer, nullable=False, default=0)
    start_time = Column(String, nullable=True)
    estimated_end = Column(String, nullable=True)
    equipment_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    job_id = Column(String, nullable=True)
    # 공정별 상세 데이터
    pressure = Column(Float, nullable=True)
    pour_angle = Column(Float, nullable=True)
    heating_power = Column(Float, nullable=True)
    cooling_progress = Column(Float, nullable=True)


# ────────────────────────────────────────
# 3. 통합 대시보드 (Equipment & Alerts)
# ────────────────────────────────────────

class Equipment(Base):
    """설비 정보 — types.ts Equipment 대응"""

    __tablename__ = "equipment"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    comm_id = Column(String, nullable=True, default="")
    install_location = Column(String, nullable=True, default="")
    status = Column(String, nullable=False, default="idle")
    pos_x = Column(Float, nullable=False, default=0.0)
    pos_y = Column(Float, nullable=False, default=0.0)
    pos_z = Column(Float, nullable=False, default=0.0)
    battery = Column(Integer, nullable=True)
    speed = Column(Float, nullable=True)
    last_update = Column(String, nullable=True)
    last_maintenance = Column(String, nullable=True)
    operating_hours = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)


class Alert(Base):
    """알림 — types.ts Alert 대응"""

    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    equipment_id = Column(String, nullable=True, default="")
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="info")
    error_code = Column(String, nullable=True, default="")
    message = Column(String, nullable=False)
    abnormal_value = Column(String, nullable=True, default="")
    zone = Column(String, nullable=True)
    timestamp = Column(String, nullable=False)
    resolved_at = Column(String, nullable=True)
    acknowledged = Column(Boolean, nullable=False, default=False)


# ────────────────────────────────────────
# 4. 품질 검사 (Quality Control)
# ────────────────────────────────────────

class InspectionRecord(Base):
    """검사 기록 — types.ts InspectionRecord 대응"""

    __tablename__ = "inspection_records"

    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, nullable=True, default="")
    casting_id = Column(String, nullable=False)
    order_id = Column(String, nullable=True)
    result = Column(String, nullable=False)
    defect_type_code = Column(String, nullable=True, default="")
    confidence = Column(Float, nullable=False, default=0.0)
    inspector_id = Column(String, nullable=True, default="")
    image_id = Column(String, nullable=True)
    inspected_at = Column(String, nullable=False)
    defect_type = Column(String, nullable=True)
    defect_detail = Column(String, nullable=True)


class InspectionStandard(Base):
    """검사 기준 — types.ts InspectionStandard 대응"""

    __tablename__ = "inspection_standards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    tolerance_range = Column(String, nullable=False)
    target_dimension = Column(String, nullable=False)
    threshold = Column(Float, nullable=False, default=95.0)


class SorterLog(Base):
    """분류기 로그 — types.ts SorterLog 대응"""

    __tablename__ = "sorter_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String, nullable=False)
    sort_direction = Column(String, nullable=False)
    sorter_angle = Column(Float, nullable=False, default=0.0)
    success = Column(Boolean, nullable=False, default=True)


# ────────────────────────────────────────
# 5. 물류 및 이송 (Logistics & Fleet)
# ────────────────────────────────────────

class TransportTask(Base):
    """이송 작업 — types.ts TransportTask 대응 (기존 TransportRequest 대체)"""

    __tablename__ = "transport_tasks"

    id = Column(String, primary_key=True, index=True)
    from_name = Column(String, nullable=False)
    from_coord = Column(String, nullable=True, default="")
    to_name = Column(String, nullable=False)
    to_coord = Column(String, nullable=True, default="")
    item_id = Column(String, nullable=True, default="")
    item_name = Column(String, nullable=True, default="")
    quantity = Column(Integer, nullable=False, default=1)
    priority = Column(String, nullable=False, default="medium")
    status = Column(String, nullable=False, default="unassigned")
    assigned_robot_id = Column(String, nullable=True, default="")
    requested_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)


class WarehouseRack(Base):
    """창고 랙 — types.ts WarehouseRack 대응"""

    __tablename__ = "warehouse_racks"

    id = Column(String, primary_key=True, index=True)
    zone = Column(String, nullable=False)
    rack_number = Column(String, nullable=False)
    status = Column(String, nullable=False, default="empty")
    item_id = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    last_inbound_at = Column(String, nullable=True)
    row = Column(Integer, nullable=False)
    col = Column(Integer, nullable=False)


class OutboundOrder(Base):
    """출고 주문 — types.ts OutboundOrder 대응"""

    __tablename__ = "outbound_orders"

    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    destination = Column(String, nullable=False)
    policy = Column(String, nullable=False, default="FIFO")
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(String, nullable=False)


# ────────────────────────────────────────
# 차트/통계 (Charts / Statistics)
# ────────────────────────────────────────

class ProductionMetric(Base):
    """일별 생산 통계 — types.ts ProductionMetric 대응"""

    __tablename__ = "production_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False, index=True)
    production = Column(Integer, nullable=False, default=0)
    defects = Column(Integer, nullable=False, default=0)
    defect_rate = Column(Float, nullable=False, default=0.0)


# ────────────────────────────────────────
# 7. 생산 스케줄링 (Production Scheduling)
# ────────────────────────────────────────

class ProductionJob(Base):
    """생산 작업 — 주문을 공정에 할당한 작업 단위"""

    __tablename__ = "production_jobs"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False, index=True)
    priority_score = Column(Float, nullable=False, default=0.0)
    priority_rank = Column(Integer, nullable=False, default=0)
    assigned_stage = Column(String, nullable=False, default="melting")
    status = Column(String, nullable=False, default="queued")  # queued/running/completed/cancelled
    estimated_completion = Column(String, nullable=True)
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    created_at = Column(String, nullable=False)


class PriorityChangeLog(Base):
    """우선순위 변경 이력 — 수동 순서 변경 감사 추적"""

    __tablename__ = "priority_change_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False, index=True)
    old_rank = Column(Integer, nullable=False)
    new_rank = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    changed_by = Column(String, nullable=False, default="admin")
    changed_at = Column(String, nullable=False)
