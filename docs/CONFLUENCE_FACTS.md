# Confluence Fact Reference — casting-factory

> **addinedute(addinedu_team_2)** space 주요 설계/기술 문서의 팩트 체크 정리본
> 원본 페이지 변경 시 이 파일을 업데이트해야 함
> **마지막 업데이트**: 2026-04-08 (Atlassian 검색 장애 우회: `fetchAtlassian` + ARI 포맷 직접 호출로 22개 페이지 전량 수집 완료)
> **READ-ONLY**: 이 문서는 로컬 참조용이며 Confluence 원본은 수정하지 않음

## 사용 원칙

1. **코드베이스 우선(Source of Truth)**: 이 파일의 Confluence 팩트와 실제 코드가 충돌할 때는 **코드가 정답**. 불일치는 하단 "알려진 불일치" 표에 기록.
2. **주기적 재검증**: Confluence 페이지는 계속 업데이트되므로 **주 1회** 이상 재수집 권장. (launchd 로 매일 자동 감지/커밋되지만, 주 1회 수기 확인 필요)
3. **재수집 방법** (장애 회피):
   ```
   mcp__atlassian__fetchAtlassian
     cloudId=a9e33fd3-7ec5-4a67-84d1-725ae97d5f0d
     method=GET
     product=confluence
     uri=/wiki/api/v2/pages/{PAGE_ID}
     id=ari:cloud:confluence:a9e33fd3-7ec5-4a67-84d1-725ae97d5f0d:page/{PAGE_ID}
   ```
   (기존 `getConfluencePage`는 Hystrix circuit 장애 시 실패. `fetchAtlassian`은 직접 API 호출로 우회 가능)

---

## 목차

