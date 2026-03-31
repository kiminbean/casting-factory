"use client";

import { useState } from "react";
import { Factory, Bot, Cpu, Zap, Battery, MapPin } from "lucide-react";

// ----------------------------------------------------------------
// CSS Keyframes injected via style tag
// ----------------------------------------------------------------

const ANIMATION_STYLES = `
  @keyframes amr-travel {
    0%   { transform: translateX(0px) translateZ(8px); }
    25%  { transform: translateX(60px) translateZ(8px); }
    50%  { transform: translateX(60px) translateY(40px) translateZ(8px); }
    75%  { transform: translateX(0px) translateY(40px) translateZ(8px); }
    100% { transform: translateX(0px) translateZ(8px); }
  }
  @keyframes charging-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0.6), 4px 4px 0 #374151; }
    50%       { box-shadow: 0 0 12px 4px rgba(250, 204, 21, 0.3), 4px 4px 0 #374151; }
  }
  @keyframes cobot-arm-rotate {
    0%   { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  @keyframes cobot-arm-slow {
    0%   { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  @keyframes zone-pulse-warn {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.7; }
  }
  @keyframes float-up {
    0%   { transform: translateZ(30px) scale(1); }
    50%  { transform: translateZ(36px) scale(1.02); }
    100% { transform: translateZ(30px) scale(1); }
  }
`;

// ----------------------------------------------------------------
// Types
// ----------------------------------------------------------------

type DeviceStatus = "active" | "idle" | "error" | "warning" | "charging";

interface ZoneDef {
  id: string;
  name: string;
  col: number;
  row: number;
  status: DeviceStatus;
  equipment?: string;
  detail: string;
  temp?: number;
}

interface MonitorItem {
  label: string;
  value: string;
  unit: string;
  isAlert?: boolean;
}

// ----------------------------------------------------------------
// Static Data
// ----------------------------------------------------------------

const ZONES: ZoneDef[] = [
  { id: "raw-material", name: "원자재 보관", col: 1, row: 1, status: "active",  detail: "주석 합금 234kg 보유. 재고 정상 수준." },
  { id: "melting",      name: "용해 구역",   col: 2, row: 1, status: "active",  temp: 720, detail: "용해로 가동 중. 온도 720°C 유지." },
  { id: "mold",         name: "주형 구역",   col: 3, row: 1, status: "idle",    detail: "다음 배치 준비 완료. 대기 중." },
  { id: "casting",      name: "주조 구역",   col: 1, row: 2, status: "active",  equipment: "COBOT-001", detail: "COBOT-001 작업 중. 시간당 120개 생산." },
  { id: "cooling",      name: "냉각 구역",   col: 2, row: 2, status: "active",  temp: 45,  detail: "냉각 컨베이어 가동 중. 평균 45°C." },
  { id: "demolding",    name: "탈형 구역",   col: 3, row: 2, status: "warning", detail: "탈형 불량 감지. 즉각 점검 필요." },
  { id: "post-process", name: "후처리 구역", col: 1, row: 3, status: "active",  equipment: "COBOT-002", detail: "COBOT-002 버르 제거 중. 85개/시간." },
  { id: "inspection",   name: "검사 구역",   col: 2, row: 3, status: "active",  detail: "비전 시스템 가동 중. 불량률 1.2%." },
  { id: "loading",      name: "적재 / 출고", col: 3, row: 3, status: "idle",    detail: "출고 대기 중. 팔레트 3개 준비." },
];

const MONITORS: MonitorItem[] = [
  { label: "생산량",      value: "47",   unit: "개",  isAlert: false },
  { label: "불량률",      value: "4.2",  unit: "%",   isAlert: true  },
  { label: "장비 가동률", value: "72.5", unit: "%",   isAlert: false },
  { label: "활성 알림",   value: "2",    unit: "건",  isAlert: true  },
  { label: "AMR 가용",    value: "1",    unit: "대",  isAlert: false },
  { label: "코봇 가동",   value: "2",    unit: "대",  isAlert: false },
];

// ----------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------

