"use client";

import { useState, useRef, useCallback } from "react";
import { Factory, Bot, Cpu, Zap, Battery, MapPin } from "lucide-react";
import FactoryMapEditor from "./FactoryMapEditor";

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

  /* === AMR 이동 애니메이션 — 복도 전용 경로 === */

  /*
   * 카메라 (26,-9,15), 렌즈24mm, 탈형→주조 방향 뷰
   * 직교 그리드: 왼=Row3, 중=Row2, 우=Row1 / 위=Col1, 아래=Col3
   *
   * 구역 중심:
   *   원자재(66,42)  용해(69,63)  주형(75,96)
   *   주조(50,42)    냉각(50,63)  탈형(50,96)
   *   후처리(34,42)  검사(31,63)  적재(25,96)
   *
   * 복도 교차점:
   *   N1=(59,51)  N2=(61,77)
   *   N3=(41,51)  N4=(39,77)
   *
   * 복도 방향: V=세로(상하), H=가로(좌우)
   */

  /* AMR-001: 원자재(25,37)→용해(50,37) — H 복도 가로 이동 */
  @keyframes render-amr-patrol-1 {
    0%   { left: 30%; top: 37%; }
    10%  { left: 30%; top: 37%; }
    25%  { left: 38%; top: 37%; }
    40%  { left: 46%; top: 37%; }
    55%  { left: 46%; top: 37%; }
    70%  { left: 40%; top: 37%; }
    85%  { left: 33%; top: 37%; }
    100% { left: 30%; top: 37%; }
  }

  /* AMR-002: 탈형(81,48)→후처리(10,67)→검사(50,67)→복귀
     N2(64,42)→N1(36,42)→N3(33,56)→N4(67,56) 복도 경유 */
  @keyframes render-amr-patrol-2 {
    0%   { left: 81%; top: 52%; }
    4%   { left: 81%; top: 52%; }
    10%  { left: 72%; top: 48%; }
    15%  { left: 64%; top: 42%; }
    16%  { left: 64%; top: 42%; }
    22%  { left: 50%; top: 42%; }
    28%  { left: 36%; top: 42%; }
    29%  { left: 36%; top: 42%; }
    36%  { left: 35%; top: 49%; }
    42%  { left: 33%; top: 56%; }
    43%  { left: 33%; top: 56%; }
    48%  { left: 16%; top: 63%; }
    55%  { left: 16%; top: 63%; }
    59%  { left: 33%; top: 63%; }
    63%  { left: 50%; top: 63%; }
    69%  { left: 50%; top: 63%; }
    74%  { left: 58%; top: 60%; }
    79%  { left: 67%; top: 56%; }
    85%  { left: 68%; top: 50%; }
    91%  { left: 73%; top: 46%; }
    96%  { left: 78%; top: 50%; }
    100% { left: 81%; top: 52%; }
  }

  /* AMR-003: 검사(50,67)→적재(90,67) — H 복도 가로 이동 */
  @keyframes render-amr-patrol-3 {
    0%   { left: 55%; top: 67%; }
    10%  { left: 55%; top: 67%; }
    25%  { left: 68%; top: 67%; }
    40%  { left: 85%; top: 67%; }
    60%  { left: 85%; top: 67%; }
    75%  { left: 70%; top: 67%; }
    90%  { left: 58%; top: 67%; }
    100% { left: 55%; top: 67%; }
  }

  @keyframes render-amr-charge {
    0%, 100% { box-shadow: 0 0 6px 2px rgba(250, 204, 21, 0.5); }
    50%      { box-shadow: 0 0 14px 5px rgba(250, 204, 21, 0.8); }
  }

  /* 프로세스 흐름 화살표 펄스 */
  @keyframes flow-pulse {
    0%, 100% { opacity: 0.4; }
    50%      { opacity: 0.9; }
  }

  /* 3D 렌더 뷰용 Cobot 작업 애니메이션 */
  @keyframes render-cobot-work {
    0%   { transform: rotate(-15deg); }
    50%  { transform: rotate(15deg); }
    100% { transform: rotate(-15deg); }
  }
  @keyframes render-cobot-pulse {
    0%, 100% { box-shadow: 0 0 8px 2px rgba(34, 197, 94, 0.4); }
    50%      { box-shadow: 0 0 16px 6px rgba(34, 197, 94, 0.7); }
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

// ----------------------------------------------------------------
// 3D Render View — Blender Photorealistic Factory Scene
// ----------------------------------------------------------------

// 3D 렌더 이미지 위 인터랙티브 핫스팟 좌표 (이미지 비율 기준 %)
// 카메라 (26,-9,15), 타겟 (6,-9,0.5), 렌즈 24mm
// 탈형→주조 방향 뷰: 직교 그리드 (Row=좌우, Col=상하)
// 왼쪽=Row3, 중앙=Row2, 오른쪽=Row1 / 위=Col1, 아래=Col3
// 카메라 (18,-30,11), 타겟 (18,-7,-1.5), 렌즈 20mm — 2:1 공장 최대 크기 뷰
// 직교 그리드: 왼=Col1, 중=Col2, 우=Col3 / 위=Row1, 아래=Row3
const HOTSPOTS: { zoneId: string; x: number; y: number; w: number; h: number }[] = [
  { zoneId: "raw-material", x: 18, y: 29, w: 16, h: 14 },  // 원자재 (1,1) center≈(25,37)
  { zoneId: "melting",      x: 42, y: 29, w: 16, h: 14 },  // 용해   (2,1) center≈(50,37)
  { zoneId: "mold",         x: 67, y: 29, w: 16, h: 14 },  // 주형   (3,1) center≈(75,37)
  { zoneId: "casting",      x: 12, y: 41, w: 16, h: 12 },  // 주조   (1,2) center≈(20,48)
  { zoneId: "cooling",      x: 42, y: 41, w: 16, h: 12 },  // 냉각   (2,2) center≈(50,48)
  { zoneId: "demolding",    x: 73, y: 41, w: 16, h: 12 },  // 탈형   (3,2) center≈(81,48)
  { zoneId: "post-process", x: 3,  y: 59, w: 16, h: 14 },  // 후처리 (1,3) center≈(10,67)
  { zoneId: "inspection",   x: 42, y: 59, w: 16, h: 14 },  // 검사   (2,3) center≈(50,67)
  { zoneId: "loading",      x: 83, y: 59, w: 16, h: 14 },  // 적재   (3,3) center≈(90,67)
];

// JetCobot280 오버레이 컴포넌트 (3D 렌더 위)
function CobotOverlay({
  id,
  label,
  x,
  y,
}: {
  id: string;
  label: string;
  x: number;
  y: number;
}) {
  return (
    <div
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y}%`,
        zIndex: 30,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        pointerEvents: "none",
      }}
    >
      {/* 코봇 바디 */}
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          background: "radial-gradient(circle at 35% 35%, #fcd34d, #d97706)",
          border: "2px solid #f59e0b",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          animation: "render-cobot-pulse 2s ease-in-out infinite",
        }}
      >
        <Bot size={14} color="#fff" />
        {/* 회전하는 로봇 암 */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 20,
            height: 3,
            background: "linear-gradient(90deg, #f59e0b, #fcd34d)",
            transformOrigin: "0 50%",
            marginTop: -1.5,
            borderRadius: 3,
            animation: "cobot-arm-rotate 3s linear infinite",
          }}
        />
      </div>
      {/* 라벨 */}
      <span
        style={{
          marginTop: 3,
          fontSize: 8,
          fontWeight: 700,
          color: "#fcd34d",
          textShadow: "0 1px 4px rgba(0,0,0,0.9)",
          whiteSpace: "nowrap",
          letterSpacing: "0.04em",
        }}
      >
        {label}
      </span>
      {/* 상태 표시 */}
      <span
        style={{
          fontSize: 7,
          color: "#4ade80",
          textShadow: "0 1px 3px rgba(0,0,0,0.9)",
        }}
      >
        작업 중
      </span>
    </div>
  );
}

// AMR 오버레이 컴포넌트 (3D 렌더 위)
function AMROverlay({
  id,
  label,
  x,
  y,
  status,
  animationName,
  task,
  animationDuration,
}: {
  id: string;
  label: string;
  x: number;
  y: number;
  status: "moving" | "idle" | "charging";
  animationName?: string;
  task?: string;
  animationDuration?: number;
}) {
  const bgColor =
    status === "moving"
      ? "linear-gradient(135deg, #164e63, #0e7490)"
      : status === "charging"
      ? "linear-gradient(135deg, #422006, #a16207)"
      : "linear-gradient(135deg, #1f2937, #374151)";

  const borderColor =
    status === "moving" ? "#22d3ee" : status === "charging" ? "#fde047" : "#6b7280";

  const dotColor =
    status === "moving" ? "#67e8f9" : status === "charging" ? "#fde047" : "#94a3b8";

  return (
    <div
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y}%`,
        zIndex: 25,
        animation: animationName ? `${animationName} ${animationDuration || 12}s ease-in-out infinite` : undefined,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        pointerEvents: "none",
      }}
    >
      {/* AMR 바디 */}
      <div
        style={{
          width: 36,
          height: 24,
          background: bgColor,
          border: `2px solid ${borderColor}`,
          borderRadius: 5,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow:
            status === "charging"
              ? undefined
              : `0 2px 8px rgba(0,0,0,0.5)`,
          animation:
            status === "charging" ? "render-amr-charge 1.5s ease-in-out infinite" : undefined,
        }}
      >
        {/* 인디케이터 도트 */}
        <div
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: dotColor,
            boxShadow: status === "moving" ? `0 0 6px ${dotColor}` : undefined,
          }}
        />
      </div>
      {/* 라벨 */}
      <span
        style={{
          marginTop: 2,
          fontSize: 7,
          fontWeight: 700,
          color: borderColor,
          textShadow: "0 1px 4px rgba(0,0,0,0.9)",
          whiteSpace: "nowrap",
          letterSpacing: "0.03em",
        }}
      >
        {label}
      </span>
      {/* 상태 텍스트 */}
      <span
        style={{
          fontSize: 6,
          color: dotColor,
          textShadow: "0 1px 3px rgba(0,0,0,0.9)",
        }}
      >
        {status === "moving" ? "이동 중" : status === "charging" ? "충전 중" : "대기"}
      </span>
      {/* 임무 설명 */}
      {task && (
        <span
          style={{
            fontSize: 6,
            color: "#94a3b8",
            textShadow: "0 1px 3px rgba(0,0,0,0.9)",
            whiteSpace: "nowrap",
          }}
        >
          {task}
        </span>
      )}
    </div>
  );
}



