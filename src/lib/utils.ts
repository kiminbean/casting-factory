import { clsx, type ClassValue } from "clsx";
import type { OrderStatus, ProcessStatus, EquipmentStatus, TransportStatus, AlertSeverity, StorageSlotStatus } from "./types";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export const orderStatusMap: Record<OrderStatus, { label: string; color: string }> = {
  pending: { label: "접수 대기", color: "bg-gray-100 text-gray-800" },
  reviewing: { label: "검토 중", color: "bg-blue-100 text-blue-800" },
  approved: { label: "승인됨", color: "bg-green-100 text-green-800" },
  in_production: { label: "생산 중", color: "bg-yellow-100 text-yellow-800" },
  shipping_ready: { label: "출하 준비", color: "bg-purple-100 text-purple-800" },
  completed: { label: "완료", color: "bg-emerald-100 text-emerald-800" },
  rejected: { label: "반려", color: "bg-red-100 text-red-800" },
};

export const processStatusMap: Record<ProcessStatus, { label: string; color: string; dot: string }> = {
  idle: { label: "대기", color: "text-gray-500", dot: "bg-gray-400" },
  running: { label: "진행 중", color: "text-blue-600", dot: "bg-blue-500 animate-pulse" },
  completed: { label: "완료", color: "text-green-600", dot: "bg-green-500" },
  error: { label: "오류", color: "text-red-600", dot: "bg-red-500 animate-pulse" },
  waiting: { label: "대기 중", color: "text-amber-600", dot: "bg-amber-500" },
};

export const equipmentStatusMap: Record<EquipmentStatus, { label: string; color: string }> = {
  idle: { label: "유휴", color: "bg-gray-100 text-gray-700" },
  running: { label: "가동 중", color: "bg-green-100 text-green-700" },
  error: { label: "오류", color: "bg-red-100 text-red-700" },
  maintenance: { label: "정비 중", color: "bg-yellow-100 text-yellow-700" },
  charging: { label: "충전 중", color: "bg-blue-100 text-blue-700" },
};

export const transportStatusMap: Record<TransportStatus, { label: string; color: string }> = {
  requested: { label: "요청됨", color: "bg-gray-100 text-gray-700" },
  assigned: { label: "배정됨", color: "bg-blue-100 text-blue-700" },
  moving_to_pickup: { label: "출발지 이동", color: "bg-indigo-100 text-indigo-700" },
  arrived_pickup: { label: "출발지 도착", color: "bg-cyan-100 text-cyan-700" },
  loading: { label: "적재 중", color: "bg-teal-100 text-teal-700" },
  moving_to_dest: { label: "도착지 이동", color: "bg-yellow-100 text-yellow-700" },
  arrived_dest: { label: "도착지 도착", color: "bg-lime-100 text-lime-700" },
  unloading: { label: "하역 중", color: "bg-orange-100 text-orange-700" },
  completed: { label: "완료", color: "bg-green-100 text-green-700" },
  failed: { label: "실패", color: "bg-red-100 text-red-700" },
};

export const alertSeverityMap: Record<AlertSeverity, { label: string; color: string; bg: string }> = {
  info: { label: "정보", color: "text-blue-600", bg: "bg-blue-50 border-blue-200" },
  warning: { label: "경고", color: "text-amber-600", bg: "bg-amber-50 border-amber-200" },
  critical: { label: "긴급", color: "text-red-600", bg: "bg-red-50 border-red-200" },
};

export const storageSlotColorMap: Record<StorageSlotStatus, string> = {
  empty: "bg-gray-100 border-gray-300",
  occupied: "bg-blue-200 border-blue-400",
  reserved: "bg-amber-200 border-amber-400",
  working: "bg-green-200 border-green-400",
  unavailable: "bg-red-200 border-red-400",
};

export function formatDate(dateStr: string): string {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return d.toLocaleDateString("ko-KR", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("ko-KR", { style: "currency", currency: "KRW" }).format(amount);
}
