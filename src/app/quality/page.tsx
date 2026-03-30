"use client";

import dynamic from "next/dynamic";
import { mockInspections } from "@/lib/mock-data";
import { formatDate } from "@/lib/utils";
import { CheckCircle, XCircle, ClipboardList, TrendingDown } from "lucide-react";

const DefectRateChart = dynamic(
  () => import("@/components/charts/DefectRateChart"),
  { ssr: false, loading: () => <div className="h-[260px] bg-gray-50 rounded animate-pulse" /> }
);

const ProductionVsDefectsChart = dynamic(
  () => import("@/components/charts/ProductionVsDefectsChart"),
  { ssr: false, loading: () => <div className="h-[260px] bg-gray-50 rounded animate-pulse" /> }
);

const DefectTypeDistChart = dynamic(
  () => import("@/components/charts/DefectTypeDistChart"),
  { ssr: false, loading: () => <div className="h-[200px] bg-gray-50 rounded animate-pulse" /> }
);

export default function QualityPage() {
  const total = mockInspections.length;
  const passCount = mockInspections.filter((i) => i.result === "pass").length;
  const failCount = mockInspections.filter((i) => i.result === "fail").length;
  const defectRate = total > 0 ? (failCount / total) * 100 : 0;

  const defectRateColor = defectRate < 5 ? "text-green-600" : defectRate < 10 ? "text-yellow-600" : "text-red-600";
  const defectRateBadgeBg = defectRate < 5 ? "bg-green-50 border-green-200" : defectRate < 10 ? "bg-yellow-50 border-yellow-200" : "bg-red-50 border-red-200";

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">품질 검사</h1>
          <p className="text-sm text-gray-500 mt-1">AI 비전 기반 품질 검사 결과 및 불량 통계</p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">총 검사</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{total}</p>
                <p className="text-xs text-gray-400 mt-1">개</p>
              </div>
              <div className="p-3 bg-gray-100 rounded-full"><ClipboardList className="w-6 h-6 text-gray-600" /></div>
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">양품</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{passCount}</p>
                <p className="text-xs text-gray-400 mt-1">{total > 0 ? `${((passCount / total) * 100).toFixed(1)}%` : "0%"}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full"><CheckCircle className="w-6 h-6 text-green-600" /></div>
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">불량품</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{failCount}</p>
                <p className="text-xs text-gray-400 mt-1">{total > 0 ? `${((failCount / total) * 100).toFixed(1)}%` : "0%"}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-full"><XCircle className="w-6 h-6 text-red-600" /></div>
            </div>
          </div>
          <div className={`bg-white rounded-lg border p-5 shadow-sm ${defectRateBadgeBg}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">불량률</p>
                <p className={`text-3xl font-bold mt-1 ${defectRateColor}`}>{defectRate.toFixed(1)}%</p>
                <p className="text-xs text-gray-400 mt-1">
                  {defectRate < 5 ? "정상 (목표 5% 이하)" : defectRate < 10 ? "주의 (목표 초과)" : "위험 (즉시 조치 필요)"}
                </p>
              </div>
              <div className={`p-3 rounded-full ${defectRate < 5 ? "bg-green-100" : defectRate < 10 ? "bg-yellow-100" : "bg-red-100"}`}>
                <TrendingDown className={`w-6 h-6 ${defectRateColor}`} />
              </div>
            </div>
          </div>
        </div>

        {/* 차트 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <h2 className="text-base font-semibold text-gray-800 mb-4">불량률 추이</h2>
            <DefectRateChart />
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <h2 className="text-base font-semibold text-gray-800 mb-4">생산량 vs 불량</h2>
            <ProductionVsDefectsChart />
          </div>
        </div>

        {/* 불량 유형 + 검사 이력 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <h2 className="text-base font-semibold text-gray-800 mb-4">불량 유형 분포</h2>
            <DefectTypeDistChart />
          </div>

          <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="text-base font-semibold text-gray-800">검사 이력</h2>
            </div>
            <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr className="border-b border-gray-200">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">검사ID</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">주물ID</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">주문번호</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">결과</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">신뢰도</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">불량유형</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">검사시간</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {mockInspections.map((ins) => (
                    <tr key={ins.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs text-gray-600">{ins.id}</td>
                      <td className="px-4 py-3 font-mono text-xs text-gray-600">{ins.castingId}</td>
                      <td className="px-4 py-3 text-gray-700">{ins.orderId}</td>
                      <td className="px-4 py-3">
                        {ins.result === "pass" ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                            <CheckCircle className="w-3 h-3" /> 양품
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                            <XCircle className="w-3 h-3" /> 불량
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-700">{ins.confidence.toFixed(1)}%</td>
                      <td className="px-4 py-3 text-gray-500">{ins.defectType ?? <span className="text-gray-300">-</span>}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{formatDate(ins.inspectedAt)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
