from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import (
    Alert,
    Equipment,
    InspectionRecord,
    Order,
    ProcessStage,
    ProductionMetric,
    TransportRequest,
)


def seed_database(db: Session) -> None:
    """Populate the database with realistic mock data if tables are empty."""
    _seed_orders(db)
    _seed_process_stages(db)
    _seed_equipment(db)
    _seed_transport_requests(db)
    _seed_inspection_records(db)
    _seed_alerts(db)
    _seed_production_metrics(db)


def _seed_orders(db: Session) -> None:
    if db.query(Order).count() > 0:
        return
    orders = [
        Order(
            id="ORD-2026-001",
            customer_name="김철수",
            company_name="(주)한국도로공사",
            product_name="맨홀 뚜껑 KS D-600",
            product_spec="600mm / 두께 50mm / EN124 D400",
            material="GCD450 (구상흑연주철)",
            quantity=50,
            unit_price=85000,
            total_price=4250000,
            status="in_production",
            post_processing="표면 연마 + 방청 코팅",
            requested_delivery="2026-04-15",
            estimated_delivery="2026-04-12",
            created_at=datetime(2026, 3, 25, 9, 0, 0),
            updated_at=datetime(2026, 3, 28, 14, 30, 0),
            notes="로고 삽입 요청",
        ),
        Order(
            id="ORD-2026-002",
            customer_name="이영희",
            company_name="(주)서울시설공단",
            product_name="맨홀 뚜껑 KS D-800",
            product_spec="800mm / 두께 60mm / EN124 E600",
            material="GCD500 (구상흑연주철)",
            quantity=30,
            unit_price=120000,
            total_price=3600000,
            status="approved",
            post_processing="표면 연마",
            requested_delivery="2026-04-20",
            estimated_delivery="2026-04-18",
            created_at=datetime(2026, 3, 26, 10, 0, 0),
            updated_at=datetime(2026, 3, 27, 11, 0, 0),
            notes="",
        ),
        Order(
            id="ORD-2026-003",
            customer_name="박민수",
            company_name="(주)대한건설",
            product_name="맨홀 뚜껑 KS D-450",
            product_spec="450mm / 두께 40mm / EN124 C250",
            material="FC250 (회주철)",
            quantity=100,
            unit_price=55000,
            total_price=5500000,
            status="pending",
            post_processing="방청 코팅",
            requested_delivery="2026-05-01",
            estimated_delivery="",
            created_at=datetime(2026, 3, 29, 8, 30, 0),
            updated_at=datetime(2026, 3, 29, 8, 30, 0),
            notes="대량 주문 할인 요청",
        ),
        Order(
            id="ORD-2026-004",
            customer_name="정수빈",
            company_name="(주)경기도시공사",
            product_name="맨홀 뚜껑 KS D-600",
            product_spec="600mm / 두께 50mm / EN124 D400",
            material="GCD450 (구상흑연주철)",
            quantity=20,
            unit_price=85000,
            total_price=1700000,
            status="completed",
            post_processing="표면 연마 + 방청 코팅 + 문구 삽입",
            requested_delivery="2026-03-28",
            estimated_delivery="2026-03-27",
            created_at=datetime(2026, 3, 15, 9, 0, 0),
            updated_at=datetime(2026, 3, 27, 16, 0, 0),
            notes="납기 완료",
        ),
        Order(
            id="ORD-2026-005",
            customer_name="최동현",
            company_name="(주)부산항만공사",
            product_name="배수구 그레이팅",
            product_spec="500x300mm / 두께 30mm",
            material="FC200 (회주철)",
            quantity=200,
            unit_price=35000,
            total_price=7000000,
            status="reviewing",
            post_processing="아연 도금",
            requested_delivery="2026-04-25",
            estimated_delivery="",
            created_at=datetime(2026, 3, 30, 7, 0, 0),
            updated_at=datetime(2026, 3, 30, 7, 0, 0),
            notes="항만용 내식성 강화 요청",
        ),
    ]
    db.add_all(orders)
    db.commit()


