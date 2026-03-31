"""
Casting Factory - Photorealistic 3D Scene v2
Blender 5.1 Python Script

공장 레이아웃 (3x3 그리드):
  Row 1: 원자재 보관 | 용해 구역 | 주형 구역
  Row 2: 주조 구역   | 냉각 구역 | 탈형 구역
  Row 3: 후처리 구역 | 검사 구역 | 적재/출고

장비: 용해로 2, 조형기 1, 컨베이어 1, 검사 카메라 1, AMR 3, JetCobot280 2
"""

import bpy
import math
import os
from mathutils import Vector

# ============================================================
# 설정
# ============================================================

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(os.path.dirname(OUTPUT_DIR), "public", "factory-3d.png")

ZONE_SIZE = 5.0
GAP = 0.4
FLOOR_THICKNESS = 0.2
WALL_HEIGHT = 6.0

# JetCobot280 스케일 팩터 (시각적 비중 강화)
COBOT_SCALE = 3.0
AMR_SCALE = 2.5

# ============================================================
# 유틸리티
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in [bpy.data.materials, bpy.data.meshes, bpy.data.curves]:
        for item in block:
            block.remove(item)


def make_mat(name, color, metallic=0.0, roughness=0.5,
             emission_color=None, emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission_color and emission_strength > 0:
        bsdf.inputs["Emission Color"].default_value = (*emission_color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 1.0:
        mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
        bsdf.inputs["Alpha"].default_value = alpha
    return mat


def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def box(name, loc, size, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    if mat: assign_mat(o, mat)
    return o


def cyl(name, loc, r, h, mat=None, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    if mat: assign_mat(o, mat)
    return o


def sphere(name, loc, r, mat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=16)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.shade_smooth()
    if mat: assign_mat(o, mat)
    return o


def zone_center(col, row):
    x = (col - 1) * (ZONE_SIZE + GAP) + ZONE_SIZE / 2
    y = -((row - 1) * (ZONE_SIZE + GAP) + ZONE_SIZE / 2)
    return (x, y)


def parent_to(parent, children):
    for c in children:
        c.parent = parent


# ============================================================
# 머티리얼
# ============================================================

def create_materials():
    M = {}
    M["concrete"]    = make_mat("Concrete",    (0.32, 0.30, 0.28), roughness=0.9)
    M["concrete_lt"] = make_mat("ConcreteLt",  (0.45, 0.43, 0.40), roughness=0.85)
    M["wall"]        = make_mat("Wall",        (0.72, 0.72, 0.72), roughness=0.65)
    M["metal"]       = make_mat("Metal",       (0.72, 0.74, 0.75), metallic=0.9, roughness=0.25)
    M["dark_metal"]  = make_mat("DarkMetal",   (0.12, 0.12, 0.14), metallic=0.85, roughness=0.35)
    M["steel_blue"]  = make_mat("SteelBlue",   (0.22, 0.32, 0.50), metallic=0.7, roughness=0.3)

    M["furnace"]     = make_mat("Furnace",     (0.55, 0.22, 0.08), metallic=0.3, roughness=0.65)
    M["furnace_glow"]= make_mat("FurnaceGlow", (0.1, 0.02, 0.0),
                                emission_color=(1.0, 0.35, 0.05), emission_strength=20.0)

    M["cobot_white"] = make_mat("CobotWhite",  (0.93, 0.93, 0.93), metallic=0.05, roughness=0.2)
    M["cobot_base"]  = make_mat("CobotBase",   (0.52, 0.52, 0.55), metallic=0.35, roughness=0.35)
    M["cobot_led"]   = make_mat("CobotLED",    (0.0, 0.08, 0.0),
                                emission_color=(0.0, 1.0, 0.2), emission_strength=12.0)

    M["amr_body"]    = make_mat("AMRBody",     (0.95, 0.72, 0.08), metallic=0.2, roughness=0.35)
    M["amr_sensor"]  = make_mat("AMRSensor",   (0.08, 0.08, 0.10), metallic=0.5, roughness=0.25)
    M["rubber"]      = make_mat("Rubber",      (0.04, 0.04, 0.04), roughness=0.95)

    M["belt"]        = make_mat("Belt",        (0.06, 0.06, 0.06), roughness=0.92)
    M["frame"]       = make_mat("Frame",       (0.22, 0.32, 0.50), metallic=0.7, roughness=0.3)

    M["safety_yellow"]= make_mat("SafetyYellow",(0.95, 0.85, 0.0),
                                 emission_color=(0.9, 0.8, 0.0), emission_strength=0.3)
    M["safety_red"]  = make_mat("SafetyRed",   (0.9, 0.15, 0.1),
                                emission_color=(0.9, 0.1, 0.05), emission_strength=0.2)

    M["mold"]        = make_mat("Mold",        (0.55, 0.45, 0.30), roughness=0.95)
    M["product"]     = make_mat("Product",     (0.18, 0.18, 0.20), metallic=0.82, roughness=0.45)
    M["pallet"]      = make_mat("Pallet",      (0.42, 0.28, 0.12), roughness=0.82)
    M["camera_body"] = make_mat("CamBody",     (0.10, 0.10, 0.12), metallic=0.6, roughness=0.25)

    M["zone_line"]   = make_mat("ZoneLine",    (0.85, 0.85, 0.2),
                                emission_color=(0.85, 0.85, 0.2), emission_strength=0.4)
    M["pipe"]        = make_mat("Pipe",        (0.5, 0.5, 0.52), metallic=0.8, roughness=0.3)
    M["green_light"] = make_mat("GreenLight",  (0.0, 0.1, 0.0),
                                emission_color=(0.0, 0.9, 0.15), emission_strength=5.0)
    M["red_light"]   = make_mat("RedLight",    (0.1, 0.0, 0.0),
                                emission_color=(0.9, 0.1, 0.0), emission_strength=5.0)
    M["orange_light"]= make_mat("OrangeLight", (0.1, 0.05, 0.0),
                                emission_color=(1.0, 0.5, 0.0), emission_strength=5.0)
    return M


# ============================================================
# JetCobot280
# ============================================================

def create_jetcobot280(name, location, rotation_z=0.0, M=None):
    """JetCobot280: 회색 베이스 + 흰색 S자 암 + 초록 LED"""
    S = COBOT_SCALE
    parts = []
    bx, by = location
    bz = FLOOR_THICKNESS

    # 베이스 (회색 직사각형 + 둥근 상단)
    base = box(f"{name}_base", (bx, by, bz + 0.075*S), (0.18*S, 0.14*S, 0.15*S), M["cobot_base"])
    parts.append(base)

    base_top = cyl(f"{name}_btop", (bx, by, bz + 0.16*S), 0.065*S, 0.025*S, M["cobot_base"])
    parts.append(base_top)

    # 포트 패널
    ports = box(f"{name}_ports", (bx, by - 0.068*S, bz + 0.045*S), (0.12*S, 0.008*S, 0.04*S), M["dark_metal"])
    parts.append(ports)

    # 포트 LED 표시 (색 포인트)
    for i, color_mat in enumerate(["green_light", "red_light", "orange_light", "cobot_led"]):
        led_x = bx - 0.035*S + i * 0.023*S
        led = box(f"{name}_port_led_{i}", (led_x, by - 0.073*S, bz + 0.045*S),
                  (0.012*S, 0.003*S, 0.008*S), M[color_mat])
        parts.append(led)

    # 파워 버튼 (좌측)
    pwr = cyl(f"{name}_pwr", (bx - 0.092*S, by, bz + 0.075*S), 0.01*S, 0.005*S, M["dark_metal"],
              rot=(0, math.pi/2, 0))
    parts.append(pwr)

    # === 로봇 암 (S자 6축) ===

    # 관절 1: 베이스 위 회전
    j1z = bz + 0.19*S
    j1 = sphere(f"{name}_j1", (bx, by, j1z), 0.042*S, M["cobot_white"])
    parts.append(j1)

    # 세그먼트 1: 수직 상승
    s1z = j1z + 0.10*S
    s1 = cyl(f"{name}_s1", (bx, by, s1z), 0.034*S, 0.16*S, M["cobot_white"])
    bpy.ops.object.shade_smooth()
    parts.append(s1)

    # 관절 2
    j2z = s1z + 0.10*S
    j2 = sphere(f"{name}_j2", (bx, by, j2z), 0.038*S, M["cobot_white"])
    parts.append(j2)

    # 세그먼트 2: 우측으로 꺾여 올라감
    dx2 = 0.07*S
    s2z = j2z + 0.08*S
    s2 = cyl(f"{name}_s2", (bx + dx2*0.5, by, s2z), 0.032*S, 0.17*S, M["cobot_white"],
             rot=(0, math.radians(25), 0))
    bpy.ops.object.shade_smooth()
    parts.append(s2)

    # 관절 3
    j3x = bx + dx2
    j3z = j2z + 0.16*S
    j3 = sphere(f"{name}_j3", (j3x, by, j3z), 0.036*S, M["cobot_white"])
    parts.append(j3)

    # 세그먼트 3: 좌측으로 꺾여 올라감
    dx3 = -0.07*S
    s3z = j3z + 0.08*S
    s3 = cyl(f"{name}_s3", (j3x + dx3*0.5, by, s3z), 0.030*S, 0.16*S, M["cobot_white"],
             rot=(0, math.radians(-25), 0))
    bpy.ops.object.shade_smooth()
    parts.append(s3)

    # 관절 4
    j4x = j3x + dx3
    j4z = j3z + 0.16*S
    j4 = sphere(f"{name}_j4", (j4x, by, j4z), 0.034*S, M["cobot_white"])
    parts.append(j4)

    # 세그먼트 4: 우측으로 짧게
    dx4 = 0.055*S
    s4z = j4z + 0.065*S
    s4 = cyl(f"{name}_s4", (j4x + dx4*0.5, by, s4z), 0.027*S, 0.13*S, M["cobot_white"],
             rot=(0, math.radians(22), 0))
    bpy.ops.object.shade_smooth()
    parts.append(s4)

    # 관절 5
    j5x = j4x + dx4
    j5z = j4z + 0.13*S
    j5 = sphere(f"{name}_j5", (j5x, by, j5z), 0.030*S, M["cobot_white"])
    parts.append(j5)

    # 세그먼트 5: 짧은 최종
    s5z = j5z + 0.04*S
    s5 = cyl(f"{name}_s5", (j5x, by, s5z), 0.024*S, 0.065*S, M["cobot_white"])
    bpy.ops.object.shade_smooth()
    parts.append(s5)

    # 엔드 이펙터 헤드
    eez = s5z + 0.05*S
    ee = box(f"{name}_ee", (j5x, by, eez), (0.05*S, 0.05*S, 0.045*S), M["cobot_white"])
    parts.append(ee)

    # LED 매트릭스 (정면)
    led = box(f"{name}_led", (j5x, by + 0.027*S, eez), (0.042*S, 0.004*S, 0.038*S), M["cobot_led"])
    parts.append(led)

    # 케이블 (베이스 뒤에서 나옴)
    cable = cyl(f"{name}_cable", (bx, by - 0.08*S, bz + 0.01), 0.006*S, 0.3*S, M["dark_metal"],
                rot=(math.radians(85), 0, 0))
    parts.append(cable)

    # Empty 그룹핑 + 회전
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(bx, by, 0))
    empty = bpy.context.active_object
    empty.name = name
    empty.rotation_euler.z = math.radians(rotation_z)
    parent_to(empty, parts)
    return empty


# ============================================================
# AMR (자율이동로봇)
# ============================================================

def create_amr(name, location, rotation_z=0.0, M=None):
    S = AMR_SCALE
    parts = []
    ax, ay = location
    az = FLOOR_THICKNESS

    # 바퀴 4개
    for dx, dy in [(-0.18, -0.15), (0.18, -0.15), (-0.18, 0.15), (0.18, 0.15)]:
        w = cyl(f"{name}_w_{dx}_{dy}", (ax+dx*S, ay+dy*S, az+0.04*S),
                0.045*S, 0.035*S, M["rubber"], rot=(math.pi/2, 0, 0))
        parts.append(w)

    # 바디
    body = box(f"{name}_body", (ax, ay, az+0.12*S), (0.48*S, 0.38*S, 0.12*S), M["amr_body"])
    parts.append(body)

    # 범퍼 (전/후)
    for sign in [1, -1]:
        bumper = box(f"{name}_bumper_{sign}", (ax, ay + sign*0.20*S, az+0.10*S),
                     (0.50*S, 0.02*S, 0.06*S), M["dark_metal"])
        parts.append(bumper)

    # 상판
    top = box(f"{name}_top", (ax, ay, az+0.19*S), (0.44*S, 0.34*S, 0.02*S), M["metal"])
    parts.append(top)

    # 라이다 타워
    tower = cyl(f"{name}_lidar", (ax, ay, az+0.23*S), 0.045*S, 0.04*S, M["amr_sensor"])
    parts.append(tower)

    # 상태 LED 바
    led_bar = box(f"{name}_led", (ax, ay+0.18*S, az+0.175*S), (0.15*S, 0.005*S, 0.015*S), M["green_light"])
    parts.append(led_bar)

    # 비상정지 버튼
    estop = cyl(f"{name}_estop", (ax+0.20*S, ay, az+0.19*S), 0.015*S, 0.015*S, M["safety_red"])
    parts.append(estop)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(ax, ay, 0))
    empty = bpy.context.active_object
    empty.name = name
    empty.rotation_euler.z = math.radians(rotation_z)
    parent_to(empty, parts)
    return empty


# ============================================================
# 용해로
# ============================================================

def create_furnace(name, loc, M):
    parts = []
    fx, fy = loc
    fz = FLOOR_THICKNESS

    outer = cyl(f"{name}_outer", (fx, fy, fz+0.7), 0.55, 1.4, M["furnace"])
    parts.append(outer)

    rim = cyl(f"{name}_rim", (fx, fy, fz+1.42), 0.58, 0.05, M["dark_metal"])
    parts.append(rim)

    base_ring = cyl(f"{name}_baser", (fx, fy, fz+0.02), 0.60, 0.04, M["dark_metal"])
    parts.append(base_ring)

    glow = cyl(f"{name}_glow", (fx, fy, fz+1.38), 0.45, 0.1, M["furnace_glow"])
    parts.append(glow)

    # 탕도
    spout = cyl(f"{name}_spout", (fx+0.6, fy, fz+0.55), 0.07, 0.3, M["dark_metal"],
                rot=(0, math.radians(75), 0))
    parts.append(spout)

    # 제어 패널
    panel = box(f"{name}_panel", (fx-0.7, fy, fz+0.7), (0.08, 0.4, 0.5), M["dark_metal"])
    parts.append(panel)
    # 패널 디스플레이
    disp = box(f"{name}_disp", (fx-0.66, fy, fz+0.8), (0.005, 0.2, 0.15), M["green_light"])
    parts.append(disp)

    # 배기 덕트
    duct = cyl(f"{name}_duct", (fx, fy, fz+1.8), 0.15, 0.7, M["pipe"])
    parts.append(duct)

    return parts


# ============================================================
# 조형기
# ============================================================

def create_molding_machine(name, loc, M):
    parts = []
    mx, my = loc
    mz = FLOOR_THICKNESS

    frame = box(f"{name}_frame", (mx, my, mz+0.85), (1.4, 1.0, 1.7), M["steel_blue"])
    parts.append(frame)

    press = box(f"{name}_press", (mx, my, mz+1.45), (0.9, 0.7, 0.35), M["metal"])
    parts.append(press)

    bed = box(f"{name}_bed", (mx, my, mz+0.28), (0.9, 0.7, 0.18), M["mold"])
    parts.append(bed)

    for dx in [-0.40, 0.40]:
        hyd = cyl(f"{name}_hyd_{dx}", (mx+dx, my, mz+1.05), 0.05, 0.6, M["metal"])
        parts.append(hyd)

    panel = box(f"{name}_cpanel", (mx+0.85, my, mz+1.0), (0.1, 0.5, 0.6), M["dark_metal"])
    parts.append(panel)

    # 경고등
    warn = sphere(f"{name}_warn", (mx+0.85, my, mz+1.35), 0.06, M["orange_light"])
    parts.append(warn)

    return parts


# ============================================================
# 컨베이어 (롤러)
# ============================================================

def create_conveyor(name, loc, length=5.0, M=None):
    parts = []
    cx, cy = loc
    cz = FLOOR_THICKNESS

    for dy in [-0.25, 0.25]:
        rail = box(f"{name}_rail_{dy}", (cx, cy+dy, cz+0.45), (length, 0.06, 0.08), M["frame"])
        parts.append(rail)

    for dx in [-length/2+0.2, length/2-0.2]:
        for dy in [-0.25, 0.25]:
            leg = box(f"{name}_leg_{dx}_{dy}", (cx+dx, cy+dy, cz+0.21), (0.05, 0.05, 0.42), M["frame"])
            parts.append(leg)

    belt = box(f"{name}_belt", (cx, cy, cz+0.48), (length-0.15, 0.44, 0.025), M["belt"])
    parts.append(belt)

    n_rollers = int(length / 0.18)
    for i in range(n_rollers):
        rx = cx - length/2 + 0.1 + i * (length-0.2) / max(n_rollers-1, 1)
        roller = cyl(f"{name}_r{i}", (rx, cy, cz+0.46), 0.03, 0.44, M["metal"], rot=(math.pi/2, 0, 0))
        parts.append(roller)

    # 제품 (컨베이어 위 맨홀 커버 3개)
    for i in range(3):
        px = cx - 1.0 + i * 1.2
        prod = cyl(f"{name}_prod{i}", (px, cy, cz+0.52), 0.15, 0.05, M["product"])
        parts.append(prod)

    return parts


# ============================================================
# 비전 검사 카메라
# ============================================================

def create_inspection_camera(name, loc, M):
    parts = []
    ix, iy = loc
    iz = FLOOR_THICKNESS

    stand = cyl(f"{name}_stand", (ix, iy, iz+1.0), 0.04, 2.0, M["metal"])
    parts.append(stand)
    base_d = cyl(f"{name}_base", (ix, iy, iz+0.02), 0.20, 0.04, M["dark_metal"])
    parts.append(base_d)

    arm = box(f"{name}_arm", (ix+0.3, iy, iz+1.9), (0.6, 0.05, 0.05), M["metal"])
    parts.append(arm)

    cam = box(f"{name}_cam", (ix+0.55, iy, iz+1.75), (0.12, 0.10, 0.15), M["camera_body"])
    parts.append(cam)
    lens = cyl(f"{name}_lens", (ix+0.55, iy, iz+1.65), 0.035, 0.06, M["dark_metal"])
    parts.append(lens)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.01,
                                     location=(ix+0.55, iy, iz+1.62))
    ring = bpy.context.active_object
    ring.name = f"{name}_ring"
    assign_mat(ring, M["green_light"])
    parts.append(ring)

    return parts


# ============================================================
# 원자재 보관
# ============================================================

def create_storage(name, loc, M):
    parts = []
    sx, sy = loc
    sz = FLOOR_THICKNESS

    # 대형 랙 선반
    rack = box(f"{name}_rack", (sx, sy, sz+1.2), (2.4, 0.7, 2.4), M["steel_blue"])
    parts.append(rack)

    for i in range(4):
        shelf = box(f"{name}_shelf{i}", (sx, sy, sz+0.3+i*0.6), (2.3, 0.65, 0.04), M["metal"])
        parts.append(shelf)

    # 컨테이너/빈
    for i in range(3):
        for j in range(2):
            cont = box(f"{name}_bin{i}_{j}", (sx-0.6+j*0.8, sy, sz+0.5+i*0.6),
                       (0.55, 0.45, 0.35), M["mold"])
            parts.append(cont)

    # 포크리프트 존 표시 (바닥)
    fork_zone = box(f"{name}_fz", (sx, sy+1.0, sz+0.001), (2.0, 0.05, 0.005), M["safety_yellow"])
    parts.append(fork_zone)

    return parts


# ============================================================
# 팔레트 + 제품
# ============================================================

def create_pallet_stack(name, loc, count=3, M=None):
    parts = []
    px, py = loc
    pz = FLOOR_THICKNESS

    for i in range(count):
        zo = i * 0.25
        pallet = box(f"{name}_pal{i}", (px, py, pz+0.06+zo), (1.0, 0.7, 0.1), M["pallet"])
        parts.append(pallet)

        for j in range(4):
            prod = cyl(f"{name}_p{i}_{j}", (px-0.2+j*0.15, py, pz+0.14+zo), 0.10, 0.05, M["product"])
            parts.append(prod)

    return parts


# ============================================================
# 안전 배리어
# ============================================================

def create_safety_barrier(name, start, end, M):
    """두 점 사이 안전 배리어 (볼라드 + 체인)"""
    parts = []
    sx, sy = start
    ex, ey = end
    z = FLOOR_THICKNESS
    length = math.sqrt((ex-sx)**2 + (ey-sy)**2)
    angle = math.atan2(ey-sy, ex-sx)
    n_posts = max(int(length / 1.5), 2)

    for i in range(n_posts + 1):
        t = i / n_posts
        px = sx + t * (ex - sx)
        py = sy + t * (ey - sy)
        post = cyl(f"{name}_post{i}", (px, py, z+0.4), 0.03, 0.8, M["safety_yellow"])
        parts.append(post)

    # 수평 바 (체인 대신)
    mid_x = (sx + ex) / 2
    mid_y = (sy + ey) / 2
    bar = box(f"{name}_bar", (mid_x, mid_y, z+0.65), (length, 0.02, 0.02), M["safety_yellow"])
    bar.rotation_euler.z = angle
    parts.append(bar)

    return parts


# ============================================================
# 배관 / 덕트
# ============================================================

def create_overhead_pipes(M):
    """천장 배관"""
    parts = []
    total_w = 3 * ZONE_SIZE + 2 * GAP
    z = WALL_HEIGHT - 0.8

    # 메인 배관 2줄 (좌→우)
    for i, dy in enumerate([-3.0, -10.0]):
        pipe = cyl(f"pipe_main_{i}", (total_w/2, dy, z), 0.08, total_w+1, M["pipe"],
                   rot=(0, math.pi/2, 0))
        parts.append(pipe)

    # 가로 배관 3줄
    total_d = 3 * ZONE_SIZE + 2 * GAP
    for i in range(3):
        px = ZONE_SIZE * 0.5 + i * (ZONE_SIZE + GAP)
        pipe = cyl(f"pipe_cross_{i}", (px, -total_d/2, z-0.15), 0.06, total_d, M["pipe"],
                   rot=(math.pi/2, 0, 0))
        parts.append(pipe)

    return parts


# ============================================================
# 공장 건물
# ============================================================

def create_building(M):
    parts = []
    tw = 3 * ZONE_SIZE + 2 * GAP
    td = 3 * ZONE_SIZE + 2 * GAP
    cx = tw / 2
    cy = -td / 2

    # 바닥
    floor = box("Floor", (cx, cy, 0), (tw+3, td+3, FLOOR_THICKNESS), M["concrete"])
    parts.append(floor)

    # 바닥 에폭시 코팅 구역 (각 존마다 약간 밝은 색)
    for col in range(1, 4):
        for row in range(1, 4):
            zx, zy = zone_center(col, row)
            epoxy = box(f"epoxy_{col}_{row}", (zx, zy, FLOOR_THICKNESS+0.001),
                        (ZONE_SIZE-0.2, ZONE_SIZE-0.2, 0.005), M["concrete_lt"])
            parts.append(epoxy)

    # 벽 3면 (정면 개방)
    back_wall = box("BackWall", (cx, cy-td/2-0.65, WALL_HEIGHT/2),
                    (tw+3, 0.3, WALL_HEIGHT), M["wall"])
    parts.append(back_wall)

    left_wall = box("LeftWall", (-0.65, cy, WALL_HEIGHT/2),
                    (0.3, td+3, WALL_HEIGHT), M["wall"])
    parts.append(left_wall)

    right_wall = box("RightWall", (tw+0.65, cy, WALL_HEIGHT/2),
                     (0.3, td+3, WALL_HEIGHT), M["wall"])
    parts.append(right_wall)

    # 구역 경계선 (바닥 노란색)
    for col in range(1, 4):
        for row in range(1, 4):
            zx, zy = zone_center(col, row)
            half = ZONE_SIZE / 2 - 0.05

            for i, (dx, dy, sw, sh) in enumerate([
                (0, half, ZONE_SIZE-0.1, 0.04),
                (0, -half, ZONE_SIZE-0.1, 0.04),
                (-half, 0, 0.04, ZONE_SIZE-0.1),
                (half, 0, 0.04, ZONE_SIZE-0.1),
            ]):
                line = box(f"zl_{col}_{row}_{i}", (zx+dx, zy+dy, FLOOR_THICKNESS+0.002),
                           (sw, sh, 0.005), M["zone_line"])
                parts.append(line)

    return parts


# ============================================================
# 조명
# ============================================================

def setup_lighting():
    tw = 3 * ZONE_SIZE + 2 * GAP
    td = 3 * ZONE_SIZE + 2 * GAP

    # 천장 Area Light (3x3 = 9개)
    for i in range(3):
        for j in range(3):
            lx = ZONE_SIZE * 0.5 + i * (ZONE_SIZE + GAP)
            ly = -(ZONE_SIZE * 0.5 + j * (ZONE_SIZE + GAP))
            bpy.ops.object.light_add(type='AREA', location=(lx, ly, WALL_HEIGHT - 0.3))
            light = bpy.context.active_object
            light.name = f"CeilingLight_{i}_{j}"
            light.data.energy = 600
            light.data.size = 1.2
            light.data.color = (1.0, 0.96, 0.92)

    # Sun (부드러운 측광)
    bpy.ops.object.light_add(type='SUN', location=(12, -8, 15))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 0.8
    sun.data.angle = math.radians(20)
    sun.data.color = (0.95, 0.95, 1.0)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(-25))

    # 용해 구역 앰비언트
    for i, furnace_loc in enumerate([(zone_center(2,1)[0]-1.0, zone_center(2,1)[1]),
                                      (zone_center(2,1)[0]+1.0, zone_center(2,1)[1])]):
        bpy.ops.object.light_add(type='POINT', location=(furnace_loc[0], furnace_loc[1], 2.5))
        fl = bpy.context.active_object
        fl.name = f"FurnaceLight_{i}"
        fl.data.energy = 300
        fl.data.color = (1.0, 0.4, 0.1)
        fl.data.shadow_soft_size = 0.8


