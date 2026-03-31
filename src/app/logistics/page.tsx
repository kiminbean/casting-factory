"use client";

import { useState } from "react";
import {
  mockTransports,
  mockEquipment,
  mockWarehouseRacks,
  mockOutboundOrders,
} from "@/lib/mock-data";
import type { TransportTask, WarehouseRack } from "@/lib/types";
import {
  transportStatusMap,
  equipmentStatusMap,
  storageSlotColorMap,
  formatDate,
  cn,
} from "@/lib/utils";
import {
  Truck,
  Bot,
  Warehouse,
  Battery,
  BatteryCharging,
  BatteryWarning,
  MapPin,
  Package,
  ArrowRight,
  Zap,
  Gauge,
  CheckCircle2,
  Circle,
  ClipboardList,
  Grid3X3,
  AlertTriangle,
} from "lucide-react";

// 우선순위 정렬: high > medium > low
const priorityOrder: Record<TransportTask["priority"], number> = {
  high: 0,
  medium: 1,
  low: 2,
};

const priorityBadge: Record<TransportTask["priority"], { label: string; color: string }> = {
  high: { label: "긴급", color: "bg-red-100 text-red-700 border-red-200" },
  medium: { label: "보통", color: "bg-yellow-100 text-yellow-700 border-yellow-200" },
  low: { label: "낮음", color: "bg-gray-100 text-gray-600 border-gray-200" },
};

// AMR 목록
const amrList = mockEquipment.filter((e) => e.type === "amr");

// 이송 작업을 우선순위 순으로 정렬
const sortedTransports = [...mockTransports].sort(
  (a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]
);

function getBatteryColor(level: number): string {
  if (level >= 60) return "bg-green-500";
  if (level >= 30) return "bg-amber-500";
  return "bg-red-500";
}

function getBatteryTextColor(level: number): string {
  if (level >= 60) return "text-green-600";
  if (level >= 30) return "text-amber-600";
  return "text-red-600";
}

