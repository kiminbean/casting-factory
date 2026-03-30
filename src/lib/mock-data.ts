import type {
  Order,
  ProcessStageData,
  Equipment,
  TransportRequest,
  InspectionRecord,
  Alert,
  DashboardStats,
  ProductionMetric,
  StorageSlot,
} from "./types";

export const mockOrders: Order[] = [
  {
    id: "ORD-2026-001",
    customerName: "김철수",
    companyName: "(주)한국도로공사",
    productName: "맨홀 뚜껑 KS D-600",
    productSpec: "600mm / 두께 50mm / EN124 D400",
    material: "GCD450 (구상흑연주철)",
    quantity: 50,
    unitPrice: 85000,
    totalPrice: 4250000,
    status: "in_production",
    postProcessing: "표면 연마 + 방청 코팅",
    requestedDelivery: "2026-04-15",
    estimatedDelivery: "2026-04-12",
    createdAt: "2026-03-25T09:00:00",
    updatedAt: "2026-03-28T14:30:00",
    notes: "로고 삽입 요청",
  },
  {
    id: "ORD-2026-002",
    customerName: "이영희",
    companyName: "(주)서울시설공단",
    productName: "맨홀 뚜껑 KS D-800",
    productSpec: "800mm / 두께 60mm / EN124 E600",
    material: "GCD500 (구상흑연주철)",
    quantity: 30,
    unitPrice: 120000,
    totalPrice: 3600000,
    status: "approved",
    postProcessing: "표면 연마",
    requestedDelivery: "2026-04-20",
    estimatedDelivery: "2026-04-18",
    createdAt: "2026-03-26T10:00:00",
    updatedAt: "2026-03-27T11:00:00",
    notes: "",
  },
  {
    id: "ORD-2026-003",
    customerName: "박민수",
    companyName: "(주)대한건설",
    productName: "맨홀 뚜껑 KS D-450",
    productSpec: "450mm / 두께 40mm / EN124 C250",
    material: "FC250 (회주철)",
    quantity: 100,
    unitPrice: 55000,
    totalPrice: 5500000,
    status: "pending",
    postProcessing: "방청 코팅",
    requestedDelivery: "2026-05-01",
    estimatedDelivery: "",
    createdAt: "2026-03-29T08:30:00",
    updatedAt: "2026-03-29T08:30:00",
    notes: "대량 주문 할인 요청",
  },
  {
    id: "ORD-2026-004",
    customerName: "정수빈",
    companyName: "(주)경기도시공사",
    productName: "맨홀 뚜껑 KS D-600",
    productSpec: "600mm / 두께 50mm / EN124 D400",
    material: "GCD450 (구상흑연주철)",
    quantity: 20,
    unitPrice: 85000,
    totalPrice: 1700000,
    status: "completed",
    postProcessing: "표면 연마 + 방청 코팅 + 문구 삽입",
    requestedDelivery: "2026-03-28",
    estimatedDelivery: "2026-03-27",
    createdAt: "2026-03-15T09:00:00",
    updatedAt: "2026-03-27T16:00:00",
    notes: "납기 완료",
  },
  {
    id: "ORD-2026-005",
    customerName: "최동현",
    companyName: "(주)부산항만공사",
    productName: "배수구 그레이팅",
    productSpec: "500x300mm / 두께 30mm",
    material: "FC200 (회주철)",
    quantity: 200,
    unitPrice: 35000,
    totalPrice: 7000000,
    status: "reviewing",
    postProcessing: "아연 도금",
    requestedDelivery: "2026-04-25",
    estimatedDelivery: "",
    createdAt: "2026-03-30T07:00:00",
    updatedAt: "2026-03-30T07:00:00",
    notes: "항만용 내식성 강화 요청",
  },
];

