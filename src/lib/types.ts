// 주문 관련 타입
export type OrderStatus =
  | "pending"
  | "reviewing"
  | "approved"
  | "in_production"
  | "shipping_ready"
  | "completed"
  | "rejected";

export interface Order {
  id: string;
  customerName: string;
  companyName: string;
  productName: string;
  productSpec: string; // 규격 (e.g., "600mm x 50mm")
  material: string; // 재질 (e.g., "GCD450")
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  status: OrderStatus;
  postProcessing: string; // 후처리 옵션
  requestedDelivery: string;
  estimatedDelivery: string;
  createdAt: string;
  updatedAt: string;
  notes: string;
}

// 공정 단계 타입
export type ProcessStage =
  | "melting" // 용해
  | "molding" // 주형 제작
  | "pouring" // 주탕
  | "cooling" // 냉각
  | "demolding" // 탈형
  | "post_processing" // 후처리
  | "inspection" // 검사
  | "classification"; // 분류

export type ProcessStatus = "idle" | "running" | "completed" | "error" | "waiting";

export interface ProcessStageData {
  stage: ProcessStage;
  label: string;
  status: ProcessStatus;
  temperature?: number;
  targetTemperature?: number;
  progress: number; // 0-100
  startTime?: string;
  estimatedEnd?: string;
  equipmentId: string;
  orderId: string;
  jobId: string;
}

// 장비 타입
export type EquipmentType = "furnace" | "mold_press" | "robot_arm" | "amr" | "conveyor" | "camera";
export type EquipmentStatus = "idle" | "running" | "error" | "maintenance" | "charging";

export interface Equipment {
  id: string;
  name: string;
  type: EquipmentType;
  status: EquipmentStatus;
  zone: string;
  lastMaintenance: string;
  operatingHours: number;
  errorCount: number;
}

// 이송 타입
export type TransportStatus =
  | "requested"
  | "assigned"
  | "moving_to_pickup"
  | "arrived_pickup"
  | "loading"
  | "moving_to_dest"
  | "arrived_dest"
  | "unloading"
  | "completed"
  | "failed";

export interface TransportRequest {
  id: string;
  fromZone: string;
  toZone: string;
  itemType: string;
  quantity: number;
  status: TransportStatus;
  assignedAmrId?: string;
  requestedAt: string;
  completedAt?: string;
  failureReason?: string;
}

// 품질 검사 타입
export type InspectionResult = "pass" | "fail";

export interface InspectionRecord {
  id: string;
  castingId: string;
  orderId: string;
  result: InspectionResult;
  confidence: number; // 0-100
  imageId: string;
  inspectedAt: string;
  defectType?: string;
}

// 알림 타입
export type AlertSeverity = "info" | "warning" | "critical";
export type AlertType = "equipment_error" | "process_delay" | "defect_rate" | "transport_failure" | "system";

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  zone: string;
  timestamp: string;
  acknowledged: boolean;
}

// 대시보드 통계
export interface DashboardStats {
  totalOrders: number;
  activeOrders: number;
  todayProduction: number;
  defectRate: number;
  equipmentUtilization: number;
  pendingTransports: number;
  activeAlerts: number;
  completedToday: number;
}

// 생산 통계 (차트용)
export interface ProductionMetric {
  date: string;
  production: number;
  defects: number;
  defectRate: number;
}

// 적재 맵
export type StorageSlotStatus = "empty" | "occupied" | "reserved" | "working" | "unavailable";

export interface StorageSlot {
  id: string;
  row: number;
  col: number;
  status: StorageSlotStatus;
  productId?: string;
  productName?: string;
  quantity?: number;
  updatedAt: string;
}
