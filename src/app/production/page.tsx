"use client";

import { useState } from "react";
import {
  Thermometer,
  Cpu,
  AlertTriangle,
  Circle,
  ChevronRight,
  Flame,
  Layers,
  Droplets,
  Wind,
  Wrench,
  Eye,
  Package,
  Zap,
  Camera,
  Bot,
} from "lucide-react";
import { mockProcessStages, mockEquipment } from "@/lib/mock-data";
import type { EquipmentType, ProcessStatus } from "@/lib/types";
import { cn, processStatusMap, equipmentStatusMap } from "@/lib/utils";

// 공정 단계 순서 정의
const STAGE_ORDER = [
  "melting",
  "molding",
  "pouring",
  "cooling",
  "demolding",
  "post_processing",
  "inspection",
  "classification",
];

// 장비 타입별 아이콘 매핑
function EquipmentIcon({ type, className }: { type: EquipmentType; className?: string }) {
  const props = { className: cn("h-5 w-5", className) };
  switch (type) {
    case "furnace":
      return <Flame {...props} />;
    case "mold_press":
      return <Layers {...props} />;
    case "robot_arm":
      return <Bot {...props} />;
    case "amr":
      return <Cpu {...props} />;
    case "conveyor":
      // lucide-react에 ConveyorBelt가 없을 수 있으므로 Package로 대체
      return <Package {...props} />;
    case "camera":
      return <Camera {...props} />;
    default:
      return <Wrench {...props} />;
  }
}

// 공정 단계 아이콘 매핑
function StageIcon({ stage, className }: { stage: string; className?: string }) {
  const props = { className: cn("h-5 w-5", className) };
  switch (stage) {
    case "melting":
      return <Flame {...props} />;
    case "molding":
      return <Layers {...props} />;
    case "pouring":
      return <Droplets {...props} />;
    case "cooling":
      return <Wind {...props} />;
    case "demolding":
      return <Wrench {...props} />;
    case "post_processing":
      return <Zap {...props} />;
    case "inspection":
      return <Eye {...props} />;
    case "classification":
      return <Package {...props} />;
    default:
      return <Circle {...props} />;
  }
}

// 상태 인디케이터 컴포넌트
function StatusDot({ status }: { status: ProcessStatus }) {
  const { dot, label, color } = processStatusMap[status];
  return (
    <span className="flex items-center gap-1.5">
      <span className={cn("inline-block h-2.5 w-2.5 rounded-full", dot)} />
      <span className={cn("text-xs font-medium", color)}>{label}</span>
    </span>
  );
}