# ============================================================
# 카메라
# ============================================================

def setup_camera():
    tw = 3 * ZONE_SIZE + 2 * GAP
    td = 3 * ZONE_SIZE + 2 * GAP
    cx = tw / 2
    cy = -td / 2

    # 3/4 뷰 - 공장 전체를 약간 위에서 내려다보는 각도
    bpy.ops.object.camera_add(
        location=(cx + 12, cy - 10, 10),
        rotation=(math.radians(60), 0, math.radians(50))
    )
    cam = bpy.context.active_object
    cam.name = "FactoryCamera"
    cam.data.lens = 28  # 와이드 앵글
    cam.data.clip_end = 150
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 18
    cam.data.dof.aperture_fstop = 8.0

    bpy.context.scene.camera = cam

    # 트래킹 (공장 중심을 바라봄)
    bpy.ops.object.empty_add(location=(cx, cy, 1.5))
    target = bpy.context.active_object
    target.name = "CamTarget"

    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    return cam


# ============================================================
# 렌더 설정
# ============================================================

def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1280  # 2:1 비율
    scene.render.resolution_percentage = 100

    cycles = scene.cycles
    cycles.samples = 256
    cycles.use_denoising = True

    # Metal GPU (Apple Silicon)
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    cycles.device = 'GPU'

    # World 배경 (어두운 회색 - 창 밖)
    world = bpy.data.worlds.get("World")
    if not world:
        world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.12, 0.13, 0.16, 1.0)
        bg.inputs[1].default_value = 0.2

    scene.render.filepath = OUTPUT_PATH
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'


