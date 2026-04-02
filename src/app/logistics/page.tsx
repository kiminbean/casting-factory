"use client";

import { useState, useEffect, useMemo } from "react";
import {
  fetchTransportTasks,
  fetchEquipment,
  fetchWarehouseRacks,
  fetchOutboundOrders,
} from "@/lib/api";
import type { TransportTask, WarehouseRack, Equipment, OutboundOrder } from "@/lib/types";
import {
  transportStatusMap,
  equipmentStatusMap,
  getAmrStatusInfo,
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
  Loader2,
} from "lucide-react";

// 우선순위 정렬: high > medium > low
const priorityOrder: Record<TransportTask["priority"], number> = {
  high: 0,
  medium: 1,
  low: 2,
};

const priorityBadge: Record<TransportTask["priority"], { label: string; color: string }> = {
  high: { label: "긴급", color: "bg-red-100 text-red-700" },
  medium: { label: "보통", color: "bg-yellow-100 text-yellow-700" },
  low: { label: "낮음", color: "bg-gray-100 text-gray-600" },
};

// (amrList, sortedTransports는 컴포넌트 내부 useMemo로 이동)

function getBatteryColor(level: number): string {
  if (level > 50) return "bg-green-500";
  if (level >= 20) return "bg-yellow-500";
  return "bg-red-500";
}

function getBatteryTextColor(level: number): string {
  if (level > 50) return "text-green-600";
  if (level >= 20) return "text-yellow-600";
  return "text-red-600";
}

function getBatteryBgColor(level: number): string {
  if (level > 50) return "bg-green-100";
  if (level >= 20) return "bg-yellow-100";
  return "bg-red-100";
}

