from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Order schemas
# ---------------------------------------------------------------------------

class OrderCreate(BaseModel):
    id: str
    customer_name: str
    company_name: str
    product_name: str
    product_spec: Optional[str] = None
    material: Optional[str] = None
    quantity: int = 0
    unit_price: int = 0
    total_price: int = 0
    status: str = "pending"
    post_processing: Optional[str] = None
    requested_delivery: Optional[str] = None
    estimated_delivery: Optional[str] = None
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_name: str
    company_name: str
    product_name: str
    product_spec: Optional[str] = None
    material: Optional[str] = None
    quantity: int
    unit_price: int
    total_price: int
    status: str
    post_processing: Optional[str] = None
    requested_delivery: Optional[str] = None
    estimated_delivery: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# ProcessStage schemas
# ---------------------------------------------------------------------------

class ProcessStageCreate(BaseModel):
    stage: str
    label: str
    status: str = "idle"
    temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    progress: int = 0
    equipment_id: Optional[str] = None
    order_id: Optional[str] = None
    job_id: Optional[str] = None


class ProcessStageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stage: str
    label: str
    status: str
    temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    progress: int
    equipment_id: Optional[str] = None
    order_id: Optional[str] = None
    job_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Equipment schemas
# ---------------------------------------------------------------------------

class EquipmentCreate(BaseModel):
    id: str
    name: str
    type: str
    status: str = "idle"
    zone: Optional[str] = None
    last_maintenance: Optional[str] = None
    operating_hours: int = 0
    error_count: int = 0


class EquipmentStatusUpdate(BaseModel):
    status: str


class EquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    status: str
    zone: Optional[str] = None
    last_maintenance: Optional[str] = None
    operating_hours: int
    error_count: int


# ---------------------------------------------------------------------------
# TransportRequest schemas
# ---------------------------------------------------------------------------

class TransportRequestCreate(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    item_type: str
    quantity: int = 1
    assigned_amr_id: Optional[str] = None


class TransportStatusUpdate(BaseModel):
    status: str
    assigned_amr_id: Optional[str] = None
    failure_reason: Optional[str] = None


class TransportRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    from_zone: str
    to_zone: str
    item_type: str
    quantity: int
    status: str
    assigned_amr_id: Optional[str] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# InspectionRecord schemas
# ---------------------------------------------------------------------------

class InspectionRecordCreate(BaseModel):
    id: str
    casting_id: str
    order_id: Optional[str] = None
    result: str
    confidence: float = 0.0
    image_id: Optional[str] = None
    defect_type: Optional[str] = None


class InspectionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    casting_id: str
    order_id: Optional[str] = None
    result: str
    confidence: float
    image_id: Optional[str] = None
    inspected_at: datetime
    defect_type: Optional[str] = None


# ---------------------------------------------------------------------------
# Alert schemas
# ---------------------------------------------------------------------------

class AlertCreate(BaseModel):
    id: str
    type: str
    severity: str = "info"
    message: str
    zone: Optional[str] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    severity: str
    message: str
    zone: Optional[str] = None
    timestamp: datetime
    acknowledged: bool


# ---------------------------------------------------------------------------
# ProductionMetric schemas
# ---------------------------------------------------------------------------

class ProductionMetricCreate(BaseModel):
    date: str
    production: int = 0
    defects: int = 0
    defect_rate: float = 0.0


class ProductionMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: str
    production: int
    defects: int
    defect_rate: float


# ---------------------------------------------------------------------------
# Quality stats schema
# ---------------------------------------------------------------------------

class QualityStats(BaseModel):
    total: int
    passed: int
    failed: int
    defect_rate: float
    defect_types: dict


# ---------------------------------------------------------------------------
# Dashboard stats schema
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    total_orders: int
    active_orders: int
    equipment_running: int
    equipment_total: int
    pending_transports: int
    active_alerts: int
    today_production: int
    defect_rate: float
