// API 클라이언트 — 백엔드 REST API 호출 + snake_case→camelCase 자동 변환
import type {
  DashboardStats,
  Alert,
  Equipment,
  Order,
  ProductionMetric,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API 오류: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  return convertKeys<T>(data);
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

export function fetchProductionMetrics(): Promise<ProductionMetric[]> {
  return apiFetch<ProductionMetric[]>("/api/production/metrics");
}