export const mockProcessStages: ProcessStageData[] = [
  {
    stage: "melting",
    label: "용해",
    status: "running",
    temperature: 1420,
    targetTemperature: 1450,
    progress: 85,
    startTime: "2026-03-30T08:00:00",
    estimatedEnd: "2026-03-30T09:30:00",
    equipmentId: "FRN-001",
    orderId: "ORD-2026-001",
    jobId: "JOB-0301",
  },
  {
    stage: "molding",
    label: "주형 제작",
    status: "completed",
    progress: 100,
    startTime: "2026-03-30T07:00:00",
    estimatedEnd: "2026-03-30T08:00:00",
    equipmentId: "MLD-001",
    orderId: "ORD-2026-001",
    jobId: "JOB-0301",
  },
  {
    stage: "pouring",
    label: "주탕",
    status: "waiting",
    temperature: 1400,
    targetTemperature: 1400,
    progress: 0,
    equipmentId: "ARM-001",
    orderId: "ORD-2026-001",
    jobId: "JOB-0301",
  },
  {
    stage: "cooling",
    label: "냉각",
    status: "running",
    temperature: 320,
    targetTemperature: 25,
    progress: 60,
    startTime: "2026-03-30T06:00:00",
    estimatedEnd: "2026-03-30T10:00:00",
    equipmentId: "CLZ-001",
    orderId: "ORD-2026-001",
    jobId: "JOB-0300",
  },
  {
    stage: "demolding",
    label: "탈형",
    status: "idle",
    progress: 0,
    equipmentId: "ARM-002",
    orderId: "ORD-2026-001",
    jobId: "JOB-0300",
  },
  {
    stage: "post_processing",
    label: "후처리",
    status: "running",
    progress: 45,
    startTime: "2026-03-30T09:00:00",
    estimatedEnd: "2026-03-30T10:30:00",
    equipmentId: "ARM-003",
    orderId: "ORD-2026-001",
    jobId: "JOB-0299",
  },
  {
    stage: "inspection",
    label: "검사",
    status: "running",
    progress: 70,
    startTime: "2026-03-30T09:30:00",
    estimatedEnd: "2026-03-30T10:00:00",
    equipmentId: "CAM-001",
    orderId: "ORD-2026-001",
    jobId: "JOB-0298",
  },
  {
    stage: "classification",
    label: "분류",
    status: "idle",
    progress: 0,
    equipmentId: "CVR-001",
    orderId: "ORD-2026-001",
    jobId: "JOB-0298",
  },
];

export const mockEquipment: Equipment[] = [
  { id: "FRN-001", name: "용해로 #1", type: "furnace", status: "running", zone: "용해 구역", lastMaintenance: "2026-03-20", operatingHours: 1250, errorCount: 0 },
  { id: "FRN-002", name: "용해로 #2", type: "furnace", status: "idle", zone: "용해 구역", lastMaintenance: "2026-03-18", operatingHours: 980, errorCount: 1 },
  { id: "MLD-001", name: "조형기 #1", type: "mold_press", status: "running", zone: "주형 구역", lastMaintenance: "2026-03-22", operatingHours: 890, errorCount: 0 },
  { id: "ARM-001", name: "로봇암 #1 (주탕)", type: "robot_arm", status: "idle", zone: "주조 구역", lastMaintenance: "2026-03-25", operatingHours: 650, errorCount: 0 },
  { id: "ARM-002", name: "로봇암 #2 (탈형)", type: "robot_arm", status: "idle", zone: "냉각 구역", lastMaintenance: "2026-03-24", operatingHours: 720, errorCount: 2 },
  { id: "ARM-003", name: "로봇암 #3 (후처리)", type: "robot_arm", status: "running", zone: "후처리 구역", lastMaintenance: "2026-03-26", operatingHours: 540, errorCount: 0 },
  { id: "AMR-001", name: "AMR #1", type: "amr", status: "running", zone: "이송 중", lastMaintenance: "2026-03-28", operatingHours: 320, errorCount: 0 },
  { id: "AMR-002", name: "AMR #2", type: "amr", status: "idle", zone: "대기 장소", lastMaintenance: "2026-03-27", operatingHours: 280, errorCount: 0 },
  { id: "AMR-003", name: "AMR #3", type: "amr", status: "charging", zone: "충전소", lastMaintenance: "2026-03-29", operatingHours: 410, errorCount: 1 },
  { id: "CVR-001", name: "컨베이어 #1", type: "conveyor", status: "running", zone: "검사 구역", lastMaintenance: "2026-03-21", operatingHours: 1100, errorCount: 0 },
  { id: "CAM-001", name: "검사 카메라 #1", type: "camera", status: "running", zone: "검사 구역", lastMaintenance: "2026-03-23", operatingHours: 800, errorCount: 0 },
];

