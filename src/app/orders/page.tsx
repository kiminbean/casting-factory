"use client";

import { useState } from "react";
import {
  Package,
  Clock,
  Factory,
  CheckCircle,
  Search,
  FileText,
  User,
  MapPin,
  Phone,
  CalendarDays,
  Calculator,
  Truck,
  ThumbsUp,
  ThumbsDown,
  ChevronRight,
  StickyNote,
  Layers,
} from "lucide-react";
import { mockOrders, mockOrderDetails } from "@/lib/mock-data";
import { orderStatusMap, formatDate, formatCurrency, cn } from "@/lib/utils";
import type { Order, OrderStatus, OrderDetail } from "@/lib/types";

// ────────────────────────────────────────
// 상태 탭 정의
// ────────────────────────────────────────

interface StatusTab {
  key: OrderStatus | "all";
  label: string;
  icon: React.ReactNode;
}

const STATUS_TABS: StatusTab[] = [
  { key: "all", label: "전체", icon: <Package size={15} /> },
  { key: "pending", label: "신규 주문", icon: <Clock size={15} /> },
  { key: "reviewing", label: "검토 중", icon: <Search size={15} /> },
  { key: "approved", label: "승인", icon: <ThumbsUp size={15} /> },
  { key: "in_production", label: "생산 중", icon: <Factory size={15} /> },
  { key: "completed", label: "완료", icon: <CheckCircle size={15} /> },
];

// ────────────────────────────────────────
// 견적/납기 계산 유틸
// ────────────────────────────────────────

function calcEstimatedDays(details: OrderDetail[]): number {
  // 수량 기반 생산 일수 추정: 기본 3일 + 50개당 1일
  const totalQty = details.reduce((sum, d) => sum + d.quantity, 0);
  return 3 + Math.ceil(totalQty / 50);
}

function calcEstimatedDelivery(order: Order, details: OrderDetail[]): string {
  const days = calcEstimatedDays(details);
  const base = new Date(order.createdAt);
  base.setDate(base.getDate() + days);
  return base.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

// ────────────────────────────────────────
// 주문 카드 컴포넌트
// ────────────────────────────────────────

interface OrderCardProps {
  order: Order;
  isSelected: boolean;
  onClick: () => void;
}

function OrderCard({ order, isSelected, onClick }: OrderCardProps) {
  const statusInfo = orderStatusMap[order.status];
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full text-left px-4 py-3 border-b border-gray-100 transition-colors",
        isSelected
          ? "bg-blue-50 border-l-4 border-l-blue-500"
          : "hover:bg-gray-50 border-l-4 border-l-transparent"
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-mono text-gray-400">{order.id}</span>
        <span
          className={cn(
            "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium",
            statusInfo.color
          )}
        >
          {statusInfo.label}
        </span>
      </div>
      <p className="text-sm font-semibold text-gray-900 truncate">
        {order.companyName}
      </p>
      <div className="flex items-center justify-between mt-1.5">
        <span className="text-xs text-gray-500">
          {formatDate(order.createdAt)}
        </span>
        <span className="text-sm font-bold text-gray-800">
          {formatCurrency(order.totalAmount)}
        </span>
      </div>
    </button>
  );
}

// ────────────────────────────────────────
// 주문 상세 패널 컴포넌트
// ────────────────────────────────────────

interface OrderDetailPanelProps {
  order: Order;
  details: OrderDetail[];
}

