"use client";

import { useState, useEffect, useMemo } from "react";
import dynamic from "next/dynamic";
import {
  Thermometer,
  Flame,
  Layers,
  Droplets,
  Wind,
  Wrench,
  ChevronRight,
  OctagonX,
  Timer,
  Gauge,
  BarChart3,
  ArrowRightLeft,
  MapPin,
  Activity,
  Settings,
  Zap,
  ClipboardList,
  Bot,
  Truck,
  Video,
  ArrowDownUp,
  BatteryMedium,
  ScanLine,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import {
  fetchProcessStages,
  fetchEquipment,
  fetchProductionMetrics,
} from "@/lib/api";
import type {
  ProcessStageData,
  ProcessStage,
  ProcessStatus,
  Equipment,
  EquipmentStatus,
  EquipmentType,
  ProductionMetric,
} from "@/lib/types";
import { cn, processStatusMap, equipmentStatusMap, formatDate } from "@/lib/utils";

// Recharts: SSR 비활성화 동적 임포트
const AreaChart = dynamic(
  () => import("recharts").then((m) => m.AreaChart),
  { ssr: false }
);
const BarChartComponent = dynamic(
  () => import("recharts").then((m) => m.BarChart),
  { ssr: false }
);
const Area = dynamic(() => import("recharts").then((m) => m.Area), {
  ssr: false,
});
const Bar = dynamic(() => import("recharts").then((m) => m.Bar), {
  ssr: false,
});
const XAxis = dynamic(() => import("recharts").then((m) => m.XAxis), {
  ssr: false,
});
const YAxis = dynamic(() => import("recharts").then((m) => m.YAxis), {
  ssr: false,
});
const CartesianGrid = dynamic(
  () => import("recharts").then((m) => m.CartesianGrid),
  { ssr: false }
);
const Tooltip = dynamic(() => import("recharts").then((m) => m.Tooltip), {
  ssr: false,
});
const ResponsiveContainer = dynamic(
  () => import("recharts").then((m) => m.ResponsiveContainer),
  { ssr: false }
);
const ReferenceLine = dynamic(
  () => import("recharts").then((m) => m.ReferenceLine),
  { ssr: false }
);
const Legend = dynamic(() => import("recharts").then((m) => m.Legend), {
  ssr: false,
});

// ────────────────────────────────────────
// 공정 흐름 정의 (5단계)
// ────────────────────────────────────────

interface FlowStep {
  key: ProcessStage;
  label: string;
  icon: React.ReactNode;
}

const PROCESS_FLOW: FlowStep[] = [
  { key: "melting", label: "원재료 투입 / 용해", icon: <Flame className="w-5 h-5" /> },
  { key: "molding", label: "조형", icon: <Layers className="w-5 h-5" /> },
  { key: "pouring", label: "주탕", icon: <Droplets className="w-5 h-5" /> },
  { key: "cooling", label: "냉각 / 탈형", icon: <Wind className="w-5 h-5" /> },
  { key: "post_processing", label: "후처리 / 검사", icon: <Wrench className="w-5 h-5" /> },
];

// ────────────────────────────────────────
// 상태별 색상 매핑
// ────────────────────────────────────────

function statusBg(status: ProcessStatus): string {
  switch (status) {
    case "running":
      return "bg-blue-500 text-white border-blue-600 shadow-blue-300/50 shadow-lg";
    case "completed":
      return "bg-green-500 text-white border-green-600";
    case "error":
      return "bg-red-500 text-white border-red-600 animate-pulse";
    case "waiting":
      return "bg-amber-400 text-amber-900 border-amber-500";
    case "idle":
      return "bg-gray-200 text-gray-500 border-gray-300";
    case "stopped":
      return "bg-red-300 text-red-800 border-red-400";
    default:
      return "bg-gray-200 text-gray-500 border-gray-300";
  }
}

function arrowColor(status: ProcessStatus): string {
  switch (status) {
    case "running":
      return "text-blue-400";
    case "completed":
      return "text-green-400";
    case "error":
      return "text-red-400";
    default:
      return "text-gray-300";
  }
}

// ────────────────────────────────────────
// 용해로 온도 시뮬레이션 데이터 생성 함수
// ────────────────────────────────────────

function buildTempTimeline(stages: ProcessStageData[]) {
  const meltingStage = stages.find((s) => s.stage === "melting");
  return Array.from({ length: 30 }, (_, i) => {
    const minute = i + 1;
    const target = meltingStage?.targetTemperature ?? 1450;
    const current = Math.round(
      target - (target - 1200) * Math.exp(-0.12 * minute) + (Math.random() - 0.5) * 8
    );
    return {
      time: `${minute}분`,
      현재온도: current,
      목표온도: target,
    };
  });
}

// ────────────────────────────────────────
// 설비 타입별 아이콘 및 허용 상태 정의
// ────────────────────────────────────────

const equipmentTypeIcon: Record<EquipmentType, React.ReactNode> = {
  furnace: <Flame className="w-4 h-4" />,
  mold_press: <Layers className="w-4 h-4" />,
  robot_arm: <Bot className="w-4 h-4" />,
  amr: <Truck className="w-4 h-4" />,
  conveyor: <ArrowRightLeft className="w-4 h-4" />,
  camera: <Video className="w-4 h-4" />,
  sorter: <ArrowDownUp className="w-4 h-4" />,
};

// 설비 타입별 전환 가능한 상태 목록
const equipmentValidStates: Record<EquipmentType, EquipmentStatus[]> = {
  robot_arm: ["running", "idle", "maintenance"],
  amr: ["running", "idle", "charging", "maintenance"],
  furnace: ["running", "idle", "maintenance"],
  mold_press: ["running", "idle", "maintenance"],
  conveyor: ["running", "idle", "error"],
  camera: ["running", "idle"],
  sorter: ["running", "idle"],
};

// 상태별 버튼 색상 (활성/비활성)
const statusButtonStyle: Record<EquipmentStatus, { active: string; inactive: string }> = {
  running: {
    active: "bg-green-500 text-white ring-2 ring-green-300 shadow-md",
    inactive: "bg-green-50 text-green-600 hover:bg-green-100 border border-green-200",
  },
  idle: {
    active: "bg-gray-500 text-white ring-2 ring-gray-300 shadow-md",
    inactive: "bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200",
  },
  charging: {
    active: "bg-blue-500 text-white ring-2 ring-blue-300 shadow-md",
    inactive: "bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200",
  },
  maintenance: {
    active: "bg-yellow-500 text-white ring-2 ring-yellow-300 shadow-md",
    inactive: "bg-yellow-50 text-yellow-600 hover:bg-yellow-100 border border-yellow-200",
  },
  error: {
    active: "bg-red-500 text-white ring-2 ring-red-300 shadow-md animate-pulse",
    inactive: "bg-red-50 text-red-600 hover:bg-red-100 border border-red-200",
  },
};

// ────────────────────────────────────────
// 메인 페이지 컴포넌트
// ────────────────────────────────────────

export default function ProductionPage() {
  const [processStages, setProcessStages] = useState<ProcessStageData[]>([]);
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  const [hourlyProduction, setHourlyProduction] = useState<ProductionMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [stagesData, eqData, metricsData] = await Promise.all([
          fetchProcessStages(),
          fetchEquipment(),
          fetchProductionMetrics(),
        ]);
        setProcessStages(stagesData);
        setEquipmentList(eqData);
        setHourlyProduction(metricsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "데이터를 불러오는 중 오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // 설비별 자동/수동 모드 토글 상태
  const [autoModes, setAutoModes] = useState<Record<string, boolean>>({});

  // 설비별 현재 상태
  const [equipmentStatuses, setEquipmentStatuses] = useState<Record<string, EquipmentStatus>>({});

  // 설비 데이터 로드 후 초기화
  useEffect(() => {
    if (equipmentList.length > 0) {
      const modes: Record<string, boolean> = {};
      const statuses: Record<string, EquipmentStatus> = {};
      equipmentList.forEach((eq) => {
        modes[eq.id] = true;
        statuses[eq.id] = eq.status;
      });
      setAutoModes(modes);
      setEquipmentStatuses(statuses);
    }
  }, [equipmentList]);

  // 상태 변경 시 시각 피드백용 (최근 변경된 설비 ID)
  const [recentlyChanged, setRecentlyChanged] = useState<string | null>(null);

  const toggleMode = (equipmentId: string) => {
    setAutoModes((prev) => ({
      ...prev,
      [equipmentId]: !prev[equipmentId],
    }));
  };

  const changeEquipmentStatus = (equipmentId: string, newStatus: EquipmentStatus) => {
    setEquipmentStatuses((prev) => ({
      ...prev,
      [equipmentId]: newStatus,
    }));
    setRecentlyChanged(equipmentId);
    setTimeout(() => setRecentlyChanged(null), 800);
  };

  // 온도 타임라인 데이터
  const tempTimelineData = useMemo(() => buildTempTimeline(processStages), [processStages]);

  // 공정 단계별 데이터 매핑
  const stageDataMap = useMemo(() => {
    const map: Record<string, ProcessStageData> = {};
    processStages.forEach((s) => {
      map[s.stage] = s;
    });
    return map;
  }, [processStages]);

  // 냉각 공정 데이터
  const coolingStage = stageDataMap["cooling"];
  const coolingProgress = coolingStage?.coolingProgress ?? 0;
  // 남은 시간 계산 (예상)
  const coolingRemainingMin = coolingStage?.estimatedEnd
    ? Math.max(
        0,
        Math.round(
          (new Date(coolingStage.estimatedEnd).getTime() - Date.now()) / 60000
        )
      )
    : 0;

  // 조형/주탕 데이터
  const meltingStage = stageDataMap["melting"];
  const moldingStage = stageDataMap["molding"];
  const pouringStage = stageDataMap["pouring"];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={36} className="animate-spin text-blue-500" />
          <p className="text-base text-gray-500">생산 데이터를 불러오는 중...</p>
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
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* ====== 페이지 헤더 ====== */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Activity className="w-7 h-7 text-blue-600" />
          생산 모니터링
        </h1>
        <span className="text-base text-gray-500">
          최종 갱신: {new Date().toLocaleTimeString("ko-KR")}
        </span>
      </div>

      {/* ====== 1. 공정 흐름 (Process Flow) ====== */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-amber-500" />
          공정 흐름
        </h2>
        <div className="flex items-center justify-between gap-1 overflow-x-auto pb-2">
          {PROCESS_FLOW.map((step, idx) => {
            const data = stageDataMap[step.key];
            const status: ProcessStatus = data?.status ?? "idle";
            const statusInfo = processStatusMap[status];
            const progress = data?.progress ?? 0;

            return (
              <div key={step.key} className="flex items-center flex-1 min-w-0">
                {/* 스텝 카드 */}
                <div
                  className={cn(
                    "relative flex flex-col items-center justify-center rounded-xl border-2 px-4 py-3 w-full transition-all",
                    statusBg(status)
                  )}
                >
                  <div className="mb-1">{step.icon}</div>
                  <span className="text-sm font-bold whitespace-nowrap">
                    {step.label}
                  </span>
                  <span className="text-[10px] mt-0.5 opacity-80">
                    {statusInfo.label}
                  </span>
                  {/* 진행률 바 */}
                  {status === "running" && (
                    <div className="w-full mt-2 bg-white/30 rounded-full h-1.5">
                      <div
                        className="bg-white rounded-full h-1.5 transition-all"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  )}
                  {status === "completed" && (
                    <div className="w-full mt-2 bg-white/30 rounded-full h-1.5">
                      <div className="bg-white rounded-full h-1.5 w-full" />
                    </div>
                  )}
                </div>
                {/* 화살표 (마지막 제외) */}
                {idx < PROCESS_FLOW.length - 1 && (
                  <ChevronRight
                    className={cn(
                      "w-6 h-6 flex-shrink-0 mx-1",
                      arrowColor(status)
                    )}
                  />
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ====== 2. 메인 3-컬럼 레이아웃 ====== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
        {/* ── 중앙: 라이브 데이터 차트 ── */}
        <div className="lg:col-span-8 space-y-5">
          {/* 용해로 실시간 온도 그래프 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Thermometer className="w-5 h-5 text-red-500" />
                용해로 실시간 온도
              </h3>
              <div className="flex items-center gap-3 text-sm">
                <span className="flex items-center gap-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
                  현재: <strong className="text-red-600">{meltingStage?.temperature ?? "-"}°C</strong>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                  목표: <strong className="text-blue-600">{meltingStage?.targetTemperature ?? "-"}°C</strong>
                </span>
                <span className="flex items-center gap-1">
                  <Gauge className="w-3.5 h-3.5 text-amber-500" />
                  가열 출력: <strong className="text-amber-600">{meltingStage?.heatingPower ?? "-"}%</strong>
                </span>
              </div>
            </div>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={tempTimelineData}>
                  <defs>
                    <linearGradient id="gradTemp" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="time" tick={{ fontSize: 10 }} interval={4} />
                  <YAxis domain={[1100, 1500]} tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ fontSize: 12, borderRadius: 8 }}
                    formatter={(value) => [`${value}°C`]}
                  />
                  <ReferenceLine
                    y={meltingStage?.targetTemperature ?? 1450}
                    stroke="#3b82f6"
                    strokeDasharray="6 3"
                    label={{
                      value: "목표",
                      position: "right",
                      fill: "#3b82f6",
                      fontSize: 10,
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="현재온도"
                    stroke="#ef4444"
                    strokeWidth={2}
                    fill="url(#gradTemp)"
                  />
                  <Area
                    type="monotone"
                    dataKey="목표온도"
                    stroke="#3b82f6"
                    strokeWidth={1.5}
                    strokeDasharray="4 2"
                    fill="none"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 조형/주탕 실시간 수치 + 시간별 생산량 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* 조형/주탕 현재 공정 수치 */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
                <Layers className="w-5 h-5 text-indigo-500" />
                조형 / 주탕 공정 데이터
              </h3>
              <div className="space-y-4">
                {/* 패턴 정보 */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <span className="text-sm text-gray-500">현재 패턴</span>
                  <p className="text-base font-semibold text-gray-800 mt-0.5">
                    맨홀 뚜껑 KS D-600 ({moldingStage?.equipmentId})
                  </p>
                </div>

                {/* 성형 압력 */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-500 flex items-center gap-1">
                      <Gauge className="w-3.5 h-3.5" />
                      성형 압력
                    </span>
                    <span className="text-xl font-bold text-indigo-600">
                      {moldingStage?.pressure ?? "-"}{" "}
                      <span className="text-sm font-normal text-gray-400">bar</span>
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-500 rounded-full h-2 transition-all"
                      style={{
                        width: `${Math.min(100, ((moldingStage?.pressure ?? 0) / 120) * 100)}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
                    <span>0</span>
                    <span>120 bar</span>
                  </div>
                </div>

                {/* 주탕 각도 */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-500 flex items-center gap-1">
                      <ArrowRightLeft className="w-3.5 h-3.5" />
                      주탕 각도
                    </span>
                    <span className="text-xl font-bold text-teal-600">
                      {pouringStage?.pourAngle ?? "-"}
                      <span className="text-sm font-normal text-gray-400">°</span>
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-teal-500 rounded-full h-2 transition-all"
                      style={{
                        width: `${Math.min(100, ((pouringStage?.pourAngle ?? 0) / 90) * 100)}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
                    <span>0°</span>
                    <span>90°</span>
                  </div>
                </div>

                {/* 주탕 온도 */}
                <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                  <span className="text-sm text-gray-500">주탕 온도</span>
                  <span className="text-base font-bold text-orange-600">
                    {pouringStage?.temperature ?? "-"}°C
                  </span>
                </div>
              </div>
            </div>

            {/* 시간별 생산량 차트 */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
                <BarChart3 className="w-5 h-5 text-emerald-500" />
                시간별 생산량
              </h3>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChartComponent data={hourlyProduction}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="hour" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8 }}
                    />
                    <Legend
                      wrapperStyle={{ fontSize: 11 }}
                      iconSize={10}
                    />
                    <Bar
                      dataKey="production"
                      name="생산량"
                      fill="#10b981"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar
                      dataKey="defects"
                      name="불량"
                      fill="#f43f5e"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChartComponent>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
                <span>
                  금일 총 생산:{" "}
                  <strong className="text-gray-800">
                    {hourlyProduction.reduce(
                      (sum, h) => sum + h.production,
                      0
                    )}
                    개
                  </strong>
                </span>
                <span>
                  금일 불량:{" "}
                  <strong className="text-red-600">
                    {hourlyProduction.reduce(
                      (sum, h) => sum + h.defects,
                      0
                    )}
                    개
                  </strong>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* ── 우측: 설비 제어 패널 ── */}
        <div className="lg:col-span-4 flex flex-col gap-5">
          {/* 비상 정지 버튼 */}
          <button
            type="button"
            className="w-full bg-red-600 hover:bg-red-700 active:bg-red-800 text-white rounded-xl border-2 border-red-700 p-5 flex items-center justify-center gap-3 shadow-lg shadow-red-200 transition-all"
            onClick={() => alert("비상 정지가 요청되었습니다.")}
          >
            <OctagonX className="w-7 h-7" />
            <span className="text-xl font-bold tracking-wide">
              비상 정지 (E-STOP)
            </span>
          </button>

          {/* 냉각 진행률 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <Wind className="w-5 h-5 text-cyan-500" />
              냉각 진행률
            </h3>
            <div className="flex items-center gap-4">
              {/* 원형 진행률 */}
              <div className="relative w-20 h-20 flex-shrink-0">
                <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
                  <circle
                    cx="40"
                    cy="40"
                    r="34"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="34"
                    stroke="#06b6d4"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${(coolingProgress / 100) * 213.6} 213.6`}
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-base font-bold text-cyan-700">
                  {coolingProgress}%
                </span>
              </div>
              <div className="space-y-1.5 text-sm flex-1">
                <div className="flex justify-between">
                  <span className="text-gray-500">현재 온도</span>
                  <span className="font-semibold text-gray-800">
                    {coolingStage?.temperature ?? "-"}°C
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">목표 온도</span>
                  <span className="font-semibold text-gray-800">
                    {coolingStage?.targetTemperature ?? "-"}°C
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 flex items-center gap-1">
                    <Timer className="w-3 h-3" />
                    잔여 시간
                  </span>
                  <span className="font-semibold text-cyan-700">
                    약 {coolingRemainingMin > 0 ? `${coolingRemainingMin}분` : "완료 임박"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 설비별 상태 제어 패널 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex-1 flex flex-col min-h-0">
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <Settings className="w-5 h-5 text-gray-500" />
              설비 제어
            </h3>
            <div className="space-y-3 overflow-y-auto pr-1 flex-1 min-h-0">
              {equipmentList.map((eq) => {
                const currentStatus = equipmentStatuses[eq.id] ?? eq.status;
                const statusInfo = equipmentStatusMap[currentStatus];
                const isAuto = autoModes[eq.id] ?? true;
                const validStates = equipmentValidStates[eq.type] ?? ["running", "idle"];
                const isChanged = recentlyChanged === eq.id;

                return (
                  <div
                    key={eq.id}
                    className={cn(
                      "bg-gray-50 rounded-lg px-3 py-3 transition-all duration-300",
                      isChanged && "ring-2 ring-blue-400 bg-blue-50"
                    )}
                  >
                    {/* 상단: 이름, 타입 아이콘, 상태 배지, 토글 */}
                    <div className="flex items-center justify-between">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500 flex-shrink-0">
                            {equipmentTypeIcon[eq.type]}
                          </span>
                          <span className="text-sm font-semibold text-gray-800 truncate">
                            {eq.name}
                          </span>
                          <span
                            className={cn(
                              "px-2 py-0.5 rounded-full text-xs font-semibold transition-all duration-300",
                              statusInfo.color
                            )}
                          >
                            {statusInfo.label}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <div className="flex items-center gap-1 text-[10px] text-gray-400">
                            <MapPin className="w-2.5 h-2.5" />
                            {eq.installLocation}
                          </div>
                          {/* AMR 배터리 표시 */}
                          {eq.type === "amr" && eq.battery != null && (
                            <div className="flex items-center gap-1 text-[10px]">
                              <BatteryMedium className={cn(
                                "w-3 h-3",
                                eq.battery > 50 ? "text-green-500" : eq.battery > 20 ? "text-yellow-500" : "text-red-500"
                              )} />
                              <span className={cn(
                                "font-semibold",
                                eq.battery > 50 ? "text-green-600" : eq.battery > 20 ? "text-yellow-600" : "text-red-600"
                              )}>
                                {eq.battery}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      {/* Auto/Manual 토글 스위치 */}
                      <button
                        type="button"
                        onClick={() => toggleMode(eq.id)}
                        className={cn(
                          "relative w-14 h-7 rounded-full transition-colors flex-shrink-0 ml-2",
                          isAuto ? "bg-blue-500" : "bg-gray-300"
                        )}
                      >
                        <span
                          className={cn(
                            "absolute top-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform",
                            isAuto ? "translate-x-7" : "translate-x-0.5"
                          )}
                        />
                        <span
                          className={cn(
                            "absolute text-[9px] font-bold top-1/2 -translate-y-1/2",
                            isAuto
                              ? "left-1.5 text-white"
                              : "right-1 text-gray-500"
                          )}
                        >
                          {isAuto ? "자동" : "수동"}
                        </span>
                      </button>
                    </div>

                    {/* 하단: 상태 변경 버튼 그룹 */}
                    <div className="flex items-center gap-1.5 mt-2">
                      {validStates.map((st) => {
                        const isActive = currentStatus === st;
                        const style = statusButtonStyle[st];
                        const label = equipmentStatusMap[st].label;

                        return (
                          <button
                            key={st}
                            type="button"
                            onClick={() => changeEquipmentStatus(eq.id, st)}
                            disabled={isActive}
                            className={cn(
                              "px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all duration-200 cursor-pointer",
                              isActive ? style.active : style.inactive,
                              isActive && "cursor-default"
                            )}
                          >
                            {label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* ====== 3. 하단: 공정 파라미터 이력 테이블 ====== */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
          <ClipboardList className="w-5 h-5 text-indigo-500" />
          공정 파라미터 이력
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-100">
                <th className="text-left py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider rounded-tl-lg">공정</th>
                <th className="text-left py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">설비 ID</th>
                <th className="text-left py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">상태</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">온도 (°C)</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">목표 온도 (°C)</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">압력 (bar)</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">주탕 각도 (°)</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">가열 출력 (%)</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">냉각률 (%)</th>
                <th className="text-right py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">진행률</th>
                <th className="text-left py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider">시작 시간</th>
                <th className="text-left py-2.5 px-3 font-semibold text-gray-600 uppercase tracking-wider rounded-tr-lg">확정 완료</th>
              </tr>
            </thead>
            <tbody>
              {processStages.map((stage) => {
                const statusInfo = processStatusMap[stage.status];
                return (
                  <tr
                    key={stage.stage}
                    className="border-b border-gray-100 even:bg-gray-50 hover:bg-blue-50 transition-colors"
                  >
                    <td className="py-2.5 px-3 font-semibold text-gray-800">
                      {stage.label}
                    </td>
                    <td className="py-2.5 px-3 text-gray-600 font-mono">
                      {stage.equipmentId}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="flex items-center gap-1.5">
                        <span
                          className={cn(
                            "w-2 h-2 rounded-full",
                            statusInfo.dot
                          )}
                        />
                        <span className={cn("font-medium", statusInfo.color)}>
                          {statusInfo.label}
                        </span>
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">
                      {stage.temperature ?? "-"}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">
                      {stage.targetTemperature ?? "-"}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">
                      {stage.pressure ?? "-"}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">
                      {stage.pourAngle ?? "-"}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">
                      {stage.heatingPower ?? "-"}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">
                      {stage.coolingProgress ?? "-"}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <div className="w-12 bg-gray-200 rounded-full h-1.5">
                          <div
                            className={cn(
                              "h-1.5 rounded-full",
                              stage.status === "error"
                                ? "bg-red-500"
                                : stage.status === "running"
                                ? "bg-blue-500"
                                : stage.status === "completed"
                                ? "bg-green-500"
                                : "bg-gray-400"
                            )}
                            style={{ width: `${stage.progress}%` }}
                          />
                        </div>
                        <span className="font-mono w-8 text-right">
                          {stage.progress}%
                        </span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3 text-gray-500">
                      {stage.startTime ? formatDate(stage.startTime) : "-"}
                    </td>
                    <td className="py-2.5 px-3 text-gray-500">
                      {stage.estimatedEnd ? formatDate(stage.estimatedEnd) : "-"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