export const mockTransports: TransportRequest[] = [
  { id: "TRN-001", fromZone: "주조 구역", toZone: "후처리 구역", itemType: "주물 (팔레트)", quantity: 5, status: "moving_to_dest", assignedAmrId: "AMR-001", requestedAt: "2026-03-30T09:15:00" },
  { id: "TRN-002", fromZone: "후처리 구역", toZone: "검사 구역", itemType: "후처리 완료 주물", quantity: 3, status: "requested", requestedAt: "2026-03-30T09:30:00" },
  { id: "TRN-003", fromZone: "검사 구역", toZone: "적재 구역", itemType: "양품 팔레트", quantity: 10, status: "completed", assignedAmrId: "AMR-002", requestedAt: "2026-03-30T08:00:00", completedAt: "2026-03-30T08:25:00" },
  { id: "TRN-004", fromZone: "검사 구역", toZone: "폐기물 구역", itemType: "불량품 박스", quantity: 2, status: "completed", assignedAmrId: "AMR-001", requestedAt: "2026-03-30T08:30:00", completedAt: "2026-03-30T08:45:00" },
  { id: "TRN-005", fromZone: "적재 구역", toZone: "출하 구역", itemType: "출고 팔레트", quantity: 8, status: "assigned", assignedAmrId: "AMR-002", requestedAt: "2026-03-30T09:45:00" },
];