function zoneColor(status: DeviceStatus): { top: string; shadow: string; border: string } {
  switch (status) {
    case "active":  return { top: "#4b5563", shadow: "#374151", border: "#22c55e" };
    case "idle":    return { top: "#3d4452", shadow: "#2d3340", border: "#6b7280" };
    case "warning": return { top: "#4b4020", shadow: "#3a3010", border: "#f59e0b" };
    case "error":   return { top: "#4b2020", shadow: "#3a1010", border: "#ef4444" };
    case "charging":return { top: "#203040", shadow: "#102030", border: "#60a5fa" };
  }
}

function statusDotColor(status: DeviceStatus): string {
  switch (status) {
    case "active":   return "#4ade80";
    case "idle":     return "#9ca3af";
    case "warning":  return "#fbbf24";
    case "error":    return "#f87171";
    case "charging": return "#60a5fa";
  }
}

function statusLabel(status: DeviceStatus): string {
  switch (status) {
    case "active":   return "가동";
    case "idle":     return "대기";
    case "warning":  return "경고";
    case "error":    return "오류";
    case "charging": return "충전";
  }
}

// Grid position to pixel offset on the isometric floor
// Each cell is 200px wide and 130px tall (with gap)
const CELL_W = 192;
const CELL_H = 128;
const GAP_W  = 12;
const GAP_H  = 12;

function cellX(col: number): number {
  return (col - 1) * (CELL_W + GAP_W);
}
function cellY(row: number): number {
  return (row - 1) * (CELL_H + GAP_H);
}

// Floor dimensions
const FLOOR_W = 3 * CELL_W + 2 * GAP_W + 32; // + padding
const FLOOR_H = 3 * CELL_H + 2 * GAP_H + 32;

// ----------------------------------------------------------------
// Zone Block — 3D raised platform effect
// ----------------------------------------------------------------

