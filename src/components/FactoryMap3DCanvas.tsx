"use client";

import { useState, useRef, useCallback, useEffect, Suspense } from "react";
import { Canvas, useThree, ThreeEvent } from "@react-three/fiber";
import { OrbitControls, useGLTF, Environment, Html } from "@react-three/drei";
import * as THREE from "three";

// GLB 모델 경로
const MODEL_PATH = "/factory-map2.glb";

// 선택된 메시의 원래 색상을 추적하기 위한 맵
const originalColors = new Map<string, THREE.Color>();

// ------------------------------------------------------------------
// 공장 씬 (GLB 모델 + 인터랙션)
// ------------------------------------------------------------------
function FactoryScene({ editMode }: { editMode: boolean }) {
  const { scene } = useGLTF(MODEL_PATH);
  const [selectedMesh, setSelectedMesh] = useState<THREE.Mesh | null>(null);
  const isDragging = useRef(false);
  const dragPlane = useRef(new THREE.Plane(new THREE.Vector3(0, 1, 0), 0));
  const dragOffset = useRef(new THREE.Vector3());
  const { camera, raycaster, gl } = useThree();

  // 클릭하여 메시 선택
  const handleClick = useCallback(
    (e: ThreeEvent<MouseEvent>) => {
      // 드래그 중에는 선택 무시
      if (isDragging.current) return;
      e.stopPropagation();

      const clicked = e.object as THREE.Mesh;

      // 이전 선택 해제 - 원래 색상 복원
      if (selectedMesh && selectedMesh !== clicked) {
        const originalColor = originalColors.get(selectedMesh.uuid);
        if (originalColor && selectedMesh.material instanceof THREE.MeshStandardMaterial) {
          selectedMesh.material.emissive.copy(originalColor);
          selectedMesh.material.emissiveIntensity = 0;
        }
      }

      // 새 메시 선택 - 하이라이트 적용
      if (clicked.material instanceof THREE.MeshStandardMaterial) {
        if (!originalColors.has(clicked.uuid)) {
          originalColors.set(clicked.uuid, clicked.material.emissive.clone());
        }
        clicked.material.emissive.set(0x3b82f6);
        clicked.material.emissiveIntensity = 0.4;
      }

      setSelectedMesh(clicked);
    },
    [selectedMesh]
  );

  // 배경 클릭 시 선택 해제
  const handleMissed = useCallback(() => {
    if (selectedMesh && selectedMesh.material instanceof THREE.MeshStandardMaterial) {
      const originalColor = originalColors.get(selectedMesh.uuid);
      if (originalColor) {
        selectedMesh.material.emissive.copy(originalColor);
        selectedMesh.material.emissiveIntensity = 0;
      }
    }
    setSelectedMesh(null);
  }, [selectedMesh]);

  // 편집 모드에서 드래그 이동 처리
  useEffect(() => {
    if (!editMode || !selectedMesh) return;

    const canvas = gl.domElement;

    const getMouseNDC = (e: MouseEvent): THREE.Vector2 => {
      const rect = canvas.getBoundingClientRect();
      return new THREE.Vector2(
        ((e.clientX - rect.left) / rect.width) * 2 - 1,
        -((e.clientY - rect.top) / rect.height) * 2 + 1
      );
    };

    const handlePointerDown = (e: MouseEvent) => {
      if (e.button !== 0) return; // 좌클릭만

      const mouse = getMouseNDC(e);
      raycaster.setFromCamera(mouse, camera);

      const intersects = raycaster.intersectObject(selectedMesh, false);
      if (intersects.length > 0) {
        isDragging.current = true;

        // Y축 기준 드래그 평면 설정 (선택 메시의 높이)
        dragPlane.current.set(
          new THREE.Vector3(0, 1, 0),
          -intersects[0].point.y
        );

        // 드래그 오프셋 계산 (메시 중심과 클릭 위치의 차이)
        const planePoint = new THREE.Vector3();
        raycaster.ray.intersectPlane(dragPlane.current, planePoint);
        dragOffset.current.copy(selectedMesh.position).sub(planePoint);

        canvas.style.cursor = "grabbing";
      }
    };

    const handlePointerMove = (e: MouseEvent) => {
      if (!isDragging.current) return;

      const mouse = getMouseNDC(e);
      raycaster.setFromCamera(mouse, camera);

      const planePoint = new THREE.Vector3();
      if (raycaster.ray.intersectPlane(dragPlane.current, planePoint)) {
        // XZ 평면에서 이동 (Y는 유지)
        selectedMesh.position.x = planePoint.x + dragOffset.current.x;
        selectedMesh.position.z = planePoint.z + dragOffset.current.z;
      }
    };

    const handlePointerUp = () => {
      if (isDragging.current) {
        isDragging.current = false;
        canvas.style.cursor = "auto";
      }
    };

    canvas.addEventListener("pointerdown", handlePointerDown);
    canvas.addEventListener("pointermove", handlePointerMove);
    canvas.addEventListener("pointerup", handlePointerUp);

    return () => {
      canvas.removeEventListener("pointerdown", handlePointerDown);
      canvas.removeEventListener("pointermove", handlePointerMove);
      canvas.removeEventListener("pointerup", handlePointerUp);
    };
  }, [editMode, selectedMesh, camera, raycaster, gl]);

  return (
    <group>
      {/* GLB 모델 렌더링 - 클릭 이벤트 연결 */}
      <primitive
        object={scene}
        onClick={handleClick}
        onPointerMissed={handleMissed}
      />

      {/* 선택된 메시 이름 표시 */}
      {selectedMesh && (
        <Html
          position={[
            selectedMesh.position.x,
            selectedMesh.position.y + 2,
            selectedMesh.position.z,
          ]}
          center
          style={{ pointerEvents: "none" }}
        >
          <div
            style={{
              background: "rgba(17, 24, 39, 0.9)",
              color: "#e5e7eb",
              padding: "4px 8px",
              borderRadius: 4,
              fontSize: 10,
              fontWeight: 600,
              border: "1px solid #3b82f6",
              whiteSpace: "nowrap",
            }}
          >
            {selectedMesh.name || "이름 없음"}
          </div>
        </Html>
      )}
    </group>
  );
}