export const mockInspections: InspectionRecord[] = [
  // ORD-2026-004 검사 기록
  { id: "INS-001", castingId: "CST-0298-01", orderId: "ORD-2026-004", result: "pass", confidence: 98.5, imageId: "IMG-001", inspectedAt: "2026-03-30T09:31:00" },
  { id: "INS-002", castingId: "CST-0298-02", orderId: "ORD-2026-004", result: "pass", confidence: 97.2, imageId: "IMG-002", inspectedAt: "2026-03-30T09:32:00" },
  { id: "INS-003", castingId: "CST-0298-03", orderId: "ORD-2026-004", result: "fail", confidence: 95.8, imageId: "IMG-003", inspectedAt: "2026-03-30T09:33:00", defectType: "표면 균열" },
  { id: "INS-004", castingId: "CST-0298-04", orderId: "ORD-2026-004", result: "pass", confidence: 99.1, imageId: "IMG-004", inspectedAt: "2026-03-30T09:34:00" },
  { id: "INS-005", castingId: "CST-0298-05", orderId: "ORD-2026-004", result: "pass", confidence: 96.7, imageId: "IMG-005", inspectedAt: "2026-03-30T09:35:00" },
  { id: "INS-006", castingId: "CST-0298-06", orderId: "ORD-2026-004", result: "fail", confidence: 94.3, imageId: "IMG-006", inspectedAt: "2026-03-30T09:36:00", defectType: "기포 불량" },
  { id: "INS-007", castingId: "CST-0298-07", orderId: "ORD-2026-004", result: "pass", confidence: 98.0, imageId: "IMG-007", inspectedAt: "2026-03-30T09:37:00" },
  { id: "INS-008", castingId: "CST-0298-08", orderId: "ORD-2026-004", result: "pass", confidence: 97.5, imageId: "IMG-008", inspectedAt: "2026-03-30T09:38:00" },
  // ORD-2026-001 검사 기록 (생산 중)
  { id: "INS-009", castingId: "CST-0301-01", orderId: "ORD-2026-001", result: "pass", confidence: 98.8, imageId: "IMG-009", inspectedAt: "2026-03-30T10:01:00" },
  { id: "INS-010", castingId: "CST-0301-02", orderId: "ORD-2026-001", result: "fail", confidence: 92.1, imageId: "IMG-010", inspectedAt: "2026-03-30T10:02:30", defectType: "수축 결함" },
  { id: "INS-011", castingId: "CST-0301-03", orderId: "ORD-2026-001", result: "pass", confidence: 97.9, imageId: "IMG-011", inspectedAt: "2026-03-30T10:04:00" },
  { id: "INS-012", castingId: "CST-0301-04", orderId: "ORD-2026-001", result: "pass", confidence: 99.3, imageId: "IMG-012", inspectedAt: "2026-03-30T10:05:30" },
  { id: "INS-013", castingId: "CST-0301-05", orderId: "ORD-2026-001", result: "fail", confidence: 96.4, imageId: "IMG-013", inspectedAt: "2026-03-30T10:07:00", defectType: "표면 균열" },
  { id: "INS-014", castingId: "CST-0301-06", orderId: "ORD-2026-001", result: "pass", confidence: 98.2, imageId: "IMG-014", inspectedAt: "2026-03-30T10:08:30" },
  { id: "INS-015", castingId: "CST-0301-07", orderId: "ORD-2026-001", result: "pass", confidence: 97.0, imageId: "IMG-015", inspectedAt: "2026-03-30T10:10:00" },
  { id: "INS-016", castingId: "CST-0301-08", orderId: "ORD-2026-001", result: "fail", confidence: 93.7, imageId: "IMG-016", inspectedAt: "2026-03-30T10:11:30", defectType: "주탕 불량" },
  { id: "INS-017", castingId: "CST-0301-09", orderId: "ORD-2026-001", result: "pass", confidence: 98.6, imageId: "IMG-017", inspectedAt: "2026-03-30T10:13:00" },
  { id: "INS-018", castingId: "CST-0301-10", orderId: "ORD-2026-001", result: "pass", confidence: 99.0, imageId: "IMG-018", inspectedAt: "2026-03-30T10:14:30" },
  // 이전 주문 검사 기록 (다양한 불량 유형)
  { id: "INS-019", castingId: "CST-0295-01", orderId: "ORD-2026-004", result: "fail", confidence: 91.5, imageId: "IMG-019", inspectedAt: "2026-03-29T14:20:00", defectType: "치수 불량" },
  { id: "INS-020", castingId: "CST-0295-02", orderId: "ORD-2026-004", result: "pass", confidence: 98.3, imageId: "IMG-020", inspectedAt: "2026-03-29T14:21:30" },
  { id: "INS-021", castingId: "CST-0295-03", orderId: "ORD-2026-004", result: "fail", confidence: 89.8, imageId: "IMG-021", inspectedAt: "2026-03-29T14:23:00", defectType: "기포 불량" },
  { id: "INS-022", castingId: "CST-0295-04", orderId: "ORD-2026-004", result: "pass", confidence: 97.6, imageId: "IMG-022", inspectedAt: "2026-03-29T14:24:30" },
  { id: "INS-023", castingId: "CST-0295-05", orderId: "ORD-2026-004", result: "fail", confidence: 93.2, imageId: "IMG-023", inspectedAt: "2026-03-29T14:26:00", defectType: "냉각 균열" },
  { id: "INS-024", castingId: "CST-0295-06", orderId: "ORD-2026-004", result: "pass", confidence: 99.4, imageId: "IMG-024", inspectedAt: "2026-03-29T14:27:30" },
  { id: "INS-025", castingId: "CST-0295-07", orderId: "ORD-2026-004", result: "fail", confidence: 90.1, imageId: "IMG-025", inspectedAt: "2026-03-29T14:29:00", defectType: "주형 결함" },
  { id: "INS-026", castingId: "CST-0295-08", orderId: "ORD-2026-004", result: "pass", confidence: 96.9, imageId: "IMG-026", inspectedAt: "2026-03-29T14:30:30" },
  { id: "INS-027", castingId: "CST-0295-09", orderId: "ORD-2026-004", result: "fail", confidence: 88.7, imageId: "IMG-027", inspectedAt: "2026-03-29T14:32:00", defectType: "표면 균열" },
  { id: "INS-028", castingId: "CST-0295-10", orderId: "ORD-2026-004", result: "pass", confidence: 98.1, imageId: "IMG-028", inspectedAt: "2026-03-29T14:33:30" },
  { id: "INS-029", castingId: "CST-0296-01", orderId: "ORD-2026-004", result: "fail", confidence: 91.9, imageId: "IMG-029", inspectedAt: "2026-03-29T15:10:00", defectType: "수축 결함" },
  { id: "INS-030", castingId: "CST-0296-02", orderId: "ORD-2026-004", result: "fail", confidence: 87.3, imageId: "IMG-030", inspectedAt: "2026-03-29T15:11:30", defectType: "기포 불량" },
];