def _seed_process_stages(db: Session) -> None:
    if db.query(ProcessStage).count() > 0:
        return
    stages = [
        ProcessStage(stage="melting", label="용해", status="running", temperature=1420.0, target_temperature=1450.0, progress=85, equipment_id="FRN-001", order_id="ORD-2026-001", job_id="JOB-0301"),
        ProcessStage(stage="molding", label="주형 제작", status="completed", progress=100, equipment_id="MLD-001", order_id="ORD-2026-001", job_id="JOB-0301"),
        ProcessStage(stage="pouring", label="주탕", status="waiting", temperature=1400.0, target_temperature=1400.0, progress=0, equipment_id="ARM-001", order_id="ORD-2026-001", job_id="JOB-0301"),
        ProcessStage(stage="cooling", label="냉각", status="running", temperature=320.0, target_temperature=25.0, progress=60, equipment_id="CLZ-001", order_id="ORD-2026-001", job_id="JOB-0300"),
        ProcessStage(stage="demolding", label="탈형", status="idle", progress=0, equipment_id="ARM-002", order_id="ORD-2026-001", job_id="JOB-0300"),
        ProcessStage(stage="post_processing", label="후처리", status="running", progress=45, equipment_id="ARM-003", order_id="ORD-2026-001", job_id="JOB-0299"),
        ProcessStage(stage="inspection", label="검사", status="running", progress=70, equipment_id="CAM-001", order_id="ORD-2026-001", job_id="JOB-0298"),
        ProcessStage(stage="classification", label="분류", status="idle", progress=0, equipment_id="CVR-001", order_id="ORD-2026-001", job_id="JOB-0298"),
    ]
    db.add_all(stages)
    db.commit()


def _seed_equipment(db: Session) -> None:
    if db.query(Equipment).count() > 0:
        return
    equipment_list = [
        Equipment(id="FRN-001", name="용해로 #1", type="furnace", status="running", zone="용해 구역", last_maintenance="2026-03-20", operating_hours=1250, error_count=0),
        Equipment(id="FRN-002", name="용해로 #2", type="furnace", status="idle", zone="용해 구역", last_maintenance="2026-03-18", operating_hours=980, error_count=1),
        Equipment(id="MLD-001", name="조형기 #1", type="mold_press", status="running", zone="주형 구역", last_maintenance="2026-03-22", operating_hours=890, error_count=0),
        Equipment(id="ARM-001", name="로봇암 #1 (주탕)", type="robot_arm", status="idle", zone="주조 구역", last_maintenance="2026-03-25", operating_hours=650, error_count=0),
        Equipment(id="ARM-002", name="로봇암 #2 (탈형)", type="robot_arm", status="idle", zone="냉각 구역", last_maintenance="2026-03-24", operating_hours=720, error_count=2),
        Equipment(id="ARM-003", name="로봇암 #3 (후처리)", type="robot_arm", status="running", zone="후처리 구역", last_maintenance="2026-03-26", operating_hours=540, error_count=0),
        Equipment(id="AMR-001", name="AMR #1", type="amr", status="running", zone="이송 중", last_maintenance="2026-03-28", operating_hours=320, error_count=0),
        Equipment(id="AMR-002", name="AMR #2", type="amr", status="idle", zone="대기 장소", last_maintenance="2026-03-27", operating_hours=280, error_count=0),
        Equipment(id="AMR-003", name="AMR #3", type="amr", status="charging", zone="충전소", last_maintenance="2026-03-29", operating_hours=410, error_count=1),
        Equipment(id="CVR-001", name="컨베이어 #1", type="conveyor", status="running", zone="검사 구역", last_maintenance="2026-03-21", operating_hours=1100, error_count=0),
        Equipment(id="CAM-001", name="검사 카메라 #1", type="camera", status="running", zone="검사 구역", last_maintenance="2026-03-23", operating_hours=800, error_count=0),
    ]
    db.add_all(equipment_list)
    db.commit()


