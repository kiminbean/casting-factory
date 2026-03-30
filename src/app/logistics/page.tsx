"use client";

import { mockTransports, mockEquipment, mockStorageSlots } from "@/lib/mock-data";
import { transportStatusMap, equipmentStatusMap, storageSlotColorMap } from "@/lib/utils";
import {
  Truck,
  Bot,
  Warehouse,
  CheckCircle2,
  Clock,
  Battery,
  BatteryCharging,
  MapPin,
  Package,
  ArrowRight,
} from "lucide-react";

// -- 통계 계산 --
const activeTransports = mockTransports.filter((t) => t.status !== "completed").length;
const completedTransports = mockTransports.filter((t) => t.status === "completed").length;
const amrList = mockEquipment.filter((e) => e.type === "amr");
const idleAmrCount = amrList.filter((a) => a.status === "idle").length;

// -- 적재 통계 계산 --
const totalSlots = mockStorageSlots.length;
const occupiedSlots = mockStorageSlots.filter((s) => s.status === "occupied").length;
const emptySlots = mockStorageSlots.filter((s) => s.status === "empty").length;
const utilizationPct = Math.round((occupiedSlots / totalSlots) * 100);

// -- AMR 배터리 시뮬레이션 (운영 시간 기반) --
function getBatteryLevel(operatingHours: number, status: string): number {
  if (status === "charging") return 85;
  // 운영 시간을 기반으로 임의 배터리 수준 시뮬레이션
  const base = 100 - ((operatingHours * 7) % 80);
  return Math.max(15, Math.min(95, base));
}

function getBatteryColor(level: number): string {
  if (level >= 60) return "bg-green-500";
  if (level >= 30) return "bg-amber-500";
  return "bg-red-500";
}