export const mockAlerts: Alert[] = [
  { id: "ALT-001", type: "equipment_error", severity: "critical", message: "AMR #3 배터리 부족 - 충전 필요 (12%)", zone: "이송 구역", timestamp: "2026-03-30T09:40:00", acknowledged: false },
  { id: "ALT-002", type: "defect_rate", severity: "warning", message: "불량률 상승 감지 - 현재 25% (기준: 10%)", zone: "검사 구역", timestamp: "2026-03-30T09:35:00", acknowledged: false },
  { id: "ALT-003", type: "process_delay", severity: "warning", message: "용해 공정 지연 - 예상 시간 초과 15분", zone: "용해 구역", timestamp: "2026-03-30T09:20:00", acknowledged: true },
  { id: "ALT-004", type: "system", severity: "info", message: "정기 점검 예정 - 용해로 #2 (2026-04-01)", zone: "용해 구역", timestamp: "2026-03-30T08:00:00", acknowledged: true },
  { id: "ALT-005", type: "transport_failure", severity: "warning", message: "이송 경로 장애물 감지 - AMR #1 우회 경로 사용", zone: "이송 구역", timestamp: "2026-03-30T09:18:00", acknowledged: true },
];

export const mockDashboardStats: DashboardStats = {
  totalOrders: 5,
  activeOrders: 3,
  todayProduction: 47,
  defectRate: 4.2,
  equipmentUtilization: 72.5,
  pendingTransports: 2,
  activeAlerts: 2,
  completedToday: 15,
};

// 30일간 생산 추이 데이터 (현실적인 주물 공장 생산량 시뮬레이션)
export const mockProductionMetrics: ProductionMetric[] = [
  { date: "03/01", production: 45, defects: 2, defectRate: 4.4 },
  { date: "03/02", production: 0, defects: 0, defectRate: 0 },   // 일요일 - 휴무
  { date: "03/03", production: 52, defects: 3, defectRate: 5.8 },
  { date: "03/04", production: 58, defects: 2, defectRate: 3.4 },
  { date: "03/05", production: 61, defects: 4, defectRate: 6.6 },
  { date: "03/06", production: 55, defects: 1, defectRate: 1.8 },
  { date: "03/07", production: 49, defects: 2, defectRate: 4.1 },
  { date: "03/08", production: 43, defects: 3, defectRate: 7.0 },
  { date: "03/09", production: 0, defects: 0, defectRate: 0 },   // 일요일 - 휴무
  { date: "03/10", production: 57, defects: 2, defectRate: 3.5 },
  { date: "03/11", production: 63, defects: 5, defectRate: 7.9 }, // 용해로 정비 후 초기 불량 증가
  { date: "03/12", production: 60, defects: 3, defectRate: 5.0 },
  { date: "03/13", production: 65, defects: 2, defectRate: 3.1 },
  { date: "03/14", production: 58, defects: 1, defectRate: 1.7 },
  { date: "03/15", production: 50, defects: 2, defectRate: 4.0 },
  { date: "03/16", production: 0, defects: 0, defectRate: 0 },   // 일요일 - 휴무
  { date: "03/17", production: 54, defects: 3, defectRate: 5.6 },
  { date: "03/18", production: 62, defects: 2, defectRate: 3.2 },
  { date: "03/19", production: 59, defects: 4, defectRate: 6.8 }, // 새 패턴 적용 초기
  { date: "03/20", production: 66, defects: 2, defectRate: 3.0 },
  { date: "03/21", production: 64, defects: 1, defectRate: 1.6 },
  { date: "03/22", production: 48, defects: 2, defectRate: 4.2 },
  { date: "03/23", production: 0, defects: 0, defectRate: 0 },   // 일요일 - 휴무
  { date: "03/24", production: 42, defects: 2, defectRate: 4.8 },
  { date: "03/25", production: 55, defects: 3, defectRate: 5.5 },
  { date: "03/26", production: 48, defects: 1, defectRate: 2.1 },
  { date: "03/27", production: 61, defects: 2, defectRate: 3.3 },
  { date: "03/28", production: 38, defects: 3, defectRate: 7.9 }, // 원자재 공급 지연
  { date: "03/29", production: 52, defects: 2, defectRate: 3.8 },
  { date: "03/30", production: 47, defects: 2, defectRate: 4.3 },
];