export default function LogisticsPage() {
  const [transports, setTransports] = useState<TransportTask[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [warehouseRacks, setWarehouseRacks] = useState<WarehouseRack[]>([]);
  const [outboundOrders, setOutboundOrders] = useState<OutboundOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [focusedRobotId, setFocusedRobotId] = useState<string | null>(null);
  const [hoveredRack, setHoveredRack] = useState<WarehouseRack | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [tData, eqData, wrData, obData] = await Promise.all([
          fetchTransportTasks(),
          fetchEquipment(),
          fetchWarehouseRacks(),
          fetchOutboundOrders(),
        ]);
        setTransports(tData);
        setEquipment(eqData);
        setWarehouseRacks(wrData);
        setOutboundOrders(obData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "데이터를 불러오는 중 오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const amrList = useMemo(() => equipment.filter((e) => e.type === "amr"), [equipment]);
  const sortedTransports = useMemo(
    () => [...transports].sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]),
    [transports]
  );

  const handleCompleteOrder = (orderId: string) => {
    setOutboundOrders((prev) =>
      prev.map((o) => (o.id === orderId ? { ...o, completed: true } : o))
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={36} className="animate-spin text-blue-500" />
          <p className="text-base text-gray-500">물류 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3 text-center">
          <AlertTriangle size={36} className="text-red-400" />
          <p className="text-base text-red-600">{error}</p>
          <button type="button" onClick={() => window.location.reload()} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">다시 시도</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-[1600px] mx-auto space-y-6">
        {/* 페이지 헤더 */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
            <Truck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">물류 / 이송 관리</h1>
            <p className="text-base text-gray-500">
              이송 큐, AMR 플릿 관리, 창고 랙 맵, 출고 주문
            </p>
          </div>
        </div>

        {/* 메인 3-컬럼 레이아웃 */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* ============================== */}
          {/* LEFT: 이송 작업 큐 */}
          {/* ============================== */}
          <div className="lg:col-span-3 flex flex-col">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-full">
              <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
                <ClipboardList className="w-5 h-5 text-blue-600" />
                <h2 className="text-xl font-bold text-gray-900">이송 작업 큐</h2>
                <span className="ml-auto px-2.5 py-0.5 rounded-full text-sm font-semibold bg-blue-100 text-blue-700">
                  {sortedTransports.length}건
                </span>
              </div>

              <div className="divide-y divide-gray-50 flex-1 overflow-y-auto">
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
                        <span className="text-sm font-mono text-gray-500">{task.id}</span>
                        <span
                          className={cn(
                            "px-2.5 py-0.5 rounded-full text-sm font-semibold",
                            prioInfo.color
                          )}
                        >
                          {prioInfo.label}
                        </span>
                        <span
                          className={cn(
                            "ml-auto px-2.5 py-0.5 rounded-full text-sm font-semibold",
                            statusInfo.color
                          )}
                        >
                          {statusInfo.label}
                        </span>
                      </div>

                      {/* 경로 */}
                      <div className="flex items-center gap-1.5 text-sm text-gray-700 mb-1">
                        <MapPin className="w-3 h-3 text-gray-400 shrink-0" />
                        <span className="truncate">{task.fromName}</span>
                        <ArrowRight className="w-3 h-3 text-gray-400 shrink-0" />
                        <span className="truncate">{task.toName}</span>
                      </div>

                      {/* 물품 + 수량 */}
                      <div className="flex items-center justify-between text-sm">
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
          <div className="lg:col-span-4 flex flex-col">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-full">
              <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
                <Bot className="w-5 h-5 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-900">AMR 플릿 관리</h2>
                <span className="ml-auto px-2.5 py-0.5 rounded-full text-sm font-semibold bg-purple-100 text-purple-700">{amrList.length}대</span>
              </div>

              <div className="p-4 space-y-3 flex-1 overflow-y-auto">
                {amrList.map((amr) => {
                  const statusInfo = getAmrStatusInfo(amr.status, amr.battery);
                  const battery = amr.battery ?? 0;
                  const batteryColor = getBatteryColor(battery);
                  const batteryText = getBatteryTextColor(battery);
                  const isCharging = amr.status === "charging";
                  const isBatteryLow = battery < 20;
                  const isFocused = focusedRobotId === amr.id;

                  // 이 AMR에 배정된 작업 찾기
                  const assignedTask = transports.find(
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
                          <span className="font-semibold text-gray-800 text-base">
                            {amr.name}
                          </span>
                          <span className="text-[10px] font-mono text-gray-400">{amr.id}</span>
                        </div>
                        <span
                          className={cn(
                            "px-2.5 py-0.5 rounded-full text-sm font-semibold",
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
                          <span className="text-sm text-red-700 font-medium">
                            배터리 부족 - 충전 필요
                          </span>
                        </div>
                      )}

                      {/* 충전 중 표시 */}
                      {isCharging && (
                        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-md bg-blue-50 border border-blue-200">
                          <Zap className="w-3.5 h-3.5 text-blue-500 animate-pulse" />
                          <span className="text-sm text-blue-700 font-medium">충전 중</span>
                        </div>
                      )}

                      {/* 배터리 프로그레스 바 */}
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-1 text-gray-500">
                            <Battery className="w-3.5 h-3.5" />
                            <span>배터리</span>
                          </div>
                          <span className={cn("px-2 py-0.5 rounded-full text-sm font-bold", batteryText, getBatteryBgColor(battery))}>{battery}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div
                            className={cn(batteryColor, "h-2.5 rounded-full transition-all duration-300")}
                            style={{ width: `${battery}%` }}
                          />
                        </div>
                      </div>

                      {/* 속도 + 위치 */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="flex items-center gap-1.5 text-sm text-gray-500">
                          <Gauge className="w-3 h-3" />
                          <span>속도: </span>
                          <span className="font-semibold text-gray-700">
                            {amr.speed ?? 0} m/s
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5 text-sm text-gray-500">
                          <MapPin className="w-3 h-3" />
                          <span className="truncate">{amr.installLocation}</span>
                        </div>
                      </div>

                      {/* 적재 물품 / 배정 작업 */}
                      {assignedTask && (
                        <div className="rounded-lg bg-white border border-gray-200 p-3 space-y-1.5 shadow-sm">
                          <div className="flex items-center gap-1.5 text-sm">
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
                                "ml-auto px-2 py-0.5 rounded-full text-sm font-semibold",
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
          <div className="lg:col-span-5 flex flex-col">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-full">
              <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
                <Grid3X3 className="w-5 h-5 text-teal-600" />
                <h2 className="text-xl font-bold text-gray-900">창고 랙 맵</h2>
                <span className="ml-auto px-2.5 py-0.5 rounded-full text-sm font-semibold bg-teal-100 text-teal-700">4행 x 6열</span>
              </div>

              <div className="p-5 space-y-5">
                {/* 랙 그리드 (4행 x 6열) */}
                <div className="grid grid-cols-6 gap-2.5">
                  {warehouseRacks.map((rack) => {
                    const colorClass = storageSlotColorMap[rack.status];
                    const isHovered = hoveredRack?.id === rack.id;

                    return (
                      <div
                        key={rack.id}
                        onMouseEnter={() => setHoveredRack(rack)}
                        onMouseLeave={() => setHoveredRack(null)}
                        className={cn(
                          "relative border-2 rounded-xl p-2.5 min-h-[84px]",
                          "flex flex-col items-center justify-center",
                          "text-center transition-all duration-200 cursor-default shadow-sm",
                          colorClass,
                          isHovered && "ring-2 ring-blue-400 scale-[1.05] shadow-md"
                        )}
                      >
                        {/* 구역 표시 */}
                        <span className="absolute top-1 left-1.5 text-[9px] font-medium text-gray-400">
                          {rack.zone}
                        </span>

                        {/* 랙 번호 */}
                        <span className="text-sm font-mono font-bold text-gray-700 mt-1">
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
                  <div className="rounded-xl bg-gray-50 border border-gray-200 p-4 text-sm space-y-1.5 shadow-sm">
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
                <div className="flex flex-wrap gap-5 pt-3 border-t border-gray-100">
                  {[
                    { status: "empty" as const, label: "비어있음" },
                    { status: "occupied" as const, label: "점유" },
                    { status: "reserved" as const, label: "예약" },
                    { status: "unavailable" as const, label: "사용불가" },
                  ].map((item) => (
                    <div key={item.status} className="flex items-center gap-2">
                      <div
                        className={cn(
                          "w-4 h-4 rounded-md border-2",
                          storageSlotColorMap[item.status]
                        )}
                      />
                      <span className="text-sm font-medium text-gray-600">{item.label}</span>
                    </div>
                  ))}
                </div>

                {/* 통계 요약 */}
                <div className="grid grid-cols-4 gap-3 pt-3 border-t border-gray-100">
                  {[
                    {
                      label: "비어있음",
                      count: warehouseRacks.filter((r) => r.status === "empty").length,
                      color: "text-gray-600",
                    },
                    {
                      label: "점유",
                      count: warehouseRacks.filter((r) => r.status === "occupied").length,
                      color: "text-blue-700",
                    },
                    {
                      label: "예약",
                      count: warehouseRacks.filter((r) => r.status === "reserved").length,
                      color: "text-amber-600",
                    },
                    {
                      label: "사용불가",
                      count: warehouseRacks.filter((r) => r.status === "unavailable").length,
                      color: "text-red-600",
                    },
                  ].map((stat) => (
                    <div key={stat.label} className="text-center">
                      <div className={cn("text-xl font-bold", stat.color)}>{stat.count}</div>
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
            <Package className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">출고 주문</h2>
            <span className="ml-auto px-2.5 py-0.5 rounded-full text-sm font-semibold bg-indigo-100 text-indigo-700">
              {outboundOrders.length}건
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-base">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">주문ID</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">제품명</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600 uppercase tracking-wider">수량</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">납품처</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600 uppercase tracking-wider">정책</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600 uppercase tracking-wider">상태</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">생성일</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600 uppercase tracking-wider">액션</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {outboundOrders.map((order) => (
                  <tr key={order.id} className="even:bg-gray-50 hover:bg-blue-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-sm text-gray-600">
                      {order.id}
                    </td>
                    <td className="px-4 py-3">
                      <span className="flex items-center gap-1.5">
                        <Package className="w-3 h-3 text-gray-400 shrink-0" />
                        <span className="text-sm text-gray-700">{order.productName}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-gray-800">
                      {order.quantity}개
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{order.destination}</td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={cn(
                          "px-2.5 py-0.5 rounded-full text-sm font-semibold",
                          order.policy === "FIFO"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-orange-100 text-orange-700"
                        )}
                      >
                        {order.policy}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {order.completed ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-sm font-semibold bg-green-100 text-green-700">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          완료
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-700">
                          <Circle className="w-3.5 h-3.5" />
                          대기
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {formatDate(order.createdAt)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {!order.completed ? (
                        <button
                          type="button"
                          onClick={() => handleCompleteOrder(order.id)}
                          className="px-3.5 py-1.5 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm hover:shadow"
                        >
                          완료 처리
                        </button>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
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