// ------------------------------------------------------------------
// 로딩 fallback (Suspense 내부용)
// ------------------------------------------------------------------
function SceneLoader() {
  return (
    <Html center>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            border: "3px solid #374151",
            borderTop: "3px solid #3b82f6",
            borderRadius: "50%",
            animation: "factory3d-spin 0.8s linear infinite",
          }}
        />
        <span style={{ color: "#9ca3af", fontSize: 11 }}>모델 로딩 중...</span>
      </div>
    </Html>
  );
}

// ------------------------------------------------------------------
// Canvas 래퍼 (dynamic import 대상)
// ------------------------------------------------------------------
export default function FactoryMap3DCanvas({
  editMode,
}: {
  editMode: boolean;
}) {
  return (
    <div
      style={{
        width: "100%",
        aspectRatio: "2 / 1",
        borderRadius: 8,
        overflow: "hidden",
      }}
    >
      <Canvas
        style={{ background: "#1f2937" }}
        camera={{
          position: [18, 11, -30],
          fov: 50,
          near: 0.1,
          far: 500,
        }}
        shadows
      >
        {/* 조명 */}
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[10, 20, 10]}
          intensity={1.2}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <directionalLight position={[-5, 10, -5]} intensity={0.3} />

        {/* 환경광 */}
        <Environment preset="warehouse" />

        {/* 카메라 컨트롤 */}
        <OrbitControls
          target={[18, 0, -9]}
          enableDamping
          dampingFactor={0.1}
          minDistance={5}
          maxDistance={100}
          maxPolarAngle={Math.PI / 2.2}
        />

        {/* 바닥 그리드 (참고용) */}
        <gridHelper args={[50, 50, "#374151", "#1f2937"]} />

        {/* 공장 씬 */}
        <Suspense fallback={<SceneLoader />}>
          <FactoryScene editMode={editMode} />
        </Suspense>
      </Canvas>
    </div>
  );
}

// GLB 사전 로드
useGLTF.preload(MODEL_PATH);
