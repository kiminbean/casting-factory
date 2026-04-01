"use client";

import dynamic from "next/dynamic";
import {
  Target,
  Bot,
  ShoppingCart,
  Bell,
  AlertTriangle,
  Clock,
  CheckCircle2,
  LayoutDashboard,
  Factory,
  BellRing,
  TrendingUp,
  ClipboardList,
} from "lucide-react";
import {
  mockDashboardStats,
  mockAlerts,
  mockEquipment,
  mockOrders,
} from "@/lib/mock-data";
import {
  alertSeverityMap,
  equipmentStatusMap,
  orderStatusMap,
  formatDate,
  formatCurrency,
  cn,
} from "@/lib/utils";
import FactoryMap from "@/components/FactoryMap";

// 차트 컴포넌트 — SSR 비활성화 (Recharts는 브라우저 전용)
const WeeklyProductionChart = dynamic(
  () => import("@/components/charts/WeeklyProductionChart"),
  {
    ssr: false,
    loading: () => (
      <div className="h-[260px] bg-gray-50 rounded-lg animate-pulse" />
    ),
  }
);

// ────────────────────────────────────────
// 요약 카드 컴포넌트
// ────────────────────────────────────────

function StatCard({
  title,
  value,
  icon: Icon,
  iconBg,
  iconColor,
  unit,
  accent,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  iconBg: string;
  iconColor: string;
  unit?: string;
  accent?: boolean;
}) {
  return (
    <div
      className={cn(
        "bg-white rounded-xl shadow-sm border p-5 flex items-center gap-4 transition-all hover:shadow-md",
        accent ? "border-red-200" : "border-gray-200"
      )}
    >
      <div
        className={cn(
          "w-12 h-12 rounded-xl flex items-center justify-center",
          iconBg
        )}
      >
        <Icon className={cn("w-6 h-6", iconColor)} />
      </div>
      <div>
        <p className="text-base text-gray-500 font-medium">{title}</p>
        <p
          className={cn(
            "text-3xl font-bold leading-tight",
            accent ? "text-red-600" : "text-gray-900"
          )}
        >
          {value}
          {unit && (
            <span className="text-lg font-normal text-gray-500 ml-1">
              {unit}
            </span>
          )}
        </p>
      </div>
    </div>
  );
}

// ────────────────────────────────────────
// 알림 심각도 우선순위 (정렬용)
// ────────────────────────────────────────

const severityOrder: Record<string, number> = {
  critical: 0,
  warning: 1,
  info: 2,
};

// ────────────────────────────────────────
// 메인 대시보드 페이지
// ────────────────────────────────────────