function OrderDetailPanel({ order, details }: OrderDetailPanelProps) {
  const statusInfo = orderStatusMap[order.status];
  const estimatedDays = calcEstimatedDays(details);
  const estimatedDelivery = calcEstimatedDelivery(order, details);

  return (
    <div className="flex-1 overflow-y-auto">
      {/* 상단 헤더 */}
      <div className="px-6 py-5 border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900">{order.id}</h2>
            <p className="text-sm text-gray-500 mt-0.5">{order.companyName}</p>
          </div>
          <span
            className={cn(
              "inline-flex items-center px-3 py-1.5 rounded-full text-sm font-semibold",
              statusInfo.color
            )}
          >
            {statusInfo.label}
          </span>
        </div>
      </div>

      <div className="px-6 py-5 space-y-6">
        {/* 제품 상세 */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
            <Layers size={16} className="text-gray-400" />
            제품 상세
          </h3>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500">
                    제품명
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500">
                    규격
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500">
                    재질
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500">
                    수량
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500">
                    단가
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500">
                    소계
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {details.map((d) => (
                  <tr key={d.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900 font-medium">
                      {d.productName}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {d.spec}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {d.material}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">
                      {d.quantity.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 text-right">
                      {formatCurrency(d.unitPrice)}
                    </td>
                    <td className="px-4 py-3 text-sm font-semibold text-gray-900 text-right">
                      {formatCurrency(d.subtotal)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-gray-50">
                  <td
                    colSpan={5}
                    className="px-4 py-3 text-sm font-semibold text-gray-700 text-right"
                  >
                    합계
                  </td>
                  <td className="px-4 py-3 text-sm font-bold text-blue-700 text-right">
                    {formatCurrency(order.totalAmount)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

          {/* 후처리 / 로고 정보 */}
          {details.some((d) => d.postProcessing || d.logoData) && (
            <div className="mt-3 space-y-2">
              {details.map((d) => (
                <div
                  key={d.id}
                  className="text-xs text-gray-500 bg-gray-50 rounded-md px-3 py-2"
                >
                  <span className="font-medium text-gray-700">
                    {d.productName}
                  </span>
                  {d.postProcessing && (
                    <span className="ml-2">
                      후처리: <span className="text-gray-700">{d.postProcessing}</span>
                    </span>
                  )}
                  {d.logoData && (
                    <span className="ml-2">
                      로고: <span className="text-gray-700">{d.logoData}</span>
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* 견적/납기 계산기 */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
            <Calculator size={16} className="text-gray-400" />
            견적 / 납기 계산
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
              <p className="text-xs text-blue-600 font-medium mb-1">총 견적 금액</p>
              <p className="text-xl font-bold text-blue-800">
                {formatCurrency(order.totalAmount)}
              </p>
              <p className="text-[11px] text-blue-500 mt-1">
                {details.reduce((s, d) => s + d.quantity, 0)}개 제품 기준
              </p>
            </div>
            <div className="bg-amber-50 border border-amber-100 rounded-lg p-4">
              <p className="text-xs text-amber-600 font-medium mb-1">
                예상 생산 기간
              </p>
              <p className="text-xl font-bold text-amber-800">
                {estimatedDays}일
              </p>
              <p className="text-[11px] text-amber-500 mt-1">
                예상 완료: {estimatedDelivery}
              </p>
            </div>
            <div className="bg-green-50 border border-green-100 rounded-lg p-4">
              <div className="flex items-center gap-1.5 mb-1">
                <CalendarDays size={13} className="text-green-600" />
                <p className="text-xs text-green-600 font-medium">요청 납기</p>
              </div>
              <p className="text-sm font-semibold text-green-800">
                {order.requestedDelivery || "-"}
              </p>
            </div>
            <div className="bg-purple-50 border border-purple-100 rounded-lg p-4">
              <div className="flex items-center gap-1.5 mb-1">
                <Truck size={13} className="text-purple-600" />
                <p className="text-xs text-purple-600 font-medium">확정 납기</p>
              </div>
              <p className="text-sm font-semibold text-purple-800">
                {order.confirmedDelivery || "미정"}
              </p>
            </div>
          </div>
        </section>

        {/* 고객 정보 */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
            <User size={16} className="text-gray-400" />
            고객 정보
          </h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
            <div className="flex items-start gap-3">
              <User size={15} className="text-gray-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-gray-500">담당자</p>
                <p className="text-sm font-medium text-gray-900">
                  {order.customerName}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Phone size={15} className="text-gray-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-gray-500">연락처</p>
                <p className="text-sm font-medium text-gray-900">
                  {order.contact}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <MapPin size={15} className="text-gray-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-gray-500">배송 주소</p>
                <p className="text-sm font-medium text-gray-900">
                  {order.shippingAddress}
                </p>
              </div>
            </div>
            {order.notes && (
              <div className="flex items-start gap-3">
                <StickyNote
                  size={15}
                  className="text-gray-400 mt-0.5 shrink-0"
                />
                <div>
                  <p className="text-xs text-gray-500">비고</p>
                  <p className="text-sm text-gray-700 bg-gray-50 rounded-md p-2 mt-1">
                    {order.notes}
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* 주문 이력 */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
            <FileText size={16} className="text-gray-400" />
            주문 이력
          </h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
                <span className="text-gray-500 w-32 shrink-0">
                  {formatDate(order.createdAt)}
                </span>
                <span className="text-gray-900">주문 접수</span>
              </div>
              {order.status !== "pending" && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-yellow-500 shrink-0" />
                  <span className="text-gray-500 w-32 shrink-0">
                    {formatDate(order.updatedAt)}
                  </span>
                  <span className="text-gray-900">
                    상태 변경:{" "}
                    <span className="font-medium">{statusInfo.label}</span>
                  </span>
                </div>
              )}
              {order.confirmedDelivery && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                  <span className="text-gray-500 w-32 shrink-0">
                    {formatDate(order.updatedAt)}
                  </span>
                  <span className="text-gray-900">
                    납기 확정: {order.confirmedDelivery}
                  </span>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>

      {/* 하단 액션 버튼 */}
      {(order.status === "pending" ||
        order.status === "reviewing" ||
        order.status === "approved") && (
        <div className="px-6 py-4 border-t border-gray-200 bg-white sticky bottom-0">
          <div className="flex gap-3">
            {(order.status === "pending" || order.status === "reviewing") && (
              <>
                <button
                  type="button"
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  <ThumbsUp size={16} />
                  승인
                </button>
                <button
                  type="button"
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  <ThumbsDown size={16} />
                  반려
                </button>
              </>
            )}
            {order.status === "approved" && (
              <button
                type="button"
                className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Factory size={16} />
                생산 시작
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ────────────────────────────────────────
// 메인 페이지
// ────────────────────────────────────────

export default function OrdersPage() {
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [activeTab, setActiveTab] = useState<OrderStatus | "all">("all");

  // 탭 필터
  const filteredOrders =
    activeTab === "all"
      ? mockOrders
      : mockOrders.filter((o) => o.status === activeTab);

  // 선택된 주문의 상세 정보
  const selectedDetails = selectedOrder
    ? mockOrderDetails.filter((d) => d.orderId === selectedOrder.id)
    : [];

  // 탭별 카운트
  const tabCounts: Record<string, number> = {
    all: mockOrders.length,
  };
  for (const tab of STATUS_TABS) {
    if (tab.key !== "all") {
      tabCounts[tab.key] = mockOrders.filter(
        (o) => o.status === tab.key
      ).length;
    }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* 페이지 헤더 */}
      <div className="px-6 py-4 bg-white border-b border-gray-200 shrink-0">
        <h1 className="text-xl font-bold text-gray-900">주문 관리</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          전체 주문 현황을 확인하고 관리합니다.
        </p>
      </div>

      {/* 메인 콘텐츠 영역 (좌측 목록 + 우측 상세) */}
      <div className="flex-1 flex overflow-hidden">
        {/* ── 좌측: 주문 목록 ── */}
        <div className="w-[380px] shrink-0 border-r border-gray-200 bg-white flex flex-col">
          {/* 상태 탭 */}
          <div className="px-3 pt-3 pb-2 border-b border-gray-100 shrink-0">
            <div className="flex flex-wrap gap-1.5">
              {STATUS_TABS.map((tab) => {
                const isActive = activeTab === tab.key;
                const count = tabCounts[tab.key] || 0;
                return (
                  <button
                    key={tab.key}
                    type="button"
                    onClick={() => {
                      setActiveTab(tab.key);
                      setSelectedOrder(null);
                    }}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors",
                      isActive
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    )}
                  >
                    {tab.icon}
                    {tab.label}
                    <span
                      className={cn(
                        "ml-0.5 px-1.5 py-0.5 rounded-full text-[10px]",
                        isActive
                          ? "bg-blue-500 text-white"
                          : "bg-gray-200 text-gray-500"
                      )}
                    >
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 주문 카드 목록 */}
          <div className="flex-1 overflow-y-auto">
            {filteredOrders.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Package size={40} strokeWidth={1.5} />
                <p className="mt-2 text-sm">해당 상태의 주문이 없습니다.</p>
              </div>
            ) : (
              filteredOrders.map((order) => (
                <OrderCard
                  key={order.id}
                  order={order}
                  isSelected={selectedOrder?.id === order.id}
                  onClick={() => setSelectedOrder(order)}
                />
              ))
            )}
          </div>

          {/* 목록 푸터 */}
          <div className="px-4 py-2.5 border-t border-gray-100 bg-gray-50 shrink-0">
            <p className="text-xs text-gray-500">
              총 {filteredOrders.length}건
              {activeTab !== "all" && ` / 전체 ${mockOrders.length}건`}
            </p>
          </div>
        </div>

        {/* ── 우측: 주문 상세 ── */}
        <div className="flex-1 bg-gray-50 flex flex-col">
          {selectedOrder ? (
            <OrderDetailPanel
              order={selectedOrder}
              details={selectedDetails}
            />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
              <ChevronRight size={48} strokeWidth={1.5} />
              <p className="mt-3 text-sm">좌측 목록에서 주문을 선택하세요.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
