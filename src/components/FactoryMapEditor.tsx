"use client";

import { useState, useCallback, useRef } from "react";
import {
  Bot,
  Camera,
  ArrowRight,
  Plus,
  Trash2,
  GripVertical,
  Settings,
  Eye,
  Pencil,
  Package,
  X,
} from "lucide-react";

// ----------------------------------------------------------------
// Types
// ----------------------------------------------------------------

type ZoneType = "robot_arm" | "conveyor" | "camera" | "workstation" | "storage";
type ZoneStatus = "active" | "idle" | "error";

interface MapZone {
  id: string;
  name: string;
  type: ZoneType;
  x: number; // percentage 0-100
  y: number; // percentage 0-100
  width: number; // percentage
  height: number; // percentage
  status: ZoneStatus;
  description: string;
}

// ----------------------------------------------------------------
// 기본 공정 레이아웃 (좌→우 생산라인)
// ----------------------------------------------------------------

// 3D 렌더 투영 좌표 기반 기본 레이아웃
const DEFAULT_ZONES: MapZone[] = [
  // 왼쪽: 주조 구역 4개 (로봇팔 4대)
  {
    id: "cast-a",
    name: "주조 A (주탕/탈형)",
    type: "robot_arm",
    x: 16,
    y: 28,
    width: 14,
    height: 12,
    status: "active",
    description: "Casting Zone A — 주탕(용탕 주입) + 탈형(주물 분리) 겸용 로봇암",
  },
  {
    id: "cast-b",
    name: "주조 B (주탕/탈형)",

    type: "robot_arm",
    x: 12,
    y: 36,
    width: 14,
    height: 12,
    status: "active",
    description: "Casting Zone A — 주탕(용탕 주입) + 탈형(주물 분리) 겸용 로봇암",
  },
  {
    id: "cast-c",
    name: "주조 C (주탕/탈형)",
    type: "robot_arm",
    x: 7,
    y: 46,
    width: 14,
    height: 12,
    status: "active",
    description: "Casting Zone C — 주탕(용탕 주입) + 탈형(주물 분리) 겸용 로봇암",
  },
  {
    id: "cast-d",
    name: "주조 D (주탕/탈형)",
    type: "robot_arm",
    x: 0,
    y: 60,
    width: 14,
    height: 12,
    status: "idle",
    description: "Casting Zone D — 주탕(용탕 주입) + 탈형(주물 분리) 겸용 로봇암",
  },
  // 중앙: 컨베이어 2개 + 카메라 2개
  {
    id: "conv-1",
    name: "컨베이어 #1 + 검사",
    type: "conveyor",
    x: 37,
    y: 31,
    width: 26,
    height: 12,
    status: "active",
    description: "Finishing & Inspection Zone 1 — 상단 라인 컨베이어 + 비전 카메라",
  },
  {
    id: "conv-2",
    name: "컨베이어 #2 + 검사",
    type: "conveyor",
    x: 37,
    y: 52,
    width: 26,
    height: 12,
    status: "active",
    description: "Finishing & Inspection Zone 2 — 하단 라인 컨베이어 + 비전 카메라",
  },
  // 오른쪽: Storage + Shipping + Charging
  {
    id: "storage-1",
    name: "공유 보관 1",
    type: "storage",
    x: 70,
    y: 29,
    width: 14,
    height: 12,
    status: "active",
    description: "Shared Storage Zone 1 — 적재 로봇팔이 완제품 보관",
  },
  {
    id: "shipping",
    name: "출하 구역",
    type: "workstation",
    x: 74,
    y: 37,
    width: 14,
    height: 12,
    status: "active",
    description: "Shipping Zone — 출하 대기 및 트럭 적재",
  },
  {
    id: "storage-2",
    name: "공유 보관 2",
    type: "storage",
    x: 79,
    y: 46,
    width: 14,
    height: 12,
    status: "active",
    description: "Shared Storage Zone 2 — 적재 로봇팔이 완제품 보관",
  },
  {
    id: "charging",
    name: "충전소",
    type: "workstation",
    x: 87,
    y: 60,
    width: 12,
    height: 12,
    status: "idle",
    description: "Charging Zone — AMR/로봇 충전 구역",
  },
];