1. [01_Project_Design](#1-01_project_design)
   - [1.1 System Architecture (3375131)](#11-system-architecture-3375131)
   - [1.2 Detailed Design (6651919)](#12-detailed-design-6651919)
   - [1.3 v_model (3506182)](#13-v_model-3506182)
   - [1.4 User_Requirements (3375120)](#14-user_requirements-3375120)
   - [1.5 System_Requirements_v3 (6258774)](#15-system_requirements_v3-6258774)
   - [1.6 Layout (4915220)](#16-layout-4915220)
   - [1.7 MVP_Prioritization (3375144)](#17-mvp_prioritization-3375144)
   - [1.8 Scenarios (15729093)](#18-scenarios-15729093)
2. [02_Domain_Research](#2-02_domain_research)
   - [2.1 intro (3211297)](#21-intro-3211297)
   - [2.2 Casting (3375162)](#22-casting-3375162)
   - [2.3 Logistics (3637320)](#23-logistics-3637320)
   - [2.4 Terminology (3407906)](#24-terminology-3407906)
3. [03_Technical_Research](#3-03_technical_research)
   - [3.1 HW_Research (8552537)](#31-hw_research-8552537)
   - [3.2 SW_Research (8552545)](#32-sw_research-8552545)
   - [3.3 DB_Research (8585277)](#33-db_research-8585277)
   - [3.4 SW_Control (15433852)](#34-sw_control-15433852)
4. [04_Implementation](#4-04_implementation)
   - [4.1 VLA (3276898)](#41-vla-3276898)
   - [4.2 LLM (3703098)](#42-llm-3703098)
   - [4.3 Prototypes (3407954)](#43-prototypes-3407954)
   - [4.4 DB (5898574)](#44-db-5898574)
   - [4.5 GUI (6389916)](#45-gui-6389916)
   - [4.6 SmartCast Robotics GitHub 폴더 구조 초안 (20217883)](#46-smartcast-robotics-github-폴더-구조-초안-20217883)
5. [통합 팩트 시트 (Quick Reference)](#통합-팩트-시트-quick-reference)
6. [알려진 Confluence ↔ 코드 불일치](#알려진-confluence--코드-불일치)
7. [참조 정책](#참조-정책)

---

## 1. 01_Project_Design

Root page: **3145739** (`01_Project_Design`)

### 1.1 System Architecture (3375131)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3375131
**최종 수정**: v26 (2026-03-26 초안, 이후 V1~V4 진화)

#### 핵심 팩트 — 4버전 진화

| 버전 | 구조 | 핵심 변경 |
|---|---|---|
| **V1** | Interface → Decision → Execution → Equipment (4-layer) | 초기 개념 (GUI / Main Server / FMS / 실제 장비) |
| **V2** | Admin/Customer PC 분리, Control Server + AI Server + Cloud Server + HW/Arm/AMR Controller | PC와 컨트롤러 물리 분리 |
| **V3** | Interface Service 레이어 추가 | UI 바꿔도 backend 무영향 (decoupling) |
| **V4** | Interface Service ↔ DB Server 단방향 연결 (read-only) | 단순 조회는 DB direct read, 해석 필요 조회만 Control Service 경유. **Factory PC(PyQt5)** vs **Admin/Customer PC(Next.js/React)** 분리 |

#### V4 최종 아키텍처 규칙
- **Interface Service → DB read-only direct**: 단순 조회 (주문 목록, 적재 이력, 알람 이력)
- **Interface Service → Control Service**: 해석 필요 (이송 가능 여부, 공정 승인, 라우팅, 작업 추천)
- **Factory PC**: PyQt5 기반 관제 모니터링
- **Admin PC / Customer PC**: 웹 (Next.js + React)
- **GUI는 DB 직접 저장 금지**: Control Server 경유 (UI/DB 디커플링)

#### 4-Layer 책임 분리 (V1 모델, 여전히 유효)
- **Interface Layer (GUI)**: 입력창 + 모니터링 화면. 검사 요청, 발주, 컨베이어 제어, 로봇 상태, 모니터링
- **Control Layer (Main Server)**: 검증 → 비즈니스 로직 → DB 저장 → AI 호출 → FMS 명령 생성. "중앙 두뇌"
- **Execution Layer (FMS)**: 로봇 작업 분배, 충돌 방지, 경로 계획, 상태 수집
- **Equipment Layer**: Conveyor, Laser (TOF), Camera, Robot Arm, AMR

#### 코드베이스 교차검증
- ✅ V4 분리 구조와 일치: `backend/` (Control), `src/` (Next.js Admin/Customer), `monitoring/` (PyQt5 Factory PC), 향후 FMS는 `casting_factory_fleet` 별도 레포 계획
- ✅ Interface Layer 개념 ↔ `backend/app/routes/` 구조 (REST API)
- ⚠️ **Open-RMF 미사용**: Confluence는 FMS 개념만 언급, 실제 구현은 자체 스케줄러 (`backend/app/routes/schedule.py`)

---

### 1.2 Detailed Design (6651919)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6651919
**최종 수정**: v10 (2026-03-30)

#### Confluence 원문 팩트

**HW SPEC**:
- RaspberryPi 4
- RaspberryPi 5
- ESP32
- Jetson Orin NX (16GB)
- Conveyor Belt
- Web Camera
- **JetCobot280** ← 오타/오기, 실제는 MyCobot280
- Pinkypro

**SW Stack**:
- **Frontend**: React / Next.js
- **Backend**: FastAPI
- **DB**: PostgreSQL
- **Develop Env**: Ubuntu / VSCode / Jupyter
- **Language**: Python, C++
- **Model**: YOLO, PatchCore
- **Robotics**: ROS2 / Nav2
- **Communication**: Mosquitto (MQTT)
- **기타**: PyQt5, NumPy, OpenCV
- **협업**: Confluence, Jira, Slack, GitHub

#### 코드베이스 교차검증
- ✅ HW 대부분 일치 (RPi 4/5, ESP32, Jetson Orin NX, Pinkypro)
- ❌ **JetCobot280 → MyCobot280**: `blender/MyCobot280.step/stl`, `.moai/project/structure.md` 모두 MyCobot280 명시
- ✅ SW Stack 일치: Next.js(16.2.1) + React(19.2.4) + FastAPI + PostgreSQL 16 + TimescaleDB + YOLO + PatchCore + ROS2 Jazzy + Nav2 + Mosquitto MQTT + PyQt5
- ⚠️ Confluence는 버전 명시 없음 → 코드베이스 버전(Next.js 16.2.1 등)을 정답으로 취급

---

### 1.3 v_model (3506182)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3506182

#### Confluence 원문 팩트
- **[애자일 방법론](https://www.atlassian.com/ko/agile)** 링크만 존재
- 본문 없음 (사실상 placeholder)

---

### 1.4 User_Requirements (3375120)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3375120
**최종 수정**: v25 (2026-03-26)

#### Confluence 원문 팩트 — UR 테이블 (공정 flow 기준)

| 공정 단계 | UR_NAME | Required | Entity/Tracking |
|---|---|---|---|
| **주문/생산 계획** | 고객 주문 및 생산 오더 생성 (UR_01) | **R** | Order ID, Quantity, Product/Customer Info, BOM |
| **원자재 처리** | 원자재 투입 관리 | O | Material, 고체/액체, Weight/Temperature |
|  | 도가니 용광로 투입 | O | Furnace, Idle/Heating/Ready |
| **주형 및 주조** | 주형 생성 | **R** | Mold ID, Ready/In-progress/Completed, Image |
|  | 용탕 주입 | **R** | Ladle, Mold, Pouring, Temperature, Flow Rate, Job ID |
| **냉각 및 탈형** | 주물 냉각 상태 모니터링 | **R** | Casting, Cooling/Completed, Temperature, Time |
|  | 주물 탈형 | **R** | Robot Arm, Task ID |
| **이송/물류** | 주물 팔레트 적재 | O | Pallet, Quantity, Pallet ID |
|  | 팔레트 구역 간 이송 | **R** | AMR, Pallet ID |
| **후처리** | ~~후처리 공정 수행~~ (삭제됨) | ~~O~~ | - |
|  | 후처리 구역 청소 | O | AMR, Active/Inactive |
|  | 후처리 → 검사 이송 | **R** | Robot Arm, AMR, Task ID |
| **검사** | 주물 품질 검사 | **R** | Camera, Image, Image ID |
| **분류/출하** | 불량품 적재 | O | Robot Arm, Order Info |
|  | 불량품 폐기 이송 | **R** | AMR, Task ID |
|  | 양품 팔레트 적재 | **R** | Robot Arm, Order Info |
|  | 양품 팔레트 이송 | **R** | AMR, Task ID |
|  | 양품 트레이 적재 | **R** | Tray, Quantity |

#### 기타 규칙
- **자동화 Level 4 목표**로 R(Required) / O(Optional) 선정
- **불량품 재활용 금지** (산업 관례상)
- **FMS 도입 시 Job ID를 자동화 시스템 전반에 tracking**

---

### 1.5 System_Requirements_v3 (6258774)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6258774
**최종 수정**: v28 (2026-03-30, 여러 차례 업데이트)

#### SR ID 체계 (9개 카테고리)

| Prefix | 의미 |
|---|---|
| `SR-ORD` | 주문 (Order) |
| `SR-CTL` | 관제 (Control) |
| `SR-CAST` | 주조 (Casting) |
| `SR-TR` | 이송 (Transport) |
| `SR-INS` | 검사 (Inspection) |
| `SR-CONV` | 컨베이어 (Conveyor) |
| `SR-STO` | 적재 (Storage) |
| `SR-OUT` | 출고 (Outbound) |
| `SR-CLN` | 청소 (Cleaning) |

POST는 후처리(별도 섹션으로 관리, 일부는 SR-POST로 표기)

#### SR ID 목록 (실제 파싱 결과, 구조적 ID 기준)

**SR-ORD (주문)**:
- SR-ORD-01 원격 발주 기능 (상위)
- SR-ORD-01-01 표준 제품 조회
- SR-ORD-01-02 제품 옵션 선택
- SR-ORD-01-03 도면/디자인 정보 확인
- SR-ORD-01-04 주문 가능 여부 검증
- SR-ORD-01-05 예상 견적 및 납기 안내
- SR-ORD-01-06 원격 주문서 제출
- SR-ORD-02 주문 상태 조회
- SR-ORD-03 관리자 주문 검토 및 승인

**SR-CTL (관제)**:
- SR-CTL-01 공정 Map 기반 실시간 모니터링
- SR-CTL-02 공정 제어
- SR-CTL-03 이상 감지 및 알림
- SR-CTL-04 생산 개시
- SR-CTL-05 우선순위 계산
- (기타) 병목 해결, 생산 종료 — ID 미부여

**SR-CAST (주조)**:
- SR-CAST-01 재료 공급 관리 및 용해 (상위)
- SR-CAST-01-01 원재료 준비 및 투입
- SR-CAST-01-02 원재료 융용
- SR-CAST-02 조형 및 주탕 제어 (상위)
- SR-CAST-02-01 조형
- SR-CAST-02-02 주탕
- SR-CAST-03 냉각 및 탈형 공정 (상위)
- SR-CAST-03-01 주물 냉각 완료 탐지
- SR-CAST-03-02 탈형

**SR-TR (이송)**:
- SR-TR-01 이송 요청 관리 (상위)
- SR-TR-01-01 이송 요청 생성
- SR-TR-01-02 이송 요청 상태 관리
- SR-TR-02 이송 자원 운영 관리 (상위)
- SR-TR-02-01 이송 자원 상태 관리
- SR-TR-02-02 이송 자원 배정
- SR-TR-02-03 이송 자원 충전 및 복귀
- SR-TR-02-04 출발 조건 확인
- SR-TR-03 이송 수행 (상위)
- SR-TR-03-01 물품 인계·인수 확인
- SR-TR-03-02 이동 기능
- SR-TR-04 이송 수행 중 예외 처리

**SR-INS (검사)**:
- SR-INS-01 주물 품질 검사 및 결과 관리 (상위)
- SR-INS-01-01 주물 품질 검증
- SR-INS-01-02 검증 결과 관리
- SR-INS-02 주물 분류 실행
- SR-INS-03 분류 장치 제어

**SR-CONV (컨베이어)**:
- SR-CONV-01 컨베이어 운전 제어 (상위)
- SR-CONV-01-01 컨베이어 구동 및 정지
- SR-CONV-01-02 이송 속도 제어
- SR-CONV-01-03 운전 모드 전환
- SR-CONV-02 검사 구간 제어 (상위)
- SR-CONV-02-01 검사구간 도착 감지 및 정지
- SR-CONV-02-02 검사 시스템 연동
- SR-CONV-02-03 비상정지 및 예외 정지

**SR-STO (적재)**:
- SR-STO-01 적재 전략 및 위치 최적화 (상위)
- SR-STO-01-01 최적 위치 할당
- SR-STO-01-02 제품 재배치
- SR-STO-02 적재 실행 및 예외 관리 (상위)
- SR-STO-02-01 제품 적재
- SR-STO-02-02 적재 예외 처리
- SR-STO-03 실시간 적재 지도 모니터링 제어

**SR-OUT (출고)**:
- SR-OUT-01 출고 관리 (상위)
- SR-OUT-01-01 출고 지시서 생성
- SR-OUT-01-02 출고 수행
- SR-OUT-02 출고 이력 관리

**SR-POST (후처리)**:
- SR-POST-01 후처리 공정 운영 및 흐름 제어 (상위)
- SR-POST-01-01 후처리 작업 (수작업 기반)
- SR-POST-01-02 청소 요청

**SR-CLN (청소)**:
- SR-CLN-01 청소 스케줄링 및 실행 (상위)
- SR-CLN-01-01 구역별 맞춤 청소 관리

**구조적 SR ID 카운트**: 약 **60~70개**
(이전 문서들이 언급한 "85개"는 SR-CTL-06~16 등 문서 내부의 중복/초기 버전을 포함한 수치로 추정)

#### 주요 비기능 요구사항 (NFR) 수치
| 항목 | 값 |
|---|---|
| 공정 Map 데이터 갱신 주기 | **1초 이내** |
| 제어 명령 반영 시간 | **1초 이내** |
| 이상 감지 시간 | **1초 이내** |
| AMR 위치 오차 | **±5 cm 이내** |
| AMR 자세 오차 | **±5° 이내** |
| AMR 직진 속도 제한 | **≤ 1.0 m/s** |
| AMR 회전 속도 제한 | **≤ 0.5 m/s** |
| 품질 검증 정확도 | **≥ 95%** |
| 검증 결과 반환 시간 | **1초 이내** |
| 분류 정확도 | **≥ 99%** |
| 컨베이어 이송 속도 범위 | **1~100%** |
| 컨베이어 구동/정지 반응 | **1초 이내** |
| 검사 구간 정지 | 도착 후 **0.5초 이내** |
| 검사 구간 정지 위치 오차 | **±5 cm 이내** |
| 주형 정밀도 | **≥ 90%** |
| 창고 공간 활용률 목표 | **≥ 90%** |
| 청소 완료율 목표 | **≥ 70%** |
| 주문 절차 최대 단계 | **≤ 5단계** |

#### 주문 상태 6단계 (SR-ORD-02)
접수 → 검토 중 → 승인됨 → 생산 중 → 출하 준비 → 완료

#### 이송 상태 전이
배정 전 → 출발 위치로 이동 → 출발 위치 도착 → 인수 중 → 인수 완료 → 도착 위치로 이동 → 도착 위치 도착 → 인계 중 → 인계 완료 → 실패

#### 이송 자원 상태 4단계 (SR-TR-02-01)
- **유휴** (충전 중 + 대기)
- **작업 중**
- **충전 필요** (배터리 30% 이하)
- **사용 불가**

#### 코드베이스 교차검증
- ✅ SR-CTL-04 생산 개시 + SR-CTL-05 우선순위 계산 → `backend/app/routes/schedule.py` (SPEC-CTL-001) 구현 완료
- ✅ 이송 자원 4단계 상태 → 코드 SR-CTL-01 매핑 구현 (`e95724a` 커밋)
- ✅ SR-ORD-01-06 주문 절차 최대 5단계 → `src/app/customer/` 5-step form 구현
- ✅ 주문 상태 6단계 → DB `customer_order.order_status` enum과 일치
- ⚠️ SR-POST (후처리): "수작업 기반" 명시 → 로봇암 후처리는 UR에서도 삭제됨 (취소선 처리). 실제 로봇암 후처리 구현 불필요

---

### 1.6 Layout (4915220)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/4915220

#### Confluence 원문 팩트
- **빈 페이지** (본문 없음)

---

### 1.7 MVP_Prioritization (3375144)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3375144

#### Confluence 원문 팩트

**Priority 1 (Critical Automation)**:
- **주탕**: 도가니에서 양초 중탕 방식 용융 → 주형 주입 (demo: 양초 사용)
- **물류 이동** (3가지 시나리오):
  1. 원재료 → 도가니 이송
  2. 완성품 중 **양품** → 수거함 이송
  3. 완성품 중 **불량품** → 수거함 이송
- **단순 반복 작업**: 브러쉬로 코어 이물질 제거 (로봇암 전담 or 별도 장치)

**Priority 2 (AI-assisted Automation)**:
- **검사**: 컨베이어 위 이물질 제거된 코어 → 양품/불량품 판별
- **공장 최적화**

**Priority 3 (Human-in-the-loop)**:
- 예외 처리
- 공정 설계
- 품질 최종 판단

#### 코드베이스 교차검증
- ✅ 검사 공정(P2) → Vision AI (YOLO + PatchCore) 기반 구현 중
- ⚠️ 주탕(P1)에서 "양초" 사용은 **MVP 데모 전용**. 실제 금속 용탕은 시연 불가

---

### 1.8 Scenarios (15729093)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15729093

#### Confluence 원문 팩트
- **빈 페이지** (본문 없음, 2026-04-06 생성)

---

## 2. 02_Domain_Research

Root page: **3342354** (`02_Domain_Research`)

### 2.1 intro (3211297)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3211297

#### Confluence 원문 팩트
- **빈 페이지** (zero-width space만 있음)

---

### 2.2 Casting (3375162)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3375162

#### Confluence 원문 팩트

**제품**: 맨홀 뚜껑 (Manhole Cover)

**제품 특성**:
- **무게**: 20 ~ 80kg
- **형상**: 단순 (원형, 네모)
- **디자인**: 다양
- **표면**: 후처리 필요 (버 제거, 그라인딩)
- **취급**: 충격 강, 긁힘/찍힘 발생 가능
- **생산**: 동일 디자인 **소량 반복** (다품종 소량)

**가정**:
- 저장용기(파레트) → 실제 시연에서는 **AMR**로 대체
- 가정 제품: 맨홀

**참고 기업**: [기남금속](http://www.kinam.co.kr/)

#### 최적화 목표
냉각 완료된 주물을 후처리 및 검사 공정으로 이송할 때:
- 총 **리드타임 최소화**
- 후처리 구역 **병목** 및 재공품 증가 방지
- **안정적인 공정 흐름** 유지

#### 실측 대상
1. **제품 쪽**: 도착 간격, 대기 수량
2. **운반 쪽**: 개별/소배치/팔레트 이송 시간
3. **후처리 쪽**: 1개당 평균 시간, 대기열 길이

#### 의사결정 규칙
- **규칙 A (대기시간 제한)**: `if waiting_time >= Tmax then move`
- **규칙 B (병목 제한)**: `if waiting_cnt >= Qmax then stop_transferring`
- **규칙 C (배치 크기 기준)**: 대기 수량 일정 이상이면 묶어서 전송

---

### 2.3 Logistics (3637320)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3637320

#### Confluence 원문 팩트
- **VDA 5050**: AGV ↔ 중앙 제어 시스템 간 **표준 통신 인터페이스**
- (본문 나머지는 이미지 + 링크)

#### 참고
VDA 5050는 독일 자동차 산업 연합(VDA)이 정의한 Fleet Management Interface 표준. Open-RMF와 유사하게 AGV/AMR과 중앙 관제의 공용 메시지 포맷을 정의. 우리 프로젝트는 VDA 5050 미채택 (자체 REST/ROS2 통신).

---

### 2.4 Terminology (3407906)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407906

#### Confluence 원문 팩트 — 주조 (Casting) 용어

**정의**: "주조 공정은 용탕을 주형에 주탕한 뒤 냉각·탈형을 거쳐 제품을 만드는 과정이며, 특히 주탕과 물류 과정은 자동화가 가장 필요한 핵심 구간"

| 용어 | 영문 | 정의 |
|---|---|---|
| 주조 | Casting | 금속을 녹여 주형에 부어 형상을 만드는 공정 |
| 용탕 | Molten Metal | 녹은 금속 상태 |
| 조형 | Molding | 틀을 만드는 행위 (Process) |
| 주형 | Mold | 쇳물을 붓는 '형'. 모래/금속/석고/세라믹 등 |
| 금형 | Die/Metal Mold | 금속을 깎아 제작한 영구 틀 |
| 사형 | Sand Mold | 모래로 만든 1회성 틀 (탈형 시 파괴) |
| 주형사 | Molding Sand | 실리카 모래 + 결합제(벤토나이트) + 수분 + 첨가제 |
| 주물 | Casting Product | 최종 결과물 |
| 용해 | Melting | 금속 고온 용해 과정 |
| 주괴 | Ingot | 용해로 투입용 금속 |
| 용해로 | Melting Furnace | 금속 용해 설비 |
| 합금 | Alloy | 2종 이상 금속/금속+비금속 혼합 |
| 슬래그 | Slag | 용해 중 발생 불순물 (표면 부상) |
| 패턴 | Pattern | 주형 제작용 원형 모델 |
| 코어 | Core | 주물 내부 빈 공간 형성 구조물 |
| 사형 주조 | Sand Casting | 모래 주형 방식 |
| 금형 주조 | Die Casting | 금속 금형 고정밀 방식 |
| 주탕 | Pouring | 용탕을 주형에 붓는 과정 |
| 도가니 | Crucible | 용해로 내부 금속 용기 (고정) |
| 래들 | Ladle | 용탕 이동/주입용 이동식 용기 |
| 탕구 | Sprue | 용탕 첫 수직 통로 |
| 러너 | Runner | 용탕 분배 수평 통로 |
| 게이트 | Gate | 제품 형상으로 들어가는 입구 |
| 압탕 | Riser | 응고 수축 보정용 용탕 저장부 |
| 냉각/응고 | Cooling/Solidification | 용탕 → 고체 변환 |
| 탈형 | Shakeout | 주형에서 주물 제거 |
| 후처리 | Finishing | 표면 다듬기 |
| 페틀링 | Fettling | 주물 표면 정리 |
| 디버링 | Deburring | 날카로운 모서리 제거 |
| 샷 블라스트 | Shot Blasting | 표면 청소/마감 |

**검사**:
- 외관 검사 (Visual Inspection): 눈으로 결함 확인
- 비파괴 검사 (NDT, Non-Destructive Testing): X-ray, 초음파

**결함 (Defect)**:
- **기공** (Porosity): 내부 기포/구멍
- **수축 결함** (Shrinkage): 응고 부피 감소
- **콜드 셧** (Cold Shut): 두 용탕 흐름 융합 실패로 선 모양 이음새
- **미스런** (Misrun): 용탕이 주형을 끝까지 못 채움

**설비 및 자동화**:
- **로봇 셀**: 로봇 중심 작업 단위 시스템
- **AMR**: 자율주행 물류 로봇
- **비전 시스템**: 카메라 기반 인식/검사
- **공정 모니터링**: 센서 실시간 상태 확인
- **택트 타임**: 제품 1개당 필요 시간

#### 물류 (Logistics) 용어

**정의**: "물류는 원자재, 반제품, 완제품을 공급망 전반에서 이동·보관·관리하는 과정"

| 용어 | 영문 | 정의 |
|---|---|---|
| 물류 | Logistics | 제품/자원 흐름 관리 |
| 공급망 | Supply Chain | 원자재 → 생산 → 유통 → 고객 전체 흐름 |
| 물류 자동화 | Logistics Automation | 인력 대신 시스템/로봇/SW로 수행 |
| 물류 최적화 | Logistics Optimization | AI/자동화/데이터 분석으로 비용 최소화 |
| 슬로팅 | Slotting | 창고 내 상품 배치 최적화 |
| 입고 | Receiving/Inbound | 외부 → 창고 |
| 출고 | Shipping/Outbound | 창고 → 고객/다음 공정 |
| 이송 | Transport/Transfer | 물류 거점/공정 간 이동 |
| 적치 | Storage/Put-away | 지정 위치 보관 |
| 피킹 | Picking | 주문 맞춤 선택/수집 |
| 패킹 | Packing | 출하 포장 |
| 검수 | Checking | 입고/출고 검증 |
| 반품 | Return | 고객/공정에서 돌아옴 |
| 재고 | Inventory/Stock | 현재 보유 수량 |
| 재고 동기화 | Inventory Synchronization | 물리 재고 ↔ WMS 일치 |
| Cross Docking | - | 입고 → 보관 없이 바로 출고 |
| **WMS** | Warehouse Management System | 창고 재고/작업 관리 시스템 |
| **FMS** | Fleet Management System | 다수 로봇/AGV/AMR 할당·경로 제어 |
| **AMR** | Autonomous Mobile Robot | 자율 경로 판단 물류 로봇 |
| **AGV** | Automated Guided Vehicle | 정해진 경로 자동 운반 |
| 컨베이어 | Conveyor | 일정 경로 연속 이동 설비 |
| Scan Lane | - | 바코드/RFID 실시간 인식 구간 |
| Golden Zone | - | 작업 효율 최고 적치 위치 (허리~가슴) |

---

## 3. 03_Technical_Research

Root page: **6488246** (`03_Technical_Research`)

### 3.1 HW_Research (8552537)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8552537
- **빈 페이지** (2026-03-31 생성, 내용 없음)

---

### 3.2 SW_Research (8552545)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8552545
- **빈 페이지** (2026-03-31 생성, 내용 없음)

---

### 3.3 DB_Research (8585277)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8585277
- 다른 페이지로의 링크만 존재 (page 7471353 참조)
- **실질 내용 없음**

---

### 3.4 SW_Control (15433852)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15433852

#### Confluence 원문 팩트
- 단일 링크: **https://github.com/addinedu-ros-4th/ros-repo-2**
- 다른 팀/과거 ROS 레포 참조 (본 프로젝트와 직접 관련 낮음)

---

## 4. 04_Implementation

Root page: **3703084** (`04_Implementation`)

### 4.1 VLA (3276898)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3276898
- **빈 페이지**

---

### 4.2 LLM (3703098)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3703098
- **빈 페이지**

---

### 4.3 Prototypes (3407954)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407954
- **빈 페이지** (zero-width space만)

---

### 4.4 DB (5898574)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5898574
**최종 수정**: v10 (2026-03-29)
**도구**: [dbdiagram.io](https://dbdiagram.io/home) (ERD 작성)

#### Confluence 원문 팩트 — DB 스키마 (16개 테이블)

##### 공통/기준 정보
1. **company** — 고객사 정보
   - `company_id (PK, SERIAL)`, `company_name (NN)`, `manager_name`, `manager_phone`, `manager_email`

2. **user_account** — 사용자 정보
   - `user_id (PK)`, `company_id (FK)`, `user_name (NN)`, `role` (`customer` | `admin` | `operator`), `phone`, `email (Unique)`, `password_hash`

3. **product** — 표준 제품
   - `product_id (PK)`, `category_id`, `category_name (Unique)`, `product_name (NN)`, `material_type`, `base_price DECIMAL(12,2)`, `image_url`, `created_at`

4. **product_option** — 제품 옵션
   - `option_id (PK)`, `product_id (FK)`, `option_type` (`diameter` | `thickness` | `material` | `postprocess` | `logo`), `option_name`, `option_value`, `extra_price DECIMAL(12,2)`, `is_active`

##### 발주/주문
5. **customer_order** — 주문서 헤더
   - `order_id (PK, VARCHAR)`, `company_id (FK)`, `user_id (FK)`, `order_status` (`received` | `reviewing` | `approved` | `in_production` | `ready_to_ship` | `completed` | `rejected`), `total_estimated_price`, `total_confirmed_price`, `requested_due_date`, `confirmed_due_date`, `shipping_address`, `memo`, `created_at`

##### 생산 관리
6. **work_order** — 생산 작업지시
   - `work_order_id (PK)`, `order_item_id (FK)`, `priority_score`, `work_status` (`waiting` | `processing` | `completed` | `failed`), `planned_start_at`, `actual_start_at`, `actual_end_at`

7. **production_process_log** — 공정 이력
   - `process_log_id (PK)`, `work_order_id (FK)`, `process_status` (`running` | `completed` | `failed`), `process_type` (`material_input` | `melting` | `molding` | `pouring` | `cooling` | `demolding`), `equipment_id (FK)`, `started_at`, `ended_at`, `result_note`

##### 관제/설비
8. **equipment** — 설비
   - `equipment_id (PK)`, `equipment_name`, `equipment_type` (`furnace` | `molding_machine` | `pouring_robot` | `conveyor` | `inspection_device` | `sorter`), `zone_id (FK)`, `status` (`idle` | `running` | `stopped` | `error` | `maintenance`), `installed_at`

9. **equipment_status_history** — 설비 상태 이력
   - `equipment_status_history_id (PK)`, `equipment_id (FK)`, `previous_status`, `new_status`, `changed_at`, `reason`

10. **transport_resource** — 이송 자원 (AMR)
    - `resource_id (PK)`, `resource_name`, `status` (`idle` | `working` | `charging` | `unavailable`), `battery_level INT (%)`, `current_zone_id (FK)`, `updated_at`

11. **notification** — 알림
    - `notification_id (PK)`, `user_id (FK)`, `notification_type` (`order` | `transport` | `equipment` | `inspection` | `shipment`), `title`, `message`, `is_read BOOLEAN`, `created_at`

##### 공정 간 이송
12. **transport_request** — 이송 요청
    - `transport_request_id (PK)`, `task_code (Unique)`, `request_type` (`internal_move` | `shipment_move` | `postprocess_move`), `source_zone_id (FK)`, `destination_zone_id (FK)`, `product_id (FK)`, `quantity`, `priority`, `status` (`pending` | `assigned` | `moving_to_source` | `loading` | `moving_to_destination` | `unloading` | `completed` | `failed`), `requested_at`

13. **transport_task** — 이송 수행
    - `transport_task_id (PK)`, `transport_request_id (FK)`, `resource_id (FK)`, `task_status` (`assigned` | `in_progress` | `completed` | `failed`), `started_at`, `ended_at`, `failure_reason`

##### 품질 검사
14. **inspection_result** — 품질 검사 결과
    - `inspection_result_id (PK)`, `work_order_id (FK)`, `product_id (FK)`, `result` (`pass` | `fail`), `passed_quantity`, `failed_quantity`, `inspected_at`

##### 적재/창고
15. **storage_zone** — 적재 구역
    - `zone_id (PK)`, `zone_name`, `product_type`, `capacity INT`

16. **storage_location** — 적재 위치
    - `location_id (PK)`, `zone_id (FK)`, `product_id (FK)`, `shelf`, `column_no`, `status` (`empty` | `occupied` | `reserved`), `stored_at`

##### 출고
17. **shipment_order** — 출고 지시서
    - `shipment_order_id (PK)`, `order_id (FK)`, `quantity`, `shipment_date`, `shipment_status` (`created` | `completed`), `created_at`

**총 17개 테이블** (Confluence 원문 명시. 상위 주석의 "16개"는 약간의 누락)

#### 코드베이스 교차검증
- ✅ 대부분 테이블 구조 일치
- ✅ order_status 6단계 ↔ Confluence 7단계 (`rejected` 추가)
- ✅ `transport_resource.status` 4단계 ↔ 코드 `e95724a` 구현
- ⚠️ Confluence는 "15개 + production_jobs/priority_change_logs (신규)" 라고 했지만 실제 리스트는 17개
- ⚠️ `production_jobs`, `priority_change_logs` 2개는 SPEC-CTL-001 (commit `0952f86`)에서 `backend/app/models/models.py`에 추가됨

---

### 4.5 GUI (6389916)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6389916
**최종 수정**: v25 (2026-03-30)

#### Confluence 원문 팩트 — 페이지 구성 (8개 라우트)

| # | 라우트 | 페이지명 | 레이아웃 |
|---|---|---|---|
| 1 | `/` | 대시보드 | 관리자 (사이드바) |
| 2 | `/production` | 생산 모니터링 | 관리자 |
| 3 | `/production/schedule` | 생산 계획 | 관리자 |
| 4 | `/orders` | 주문 관리 | 관리자 |
| 5 | `/quality` | 품질 검사 | 관리자 |
| 6 | `/logistics` | 물류/이송 | 관리자 |
| 7 | `/customer` | 고객 발주 (5단계 폼) | 독립 |
| 8 | `/customer/orders` | 고객 주문 조회 | 독립 |

#### 사이드바 메뉴
대시보드 / 생산 모니터링 / 생산 계획 / 주문 관리 / 품질 검사 / 물류/이송

#### 대시보드 KPI 4개
1. 생산 목표 달성률 (게이지) — 예: 47%
2. 실시간 가동 로봇 (로봇 아이콘) — 예: 1대
3. 미처리 주문 (카트) — 예: 2건
4. 금일 발생 알람 (종) — 예: 2건

#### 대시보드 3D 공장 맵 탭 4개
- 3D 공장 / 인터렉티브 맵 / 공정 레이아웃 / 3D 실시간

#### 공정 흐름 5단계
원재료 투입/용해 → 조형 → 주탕 → 냉각/탈형 → 후처리/검사

#### 실시간 수치 데이터 (생산 모니터링)
| 항목 | 상세 |
|---|---|
| 용해로 온도 | 라인 차트, 현재 **1420°C**, 목표 **1450°C**, 가열 출력 **92%** |
| 조형/주탕 데이터 | 제품: 맨홀 뚜껑 **KS D-600** (`MLD-001`) |
| 성형 압력 | 85 bar |
| 주입 각도 | 45° |
| 주물 온도 | 1400°C |
| 냉각 진행률 | 80%, 목표 25°C |
| 시간별 생산량 | 불량 61개, 생산량 1412개 |

#### 설비 ID 예시 (로그 테이블)
- `FRN-001`: 용해로 #1
- `MLD-001`: 주체 제작 #1

#### AMR 플릿 (3대)
- AMR #1: 가동 중, 가동률 **78%**
- AMR #2: 유휴
- AMR #3: 충전 중, 배터리 **15%**

#### 창고 랙 (6×4 = 24 슬롯)
- 비어있음: 9개
- 점유: 12개
- 예약: 2개
- 사용불가: 1개

#### 검사 기준 (품질 검사 페이지)
- **KS D-600**: 외경 600mm / 두께 50mm / 허용 오차 **±0.5mm**
- **KS D-450**: 외경 450mm / 두께 40mm / 허용 오차 **±0.4mm**

#### TOP 3 불량 유형
1. 표면 균열 (25%)
2. 기포 불량 (25%)
3. 수축 결함 (16.7%)

#### 생산 계획 — 우선순위 계산 엔진 (7요소, 100점 만점)

| 요소 | 배점 | 산출 방식 |
|---|---|---|
| 납기일 긴급도 | **25점** | D-day (3일 이내=25, 7일=20, 14일=15, 30일=10) |
| 착수 가능 여부 | **20점** | 공정 idle + 용해로/조형기/AMR 가용성 |
| 주문 체류 시간 | **15점** | 승인 후 경과일 |
| 지연 위험도 | **15점** | 예상완료일 vs 납기일 마진 |
| 고객 중요도 | **10점** | 주문 금액 상위 20% 판별 |
| 수량 효율 | **10점** | 소량 우선 |
| 세팅 변경 비용 | **5점** | 직전 작업 제품 연속 시 보너스 |

#### 백엔드 API 전체 목록 (27개 + WebSocket)

| Method | Endpoint |
|---|---|
| GET | `/api/dashboard/stats` |
| GET/POST | `/api/orders` |
| PATCH | `/api/orders/{id}/status` |
| PATCH | `/api/orders/{id}` |
| GET/POST | `/api/orders/{id}/details` |
| GET | `/api/products` |
| GET/PATCH | `/api/production/stages`, `/api/production/stages/{id}` |
| GET | `/api/production/metrics` |
| GET | `/api/production/equipment` |
| POST | `/api/production/schedule/calculate` |
| POST | `/api/production/schedule/start` |
| GET | `/api/production/schedule/jobs` |
| POST/GET | `/api/production/schedule/priority-log`, `/api/production/schedule/priority-log/{id}` |
| GET | `/api/quality/inspections` |
| GET | `/api/quality/stats` |
| GET | `/api/quality/standards` |
| GET | `/api/quality/sorter-logs` |
| GET/POST | `/api/logistics/tasks` |
| PATCH | `/api/logistics/tasks/{id}/status` |
| GET | `/api/logistics/warehouse` |
| GET | `/api/logistics/outbound-orders` |
| PATCH | `/api/logistics/outbound-orders/{id}/complete` |
| GET | `/api/alerts` |
| WS | `ws://localhost:8000/ws/dashboard` (5초 주기) |

#### 주문 상태 전이
접수 → 검토 → 승인 → 생산 중 → 출하 준비 → 완료 (또는 반려)

#### Confluence 명시 기술 스택
- **GitHub**: [kiminbean/casting-factory](https://github.com/kiminbean/casting-factory)
- **Tech**: Next.js 16 + TypeScript + Tailwind CSS + FastAPI + **SQLite** + Three.js
- **종합 모니터링**: http://192.168.0.16:3000
- **고객 주문**: http://192.168.0.16:3000/customer

#### PyQt5 GUI (관제 대시보드)
- Factory PC용 별도 GUI

#### 코드베이스 교차검증
- ✅ **8개 라우트 완전 일치** (`src/app/` 구조)
- ✅ **27개 API 엔드포인트 완전 일치** (`backend/app/routes/`)
- ✅ `schedule.py` 7요소 계산 엔진 일치
- ✅ 설비 ID (FRN-001, MLD-001) 일치
- ❌ **SQLite → PostgreSQL 16 + TimescaleDB** (실제 코드베이스는 PostgreSQL로 마이그레이션 완료/진행 중)
- ❌ **Next.js 16 → Next.js 16.2.1 + React 19.2.4** (구체 버전 불일치)

---

### 4.6 SmartCast Robotics GitHub 폴더 구조 초안 (20217883)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20217883
**최종 수정**: v3 (2026-04-08)

#### Confluence 원문 팩트 — 폴더 구조

```
SmartCast_Robotics/
├── README.md
├── .gitignore
├── LICENSE
├── docs/
│   ├── overview/           # project_overview, system_architecture, team_roles
│   ├── requirements/       # system/functional/nonfunctional_requirements
│   ├── db/                 # erd.dbml, erd_relationships, schema_notes
│   ├── api/                # api_spec, message_flow
│   ├── uiux/               # screen_flow, wireframes
│   ├── hardware/           # equipment_list, sensor_actuator_map, network_topology
│   └── ops/                # deployment, monitoring, troubleshooting
├── backend/                # app, services, models, routes, schemas, utils, tests
├── frontend/               # src, public, components, pages, assets, tests
├── database/               # migrations, seeds, init
├── plc/                    # ladder, structured_text, tags, hmi
├── edge/                   # collectors, mqtt, opcua, modbus
├── ai/                     # notebooks, datasets, preprocessing, training, inference, models
├── simulation/             # process, logistics, layout
├── data/                   # raw, processed, external, sample
├── scripts/                # setup, import, export, maintenance
├── configs/                # dev, prod, local
├── infra/                  # docker, nginx, k8s, terraform
└── .github/                # workflows, ISSUE_TEMPLATE, PULL_REQUEST_TEMPLATE
```

#### 폴더별 역할 (Confluence 원문)
- `docs/` — 요구사항, 아키텍처, DB, API, 장비 문서
- `backend/` — 관제, 주문, 이송, 검사, 적재, 출고 로직
- `frontend/` — 관리자/현장/주문 화면
- `database/` — 스키마 초기화, 마이그레이션, 시드
- `plc/` — PLC 로직, 태그, HMI
- `edge/` — 센서/설비 데이터 수집, 프로토콜, 메시지 브로커
- `ai/` — 품질 검사, 이상 감지, 예측 모델
- `simulation/` — 공정/이송/레이아웃 시뮬레이션
- `data/` — 원천/전처리/외부 데이터
- `scripts/` — 환경 세팅, 유지보수
- `configs/` — dev/prod/local 환경 설정
- `infra/` — Docker, 배포, 인프라
- `.github/` — CI/CD, 템플릿

#### 코드베이스 교차검증
- ⚠️ **별도 레포 구상**: "SmartCast_Robotics" 이름은 별개 프로젝트/제안 (현재 레포는 `casting-factory`)
- ⚠️ 실제 우리 레포는 훨씬 단순한 구조 (monorepo: `backend/`, `src/`(Next.js), `monitoring/`, `blender/`, `firmware/`, `docs/`)
- ⚠️ PLC, OPC-UA, Modbus 등은 **미사용** (ESP32 + MQTT 기반)
- ⚠️ Kubernetes, Terraform 등은 **단일 PC 배포 수준이라 불필요**

---

## 통합 팩트 시트 (Quick Reference)

### Hardware Stack (확정)
| 카테고리 | 모델 | 용도 |
|---|---|---|
| SBC | **Raspberry Pi 4** | AMR 컨트롤러 (3대) |
| SBC | **Raspberry Pi 5** | Cobot 컨트롤러 / Vision edge |
| MCU | **ESP32** | 컨베이어 + TOF250 x2 + L298N 모터 |
| AI | **Jetson Orin NX 16GB** | YOLO / PatchCore 추론 서버 |
| 로봇팔 | **MyCobot280** (Elephant Robotics) | 주탕/탈형/후처리 2대 *(Confluence는 JetCobot280로 오기)* |
| AMR | **Pinkypro** | 3대 (0.12m × 0.12m, differential drive) |
| 컨베이어 | 자체 제작 | L298N + JGB37-555 모터 + TOF250 x2 ASCII UART 9600 |
| 비전 | Web Camera | USB, Jetson 연결 |

### Software Stack (확정, 2026-04 기준)
| 카테고리 | 기술 | 버전/세부 |
|---|---|---|
| Frontend | **Next.js** | 16.2.1 (App Router) |
| | **React** | 19.2.4 |
| | Tailwind CSS | ✓ |
| | TypeScript | ✓ |
| | Three.js, @react-three/fiber 9.5.0 | 3D 맵 |
| Backend | **FastAPI** | Python 3.11 |
| DB | **PostgreSQL 16** | + TimescaleDB (Phase 1 마이그레이션, SQLite 폐기) |
| Factory PC | **PyQt5** | 관제 모니터링 앱 (v1.0 빌드 완료) |
| OS | Ubuntu | VSCode, Jupyter |
| AI | YOLO, PatchCore | Vision 검사 |
| Robotics | **ROS 2 Jazzy**, Nav2 | 계획 (아직 미구축) |
| Comm | Mosquitto MQTT | ESP32 ↔ Backend |
| Vision Lib | NumPy, OpenCV | |
| 협업 | Confluence, Jira, Slack, GitHub | |

### 8단계 생산 공정 (확정)
1. 주문/생산 계획 (UR_01)
2. 원자재 처리 (용해로 투입)
3. 주형 및 주조 (조형 → 주탕)
4. 냉각 및 탈형
5. 이송 / 물류 (AMR)
6. 후처리 (수작업 기반, 청소 포함)
7. 검사 (Vision AI)
8. 분류 / 출하 (양품/불량 분류 + 적재)

### 8개 GUI 라우트 (확정)
1. `/` 대시보드
2. `/production` 생산 모니터링
3. `/production/schedule` 생산 계획
4. `/orders` 주문 관리
5. `/quality` 품질 검사
6. `/logistics` 물류/이송
7. `/customer` 고객 발주 (5단계 폼)
8. `/customer/orders` 고객 주문 조회

### 27개 REST API + WebSocket (확정)
(상세는 [4.5 GUI](#45-gui-6389916) 참조)

### SR 카테고리 (9개)
- SR-ORD (주문)
- SR-CTL (관제)
- SR-CAST (주조)
- SR-TR (이송)
- SR-INS (검사)
- SR-CONV (컨베이어)
- SR-STO (적재)
- SR-OUT (출고)
- SR-POST (후처리, 일부 문서는 별도)
- SR-CLN (청소)

**총 구조적 SR ID 수**: 약 **60~70개** (Confluence 내 중복 및 draft 제외)

### 주요 NFR 수치 (확정)
| 항목 | 값 |
|---|---|
| 공정 상태 갱신 주기 | ≤ 1초 |
| 제어 명령 반영 | ≤ 1초 |
| 이상 감지 | ≤ 1초 |
| AMR 위치 오차 | ±5cm |
| AMR 자세 오차 | ±5° |
| AMR 직진 속도 | ≤ 1.0 m/s |
| AMR 회전 속도 | ≤ 0.5 m/s |
| 품질 검증 정확도 | ≥ 95% |
| 분류 정확도 | ≥ 99% |
| 창고 공간 활용률 목표 | ≥ 90% |
| 주문 절차 | ≤ 5단계 |

### 생산 계획 — 7요소 우선순위 엔진 (확정)
총점 100점:
- 납기일 긴급도 25점
- 착수 가능 여부 20점
- 주문 체류 시간 15점
- 지연 위험도 15점
- 고객 중요도 10점
- 수량 효율 10점
- 세팅 변경 비용 5점

구현: `backend/app/routes/schedule.py` (SPEC-CTL-001, commit `0952f86`)

### Factory 제품 (확정)
- **맨홀 뚜껑** (manhole cover)
- 무게: 20 ~ 80 kg
- 형상: 원형 / 네모
- 규격 예: **KS D-600** (외경 600mm, 두께 50mm, ±0.5mm), **KS D-450** (외경 450mm, 두께 40mm, ±0.4mm)
- 생산 방식: 다품종 소량
- MVP 데모용 재료: **양초** (실제 금속 용탕 불가)
- 참고 기업: 기남금속

---

## 알려진 Confluence ↔ 코드 불일치

| 항목 | Confluence | 코드 (정답) | 출처 파일 |
|---|---|---|---|
| 로봇팔 모델 | JetCobot280 | **MyCobot280** (Elephant Robotics) | `blender/MyCobot280.step/stl`, `.moai/project/tech.md` |
| Frontend 버전 | "Next.js 16" (구체 버전 없음) | **Next.js 16.2.1 + React 19.2.4** | `.moai/project/tech.md`, `package.json` |
| DB | **SQLite** (GUI 페이지 하단 기재) | **PostgreSQL 16 + TimescaleDB** | `backend/app/database.py`, memory `feedback_postgres_decision.md` |
| Open-RMF | (암시만, 명시 없음) FMS 개념 | **자체 스케줄러 `backend/app/routes/schedule.py`** (Open-RMF 미사용) | SPEC-CTL-001, memory `project_fleet_traffic_design.md` |
| micro-ROS | (언급 없음) | **plain Arduino JSON** (1:1 ESP32↔RPi5 serial로 micro-ROS 불필요) | memory `feedback_microros_decision.md` |
| TOF 센서 프로토콜 | (세부 없음) | **ASCII UART 9600** (I2C 아님) | `firmware/conveyor_controller/`, memory `feedback_tof250_protocol.md` |
| SR ID 총 개수 | "85개" (초기 문서 언급) | **약 60~70개** (실제 파싱 결과) | 본 파일 §1.5 |
| 후처리 자동화 | (일부 SR에 로봇암 포함) | **수작업 기반** (UR 페이지에서 로봇암 후처리 삭제선) | UR page §1.4 |
| Layout/Scenarios/VLA/LLM/HW Research/SW Research | 페이지 존재 | **모두 빈 페이지** (placeholder) | 본 파일 §1.6~§4.3 |
| SmartCast_Robotics 레포 구조 | 별도 제안 (PLC/OPC-UA/K8s 포함) | **실제 레포는 `casting-factory`, 훨씬 단순** | 본 파일 §4.6 |

---

## 참조 정책

1. **이 파일은 프로젝트 작업 시 Confluence 대신 우선 참조**할 사실 모음
2. **원본 Confluence는 read-only**: 우리는 수정 권한 있는 특정 페이지만 업데이트 (예: 20774933 관제 기술조사). 대부분의 설계 페이지는 건드리지 않음
3. **코드베이스와 Confluence가 충돌 시 코드베이스가 정답**
4. **주기적 재검증 필요**: Confluence가 업데이트될 수 있으므로 월 1회 이상 `fetchAtlassian`으로 재수집
5. **재수집 순서** (권장):
   - 우선순위 높은 페이지: System_Requirements_v3 (6258774), GUI (6389916), DB (5898574), User_Requirements (3375120), System Architecture (3375131), Detailed Design (6651919)
   - 보통: Terminology (3407906), Casting (3375162), MVP_Prioritization (3375144)
   - 낮음: 나머지 (대부분 빈 페이지)
6. **장애 회피**: `getConfluencePage` 실패 시 `fetchAtlassian` + ARI 포맷 (`ari:cloud:confluence:{cloudId}:page/{pageId}`)으로 우회

### 페이지 ID 빠른 참조

```
01_Project_Design (root: 3145739):
  3375131  System Architecture           ← 핵심, v26
  6651919  Detailed Design                ← 핵심, v10 (HW/SW stack)
  3506182  v_model                        (거의 비어있음)
  3375120  User_Requirements              ← 핵심, v25 (UR table)
  6258774  System_Requirements_v3         ← 최중요, v28 (모든 SR ID)
  4915220  Layout                          (비어있음)
  3375144  MVP_Prioritization              (Priority 1~3 정의)
  15729093 Scenarios                       (비어있음)

02_Domain_Research (root: 3342354):
  3211297  intro                           (비어있음)
  3375162  Casting                         (맨홀뚜껑 스펙, 최적화 목표)
  3637320  Logistics                       (VDA 5050 언급만)
  3407906  Terminology                    ← 핵심 (주조/물류 용어)

03_Technical_Research (root: 6488246):
  8552537  HW_Research                     (비어있음)
  8552545  SW_Research                     (비어있음)
  8585277  DB_Research                     (링크만)
  15433852 SW_Control                      (다른 팀 GitHub 링크만)

04_Implementation (root: 3703084):
  3276898  VLA                              (비어있음)
  3703098  LLM                              (비어있음)
  3407954  Prototypes                       (비어있음)
  5898574  DB                              ← 핵심, v10 (16~17개 테이블 스키마)
  6389916  GUI                             ← 핵심, v25 (8 routes, 27 API, KPI 전체)
  20217883 SmartCast Robotics GitHub 구조   (v3, 별도 제안)
```

---

*Generated 2026-04-08 by casting-factory project. Source: Confluence space addinedute, homepage 753829. Read-only policy enforced.*
