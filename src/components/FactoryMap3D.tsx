"use client";

import { useState, useRef, useCallback, Suspense } from "react";
import dynamic from "next/dynamic";

// Three.js Canvas는 SSR과 호환되지 않으므로 dynamic import 사용
const ThreeCanvas = dynamic(
  () => import("./FactoryMap3DCanvas"),
  {
    ssr: false,
    loading: () => <LoadingSpinner />,
  }
);

// 로딩 스피너 컴포넌트
function LoadingSpinner() {
  return (
    <div
      style={{
        width: "100%",
        aspectRatio: "2 / 1",
        background: "#1f2937",
        borderRadius: 8,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          border: "3px solid #374151",
          borderTop: "3px solid #3b82f6",
          borderRadius: "50%",
          animation: "factory3d-spin 0.8s linear infinite",
        }}
      />
      <span style={{ color: "#9ca3af", fontSize: 12 }}>3D 모델 로딩 중...</span>
      <style>{`
        @keyframes factory3d-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// 메인 래퍼 컴포넌트 - 편집 모드 토글 + Canvas
export default function FactoryMap3D() {
  const [editMode, setEditMode] = useState(false);

  return (
    <div style={{ position: "relative", width: "100%" }}>
      {/* 편집 모드 토글 버튼 */}
      <div
        style={{
          position: "absolute",
          top: 12,
          left: 12,
          zIndex: 10,
          display: "flex",
          gap: 8,
          alignItems: "center",
        }}
      >
        <button
          onClick={() => setEditMode((prev) => !prev)}
          style={{
            padding: "6px 14px",
            fontSize: 11,
            fontWeight: 600,
            borderRadius: 6,
            border: editMode ? "1px solid #f59e0b" : "1px solid #4b5563",
            background: editMode ? "rgba(245, 158, 11, 0.2)" : "rgba(31, 41, 55, 0.8)",
            color: editMode ? "#fbbf24" : "#9ca3af",
            cursor: "pointer",
            backdropFilter: "blur(8px)",
            transition: "all 0.2s ease",
          }}
        >
          {editMode ? "편집 모드 ON" : "편집 모드 OFF"}
        </button>
        {editMode && (
          <span style={{ fontSize: 10, color: "#fbbf24", opacity: 0.8 }}>
            드래그: 이동 | Ctrl+D: 복사 | Delete: 삭제
          </span>
        )}
      </div>

      {/* 조작 안내 */}
      <div
        style={{
          position: "absolute",
          bottom: 12,
          right: 12,
          zIndex: 10,
          padding: "6px 10px",
          background: "rgba(17, 24, 39, 0.8)",
          borderRadius: 6,
          backdropFilter: "blur(8px)",
          border: "1px solid #374151",
        }}
      >
        <span style={{ fontSize: 9, color: "#6b7280" }}>
          좌클릭: 회전 | 우클릭: 이동 | 스크롤: 줌
        </span>
      </div>

      <ThreeCanvas editMode={editMode} />
    </div>
  );
}
