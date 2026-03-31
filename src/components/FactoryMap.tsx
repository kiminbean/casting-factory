"use client";

import { useState } from "react";
import { Factory, Bot, Cpu, Zap, Battery, Thermometer } from "lucide-react";

// ----------------------------------------------------------------
// Types
// ----------------------------------------------------------------

type DeviceStatus = "active" | "idle" | "error" | "warning" | "charging";

interface Zone {
  id: string;
  name: string;
  col: number; // grid column (1-3)
  row: number; // grid row (1-3)
  status: DeviceStatus;
  equipment?: string;
  temp?: number;
  detail: string;
}

interface AMR {
  id: string;
  name: string;
  status: DeviceStatus;
  battery: number;
  position: string; // zone id
  detail: string;
  animationClass?: string;
}

interface Cobot {
  id: string;
  name: string;
  zone: string;
  status: DeviceStatus;
  task: string;
  detail: string;
}

interface MonitorItem {
  label: string;
  value: string;
  unit: string;
  status: DeviceStatus;
}

// ----------------------------------------------------------------
// Data
// ----------------------------------------------------------------

const ZONES: Zone[] = [
  {
    id: "raw-material",
    name: "원자재 보관",
    col: 1,
    row: 1,
    status: "active",
    detail: "원자재 재고 정상 수준. 주석 합금 234kg 보유 중.",
  },
  {
    id: "melting",
    name: "용해 구역",
    col: 2,
    row: 1,
    status: "active",
    temp: 720,
    detail: "용해로 가동 중. 온도 720°C 유지. 합금 조성 확인 완료.",
  },
  {
    id: "mold",
    name: "주형 구역",
    col: 3,
    row: 1,
    status: "idle",
    detail: "주형 대기 중. 다음 배치 준비 완료.",
  },
  {
    id: "casting",
    name: "주조 구역",
    col: 1,
    row: 2,
    status: "active",
    equipment: "COBOT-001",
    detail: "COBOT-001 작업 중. 시간당 120개 생산.",
  },
  {
    id: "cooling",
    name: "냉각 구역",
    col: 2,
    row: 2,
    status: "active",
    temp: 45,
    detail: "냉각 컨베이어 가동 중. 평균 온도 45°C.",
  },
  {
    id: "demolding",
    name: "탈형 구역",
    col: 3,
    row: 2,
    status: "warning",
    detail: "탈형 불량 감지. 검토 필요.",
  },
  {
    id: "post-process",
    name: "후처리 구역",
    col: 1,
    row: 3,
    status: "active",
    equipment: "COBOT-002",
    detail: "COBOT-002 버르 제거 작업 중.",
  },
  {
    id: "inspection",
    name: "검사 구역",
    col: 2,
    row: 3,
    status: "active",
    detail: "비전 검사 시스템 가동 중. 불량률 1.2%.",
  },
  {
    id: "loading",
    name: "적재 / 출고",
    col: 3,
    row: 3,
    status: "idle",
    detail: "출고 대기 중. 팔레트 3개 준비 완료.",
  },
];

const AMRS: AMR[] = [
  {
    id: "AMR-001",
    name: "AMR-001",
    status: "active",
    battery: 78,
    position: "melting",
    detail: "원자재 → 용해 구역 이송 중. 예상 완료 2분.",
    animationClass: "amr-move-horizontal",
  },
  {
    id: "AMR-002",
    name: "AMR-002",
    status: "idle",
    battery: 62,
    position: "cooling",
    detail: "냉각 구역 대기 중. 다음 작업 명령 대기.",
  },
  {
    id: "AMR-003",
    name: "AMR-003",
    status: "charging",
    battery: 23,
    position: "loading",
    detail: "충전소에서 충전 중. 충전 완료까지 약 35분.",
  },
];

const COBOTS: Cobot[] = [
  {
    id: "COBOT-001",
    name: "JetCobot280 #1",
    zone: "casting",
    status: "active",
    task: "주조 부품 픽앤플레이스",
    detail: "COBOT-001 | 주조 구역 | 정상 가동 중 | 사이클 타임 18초",
  },
  {
    id: "COBOT-002",
    name: "JetCobot280 #2",
    zone: "post-process",
    status: "active",
    task: "버르 제거 및 표면 처리",
    detail: "COBOT-002 | 후처리 구역 | 정상 가동 중 | 처리량 85개/시간",
  },
];

