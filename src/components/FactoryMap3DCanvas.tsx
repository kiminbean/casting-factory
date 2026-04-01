"use client";

import { useState, useRef, useCallback, useEffect, useMemo, Suspense } from "react";
import { Canvas, useThree, useFrame, ThreeEvent } from "@react-three/fiber";
import { OrbitControls, useGLTF, Environment, Html } from "@react-three/drei";
import * as THREE from "three";

// GLB 모델 경로
const MODEL_PATH = "/factory-map2.glb";

// 선택된 메시의 원래 색상을 추적하기 위한 맵
const originalColors = new Map<string, THREE.Color>();

// ------------------------------------------------------------------
// AMR 경로 정의 (Blender 좌표 기준, Y=0 바닥)
// ------------------------------------------------------------------
interface PathPoint { x: number; z: number; wait: number }

/*
 * 맵 2 공장 복도 네트워크 (Three.js 좌표: X=가로, Z=세로)
 * Blender (x, y) → Three.js (x, 0, -y)
 *
 * 구역 배치:
 *   주조A(4,2.5) 주조B(4,7) 주조C(4,11.5) 주조D(4,16)
 *   컨베이어1(18,4.5) 컨베이어2(18,13.5)
 *   보관1(32,3) 출하(32,7.5) 보관2(32,11.5) 충전(32,16)
 *
 * 복도:
 *   좌측 세로복도: x=10 (주조↔컨베이어)
 *   우측 세로복도: x=27 (컨베이어↔보관)
 *   가로복도1: z=5 (주조A↔주조B 사이)
 *   가로복도2: z=9 (주조B↔주조C 사이)
 *   가로복도3: z=14 (주조C↔주조D 사이)
 *
 * AMR 규칙: 구역 내부 진입 불가, 복도만 이동
 */
const AMR_PATHS: { id: string; color: string; task: string; speed: number; path: PathPoint[] }[] = [
  {
    id: "AMR-001", color: "#22d3ee", task: "주조→컨베이어", speed: 1.5,
    path: [
      // 주조A 가장자리에서 적재
      { x: 7.5, z: 2.5, wait: 2 },
      // 좌측 세로복도 진입
      { x: 10, z: 2.5, wait: 0 },
      // 가로복도1로 이동
      { x: 10, z: 4.5, wait: 0 },
      // 컨베이어1 좌측 가장자리 도착
      { x: 12, z: 4.5, wait: 1.5 },
      // 복귀: 세로복도
      { x: 10, z: 4.5, wait: 0 },
      // 가로복도2로 남행
      { x: 10, z: 7, wait: 0 },
      // 주조B 가장자리
      { x: 7.5, z: 7, wait: 2 },
      // 세로복도 복귀
      { x: 10, z: 7, wait: 0 },
      // 컨베이어1 방향
      { x: 10, z: 4.5, wait: 0 },
      { x: 12, z: 4.5, wait: 1.5 },
      // 복귀 → 주조A
      { x: 10, z: 4.5, wait: 0 },
      { x: 10, z: 2.5, wait: 0 },
    ],
  },
  {
    id: "AMR-002", color: "#22d3ee", task: "컨베이어→보관", speed: 1.2,
    path: [
      // 컨베이어1 우측에서 수령
      { x: 24, z: 4.5, wait: 2 },
      // 우측 세로복도 진입
      { x: 27, z: 4.5, wait: 0 },
      // 보관1 방향
      { x: 27, z: 3, wait: 0 },
      // 보관1 좌측 가장자리
      { x: 29, z: 3, wait: 1.5 },
      // 복귀
      { x: 27, z: 3, wait: 0 },
      // 컨베이어2로 이동 (세로복도 남행)
      { x: 27, z: 13.5, wait: 0 },
      // 컨베이어2 우측
      { x: 24, z: 13.5, wait: 2 },
      // 세로복도
      { x: 27, z: 13.5, wait: 0 },
      // 보관2
      { x: 27, z: 11.5, wait: 0 },
      { x: 29, z: 11.5, wait: 1.5 },
      // 복귀
      { x: 27, z: 11.5, wait: 0 },
      { x: 27, z: 4.5, wait: 0 },
    ],
  },
  {
    id: "AMR-003", color: "#fde047", task: "보관→출하→충전", speed: 1.0,
    path: [
      // 보관1 가장자리
      { x: 35, z: 3, wait: 2 },
      // 출하 구역 (같은 x축, z만 이동)
      { x: 35, z: 7.5, wait: 2 },
      // 보관2
      { x: 35, z: 11.5, wait: 2 },
      // 출하 구역
      { x: 35, z: 7.5, wait: 2 },
      // 충전소
      { x: 35, z: 16, wait: 4 },
      // 보관1 복귀
      { x: 35, z: 3, wait: 0 },
    ],
  },
];