export default function DashboardPage() {
  const stats = mockDashboardStats;

  // 알림 — 심각도 순 정렬
  const sortedAlerts = [...mockAlerts].sort(
    (a, b) =>
      (severityOrder[a.severity] ?? 9) - (severityOrder[b.severity] ?? 9)
  );

  // 최근 주문 5건
  const recentOrders = mockOrders.slice(0, 5);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-screen-2xl mx-auto space-y-6">
        {/* ── 헤더 ── */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <LayoutDashboard className="w-7 h-7 text-blue-600" />
            통합 대시보드
          </h1>
          <p className="text-base text-gray-500 mt-1">
            주물 스마트 공장 실시간 관제
          </p>
        </div>

        {/* ── 요약 카드 4종 ── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <StatCard
            title="생산 목표 달성률"
            value={stats.productionGoalRate}
            unit="%"
            icon={Target}
            iconBg="bg-blue-50"
            iconColor="text-blue-600"
          />
          <StatCard
            title="실시간 가동 로봇"
            value={stats.activeRobots}
            unit="대"
            icon={Bot}
            iconBg="bg-green-50"
            iconColor="text-green-600"
          />
          <StatCard
            title="미처리 주문"
            value={stats.pendingOrders}
            unit="건"
            icon={ShoppingCart}
            iconBg="bg-amber-50"
            iconColor="text-amber-600"
          />
          <StatCard
            title="금일 발생 알람"
            value={stats.todayAlarms}
            unit="건"
            icon={Bell}
            iconBg="bg-red-50"
            iconColor="text-red-500"
            accent={stats.todayAlarms > 0}
          />
        </div>

        {/* ── 공장 Map + 실시간 알림 ── */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5 items-stretch">
          {/* 공장 레이아웃 (2/3 폭) */}
          <div className="xl:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-5 h-full">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Factory className="w-5 h-5 text-blue-600" />
                공장 레이아웃
              </h2>
              {/* 장비 상태 범례 */}
              <div className="flex items-center gap-3 text-sm text-gray-500">
                {(
                  Object.entries(equipmentStatusMap) as [
                    string,
                    { label: string; color: string },
                  ][]
                ).map(([key, { label, color }]) => (
                  <span key={key} className="flex items-center gap-1">
                    <span
                      className={cn(
                        "inline-block w-2.5 h-2.5 rounded-full",
                        color.replace(/text-\S+/, "").trim()
                      )}
                    />
                    {label}
                  </span>
                ))}
              </div>
            </div>
            <FactoryMap />
          </div>

          {/* 실시간 알림 피드 (1/3 폭) */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex flex-col min-h-0 h-full">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <BellRing className="w-5 h-5 text-amber-500" />
              실시간 알림
            </h2>
            <div className="space-y-3 overflow-y-auto flex-1 min-h-0 pr-1">
              {sortedAlerts.map((alert) => {
                const sev = alertSeverityMap[alert.severity];
                // 장비 이름 조회
                const eq = mockEquipment.find(
                  (e) => e.id === alert.equipmentId
                );
                return (
                  <div
                    key={alert.id}
                    className={cn(
                      "rounded-lg border p-3 transition-colors",
                      sev.bg
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 mb-1">
                          {alert.severity === "critical" ? (
                            <AlertTriangle className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
                          ) : alert.severity === "warning" ? (
                            <Clock className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                          ) : (
                            <CheckCircle2 className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                          )}
                          <span
                            className={cn(
                              "px-2.5 py-0.5 rounded-full text-sm font-semibold",
                              sev.color,
                              sev.bg
                            )}
                          >
                            {sev.label}
                          </span>
                        </div>
                        <p
                          className={cn(
                            "text-base font-medium leading-snug",
                            sev.color
                          )}
                        >
                          {alert.message}
                        </p>
                        {alert.abnormalValue && (
                          <p className="text-sm text-gray-500 mt-1">
                            이상값: {alert.abnormalValue}
                          </p>
                        )}
                        <div className="flex items-center gap-2 mt-1.5 text-sm text-gray-400">
                          {eq && <span>{eq.name}</span>}
                          <span>&middot;</span>
                          <span>{alert.zone}</span>
                          <span>&middot;</span>
                          <span>{formatDate(alert.timestamp)}</span>
                        </div>
                      </div>
                      {!alert.acknowledged && (
                        <span className="w-2 h-2 bg-red-500 rounded-full flex-shrink-0 mt-1 animate-pulse" />
                      )}
                    </div>
                  </div>
                );
              })}
              {sortedAlerts.length === 0 && (
                <p className="text-base text-gray-400 text-center py-8">
                  알림이 없습니다.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* ── 주간 생산 차트 + 최근 주문 ── */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 items-stretch">
          {/* 주간 생산 추이 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
              주간 생산 추이
            </h2>
            <WeeklyProductionChart />
          </div>

          {/* 최근 주문 테이블 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <ClipboardList className="w-5 h-5 text-indigo-500" />
              최근 주문
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-base">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="text-left text-sm font-semibold text-gray-600 uppercase tracking-wider py-2.5 px-3 rounded-tl-lg">
                      주문번호
                    </th>
                    <th className="text-left text-sm font-semibold text-gray-600 uppercase tracking-wider py-2.5 px-3">
                      고객사
                    </th>
                    <th className="text-right text-sm font-semibold text-gray-600 uppercase tracking-wider py-2.5 px-3">
                      금액
                    </th>
                    <th className="text-left text-sm font-semibold text-gray-600 uppercase tracking-wider py-2.5 px-3">
                      납기
                    </th>
                    <th className="text-center text-sm font-semibold text-gray-600 uppercase tracking-wider py-2.5 px-3 rounded-tr-lg">
                      상태
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recentOrders.map((order) => {
                    const statusInfo = orderStatusMap[order.status];
                    return (
                      <tr
                        key={order.id}
                        className="border-b border-gray-100 even:bg-gray-50 hover:bg-blue-50 transition-colors"
                      >
                        <td className="py-2.5 px-3">
                          <span className="font-mono text-sm text-gray-600">
                            {order.id}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="text-gray-800 truncate block max-w-[160px]">
                            {order.companyName}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right text-gray-700 font-medium whitespace-nowrap">
                          {formatCurrency(order.totalAmount)}
                        </td>
                        <td className="py-2.5 px-3 text-gray-600 text-sm whitespace-nowrap">
                          {order.requestedDelivery || "-"}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <span
                            className={cn(
                              "inline-block px-2.5 py-0.5 rounded-full text-sm font-semibold",
                              statusInfo.color
                            )}
                          >
                            {statusInfo.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {recentOrders.length === 0 && (
                <p className="text-base text-gray-400 text-center py-6">
                  주문이 없습니다.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