const MONITORS: MonitorItem[] = [
  {
    label: "생산량",
    value: "1,247",
    unit: "개/일",
    status: "active",
  },
  {
    label: "불량률",
    value: "1.2",
    unit: "%",
    status: "warning",
  },
  {
    label: "장비 가동률",
    value: "94.3",
    unit: "%",
    status: "active",
  },
  {
    label: "알림",
    value: "2",
    unit: "건",
    status: "warning",
  },
];

// ----------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------

function statusBorder(status: DeviceStatus): string {
  switch (status) {
    case "active":
      return "border-green-500";
    case "idle":
      return "border-gray-500";
    case "error":
      return "border-red-500";
    case "warning":
      return "border-yellow-400";
    case "charging":
      return "border-blue-400";
  }
}

function statusDot(status: DeviceStatus): string {
  switch (status) {
    case "active":
      return "bg-green-400";
    case "idle":
      return "bg-gray-400";
    case "error":
      return "bg-red-400";
    case "warning":
      return "bg-yellow-400";
    case "charging":
      return "bg-blue-400";
  }
}

function statusLabel(status: DeviceStatus): string {
  switch (status) {
    case "active":
      return "가동";
    case "idle":
      return "대기";
    case "error":
      return "오류";
    case "warning":
      return "경고";
    case "charging":
      return "충전";
  }
}

function monitorValueColor(status: DeviceStatus): string {
  switch (status) {
    case "active":
      return "text-green-400";
    case "warning":
      return "text-yellow-400";
    case "error":
      return "text-red-400";
    default:
      return "text-white";
  }
}

function amrBatteryColor(battery: number): string {
  if (battery > 60) return "bg-green-500";
  if (battery > 30) return "bg-yellow-500";
  return "bg-red-500";
}

// ----------------------------------------------------------------
// Sub-components
// ----------------------------------------------------------------

interface TooltipPanelProps {
  title: string;
  detail: string;
  onClose: () => void;
}

function TooltipPanel({ title, detail, onClose }: TooltipPanelProps) {
  return (
    <div className="absolute z-50 top-2 right-2 w-56 bg-gray-900 border border-gray-600 rounded-lg p-3 shadow-xl">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-white">{title}</span>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-xs leading-none w-4 h-4 flex items-center justify-center"
          aria-label="닫기"
        >
          x
        </button>
      </div>
      <p className="text-xs text-gray-300 leading-relaxed">{detail}</p>
    </div>
  );
}

// ----------------------------------------------------------------
// Zone Card
// ----------------------------------------------------------------

interface ZoneCardProps {
  zone: Zone;
  cobots: Cobot[];
  amrs: AMR[];
  isSelected: boolean;
  onClick: (id: string) => void;
}