interface ZoneBlockProps {
  zone: ZoneDef;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

function ZoneBlock({ zone, isSelected, onSelect }: ZoneBlockProps) {
  const colors = zoneColor(zone.status);
  const x = cellX(zone.col) + 16;
  const y = cellY(zone.row) + 16;
  const isWarn = zone.status === "warning";
  const hasCobot = !!zone.equipment;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: CELL_W,
        height: CELL_H,
        cursor: "pointer",
        /* 3D block using box-shadow for depth */
        background: `linear-gradient(135deg, ${colors.top} 0%, #374151 100%)`,
        boxShadow: isSelected
          ? `5px 5px 0 ${colors.shadow}, 0 5px 0 ${colors.shadow}, 5px 0 0 ${colors.shadow}, 0 0 0 2px ${colors.border}, 0 0 20px rgba(34,197,94,0.3)`
          : `5px 5px 0 ${colors.shadow}, 0 5px 0 ${colors.shadow}, 5px 0 0 ${colors.shadow}`,
        border: `1.5px solid ${isSelected ? colors.border : "rgba(255,255,255,0.12)"}`,
        borderRadius: 6,
        animation: isWarn ? "zone-pulse-warn 1.8s ease-in-out infinite" : undefined,
        transition: "box-shadow 0.2s, border 0.2s",
      }}
      onClick={() => onSelect(zone.id)}
    >
      {/* Zone name header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 5,
          padding: "6px 8px 4px",
          borderBottom: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <span
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: statusDotColor(zone.status),
            flexShrink: 0,
            boxShadow: `0 0 4px ${statusDotColor(zone.status)}`,
          }}
        />
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: "#f3f4f6",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            flex: 1,
          }}
        >
          {zone.name}
        </span>
        <span style={{ fontSize: 8, color: "#9ca3af", flexShrink: 0 }}>
          {statusLabel(zone.status)}
        </span>
      </div>

      {/* Temperature badge */}
      {zone.temp !== undefined && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 3,
            padding: "2px 8px",
          }}
        >
          <span style={{ fontSize: 8, color: "#fb923c" }}>{zone.temp}°C</span>
        </div>
      )}

      {/* Cobot indicator — floated above floor */}
      {hasCobot && (
        <div
          style={{
            position: "absolute",
            bottom: 12,
            left: 10,
            display: "flex",
            alignItems: "center",
            gap: 4,
            transform: "translateZ(15px)",
          }}
        >
          {/* Cobot body circle */}
          <div
            style={{
              width: 22,
              height: 22,
              borderRadius: "50%",
              background: "radial-gradient(circle at 35% 35%, #fcd34d, #d97706)",
              border: "1.5px solid #f59e0b",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
              boxShadow: "0 0 6px rgba(245,158,11,0.5)",
            }}
          >
            <Bot size={11} color="#fff" />
            {/* Rotating arm */}
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                width: 14,
                height: 2,
                background: "#f59e0b",
                transformOrigin: "0 50%",
                marginTop: -1,
                borderRadius: 2,
                animation: "cobot-arm-rotate 2.8s linear infinite",
              }}
            />
          </div>
          <span style={{ fontSize: 8, color: "#fcd34d" }}>{zone.equipment}</span>
        </div>
      )}

      {/* Selected detail pop-up */}
      {isSelected && (
        <div
          style={{
            position: "absolute",
            top: -70,
            left: "50%",
            transform: "translateX(-50%) translateZ(30px)",
            background: "#111827",
            border: "1px solid #4b5563",
            borderRadius: 6,
            padding: "6px 10px",
            minWidth: 160,
            maxWidth: 200,
            zIndex: 100,
            boxShadow: "0 4px 20px rgba(0,0,0,0.6)",
            pointerEvents: "none",
            animation: "float-up 2s ease-in-out infinite",
          }}
        >
          <div style={{ fontSize: 10, fontWeight: 700, color: "#f9fafb", marginBottom: 3 }}>
            {zone.name}
          </div>
          <div style={{ fontSize: 9, color: "#9ca3af", lineHeight: 1.5 }}>{zone.detail}</div>
          {/* Arrow pointer */}
          <div
            style={{
              position: "absolute",
              bottom: -6,
              left: "50%",
              transform: "translateX(-50%)",
              width: 0,
              height: 0,
              borderLeft: "5px solid transparent",
              borderRight: "5px solid transparent",
              borderTop: "6px solid #4b5563",
            }}
          />
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------------------
// AMR Robot on the floor
// ----------------------------------------------------------------

interface AMROnFloorProps {
  id: string;
  label: string;
  startX: number;
  startY: number;
  animated?: boolean;
  pulsing?: boolean;
}

function AMROnFloor({ id, label, startX, startY, animated, pulsing }: AMROnFloorProps) {
  return (
    <div
      style={{
        position: "absolute",
        left: startX,
        top: startY,
        width: 28,
        height: 20,
        background: "linear-gradient(135deg, #164e63 0%, #0e7490 100%)",
        border: "1.5px solid #22d3ee",
        borderRadius: 4,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: pulsing
          ? "charging-pulse 1.4s ease-in-out infinite"
          : `4px 4px 0 #374151`,
        animation: animated
          ? "amr-travel 5s linear infinite"
          : pulsing
          ? "charging-pulse 1.4s ease-in-out infinite"
          : undefined,
        transform: "translateZ(8px)",
        zIndex: 20,
      }}
      title={id}
    >
      {/* Indicator dot */}
      <div
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: animated ? "#67e8f9" : pulsing ? "#fde047" : "#94a3b8",
          boxShadow: animated ? "0 0 4px #67e8f9" : undefined,
        }}
      />
      {/* Label below */}
      <span
        style={{
          position: "absolute",
          top: 22,
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: 7,
          color: "#67e8f9",
          whiteSpace: "nowrap",
          fontWeight: 600,
          letterSpacing: "0.03em",
        }}
      >
        {label}
      </span>
    </div>
  );
}

// ----------------------------------------------------------------
// AMR Path Lines (SVG overlay)
// ----------------------------------------------------------------

function PathOverlay() {
  // Paths between zone centers on the floor grid
  // Using simple right-angle routes
  const strokeProps = {
    stroke: "rgba(255,255,255,0.25)",
    strokeWidth: 1.5,
    strokeDasharray: "6 4",
    fill: "none",
  };

  return (
    <svg
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        zIndex: 5,
      }}
      width={FLOOR_W}
      height={FLOOR_H}
    >
      {/* Horizontal corridors */}
      <line x1={16} y1={80} x2={FLOOR_W - 16} y2={80} {...strokeProps} />
      <line x1={16} y1={CELL_H + GAP_H + 16 + 64} x2={FLOOR_W - 16} y2={CELL_H + GAP_H + 16 + 64} {...strokeProps} />
      <line x1={16} y1={2 * (CELL_H + GAP_H) + 16 + 64} x2={FLOOR_W - 16} y2={2 * (CELL_H + GAP_H) + 16 + 64} {...strokeProps} />
      {/* Vertical corridors */}
      <line x1={112} y1={16} x2={112} y2={FLOOR_H - 16} {...strokeProps} />
      <line x1={CELL_W + GAP_W + 16 + 96} y1={16} x2={CELL_W + GAP_W + 16 + 96} y2={FLOOR_H - 16} {...strokeProps} />
      <line x1={2 * (CELL_W + GAP_W) + 16 + 96} y1={16} x2={2 * (CELL_W + GAP_W) + 16 + 96} y2={FLOOR_H - 16} {...strokeProps} />
    </svg>
  );
}