// 최근 7일 데이터 (대시보드 메인에서 사용)
export const mockWeeklyMetrics: ProductionMetric[] = mockProductionMetrics.slice(-7);

// 시간대별 오늘 생산량 (생산 모니터링에서 사용)
export interface HourlyProduction {
  hour: string;
  production: number;
  defects: number;
  temperature: number;
}

export const mockHourlyProduction: HourlyProduction[] = [
  { hour: "06:00", production: 0, defects: 0, temperature: 25 },
  { hour: "07:00", production: 3, defects: 0, temperature: 850 },
  { hour: "08:00", production: 7, defects: 0, temperature: 1380 },
  { hour: "09:00", production: 12, defects: 1, temperature: 1420 },
  { hour: "10:00", production: 8, defects: 0, temperature: 1445 },
  { hour: "11:00", production: 6, defects: 1, temperature: 1430 },
  { hour: "12:00", production: 2, defects: 0, temperature: 1200 },  // 점심
  { hour: "13:00", production: 5, defects: 0, temperature: 1410 },
  { hour: "14:00", production: 4, defects: 0, temperature: 1440 },
];

// 월별 불량 유형 집계 (품질 검사 페이지에서 사용)
export interface DefectTypeStat {
  type: string;
  count: number;
  percentage: number;
  color: string;
}

export const mockDefectTypeStats: DefectTypeStat[] = [
  { type: "표면 균열", count: 12, percentage: 28.6, color: "#ef4444" },
  { type: "기포 불량", count: 9, percentage: 21.4, color: "#f97316" },
  { type: "수축 결함", count: 7, percentage: 16.7, color: "#eab308" },
  { type: "치수 불량", count: 6, percentage: 14.3, color: "#22c55e" },
  { type: "냉각 균열", count: 4, percentage: 9.5, color: "#3b82f6" },
  { type: "주탕 불량", count: 2, percentage: 4.8, color: "#8b5cf6" },
  { type: "주형 결함", count: 2, percentage: 4.8, color: "#ec4899" },
];

// 월별 생산 요약 (대시보드에서 사용)
export interface MonthlyProductionSummary {
  month: string;
  totalProduction: number;
  totalDefects: number;
  defectRate: number;
  ordersFulfilled: number;
}

export const mockMonthlySummary: MonthlyProductionSummary[] = [
  { month: "2025/10", totalProduction: 1180, totalDefects: 52, defectRate: 4.4, ordersFulfilled: 12 },
  { month: "2025/11", totalProduction: 1250, totalDefects: 48, defectRate: 3.8, ordersFulfilled: 14 },
  { month: "2025/12", totalProduction: 980, totalDefects: 55, defectRate: 5.6, ordersFulfilled: 10 },
  { month: "2026/01", totalProduction: 1320, totalDefects: 42, defectRate: 3.2, ordersFulfilled: 15 },
  { month: "2026/02", totalProduction: 1150, totalDefects: 39, defectRate: 3.4, ordersFulfilled: 13 },
  { month: "2026/03", totalProduction: 1087, totalDefects: 47, defectRate: 4.3, ordersFulfilled: 11 },
];

export const mockStorageSlots: StorageSlot[] = Array.from({ length: 24 }, (_, i) => {
  const row = Math.floor(i / 6);
  const col = i % 6;
  const statuses: StorageSlot["status"][] = ["occupied", "empty", "occupied", "reserved", "empty", "occupied", "occupied", "empty", "unavailable", "occupied", "empty", "occupied", "occupied", "occupied", "empty", "empty", "occupied", "reserved", "empty", "occupied", "empty", "empty", "occupied", "occupied"];
  const slot: StorageSlot = {
    id: `SLT-${String(row + 1).padStart(2, "0")}-${String(col + 1).padStart(2, "0")}`,
    row: row + 1,
    col: col + 1,
    status: statuses[i],
    updatedAt: "2026-03-30T09:00:00",
  };
  if (slot.status === "occupied") {
    slot.productName = "맨홀 뚜껑 KS D-600";
    slot.quantity = Math.floor(Math.random() * 8) + 2;
  }
  return slot;
});
