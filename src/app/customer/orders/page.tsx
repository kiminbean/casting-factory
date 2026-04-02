"use client";

import { useState, useMemo } from "react";
import {
  Factory,
  CheckCircle,
  Package,
  Search,
  Clock,
  Bell,
  ClipboardList,
  Eye,
  ArrowLeft,
  X,
  Truck,
  ShieldCheck,
  PackageCheck,
} from "lucide-react";
import { mockOrders, mockOrderDetails } from "@/lib/mock-data";
import { orderStatusMap, formatDate, formatCurrency as formatKRW } from "@/lib/utils";
import type { Order, OrderDetail, OrderStatus } from "@/lib/types";

// ─────────────────────────────────────────────
// 6단계 상태 파이프라인 (rejected 제외)
// ─────────────────────────────────────────────

const ORDER_STATUS_PIPELINE: OrderStatus[] = [
  "pending",
  "reviewing",
  "approved",
  "in_production",
  "shipping_ready",
  "completed",
];

const STATUS_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  pending: ClipboardList,
  reviewing: Search,
  approved: ShieldCheck,
  in_production: Factory,
  shipping_ready: Truck,
  completed: PackageCheck,
};

// ─────────────────────────────────────────────
// Status Timeline Component
// ─────────────────────────────────────────────

