from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Order schemas
# ---------------------------------------------------------------------------

class OrderCreate(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    company_name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[str] = None
    total_amount: float = 0.0
    status: str = "pending"
    requested_delivery: Optional[str] = None
    confirmed_delivery: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str


class OrderUpdate(BaseModel):
    """주문 필드 부분 수정 (견적 금액, 확정 납기)."""
    total_amount: Optional[float] = None
    confirmed_delivery: Optional[str] = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: str
    customer_name: str
    company_name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[str] = None
    total_amount: float
    status: str
    requested_delivery: Optional[str] = None
    confirmed_delivery: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# OrderDetail schemas
# ---------------------------------------------------------------------------

class OrderDetailCreate(BaseModel):
    id: str
    order_id: str
    product_id: str
    product_name: str
    quantity: int = 0
    spec: Optional[str] = None
    material: Optional[str] = None
    post_processing: Optional[str] = None
    logo_data: Optional[str] = None
    unit_price: float = 0.0
    subtotal: float = 0.0


class OrderDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    product_id: str
    product_name: str
    quantity: int
    spec: Optional[str] = None
    material: Optional[str] = None
    post_processing: Optional[str] = None
    logo_data: Optional[str] = None
    unit_price: float
    subtotal: float


# ---------------------------------------------------------------------------
# Product schemas
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str
    name: str
    category: str
    category_label: str = ""
    spec: str = ""
    price_range: str = ""
    base_price: int = 0
    diameter_options: List[str] = []
    thickness_options: List[str] = []
    materials: List[str] = []
    load_class_range: str = ""
    option_pricing: Optional[dict] = None
    design_image_url: Optional[str] = None
    model_3d_path: Optional[str] = None


class ProductResponse(BaseModel):
    """프론트 Product interface 와 1:1 매칭 (snake→camel 변환은 src/lib/api.ts 에서)."""

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    name: str
    category: str
    category_label: str
    spec: str
    price_range: str
    base_price: int
    diameter_options: List[str] = []
    thickness_options: List[str] = []
    materials: List[str] = []
    load_class_range: str
    option_pricing: Optional[dict] = None
    design_image_url: Optional[str] = None
    model_3d_path: Optional[str] = None

    @classmethod
    def from_orm_model(cls, product) -> "ProductResponse":
        """Product ORM 인스턴스의 *_json 컬럼을 파싱해서 list/dict 로 변환."""
        import json as _json

        def _parse_list(raw: Optional[str]) -> List[str]:
            if not raw:
                return []
            try:
                val = _json.loads(raw)
                return val if isinstance(val, list) else []
            except (ValueError, TypeError):
                return []

        def _parse_dict(raw: Optional[str]) -> Optional[dict]:
            if not raw:
                return None
            try:
                val = _json.loads(raw)
                return val if isinstance(val, dict) else None
            except (ValueError, TypeError):
                return None

        return cls(
            id=product.id,
            name=product.name,
            category=product.category,
            category_label=product.category_label or "",
            spec=product.spec or "",
            price_range=product.price_range or "",
            base_price=product.base_price or 0,
            diameter_options=_parse_list(product.diameter_options_json),
            thickness_options=_parse_list(product.thickness_options_json),
            materials=_parse_list(product.materials_json),
            load_class_range=product.load_class_range or "",
            option_pricing=_parse_dict(product.option_pricing_json),
            design_image_url=product.design_image_url or None,
            model_3d_path=product.model_3d_path or None,
        )


# ---------------------------------------------------------------------------
# LoadClass schemas (EN 124 하중 등급 마스터)
# ---------------------------------------------------------------------------

class LoadClassResponse(BaseModel):
    """EN 124 하중 등급 한 행."""

    model_config = ConfigDict(from_attributes=True)

    code: str          # "A15", "B125", ...
    load_tons: float   # 1.5, 12.5, ...
    use_case: str      # "보행자 전용 구역" 등 설명
    display_order: int


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
    start_time: Optional[str] = None
    estimated_end: Optional[str] = None
    equipment_id: Optional[str] = None
    order_id: Optional[str] = None
    job_id: Optional[str] = None
    pressure: Optional[float] = None
    pour_angle: Optional[float] = None
    heating_power: Optional[float] = None
    cooling_progress: Optional[float] = None


class ProcessStageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stage: str
    label: str
    status: str
    temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    progress: int
    start_time: Optional[str] = None
    estimated_end: Optional[str] = None
    equipment_id: Optional[str] = None
    order_id: Optional[str] = None
    job_id: Optional[str] = None
    pressure: Optional[float] = None
    pour_angle: Optional[float] = None
    heating_power: Optional[float] = None
    cooling_progress: Optional[float] = None


# ---------------------------------------------------------------------------
# Equipment schemas
# ---------------------------------------------------------------------------

class EquipmentCreate(BaseModel):
    id: str
    name: str
    type: str
    comm_id: Optional[str] = None
    install_location: Optional[str] = None
    status: str = "idle"
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    battery: Optional[float] = None
    speed: Optional[float] = None
    last_update: Optional[str] = None
    last_maintenance: Optional[str] = None
    operating_hours: int = 0
    error_count: int = 0


class EquipmentStatusUpdate(BaseModel):
    status: str
    battery: Optional[float] = None
    speed: Optional[float] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    pos_z: Optional[float] = None


class EquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    comm_id: Optional[str] = None
    install_location: Optional[str] = None
    status: str
    pos_x: float
    pos_y: float
    pos_z: float
    battery: Optional[float] = None
    speed: Optional[float] = None
    last_update: Optional[str] = None
    last_maintenance: Optional[str] = None
    operating_hours: int
    error_count: int


# ---------------------------------------------------------------------------
# Alert schemas
# ---------------------------------------------------------------------------

class AlertCreate(BaseModel):
    id: str
    equipment_id: Optional[str] = None
    type: str
    severity: str = "info"
    error_code: Optional[str] = None
    message: str
    abnormal_value: Optional[str] = None
    zone: Optional[str] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    equipment_id: Optional[str] = None
    type: str
    severity: str
    error_code: Optional[str] = None
    message: str
    abnormal_value: Optional[str] = None
    zone: Optional[str] = None
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool


# ---------------------------------------------------------------------------
# InspectionRecord schemas
# ---------------------------------------------------------------------------

class InspectionRecordCreate(BaseModel):
    id: str
    product_id: Optional[str] = None
    casting_id: str
    order_id: Optional[str] = None
    result: str
    defect_type_code: Optional[str] = None
    confidence: float = 0.0
    inspector_id: Optional[str] = None
    image_id: Optional[str] = None
    defect_type: Optional[str] = None
    defect_detail: Optional[str] = None


class InspectionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: Optional[str] = None
    casting_id: str
    order_id: Optional[str] = None
    result: str
    defect_type_code: Optional[str] = None
    confidence: float
    inspector_id: Optional[str] = None
    image_id: Optional[str] = None
    inspected_at: datetime
    defect_type: Optional[str] = None
    defect_detail: Optional[str] = None


# ---------------------------------------------------------------------------
# InspectionStandard schemas
# ---------------------------------------------------------------------------

class InspectionStandardCreate(BaseModel):
    product_id: str
    product_name: str
    tolerance_range: Optional[str] = None
    target_dimension: Optional[str] = None
    threshold: float = 0.0


class InspectionStandardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: str
    product_name: str
    tolerance_range: Optional[str] = None
    target_dimension: Optional[str] = None
    threshold: float


# ---------------------------------------------------------------------------
# SorterLog schemas
# ---------------------------------------------------------------------------

class SorterLogCreate(BaseModel):
    inspection_id: str
    sort_direction: str  # "pass_line" | "fail_line"
    sorter_angle: float = 0.0
    success: bool = True


class SorterLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_id: str
    sort_direction: str
    sorter_angle: float
    success: bool


# ---------------------------------------------------------------------------
# TransportTask schemas (replaces TransportRequest)
# ---------------------------------------------------------------------------

class TransportTaskCreate(BaseModel):
    id: str
    from_name: str
    from_coord: Optional[str] = None
    to_name: str
    to_coord: Optional[str] = None
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: int = 1
    priority: str = "medium"  # "high" | "medium" | "low"
    assigned_robot_id: Optional[str] = None


class TransportStatusUpdate(BaseModel):
    status: str
    assigned_robot_id: Optional[str] = None


class TransportTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    from_name: str
    from_coord: Optional[str] = None
    to_name: str
    to_coord: Optional[str] = None
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: int
    priority: str
    status: str
    assigned_robot_id: Optional[str] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# WarehouseRack schemas
# ---------------------------------------------------------------------------

class WarehouseRackCreate(BaseModel):
    id: str
    zone: str
    rack_number: str
    status: str = "empty"  # "empty" | "occupied" | "reserved" | "unavailable"
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    row: int = 0
    col: int = 0


class WarehouseRackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zone: str
    rack_number: str
    status: str
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    last_inbound_at: Optional[datetime] = None
    row: int
    col: int


# ---------------------------------------------------------------------------
# OutboundOrder schemas
# ---------------------------------------------------------------------------

class OutboundOrderCreate(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: int = 0
    destination: Optional[str] = None
    policy: str = "FIFO"  # "LIFO" | "FIFO"
    completed: bool = False


class OutboundOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    product_name: str
    quantity: int
    destination: Optional[str] = None
    policy: str
    completed: bool
    created_at: datetime


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
    defect_type_codes: Optional[dict] = None
    inspector_stats: Optional[dict] = None


# ---------------------------------------------------------------------------
# Dashboard stats schema
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    production_goal_rate: float = 0.0
    active_robots: int = 0
    pending_orders: int = 0
    today_alarms: int = 0
    today_production: int = 0
    defect_rate: float = 0.0
    equipment_utilization: float = 0.0
    completed_today: int = 0


# ---------------------------------------------------------------------------
# Production Scheduling schemas
# ---------------------------------------------------------------------------

class PriorityCalculateRequest(BaseModel):
    """우선순위 계산 요청 — 주문 ID 목록"""
    order_ids: list[str]


class PriorityFactor(BaseModel):
    """개별 우선순위 요인 점수"""
    name: str
    score: float
    max_score: float
    detail: str


class PriorityResult(BaseModel):
    """단일 주문의 우선순위 계산 결과"""
    order_id: str
    company_name: str
    product_summary: str
    total_quantity: int
    requested_delivery: Optional[str] = None
    total_score: float
    rank: int
    factors: list[PriorityFactor]
    recommendation_reason: str
    delay_risk: str  # high / medium / low
    ready_status: str  # ready / not_ready
    blocking_reasons: list[str]
    estimated_days: int


class PriorityCalculateResponse(BaseModel):
    """우선순위 계산 응답"""
    results: list[PriorityResult]


class ProductionStartRequest(BaseModel):
    """생산 개시 요청 — 주문 ID + 순위 목록"""
    order_ids: list[str]


class ProductionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    priority_score: float
    priority_rank: int
    assigned_stage: str
    status: str
    estimated_completion: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str


class PriorityLogCreate(BaseModel):
    """우선순위 변경 이력 생성"""
    order_id: str
    old_rank: int
    new_rank: int
    reason: str


class PriorityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: str
    old_rank: int
    new_rank: int
    reason: str
    changed_by: str
    changed_at: str