function ZoneCard({ zone, cobots, isSelected, amrs, onClick }: ZoneCardProps) {
  const cobot = cobots.find((c) => c.zone === zone.id);
  const amr = amrs.find((a) => a.position === zone.id);

  return (
    <div
      className={`
        relative rounded-lg border-2 ${statusBorder(zone.status)}
        bg-[#5a5a5a] hover:bg-[#636363] cursor-pointer transition-colors
        p-2 flex flex-col gap-1 select-none min-h-0
      `}
      onClick={() => onClick(zone.id)}
      title={zone.name}
    >
      {/* Header row */}
      <div className="flex items-center gap-1.5">
        <span
          className={`w-2 h-2 rounded-full flex-shrink-0 ${statusDot(zone.status)}`}
        />
        <span className="text-[10px] font-semibold text-white truncate leading-tight">
          {zone.name}
        </span>
        <span className="ml-auto text-[9px] text-gray-400 flex-shrink-0">
          {statusLabel(zone.status)}
        </span>
      </div>

      {/* Temperature badge */}
      {zone.temp !== undefined && (
        <div className="flex items-center gap-1">
          <Thermometer size={8} className="text-orange-400 flex-shrink-0" />
          <span className="text-[9px] text-orange-300">{zone.temp}°C</span>
        </div>
      )}

      {/* Cobot indicator */}
      {cobot && (
        <div className="flex items-center gap-1 mt-auto">
          <div className="relative flex-shrink-0">
            <div className="w-5 h-5 rounded-full bg-amber-500 flex items-center justify-center">
              <Bot size={10} className="text-white" />
            </div>
            {/* Arm line visual */}
            <div className="absolute top-1/2 -right-2 w-2 h-0.5 bg-amber-400 -translate-y-1/2" />
          </div>
          <span className="text-[8px] text-amber-300 truncate">
            {cobot.id}
          </span>
        </div>
      )}

      {/* AMR indicator */}
      {amr && (
        <div className="flex items-center gap-1">
          <div
            className={`w-4 h-3 rounded-sm bg-cyan-600 border border-cyan-400 flex items-center justify-center flex-shrink-0 ${amr.animationClass || ""}`}
          >
            <div className="w-1 h-1 rounded-full bg-cyan-300" />
          </div>
          <span className="text-[8px] text-cyan-300 truncate">{amr.id}</span>
        </div>
      )}

      {/* Tooltip on select */}
      {isSelected && (
        <TooltipPanel
          title={zone.name}
          detail={zone.detail}
          onClose={() => onClick("")}
        />
      )}
    </div>
  );
}

// ----------------------------------------------------------------
// AMR Panel
// ----------------------------------------------------------------

interface AMRPanelProps {
  amr: AMR;
  isSelected: boolean;
  onClick: (id: string) => void;
}

function AMRPanel({ amr, isSelected, onClick }: AMRPanelProps) {
  return (
    <div
      className={`
        relative rounded border ${statusBorder(amr.status)}
        bg-[#3a3a3a] hover:bg-[#454545] cursor-pointer p-2 transition-colors
      `}
      onClick={() => onClick(amr.id)}
    >
      <div className="flex items-center gap-2">
        {/* AMR icon */}
        <div
          className={`
            w-6 h-5 rounded bg-cyan-700 border border-cyan-400 flex items-center justify-center flex-shrink-0
            ${amr.animationClass || ""}
          `}
        >
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-300" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="text-[10px] font-semibold text-white">
              {amr.name}
            </span>
            <span
              className={`w-1.5 h-1.5 rounded-full ${statusDot(amr.status)}`}
            />
          </div>
          <div className="text-[9px] text-gray-400">{statusLabel(amr.status)}</div>
        </div>

        {/* Battery */}
        <div className="flex flex-col items-end gap-0.5 flex-shrink-0">
          <div className="flex items-center gap-1">
            <Battery size={9} className="text-gray-400" />
            <span className="text-[9px] text-gray-300">{amr.battery}%</span>
          </div>
          <div className="w-12 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${amrBatteryColor(amr.battery)}`}
              style={{ width: `${amr.battery}%` }}
            />
          </div>
        </div>
      </div>

      {isSelected && (
        <TooltipPanel
          title={amr.name}
          detail={amr.detail}
          onClose={() => onClick("")}
        />
      )}
    </div>
  );
}

// ----------------------------------------------------------------
// Cobot Panel
// ----------------------------------------------------------------

interface CobotPanelProps {
  cobot: Cobot;
  isSelected: boolean;
  onClick: (id: string) => void;
}