def _seed_transport_requests(db: Session) -> None:
    if db.query(TransportRequest).count() > 0:
        return
    transports = [
        TransportRequest(id="TRN-001", from_zone="주조 구역", to_zone="후처리 구역", item_type="주물 (팔레트)", quantity=5, status="moving_to_dest", assigned_amr_id="AMR-001", requested_at=datetime(2026, 3, 30, 9, 15, 0)),
        TransportRequest(id="TRN-002", from_zone="후처리 구역", to_zone="검사 구역", item_type="후처리 완료 주물", quantity=3, status="requested", requested_at=datetime(2026, 3, 30, 9, 30, 0)),
        TransportRequest(id="TRN-003", from_zone="검사 구역", to_zone="적재 구역", item_type="양품 팔레트", quantity=10, status="completed", assigned_amr_id="AMR-002", requested_at=datetime(2026, 3, 30, 8, 0, 0), completed_at=datetime(2026, 3, 30, 8, 25, 0)),
        TransportRequest(id="TRN-004", from_zone="검사 구역", to_zone="폐기물 구역", item_type="불량품 박스", quantity=2, status="completed", assigned_amr_id="AMR-001", requested_at=datetime(2026, 3, 30, 8, 30, 0), completed_at=datetime(2026, 3, 30, 8, 45, 0)),
        TransportRequest(id="TRN-005", from_zone="적재 구역", to_zone="출하 구역", item_type="출고 팔레트", quantity=8, status="assigned", assigned_amr_id="AMR-002", requested_at=datetime(2026, 3, 30, 9, 45, 0)),
    ]
    db.add_all(transports)
    db.commit()