// ------------------------------------------------------------------
// AMR 3D 오브젝트 (실시간 이동)
// ------------------------------------------------------------------
function AMRUnit({ id, color, task, speed, path }: typeof AMR_PATHS[0]) {
  const meshRef = useRef<THREE.Group>(null);
  const progressRef = useRef(0);
  const segmentRef = useRef(0);
  const waitRef = useRef(0);
  const posRef = useRef(new THREE.Vector3(path[0].x, 0.35, path[0].z));

  useFrame((_, delta) => {
    if (!meshRef.current) return;

    const currentSeg = segmentRef.current;
    const nextSeg = (currentSeg + 1) % path.length;
    const from = path[currentSeg];
    const to = path[nextSeg];

    // 대기 시간 처리
    if (waitRef.current > 0) {
      waitRef.current -= delta;
      return;
    }

    // 이동
    const dx = to.x - from.x;
    const dz = to.z - from.z;
    const dist = Math.sqrt(dx * dx + dz * dz);

    if (dist < 0.01) {
      // 같은 위치 → 다음 세그먼트
      segmentRef.current = nextSeg;
      waitRef.current = to.wait;
      return;
    }

    progressRef.current += (speed * delta) / dist;

    if (progressRef.current >= 1) {
      // 세그먼트 완료
      progressRef.current = 0;
      segmentRef.current = nextSeg;
      waitRef.current = to.wait;
      posRef.current.set(to.x, 0.35, to.z);
    } else {
      // 보간 이동
      const t = progressRef.current;
      posRef.current.set(
        from.x + dx * t,
        0.35,
        from.z + dz * t
      );
    }

    meshRef.current.position.copy(posRef.current);

    // AMR 방향 회전 (이동 방향을 바라봄)
    if (dist > 0.1) {
      const angle = Math.atan2(dx, dz);
      meshRef.current.rotation.y = angle;
    }
  });

  return (
    <group ref={meshRef} position={[path[0].x, 0.35, path[0].z]}>
      {/* AMR 바디 */}
      <mesh castShadow>
        <boxGeometry args={[0.8, 0.25, 0.6]} />
        <meshStandardMaterial color={color === "#fde047" ? "#a16207" : "#0e7490"} metalness={0.3} roughness={0.5} />
      </mesh>
      {/* 상단 라이다 */}
      <mesh position={[0, 0.2, 0]}>
        <cylinderGeometry args={[0.06, 0.06, 0.1, 8]} />
        <meshStandardMaterial color="#1e293b" metalness={0.5} roughness={0.3} />
      </mesh>
      {/* 상태 LED */}
      <mesh position={[0, 0.3, 0]}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2} />
      </mesh>
      {/* 라벨 */}
      <Html position={[0, 0.8, 0]} center style={{ pointerEvents: "none" }}>
        <div style={{
          background: "rgba(0,0,0,0.8)", color, padding: "2px 6px",
          borderRadius: 3, fontSize: 8, fontWeight: 700, whiteSpace: "nowrap",
          border: `1px solid ${color}`,
        }}>
          {id}
          <span style={{ fontSize: 6, color: "#94a3b8", marginLeft: 4 }}>{task}</span>
        </div>
      </Html>
    </group>
  );
}

// ------------------------------------------------------------------
// 공장 씬 (GLB 모델 + 인터랙션)
// ------------------------------------------------------------------
// Blender 재질 이름 → 색상 매핑
const MAT_COLORS: Record<string, { color: string; metal?: number; rough?: number; emissive?: string; emissiveI?: number }> = {
  "Floor":     { color: "#333338", rough: 0.8 },
  "Zone":      { color: "#b5b0aa", rough: 0.5 },
  "Metal":     { color: "#8c8c90", metal: 0.4, rough: 0.3 },
  "Robot":     { color: "#eaeaef", metal: 0.1, rough: 0.25 },
  "CobotWhite":{ color: "#eaeaef", metal: 0.1, rough: 0.25 },
  "Conv":      { color: "#4d4d52", metal: 0.5, rough: 0.4 },
  "Cam":       { color: "#333840", metal: 0.3, rough: 0.3 },
  "Pallet":    { color: "#6b4720", rough: 0.8 },
  "Furnace":   { color: "#8c3814", metal: 0.3, rough: 0.65 },
  "Glow":      { color: "#ff8020", emissive: "#ff6000", emissiveI: 2 },
  "ZoneLine":  { color: "#d9d920", rough: 0.5 },
  "Shelf":     { color: "#9a9aa0", metal: 0.3, rough: 0.4 },
  "Charge":    { color: "#1a66cc", metal: 0.2 },
  "Product":   { color: "#808080", metal: 0.2 },
  "AMR_Body":  { color: "#f0b810", metal: 0.2, rough: 0.35 },
  "AMR_Sensor":{ color: "#f0b810", metal: 0.2, rough: 0.35 },
  "RingLight": { color: "#fffce0", emissive: "#fff8b0", emissiveI: 1 },
};