export default function LogisticsPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* 페이지 헤더 */}
        <div className="flex items-center gap-3">
          <Truck className="w-7 h-7 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">물류 / 이송 관리</h1>
            <p className="text-sm text-gray-500">AMR 이송 현황, 적재 맵, 이송 요청 관리</p>
          </div>
        </div>

        {/* 1. 이송 통계 카드 (상단 3개) */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* 활성 이송 */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-500">활성 이송</span>
              <div className="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center">
                <Truck className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{activeTransports}</p>
            <p className="text-xs text-gray-400 mt-1">현재 진행 중인 이송 건수</p>
          </div>

          {/* 완료 이송 */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-500">완료 이송</span>
              <div className="w-9 h-9 bg-green-50 rounded-lg flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{completedTransports}</p>
            <p className="text-xs text-gray-400 mt-1">오늘 완료된 이송 건수</p>
          </div>

          {/* AMR 가용 */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-500">AMR 가용</span>
              <div className="w-9 h-9 bg-purple-50 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-purple-600" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{idleAmrCount}</p>
            <p className="text-xs text-gray-400 mt-1">대기 중인 AMR 대수</p>
          </div>
        </div>

        {/* 2. 이송 요청 현황 테이블 + 3. AMR 현황 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* 이송 요청 현황 테이블 */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <h2 className="text-base font-semibold text-gray-800">이송 요청 현황</h2>
              <span className="ml-auto text-xs text-gray-400">{mockTransports.length}건</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100">
                    <th className="px-4 py-3 text-left font-medium text-gray-500">이송ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">출발지</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">도착지</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">물품</th>
                    <th className="px-4 py-3 text-right font-medium text-gray-500">수량</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">상태</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">AMR</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">요청시간</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {mockTransports.map((t) => {
                    const statusInfo = transportStatusMap[t.status];
                    const reqTime = new Date(t.requestedAt).toLocaleTimeString("ko-KR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    });
                    return (
                      <tr key={t.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 font-mono text-xs text-gray-600">{t.id}</td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1 text-gray-700">
                            <MapPin className="w-3 h-3 text-gray-400 shrink-0" />
                            <span className="text-xs">{t.fromZone}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1 text-gray-700">
                            <ArrowRight className="w-3 h-3 text-gray-400 shrink-0" />
                            <span className="text-xs">{t.toZone}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1">
                            <Package className="w-3 h-3 text-gray-400 shrink-0" />
                            <span className="text-xs text-gray-700">{t.itemType}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right font-semibold text-gray-800">
                          {t.quantity}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}
                          >
                            {statusInfo.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600">
                          {t.assignedAmrId ?? (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-500">{reqTime}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* AMR 현황 패널 */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
              <Bot className="w-4 h-4 text-gray-500" />
              <h2 className="text-base font-semibold text-gray-800">AMR 현황</h2>
              <span className="ml-auto text-xs text-gray-400">{amrList.length}대</span>
            </div>
            <div className="p-4 space-y-3">
              {amrList.map((amr) => {
                const statusInfo = equipmentStatusMap[amr.status];
                const batteryLevel = getBatteryLevel(amr.operatingHours, amr.status);
                const batteryColor = getBatteryColor(batteryLevel);
                const isCharging = amr.status === "charging";

                return (
                  <div
                    key={amr.id}
                    className="rounded-lg border border-gray-100 bg-gray-50 p-4 space-y-3"
                  >
                    {/* AMR 이름 + 상태 배지 */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {isCharging ? (
                          <BatteryCharging className="w-4 h-4 text-blue-500" />
                        ) : (
                          <Bot className="w-4 h-4 text-gray-500" />
                        )}
                        <span className="font-medium text-gray-800 text-sm">{amr.name}</span>
                      </div>
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}
                      >
                        {statusInfo.label}
                      </span>
                    </div>

                    {/* 위치 */}
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <MapPin className="w-3 h-3" />
                      <span>{amr.zone}</span>
                    </div>

                    {/* 배터리 인디케이터 */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1 text-gray-500">
                          <Battery className="w-3 h-3" />
                          <span>배터리</span>
                        </div>
                        <span
                          className={`font-semibold ${
                            batteryLevel >= 60
                              ? "text-green-600"
                              : batteryLevel >= 30
                              ? "text-amber-600"
                              : "text-red-600"
                          }`}
                        >
                          {batteryLevel}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className={`${batteryColor} h-1.5 rounded-full transition-all`}
                          style={{ width: `${batteryLevel}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 4. 적재 현황 맵 + 5. 적재 통계 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* 적재 현황 맵 */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
              <Warehouse className="w-4 h-4 text-gray-500" />
              <h2 className="text-base font-semibold text-gray-800">적재 현황 맵</h2>
              <span className="ml-auto text-xs text-gray-400">4행 x 6열</span>
            </div>

            <div className="p-5 space-y-4">
              {/* 슬롯 그리드 */}
              <div className="grid grid-cols-6 gap-2">
                {mockStorageSlots.map((slot) => {
                  const colorClass = storageSlotColorMap[slot.status];
                  return (
                    <div
                      key={slot.id}
                      className={`
                        relative border-2 rounded-lg p-2 min-h-[72px]
                        flex flex-col items-center justify-center
                        text-center transition-colors cursor-default
                        ${colorClass}
                      `}
                      title={`${slot.id} / ${slot.status}${slot.quantity ? ` / ${slot.quantity}개` : ""}`}
                    >
                      <span className="text-[10px] font-mono font-semibold text-gray-600 leading-tight">
                        {slot.id.replace("SLT-", "")}
                      </span>
                      {slot.status === "occupied" && slot.quantity != null && (
                        <span className="mt-1 text-[11px] font-bold text-blue-800">
                          {slot.quantity}개
                        </span>
                      )}
                      {slot.status === "reserved" && (
                        <span className="mt-1 text-[10px] text-amber-700">예약</span>
                      )}
                      {slot.status === "unavailable" && (
                        <span className="mt-1 text-[10px] text-red-700">불가</span>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* 범례 */}
              <div className="flex flex-wrap gap-4 pt-2 border-t border-gray-100">
                <div className="flex items-center gap-1.5">
                  <div className="w-4 h-4 rounded border-2 bg-gray-100 border-gray-300" />
                  <span className="text-xs text-gray-600">비어있음</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-4 h-4 rounded border-2 bg-blue-200 border-blue-400" />
                  <span className="text-xs text-gray-600">점유</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-4 h-4 rounded border-2 bg-amber-200 border-amber-400" />
                  <span className="text-xs text-gray-600">예약</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-4 h-4 rounded border-2 bg-red-200 border-red-400" />
                  <span className="text-xs text-gray-600">사용불가</span>
                </div>
              </div>
            </div>
          </div>

          {/* 적재 통계 */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
              <Package className="w-4 h-4 text-gray-500" />
              <h2 className="text-base font-semibold text-gray-800">적재 통계</h2>
            </div>
            <div className="p-5 space-y-5">

              {/* 통계 항목 */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">전체 슬롯</span>
                  <span className="font-semibold text-gray-900">{totalSlots}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">점유 슬롯</span>
                  <span className="font-semibold text-blue-700">{occupiedSlots}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">빈 슬롯</span>
                  <span className="font-semibold text-gray-600">{emptySlots}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">예약</span>
                  <span className="font-semibold text-amber-600">
                    {mockStorageSlots.filter((s) => s.status === "reserved").length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">사용불가</span>
                  <span className="font-semibold text-red-600">
                    {mockStorageSlots.filter((s) => s.status === "unavailable").length}
                  </span>
                </div>
              </div>

              {/* 가동률 프로그레스 바 */}
              <div className="space-y-2 pt-3 border-t border-gray-100">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 font-medium">가동률</span>
                  <span
                    className={`font-bold ${
                      utilizationPct >= 80
                        ? "text-red-600"
                        : utilizationPct >= 60
                        ? "text-amber-600"
                        : "text-green-600"
                    }`}
                  >
                    {utilizationPct}%
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${
                      utilizationPct >= 80
                        ? "bg-red-500"
                        : utilizationPct >= 60
                        ? "bg-amber-500"
                        : "bg-blue-500"
                    }`}
                    style={{ width: `${utilizationPct}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400">
                  {totalSlots}개 중 {occupiedSlots}개 사용 중
                </p>
              </div>

              {/* 빠른 현황 요약 */}
              <div className="rounded-lg bg-blue-50 border border-blue-100 p-3 space-y-1">
                <p className="text-xs font-semibold text-blue-800">현황 요약</p>
                <p className="text-xs text-blue-700">
                  가용 슬롯 {emptySlots}개 남음 ({100 - utilizationPct}% 여유)
                </p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