// 진행률 바 컴포넌트
function ProgressBar({ progress, status }: { progress: number; status: ProcessStatus }) {
  const barColor: Record<ProcessStatus, string> = {
    idle: "bg-gray-300",
    running: "bg-blue-500",
    completed: "bg-green-500",
    error: "bg-red-500",
    waiting: "bg-amber-400",
  };

  return (
    <div className="h-1.5 w-full rounded-full bg-gray-700">
      <div
        className={cn("h-1.5 rounded-full transition-all duration-500", barColor[status])}
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

export default function ProductionPage() {
  const [activeZone, setActiveZone] = useState<string>("전체");

  // 공정 단계를 STAGE_ORDER 기준으로 정렬
  const sortedStages = [...mockProcessStages].sort(
    (a, b) => STAGE_ORDER.indexOf(a.stage) - STAGE_ORDER.indexOf(b.stage)
  );

  // 장비 구역 목록
  const zones = ["전체", ...Array.from(new Set(mockEquipment.map((e) => e.zone)))];

  // 필터링된 장비
  const filteredEquipment =
    activeZone === "전체"
      ? mockEquipment
      : mockEquipment.filter((e) => e.zone === activeZone);

  // 온도 데이터가 있는 공정 단계만 필터링
  const tempStages = sortedStages.filter(
    (s) => s.temperature !== undefined && s.targetTemperature !== undefined
  );

  return (
    <div className="space-y-6">
      {/* 페이지 헤더 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">생산 공정 모니터링</h1>
        <p className="mt-1 text-sm text-gray-500">
          주물 생산 8단계 공정의 실시간 상태를 모니터링합니다.
        </p>
      </div>

      {/* ===== 1. 공정 흐름도 ===== */}
      <section>
        <h2 className="mb-3 text-base font-semibold text-gray-800">공정 흐름도</h2>
        <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          {/* 수평 스크롤 가능한 공정 흐름 */}
          <div className="overflow-x-auto pb-2">
            <div className="flex min-w-max items-stretch gap-0">
              {sortedStages.map((stage, idx) => {
                const isActive = stage.status === "running";
                const isCompleted = stage.status === "completed";
                const isError = stage.status === "error";

                return (
                  <div key={stage.stage} className="flex items-center">
                    {/* 공정 카드 */}
                    <div
                      className={cn(
                        "relative w-36 rounded-lg border p-3 transition-all",
                        isActive &&
                          "border-blue-400 bg-blue-950 shadow-lg shadow-blue-500/20 ring-1 ring-blue-500",
                        isCompleted && "border-green-700 bg-green-950",
                        isError && "border-red-400 bg-red-950",
                        !isActive &&
                          !isCompleted &&
                          !isError &&
                          "border-gray-700 bg-gray-800"
                      )}
                    >
                      {/* 활성 공정 펄스 효과 */}
                      {isActive && (
                        <span className="absolute -top-1 -right-1 h-3 w-3">
                          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75" />
                          <span className="relative inline-flex h-3 w-3 rounded-full bg-blue-500" />
                        </span>
                      )}

                      {/* 단계 헤더 */}
                      <div className="mb-2 flex items-center gap-1.5">
                        <StageIcon
                          stage={stage.stage}
                          className={cn(
                            isActive && "text-blue-400",
                            isCompleted && "text-green-400",
                            isError && "text-red-400",
                            !isActive && !isCompleted && !isError && "text-gray-400"
                          )}
                        />
                        <span
                          className={cn(
                            "text-sm font-semibold",
                            isActive && "text-blue-100",
                            isCompleted && "text-green-100",
                            isError && "text-red-100",
                            !isActive && !isCompleted && !isError && "text-gray-300"
                          )}
                        >
                          {stage.label}
                        </span>
                      </div>

                      {/* 상태 인디케이터 */}
                      <StatusDot status={stage.status} />

                      {/* 진행률 바 */}
                      <div className="mt-2">
                        <ProgressBar progress={stage.progress} status={stage.status} />
                        <div className="mt-0.5 flex justify-between">
                          <span className="text-xs text-gray-500">{stage.progress}%</span>
                        </div>
                      </div>

                      {/* 온도 표시 (있는 경우) */}
                      {stage.temperature !== undefined && (
                        <div className="mt-2 flex items-center gap-1">
                          <Thermometer className="h-3 w-3 text-orange-400" />
                          <span className="text-xs font-mono text-orange-300">
                            {stage.temperature}°C
                          </span>
                        </div>
                      )}
                    </div>

                    {/* 화살표 연결 */}
                    {idx < sortedStages.length - 1 && (
                      <ChevronRight className="mx-0.5 h-5 w-5 shrink-0 text-gray-600" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 범례 */}
          <div className="mt-3 flex flex-wrap gap-4 border-t border-gray-100 pt-3">
            {(["running", "completed", "waiting", "idle", "error"] as ProcessStatus[]).map(
              (s) => (
                <div key={s} className="flex items-center gap-1.5">
                  <span
                    className={cn("inline-block h-2 w-2 rounded-full", processStatusMap[s].dot)}
                  />
                  <span className="text-xs text-gray-500">{processStatusMap[s].label}</span>
                </div>
              )
            )}
          </div>
        </div>
      </section>

      {/* ===== 2 & 3: 장비 현황 + 공정 제어 (2컬럼) ===== */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* ===== 2. 장비 현황 ===== */}
        <section className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold text-gray-800">장비 현황</h2>
            {/* 구역 필터 탭 */}
            <div className="flex flex-wrap gap-1">
              {zones.map((zone) => (
                <button
                  key={zone}
                  onClick={() => setActiveZone(zone)}
                  className={cn(
                    "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                    activeZone === zone
                      ? "bg-gray-900 text-white"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  )}
                >
                  {zone}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {filteredEquipment.map((equipment) => {
              const statusInfo = equipmentStatusMap[equipment.status];
              const isRunning = equipment.status === "running";
              const isError = equipment.status === "error";

              return (
                <div
                  key={equipment.id}
                  className={cn(
                    "rounded-xl border p-4 transition-all",
                    isRunning && "border-gray-700 bg-gray-800",
                    isError && "border-red-800 bg-red-950",
                    !isRunning && !isError && "border-gray-700 bg-gray-800/50"
                  )}
                >
                  {/* 카드 헤더 */}
                  <div className="mb-3 flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className={cn(
                          "flex h-9 w-9 items-center justify-center rounded-lg",
                          isRunning && "bg-green-900",
                          isError && "bg-red-900",
                          !isRunning && !isError && "bg-gray-700"
                        )}
                      >
                        <EquipmentIcon
                          type={equipment.type}
                          className={cn(
                            isRunning && "text-green-400",
                            isError && "text-red-400",
                            !isRunning && !isError && "text-gray-400"
                          )}
                        />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-100">{equipment.name}</p>
                        <p className="text-xs text-gray-400">{equipment.id}</p>
                      </div>
                    </div>

                    {/* 상태 배지 */}
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-xs font-medium",
                        equipment.status === "running" && "bg-green-900 text-green-300",
                        equipment.status === "idle" && "bg-gray-700 text-gray-300",
                        equipment.status === "error" && "bg-red-900 text-red-300",
                        equipment.status === "maintenance" && "bg-yellow-900 text-yellow-300",
                        equipment.status === "charging" && "bg-blue-900 text-blue-300"
                      )}
                    >
                      {statusInfo.label}
                    </span>
                  </div>

                  {/* 장비 정보 */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">구역</span>
                      <span className="font-medium text-gray-200">{equipment.zone}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">가동 시간</span>
                      <span className="font-mono font-medium text-gray-200">
                        {equipment.operatingHours.toLocaleString()}h
                      </span>
                    </div>
                    {equipment.errorCount > 0 && (
                      <div className="flex items-center gap-1 rounded-md bg-red-900/50 px-2 py-1">
                        <AlertTriangle className="h-3 w-3 text-red-400" />
                        <span className="text-xs text-red-300">오류 발생 {equipment.errorCount}건</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* ===== 3. 공정 제어 패널 ===== */}
        <section>
          <h2 className="mb-3 text-base font-semibold text-gray-800">공정 제어</h2>
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            {/* 구역별 제어 */}
            <div className="space-y-4">
              {[
                { label: "용해 구역", zone: "melting" },
                { label: "주조 구역", zone: "pouring" },
                { label: "냉각 구역", zone: "cooling" },
                { label: "후처리 구역", zone: "processing" },
              ].map(({ label }) => (
                <div key={label} className="rounded-lg bg-gray-50 p-3">
                  <p className="mb-2 text-xs font-semibold text-gray-600">{label}</p>
                  <div className="flex gap-2">
                    <button
                      className="flex-1 rounded-md bg-green-600 px-2 py-1.5 text-xs font-medium text-white transition-colors hover:bg-green-700 active:bg-green-800"
                      onClick={() => {}}
                    >
                      시작
                    </button>
                    <button
                      className="flex-1 rounded-md bg-gray-500 px-2 py-1.5 text-xs font-medium text-white transition-colors hover:bg-gray-600 active:bg-gray-700"
                      onClick={() => {}}
                    >
                      중지
                    </button>
                    <button
                      className="flex-1 rounded-md bg-blue-600 px-2 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-700 active:bg-blue-800"
                      onClick={() => {}}
                    >
                      재개
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* 비상 정지 버튼 */}
            <div className="mt-6">
              <p className="mb-2 text-center text-xs font-medium text-gray-500">비상 정지</p>
              <button
                className="group relative w-full overflow-hidden rounded-xl border-2 border-red-700 bg-red-600 py-4 font-bold text-white shadow-lg shadow-red-600/30 transition-all hover:bg-red-700 hover:shadow-red-600/50 active:scale-95"
                onClick={() => {}}
              >
                {/* 경고 줄무늬 패턴 */}
                <div className="absolute inset-0 opacity-10">
                  <div
                    className="h-full w-full"
                    style={{
                      backgroundImage:
                        "repeating-linear-gradient(45deg, #000 0, #000 10px, transparent 10px, transparent 20px)",
                    }}
                  />
                </div>
                <div className="relative flex items-center justify-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="text-base tracking-wide">전체 공정 비상 정지</span>
                </div>
              </button>
              <p className="mt-2 text-center text-xs text-gray-400">
                모든 공정을 즉시 중단합니다
              </p>
            </div>
          </div>
        </section>
      </div>

      {/* ===== 4. 온도 모니터링 ===== */}
      <section>
        <h2 className="mb-3 text-base font-semibold text-gray-800">온도 모니터링</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {tempStages.map((stage) => {
            const temp = stage.temperature!;
            const target = stage.targetTemperature!;
            // 진행률: 용해 공정은 목표온도에 가까울수록 좋고, 냉각 공정은 낮아질수록 좋음
            const isCooling = stage.stage === "cooling";
            const ratio = isCooling
              ? Math.max(0, Math.min(100, ((target + 100 - temp) / (target + 100)) * 100))
              : Math.max(0, Math.min(100, (temp / target) * 100));

            const isOver = !isCooling && temp > target;
            const isUnder = !isCooling && temp < target * 0.9;

            return (
              <div
                key={stage.stage}
                className="rounded-xl border border-gray-700 bg-gray-800 p-4"
              >
                {/* 헤더 */}
                <div className="mb-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <StageIcon stage={stage.stage} className="h-4 w-4 text-orange-400" />
                    <span className="text-sm font-semibold text-gray-200">{stage.label}</span>
                  </div>
                  {isOver ? (
                    <span className="rounded-full bg-red-900 px-2 py-0.5 text-xs text-red-300">
                      초과
                    </span>
                  ) : isUnder ? (
                    <span className="rounded-full bg-amber-900 px-2 py-0.5 text-xs text-amber-300">
                      미달
                    </span>
                  ) : (
                    <span className="rounded-full bg-green-900 px-2 py-0.5 text-xs text-green-300">
                      정상
                    </span>
                  )}
                </div>

                {/* 현재 온도 */}
                <div className="mb-3 text-center">
                  <div className="flex items-end justify-center gap-1">
                    <span
                      className={cn(
                        "text-3xl font-bold font-mono tabular-nums",
                        isOver ? "text-red-400" : isUnder ? "text-amber-400" : "text-orange-300"
                      )}
                    >
                      {temp.toLocaleString()}
                    </span>
                    <span className="mb-1 text-base text-gray-400">°C</span>
                  </div>
                  <div className="flex items-center justify-center gap-1 text-xs text-gray-500">
                    <span>목표</span>
                    <span className="font-mono font-semibold text-gray-300">
                      {target.toLocaleString()}°C
                    </span>
                  </div>
                </div>

                {/* 온도 게이지 바 */}
                <div className="space-y-1.5">
                  <div className="relative h-3 w-full overflow-hidden rounded-full bg-gray-700">
                    {/* 목표 온도 마커 */}
                    <div
                      className="absolute top-0 z-10 h-full w-0.5 bg-white/60"
                      style={{ left: isCooling ? "10%" : "90%" }}
                    />
                    {/* 현재 온도 바 */}
                    <div
                      className={cn(
                        "h-full rounded-full transition-all duration-700",
                        isOver
                          ? "bg-gradient-to-r from-orange-500 to-red-500"
                          : isUnder
                          ? "bg-gradient-to-r from-blue-500 to-amber-400"
                          : "bg-gradient-to-r from-orange-400 to-orange-600"
                      )}
                      style={{ width: `${Math.min(100, ratio)}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>0°C</span>
                    <span>{isCooling ? "상온" : "목표"}</span>
                    <span>{isCooling ? `${temp}°C` : `${target}°C`}</span>
                  </div>
                </div>

                {/* 장비 ID */}
                <div className="mt-2 flex items-center gap-1 text-xs text-gray-500">
                  <Cpu className="h-3 w-3" />
                  <span>{stage.equipmentId}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
