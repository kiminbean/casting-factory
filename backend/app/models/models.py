from datetime import datetime, timezone


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from app.database import Base


class Order(Base):
    """Production order from a customer."""

    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    product_spec = Column(String, nullable=True)
    material = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    unit_price = Column(Integer, nullable=False, default=0)
    total_price = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="pending")
    post_processing = Column(String, nullable=True)
    requested_delivery = Column(String, nullable=True)
    estimated_delivery = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now, nullable=False)
    notes = Column(String, nullable=True)


class ProcessStage(Base):
    """Current status of a production process stage."""

    __tablename__ = "process_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage = Column(String, nullable=False)
    label = Column(String, nullable=False)
    status = Column(String, nullable=False, default="idle")
    temperature = Column(Float, nullable=True)
    target_temperature = Column(Float, nullable=True)
    progress = Column(Integer, nullable=False, default=0)
    equipment_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    job_id = Column(String, nullable=True)


class Equipment(Base):
    """Factory equipment including furnaces, robots, AMRs, and cameras."""

    __tablename__ = "equipment"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="idle")
    zone = Column(String, nullable=True)
    last_maintenance = Column(String, nullable=True)
    operating_hours = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)


class TransportRequest(Base):
    """AMR transport request between factory zones."""

    __tablename__ = "transport_requests"

    id = Column(String, primary_key=True, index=True)
    from_zone = Column(String, nullable=False)
    to_zone = Column(String, nullable=False)
    item_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="requested")
    assigned_amr_id = Column(String, nullable=True)
    requested_at = Column(DateTime, default=_utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String, nullable=True)


class InspectionRecord(Base):
    """AI vision inspection result for a casting."""

    __tablename__ = "inspection_records"

    id = Column(String, primary_key=True, index=True)
    casting_id = Column(String, nullable=False)
    order_id = Column(String, nullable=True)
    result = Column(String, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    image_id = Column(String, nullable=True)
    inspected_at = Column(DateTime, default=_utc_now, nullable=False)
    defect_type = Column(String, nullable=True)


class Alert(Base):
    """System alert or notification."""

    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="info")
    message = Column(String, nullable=False)
    zone = Column(String, nullable=True)
    timestamp = Column(DateTime, default=_utc_now, nullable=False)
    acknowledged = Column(Boolean, nullable=False, default=False)


class ProductionMetric(Base):
    """Daily production summary metric."""

    __tablename__ = "production_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False, index=True)
    production = Column(Integer, nullable=False, default=0)
    defects = Column(Integer, nullable=False, default=0)
    defect_rate = Column(Float, nullable=False, default=0.0)
