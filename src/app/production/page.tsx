"use client";

import { useState } from "react";
import FactoryMap from "@/components/FactoryMap";
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
  MapPin,
  Settings,
  RotateCw,
} from "lucide-react";
import { mockProcessStages, mockEquipment } from "@/lib/mock-data";
import type { EquipmentType, ProcessStatus, Equipment } from "@/lib/types";
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

// 공장 레이아웃 구역 정의 (3x3 그리드)
const FACTORY_ZONES = [
  // row 0
  { id: "raw_material", label: "원자재 보관 구역", row: 0, col: 0, zoneKey: "원자재 구역" },
  { id: "melting", label: "용해 구역", row: 0, col: 1, zoneKey: "용해 구역" },
  { id: "molding", label: "주형 구역", row: 0, col: 2, zoneKey: "주형 구역" },
  // row 1
  { id: "pouring", label: "주조 구역", row: 1, col: 0, zoneKey: "주조 구역" },
  { id: "cooling", label: "냉각 구역", row: 1, col: 1, zoneKey: "냉각 구역" },
  { id: "demolding", label: "탈형 구역", row: 1, col: 2, zoneKey: "탈형 구역" },
  // row 2
  { id: "post_processing", label: "후처리 구역", row: 2, col: 0, zoneKey: "후처리 구역" },
  { id: "inspection", label: "검사 구역", row: 2, col: 1, zoneKey: "검사 구역" },
  { id: "shipping", label: "적재/출고 구역", row: 2, col: 2, zoneKey: "적재 구역" },
];

// AMR 위치 데이터
const AMR_POSITIONS = [
  { id: "AMR-001", label: "AMR-001", status: "moving", color: "bg-blue-400", description: "이송 중" },
  { id: "AMR-002", label: "AMR-002", status: "idle", color: "bg-gray-400", description: "대기 중" },
  { id: "AMR-003", label: "AMR-003", status: "charging", color: "bg-yellow-400", description: "충전 중" },
];

// 구역별 장비 매핑 함수
function getEquipmentForZone(zoneKey: string): Equipment[] {
  return mockEquipment.filter((e) => e.zone === zoneKey);
}

// 구역 상태 계산 (장비 상태 기반)
function getZoneStatus(zoneKey: string): "active" | "idle" | "error" {
  const equipment = getEquipmentForZone(zoneKey);
  if (equipment.some((e) => e.status === "error")) return "error";
  if (equipment.some((e) => e.status === "running")) return "active";
  return "idle";
}

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