# ============================================================
# 메인
# ============================================================

def main():
    print("=== Casting Factory 3D Scene v2 ===")
    print(f"Output: {OUTPUT_PATH}")

    clear_scene()
    M = create_materials()

    # 건물
    create_building(M)

    # --- 구역별 장비 ---

    # (1,1) 원자재 보관
    cx, cy = zone_center(1, 1)
    create_storage("Storage", (cx, cy), M)

    # (2,1) 용해 구역 - 용해로 2대
    cx, cy = zone_center(2, 1)
    create_furnace("Furnace_A", (cx-1.2, cy), M)
    create_furnace("Furnace_B", (cx+1.2, cy), M)

    # (3,1) 주형 구역 - 조형기
    cx, cy = zone_center(3, 1)
    create_molding_machine("Molder", (cx, cy), M)

    # (1,2) 주조 구역 - JetCobot #1 + 작업대
    cx, cy = zone_center(1, 2)
    create_jetcobot280("COBOT-001", (cx-0.5, cy+0.3), rotation_z=30, M=M)
    box("WorkTable_1", (cx+1.2, cy+0.3, FLOOR_THICKNESS+0.45), (1.4, 1.0, 0.9), M["metal"])
    # 주조 금형
    box("CastMold_1", (cx+1.2, cy+0.3, FLOOR_THICKNESS+0.92), (0.5, 0.5, 0.05), M["mold"])
    # 안전 배리어
    create_safety_barrier("Barrier_1",
                          (cx-2.2, cy-2.2), (cx+2.2, cy-2.2), M)

    # (2,2) 냉각 구역 - 컨베이어
    cx, cy = zone_center(2, 2)
    create_conveyor("Conveyor", (cx, cy), length=4.5, M=M)

    # (3,2) 탈형 구역
    cx, cy = zone_center(3, 2)
    box("DemoldTable", (cx, cy, FLOOR_THICKNESS+0.4), (1.8, 1.2, 0.8), M["metal"])
    box("WasteBin", (cx+1.8, cy, FLOOR_THICKNESS+0.3), (0.9, 0.7, 0.6), M["dark_metal"])
    # 탈형된 제품들
    for i in range(3):
        cyl(f"DemoldProd_{i}", (cx-0.3+i*0.3, cy, FLOOR_THICKNESS+0.83), 0.12, 0.05, M["product"])

    # (1,3) 후처리 구역 - JetCobot #2
    cx, cy = zone_center(1, 3)
    create_jetcobot280("COBOT-002", (cx-0.3, cy), rotation_z=-20, M=M)
    box("GrindTable", (cx+1.3, cy, FLOOR_THICKNESS+0.45), (1.2, 0.9, 0.9), M["metal"])
    # 그라인딩 디스크
    cyl("GrindDisc", (cx+1.3, cy, FLOOR_THICKNESS+0.95), 0.15, 0.02, M["dark_metal"])

    # (2,3) 검사 구역 - 비전 카메라
    cx, cy = zone_center(2, 3)
    create_inspection_camera("VisionCam", (cx-0.5, cy), M)
    box("InspTable", (cx+0.5, cy, FLOOR_THICKNESS+0.4), (1.8, 1.0, 0.8), M["metal"])
    # 검사 대상 제품
    for i in range(4):
        cyl(f"InspProd_{i}", (cx+0.1+i*0.3, cy, FLOOR_THICKNESS+0.83), 0.10, 0.05, M["product"])

    # (3,3) 적재/출고 구역 - 팔레트
    cx, cy = zone_center(3, 3)
    create_pallet_stack("Pallet_A", (cx-1.2, cy-0.5), 3, M)
    create_pallet_stack("Pallet_B", (cx+0.8, cy-0.5), 2, M)
    create_pallet_stack("Pallet_C", (cx-0.2, cy+1.2), 1, M)

    # --- AMR 3대 ---
    cx1, cy1 = zone_center(1, 1)
    cx2, cy2 = zone_center(1, 2)
    create_amr("AMR-001", (cx1+2.8, (cy1+cy2)/2), rotation_z=180, M=M)

    cx3, cy3 = zone_center(2, 2)
    cx4, cy4 = zone_center(2, 3)
    create_amr("AMR-002", (cx3+2.0, (cy3+cy4)/2), rotation_z=200, M=M)

    cx5, cy5 = zone_center(3, 3)
    create_amr("AMR-003", (cx5-0.5, cy5+1.8), rotation_z=90, M=M)

    # --- 배관 제거됨 (시야 확보) ---

    # --- 안전 배리어 (용해 구역) ---
    fcx, fcy = zone_center(2, 1)
    create_safety_barrier("FurnaceBarrier",
                          (fcx-2.4, fcy+2.4), (fcx+2.4, fcy+2.4), M)

    # --- 조명 + 카메라 + 렌더 설정 ---
    setup_lighting()
    setup_camera()
    setup_render()

    # --- 렌더링 ---
    print("Rendering with Cycles (256 samples, Metal GPU)...")
    bpy.ops.render.render(write_still=True)
    print(f"Complete! → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