function applyMaterialColors(scene: THREE.Group) {
  // 방법 1: 재질 이름 기반 (Blender 재질명과 매칭)
  for (const mat of Object.values(scene.userData)) {
    // skip
  }

  // 모든 재질을 순회하며 색상 적용
  const processedMats = new Set<string>();
  scene.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) return;

    const materials = Array.isArray(child.material) ? child.material : [child.material];
    for (const mat of materials) {
      if (!mat || processedMats.has(mat.uuid)) continue;
      processedMats.add(mat.uuid);

      if (!(mat instanceof THREE.MeshStandardMaterial || mat instanceof THREE.MeshPhysicalMaterial)) continue;

      // 재질 이름으로 매칭
      const matName = mat.name || "";
      let matched = false;
      for (const [key, cfg] of Object.entries(MAT_COLORS)) {
        if (matName.includes(key) || matName.toLowerCase().includes(key.toLowerCase())) {
          mat.color.set(cfg.color);
          if (cfg.metal !== undefined) mat.metalness = cfg.metal;
          if (cfg.rough !== undefined) mat.roughness = cfg.rough;
          if (cfg.emissive) { mat.emissive = new THREE.Color(cfg.emissive); mat.emissiveIntensity = cfg.emissiveI || 1; }
          matched = true;
          break;
        }
      }

      // 매칭 안 되고 거의 흰색인 재질 → 기본 회색으로
      if (!matched) {
        const c = mat.color;
        if (c.r > 0.85 && c.g > 0.85 && c.b > 0.85) {
          // 오브젝트 이름으로 2차 매칭
          const objName = child.name.toLowerCase();
          if (objName.includes("floor")) { mat.color.set("#333338"); }
          else if (objName.includes("zone") || objName.includes("epoxy")) { mat.color.set("#b5b0aa"); }
          else if (objName.includes("cobot") || objName.includes("mycobot")) { mat.color.set("#eaeaef"); }
          else if (objName.includes("furnace")) { mat.color.set("#8c3814"); }
          else if (objName.includes("conv")) { mat.color.set("#4d4d52"); }
          else if (objName.includes("pallet") || objName.includes("ship")) { mat.color.set("#6b4720"); }
          else if (objName.includes("shelf")) { mat.color.set("#9a9aa0"); }
          else if (objName.includes("charge")) { mat.color.set("#1a66cc"); }
          else if (objName.includes("barrier") || objName.includes("bollard")) { mat.color.set("#d9d920"); }
          else { mat.color.set("#7a7a80"); mat.metalness = 0.2; mat.roughness = 0.5; }
        }
      }
    }
  });
}

function FactoryScene({ editMode }: { editMode: boolean }) {
  const { scene } = useGLTF(MODEL_PATH);
  const [selectedMesh, setSelectedMesh] = useState<THREE.Mesh | null>(null);
  const colorsApplied = useRef(false);

  // 씬 로드 후 색상 적용 — 매 렌더 시 강제 적용
  useEffect(() => {
    if (!colorsApplied.current) {
      applyMaterialColors(scene);
      // 모든 재질을 clone하여 독립 수정 가능하게
      scene.traverse((child) => {
        if (child instanceof THREE.Mesh && child.material) {
          if (Array.isArray(child.material)) {
            child.material = child.material.map(m => m.clone());
          } else {
            child.material = child.material.clone();
          }
        }
      });
      applyMaterialColors(scene); // clone 후 재적용
      colorsApplied.current = true;
    }
  }, [scene]);
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

      {/* AMR 3대 실시간 이동 */}
      {AMR_PATHS.map((amr) => (
        <AMRUnit key={amr.id} {...amr} />
      ))}

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
// 스페이스+좌클릭 = Pan 커스텀 컨트롤
// ------------------------------------------------------------------
function SpacePanControls() {
  const controlsRef = useRef<any>(null);
  const spaceDown = useRef(false);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" && !spaceDown.current) {
        spaceDown.current = true;
        if (controlsRef.current) {
          controlsRef.current.mouseButtons.LEFT = 2; // PAN
        }
      }
    };
    const onKeyUp = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        spaceDown.current = false;
        if (controlsRef.current) {
          controlsRef.current.mouseButtons.LEFT = 0; // ROTATE
        }
      }
    };
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, []);

  return (
    <OrbitControls
      ref={controlsRef}
      target={[18, 0, -9]}
      enableDamping
      dampingFactor={0.1}
      minDistance={5}
      maxDistance={100}
      maxPolarAngle={Math.PI / 2.2}
    />
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
          position: [18, 11, 30],
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

        {/* 카메라 컨트롤 — 스페이스+좌클릭=Pan 지원 */}
        <SpacePanControls />

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
