"use client";

import { useMemo } from "react";
import dynamic from "next/dynamic";
import {
  mockInspections,
  mockDefectTypeStats,
  mockSorterLogs,
  mockInspectionStandards,
} from "@/lib/mock-data";
import { formatDate, cn } from "@/lib/utils";
import {
  CheckCircle,
  XCircle,
  ClipboardList,
  ShieldCheck,
  Camera,
  ArrowDownUp,
  Eye,
  AlertTriangle,
  Ruler,
  ImageIcon,
} from "lucide-react";

// Recharts 동적 임포트 (SSR 비활성화)
const DefectTypeDistChart = dynamic(
  () => import("@/components/charts/DefectTypeDistChart"),
  { ssr: false, loading: () => <div className="h-[260px] bg-gray-50 rounded animate-pulse" /> }
);

const DefectRateChart = dynamic(
  () => import("@/components/charts/DefectRateChart"),
  { ssr: false, loading: () => <div className="h-[260px] bg-gray-50 rounded animate-pulse" /> }
);

const ProductionVsDefectsChart = dynamic(
  () => import("@/components/charts/ProductionVsDefectsChart"),
  { ssr: false, loading: () => <div className="h-[260px] bg-gray-50 rounded animate-pulse" /> }
);

export default function QualityPage(): React.JSX.Element {
  // 검사 통계 계산
  const stats = useMemo(() => {
    const total = mockInspections.length;
    const passCount = mockInspections.filter((i) => i.result === "pass").length;
    const failCount = total - passCount;
    const passRate = total > 0 ? (passCount / total) * 100 : 0;
    return { total, passCount, failCount, passRate };
  }, []);

  // 불량 유형 TOP 3
  const top3Defects = useMemo(
    () => mockDefectTypeStats.slice(0, 3),
    []
  );

  // 불량 검사 로그만 추출
  const failedInspections = useMemo(
    () => mockInspections.filter((i) => i.result === "fail"),
    []
  );

  // 최신 sorter 로그 (가장 최근 것)
  const latestSorter = mockSorterLogs[mockSorterLogs.length - 1];

  // 가장 최근 검사 결과 (비전 피드 시뮬레이션용)
  const latestInspection = mockInspections[mockInspections.length - 1];
  const isLatestPass = latestInspection?.result === "pass";

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-[1600px] mx-auto space-y-6">
        {/* 페이지 헤더 */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">품질 검사 대시보드</h1>
          <p className="text-sm text-gray-500 mt-1">
            AI 비전 기반 실시간 품질 검사 현황 및 분류 장치 모니터링
          </p>
        </div>

        {/* ──────────────────────────────── */}
        {/* TOP: 검사 통계 카드 */}
        {/* ──────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 금일 총 검사 수 */}
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">금일 총 검사 수</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
                <p className="text-xs text-gray-400 mt-1">
                  양품 {stats.passCount} / 불량 {stats.failCount}
                </p>
              </div>
              <div className="p-3 bg-gray-100 rounded-full">
                <ClipboardList className="w-6 h-6 text-gray-600" />
              </div>
            </div>
          </div>

          {/* 양품률 */}
          <div
            className={cn(
              "bg-white rounded-lg border p-5 shadow-sm",
              stats.passRate >= 95
                ? "border-green-200 bg-green-50/30"
                : stats.passRate >= 90
                  ? "border-yellow-200 bg-yellow-50/30"
                  : "border-red-200 bg-red-50/30"
            )}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">양품률</p>
                <p
                  className={cn(
                    "text-3xl font-bold mt-1",
                    stats.passRate >= 95
                      ? "text-green-600"
                      : stats.passRate >= 90
                        ? "text-yellow-600"
                        : "text-red-600"
                  )}
                >
                  {stats.passRate.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  {stats.passRate >= 95
                    ? "정상 (목표 95% 이상)"
                    : stats.passRate >= 90
                      ? "주의 (목표 미달)"
                      : "위험 (즉시 조치 필요)"}
                </p>
              </div>
              <div
                className={cn(
                  "p-3 rounded-full",
                  stats.passRate >= 95
                    ? "bg-green-100"
                    : stats.passRate >= 90
                      ? "bg-yellow-100"
                      : "bg-red-100"
                )}
              >
                <ShieldCheck
                  className={cn(
                    "w-6 h-6",
                    stats.passRate >= 95
                      ? "text-green-600"
                      : stats.passRate >= 90
                        ? "text-yellow-600"
                        : "text-red-600"
                  )}
                />
              </div>
            </div>
          </div>

          {/* 주요 불량 유형 TOP 3 */}
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm lg:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <p className="text-sm font-semibold text-gray-700">주요 불량 유형 TOP 3</p>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {top3Defects.map((d, idx) => (
                <div key={d.type} className="text-center">
                  <div
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full text-white text-sm font-bold mb-1"
                    style={{ backgroundColor: d.color }}
                  >
                    {idx + 1}
                  </div>
                  <p className="text-sm font-medium text-gray-800">{d.type}</p>
                  <p className="text-xs text-gray-500">
                    {d.count}건 ({d.percentage}%)
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ──────────────────────────────── */}
        {/* CENTER: 비전/센서 피드 + 불량 유형 차트 */}
        {/* ──────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 비전 카메라 피드 + 분류 장치 상태 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 비전 카메라 시뮬레이션 */}
            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <Camera className="w-5 h-5 text-blue-600" />
                <h2 className="text-base font-semibold text-gray-800">비전 검사 피드</h2>
                <span className="ml-auto flex items-center gap-1.5 text-xs text-green-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  실시간
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 카메라 뷰 시뮬레이션 */}
                <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video flex items-center justify-center">
                  {/* 스캔라인 효과 */}
                  <div className="absolute inset-0 opacity-10">
                    {Array.from({ length: 20 }).map((_, i) => (
                      <div
                        key={i}
                        className="w-full border-t border-green-500/30"
                        style={{ marginTop: `${i * 5}%` }}
                      />
                    ))}
                  </div>
                  {/* 중앙 주물 이미지 플레이스홀더 */}
                  <div className="relative z-10 flex flex-col items-center gap-2">
                    <div className="w-24 h-24 rounded-full border-2 border-dashed border-gray-600 flex items-center justify-center">
                      <Eye className="w-8 h-8 text-gray-500" />
                    </div>
                    <span className="text-xs text-gray-500 font-mono">
                      CAM-001 | {latestInspection?.castingId ?? "---"}
                    </span>
                  </div>
                  {/* PASS / FAIL 배지 */}
                  <div className="absolute top-3 right-3 z-20">
                    {isLatestPass ? (
                      <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-sm font-bold bg-green-600 text-white shadow-lg shadow-green-600/30">
                        <CheckCircle className="w-4 h-4" /> PASS
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-sm font-bold bg-red-600 text-white shadow-lg shadow-red-600/30">
                        <XCircle className="w-4 h-4" /> FAIL
                      </span>
                    )}
                  </div>
                  {/* 신뢰도 표시 */}
                  <div className="absolute bottom-3 left-3 z-20">
                    <span className="text-xs font-mono text-green-400 bg-black/60 px-2 py-1 rounded">
                      신뢰도: {latestInspection?.confidence.toFixed(1)}%
                    </span>
                  </div>
                  {/* 타임스탬프 */}
                  <div className="absolute bottom-3 right-3 z-20">
                    <span className="text-xs font-mono text-gray-400 bg-black/60 px-2 py-1 rounded">
                      {latestInspection ? formatDate(latestInspection.inspectedAt) : "--:--"}
                    </span>
                  </div>
                </div>

                {/* 분류 장치 상태 */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <ArrowDownUp className="w-4 h-4 text-indigo-600" />
                    <h3 className="text-sm font-semibold text-gray-700">분류 장치 상태</h3>
                  </div>

                  {/* 분류기 시각화 */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                    <div className="flex items-center justify-center mb-4">
                      <div className="relative w-40 h-40">
                        {/* 분류기 원형 베이스 */}
                        <div className="absolute inset-0 rounded-full border-4 border-gray-300 flex items-center justify-center">
                          {/* 분류 방향 화살표 */}
                          <div
                            className="absolute w-1 bg-indigo-500 rounded-full origin-bottom"
                            style={{
                              height: "45%",
                              bottom: "50%",
                              left: "calc(50% - 2px)",
                              transform: `rotate(${latestSorter?.sorterAngle ?? 0}deg)`,
                              transition: "transform 0.5s ease-in-out",
                            }}
                          />
                          {/* 중앙 점 */}
                          <div className="w-4 h-4 rounded-full bg-indigo-600 z-10" />
                        </div>
                        {/* 양품 라인 라벨 */}
                        <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-xs font-medium text-green-600">
                          양품 (0deg)
                        </span>
                        {/* 불량 라인 라벨 */}
                        <span className="absolute top-6 -right-10 text-xs font-medium text-red-600">
                          불량 (45deg)
                        </span>
                      </div>
                    </div>

                    {/* 분류기 상세 정보 */}
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="bg-white rounded-md p-2 text-center border border-gray-100">
                        <p className="text-xs text-gray-500">현재 각도</p>
                        <p className="font-bold text-indigo-700">
                          {latestSorter?.sorterAngle ?? 0}&deg;
                        </p>
                      </div>
                      <div className="bg-white rounded-md p-2 text-center border border-gray-100">
                        <p className="text-xs text-gray-500">분류 방향</p>
                        <p
                          className={cn(
                            "font-bold",
                            latestSorter?.sortDirection === "pass_line"
                              ? "text-green-600"
                              : "text-red-600"
                          )}
                        >
                          {latestSorter?.sortDirection === "pass_line"
                            ? "양품 라인"
                            : "불량 라인"}
                        </p>
                      </div>
                      <div className="bg-white rounded-md p-2 text-center border border-gray-100">
                        <p className="text-xs text-gray-500">동작 성공</p>
                        <p
                          className={cn(
                            "font-bold",
                            latestSorter?.success ? "text-green-600" : "text-red-600"
                          )}
                        >
                          {latestSorter?.success ? "성공" : "실패"}
                        </p>
                      </div>
                      <div className="bg-white rounded-md p-2 text-center border border-gray-100">
                        <p className="text-xs text-gray-500">검사 ID</p>
                        <p className="font-bold text-gray-700 font-mono text-xs">
                          {latestSorter?.inspectionId ?? "-"}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 불량률 추이 + 생산량 vs 불량 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
                <h2 className="text-base font-semibold text-gray-800 mb-4">불량률 추이</h2>
                <DefectRateChart />
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
                <h2 className="text-base font-semibold text-gray-800 mb-4">생산량 vs 불량</h2>
                <ProductionVsDefectsChart />
              </div>
            </div>
          </div>

          {/* 우측: 불량 유형 분포 + 검사 기준 */}
          <div className="space-y-6">
            {/* 불량 유형 분포 차트 */}
            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <h2 className="text-base font-semibold text-gray-800 mb-4">불량 유형 분포</h2>
              <DefectTypeDistChart />
            </div>

            {/* 검사 기준 참조 패널 */}
            <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <Ruler className="w-4 h-4 text-gray-500" />
                <h2 className="text-sm font-semibold text-gray-700">검사 기준 참조</h2>
              </div>
              <div className="space-y-3">
                {mockInspectionStandards.map((std) => (
                  <div
                    key={std.productId}
                    className="bg-gray-50 rounded-md p-3 border border-gray-100 text-sm"
                  >
                    <p className="font-medium text-gray-800 mb-1">{std.productName}</p>
                    <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
                      <span>목표 치수</span>
                      <span className="text-gray-700">{std.targetDimension}</span>
                      <span>허용 오차</span>
                      <span className="text-gray-700">{std.toleranceRange}</span>
                      <span>판정 임계값</span>
                      <span className="text-gray-700">{std.threshold}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ──────────────────────────────── */}
        {/* BOTTOM: 불량 검사 로그 테이블 */}
        {/* ──────────────────────────────── */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-base font-semibold text-gray-800">불량 검사 로그</h2>
            <span className="text-xs text-gray-400">
              총 {failedInspections.length}건의 불량 기록
            </span>
          </div>
          <div className="overflow-x-auto max-h-[420px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-50 z-10">
                <tr className="border-b border-gray-200">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    이미지
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    검사ID
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    제품ID
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    판정
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    불량유형
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    상세사유
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    신뢰도
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">
                    검사시각
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {failedInspections.map((ins) => (
                  <tr
                    key={ins.id}
                    className="hover:bg-red-50/40 transition-colors"
                  >
                    {/* 이미지 플레이스홀더 */}
                    <td className="px-4 py-3">
                      <div className="w-10 h-10 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
                        <ImageIcon className="w-4 h-4 text-gray-400" />
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-600">
                      {ins.id}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-600">
                      {ins.castingId}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                        <XCircle className="w-3 h-3" /> 불량
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-800 font-medium">
                        {ins.defectType ?? "-"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs max-w-[200px] truncate">
                      {ins.defectDetail ?? "-"}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5">
                          <div
                            className={cn(
                              "h-1.5 rounded-full",
                              ins.confidence >= 95
                                ? "bg-green-500"
                                : ins.confidence >= 90
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                            )}
                            style={{ width: `${ins.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-700">
                          {ins.confidence.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                      {formatDate(ins.inspectedAt)}
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