// 구역 팝오버 컴포넌트
function ZonePopover({
  zoneLabel,
  zoneKey,
  onClose,
}: {
  zoneLabel: string;
  zoneKey: string;
  onClose: () => void;
}) {
  const equipment = getEquipmentForZone(zoneKey);
  return (
    <div className="absolute z-50 left-1/2 -translate-x-1/2 top-full mt-2 w-56 rounded-lg border border-gray-600 bg-gray-900 p-3 shadow-xl">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-200">{zoneLabel}</span>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-300 text-xs">
          닫기
        </button>
      </div>
      {equipment.length === 0 ? (
        <p className="text-xs text-gray-500">장비 없음</p>
      ) : (
        <ul className="space-y-1.5">
          {equipment.map((eq) => {
            const statusInfo = equipmentStatusMap[eq.status];
            return (
              <li key={eq.id} className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <EquipmentIcon type={eq.type} className="h-3.5 w-3.5 text-gray-400" />
                  <span className="text-xs text-gray-300">{eq.name}</span>
                </div>
                <span
                  className={cn(
                    "rounded-full px-1.5 py-0.5 text-xs font-medium",
                    eq.status === "running" && "bg-green-900 text-green-300",
                    eq.status === "idle" && "bg-gray-700 text-gray-300",
                    eq.status === "error" && "bg-red-900 text-red-300",
                    eq.status === "maintenance" && "bg-yellow-900 text-yellow-300",
                    eq.status === "charging" && "bg-blue-900 text-blue-300"
                  )}
                >
                  {statusInfo.label}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default function ProductionPage() {
  const [activeZone, setActiveZone] = useState<string>("전체");
  const [openPopoverZone, setOpenPopoverZone] = useState<string | null>(null);
  // 컨베이어 제어 상태
  const [conveyorSpeed, setConveyorSpeed] = useState<number>(65);
  const [conveyorMode, setConveyorMode] = useState<"auto" | "manual">("auto");
  const [conveyorRunning, setConveyorRunning] = useState<boolean>(true);
  // 분류 장치 상태 (0도 = 양품, 45도 = 불량품)
  const [sorterAngle, setSorterAngle] = useState<number>(0);

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

      {/* ===== 0. 공정 레이아웃 Map ===== */}
      <section>
        <h2 className="mb-3 text-base font-semibold text-gray-800">공정 레이아웃 Map</h2>
        <FactoryMap />
      </section>

      {/* ===== OLD MAP REPLACED ===== */}
      <section className="hidden">
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-5 shadow-sm">
          {/* 범례 */}
          <div className="mb-4 flex flex-wrap items-center gap-4">
            <span className="text-xs font-medium text-gray-400">구역 상태</span>
            <div className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-sm bg-green-700 ring-1 ring-green-500" />
              <span className="text-xs text-gray-400">가동 중</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-sm bg-gray-700 ring-1 ring-gray-500" />
              <span className="text-xs text-gray-400">대기</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-sm bg-red-900 ring-1 ring-red-500" />
              <span className="text-xs text-gray-400">오류</span>
            </div>
            <span className="ml-auto text-xs text-gray-500">구역 클릭 시 장비 상세 확인</span>
          </div>

          {/* 3x3 공장 레이아웃 그리드 */}
          <div className="grid grid-cols-3 gap-3">
            {FACTORY_ZONES.map((zone) => {
              const zoneStatus = getZoneStatus(zone.zoneKey);
              const equipment = getEquipmentForZone(zone.zoneKey);
              const isOpen = openPopoverZone === zone.id;

              return (
                <div key={zone.id} className="relative">
                  <button
                    onClick={() => setOpenPopoverZone(isOpen ? null : zone.id)}
                    className={cn(
                      "w-full rounded-lg border p-3 text-left transition-all hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-blue-500",
                      zoneStatus === "active" &&
                        "border-green-600 bg-green-900/40 shadow-lg shadow-green-900/20",
                      zoneStatus === "idle" && "border-gray-600 bg-gray-800",
                      zoneStatus === "error" && "border-red-600 bg-red-900/40"
                    )}
                  >
                    {/* 구역 헤더 */}
                    <div className="mb-2 flex items-center justify-between">
                      <span
                        className={cn(
                          "text-xs font-semibold leading-tight",
                          zoneStatus === "active" && "text-green-200",
                          zoneStatus === "idle" && "text-gray-300",
                          zoneStatus === "error" && "text-red-200"
                        )}
                      >
                        {zone.label}
                      </span>
                      {/* 상태 표시등 */}
                      <span
                        className={cn(
                          "inline-block h-2.5 w-2.5 rounded-full",
                          zoneStatus === "active" && "bg-green-400 shadow-sm shadow-green-400",
                          zoneStatus === "idle" && "bg-gray-500",
                          zoneStatus === "error" && "bg-red-400 animate-pulse"
                        )}
                      />
                    </div>

                    {/* 장비 아이콘 도트 (최대 4개) */}
                    <div className="flex flex-wrap gap-1">
                      {equipment.slice(0, 4).map((eq) => (
                        <span
                          key={eq.id}
                          className={cn(
                            "inline-flex h-4 w-4 items-center justify-center rounded-full",
                            eq.status === "running" && "bg-green-700",
                            eq.status === "idle" && "bg-gray-700",
                            eq.status === "error" && "bg-red-700",
                            eq.status === "maintenance" && "bg-yellow-700",
                            eq.status === "charging" && "bg-blue-700"
                          )}
                          title={eq.name}
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-current opacity-70" />
                        </span>
                      ))}
                      {equipment.length === 0 && (
                        <span className="text-xs text-gray-600">-</span>
                      )}
                    </div>

                    {/* 장비 수 */}
                    {equipment.length > 0 && (
                      <p className="mt-1.5 text-xs text-gray-500">
                        장비 {equipment.length}대
                      </p>
                    )}
                  </button>

                  {/* 팝오버 */}
                  {isOpen && (
                    <ZonePopover
                      zoneLabel={zone.label}
                      zoneKey={zone.zoneKey}
                      onClose={() => setOpenPopoverZone(null)}
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* AMR 위치 표시 패널 */}
          <div className="mt-5 rounded-lg border border-gray-700 bg-gray-800 p-3">
            <div className="mb-2 flex items-center gap-2">
              <Cpu className="h-4 w-4 text-blue-400" />
              <span className="text-xs font-semibold text-gray-300">AMR 현재 위치</span>
            </div>
            <div className="flex flex-wrap gap-3">
              {AMR_POSITIONS.map((amr) => (
                <div
                  key={amr.id}
                  className="flex items-center gap-2 rounded-md bg-gray-700/60 px-3 py-1.5"
                >
                  {/* AMR 애니메이션 도트 */}
                  <span className="relative inline-flex h-3 w-3">
                    {amr.status === "moving" && (
                      <span
                        className={cn(
                          "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
                          amr.color
                        )}
                      />
                    )}
                    <span
                      className={cn(
                        "relative inline-flex h-3 w-3 rounded-full",
                        amr.color
                      )}
                    />
                  </span>
                  <div>
                    <p className="text-xs font-semibold text-gray-200">{amr.label}</p>
                    <p className="text-xs text-gray-400">{amr.description}</p>
                  </div>
                  <MapPin className="ml-1 h-3 w-3 text-gray-500" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

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
                        "relative w-40 h-36 rounded-lg border p-3 transition-all flex flex-col",
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
                      <div className="mt-2 flex-1">
                        <ProgressBar progress={stage.progress} status={stage.status} />
                        <div className="mt-0.5 flex justify-between">
                          <span className="text-xs text-gray-500">{stage.progress}%</span>
                        </div>
                      </div>

                      {/* 온도 표시 (있는 경우, 없으면 빈 공간) */}
                      <div className="mt-auto pt-1">
                        {stage.temperature !== undefined ? (
                          <div className="flex items-center gap-1">
                            <Thermometer className="h-3 w-3 text-orange-400" />
                            <span className="text-xs font-mono text-orange-300">
                              {stage.temperature}°C
                            </span>
                          </div>
                        ) : (
                          <div className="h-4" />
                        )}
                      </div>
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
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm space-y-5">
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

            {/* 컨베이어 제어 패널 */}
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <div className="mb-3 flex items-center gap-2">
                <Settings className="h-4 w-4 text-gray-600" />
                <p className="text-xs font-semibold text-gray-700">컨베이어 제어 패널</p>
              </div>

              {/* 컨베이어 속도 슬라이더 */}
              <div className="mb-3">
                <div className="mb-1 flex items-center justify-between">
                  <label className="text-xs text-gray-500">컨베이어 속도</label>
                  <span className="text-xs font-mono font-semibold text-gray-700">
                    {conveyorSpeed}%
                  </span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={100}
                  value={conveyorSpeed}
                  onChange={(e) => setConveyorSpeed(Number(e.target.value))}
                  className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-gray-300 accent-blue-600"
                />
                <div className="mt-0.5 flex justify-between text-xs text-gray-400">
                  <span>1%</span>
                  <span>100%</span>
                </div>
              </div>

              {/* 운전 모드 토글 */}
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs text-gray-500">운전 모드</span>
                <div className="flex rounded-md border border-gray-300 bg-white overflow-hidden">
                  <button
                    onClick={() => setConveyorMode("auto")}
                    className={cn(
                      "px-3 py-1 text-xs font-medium transition-colors",
                      conveyorMode === "auto"
                        ? "bg-blue-600 text-white"
                        : "text-gray-500 hover:bg-gray-100"
                    )}
                  >
                    Auto
                  </button>
                  <button
                    onClick={() => setConveyorMode("manual")}
                    className={cn(
                      "px-3 py-1 text-xs font-medium transition-colors",
                      conveyorMode === "manual"
                        ? "bg-blue-600 text-white"
                        : "text-gray-500 hover:bg-gray-100"
                    )}
                  >
                    Manual
                  </button>
                </div>
              </div>

              {/* 현재 상태 */}
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs text-gray-500">현재 상태</span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={cn(
                      "inline-block h-2 w-2 rounded-full",
                      conveyorRunning ? "bg-green-500 animate-pulse" : "bg-gray-400"
                    )}
                  />
                  <span
                    className={cn(
                      "text-xs font-medium",
                      conveyorRunning ? "text-green-700" : "text-gray-500"
                    )}
                  >
                    {conveyorRunning ? "구동 중" : "정지"}
                  </span>
                </div>
              </div>

              {/* 구동/정지 버튼 */}
              <div className="flex gap-2">
                <button
                  onClick={() => setConveyorRunning(true)}
                  disabled={conveyorRunning}
                  className={cn(
                    "flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors",
                    conveyorRunning
                      ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                      : "bg-green-600 text-white hover:bg-green-700"
                  )}
                >
                  구동
                </button>
                <button
                  onClick={() => setConveyorRunning(false)}
                  disabled={!conveyorRunning}
                  className={cn(
                    "flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors",
                    !conveyorRunning
                      ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                      : "bg-gray-600 text-white hover:bg-gray-700"
                  )}
                >
                  정지
                </button>
              </div>
            </div>

            {/* 분류 장치 상태 */}
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <div className="mb-3 flex items-center gap-2">
                <RotateCw className="h-4 w-4 text-gray-600" />
                <p className="text-xs font-semibold text-gray-700">분류 장치 상태</p>
              </div>

              {/* 모터 각도 표시 */}
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs text-gray-500">현재 모터 각도</span>
                <div className="flex items-center gap-1.5">
                  <span className="font-mono text-sm font-bold text-gray-800">
                    {sorterAngle}도
                  </span>
                  <span
                    className={cn(
                      "rounded-full px-1.5 py-0.5 text-xs font-medium",
                      sorterAngle === 0
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    )}
                  >
                    {sorterAngle === 0 ? "양품" : "불량품"}
                  </span>
                </div>
              </div>

              {/* 각도 시각화 */}
              <div className="mb-3 flex items-center justify-center">
                <div className="relative h-16 w-16">
                  {/* 원형 배경 */}
                  <div className="h-full w-full rounded-full border-2 border-gray-300 bg-white flex items-center justify-center">
                    {/* 방향 바 */}
                    <div
                      className={cn(
                        "h-0.5 w-8 rounded-full transition-transform duration-500 origin-left",
                        sorterAngle === 0 ? "bg-green-500" : "bg-red-500"
                      )}
                      style={{ transform: `rotate(${sorterAngle}deg)` }}
                    />
                  </div>
                  {/* 중심점 */}
                  <div className="absolute inset-1/2 -translate-x-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-gray-700" />
                </div>
              </div>

              {/* 분류 상태 인디케이터 */}
              <div className="mb-3 flex items-center justify-between rounded-md bg-white border border-gray-200 px-3 py-2">
                <span className="text-xs text-gray-500">분류 상태</span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={cn(
                      "inline-block h-2 w-2 rounded-full",
                      sorterAngle === 0 ? "bg-green-500" : "bg-red-500 animate-pulse"
                    )}
                  />
                  <span
                    className={cn(
                      "text-xs font-semibold",
                      sorterAngle === 0 ? "text-green-700" : "text-red-700"
                    )}
                  >
                    {sorterAngle === 0 ? "양품 라인 진행 중" : "불량품 분리 중"}
                  </span>
                </div>
              </div>

              {/* 각도 전환 버튼 */}
              <div className="flex gap-2">
                <button
                  onClick={() => setSorterAngle(0)}
                  className={cn(
                    "flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors",
                    sorterAngle === 0
                      ? "bg-green-600 text-white"
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                  )}
                >
                  0도 (양품)
                </button>
                <button
                  onClick={() => setSorterAngle(45)}
                  className={cn(
                    "flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors",
                    sorterAngle === 45
                      ? "bg-red-600 text-white"
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                  )}
                >
                  45도 (불량)
                </button>
              </div>
            </div>

            {/* 비상 정지 버튼 */}
            <div>
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
