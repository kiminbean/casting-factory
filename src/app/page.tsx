"use client";

import dynamic from "next/dynamic";
import { Package, AlertTriangle, Activity, Bell } from "lucide-react";
import {
  mockDashboardStats,
  mockProcessStages,
  mockAlerts,
  mockOrders,
} from "@/lib/mock-data";
import {
  processStatusMap,
  alertSeverityMap,
  orderStatusMap,
  formatDate,
  cn,
} from "@/lib/utils";

const WeeklyProductionChart = dynamic(
  () => import("@/components/charts/WeeklyProductionChart"),
  { ssr: false, loading: () => <div className="h-[220px] bg-gray-50 rounded animate-pulse" /> }
);

function StatCard({
  title,
  value,
  icon: Icon,
  iconClassName,
  unit,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  iconClassName?: string;
  unit?: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex items-center gap-4">
      <div className={cn("p-3 rounded-lg", iconClassName ?? "bg-blue-50")}>
        <Icon className={cn("w-6 h-6", iconClassName ? "" : "text-blue-600")} />
      </div>
      <div>
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900 leading-tight">
          {value}
          {unit && <span className="text-base font-normal text-gray-500 ml-1">{unit}</span>}
        </p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const activeOrders = mockOrders.filter((o) =>
    ["pending", "reviewing", "approved", "in_production"].includes(o.status)
  );
  const recentAlerts = mockAlerts.slice(0, 3);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-screen-xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">생산 현황 대시보드</h1>
          <p className="text-sm text-gray-500 mt-1">주조 공장 실시간 모니터링</p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="오늘 생산량" value={mockDashboardStats.todayProduction} unit="개" icon={Package} iconClassName="bg-blue-50" />
          <StatCard title="불량률" value={`${mockDashboardStats.defectRate}%`} icon={AlertTriangle} iconClassName="bg-amber-50" />
          <StatCard title="장비 가동률" value={`${mockDashboardStats.equipmentUtilization}%`} icon={Activity} iconClassName="bg-green-50" />
          <div className={cn("bg-white rounded-xl shadow-sm border p-5 flex items-center gap-4", mockDashboardStats.activeAlerts > 0 ? "border-red-200" : "border-gray-100")}>
            <div className={cn("p-3 rounded-lg", mockDashboardStats.activeAlerts > 0 ? "bg-red-50" : "bg-gray-50")}>
              <Bell className={cn("w-6 h-6", mockDashboardStats.activeAlerts > 0 ? "text-red-500" : "text-gray-400")} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">활성 알림</p>
              <p className={cn("text-2xl font-bold leading-tight", mockDashboardStats.activeAlerts > 0 ? "text-red-600" : "text-gray-900")}>
                {mockDashboardStats.activeAlerts}
                <span className="text-base font-normal text-gray-500 ml-1">건</span>
              </p>
            </div>
          </div>
        </div>

        {/* 차트 + 공정 현황 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
            <h2 className="text-base font-semibold text-gray-800 mb-4">주간 생산 추이</h2>
            <WeeklyProductionChart />
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
            <h2 className="text-base font-semibold text-gray-800 mb-4">현재 공정 현황</h2>
            <div className="space-y-3 overflow-y-auto max-h-[220px]">
              {mockProcessStages.map((stage) => {
                const statusInfo = processStatusMap[stage.status];
                return (
                  <div key={stage.stage} className="flex items-center gap-3">
                    <span className={cn("w-2.5 h-2.5 rounded-full flex-shrink-0", statusInfo.dot)} />
                    <span className="text-sm font-medium text-gray-700 w-20 flex-shrink-0">{stage.label}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          stage.status === "running" ? "bg-blue-500"
                            : stage.status === "completed" ? "bg-green-500"
                            : stage.status === "error" ? "bg-red-500"
                            : stage.status === "waiting" ? "bg-amber-400"
                            : "bg-gray-300"
                        )}
                        style={{ width: `${stage.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-8 text-right flex-shrink-0">{stage.progress}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 알림 + 주문 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
            <h2 className="text-base font-semibold text-gray-800 mb-4">최근 알림</h2>
            <div className="space-y-3">
              {recentAlerts.map((alert) => {
                const severityInfo = alertSeverityMap[alert.severity];
                return (
                  <div key={alert.id} className={cn("rounded-lg border p-3", severityInfo.bg)}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className={cn("text-sm font-medium leading-snug", severityInfo.color)}>{alert.message}</p>
                        <p className="text-xs text-gray-400 mt-1">{alert.zone} &middot; {formatDate(alert.timestamp)}</p>
                      </div>
                      <span className={cn("text-xs font-semibold px-2 py-0.5 rounded-full flex-shrink-0", severityInfo.color, severityInfo.bg)}>
                        {severityInfo.label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
            <h2 className="text-base font-semibold text-gray-800 mb-4">진행 중 주문</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left text-xs font-semibold text-gray-500 pb-2 pr-3">주문번호</th>
                    <th className="text-left text-xs font-semibold text-gray-500 pb-2 pr-3">제품명</th>
                    <th className="text-right text-xs font-semibold text-gray-500 pb-2 pr-3">수량</th>
                    <th className="text-center text-xs font-semibold text-gray-500 pb-2">상태</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {activeOrders.map((order) => {
                    const statusInfo = orderStatusMap[order.status];
                    return (
                      <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-2.5 pr-3"><span className="font-mono text-xs text-gray-600">{order.id}</span></td>
                        <td className="py-2.5 pr-3"><span className="text-gray-800 truncate block max-w-[140px]">{order.productName}</span></td>
                        <td className="py-2.5 pr-3 text-right text-gray-700 font-medium">{order.quantity.toLocaleString()}개</td>
                        <td className="py-2.5 text-center">
                          <span className={cn("inline-block text-xs font-medium px-2 py-0.5 rounded-full", statusInfo.color)}>{statusInfo.label}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {activeOrders.length === 0 && <p className="text-sm text-gray-400 text-center py-6">진행 중인 주문이 없습니다.</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