function OrderStatusTimeline({ status }: { status: OrderStatus }) {
  const currentIndex = ORDER_STATUS_PIPELINE.indexOf(status);

  return (
    <div className="flex items-center justify-between w-full">
      {ORDER_STATUS_PIPELINE.map((s, index) => {
        const Icon = STATUS_ICONS[s] ?? Clock;
        const info = orderStatusMap[s];
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;

        return (
          <div key={s} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm transition-all ${
                  isCompleted
                    ? "bg-blue-600 text-white"
                    : isCurrent
                    ? "bg-blue-600 text-white ring-4 ring-blue-100"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>
              <span
                className={`mt-1.5 text-[10px] font-medium whitespace-nowrap ${
                  isCurrent
                    ? "text-blue-600"
                    : isCompleted
                    ? "text-gray-600"
                    : "text-gray-400"
                }`}
              >
                {info.label}
              </span>
            </div>
            {index < ORDER_STATUS_PIPELINE.length - 1 && (
              <div
                className={`flex-1 h-0.5 mx-1 mb-5 transition-all ${
                  index < currentIndex ? "bg-blue-600" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─────────────────────────────────────────────
// Order Detail Panel
// ─────────────────────────────────────────────

function OrderDetailPanel({
  order,
  details,
  onBack,
}: {
  order: Order;
  details: OrderDetail[];
  onBack: () => void;
}) {
  const info = orderStatusMap[order.status];

  // 시뮬레이션: 최근 상태 변경 알림 (updatedAt이 3일 이내)
  const updatedDate = new Date(order.updatedAt);
  const now = new Date();
  const daysDiff = (now.getTime() - updatedDate.getTime()) / (1000 * 60 * 60 * 24);
  const recentlyChanged = daysDiff <= 3;

  return (
    <div>
      {/* 상태 변경 알림 배너 */}
      {recentlyChanged && (
        <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 mb-5">
          <Bell className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-800">상태 변경 알림</p>
            <p className="text-xs text-blue-600 mt-0.5">
              주문 상태가 &quot;{info.label}&quot;(으)로 변경되었습니다. ({formatDate(order.updatedAt)})
            </p>
          </div>
        </div>
      )}

      {/* 뒤로 가기 */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 mb-4 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        목록으로 돌아가기
      </button>

      {/* 주문 기본 정보 */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-gray-900">{order.id}</h3>
          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${info.color}`}>
            {info.label}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-gray-500">회사명</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.companyName}</p>
          </div>
          <div>
            <span className="text-gray-500">담당자</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.customerName}</p>
          </div>
          <div>
            <span className="text-gray-500">연락처</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.contact}</p>
          </div>
          <div>
            <span className="text-gray-500">이메일</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.contact?.includes("@") ? order.contact : "-"}</p>
          </div>
          <div>
            <span className="text-gray-500">주문일</span>
            <p className="font-medium text-gray-900 mt-0.5">{formatDate(order.createdAt)}</p>
          </div>
          <div>
            <span className="text-gray-500">요청 납기</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.requestedDelivery || "-"}</p>
          </div>
          <div>
            <span className="text-gray-500">확정 납기</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.confirmedDelivery || "-"}</p>
          </div>
          <div>
            <span className="text-gray-500">배송지</span>
            <p className="font-medium text-gray-900 mt-0.5">{order.shippingAddress || "-"}</p>
          </div>
          <div>
            <span className="text-gray-500">예상 금액</span>
            <p className="font-medium text-blue-600 mt-0.5">{formatKRW(order.totalAmount)}</p>
          </div>
        </div>
        {order.notes && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <span className="text-gray-500 text-sm">비고</span>
            <p className="text-sm text-gray-700 mt-0.5">{order.notes}</p>
          </div>
        )}
      </div>

      {/* 상태 타임라인 */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-blue-600" />
          진행 상태
        </h3>
        <OrderStatusTimeline status={order.status} />
      </div>

      {/* 주문 상세 (제품 정보) */}
      {details.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Package className="w-4 h-4 text-blue-600" />
            주문 상세
          </h3>
          <div className="space-y-3">
            {details.map((d) => (
              <div key={d.id} className="border border-gray-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-semibold text-gray-900">{d.productName}</p>
                  <p className="text-sm font-bold text-blue-600">{formatKRW(d.subtotal)}</p>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-gray-600">
                  <div>
                    <span className="text-gray-400">규격</span>
                    <p className="mt-0.5">{d.spec}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">재질</span>
                    <p className="mt-0.5">{d.material}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">후처리</span>
                    <p className="mt-0.5">{d.postProcessing || "-"}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">수량</span>
                    <p className="mt-0.5">{d.quantity.toLocaleString()}개</p>
                  </div>
                  <div>
                    <span className="text-gray-400">단가</span>
                    <p className="mt-0.5">{formatKRW(d.unitPrice)}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">로고/문구</span>
                    <p className="mt-0.5">{d.logoData || "-"}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-4 pt-3 border-t border-gray-200 text-sm">
            <span className="font-medium text-gray-700">합계</span>
            <span className="font-bold text-blue-600">{formatKRW(order.totalAmount)}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Page Component
// ─────────────────────────────────────────────

export default function CustomerOrdersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  // 주문번호 또는 연락처로 검색
  const filteredOrders = useMemo(() => {
    if (!searchQuery.trim()) return mockOrders;
    const q = searchQuery.trim().toLowerCase();
    return mockOrders.filter(
      (order) =>
        order.id.toLowerCase().includes(q) ||
        order.contact.includes(q) ||
        order.companyName.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  // 선택한 주문의 상세 정보
  const selectedDetails = useMemo(() => {
    if (!selectedOrder) return [];
    return mockOrderDetails.filter((d) => d.orderId === selectedOrder.id);
  }, [selectedOrder]);

  // 주문 상세 보기
  if (selectedOrder) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sm:p-8">
          <OrderDetailPanel
            order={selectedOrder}
            details={selectedDetails}
            onBack={() => setSelectedOrder(null)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-gray-900 mb-2">주문 조회</h2>
        <p className="text-sm text-gray-500 mb-6">
          주문번호, 연락처 또는 회사명으로 주문 현황을 조회할 수 있습니다.
        </p>

        {/* 검색 입력 */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="주문번호 (예: ORD-2026-001) 또는 연락처, 회사명"
            className="w-full rounded-lg border border-gray-300 pl-10 pr-10 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* 검색 결과 */}
        {filteredOrders.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">검색 결과가 없습니다.</p>
            <p className="text-xs text-gray-400 mt-1">주문번호, 연락처 또는 회사명을 확인해 주세요.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredOrders.map((order) => {
              const info = orderStatusMap[order.status];
              return (
                <button
                  key={order.id}
                  onClick={() => setSelectedOrder(order)}
                  className="w-full text-left bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition-all group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-bold text-gray-900">{order.id}</span>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium ${info.color}`}>
                        {info.label}
                      </span>
                    </div>
                    <Eye className="w-4 h-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{order.companyName}</span>
                    <span>{order.customerName}</span>
                    <span>{formatDate(order.createdAt)}</span>
                    <span className="ml-auto font-medium text-gray-700">
                      예상 {formatKRW(order.totalAmount)}
                    </span>
                  </div>
                  {/* 미니 타임라인 */}
                  <div className="mt-3">
                    <OrderStatusTimeline status={order.status} />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