def _seed_inspection_records(db: Session) -> None:
    if db.query(InspectionRecord).count() > 0:
        return
    records = [
        # ORD-2026-004 inspection records
        InspectionRecord(id="INS-001", casting_id="CST-0298-01", order_id="ORD-2026-004", result="pass", confidence=98.5, image_id="IMG-001", inspected_at=datetime(2026, 3, 30, 9, 31, 0)),
        InspectionRecord(id="INS-002", casting_id="CST-0298-02", order_id="ORD-2026-004", result="pass", confidence=97.2, image_id="IMG-002", inspected_at=datetime(2026, 3, 30, 9, 32, 0)),
        InspectionRecord(id="INS-003", casting_id="CST-0298-03", order_id="ORD-2026-004", result="fail", confidence=95.8, image_id="IMG-003", inspected_at=datetime(2026, 3, 30, 9, 33, 0), defect_type="표면 균열"),
        InspectionRecord(id="INS-004", casting_id="CST-0298-04", order_id="ORD-2026-004", result="pass", confidence=99.1, image_id="IMG-004", inspected_at=datetime(2026, 3, 30, 9, 34, 0)),
        InspectionRecord(id="INS-005", casting_id="CST-0298-05", order_id="ORD-2026-004", result="pass", confidence=96.7, image_id="IMG-005", inspected_at=datetime(2026, 3, 30, 9, 35, 0)),
        InspectionRecord(id="INS-006", casting_id="CST-0298-06", order_id="ORD-2026-004", result="fail", confidence=94.3, image_id="IMG-006", inspected_at=datetime(2026, 3, 30, 9, 36, 0), defect_type="기포 불량"),
        InspectionRecord(id="INS-007", casting_id="CST-0298-07", order_id="ORD-2026-004", result="pass", confidence=98.0, image_id="IMG-007", inspected_at=datetime(2026, 3, 30, 9, 37, 0)),
        InspectionRecord(id="INS-008", casting_id="CST-0298-08", order_id="ORD-2026-004", result="pass", confidence=97.5, image_id="IMG-008", inspected_at=datetime(2026, 3, 30, 9, 38, 0)),
        # ORD-2026-001 inspection records (in production)
        InspectionRecord(id="INS-009", casting_id="CST-0301-01", order_id="ORD-2026-001", result="pass", confidence=98.8, image_id="IMG-009", inspected_at=datetime(2026, 3, 30, 10, 1, 0)),
        InspectionRecord(id="INS-010", casting_id="CST-0301-02", order_id="ORD-2026-001", result="fail", confidence=92.1, image_id="IMG-010", inspected_at=datetime(2026, 3, 30, 10, 2, 30), defect_type="수축 결함"),
        InspectionRecord(id="INS-011", casting_id="CST-0301-03", order_id="ORD-2026-001", result="pass", confidence=97.9, image_id="IMG-011", inspected_at=datetime(2026, 3, 30, 10, 4, 0)),
        InspectionRecord(id="INS-012", casting_id="CST-0301-04", order_id="ORD-2026-001", result="pass", confidence=99.3, image_id="IMG-012", inspected_at=datetime(2026, 3, 30, 10, 5, 30)),
        InspectionRecord(id="INS-013", casting_id="CST-0301-05", order_id="ORD-2026-001", result="fail", confidence=96.4, image_id="IMG-013", inspected_at=datetime(2026, 3, 30, 10, 7, 0), defect_type="표면 균열"),
        InspectionRecord(id="INS-014", casting_id="CST-0301-06", order_id="ORD-2026-001", result="pass", confidence=98.2, image_id="IMG-014", inspected_at=datetime(2026, 3, 30, 10, 8, 30)),
        InspectionRecord(id="INS-015", casting_id="CST-0301-07", order_id="ORD-2026-001", result="pass", confidence=97.0, image_id="IMG-015", inspected_at=datetime(2026, 3, 30, 10, 10, 0)),
        InspectionRecord(id="INS-016", casting_id="CST-0301-08", order_id="ORD-2026-001", result="fail", confidence=93.7, image_id="IMG-016", inspected_at=datetime(2026, 3, 30, 10, 11, 30), defect_type="주탕 불량"),
        InspectionRecord(id="INS-017", casting_id="CST-0301-09", order_id="ORD-2026-001", result="pass", confidence=98.6, image_id="IMG-017", inspected_at=datetime(2026, 3, 30, 10, 13, 0)),
        InspectionRecord(id="INS-018", casting_id="CST-0301-10", order_id="ORD-2026-001", result="pass", confidence=99.0, image_id="IMG-018", inspected_at=datetime(2026, 3, 30, 10, 14, 30)),
        # Historical inspection records with various defect types
        InspectionRecord(id="INS-019", casting_id="CST-0295-01", order_id="ORD-2026-004", result="fail", confidence=91.5, image_id="IMG-019", inspected_at=datetime(2026, 3, 29, 14, 20, 0), defect_type="치수 불량"),
        InspectionRecord(id="INS-020", casting_id="CST-0295-02", order_id="ORD-2026-004", result="pass", confidence=98.3, image_id="IMG-020", inspected_at=datetime(2026, 3, 29, 14, 21, 30)),
        InspectionRecord(id="INS-021", casting_id="CST-0295-03", order_id="ORD-2026-004", result="fail", confidence=89.8, image_id="IMG-021", inspected_at=datetime(2026, 3, 29, 14, 23, 0), defect_type="기포 불량"),
        InspectionRecord(id="INS-022", casting_id="CST-0295-04", order_id="ORD-2026-004", result="pass", confidence=97.6, image_id="IMG-022", inspected_at=datetime(2026, 3, 29, 14, 24, 30)),
        InspectionRecord(id="INS-023", casting_id="CST-0295-05", order_id="ORD-2026-004", result="fail", confidence=93.2, image_id="IMG-023", inspected_at=datetime(2026, 3, 29, 14, 26, 0), defect_type="냉각 균열"),
        InspectionRecord(id="INS-024", casting_id="CST-0295-06", order_id="ORD-2026-004", result="pass", confidence=99.4, image_id="IMG-024", inspected_at=datetime(2026, 3, 29, 14, 27, 30)),
        InspectionRecord(id="INS-025", casting_id="CST-0295-07", order_id="ORD-2026-004", result="fail", confidence=90.1, image_id="IMG-025", inspected_at=datetime(2026, 3, 29, 14, 29, 0), defect_type="주형 결함"),
        InspectionRecord(id="INS-026", casting_id="CST-0295-08", order_id="ORD-2026-004", result="pass", confidence=96.9, image_id="IMG-026", inspected_at=datetime(2026, 3, 29, 14, 30, 30)),
        InspectionRecord(id="INS-027", casting_id="CST-0295-09", order_id="ORD-2026-004", result="fail", confidence=88.7, image_id="IMG-027", inspected_at=datetime(2026, 3, 29, 14, 32, 0), defect_type="표면 균열"),
        InspectionRecord(id="INS-028", casting_id="CST-0295-10", order_id="ORD-2026-004", result="pass", confidence=98.1, image_id="IMG-028", inspected_at=datetime(2026, 3, 29, 14, 33, 30)),
        InspectionRecord(id="INS-029", casting_id="CST-0296-01", order_id="ORD-2026-004", result="fail", confidence=91.9, image_id="IMG-029", inspected_at=datetime(2026, 3, 29, 15, 10, 0), defect_type="수축 결함"),
        InspectionRecord(id="INS-030", casting_id="CST-0296-02", order_id="ORD-2026-004", result="fail", confidence=87.3, image_id="IMG-030", inspected_at=datetime(2026, 3, 29, 15, 11, 30), defect_type="기포 불량"),
    ]
    db.add_all(records)
    db.commit()