function Render3DView({
  selectedId,
  onSelect,
}: {
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const [debugMode, setDebugMode] = useState(false);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);
  const [clickLog, setClickLog] = useState<{ x: number; y: number }[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!debugMode || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setMousePos({ x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10 });
  }, [debugMode]);

  const handleDebugClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!debugMode || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.round(((e.clientX - rect.left) / rect.width) * 100 * 10) / 10;
    const y = Math.round(((e.clientY - rect.top) / rect.height) * 100 * 10) / 10;
    setClickLog((prev) => [...prev.slice(-19), { x, y }]);
  }, [debugMode]);

  return (
    <div style={{ position: "relative" }}>
      {/* 디버그 모드 토글 */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <button
          onClick={() => { setDebugMode((v) => !v); setMousePos(null); }}
          style={{
            padding: "3px 10px",
            fontSize: 9,
            fontWeight: 700,
            borderRadius: 4,
            border: debugMode ? "1px solid #f59e0b" : "1px solid #374151",
            background: debugMode ? "#422006" : "#1f2937",
            color: debugMode ? "#fde047" : "#6b7280",
            cursor: "pointer",
          }}
        >
          {debugMode ? "DEBUG ON" : "DEBUG OFF"}
        </button>
        {debugMode && mousePos && (
          <span style={{ fontSize: 11, fontWeight: 700, color: "#fde047", fontFamily: "monospace" }}>
            x: {mousePos.x}% &nbsp; y: {mousePos.y}%
          </span>
        )}
        {debugMode && clickLog.length > 0 && (
          <button
            onClick={() => setClickLog([])}
            style={{
              padding: "2px 8px", fontSize: 8, borderRadius: 3,
              border: "1px solid #374151", background: "#1f2937", color: "#9ca3af", cursor: "pointer",
            }}
          >
            로그 초기화
          </button>
        )}
      </div>

      <div
        ref={containerRef}
        style={{ position: "relative", borderRadius: 10, overflow: "hidden", cursor: debugMode ? "crosshair" : "default" }}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setMousePos(null)}
        onClick={handleDebugClick}
      >
      {/* 3D 렌더 이미지 */}
      <img
        src="/factory-3d.png"
        alt="주조 공장 3D 렌더링"
        style={{
          width: "100%",
          height: "auto",
          display: "block",
          borderRadius: 10,
        }}
      />

      {/* 디버그: 십자선 + 좌표 표시 */}
      {debugMode && mousePos && (
        <>
          {/* 수평선 */}
          <div style={{
            position: "absolute", left: 0, top: `${mousePos.y}%`,
            width: "100%", height: 1, background: "rgba(253, 224, 71, 0.4)", pointerEvents: "none", zIndex: 50,
          }} />
          {/* 수직선 */}
          <div style={{
            position: "absolute", left: `${mousePos.x}%`, top: 0,
            width: 1, height: "100%", background: "rgba(253, 224, 71, 0.4)", pointerEvents: "none", zIndex: 50,
          }} />
          {/* 좌표 라벨 */}
          <div style={{
            position: "absolute",
            left: `${mousePos.x}%`, top: `${mousePos.y}%`,
            transform: "translate(12px, -28px)",
            background: "rgba(0,0,0,0.85)", border: "1px solid #fde047",
            borderRadius: 4, padding: "2px 6px", pointerEvents: "none", zIndex: 60, whiteSpace: "nowrap",
          }}>
            <span style={{ fontSize: 10, fontWeight: 700, color: "#fde047", fontFamily: "monospace" }}>
              ({mousePos.x}, {mousePos.y})
            </span>
          </div>
        </>
      )}

      {/* 디버그: 클릭 기록 마커 */}
      {debugMode && clickLog.map((pt, i) => (
        <div key={i} style={{
          position: "absolute", left: `${pt.x}%`, top: `${pt.y}%`,
          width: 8, height: 8, borderRadius: "50%",
          background: "#ef4444", border: "1.5px solid #fff",
          transform: "translate(-4px, -4px)", pointerEvents: "none", zIndex: 55,
        }}>
          <span style={{
            position: "absolute", left: 12, top: -3,
            fontSize: 8, color: "#fca5a5", fontFamily: "monospace", whiteSpace: "nowrap",
          }}>
            {i + 1}. ({pt.x}, {pt.y})
          </span>
        </div>
      ))}

      {/* === JetCobot280 2대 === */}
      <CobotOverlay id="COBOT-001" label="COBOT-001" x={17} y={44} />
      <CobotOverlay id="COBOT-002" label="COBOT-002" x={7} y={62} />

      {/* === AMR 3대 === */}
      <AMROverlay id="AMR-001" label="AMR-001" x={30} y={37}
                  status="moving" animationName="render-amr-patrol-1"
                  task="원자재→용해" animationDuration={10} />
      <AMROverlay id="AMR-002" label="AMR-002" x={81} y={52}
                  status="moving" animationName="render-amr-patrol-2"
                  task="탈형→후처리→검사" animationDuration={24} />
      <AMROverlay id="AMR-003" label="AMR-003" x={55} y={67}
                  status="moving" animationName="render-amr-patrol-3"
                  task="검사→출고" animationDuration={10} />

      {/* 인터랙티브 핫스팟 오버레이 */}
      {HOTSPOTS.map((hs) => {
        const zone = ZONES.find((z) => z.id === hs.zoneId);
        if (!zone) return null;
        const isSelected = selectedId === zone.id;
        const colors = zoneColor(zone.status);

        return (
          <div
            key={zone.id}
            onClick={() => onSelect(zone.id)}
            style={{
              position: "absolute",
              left: `${hs.x}%`,
              top: `${hs.y}%`,
              width: `${hs.w}%`,
              height: `${hs.h}%`,
              cursor: "pointer",
              border: isSelected
                ? `2px solid ${colors.border}`
                : "none",
              borderRadius: 6,
              background: isSelected
                ? "rgba(0,0,0,0.5)"
                : "transparent",
              transition: "all 0.2s ease",
            }}
            title={zone.detail}
          >
            {/* 구역명 — 핫스팟 위쪽 바깥에 표시 (장비와 겹침 방지) */}
            <div
              style={{
                position: "absolute",
                bottom: "calc(100% + 4px)",
                left: "50%",
                transform: "translateX(-50%)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                pointerEvents: "none",
                zIndex: 20,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                <span
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: statusDotColor(zone.status),
                    boxShadow: `0 0 6px ${statusDotColor(zone.status)}`,
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontSize: 18,
                    fontWeight: 700,
                    color: "#fff",
                    textShadow: "0 2px 6px rgba(0,0,0,0.9), 0 0 12px rgba(0,0,0,0.7)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {zone.name}
                </span>
              </div>
              {/* 온도 표시 */}
              {zone.temp !== undefined && (
                <span
                  style={{
                    fontSize: 14,
                    color: "#fb923c",
                    textShadow: "0 1px 4px rgba(0,0,0,0.9)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {zone.temp}°C
                </span>
              )}
              {/* 장비 표시 */}
              {zone.equipment && (
                <span
                  style={{
                    fontSize: 12,
                    color: "#fcd34d",
                    textShadow: "0 1px 4px rgba(0,0,0,0.9)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {zone.equipment}
              </span>
            )}
            </div>

            {/* 선택 시 상세 팝업 */}
            {isSelected && (
              <div
                style={{
                  position: "absolute",
                  bottom: "calc(100% + 40px)",
                  left: "50%",
                  transform: "translateX(-50%)",
                  background: "rgba(17, 24, 39, 0.95)",
                  border: "1px solid #4b5563",
                  borderRadius: 6,
                  padding: "8px 12px",
                  minWidth: 180,
                  maxWidth: 240,
                  zIndex: 100,
                  boxShadow: "0 4px 20px rgba(0,0,0,0.7)",
                  pointerEvents: "none",
                }}
              >
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#f9fafb",
                    marginBottom: 4,
                  }}
                >
                  {zone.name}
                </div>
                <div style={{ fontSize: 10, color: "#9ca3af", lineHeight: 1.5 }}>
                  {zone.detail}
                </div>
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
      })}
    </div>

      {/* 디버그: 클릭 로그 패널 */}
      {debugMode && clickLog.length > 0 && (
        <div style={{
          marginTop: 6, background: "#111827", border: "1px solid #374151",
          borderRadius: 6, padding: "8px 10px", maxHeight: 120, overflowY: "auto",
        }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: "#fde047", marginBottom: 4 }}>
            클릭 좌표 로그 (최근 {clickLog.length}개)
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "2px 12px" }}>
            {clickLog.map((pt, i) => (
              <span key={i} style={{ fontSize: 9, color: "#9ca3af", fontFamily: "monospace" }}>
                {i + 1}. x:{pt.x} y:{pt.y}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------------------
// View Toggle Button
// ----------------------------------------------------------------

function ViewToggle({
  mode,
  onToggle,
}: {
  mode: "3d" | "interactive" | "map2";
  onToggle: (m: "3d" | "interactive" | "map2") => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        gap: 2,
        background: "#1f2937",
        borderRadius: 6,
        padding: 2,
        border: "1px solid #374151",
      }}
    >
      {[
        { key: "3d" as const, label: "맵 1: 3D 공장" },
        { key: "interactive" as const, label: "인터랙티브 맵" },
        { key: "map2" as const, label: "맵 2: 공정 레이아웃" },
      ].map((item) => (
        <button
          key={item.key}
          onClick={() => onToggle(item.key)}
          style={{
            padding: "4px 12px",
            fontSize: 10,
            fontWeight: 600,
            borderRadius: 4,
            border: "none",
            cursor: "pointer",
            background: mode === item.key ? "#3b82f6" : "transparent",
            color: mode === item.key ? "#fff" : "#9ca3af",
            transition: "all 0.15s ease",
          }}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

// ----------------------------------------------------------------
// Main Component
// ----------------------------------------------------------------

export default function FactoryMap() {
  const [selectedId, setSelectedId] = useState<string>("");
  const [viewMode, setViewMode] = useState<"3d" | "interactive" | "map2">("3d");

  function handleSelect(id: string) {
    setSelectedId((prev) => (prev === id ? "" : id));
  }

  return (
    <div
      style={{
        width: "100%",
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
            <ViewToggle mode={viewMode} onToggle={setViewMode} />
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

          {/* === 3D Render View === */}
          {viewMode === "3d" && (
            <Render3DView selectedId={selectedId} onSelect={handleSelect} />
          )}

          {/* === Map 2: 공정 레이아웃 편집기 === */}
          {viewMode === "map2" && (
            <FactoryMapEditor />
          )}

          {/* === Interactive Isometric Map View === */}
          {viewMode === "interactive" && (
          /* 3D Isometric view container */
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
          )}

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