export default function LogisticsPage() {
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [focusedRobotId, setFocusedRobotId] = useState<string | null>(null);
  const [outboundOrders, setOutboundOrders] = useState(mockOutboundOrders);
  const [hoveredRack, setHoveredRack] = useState<WarehouseRack | null>(null);

  const handleCompleteOrder = (orderId: string) => {
    setOutboundOrders((prev) =>
      prev.map((o) => (o.id === orderId ? { ...o, completed: true } : o))
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-[1600px] mx-auto space-y-6">
        {/* 페이지 헤더 */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
            <Truck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">물류 / 이송 관리</h1>
            <p className="text-sm text-gray-500">
              이송 큐, AMR 플릿 관리, 창고 랙 맵, 출고 주문
            </p>
          </div>
        </div>

        {/* 메인 3-컬럼 레이아웃 */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* ============================== */}
          {/* LEFT: 이송 작업 큐 */}
          {/* ============================== */}
          <div className="lg:col-span-3 space-y-0">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
                <ClipboardList className="w-4 h-4 text-blue-600" />
                <h2 className="text-sm font-semibold text-gray-800">이송 작업 큐</h2>
                <span className="ml-auto text-xs text-gray-400">
                  {sortedTransports.length}건
                </span>
              </div>

              <div className="divide-y divide-gray-50 max-h-[600px] overflow-y-auto">
                {sortedTransports.map((task) => {
                  const statusInfo = transportStatusMap[task.status];
                  const prioInfo = priorityBadge[task.priority];
                  const isSelected = selectedTaskId === task.id;

                  return (
                    <button
                      key={task.id}
                      type="button"
                      onClick={() => {
                        setSelectedTaskId(isSelected ? null : task.id);
                        // AMR에 포커스 연결
                        if (!isSelected && task.assignedRobotId) {
                          setFocusedRobotId(task.assignedRobotId);
                        } else {
                          setFocusedRobotId(null);
                        }
                      }}
                      className={cn(
                        "w-full text-left px-4 py-3 transition-colors",
                        isSelected
                          ? "bg-blue-50 border-l-4 border-l-blue-500"
                          : "hover:bg-gray-50 border-l-4 border-l-transparent"
                      )}
                    >
                      {/* 상단: ID + 우선순위 + 상태 */}
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-xs font-mono text-gray-500">{task.id}</span>
                        <span
                          className={cn(
                            "px-1.5 py-0.5 rounded text-[10px] font-semibold border",
                            prioInfo.color
                          )}
                        >
                          {prioInfo.label}
                        </span>
                        <span
                          className={cn(
                            "ml-auto px-2 py-0.5 rounded-full text-[10px] font-medium",
                            statusInfo.color
                          )}
                        >
                          {statusInfo.label}
                        </span>
                      </div>

                      {/* 경로 */}
                      <div className="flex items-center gap-1.5 text-xs text-gray-700 mb-1">
                        <MapPin className="w-3 h-3 text-gray-400 shrink-0" />
                        <span className="truncate">{task.fromName}</span>
                        <ArrowRight className="w-3 h-3 text-gray-400 shrink-0" />
                        <span className="truncate">{task.toName}</span>
                      </div>

                      {/* 물품 + 수량 */}
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-500 flex items-center gap-1">
                          <Package className="w-3 h-3" />
                          {task.itemName}
                        </span>
                        <span className="font-semibold text-gray-700">{task.quantity}개</span>
                      </div>

                      {/* 배정 AMR */}
                      {task.assignedRobotId && (
                        <div className="mt-1.5 flex items-center gap-1 text-[10px] text-blue-600">
                          <Bot className="w-3 h-3" />
                          <span>{task.assignedRobotId}</span>
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* ============================== */}
          {/* CENTER: AMR 플릿 관리 */}
          {/* ============================== */}
          <div className="lg:col-span-4 space-y-0">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
                <Bot className="w-4 h-4 text-purple-600" />
                <h2 className="text-sm font-semibold text-gray-800">AMR 플릿 관리</h2>
                <span className="ml-auto text-xs text-gray-400">{amrList.length}대</span>
              </div>

              <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
                {amrList.map((amr) => {
                  const statusInfo = equipmentStatusMap[amr.status];
                  const battery = amr.battery ?? 0;
                  const batteryColor = getBatteryColor(battery);
                  const batteryText = getBatteryTextColor(battery);
                  const isCharging = amr.status === "charging";
                  const isBatteryLow = battery < 20;
                  const isFocused = focusedRobotId === amr.id;

                  // 이 AMR에 배정된 작업 찾기
                  const assignedTask = mockTransports.find(
                    (t) => t.assignedRobotId === amr.id && t.status !== "completed"
                  );

                  return (
                    <div
                      key={amr.id}
                      onClick={() => setFocusedRobotId(isFocused ? null : amr.id)}
                      className={cn(
                        "rounded-lg border p-4 space-y-3 cursor-pointer transition-all",
                        isFocused
                          ? "border-purple-300 bg-purple-50 ring-1 ring-purple-200"
                          : "border-gray-100 bg-gray-50 hover:border-gray-200"
                      )}
                    >
                      {/* 이름 + 상태 */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {isCharging ? (
                            <BatteryCharging className="w-4 h-4 text-blue-500" />
                          ) : isBatteryLow ? (
                            <BatteryWarning className="w-4 h-4 text-red-500 animate-pulse" />
                          ) : (
                            <Bot className="w-4 h-4 text-purple-500" />
                          )}
                          <span className="font-semibold text-gray-800 text-sm">
                            {amr.name}
                          </span>
                          <span className="text-[10px] font-mono text-gray-400">{amr.id}</span>
                        </div>
                        <span
                          className={cn(
                            "px-2 py-0.5 rounded-full text-xs font-medium",
                            statusInfo.color
                          )}
                        >
                          {statusInfo.label}
                        </span>
                      </div>

                      {/* 배터리 경고 */}
                      {isBatteryLow && !isCharging && (
                        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-md bg-red-50 border border-red-200">
                          <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
                          <span className="text-xs text-red-700 font-medium">
                            배터리 부족 - 충전 필요
                          </span>
                        </div>
                      )}

                      {/* 충전 중 표시 */}
                      {isCharging && (
                        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-md bg-blue-50 border border-blue-200">
                          <Zap className="w-3.5 h-3.5 text-blue-500 animate-pulse" />
                          <span className="text-xs text-blue-700 font-medium">충전 중</span>
                        </div>
                      )}

                      {/* 배터리 프로그레스 바 */}
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-1 text-gray-500">
                            <Battery className="w-3 h-3" />
                            <span>배터리</span>
                          </div>
                          <span className={cn("font-bold", batteryText)}>{battery}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={cn(batteryColor, "h-2 rounded-full transition-all")}
                            style={{ width: `${battery}%` }}
                          />
                        </div>
                      </div>

                      {/* 속도 + 위치 */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="flex items-center gap-1.5 text-xs text-gray-500">
                          <Gauge className="w-3 h-3" />
                          <span>속도: </span>
                          <span className="font-semibold text-gray-700">
                            {amr.speed ?? 0} m/s
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-gray-500">
                          <MapPin className="w-3 h-3" />
                          <span className="truncate">{amr.installLocation}</span>
                        </div>
                      </div>

                      {/* 적재 물품 / 배정 작업 */}
                      {assignedTask && (
                        <div className="rounded-md bg-white border border-gray-200 p-2.5 space-y-1">
                          <div className="flex items-center gap-1.5 text-xs">
                            <Package className="w-3 h-3 text-blue-500" />
                            <span className="font-medium text-gray-700">
                              {assignedTask.itemName}
                            </span>
                            <span className="text-gray-400">x{assignedTask.quantity}</span>
                          </div>
                          <div className="flex items-center gap-1 text-[10px] text-gray-500">
                            <ClipboardList className="w-3 h-3" />
                            <span>Task: {assignedTask.id}</span>
                            <span
                              className={cn(
                                "ml-auto px-1.5 py-0.5 rounded-full font-medium",
                                transportStatusMap[assignedTask.status].color
                              )}
                            >
                              {transportStatusMap[assignedTask.status].label}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* ============================== */}
          {/* RIGHT: 창고 랙 맵 */}
          {/* ============================== */}
          <div className="lg:col-span-5 space-y-0">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
                <Grid3X3 className="w-4 h-4 text-teal-600" />
                <h2 className="text-sm font-semibold text-gray-800">창고 랙 맵</h2>
                <span className="ml-auto text-xs text-gray-400">4행 x 6열</span>
              </div>

              <div className="p-5 space-y-4">
                {/* 랙 그리드 (4행 x 6열) */}
                <div className="grid grid-cols-6 gap-2">
                  {mockWarehouseRacks.map((rack) => {
                    const colorClass = storageSlotColorMap[rack.status];
                    const isHovered = hoveredRack?.id === rack.id;

                    return (
                      <div
                        key={rack.id}
                        onMouseEnter={() => setHoveredRack(rack)}
                        onMouseLeave={() => setHoveredRack(null)}
                        className={cn(
                          "relative border-2 rounded-lg p-2 min-h-[80px]",
                          "flex flex-col items-center justify-center",
                          "text-center transition-all cursor-default",
                          colorClass,
                          isHovered && "ring-2 ring-blue-400 scale-105"
                        )}
                      >
                        {/* 구역 표시 */}
                        <span className="absolute top-1 left-1.5 text-[9px] font-medium text-gray-400">
                          {rack.zone}
                        </span>

                        {/* 랙 번호 */}
                        <span className="text-xs font-mono font-bold text-gray-700 mt-1">
                          {rack.rackNumber}
                        </span>

                        {/* 상태별 표시 */}
                        {rack.status === "occupied" && (
                          <>
                            <span className="text-[10px] text-blue-700 truncate w-full mt-0.5">
                              {rack.itemName ?? ""}
                            </span>
                            <span className="text-[11px] font-bold text-blue-900">
                              {rack.quantity ?? 0}개
                            </span>
                          </>
                        )}
                        {rack.status === "reserved" && (
                          <span className="mt-1 text-[10px] font-medium text-amber-700">
                            예약
                          </span>
                        )}
                        {rack.status === "empty" && (
                          <span className="mt-1 text-[10px] text-gray-400">비어있음</span>
                        )}
                        {rack.status === "unavailable" && (
                          <span className="mt-1 text-[10px] text-red-700 font-medium">
                            사용불가
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* 호버 시 상세 정보 */}
                {hoveredRack && (
                  <div className="rounded-lg bg-gray-50 border border-gray-200 p-3 text-xs space-y-1">
                    <div className="flex items-center gap-2 text-gray-800 font-semibold">
                      <Warehouse className="w-3.5 h-3.5" />
                      <span>
                        {hoveredRack.zone} / 랙 {hoveredRack.rackNumber}
                      </span>
                    </div>
                    <div className="text-gray-500">
                      상태:{" "}
                      <span className="font-medium text-gray-700">
                        {hoveredRack.status === "empty"
                          ? "비어있음"
                          : hoveredRack.status === "occupied"
                          ? "점유 중"
                          : hoveredRack.status === "reserved"
                          ? "예약됨"
                          : "사용불가"}
                      </span>
                    </div>
                    {hoveredRack.itemName && (
                      <div className="text-gray-500">
                        물품: <span className="font-medium text-gray-700">{hoveredRack.itemName}</span>
                        {" / "}
                        <span className="font-semibold text-blue-700">{hoveredRack.quantity}개</span>
                      </div>
                    )}
                    {hoveredRack.lastInboundAt && (
                      <div className="text-gray-400">
                        마지막 입고: {formatDate(hoveredRack.lastInboundAt)}
                      </div>
                    )}
                  </div>
                )}

                {/* 범례 */}
                <div className="flex flex-wrap gap-4 pt-2 border-t border-gray-100">
                  {[
                    { status: "empty" as const, label: "비어있음" },
                    { status: "occupied" as const, label: "점유" },
                    { status: "reserved" as const, label: "예약" },
                    { status: "unavailable" as const, label: "사용불가" },
                  ].map((item) => (
                    <div key={item.status} className="flex items-center gap-1.5">
                      <div
                        className={cn(
                          "w-4 h-4 rounded border-2",
                          storageSlotColorMap[item.status]
                        )}
                      />
                      <span className="text-xs text-gray-600">{item.label}</span>
                    </div>
                  ))}
                </div>

                {/* 통계 요약 */}
                <div className="grid grid-cols-4 gap-2 pt-2 border-t border-gray-100">
                  {[
                    {
                      label: "비어있음",
                      count: mockWarehouseRacks.filter((r) => r.status === "empty").length,
                      color: "text-gray-600",
                    },
                    {
                      label: "점유",
                      count: mockWarehouseRacks.filter((r) => r.status === "occupied").length,
                      color: "text-blue-700",
                    },
                    {
                      label: "예약",
                      count: mockWarehouseRacks.filter((r) => r.status === "reserved").length,
                      color: "text-amber-600",
                    },
                    {
                      label: "사용불가",
                      count: mockWarehouseRacks.filter((r) => r.status === "unavailable").length,
                      color: "text-red-600",
                    },
                  ].map((stat) => (
                    <div key={stat.label} className="text-center">
                      <div className={cn("text-lg font-bold", stat.color)}>{stat.count}</div>
                      <div className="text-[10px] text-gray-500">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ============================== */}
        {/* BOTTOM: 출고 주문 테이블 */}
        {/* ============================== */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
            <Package className="w-4 h-4 text-indigo-600" />
            <h2 className="text-sm font-semibold text-gray-800">출고 주문</h2>
            <span className="ml-auto text-xs text-gray-400">
              {outboundOrders.length}건
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="px-4 py-3 text-left font-medium text-gray-500">주문ID</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">제품명</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-500">수량</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">납품처</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-500">정책</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-500">상태</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">생성일</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-500">액션</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {outboundOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-600">
                      {order.id}
                    </td>
                    <td className="px-4 py-3">
                      <span className="flex items-center gap-1.5">
                        <Package className="w-3 h-3 text-gray-400 shrink-0" />
                        <span className="text-xs text-gray-700">{order.productName}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-gray-800">
                      {order.quantity}개
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-700">{order.destination}</td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-bold",
                          order.policy === "FIFO"
                            ? "bg-blue-50 text-blue-700 border border-blue-200"
                            : "bg-orange-50 text-orange-700 border border-orange-200"
                        )}
                      >
                        {order.policy}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {order.completed ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                          <CheckCircle2 className="w-3 h-3" />
                          완료
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                          <Circle className="w-3 h-3" />
                          대기
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {formatDate(order.createdAt)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {!order.completed ? (
                        <button
                          type="button"
                          onClick={() => handleCompleteOrder(order.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                        >
                          완료 처리
                        </button>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