// ----------------------------------------------------------------
// Monitor Bar (2D, above 3D view)
// ----------------------------------------------------------------

function MonitorBar() {
  return (
    <div
      style={{
        display: "flex",
        gap: 8,
        marginBottom: 16,
        padding: "10px 12px",
        background: "#111827",
        borderRadius: 8,
        border: "1px solid #374151",
      }}
    >
      {MONITORS.map((m) => (
        <div
          key={m.label}
          style={{
            flex: 1,
            background: "#0f172a",
            border: `1px solid ${m.isAlert ? "#f59e0b" : "#1f2937"}`,
            borderRadius: 5,
            padding: "6px 8px",
            textAlign: "center",
          }}
        >
          {/* CRT-style screen area */}
          <div
            style={{
              background: "#020617",
              borderRadius: 3,
              padding: "4px 4px 3px",
              marginBottom: 3,
              border: "1px solid #1e3a5f",
            }}
          >
            <span
              style={{
                fontSize: 14,
                fontWeight: 800,
                color: m.isAlert ? "#f87171" : "#4ade80",
                letterSpacing: "0.04em",
                display: "block",
                lineHeight: 1,
              }}
            >
              {m.value}
              <span style={{ fontSize: 8, color: "#6b7280", marginLeft: 2 }}>
                {m.unit}
              </span>
            </span>
          </div>
          <span style={{ fontSize: 8, color: "#6b7280" }}>{m.label}</span>
        </div>
      ))}
    </div>
  );
}

// ----------------------------------------------------------------
// Legend (2D, below 3D view)
// ----------------------------------------------------------------

