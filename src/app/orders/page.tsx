"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  X,
  Package,
  Clock,
  Factory,
  CheckCircle,
} from "lucide-react";
import { mockOrders } from "@/lib/mock-data";
import { orderStatusMap, formatDate, formatCurrency } from "@/lib/utils";
import type { Order } from "@/lib/types";

// 통계 카드 컴포넌트
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  colorClass: string;
}

function StatCard({ title, value, icon, colorClass }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 flex items-center gap-4">
      <div className={`p-3 rounded-full ${colorClass}`}>{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  );
}

// 주문 상세 패널 컴포넌트
interface OrderDetailPanelProps {
  order: Order;
  onClose: () => void;
}

function OrderDetailPanel({ order, onClose }: OrderDetailPanelProps) {
  const statusInfo = orderStatusMap[order.status];

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* 배경 오버레이 */}
      <div
        className="absolute inset-0 bg-black/30"
        onClick={onClose}
        aria-label="닫기"
      />

      {/* 슬라이드 패널 */}
      <div className="relative z-10 bg-white w-full max-w-lg h-full shadow-xl overflow-y-auto flex flex-col">
        {/* 패널 헤더 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10">
          <h2 className="text-lg font-semibold text-gray-900">
            주문 상세 - {order.id}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="패널 닫기"
          >
            <X size={20} />
          </button>
        </div>

        {/* 패널 본문 */}
        <div className="flex-1 px-6 py-5 space-y-6">
          {/* 상태 배지 */}
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusInfo.color}`}
            >
              {statusInfo.label}
            </span>
          </div>

          {/* 기본 정보 */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-100">
              기본 정보
            </h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              <div>
                <dt className="text-gray-500">주문번호</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.id}</dd>
              </div>
              <div>
                <dt className="text-gray-500">고객사</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.companyName}</dd>
              </div>
              <div>
                <dt className="text-gray-500">담당자</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.customerName}</dd>
              </div>
              <div>
                <dt className="text-gray-500">주문일</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{formatDate(order.createdAt)}</dd>
              </div>
            </dl>
          </section>

          {/* 제품 정보 */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-100">
              제품 정보
            </h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              <div className="col-span-2">
                <dt className="text-gray-500">제품명</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.productName}</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-gray-500">규격</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.productSpec}</dd>
              </div>
              <div>
                <dt className="text-gray-500">재질</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.material}</dd>
              </div>
              <div>
                <dt className="text-gray-500">수량</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{order.quantity.toLocaleString()}개</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-gray-500">후처리</dt>
                <dd className="font-medium text-gray-900 mt-0.5">
                  {order.postProcessing || "-"}
                </dd>
              </div>
            </dl>
          </section>

          {/* 금액 정보 */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-100">
              금액 정보
            </h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              <div>
                <dt className="text-gray-500">단가</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{formatCurrency(order.unitPrice)}</dd>
              </div>
              <div>
                <dt className="text-gray-500">총 금액</dt>
                <dd className="font-bold text-gray-900 mt-0.5 text-base">{formatCurrency(order.totalPrice)}</dd>
              </div>
            </dl>
          </section>

          {/* 납기 정보 */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-100">
              납기 정보
            </h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              <div>
                <dt className="text-gray-500">요청 납기일</dt>
                <dd className="font-medium text-gray-900 mt-0.5">
                  {order.requestedDelivery || "-"}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">예상 납기일</dt>
                <dd className="font-medium text-gray-900 mt-0.5">
                  {order.estimatedDelivery || "-"}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">최종 수정일</dt>
                <dd className="font-medium text-gray-900 mt-0.5">{formatDate(order.updatedAt)}</dd>
              </div>
            </dl>
          </section>

          {/* 비고 */}
          {order.notes && (
            <section>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 pb-1 border-b border-gray-100">
                비고
              </h3>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-md p-3">
                {order.notes}
              </p>
            </section>
          )}
        </div>

        {/* 액션 버튼 (검토 중 상태일 때만 표시) */}
        {order.status === "reviewing" && (
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3">
            <button className="flex-1 py-2 px-4 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors">
              승인
            </button>
            <button className="flex-1 py-2 px-4 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors">
              반려
            </button>
            <button className="flex-1 py-2 px-4 bg-amber-500 text-white text-sm font-medium rounded-md hover:bg-amber-600 transition-colors">
              수정 요청
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// 정렬 키 타입
type SortKey = "id" | "companyName" | "productName" | "quantity" | "totalPrice" | "status" | "createdAt";
type SortDir = "asc" | "desc";

// 정렬 헤더 컴포넌트
interface SortableHeaderProps {
  label: string;
  sortKey: SortKey;
  currentKey: SortKey;
  currentDir: SortDir;
  onSort: (key: SortKey) => void;
}

function SortableHeader({ label, sortKey, currentKey, currentDir, onSort }: SortableHeaderProps) {
  const isActive = currentKey === sortKey;
  return (
    <th
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 transition-colors"
      onClick={() => onSort(sortKey)}
    >
      <span className="flex items-center gap-1">
        {label}
        {isActive ? (
          currentDir === "asc" ? (
            <ChevronUp size={14} className="text-blue-500" />
          ) : (
            <ChevronDown size={14} className="text-blue-500" />
          )
        ) : (
          <ChevronsUpDown size={14} className="text-gray-300" />
        )}
      </span>
    </th>
  );
}

// 메인 페이지
export default function OrdersPage() {
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("createdAt");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  // 통계 계산
  const totalCount = mockOrders.length;
  const newCount = mockOrders.filter(
    (o) => o.status === "pending" || o.status === "reviewing"
  ).length;
  const inProductionCount = mockOrders.filter(
    (o) => o.status === "in_production"
  ).length;
  const completedCount = mockOrders.filter(
    (o) => o.status === "completed"
  ).length;

  // 정렬 핸들러
  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  // 정렬된 주문 목록
  const sortedOrders = [...mockOrders].sort((a, b) => {
    const aVal: string | number = a[sortKey] as string | number;
    const bVal: string | number = b[sortKey] as string | number;

    if (typeof aVal === "string" && typeof bVal === "string") {
      const cmp = aVal.localeCompare(bVal, "ko");
      return sortDir === "asc" ? cmp : -cmp;
    }
    if (typeof aVal === "number" && typeof bVal === "number") {
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    }
    return 0;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">주문 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            전체 주문 현황을 확인하고 관리합니다.
          </p>
        </div>

        {/* 요약 통계 카드 */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="전체 주문"
            value={totalCount}
            icon={<Package size={20} className="text-gray-600" />}
            colorClass="bg-gray-100"
          />
          <StatCard
            title="신규 주문"
            value={newCount}
            icon={<Clock size={20} className="text-blue-600" />}
            colorClass="bg-blue-100"
          />
          <StatCard
            title="생산 중"
            value={inProductionCount}
            icon={<Factory size={20} className="text-yellow-600" />}
            colorClass="bg-yellow-100"
          />
          <StatCard
            title="완료"
            value={completedCount}
            icon={<CheckCircle size={20} className="text-emerald-600" />}
            colorClass="bg-emerald-100"
          />
        </div>

        {/* 주문 목록 테이블 */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-base font-semibold text-gray-900">주문 목록</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <SortableHeader
                    label="주문번호"
                    sortKey="id"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                  <SortableHeader
                    label="고객사"
                    sortKey="companyName"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                  <SortableHeader
                    label="제품명"
                    sortKey="productName"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    규격
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    재질
                  </th>
                  <SortableHeader
                    label="수량"
                    sortKey="quantity"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                  <SortableHeader
                    label="금액"
                    sortKey="totalPrice"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                  <SortableHeader
                    label="상태"
                    sortKey="status"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                  <SortableHeader
                    label="주문일"
                    sortKey="createdAt"
                    currentKey={sortKey}
                    currentDir={sortDir}
                    onSort={handleSort}
                  />
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {sortedOrders.map((order, idx) => {
                  const statusInfo = orderStatusMap[order.status];
                  const isSelected = selectedOrder?.id === order.id;
                  return (
                    <tr
                      key={order.id}
                      onClick={() => setSelectedOrder(order)}
                      className={`cursor-pointer transition-colors ${
                        isSelected
                          ? "bg-blue-50"
                          : idx % 2 === 0
                          ? "bg-white hover:bg-gray-50"
                          : "bg-gray-50/50 hover:bg-gray-100"
                      }`}
                    >
                      <td className="px-4 py-3 text-sm font-mono font-medium text-blue-600 whitespace-nowrap">
                        {order.id}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                        <div className="font-medium">{order.companyName}</div>
                        <div className="text-xs text-gray-400">{order.customerName}</div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap max-w-[160px] truncate">
                        {order.productName}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap max-w-[140px] truncate">
                        {order.productSpec}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                        {order.material}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap text-right">
                        {order.quantity.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap text-right font-medium">
                        {formatCurrency(order.totalPrice)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}
                        >
                          {statusInfo.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                        {formatDate(order.createdAt)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* 테이블 푸터 */}
          <div className="px-6 py-3 border-t border-gray-100 bg-gray-50">
            <p className="text-xs text-gray-500">
              총 {mockOrders.length}건의 주문
            </p>
          </div>
        </div>
      </div>

      {/* 주문 상세 패널 */}
      {selectedOrder && (
        <OrderDetailPanel
          order={selectedOrder}
          onClose={() => setSelectedOrder(null)}
        />
      )}
    </div>
  );
}