// ----------------------------------------------------------------
// 상수
// ----------------------------------------------------------------

const ZONE_TYPE_META: Record<
  ZoneType,
  { color: string; icon: typeof Bot; label: string }
> = {
  robot_arm: { color: "#3b82f6", icon: Bot, label: "로봇암" },
  conveyor: { color: "#22c55e", icon: ArrowRight, label: "컨베이어" },
  camera: { color: "#a855f7", icon: Camera, label: "비전 카메라" },
  workstation: { color: "#f97316", icon: Settings, label: "작업대" },
  storage: { color: "#6b7280", icon: Package, label: "보관 구역" },
};

const STATUS_COLOR: Record<ZoneStatus, string> = {
  active: "#22c55e",
  idle: "#9ca3af",
  error: "#ef4444",
};

const STATUS_LABEL: Record<ZoneStatus, string> = {
  active: "가동 중",
  idle: "대기",
  error: "오류",
};

// ----------------------------------------------------------------
// 유틸
// ----------------------------------------------------------------

function generateId(): string {
  return `zone-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
}

// ----------------------------------------------------------------
// 메인 컴포넌트
// ----------------------------------------------------------------

export default function FactoryMapEditor() {
  const [zones, setZones] = useState<MapZone[]>(DEFAULT_ZONES);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  // 드래그 상태
  const mapRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<{
    zoneId: string;
    offsetX: number;
    offsetY: number;
  } | null>(null);

  // ---- 드래그 핸들러 ----
  const handleMouseDown = useCallback(
    (e: React.MouseEvent, zoneId: string) => {
      if (!editMode) return;
      e.preventDefault();
      e.stopPropagation();

      const mapEl = mapRef.current;
      if (!mapEl) return;

      const rect = mapEl.getBoundingClientRect();
      const zone = zones.find((z) => z.id === zoneId);
      if (!zone) return;

      const cursorX = ((e.clientX - rect.left) / rect.width) * 100;
      const cursorY = ((e.clientY - rect.top) / rect.height) * 100;

      dragRef.current = {
        zoneId,
        offsetX: cursorX - zone.x,
        offsetY: cursorY - zone.y,
      };

      setSelectedId(zoneId);
    },
    [editMode, zones]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!dragRef.current || !mapRef.current) return;

      const rect = mapRef.current.getBoundingClientRect();
      const cursorX = ((e.clientX - rect.left) / rect.width) * 100;
      const cursorY = ((e.clientY - rect.top) / rect.height) * 100;

      const newX = Math.max(
        0,
        Math.min(100 - 5, cursorX - dragRef.current.offsetX)
      );
      const newY = Math.max(
        0,
        Math.min(100 - 5, cursorY - dragRef.current.offsetY)
      );

      setZones((prev) =>
        prev.map((z) =>
          z.id === dragRef.current!.zoneId ? { ...z, x: newX, y: newY } : z
        )
      );
    },
    []
  );

  const handleMouseUp = useCallback(() => {
    dragRef.current = null;
  }, []);

  // ---- 구역 추가 ----
  const handleAddZone = useCallback(
    (name: string, type: ZoneType) => {
      const newZone: MapZone = {
        id: generateId(),
        name,
        type,
        x: 40,
        y: 40,
        width: 12,
        height: 14,
        status: "idle",
        description: `${name} — 새로 추가된 구역`,
      };
      setZones((prev) => [...prev, newZone]);
      setSelectedId(newZone.id);
      setShowAddForm(false);
    },
    []
  );

  // ---- 구역 삭제 ----
  const handleDelete = useCallback((id: string) => {
    setZones((prev) => prev.filter((z) => z.id !== id));
    setSelectedId(null);
  }, []);

  // ---- 선택된 구역 정보 ----
  const selectedZone = zones.find((z) => z.id === selectedId) ?? null;

  const AMR_STYLES = `
    @keyframes map2-amr1 {
      0%   { left: 28%; top: 37%; }
      8%   { left: 28%; top: 37%; }
      20%  { left: 34%; top: 38%; }
      32%  { left: 46%; top: 40%; }
      45%  { left: 46%; top: 40%; }
      58%  { left: 34%; top: 38%; }
      70%  { left: 28%; top: 44%; }
      82%  { left: 34%; top: 50%; }
      90%  { left: 46%; top: 55%; }
      95%  { left: 46%; top: 55%; }
      100% { left: 28%; top: 37%; }
    }
    @keyframes map2-amr2 {
      0%   { left: 55%; top: 40%; }
      6%   { left: 55%; top: 40%; }
      18%  { left: 64%; top: 38%; }
      28%  { left: 72%; top: 38%; }
      40%  { left: 72%; top: 38%; }
      52%  { left: 64%; top: 42%; }
      60%  { left: 55%; top: 55%; }
      70%  { left: 64%; top: 52%; }
      80%  { left: 72%; top: 50%; }
      90%  { left: 72%; top: 50%; }
      100% { left: 55%; top: 40%; }
    }
    @keyframes map2-amr3 {
      0%   { left: 80%; top: 52%; }
      10%  { left: 80%; top: 52%; }
      25%  { left: 86%; top: 58%; }
      40%  { left: 90%; top: 65%; }
      55%  { left: 90%; top: 65%; }
      70%  { left: 86%; top: 58%; }
      85%  { left: 80%; top: 52%; }
      100% { left: 80%; top: 52%; }
    }
  `;

  return (
    <div
      style={{
        background: "#111827",
        borderRadius: 10,
        border: editMode
          ? "2px dashed #fbbf24"
          : "1px solid #1e3a5f",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <style>{AMR_STYLES}</style>
      {/* 상단 툴바 */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 12px",
          background: "#0f172a",
          borderBottom: "1px solid #1e293b",
        }}
      >
        <span
          style={{
            fontSize: 11,
            fontWeight: 700,
            color: "#e2e8f0",
            letterSpacing: "0.05em",
          }}
        >
          공정 레이아웃 편집기
        </span>
        <div style={{ display: "flex", gap: 6 }}>
          {editMode && (
            <button
              onClick={() => setShowAddForm(true)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 4,
                padding: "4px 10px",
                fontSize: 10,
                fontWeight: 600,
                borderRadius: 4,
                border: "1px solid #22c55e",
                background: "rgba(34, 197, 94, 0.1)",
                color: "#4ade80",
                cursor: "pointer",
              }}
            >
              <Plus size={10} /> 구역 추가
            </button>
          )}
          <button
            onClick={() => {
              setEditMode((prev) => !prev);
              if (editMode) setSelectedId(null);
            }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              padding: "4px 10px",
              fontSize: 10,
              fontWeight: 600,
              borderRadius: 4,
              border: editMode
                ? "1px solid #fbbf24"
                : "1px solid #6b7280",
              background: editMode
                ? "rgba(251, 191, 36, 0.15)"
                : "transparent",
              color: editMode ? "#fbbf24" : "#9ca3af",
              cursor: "pointer",
            }}
          >
            {editMode ? (
              <>
                <Eye size={10} /> 보기 모드
              </>
            ) : (
              <>
                <Pencil size={10} /> 편집 모드
              </>
            )}
          </button>
        </div>
      </div>

      {/* 맵 영역 */}
      <div
        ref={mapRef}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          position: "relative",
          width: "100%",
          height: 0,
          paddingBottom: "50%",
          background: "#1f2937",
          backgroundImage: "url('/factory-3d-map2.png')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          borderRadius: 10,
          overflow: "hidden",
          cursor: editMode ? "crosshair" : "default",
          userSelect: "none",
        }}
      >

        {/* 구역 렌더링 */}
        {zones.map((zone) => {
          const meta = ZONE_TYPE_META[zone.type];
          const Icon = meta.icon;
          const isSelected = zone.id === selectedId;

          return (
            <div
              key={zone.id}
              onMouseDown={(e) => handleMouseDown(e, zone.id)}
              onClick={(e) => {
                e.stopPropagation();
                setSelectedId(zone.id === selectedId ? null : zone.id);
              }}
              style={{
                position: "absolute",
                left: `${zone.x}%`,
                top: `${zone.y}%`,
                width: `${zone.width}%`,
                height: `${zone.height}%`,
                background: isSelected ? "rgba(0,0,0,0.3)" : "transparent",
                borderRadius: 8,
                border: isSelected ? `2px solid ${meta.color}` : "none",
                boxShadow: "none",
                cursor: editMode ? "grab" : "pointer",
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-end",
                padding: "4px 6px",
                gap: 2,
                transition: "background 0.15s ease",
                overflow: "visible",
                zIndex: isSelected ? 10 : 1,
              }}
            >
              {/* 헤더 행 */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                  minWidth: 0,
                }}
              >
                {editMode && (
                  <GripVertical
                    size={10}
                    color="#9ca3af"
                    style={{ flexShrink: 0 }}
                  />
                )}
                <Icon
                  size={12}
                  color={meta.color}
                  style={{ flexShrink: 0 }}
                />
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#fff",
                    textShadow: "0 1px 4px rgba(0,0,0,0.9)",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    lineHeight: 1.2,
                  }}
                >
                  {zone.name}
                </span>
              </div>

              {/* 상태 표시 */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 3,
                }}
              >
                <div
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: STATUS_COLOR[zone.status],
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontSize: 9,
                    color: "#d1d5db",
                    textShadow: "0 1px 3px rgba(0,0,0,0.8)",
                    lineHeight: 1,
                  }}
                >
                  {STATUS_LABEL[zone.status]}
                </span>
              </div>


              {/* 편집 모드: 삭제 버튼 */}
              {editMode && isSelected && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(zone.id);
                  }}
                  style={{
                    position: "absolute",
                    top: 2,
                    right: 2,
                    width: 16,
                    height: 16,
                    borderRadius: "50%",
                    border: "none",
                    background: "#ef4444",
                    color: "#fff",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: 0,
                  }}
                >
                  <Trash2 size={8} />
                </button>
              )}
            </div>
          );
        })}

        {/* 클릭으로 선택 해제 */}
        <div
          onClick={() => setSelectedId(null)}
          style={{
            position: "absolute",
            inset: 0,
            zIndex: 0,
          }}
        />
        {/* === AMR 3대 오버레이 === */}
        {[
          { id: "AMR-001", label: "AMR-001", task: "주조→컨베이어", anim: "map2-amr1", dur: 14, color: "#22d3ee" },
          { id: "AMR-002", label: "AMR-002", task: "컨베이어→보관", anim: "map2-amr2", dur: 16, color: "#22d3ee" },
          { id: "AMR-003", label: "AMR-003", task: "보관→충전소", anim: "map2-amr3", dur: 10, color: "#fde047" },
        ].map((amr) => (
          <div
            key={amr.id}
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              zIndex: 25,
              animation: `${amr.anim} ${amr.dur}s ease-in-out infinite`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              pointerEvents: "none",
            }}
          >
            <div
              style={{
                width: 36,
                height: 24,
                background: "linear-gradient(135deg, #164e63, #0e7490)",
                border: `2px solid ${amr.color}`,
                borderRadius: 5,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
              }}
            >
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: amr.color, boxShadow: `0 0 6px ${amr.color}` }} />
            </div>
            <span style={{ marginTop: 2, fontSize: 8, fontWeight: 700, color: amr.color, textShadow: "0 1px 4px rgba(0,0,0,0.9)", whiteSpace: "nowrap" }}>
              {amr.label}
            </span>
            <span style={{ fontSize: 6, color: "#94a3b8", textShadow: "0 1px 3px rgba(0,0,0,0.9)" }}>
              {amr.task}
            </span>
          </div>
        ))}
      </div>

      {/* 하단 정보 패널 */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "8px 12px",
          background: "#0f172a",
          borderTop: "1px solid #1e293b",
          minHeight: 36,
        }}
      >
        {selectedZone ? (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: STATUS_COLOR[selectedZone.status],
              }}
            />
            <span style={{ fontSize: 10, color: "#e2e8f0", fontWeight: 600 }}>
              {selectedZone.name}
            </span>
            <span style={{ fontSize: 9, color: "#9ca3af" }}>
              {selectedZone.description}
            </span>
          </div>
        ) : (
          <span style={{ fontSize: 9, color: "#6b7280" }}>
            구역을 선택하면 상세 정보가 표시됩니다
          </span>
        )}
        <span style={{ fontSize: 9, color: "#6b7280" }}>
          구역 {zones.length}개
          {editMode && " · 편집 모드"}
        </span>
      </div>

      {/* 구역 추가 모달 */}
      {showAddForm && <AddZoneModal onAdd={handleAddZone} onClose={() => setShowAddForm(false)} />}
    </div>
  );
}

// ----------------------------------------------------------------
// 구역 추가 모달
// ----------------------------------------------------------------

function AddZoneModal({
  onAdd,
  onClose,
}: {
  onAdd: (name: string, type: ZoneType) => void;
  onClose: () => void;
}) {
  const [name, setName] = useState("");
  const [type, setType] = useState<ZoneType>("robot_arm");

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 50,
      }}
    >
      <div
        style={{
          background: "#1f2937",
          borderRadius: 10,
          border: "1px solid #374151",
          padding: 20,
          width: 300,
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ fontSize: 13, fontWeight: 700, color: "#f9fafb" }}>
            새 구역 추가
          </span>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "#9ca3af",
              padding: 0,
            }}
          >
            <X size={14} />
          </button>
        </div>

        {/* 이름 입력 */}
        <div>
          <label
            style={{
              fontSize: 10,
              color: "#9ca3af",
              fontWeight: 600,
              display: "block",
              marginBottom: 4,
            }}
          >
            구역 이름
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="예: 로봇암 #7"
            style={{
              width: "100%",
              padding: "6px 10px",
              fontSize: 11,
              borderRadius: 4,
              border: "1px solid #374151",
              background: "#111827",
              color: "#f9fafb",
              outline: "none",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* 유형 선택 */}
        <div>
          <label
            style={{
              fontSize: 10,
              color: "#9ca3af",
              fontWeight: 600,
              display: "block",
              marginBottom: 4,
            }}
          >
            유형
          </label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as ZoneType)}
            style={{
              width: "100%",
              padding: "6px 10px",
              fontSize: 11,
              borderRadius: 4,
              border: "1px solid #374151",
              background: "#111827",
              color: "#f9fafb",
              outline: "none",
              boxSizing: "border-box",
            }}
          >
            {(Object.keys(ZONE_TYPE_META) as ZoneType[]).map((t) => (
              <option key={t} value={t}>
                {ZONE_TYPE_META[t].label}
              </option>
            ))}
          </select>
        </div>

        {/* 버튼 */}
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button
            onClick={onClose}
            style={{
              padding: "6px 14px",
              fontSize: 10,
              fontWeight: 600,
              borderRadius: 4,
              border: "1px solid #374151",
              background: "transparent",
              color: "#9ca3af",
              cursor: "pointer",
            }}
          >
            취소
          </button>
          <button
            onClick={() => {
              if (name.trim()) onAdd(name.trim(), type);
            }}
            disabled={!name.trim()}
            style={{
              padding: "6px 14px",
              fontSize: 10,
              fontWeight: 600,
              borderRadius: 4,
              border: "none",
              background: name.trim() ? "#3b82f6" : "#374151",
              color: name.trim() ? "#fff" : "#6b7280",
              cursor: name.trim() ? "pointer" : "not-allowed",
            }}
          >
            추가
          </button>
        </div>
      </div>
    </div>
  );
}
