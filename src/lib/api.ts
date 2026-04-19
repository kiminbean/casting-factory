// API 클라이언트 — 백엔드 REST API 호출 + snake_case→camelCase 자동 변환
import type {
  DashboardStats,
  Alert,
  Equipment,
  Order,
  OrderDetail,
  ProductionMetric,
  ProcessStageData,
  InspectionRecord,
  InspectionStandard,
  SorterLog,
  TransportTask,
  WarehouseRack,
  OutboundOrder,
  OrderStatus,
  PriorityResult,
  ProductionJob,
  PriorityChangeLog,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "";

// snake_case → camelCase 재귀 변환
function toCamelCase(str: string): string {
  return str.replace(/_([a-z0-9])/g, (_, c) => c.toUpperCase());
}

function convertKeys<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeys(item)) as T;
  }
  if (obj !== null && typeof obj === "object") {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      result[toCamelCase(key)] = convertKeys(value);
    }
    return result as T;
  }
  return obj as T;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    throw new Error(`API 오류: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  return convertKeys<T>(data);
}

async function apiPatch<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return apiFetch<T>(path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// ── API 함수 ──

export function fetchDashboardStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/api/dashboard/stats");
}

export function fetchAlerts(): Promise<Alert[]> {
  return apiFetch<Alert[]>("/api/alerts");
}

export function fetchEquipment(): Promise<Equipment[]> {
  return apiFetch<Equipment[]>("/api/production/equipment");
}

export function fetchOrders(): Promise<Order[]> {
  return apiFetch<Order[]>("/api/orders");
}

/** 특정 이메일로 접수된 주문만 반환. /customer/lookup 흐름에서 사용.
 *  smartcast schema: GET /api/orders/lookup?email=... — 결과 없으면 빈 배열.
 */
export function fetchOrdersByEmail(email: string): Promise<Order[]> {
  return apiFetch<Order[]>(`/api/orders/lookup?email=${encodeURIComponent(email)}`);
}

export function fetchProductionMetrics(): Promise<ProductionMetric[]> {
  return apiFetch<ProductionMetric[]>("/api/production/metrics");
}

// ── 생산 모니터링 ──

export function fetchProcessStages(): Promise<ProcessStageData[]> {
  return apiFetch<ProcessStageData[]>("/api/production/stages");
}

// ── 품질 검사 ──

export function fetchInspections(): Promise<InspectionRecord[]> {
  return apiFetch<InspectionRecord[]>("/api/quality/inspections");
}

export function fetchQualityStats(): Promise<{
  total: number;
  passed: number;
  failed: number;
  defectRate: number;
  defectTypes: Record<string, number>;
  defectTypeCodes: Record<string, number> | null;
  inspectorStats: Record<string, { total: number; passed: number; failed: number }> | null;
}> {
  return apiFetch("/api/quality/stats");
}

export function fetchInspectionStandards(): Promise<InspectionStandard[]> {
  return apiFetch<InspectionStandard[]>("/api/quality/standards");
}

export function fetchSorterLogs(): Promise<SorterLog[]> {
  return apiFetch<SorterLog[]>("/api/quality/sorter-logs");
}

// ── 물류/이송 ──

export function fetchTransportTasks(): Promise<TransportTask[]> {
  return apiFetch<TransportTask[]>("/api/logistics/tasks");
}

export function fetchWarehouseRacks(): Promise<WarehouseRack[]> {
  return apiFetch<WarehouseRack[]>("/api/logistics/warehouse");
}

export function fetchOutboundOrders(): Promise<OutboundOrder[]> {
  return apiFetch<OutboundOrder[]>("/api/logistics/outbound-orders");
}

// ── 주문 상세/관리 ──

export function fetchOrderDetails(orderId: string): Promise<OrderDetail[]> {
  return apiFetch<OrderDetail[]>(`/api/orders/${orderId}/details`);
}

export function updateOrderStatus(
  orderId: string,
  status: OrderStatus,
): Promise<Order> {
  return apiPatch<Order>(`/api/orders/${orderId}/status`, { status });
}

export function updateOrder(
  orderId: string,
  data: { total_amount?: number; confirmed_delivery?: string },
): Promise<Order> {
  return apiPatch<Order>(`/api/orders/${orderId}`, data);
}

// ── 생산 스케줄링 ──

export function calculatePriority(
  orderIds: string[],
): Promise<{ results: PriorityResult[] }> {
  return apiFetch("/api/production/schedule/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_ids: orderIds }),
  });
}

export function startProduction(
  orderIds: string[],
): Promise<ProductionJob[]> {
  return apiFetch("/api/production/schedule/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_ids: orderIds }),
  });
}

export function fetchProductionJobs(): Promise<ProductionJob[]> {
  return apiFetch<ProductionJob[]>("/api/production/schedule/jobs");
}

export function createPriorityLog(data: {
  order_id: string;
  old_rank: number;
  new_rank: number;
  reason: string;
}): Promise<PriorityChangeLog> {
  return apiFetch("/api/production/schedule/priority-log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
