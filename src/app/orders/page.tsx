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
  ClipboardList,
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
        "w-full text-left px-4 py-3.5 border-b border-gray-100 transition-all duration-200",
        isSelected
          ? "bg-blue-50 border-l-4 border-l-blue-500 ring-2 ring-blue-500 ring-inset"
          : "hover:bg-blue-50/50 border-l-4 border-l-transparent"
      )}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm font-mono text-gray-400">{order.id}</span>
        <span
          className={cn(
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-semibold",
            statusInfo.color
          )}
        >
          {statusInfo.label}
        </span>
      </div>
      <p className="text-base font-semibold text-gray-900 truncate">
        {order.companyName}
      </p>
      <div className="flex items-center justify-between mt-2">
        <span className="text-sm text-gray-500">
          {formatDate(order.createdAt)}
        </span>
        <span className="text-base font-bold text-gray-800">
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
            <h2 className="text-xl font-bold text-gray-900">{order.id}</h2>
            <p className="text-base text-gray-500 mt-0.5">{order.companyName}</p>
          </div>
          <span
            className={cn(
              "inline-flex items-center px-3 py-1.5 rounded-full text-base font-semibold",
              statusInfo.color
            )}
          >
            {statusInfo.label}
          </span>
        </div>
      </div>

      <div className="px-6 py-5 space-y-6">
        {/* 제품 상세 */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="flex items-center gap-2 text-xl font-bold text-gray-900 mb-4">
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
              <Layers size={16} className="text-blue-600" />
            </div>
            제품 상세
          </h3>
          <div className="rounded-lg overflow-hidden border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    제품명
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    규격
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    재질
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    수량
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    단가
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    소계
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {details.map((d) => (
                  <tr key={d.id} className="even:bg-gray-50 hover:bg-blue-50 transition-colors">
                    <td className="px-4 py-3 text-base text-gray-900 font-medium">
                      {d.productName}
                    </td>
                    <td className="px-4 py-3 text-base text-gray-600">
                      {d.spec}
                    </td>
                    <td className="px-4 py-3 text-base text-gray-600">
                      {d.material}
                    </td>
                    <td className="px-4 py-3 text-base text-gray-900 text-right">
                      {d.quantity.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-base text-gray-600 text-right">
                      {formatCurrency(d.unitPrice)}
                    </td>
                    <td className="px-4 py-3 text-base font-semibold text-gray-900 text-right">
                      {formatCurrency(d.subtotal)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-gray-100">
                  <td
                    colSpan={5}
                    className="px-4 py-3 text-base font-semibold text-gray-700 text-right"
                  >
                    합계
                  </td>
                  <td className="px-4 py-3 text-base font-bold text-blue-700 text-right">
                    {formatCurrency(order.totalAmount)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

          {/* 후처리 / 로고 정보 */}
          {details.some((d) => d.postProcessing || d.logoData) && (
            <div className="mt-4 space-y-2">
              {details.map((d) => (
                <div
                  key={d.id}
                  className="text-sm text-gray-500 bg-gray-50 rounded-lg px-3 py-2.5 border border-gray-100"
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
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="flex items-center gap-2 text-xl font-bold text-gray-900 mb-4">
            <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center">
              <Calculator size={16} className="text-amber-600" />
            </div>
            견적 / 납기 계산
          </h3>
          <div className="grid grid-cols-2 gap-5">
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">
              <p className="text-sm text-blue-600 font-semibold mb-1">총 견적 금액</p>
              <p className="text-2xl font-bold text-blue-800">
                {formatCurrency(order.totalAmount)}
              </p>
              <p className="text-[11px] text-blue-500 mt-1.5">
                {details.reduce((s, d) => s + d.quantity, 0)}개 제품 기준
              </p>
            </div>
            <div className="bg-amber-50 border border-amber-100 rounded-xl p-5">
              <p className="text-sm text-amber-600 font-semibold mb-1">
                예상 생산 기간
              </p>
              <p className="text-2xl font-bold text-amber-800">
                {estimatedDays}일
              </p>
              <p className="text-[11px] text-amber-500 mt-1.5">
                예상 완료: {estimatedDelivery}
              </p>
            </div>
            <div className="bg-green-50 border border-green-100 rounded-xl p-5">
              <div className="flex items-center gap-1.5 mb-1">
                <CalendarDays size={13} className="text-green-600" />
                <p className="text-sm text-green-600 font-semibold">요청 납기</p>
              </div>
              <p className="text-base font-semibold text-green-800">
                {order.requestedDelivery || "-"}
              </p>
            </div>
            <div className="bg-purple-50 border border-purple-100 rounded-xl p-5">
              <div className="flex items-center gap-1.5 mb-1">
                <Truck size={13} className="text-purple-600" />
                <p className="text-sm text-purple-600 font-semibold">확정 납기</p>
              </div>
              <p className="text-base font-semibold text-purple-800">
                {order.confirmedDelivery || "미정"}
              </p>
            </div>
          </div>
        </section>

        {/* 고객 정보 */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="flex items-center gap-2 text-xl font-bold text-gray-900 mb-4">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center">
              <User size={16} className="text-indigo-600" />
            </div>
            고객 정보
          </h3>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0">
                <User size={14} className="text-gray-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500">담당자</p>
                <p className="text-base font-medium text-gray-900">
                  {order.customerName}
                </p>
              </div>
            </div>
            <div className="border-t border-gray-100" />
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0">
                <Phone size={14} className="text-gray-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500">연락처</p>
                <p className="text-base font-medium text-gray-900">
                  {order.contact}
                </p>
              </div>
            </div>
            <div className="border-t border-gray-100" />
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0">
                <MapPin size={14} className="text-gray-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500">배송 주소</p>
                <p className="text-base font-medium text-gray-900">
                  {order.shippingAddress}
                </p>
              </div>
            </div>
            {order.notes && (
              <>
                <div className="border-t border-gray-100" />
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0">
                    <StickyNote size={14} className="text-gray-500" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">비고</p>
                    <p className="text-base text-gray-700 bg-gray-50 rounded-lg p-2.5 mt-1 border border-gray-100">
                      {order.notes}
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </section>

        {/* 주문 이력 */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="flex items-center gap-2 text-xl font-bold text-gray-900 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center">
              <FileText size={16} className="text-gray-600" />
            </div>
            주문 이력
          </h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3 text-base">
              <div className="w-3 h-3 rounded-full bg-blue-500 shrink-0 ring-4 ring-blue-100" />
              <span className="text-gray-500 w-32 shrink-0">
                {formatDate(order.createdAt)}
              </span>
              <span className="text-gray-900 font-medium">주문 접수</span>
            </div>
            {order.status !== "pending" && (
              <div className="flex items-center gap-3 text-base">
                <div className="w-3 h-3 rounded-full bg-yellow-500 shrink-0 ring-4 ring-yellow-100" />
                <span className="text-gray-500 w-32 shrink-0">
                  {formatDate(order.updatedAt)}
                </span>
                <span className="text-gray-900">
                  상태 변경:{" "}
                  <span className="font-semibold">{statusInfo.label}</span>
                </span>
              </div>
            )}
            {order.confirmedDelivery && (
              <div className="flex items-center gap-3 text-base">
                <div className="w-3 h-3 rounded-full bg-green-500 shrink-0 ring-4 ring-green-100" />
                <span className="text-gray-500 w-32 shrink-0">
                  {formatDate(order.updatedAt)}
                </span>
                <span className="text-gray-900">
                  납기 확정: <span className="font-semibold">{order.confirmedDelivery}</span>
                </span>
              </div>
            )}
          </div>
        </section>
      </div>

      {/* 하단 액션 버튼 */}
      {(order.status === "pending" ||
        order.status === "reviewing" ||
        order.status === "approved") && (
        <div className="px-6 py-4 border-t border-gray-200 bg-white sticky bottom-0 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
          <div className="flex gap-3">
            {(order.status === "pending" || order.status === "reviewing") && (
              <>
                <button
                  type="button"
                  className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-green-600 text-white rounded-lg font-semibold text-base hover:bg-green-700 transition-colors shadow-sm"
                >
                  <ThumbsUp size={16} />
                  승인
                </button>
                <button
                  type="button"
                  className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-red-600 text-white rounded-lg font-semibold text-base hover:bg-red-700 transition-colors shadow-sm"
                >
                  <ThumbsDown size={16} />
                  반려
                </button>
              </>
            )}
            {order.status === "approved" && (
              <button
                type="button"
                className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-blue-600 text-white rounded-lg font-semibold text-base hover:bg-blue-700 transition-colors shadow-sm"
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
      <div className="px-6 py-5 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
            <ClipboardList className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">주문 관리</h1>
            <p className="text-base text-gray-500 mt-0.5">
              전체 주문 현황을 확인하고 관리합니다.
            </p>
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 영역 (좌측 목록 + 우측 상세) */}
      <div className="flex-1 flex overflow-hidden">
        {/* -- 좌측: 주문 목록 -- */}
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
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold transition-colors",
                      isActive
                        ? "bg-blue-600 text-white shadow-sm"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    )}
                  >
                    {tab.icon}
                    {tab.label}
                    <span
                      className={cn(
                        "ml-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold",
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
                <p className="mt-2 text-base">해당 상태의 주문이 없습니다.</p>
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
            <p className="text-sm text-gray-500 font-medium">
              총 {filteredOrders.length}건
              {activeTab !== "all" && ` / 전체 ${mockOrders.length}건`}
            </p>
          </div>
        </div>

        {/* -- 우측: 주문 상세 -- */}
        <div className="flex-1 bg-gray-50 flex flex-col">
          {selectedOrder ? (
            <OrderDetailPanel
              order={selectedOrder}
              details={selectedDetails}
            />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
              <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mb-3">
                <ChevronRight size={32} strokeWidth={1.5} className="text-gray-300" />
              </div>
              <p className="text-base text-gray-500">좌측 목록에서 주문을 선택하세요.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