function CobotPanel({ cobot, isSelected, onClick }: CobotPanelProps) {
  return (
    <div
      className={`
        relative rounded border ${statusBorder(cobot.status)}
        bg-[#3a3a3a] hover:bg-[#454545] cursor-pointer p-2 transition-colors
      `}
      onClick={() => onClick(cobot.id)}
    >
      <div className="flex items-center gap-2">
        {/* Cobot icon */}
        <div className="relative flex-shrink-0">
          <div className="w-6 h-6 rounded-full bg-amber-600 border border-amber-400 flex items-center justify-center">
            <Bot size={12} className="text-white" />
          </div>
          <div className="absolute top-1/2 -right-1.5 w-2 h-0.5 bg-amber-400 -translate-y-1/2" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="text-[10px] font-semibold text-white truncate">
              {cobot.id}
            </span>
            <span
              className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${statusDot(cobot.status)}`}
            />
          </div>
          <div className="text-[9px] text-gray-400 truncate">{cobot.task}</div>
        </div>
      </div>

      {isSelected && (
        <TooltipPanel
          title={cobot.name}
          detail={cobot.detail}
          onClose={() => onClick("")}
        />
      )}
    </div>
  );
}

// ----------------------------------------------------------------
// Monitor Bar
// ----------------------------------------------------------------

function MonitorBar() {
  return (
    <div className="flex gap-2 mb-3 flex-shrink-0">
      {MONITORS.map((m) => (
        <div
          key={m.label}
          className="flex-1 bg-[#2a2a2a] border border-gray-600 rounded p-2"
        >
          {/* Fake mini monitor screen */}
          <div className="bg-[#1a1a1a] rounded px-2 py-1.5 mb-1">
            <div className={`text-sm font-bold leading-none ${monitorValueColor(m.status)}`}>
              {m.value}
              <span className="text-[9px] text-gray-500 ml-0.5">{m.unit}</span>
            </div>
          </div>
          <div className="text-[9px] text-gray-400 text-center">{m.label}</div>
        </div>
      ))}
    </div>
  );
}

// ----------------------------------------------------------------
// Path Lines (AMR routes)
// ----------------------------------------------------------------

function PathLines() {
  return (
    <>
      {/* Horizontal path: row 1 connecting all 3 columns */}
      <div
        className="absolute border-t-2 border-dashed border-white/30"
        style={{ top: "calc(16.7% + 50px)", left: "5%", right: "5%" }}
      />
      {/* Horizontal path: row 2 */}
      <div
        className="absolute border-t-2 border-dashed border-white/30"
        style={{ top: "calc(50%)", left: "5%", right: "5%" }}
      />
      {/* Horizontal path: row 3 */}
      <div
        className="absolute border-t-2 border-dashed border-white/30"
        style={{ top: "calc(83.3% - 10px)", left: "5%", right: "5%" }}
      />
      {/* Vertical path: col 1 */}
      <div
        className="absolute border-l-2 border-dashed border-white/20"
        style={{
          left: "calc(16.7% - 1px)",
          top: "calc(16.7% + 50px)",
          bottom: "calc(16.7% - 10px)",
        }}
      />
      {/* Vertical path: col 2 */}
      <div
        className="absolute border-l-2 border-dashed border-white/20"
        style={{
          left: "calc(50%)",
          top: "calc(16.7% + 50px)",
          bottom: "calc(16.7% - 10px)",
        }}
      />
      {/* Vertical path: col 3 */}
      <div
        className="absolute border-l-2 border-dashed border-white/20"
        style={{
          left: "calc(83.3% - 1px)",
          top: "calc(16.7% + 50px)",
          bottom: "calc(16.7% - 10px)",
        }}
      />
    </>
  );
}

// ----------------------------------------------------------------
// Legend
// ----------------------------------------------------------------

function Legend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 pt-2 border-t border-gray-700">
      <div className="flex items-center gap-1.5">
        <span className="w-3 h-3 rounded-full bg-amber-500 flex items-center justify-center">
          <Bot size={7} className="text-white" />
        </span>
        <span className="text-[9px] text-gray-400">JetCobot280</span>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="w-4 h-2.5 rounded-sm bg-cyan-600 border border-cyan-400 block" />
        <span className="text-[9px] text-gray-400">AMR 로봇</span>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="w-4 border-t-2 border-dashed border-white/50 block" />
        <span className="text-[9px] text-gray-400">AMR 경로</span>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-green-400" />
        <span className="text-[9px] text-gray-400">가동</span>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-yellow-400" />
        <span className="text-[9px] text-gray-400">경고</span>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-gray-400" />
        <span className="text-[9px] text-gray-400">대기</span>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------
// Main Component
// ----------------------------------------------------------------

export default function FactoryMap() {
  const [selectedId, setSelectedId] = useState<string>("");

  function handleSelect(id: string) {
    setSelectedId((prev) => (prev === id ? "" : id));
  }

  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* Outer frame - control room style */}
      <div
        className="rounded-xl border border-gray-600 overflow-hidden shadow-2xl"
        style={{ background: "#2d2d2d" }}
      >
        {/* Title bar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-[#1e1e1e]">
          <div className="flex items-center gap-2">
            <Factory size={14} className="text-cyan-400" />
            <span className="text-xs font-bold text-white tracking-widest uppercase">
              주조 공장 제어 시스템
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              <Cpu size={10} className="text-green-400" />
              <span className="text-[9px] text-green-400">시스템 정상</span>
            </div>
            <div className="flex items-center gap-1">
              <Zap size={10} className="text-yellow-400" />
              <span className="text-[9px] text-yellow-400">경고 2건</span>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-3">
          {/* Monitor bar */}
          <MonitorBar />

          {/* Factory floor + side panels */}
          <div className="flex gap-3">
            {/* Factory floor map */}
            <div
              className="relative flex-1 rounded-lg overflow-hidden"
              style={{
                background: "#4a4a4a",
                /* subtle grid */
                backgroundImage:
                  "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
                backgroundSize: "20px 20px",
                aspectRatio: "16/9",
                minHeight: "280px",
              }}
            >
              {/* Path lines */}
              <PathLines />

              {/* Zone grid - 3x3 */}
              <div
                className="absolute inset-2 grid gap-2"
                style={{ gridTemplateColumns: "1fr 1fr 1fr", gridTemplateRows: "1fr 1fr 1fr" }}
              >
                {ZONES.map((zone) => (
                  <ZoneCard
                    key={zone.id}
                    zone={zone}
                    cobots={COBOTS}
                    amrs={AMRS}
                    isSelected={selectedId === zone.id}
                    onClick={handleSelect}
                  />
                ))}
              </div>
            </div>

            {/* Right side panel */}
            <div className="w-44 flex flex-col gap-2 flex-shrink-0">
              {/* AMR status */}
              <div>
                <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 font-semibold">
                  AMR 로봇
                </div>
                <div className="flex flex-col gap-1.5">
                  {AMRS.map((amr) => (
                    <AMRPanel
                      key={amr.id}
                      amr={amr}
                      isSelected={selectedId === amr.id}
                      onClick={handleSelect}
                    />
                  ))}
                </div>
              </div>

              {/* Cobot status */}
              <div>
                <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 font-semibold">
                  협동 로봇
                </div>
                <div className="flex flex-col gap-1.5">
                  {COBOTS.map((cobot) => (
                    <CobotPanel
                      key={cobot.id}
                      cobot={cobot}
                      isSelected={selectedId === cobot.id}
                      onClick={handleSelect}
                    />
                  ))}
                </div>
              </div>

              {/* Quick stats */}
              <div className="mt-auto">
                <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 font-semibold">
                  공장 현황
                </div>
                <div className="bg-[#2a2a2a] rounded border border-gray-700 p-2 space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-[9px] text-gray-400">가동 구역</span>
                    <span className="text-[9px] text-green-400 font-semibold">
                      {ZONES.filter((z) => z.status === "active").length} / {ZONES.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[9px] text-gray-400">AMR 가동</span>
                    <span className="text-[9px] text-cyan-400 font-semibold">
                      {AMRS.filter((a) => a.status === "active").length} / {AMRS.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[9px] text-gray-400">코봇 가동</span>
                    <span className="text-[9px] text-amber-400 font-semibold">
                      {COBOTS.filter((c) => c.status === "active").length} / {COBOTS.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[9px] text-gray-400">경고</span>
                    <span className="text-[9px] text-yellow-400 font-semibold">
                      {
                        ZONES.filter(
                          (z) => z.status === "warning" || z.status === "error"
                        ).length
                      } 건
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Legend */}
          <Legend />
        </div>
      </div>

      {/* AMR movement animation styles */}
      <style>{`
        @keyframes amr-move-h {
          0%   { transform: translateX(-6px); }
          50%  { transform: translateX(6px); }
          100% { transform: translateX(-6px); }
        }
        .amr-move-horizontal {
          animation: amr-move-h 2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