function Legend() {
  const items = [
    { color: "#f59e0b", label: "JetCobot280", shape: "circle" as const },
    { color: "#22d3ee", label: "AMR 로봇",    shape: "rect" as const   },
    { color: "#4ade80", label: "가동 중",      shape: "dot" as const    },
    { color: "#fbbf24", label: "경고",         shape: "dot" as const    },
    { color: "#9ca3af", label: "대기",         shape: "dot" as const    },
    { color: "#f87171", label: "오류",         shape: "dot" as const    },
  ];

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "6px 16px",
        marginTop: 12,
        paddingTop: 10,
        borderTop: "1px solid #374151",
      }}
    >
      {items.map((item) => (
        <div key={item.label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
          {item.shape === "circle" && (
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: item.color,
                border: "1.5px solid rgba(255,255,255,0.3)",
              }}
            />
          )}
          {item.shape === "rect" && (
            <div
              style={{
                width: 16,
                height: 10,
                borderRadius: 2,
                background: "#0e7490",
                border: `1.5px solid ${item.color}`,
              }}
            />
          )}
          {item.shape === "dot" && (
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: item.color,
                boxShadow: `0 0 4px ${item.color}`,
              }}
            />
          )}
          <span style={{ fontSize: 9, color: "#9ca3af" }}>{item.label}</span>
        </div>
      ))}
      {/* Path legend */}
      <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
        <svg width={20} height={8}>
          <line
            x1={0} y1={4} x2={20} y2={4}
            stroke="rgba(255,255,255,0.35)"
            strokeWidth={1.5}
            strokeDasharray="4 3"
          />
        </svg>
        <span style={{ fontSize: 9, color: "#9ca3af" }}>AMR 경로</span>
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
    <div
      style={{
        width: "100%",
        maxWidth: 960,
        margin: "0 auto",
        fontFamily: "'Inter', 'Segoe UI', sans-serif",
      }}
    >
      <style>{ANIMATION_STYLES}</style>

      {/* Outer control-room frame */}
      <div
        style={{
          background: "#1f2937",
          border: "1px solid #374151",
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: "0 25px 50px rgba(0,0,0,0.7)",
        }}
      >
        {/* Title bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "8px 16px",
            background: "#111827",
            borderBottom: "1px solid #374151",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Factory size={14} color="#22d3ee" />
            <span
              style={{
                fontSize: 11,
                fontWeight: 800,
                color: "#f9fafb",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
              }}
            >
              주조 공장 3D 제어 시스템
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <Cpu size={10} color="#4ade80" />
              <span style={{ fontSize: 9, color: "#4ade80" }}>시스템 정상</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <Zap size={10} color="#fbbf24" />
              <span style={{ fontSize: 9, color: "#fbbf24" }}>경고 2건</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <MapPin size={10} color="#818cf8" />
              <span style={{ fontSize: 9, color: "#818cf8" }}>AMR 3대</span>
            </div>
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: 16 }}>
          {/* Monitor Bar — flat 2D display */}
          <MonitorBar />

          {/* 3D Isometric view container */}
          <div
            style={{
              perspective: "1200px",
              height: 700,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "radial-gradient(ellipse at center, #1e293b 0%, #0f172a 100%)",
              borderRadius: 10,
              border: "1px solid #1e3a5f",
              overflow: "hidden",
              position: "relative",
            }}
          >
            {/* Ambient grid glow */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                backgroundImage:
                  "linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px)",
                backgroundSize: "40px 40px",
                borderRadius: 10,
              }}
            />

            {/* 3D floor plane */}
            <div
              style={{
                transform: "rotateX(55deg) rotateZ(-5deg)",
                transformStyle: "preserve-3d",
                position: "relative",
                width: FLOOR_W,
                height: FLOOR_H,
              }}
            >
              {/* Floor base */}
              <div
                style={{
                  position: "absolute",
                  inset: -20,
                  background: "linear-gradient(145deg, #4b5563 0%, #374151 50%, #1f2937 100%)",
                  borderRadius: 12,
                  boxShadow: "0 0 0 1px rgba(255,255,255,0.06)",
                  /* Subtle grid on floor */
                  backgroundImage:
                    "linear-gradient(145deg, #4b5563, #374151), " +
                    "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), " +
                    "linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
                  backgroundSize: "100% 100%, 50px 50px, 50px 50px",
                  backgroundBlendMode: "overlay, normal, normal",
                }}
              />

              {/* AMR path lines */}
              <PathOverlay />

              {/* Zone blocks */}
              {ZONES.map((zone) => (
                <ZoneBlock
                  key={zone.id}
                  zone={zone}
                  isSelected={selectedId === zone.id}
                  onSelect={handleSelect}
                />
              ))}

              {/* AMR-001: animated, moving along path */}
              <AMROnFloor
                id="AMR-001"
                label="AMR-001"
                startX={cellX(2) + 16 + CELL_W / 2 - 14}
                startY={cellY(1) + 16 + CELL_H / 2 - 10}
                animated
              />

              {/* AMR-002: idle, parked at cooling zone */}
              <AMROnFloor
                id="AMR-002"
                label="AMR-002"
                startX={cellX(2) + 16 + CELL_W / 2 - 14}
                startY={cellY(2) + 16 + CELL_H - 36}
              />

              {/* AMR-003: charging, at loading zone with pulse */}
              <AMROnFloor
                id="AMR-003"
                label="AMR-003"
                startX={cellX(3) + 16 + 12}
                startY={cellY(3) + 16 + 10}
                pulsing
              />

              {/* Charging station indicator */}
              <div
                style={{
                  position: "absolute",
                  left: cellX(3) + 16 + 8,
                  top: cellY(3) + 16 + 6,
                  fontSize: 7,
                  color: "#fde047",
                  fontWeight: 700,
                  letterSpacing: "0.05em",
                }}
              >
                <Battery size={9} color="#fde047" style={{ display: "inline", marginRight: 2 }} />
              </div>
            </div>
          </div>

          {/* Legend — flat 2D */}
          <Legend />

          {/* Help text */}
          <div
            style={{
              marginTop: 8,
              fontSize: 9,
              color: "#4b5563",
              textAlign: "center",
            }}
          >
            구역을 클릭하면 상세 정보를 확인할 수 있습니다.
          </div>
        </div>
      </div>
    </div>
  );
}