def _seed_alerts(db: Session) -> None:
    if db.query(Alert).count() > 0:
        return
    alerts = [
        Alert(id="ALT-001", type="equipment_error", severity="critical", message="AMR #3 배터리 부족 - 충전 필요 (12%)", zone="이송 구역", timestamp=datetime(2026, 3, 30, 9, 40, 0), acknowledged=False),
        Alert(id="ALT-002", type="defect_rate", severity="warning", message="불량률 상승 감지 - 현재 25% (기준: 10%)", zone="검사 구역", timestamp=datetime(2026, 3, 30, 9, 35, 0), acknowledged=False),
        Alert(id="ALT-003", type="process_delay", severity="warning", message="용해 공정 지연 - 예상 시간 초과 15분", zone="용해 구역", timestamp=datetime(2026, 3, 30, 9, 20, 0), acknowledged=True),
        Alert(id="ALT-004", type="system", severity="info", message="정기 점검 예정 - 용해로 #2 (2026-04-01)", zone="용해 구역", timestamp=datetime(2026, 3, 30, 8, 0, 0), acknowledged=True),
        Alert(id="ALT-005", type="transport_failure", severity="warning", message="이송 경로 장애물 감지 - AMR #1 우회 경로 사용", zone="이송 구역", timestamp=datetime(2026, 3, 30, 9, 18, 0), acknowledged=True),
    ]
    db.add_all(alerts)
    db.commit()


def _seed_production_metrics(db: Session) -> None:
    if db.query(ProductionMetric).count() > 0:
        return
    metrics_data = [
        ("03/01", 45, 2, 4.4),
        ("03/02", 0, 0, 0.0),
        ("03/03", 52, 3, 5.8),
        ("03/04", 58, 2, 3.4),
        ("03/05", 61, 4, 6.6),
        ("03/06", 55, 1, 1.8),
        ("03/07", 49, 2, 4.1),
        ("03/08", 43, 3, 7.0),
        ("03/09", 0, 0, 0.0),
        ("03/10", 57, 2, 3.5),
        ("03/11", 63, 5, 7.9),
        ("03/12", 60, 3, 5.0),
        ("03/13", 65, 2, 3.1),
        ("03/14", 58, 1, 1.7),
        ("03/15", 50, 2, 4.0),
        ("03/16", 0, 0, 0.0),
        ("03/17", 54, 3, 5.6),
        ("03/18", 62, 2, 3.2),
        ("03/19", 59, 4, 6.8),
        ("03/20", 66, 2, 3.0),
        ("03/21", 64, 1, 1.6),
        ("03/22", 48, 2, 4.2),
        ("03/23", 0, 0, 0.0),
        ("03/24", 42, 2, 4.8),
        ("03/25", 55, 3, 5.5),
        ("03/26", 48, 1, 2.1),
        ("03/27", 61, 2, 3.3),
        ("03/28", 38, 3, 7.9),
        ("03/29", 52, 2, 3.8),
        ("03/30", 47, 2, 4.3),
    ]
    metrics = [
        ProductionMetric(date=d, production=p, defects=def_, defect_rate=dr)
        for d, p, def_, dr in metrics_data
    ]
    db.add_all(metrics)
    db.commit()
