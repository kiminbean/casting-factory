# Confluence Fact Reference — casting-factory

> **addinedute(addinedu_team_2)** space 주요 설계/기술 문서의 팩트 체크 정리본
> 원본 페이지 변경 시 이 파일을 업데이트해야 함
> **마지막 업데이트**: 2026-04-19 (cron sync: 43건)
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

### System Architecture (3375131)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3375131
**최종 수정**: v44 (2026-04-16 sync)

# SA 설계 방법 
System architecture (기능 명세서)에서 정의한 스펙 구현을 위해 HW/SW system level 설계해야한다. 
<SA 작업 전 선행 조건>

- 
GUI 설계 → 동작 시나리오 구성  

- 
Interface layer 설계: 컴포넌트 간 인터페이스를 계층적으로 정리한 구조

  - 
들어가야하는 정보  

    - 
누가 누구와 통신하는지 

    - 
데이터 구조

    - 
타이밍: 언제 보내고 응답하는지 

# SA 설계 예시 

## HW 예시 

### Interface (GUI)
관리자나 일반 사용자가 시스템에 요청을 보내거나 현재 상태를 확인하는 화면이다.
예를 들어 GUI에서는 다음과 같은 작업을 할 수 있다.

- 
검사 시작 요청

- 
제품 발주 요청

- 
conveyor belt 작동 / 정지 요청

- 
로봇 상태 확인

- 
현재 공정 상태 모니터링
즉, GUI는 **입력창이자 모니터링 화면**이다.

#### 왜 GUI가 DB에 직접 저장하지 않는가.
GUI가 DB에 바로 저장하면 DB 구조가 바뀔 때 UI도 함께 수정되어야 한다.
반면, Main Server를 중간에 두면 GUI는 단순히 요청만 보내면 되고, 실제 저장 형식은 Main Server가 처리하므로 **UI와 DB를 분리**할 수 있다.
예시 요청: <GUI → Main Server>
<간단한 frontend 예시>

### Main Server  (Decision Layer)
Main Server는 시스템의 **중앙 관리자** 역할을 한다.
단순히 데이터를 저장하는 서버가 아니라, 요청을 받아서 **판단하고 연결하는 계층**이다.
주요 역할은 다음과 같다.

- 
UI 요청 받기

- 
입력 검증 / 권한 검증

- 
DB 저장

- 
AI 서비스 호출

- 
FMS에 작업 전달

- 
결과를 다시 UI로 전달

- 
전체 상태를 통합 관리
<추천 폴더 구조>
<Main server → FMS 명령 예시> 

### FMS (Execution Layer)
FMS는 **실행 매니저** 역할을 한다.
Main Server가 “무엇을 할지” 결정했다면, FMS는 그것을 실제 로봇이 수행할 수 있는 방식으로 바꿔서 실행한다.
주요 역할은 다음과 같다.

- 
로봇에게 작업 분배

- 
작업 순서 관리

- 
여러 장비 간 충돌 방지

- 
AMR / Robot Arm 제어

- 
경로 계획 및 실행

- 
장비 상태 수집
즉, Main Server가 “pick and place 하라”고 하면, FMS는
“어느 로봇이 할지, 어느 경로로 갈지, 지금 가능한지”를 판단한다.

### AI Server 
AI Server는 카메라나 센서에서 들어온 데이터를 분석하는 역할을 한다.
예를 들어:

- 
제품 검출

- 
segmentation

- 
defect detection

- 
객체 위치 추정

- 
정상 / 불량 판별
즉, Main Server가 “이 제품 상태를 분석해줘”라고 요청하면,
AI Server가 분석 결과를 반환한다.
<Main Server → AI Server>
<AI Server → Main Server> 

### DB Cloud  
DB는 시스템의 상태와 이력을 저장하는 저장소 역할을 한다.
예를 들어 저장하는 정보는 다음과 같다.

- 
작업 요청 정보

- 
제품 정보

- 
생산 조건

- 
장비 상태 로그

- 
AI 분석 결과

- 
작업 완료 / 실패 이력
즉, DB는 판단을 하는 곳이 아니라 **기록과 조회를 담당하는 저장소**다.

### Equipment 
Equipment Layer는 실제로 물리적인 작업을 수행하는 장비들이 있는 계층이다.
이 구조에서는 다음 장비들이 포함된다.

- 
Conveyor Belt

- 
Laser (Depth Detector)

- 
Camera

- 
Robot Arm

- 
AMR

#### Conveyor Belt

- 
제품을 이동시키는 장치

- 
Arduino 기반 Conveyor Controller가 제어 가능

- 
시작 / 정지 / 상태 보고 가능

#### Laser

- 
거리 또는 깊이 정보 측정

- 
conveyor belt 위 제품 유무나 높이 감지 가능

#### Camera

- 
이미지 획득

- 
AI Server로 이미지 전송

#### Robot Arm

- 
pick / place 작업 수행

- 
특정 좌표에서 물체를 집고 놓음

#### AMR

- 
물체나 장비를 다른 위치로 운반

- 
Nav2 기반 자율주행 가능

## V2

### HW Architecture

- 
**Admin PC**:** **관리자용 PC

- 
**Customer PC**: 고객 PC

- 
**Control Server**: 관제 시스템을 구동시키는 서버

- 
**AI Server**: AI 모델을 작동시키는 서버.

- 
**Cloud Server**: DB 사용을 위한 서버. 시스템의 상태, 이력을 저장하는 저장소 역할

- 
**HW Controller**: 컨베이어, Laser 센서 등을 연결하는 하드웨어

- 
**Arm Controller**: 로봇팔 작동을 위한 하드웨어

  - 
주물 제작 과정, 적재/출고 과정에서 사용하는 기능이 다르기 때문에 나눔

- 
**AMR Controller**: AMR 작동을 위한 하드웨어

### SW Architecture

- 
**Management Service**

  - 
관리자에게 공정 관리를 위한 서비스를 제공한다. 

  - 
Control Server의 Control Service와 연결된다.

  - 
관리자 / 고객을 구분하기 위해 유저 인증 기능 필요

- 
**Ordering Service**

  - 
고객에게 주물 발주를 위한 서비스를 제공한다.

  - 
발주 기능을 제외한 서비스에 접근이 불가능 하도록 권한 설정이 필요하다.

  - 
AI Server, Cloud Server로 접근이 불가해야 함.

- 
**Control Service(Server)**

  - 
공정 전체 시스템에 대한 관리자 역할을 한다.

  - 
HW 제어, AI Service, DB Service 등 전반적인 시스템 서비스를 관리한다.

- 
**Fleet Management System**

  - 
HW 제어의 실행 부분을 담당한다.

  - 
Control Server(Server)가 제어 명령을 내리면 하드웨어가 실제로 동작할 수 있도록 실행 명령을 내림

- 
**AI Service**

  - 
제품 검출/ segmentation / defect detection / 객체 위치 추정 / 정상, 불량 판별을 수행한다.

  - 
Control Service(Server)로부터 추론 요청이 들어오면 AI Service는 추론 결과를 응답한다.

- 
**DB Service**

  - 
데이터를 기록/조회 하기 위한 서비스

  - 
반드시 Control Service(Server)를 통해 데이터를 핸들링 한다.

- 
**Control Service(HW)**

  - 
컨베이어, Laser 센서 등을 연결하는 서비스

- 
**Arm Control Service**

  - 
로봇팔 작동을 위한 서비스

- 
**AMR Control Service**

  - 
AMR 작동을 위한 서비스

## V3

### HW 

- 
이전 피드백: 화살표는 뭉쳐지면 안된다. 

- 
Arm Controller 쪽 화살표 추가 

- 
Cloud Server X → DB Server 하고 cloud 에서 쓸거면 따로 표시 

### SW 

- 
피드백 

  - 
점선은 다른 거 의미해서, 실선으로 교체 

  - 
FMS랑 control service가 따로 있으면, DB랑 AI가 control을 무조건 거쳐서 FMS로 가니까 비효율적이다. 

    - 
차라리 Interface layer를 넣어서, ui갈아끼우면 유지보수 잘 할 수 있도록 해라

- 
Interface Layer (Interface Service)

  - 
역할

    - 
UI (Admin / Customer)와 시스템 사이의 **입출력 창구**

    - 
요청을 **표준 API 형태(JSON 등)**로 변환해서 Control Layer로 전달

    - 
응답도 UI에 맞게 가공해서 전달

  - 
필요 이유: 

    - 
UI와 내부 시스템을 **완전히 분리 (Decoupling)**

    - 
UI 바꿔도 backend 안 바꿔도 됨

    - 
ex)

      - 
웹 → 앱 → 태블릿 UI 바뀌어도 **backend 그대로 사용 가능**

      - 
유지보수 비용 ↓

- 
 Control Layer (Control Service)

  - 
역할:

    - 
전체 시스템의 **중앙 두뇌 (Decision Layer)**

  - 
하는 일:

    - 
요청 검증 (권한, 데이터 형식)

    - 
비즈니스 로직 처리

    - 
DB 저장

    - 
AI 호출

    - 
HW/로봇 제어 명령 생성

    - 
상태 관리

  - 
필요 이유: 

    - 
모든 로직을 한 곳에서 관리 → **시스템 일관성 유지**

    - 
UI, AI, DB, HW를 **서로 직접 연결하지 않게 막음**

- 
AI Server (AI Service)

  - 
역할: AI 모델 실행

    - 
품질 검사

    - 
객체 인식 (YOLO, SAM 등)

    - 
상태 판단

    - 
Control Server의 요청을 받아 결과 반환

  - 
필요 이유 

    - 
AI는 **GPU + 무거운 연산**

    - 
일반 서버와 분리해야 성능 안정

- 
DB Server (Cloud)

  - 
역할: 모든 데이터 저장

    - 
Control Server가 CRUD 수행

  - 
필요 이유: 

    - 
데이터는 **단일 source of truth**로 관리해야 

    - 
Cloud에 두면:

      - 
백업

      - 
확장

      - 
접근성 ↑

## V4

### SW 

- 
**V3와 다르게, Interface Service와 DB Server가 ‘단방향’ 연결되어있다.  **

  - 
이유1: Interface Service는 **read-only**, Control Service를 거쳐야만 하면 비효율적 

  - 
이유2: Control Service 입장에서도 (작업 순서 결정, HW 명령 등) 이미 바쁜 제어 로직을 맡고 있어 조회 트래픽을 따로 안게 되지 않아도 된다. 

  - 
예상 문제 상황:

    - 
direct read가 위험한 경우

      - 
“현재 작업 가능 여부”처럼 **비즈니스 규칙 해석이 필요한 값**

      - 
여러 테이블을 조합해서 계산해야 하는 값

      - 
DB raw state와 실제 시스템 state가 다를 수 있는 값

      - 
아직 commit 안 된 중간 상태
이런 건 Interface가 DB만 보고 판단하면 안 되고,
**Control Service가 계산한 결과**를 보여줘야 해.

  - 
**결론:  조회를 두 종류로 나눔.** 

    - 
단순 조회: Interface Service → DB direct read 

      - 
ex) 주문 목록, 적재 이력, 알람 이력, .. 

    - 
해석이 필요한 조회: Interface Service → Control Service 

      - 
ex) 이송 가능 여부, 현재 공정 승인 가능 여부, 라우팅 결정 결과, 작업 추천/최적화 결과 

- 
Factory PC vs. Admin PC vs. Customer PC 분리 

  - 
Facotory PC는 PyQT 기반 

  - 
Admin PC, Cutomer PC: 웹페이지 (Next.js, React)

### HW

## V5

### SW
**pyqt 관련**

- 
V4에서는 pyqt에서 monitoring service를 UI와 Server에서 분리하였는데,

- 
pyqt는 web과 다르게 하나의 프로그램으로 web의 frontend와 backend가 하나의 프로그램으로 실행됨.

  - 
pyqt는 UI의 역할이 더 강하기 때문에 UI 파트로 이동x
**Interface service - Control Service 통신 방식 관련**

- 
기존 통신 방식을 양방향 http에서 Interface service → Control Service tcp로 변경

  - 
변경 이유: 불필요한 오버헤드를 줄이고 단방향으로만 받기 때문에 http의 복잡한 구조가 필요없다.
**추가적으로 변경해야하는 사항**

1. 
**Jetson(cam) → Control Service → AI Server로 변경해야함.**

  1. 
포토센서가 주물을 확인하는 게 trigger가 되어서 카메라가 사진을 찍음.

  1. 
이미지를 Control Service로 보냄

  1. 
Control Service는 AI Service에 이미지와 함께 추론 요청을 보냄

  1. 
AI Service는 추론 결과를 Control Server로 보냄

1. 
**HW Controller의 통신을 ROS2 → MQTT로 변경**

1. 
**HW Controller의 Control Service 이름 변경**

  1. 
Main Server의 Control Service와 네이밍 겹침

1. 
**Arm Control Service 이름 변경**

  1. 
Main Server의 Control Service와 네이밍 겹침

1. 
**AMR Control Service 이름 변경**

  1. 
Main Server의 Control Service와 네이밍 겹침

### HW

## V6

### SW

1. 
**HW Controller의 분리**

- 
V5에서는 Camera와 Conveyor가 HW Controller 하나로 통합되어 있었음

- 
카메라로부터 이미지를 전송하는 하드웨어와 컨베이어를 제어하는 하드웨어가 분리됨에 따라서

  - 
Image Publisher(Jetson), HW Controller(ESP32) 두 개의 컴포넌트로 분리

1. 
**MQTT 통신 추가**

- 
HW Controller의 분리에 따라, ESP32와 Jetson의 통신을 위한 MQTT 통신이 추가됨

1. 
**HW Controller(ESP32)와 Image Publisher(Jetson-orin)간 Serial 통신 추가**

  1. 
1번째 포토센서에 물체가 감지되면 컨베이어 가동 **(HW Controller(ESP32)에서 컨베이어 직접 제어)**

  1. 
2번째 포토센서에 물체가 감지되면 아래 2가지 동작을 수행한다.

    1. 
컨베이어 중지 **(HW Controller(ESP32)에서 컨베이어 직접 제어)**

    1. 
Image Publisher에 연결된 카메라에서 이미지 캡처 **(ESP32 → Image Publisher간 Serial 통신)**

  1. 
이미지를 Management Service에 전송 **(Image Publisher → Manegement Service간 TCP 통신)**

  1. 
불량 검사가 완료되면 컨베이어 가동 **(Management Service → Image Publisher간 TCP 통신)**

1. 
**전반적인 네이밍 수정**

- 
Main Server

  - 
Control Service → Management Service

- 
Image Publisher

  - 
Image Publishing Service

- 
HW Controller

  - 
HW Control Service

- 
좌측 Arm Controller → Manufacturing Controller

  - 
Arm Control Service → Manufacturing Service

- 
우측 Arm Controller → Stacking Controller

  - 
Arm Control Service → Stacking Service

- 
AMR Controller → Transport Controller

  - 
AMR Control Service → Transport Service

### HW

- 
네이밍 수정은 SW쪽 참고

- 
HW Controller 부분 Conveyor와 Camera 분리

- 
*온도 측정에 Laser 사용 안 하는 것으로 알고 Laser 제외시킴*

### Detailed Design (6651919)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6651919
**최종 수정**: v11 (2026-04-10 sync)

[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/6389808/?draftShareId=37718f45-2634-4a3e-821b-d2a51e5be9c1](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/6389808/?draftShareId=37718f45-2634-4a3e-821b-d2a51e5be9c1)
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/6488115/?draftShareId=a01472c4-992c-4548-b921-4241acda15d7](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/6488115/?draftShareId=a01472c4-992c-4548-b921-4241acda15d7)

#### HW (6389808)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6389808
**최종 수정**: v2 (2026-04-19 sync)

#### SW (6488115)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6488115
**최종 수정**: v1 (2026-04-19 sync)

#### System Scenario - State Diagram (22741008)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22741008
**최종 수정**: v39 (2026-04-19 sync)

# 작성법 

- 
둥근 네모: state, 

- 
화살표 위: **event [guard] / acion (parameters)**

- 
일단 크게 분류한다. → 그 안에 복합 상태로 보이는 것이 있는 경우, 나눈다. 

  - 
복합 상태란, initial signal 과 final event 가 동일할때를 의미한다. 

    - 
예를 들어, 복합 상태 (container)로 묶인 상태 안의 하위 상태의 시작과 끝이 다른 signal가 하나라도 연결되어 있으면 안된다. 

- 
로봇상태에서 destination으로 가는 것은 동일하게 볼 수 있지만, 작업 구역에 따라 state를 나누는 것이 좋다. 

  - 
이유: 각 작업 안에서 state 가 달라지거나, 시나리오상 다른 flow가 생길 수 있기 때문이다. 

# Standard UML for State Diagram 

# AMR for SmartCast Robotics 

- 
Task (Transport from zone to another zone) 

  1. 
CAST (주조) → PP (후처리) 구역 이동 

  1. 
INSP (검사) → STRG (적재) 구역 이동 

  1. 
STRG (적재) → SHIP (출고) 구역 이동 

- 
AMR 은 src 구역 → dest 구역으로 이동으로의 역할이 같기 때문에, composite state 로 나눴습니다. 

  - 
다만 아래서 설명드릴 예외 상황이 존재하기 때문에 history state  를 적용하여 그렸습니다. 

- 
Task 중간 충전하러 가는 예외 상황 정의

  - 
AMR 은 FMS 에 의해, charging 이 된 상태에서만 task를 부여받습니다. 

  - 
따라서, AMR의 배터리가 특정 threshold아래로 내려갈 수 있는 상황은 Loading (상차)를 기다리는 상황밖에 없다고 가정하였습니다. 

  - 
만약, 특정 Task 로 이동시에 방전이 된다고 가정하면 그건 FMS의 문제일 것이기 때문입니다. 

    - 
따라서, FMS 는 해당 task 의 거리에 필요한 충전량과 현재 충전량을 비교하여 높을 때에만 task를 할당합니다. 

- 

# RobotArm for SmartCast Robotics 
****
**질문** : 현재는 상위 상태(Idle, Pro위(makingMold, pouring 등)를 기준으로 다이어그램을 작성했습니다.
명확성을 위해 '패턴 위치로 이동', '파지' 같은 세부 동작 단위까지 모두 상태(State)로 정의해서 다이어그램에 포함시켜야 할지 아니면 현재처럼 주요 공정 단위로 상태를 유지하되, 세부 동작은 별도 명세서로 관리할지 궁금합니다
상차 도착해서 기다리다가 배터리 나가서 재배차 하는 경우에는?

# Manhole for SmartCast Robotics 

# Reference 

- 
[https://www.visual-paradigm.com/guide/uml-unified-modeling-language/about-state-diagrams/](https://www.visual-paradigm.com/guide/uml-unified-modeling-language/about-state-diagrams/) 

- 
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/24412161/?draftShareId=88b01257-81d2-4644-bbe5-7adb487a2622](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/24412161/?draftShareId=88b01257-81d2-4644-bbe5-7adb487a2622)

#### Data Structure - Class Diagram (22216784)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22216784
**최종 수정**: v12 (2026-04-19 sync)

# Class Diagram 
주조공장 스마트팩토리에서 서버, 센서, 컨베이어, 카메라, 로봇 등이 어떤 역할을 하고 서로 어떻게 연결되는지를 객체지향적으로 정리한 시스템 구조도
**Device (Interface)**
Description: 전원 제어 기능을 정의하는 장치 공통 인터페이스
**Robot (Interface)**
Description: 이동 및 작업 수행 기능을 정의하는 로봇 인터페이스
**Sensor (Interface)**
Description: 객체 감지 및 신호 전송 기능을 정의하는 센서 인터페이스
**Server (Interface)**
Description: 데이터 송수신 기능을 정의하는 서버 인터페이스
ControlServer
Description: 전체 시스템을 제어하고 각 장치 및 로봇을 관리하는 중앙 제어 서버
InspectionComputer
Description: 비전 기반으로 주물 상태를 검사하고 결과를 제어 서버에 전달하는 시스템
ConveyorBelt
Description: 주물을 공정 간 이동시키는 이송 장치
LaserSensor
Description: 거리 변화를 이용하여 물체 존재 여부를 감지하는 센서
Motor
Description: 컨베이어 및 장치의 구동을 담당하는 구동 장치
WebCamera
Description: 이미지를 촬영하여 검사 시스템에 제공하는 영상 입력 장치
RobotArm1
Description: 패턴 작업 및 재료 주입 공정을 수행하는 로봇팔
RobotArm2
Description: 완성된 주물을 수거하고 분류하는 로봇팔
TransferRobot
Description: 주물을 로봇 간에 전달하는 이송 로봇
CleaningRobot
Description: 공장 내부를 순찰하며 청소 작업을 수행하는 로봇이
Worker
Description: 작업 지시를 입력하고 주물을 컨베이어에 적재하는 작업자
Bin
Description: 분류된 주물을 저장하는 저장 용기

#### Data Structure - ER Diagram (22184015)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22184015
**최종 수정**: v1 (2026-04-19 sync)

#### GUI Design - 화면 구성도 (22151233)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22151233
**최종 수정**: v1 (2026-04-19 sync)

#### System Scenario - Sequence Diagram (22937608)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22937608
**최종 수정**: v24 (2026-04-19 sync)

## **Sequence Diagram이란?**

- 
UML(통합 모델링 언어)에서 시스템 구성 요소들이 시간의 흐름에 따라 서로 어떤 메시지를 주고받으며 상호작용하는지를 시각적으로 보여주는 동적 다이어그램

## 특징

- 
 및 보고한다.

- 
컨베이어 벨트 시스템 : 컨베이어 벨트 위에 주물 투입 → 첫 번째 포토센서에 주물 감지 후 벨트 동작 → 두 번째 포토센서 인식 후 벨트 정지 → 상단의 카메라가 비전 검사 시작 → 검사 종료 후 수동으로 벨트 동작 버튼 클릭 → 4-5초 동작 → 하단 대기 중인 AMR위로 자동 적재

- 

- 
Storgae zone은 양품이 종류별로 적재되는 곡선형 보관 랙과, 불량품이 한 곳에 모이는 박스로 구성

## Question

- 
출고, 예외 상황과 같이 비동기인 이벤트들도 한 다이어그램에 표현해야 하는지

- 
Mold making에서 발생되는 세부 Task들도 나눠야 하는지(패턴 집기, 사형에 패턴 찍기, 패턴 제자리에 두기)

- 
Conveyor belt 에서 AMR로 Loading 되고 나서 완료 신호를 누가 어떻게 Control Service로 보내야 하는지

#### Interface Specification (22806540)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22806540
**최종 수정**: v28 (2026-04-19 sync)

# 작성 기준 및 목표

- 
**작성 기준**: , , (HW, SW architecture version: V6)

- 
**목적**: 컴포넌트 간 통신 프로토콜, 메시지 형식, 방향성 정의

# 프로토콜 및 통신 방향 정의

| 심볼 | 의미 | 적용 계층 |
|---|---|---|
``
| → | 단방향 전송 (Publisher/Request/Command) | HW Controller, Image Publisher, Image Publisher-Management Service, DB Service-Interface Service |
``
| ↔ | 양방향 통신 (Request-Response, Action, Pub/Sub) | UI-Server, Server-Server, ROS2 Action |
| 🟣 HTTP | RESTful API (JSON) | Customer/Admin PC ↔ Interface Service |
| 🟠 TCP | Low-overhead Binary/JSON Stream | Interface Service ↔ Management Service, Server ↔ DB/AI |
| 🔵 MQTT | Lightweight Pub/Sub (IoT/HW) | Image Publishing Service -> Management Service |
| 🟢 ROS2 (DDS) | Real-time Action/Topic/Service | Management Service ↔ Manufacturing, Stacking, Transfer Service |

# UI Layer (Customer / Admin / Factory PC)
고객(Customer)과 관리자(Admin)가 시스템과 상호작용하는 인터페이스 계층

## UI ↔ Interface Service (HTTP)
웹/앱 기반 고객(Customer) 인터페이스와 백엔드 관리자(Admin) 시스템 간의 표준 RESTful API 통신

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
``
| Ordering Service(Customer PC) | Interface Service | 🟣 HTTP ↔ | POST /api/orders | JSON (주문 생성/조회) |
``
``
| Ordering Management Service(Admin PC) | Interface Service | 🟣 HTTP ↔ | POST /api/orders/manage | JSON (주문 승인/수정/상태조회) |
``
``
| Interface Service | Ordering Management Service (Admin PC) | 🟣 HTTP ↔ | 200 OK / 4xx / 5xx | JSON (처리 결과 응답) |

###  `POST /api/orders` (고객 주문 요청) 

### Request (Admin PC → Interface Service)

### Response (Interface Service → Admin PC)

## Monitoring Service (UI) ↔ Management Service (Server)
공장 운영자 PC의 공정 모니터링 화면과 Main Server 간 실시간 상태 공유 및 장비 제어

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
``
| Management Service | Monitoring Service | 🟠 TCP ↔ | StatusStream.pub | JSON/Binary (실시간 공정 모니터링/공장 좌표/이상 알림) |
``
``
| Monitoring Service | Management Service | 🟠 TCP ↔ | ControlCommand.req | JSON/Binary (장비 제어/모드 변경 요청) |
``
| Management Service | Monitoring Service | 🟠 TCP `` | ControlCommand.res | JSON/Binary (제어 결과/현재 상태) |

### `StatusStream.pub` (서버 → UI, 실시간 공정 모니터링 스트림)

### `ControlCommand.req` / `.res` (UI ↔ 서버, 장비 제어)

# Server Layer (Main / Interface / AI / DB)
관제 시스템과 이와 연동된 AI(Artificial Intelliegnece), DB(Database)의 서버들간의 통신

## Interface Service → Management Service (TCP, 단방향)
관리자 요청을 처리하는 Interface Layer에서 Main Server로 작업 할당을 단방향으로 푸시하는 채널

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
``
| Interface Service | Management Service | 🟠 TCP → | TaskAllocation.pub | JSON/Binary (단방향 작업/주문 할당 스트림) |

### `TaskAllocation.pub` (Interface → Management, 단방향 푸시)

## Management Service ↔ AI / DB Service (TCP)
비전 시스템(Vision System)을 통한 검사(Inspection) 요청과 주문/작업/이력 데이터의 저장·조회를 처리하는 서버 간 통신

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
| Management Service | AI Service | 🟠 TCP `` | InferenceRequest/Response | JSON + Image Buffer |
``
| Management Service | DB Service | 🟠 TCP `` | CRUD_Operation | SQL/JSON Query |

### `InferenceRequest` (비전 시스템(Vision System)을 통한 검사(Inspection)/객체 인식 요청)

### `CRUD_Operation` (주문/작업/이력 데이터 처리)

# HW Layer (Operators, Controllers)
ROS2 Action과 센서 파이프라인을 통해 실제 생산, 이송, 적재 장비를 제어하고 각 상태를 수집하는 실행 계층

## Management Service ↔ HW Operators (ROS2 Action)
Management Service가 작업 지시를 내리면 Manufacturing/Transfer/Stacking Operator가 ROS2 Action으로 실제 생산, 이송, 적재 장비를 제어하는 양방향 인터페이스

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
``
| Management Service | Manufacturing Service | 🟢 ROS2 ↔ | CastJob.action | ROS2 Action |
``
``
| Management Service | Transfering Service | 🟢 ROS2 ↔ | TransferJob.action | ROS2 Action |
``
``
| Management Service | Stacking Service | 🟢 ROS2 ↔ | StackingJob.action | ROS2 Action |

### `CastJob.action` (주조 공정)

### `TransferJob.action` (AMR(Autonomous Mobile Robot) 이송)

### `StackingJob.action` (로봇팔(Robotic Arm) 파지(picking))

## Sensors/Image pipeline (TCP → MQTT 단방향 스트림)
포토 센서(Photo Sensor) 트리거부터 이미지 캡처, 전송까지의 단방향 데이터 파이프라인으로 비전 시스템(Vision System)의 검사(Inspection) 공정의 자동화를 지원. **V6 아키텍처**

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
``
| HW Control Service | Image Publishing Service | 🟠 TCP → | TriggerStream | Binary/JSON (센서 트리거 + 메타데이터) |
``
``
| Image Publishing Service | Management Service | 🔵 MQTT → | /factory/vision/trigger | MQTT Payload (이미지 참조/버퍼 + Job ID) |

### `TriggerStream`** (HW Control → Image Pub, TCP)**

### `/factory/vision/trigger`** (Image Pub → Management, MQTT)**
Inquiries

1. 
메세지 포맷에는 **JSON/Binary/Protobuf 등**이 있는데, 이들 중 하나로 단일화하는 것이 좋은지, 아님 목적에 맞는 방향으로 맞춰서 작성하는 것이 좋은가?

1. 
User Requirement, System Requirement, System Architecture에 이어서 이를 바탕으로 Detailed Design 단계 중 하나인 Interface Specification을 작성함. 특히 SW, HW architecture를 기반으로 작성했는데, 이러한 방향이 맞는가?

1. 
From, To, 프로토콜은 시스템 아키텍처로부터 충분히 알수 있었지만, 이로부터 Interface Item, Message Font 등을 얻어내기 위해서는 어떤 규격을 참조해야 하는가? 검색해보니 HTTP, REST(RESTful API), URI/URL, JSON가 있는데, 이들에 맞춰서 작성해야 하는건가? 만일 가능하다면, 관련 규격 가이드라인을 추천해줄 수 있는가? 이를 위해서는 일정 수준의 백엔드 관련 지식이 필요한가?

1. 
3번과는 별개로, Interface Specification을 작성할시 다음의 단계를 따르는 것이 합리적인가?

  1. 
1단계: "누가, 무엇을, 왜" 통신하는가? (요구사항 → 인터페이스 후보 추출)

    1. 
이 기능/요구사항을 구현하려면 **어떤 컴포넌트 간 데이터 교환**이 필요한가?

    1. 
데이터의 **방향**(누가 보내고 누가 받는가)은 어떻게 되는가?

    1. 
이 통신의 **목적**(명령/조회/알림/스트림)은 무엇인가?

  1. 
2단계: "어떤 데이터가 오가야 하는가?" (엔티티/파라미터 분석, 메세지 포맷 도출)

    1. 
이 작업에 필요한 **입력 파라미터**는 무엇인가? (User Requirements의 `Data` 컬럼 참고)

    1. 
작업 결과로 반환해야 할 **출력 데이터**는 무엇인가?

    1. 
추적/로깅을 위해 필요한 **메타데이터**(ID, timestamp 등)는 무엇인가?

  1. 
3단계: "어떤 프로토콜/형식으로 전송할 것인가?" (아키텍처 매핑)

    1. 
아키텍처 다이어그램에서 이 연결의 **프로토콜**(HTTP/TCP/MQTT/ROS2)은 무엇인가?

    1. 
데이터 직렬화는 **JSON/Binary/Protobuf**중 어떤 방식이 적합한가?

    1. 
실시간성/신뢰성 요구사항에 따라 **QoS**(At least once, Best effort 등)는 어떻게 설정할 것인가?

  1. 
4단계: "제약조건과 비기능 요구사항은 어떻게 반영할 것인가?" (비기능적 요구사항(NFR) 통합)

    1. 
응답 시간, 갱신 주기 같은 **성능 요구사항**(1초 이내 등)은 메시지 구조에 어떻게 반영할 것인가?

    1. 
에러 처리, 재시도, 타임아웃 같은 **신뢰성 요구사항**은 어떻게 명세화할 것인가?

    1. 
보안(인증/인가), 데이터 무결성 같은 **품질 요구사항**은 어디에 기술할 것인가?

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

### System_Requirements_v3 (6258774)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6258774
**최종 수정**: v29 (2026-04-15 sync)

누르면 바로 이동합니다~
|   |
|---|
****
| SR-ORD-01 | 원격 발주 기능 |   | 시스템은 고객이 표준화된 주조 제품을 선택하고, 규격/수량/납기/후처리 옵션을 입력하여 발주할 수 있는 원격 주문 시스템을 제공한다 |   |
****

- 

- 

  - 
| SR-ORD-01-01 |   | 표준 제품 조회 기능 | 사용자는 시스템에 등록된 표준 주조 제품 리스트를 카테고리 별로 조회할 수 있어야 한다.  [기능]제품 카테고리 별 필터링 기능 제공제품별 상세 데이터 제공 규격별 기본 이미지, 이름,  재질, 기본 가격 범위, 하중 등급 |   |
****

- 

  - 

- 

- 
| SR-ORD-01-02 |   | 제품 옵션 선택 기능 | 사용자는 선택한 제품에 대해 규격, 수량, 재질, 후처리 조건의 주문 사양을 입력할 수 있어야 한다.[기능]규격 옵션 선택직경, 두께, 하중 등급, 재질 옵션, 후처리 옵션수량, 희망 납기일 입력비고란 제공 |   |
****

- 

- 

- 
| SR-ORD-01-03 |   | 도면/디자인 정보 확인 기능 | 사용자는 주문 제품의 기본 디자인과 선택 사양을 주문 전에 확인할 수 있어야 한다. [기능]시스템은 선택한 규격과 옵션에 따른 제품 요약 정보를 보여줘야 한다.시스템은 기본 디자인 시안을 표시해야 한다.시스템은 옵션 선택 결과를 미리보기 형태로 보여줄 수 있어야 한다. |   |
****

- 

- 
| SR-ORD-01-04 |   | 주문 가능 여부 검증 기능 | 시스템은 사용자가 입력한 주문 조건이 실제 생산 가능한 범위인지 논리적으로 검증해야 한다. [기능]시스템은 입력된 주문이 기술적으로 호환되는 조합인지 검증할 수 있어야 한다시스템은 모든 입력 항목의 유효성이 확인되지 않은 경우, 주문 제출 프로세스 실행을 제한해야 한다. |   |
****

- 

- 

- 

- 

- 
| SR-ORD-01-05 |   | 예상 견적 및 납기 안내 기능 | 시스템은 사용자가 입력한 데이터를 바탕으로 예상 견적과 예상 납기를 제공해야 한다.[기능]시스템은 [ 제품 기본 단가 + 옵션 가산비 + 수량 ] 로직에 따라 예상 합계 금액을 산출해야 한다.시스템은 예상 납기 범위를 표시해야 한다.시스템은 최종 견적은 관리자 검토 후 확정됨을 안내해야 한다.시스템은 주문 정보를 저장할 수 있어야 한다시스템은 고유한 주문 ID를 생성할 수 있어야 한다 |   |
****

- 

- 

- 
| SR-ORD-01-06 |   | 원격 주문서 제출 기능 | 사용자는 최종 정보를 결합하여 주문 요청서를 관리자에게 제출할 수 있어야 한다.[기능]시스템은 사용자로부터 회사명, 연락처, 배송지 주소,담당자명,이메일을 필수로 입력 받아야 한다.시스템은 주문서 제출 전 모든 선택 사양을 한눈에 볼 수 있는 '주문 요약 페이지'를 제공해야 한다[비기능]주문 절차는 최대 5단계 이내로 완료 가능해야 한다. |   |
****

- 

- 

- 
| SR-ORD-02 | 주문 상태 조회 기능 |   | 사용자는 제출한 주문의 처리 상태를 조회할 수 있어야 한다[기능]시스템은 주문 접수 상태를 [접수/검토 중/승인됨/생산 중/출하 준비/완료] 6단계 상태를 구분하여 표시해야 한다.사용자는 과거 제출한 주문서의 상세 옵션 내역을 상시 열람 가능해야 한다.시스템은 상태 변경 시 사용자에게 알림을 제공할 수 있어야 한다. |   |
****

- 

- 

- 

- 

- 

- 
| SR-ORD-03 | 관리자 주문 검토 및 승인 기능 |   | 관리자는 접수된 주문 요청을 검토하고 승인 또는 수정 요청할 수 있어야 한다.[기능]관리자는 고객이 입력한 상세 사양을 확인할 수 있어야 한다.관리자는 생산 가능 여부를 검토할 수 있어야 한다.관리자는 예상 견적/납기를 수동으로 수정 및 확정할 수 있어야 한다.관리자는 접수된 주문에 대해 [승인/반려/수정 요청] 중 하나의 상태로 최종 결정 및 변경할 수 있어야 한다.[비기능]주문자 정보와 연락처는 안전하게 저장되어야 한다.관리자 기능은 권한이 있는 사용자만 접근 가능해야 한다. |   |

### 
| [공정 통합 관제] |
****

- 

- 

- 

  - 

  - 

- 

- 

- 

- 

- 

- 
| SR-CTL-01 | 공정 Map 기반 실시간 모니터링 기능 |   | 시스템은 공정 레이아웃(Map) 상에서 이송 자원 및 주요 설비의 위치와 상태를 실시간으로 시각화하여 관리자가 전체 운영 상황을 직관적으로 파악할 수 있도록 해야 한다.[기능]시스템은 공장 전체 레이아웃(Map)을 화면에 표시할 수 있어야 한다.시스템은 각 이송 자원의 상태를 표시할 수 있어야 한다.시스템은 Map 상에 표시할 수 있어야 한다.이송 자원과 주요 공정 설비의 위치이송 자원과 주요 공정 설비의 상태시스템은 공정 상태에 따라 색상과 아이콘으로 상태를 구분하여 표시할 수 있어야 한다.시스템은 특정 자원과 설비를 선택할 수 있어야 한다.시스템은 선택된 자원 또는 설비의 상세 정보를 표시할 수 있어야 한다.[비기능]시스템은 위치 및 상태 정보를 1초 이내 주기로 갱신해야 한다.시스템은 다수의 이송 자원 및 설비를 동시에 표시하더라도 성능 저하 없이 동작해야 한다.시스템은 사용자가 직관적으로 상태를 인식할 수 있도록 UI를 구성해야 한다. |   |
****

- 

- 

- 

- 

- 
| SR-CTL-02 | 공정 제어 기능 |   | 관리자는 공정 장비를 제어하여 전체 생산 공정을 관리할 수 있어야 한다.[기능]시스템은 장비의 상태를 시작/중지로 변경할 수 있어야 한다.시스템은 관리자의 제어 명령을 각 장비에 전달할 수 있어야 한다..[비기능]시스템은 관리자의 제어 명령을 1초 이내 반영해야 한다.시스템은 긴급 상황 시 장비를 즉시 정지할 수 있어야 한다.시스템은 제어 명령 수행 중에도 시스템 안정성을 유지해야 한다. |   |
****

- 

- 

- 

- 
| SR-CTL-03 | 이상 감지 및 알림 기능 |   | 시스템은 공정 중 발생하는 이상 상태를 감지하고 관리자에게 알림을 제공할 수 있어야 한다. [기능]시스템은 공정 중 발생하는 이상 상태를 감지할 수 있어야 한다.시스템은 감지된 이상 상태를 관리자에게 알림으로 제공할 수 있어야 한다.시스템은 다수의 알림 발생 시 우선순위를 구분할 수 있어야 한다.[비기능]시스템은 이상 상태를 1초 이내 감지해야 한다. |   |

- 

- 

  - 

- 

- 

- 
| SR-CTL-04 | 생산 개시 |   | 시스템에서 승인된 주문 중 생산 가능한 항목을 선택하여 실제 공정에 작업을 할당하고 생산을 시작할 수 있어야 한다. [기능] 시스템은 관리자가 단일 또는 다수의 주문을 선택하면 추천 우선순위를 보여준다.관리자는 시스템이 추천한 우선순위를 참고하여 시작할 주문을 선택할 수 있어야 하며, 추천 순서를 변경하거나 특정 주문을 우선 지정할 수 있어야 한다.시스템은 관리자가 주문에 대한 생산을 결정하면 주문 상태를 [승인] → [생산 중]으로 변경하고, 해당 주문을 실제 공정 작업에 할당해야 한다.시스템은 각 주문에 대해 예상 완료 시점, 지연 위험도, 착수 가능 여부(Ready 상태)를 함께 표시해야 한다.시스템은 착수 불가능한 주문에 대해 선택 제한 또는 경고 표시를 제공해야 한다.시스템은 관리자에 의해 우선순위가 수동으로 변경된 경우, 변경 이력 및 사유를 기록해야 한다. |   |

- 

- 

  - 

  - 

  - 

  - 

  - 

  - 

  - 

  - 

  - 

  - 

  - 
| SR-CTL-05 | 우선순위계산 |   | 시스템은 관리자가 다수의 주문을 선택하면 생산 우선순위를 계산해 보여줄 수 있어야 한다. [기능]시스템은 관리자가 다수의 주문을 선택하면, 납기일뿐만 아니라 공정 가용성, 병목 상태, 자재/금형 준비 여부 등을 고려하여 생산 우선순위를 자동으로 계산하고 추천 순위를 제공해야 한다.시스템은 우선순위 추천 결과에 대해 추천 사유를 함께 제공해야 한다.납기일 임박 예상 완료일 늦음지연 위험착수 가능 여부병목 공정 상태세팅 변경 비용고객 중요도수량 및 부분 납품 가능성설비/작업자 가용성 자재 부족금형 미준비 |   |
|   | 병목 해결 |   | 시스템은 주물 제작 병목현상을 해결하기 위해 진행률을 기준으로 작업량을 재분배할 수 있어야 한다. |   |
|   | 생산 종료 |   | 주물 생산이 종료되면 시스템은 다음 공정 진행을 위해 제작된 주물을 이송요청을 할 수 있어야 한다. - 제작수량 누가 카운팅?? 생산종료 조건? |   |

### 
| [ 주물 생산 자동화 공정 ] |
****
| SR-CAST-01 | 재료 공급 관리 및 용해 |   | 시스템은 외부에서 반입된 고체 원재료를 검수하고, 열에너지를 가해 주조에 적합한 최적의 용탕 상태로 전환 및 유지할 수 있어야 한다 |   |
****

- 

- 

- 

- 

- 

- 
| SR-CAST-01-01 |   | 원재료 준비 및 투입 기능 | 시스템은 투입 전 원재료의 상태를 분석하여 부적합품을 선별하고, 설정된 규격과 중량에 맞춰 용탕 제조 설비 내부로 재료를 공급할 수 있어야한다.[기능]시스템은 원재료의 외형 및 물성을 분석하여 이물질 및 부적합 재료를 판별해야 하며, 최소 2단계 이상의 독립적인 선별 공정을 거쳐 이를 분리해야 한다.시스템은 유효한 원재료의 치수와 중량을 실시간으로 측정하고, 해당 데이터가 설비 투입 가능 범위 내에 있는지 논리적으로 판단해야 한다.시스템은 설비 내부의 수용 가능 부피를 실시간으로 계산하여, 전체 부피 대비 재료 투입량이 80%수준에 도달할 경우 투입 공정을 자동으로 중단하거나 조절해야 한다.검증 및 투입 조건을 모두 만족하는 경우에만 시스템은 공급 장치를 가동하여 재료를 설비 내부로 안전하게 투입해야 한다.[비기능]원재료 투입 프로세스의 모든 단계는 산업 안전 표준 가이드라인을 준수하여 설계되어야 한다.시스템은 향후 새로운 종류의 원재료나 물성 변화 데이터가 추가되더라도 기존의 선별 및 투입 로직을 최소한의 수정으로 유지할 수 있는 유연한 구조를 가져야 한다. |   |
****

- 

- 

- 

- 

- 
| SR-CAST-01-02 |   | 원재료 융용 기능 | 시스템은 가열 설비를 제어하여 고체 상태의 원재료를 완전한 용탕 상태로 용융 시키고, 주입 공정 전까지 최적의 가공 온도를 안정적으로 유지할 수 있어야 한다.[기능] 시스템은 설정된 목표 온도까지 내부 온도를 상승시키기 위한 가열 출력을 제어해야 한다.시스템은 용융 과정에서 용탕의 온도를 측정할 수 있어야 한다.시스템은 가열 시작부터 완전 용융 시점까지의 소요 시간을 측정하고 데이터화해야 한다.시스템은 용융 완료 후 외부 방열을 고려하여 설정된 온도 오차 범위 내에서 등온 상태를 유지해야 한다.[비기능]상온(25도)에서 가열 시작 시 목표 온도 도달 곡선의 안정성을 유지해야 한다. |   |
****
| SR-CAST-02 | 조형 및 주탕 제어 |   | 시스템은 주형을 제작하고, 준비된 용탕을 주형 내부로 정밀하게 주탕할 수 있어야 한다 |   |
****

- 

- 

- 

- 

- 

- 

- 
| SR-CAST-02-01 |   | 조형 기능 | 시스템은 특정 제품 패턴을 식별하여 주형사에 압력을 가해 형상을 성형한 뒤, 결과물을 훼손하지 않고 패턴을 분리할 수 있어야 한다.[기능] 시스템은 패턴의 고유 정보를 식별하고 해당 제품 데이터를 매칭해야 한다.시스템은 패턴을 파지(grasp)하여 성형 위치로 정밀하게 이동시킨 후 수평/수직 정렬을 수행해야 한다.시스템은 설정된 압력값에 도달할 때까지 패턴을 압입하여 형상을 성형해야 한다..시스템은 성형 완료 후 주형 내부 형상을 유지하며 패턴을 안전하게 분리해야 한다.시스템은 주형 제작에 사용된 패턴 정보 및 공정 데이터를 저장할 수 있어야 한다.[비기능]제작된 주형 치수와 패턴 원형 간 정밀도를 90% 이상 유지해야 한다.시스템은 동일 조건에서의 반복 공정 수행 시, 설정된 허용 오차 범위 내에서 결과의 재현성(Repeatability)을 유지해야 한다 |   |
****

- 

- 

- 

- 

- 

- 

- 
| SR-CAST-02-02 |   | 주탕 기능 | 시스템은 용탕을 주형으로 안전하고 정확하게 주입(주탕)할 수 있어야 한다.[기능]시스템은 주형의 주입구 위치 좌표를 실시간으로 인식하고, 공급 용기를 해당 목표 좌표로 간섭 없이 이송해야 한다.시스템은 주변 설비 및 장애물과의 접촉을 회피하는 안전한 이동 경로를 생성해야 하며, 공정 효율을 위해 이동 거리가 최소화된 최적 경로를 도출해야 한다.시스템은 주입구와 공급 용기의 상대적 위치를 정밀하게 정렬하여, 용탕 주입 시 외부 유출이 발생하지 않도록 물리적 주입 경로를 확보해야 한다.시스템은 용탕의 넘침이나 부족 현상을 방지하기 위해, 사전에 설정된 각도 시퀀스(기울기 변화량)와 속도 데이터에 따라 용탕을 주입해야 한다.주입 공정 완료 후, 시스템은 공급 용기를 즉시 수평 상태로 복귀시키고 다음 공정을 위한 지정 대기 위치로 이송해야 한다[비기능]경로 생성 및 이송 중 예상치 못한 장애물이 감지될 경우, 시스템은 즉시 동작을 중단(Emergency Stop)하고 안전 상태를 유지해야 한다.반복적인 주탕 공정 수행 시에도 설정된 주입 각도와 정렬 위치에 대한 오차가 허용 범위 내에서 일정하게 유지되어야 한다. |   |
****
| SR-CAST-03 | 냉각 및 탈형 공정 |   | 시스템은 주입된 금속이 굳는 과정을 모니터링하여 적정 시점에 최종 제품을 추출하고 관련 공정 데이터를 기록할 수 있어야 한다. |   |
****

- 

- 

- 
| SR-CAST-03-01 |   | 주물 냉각 완료 탐지 기능 | 시스템은 제품별 특성에 따른 냉각 시간과 실제 온도를 분석하여 다음 공정 수행이 가능한 상태인지 판정할 수 있어야 한다.[기능]시스템은 제품별 표준 냉각 시간 및 목표 온도 데이터를 관리하고 호출할 수 있어야 한다.시스템은 주물의 상태 정보를 실시간으로 수집하여 냉각 진행률을 파악해야 한다. 시스템은 [설정 시간 경과] 및 [목표 온도 도달] 조건을 충족할 때 완료 신호를 생성해야 한다. |   |
****

- 

- 

- 
| SR-CAST-03-02 |   | 탈형 기능 | 시스템은 냉각이 완료된 주물을 주형으로부터 분리(탈형)하고, 생산 결과를 시스템에 업데이트할 수 있어야 한다.[기능]시스템은 냉각이 완료된 제품의 위치 정보를 파악하고 최적의 추출 경로를 생성해야 한다.시스템은 주물의 손상없이 주형으로부터 주물을 탈형하여 지정된 구역으로 옮겨야한다.주물의 탈형 후, 시스템은 제품의 고유 정보와 생산 성공 여부를 기록해야 한다. |   |

### ****
| [구역 간 이송 관리] |
****
| SR-TR-01 | 이송 요청 관리 |   | 시스템은 구역 간 물품 이송 요청을 생성하고, 요청의 상태 및 이력을 관리할 수 있어야 한다. |   |
****

- 

  - 

    - 

      - 

- 

- 

- 

- 
| SR-TR-01-01 |   | 이송 요청 생성 기능 | 시스템은 구역 간 물품 이송을 위한 이송 요청을 생성할 수 있어야 한다.[기능]시스템은 생성된 이송 요청에 대해 상세 정보를 저장해야 한다.고유 식별 번호(task id)/출발 위치/도착 위치/이송 대상 물품의 종류와 수량/ 요청 시각/ 이송 상태 /배정된 이송 자원의 ID이송 상태배정 전/출발 위치로 이동/출발 위치 도착/인수 중/인수 완료(출발조건)/도착 위치로 이동/도착 위치 도착/인계 중/인계 완료/실패시스템은 이송 요청을 기본적으로 요청 순서에 따라 처리해야 한다.시스템은 우선순위가 부여된 요청에 대해 처리 순서를 조정할 수 있어야 한다.시스템은 여러 이송 요청이 동시에 생성되더라도 각 요청을 독립적으로 처리할 수 있어야 한다.[비기능]시스템은 이송 요청 정보를 누락 없이 저장해야 한다. |   |
****

- 

  - 

  - 

- 

  - 

  - 

  - 

- 

- 

- 
| SR-TR-01-02 |   | 이송 요청 상태 관리 기능 | 시스템은 각 이송 요청의 진행 상태 및 상태 이력을 관리하고, 관리자가 이를 조회할 수 있어야 한다.[기능] 관리자 기능 관리자는 이송 요청 식별 번호를 통해 각 요청의 현재 진행 상태를 조회할 수 있어야 한다.관리자는 이송 요청의 결과와 상세 정보를 조회할 수 있어야 한다.시스템 기능 시스템은 각 이송 요청의 진행 상태를 추적할 수 있어야 한다.시스템은 이송 요청의 상태 변경 시각을 기록할 수 있어야 한다.시스템은 이송 요청의 상태 이력을 저장하고 관리할 수 있어야 한다.[비기능] 시스템은 이송 요청 상태 정보를 변경 1초 이내에 갱신할 수 있어야 한다.시스템은 상태 정보 조회 요청에 대해 1초 이내에 제공해야 한다.시스템은 다수의 이송 요청을 동시에 처리하더라도 안정적으로 상태를 관리할 수 있어야 한다. |   |
****
| SR-TR-02 | 이송 자원 운영 관리 |   | 시스템은 이송 자원의 상태를 관리하고, 이송 요청에 따라 적절한 자원을 배정·호출하며, 필요 시 충전 또는 대기 위치로 복귀시킬 수 있어야 한다. |   |
****

- 

- 

- 

- 
| SR-TR-02-01 |   | 이송 자원 상태 관리 기능 | 시스템은 각 이송 자원의 상태를 확인하고 관리할 수 있어야 한다.[기능]시스템은 각 이송 자원의 상태(유휴(충전 중+대기) / 작업 중 / 충전 필요(30%) / 사용 불가)를 확인할 수 있어야 한다.시스템은 이송 자원의 상태 변화를 감지하여 실시간으로 현재 자원 상태 정보에 반영할 수 있어야 한다.[비기능]시스템은 다수 이송 자원의 상태 변경 정보가 동시에 발생하더라도 상태 정보를 누락 없이 반영할 수 있어야 한다.시스템은 동일 이송 자원에 대해 상충되는 상태 정보가 동시에 저장되지 않도록 해야 한다. |   |
****

- 

- 

- 

- 
| SR-TR-02-02 |   | 이송 자원 배정 기능 | 시스템은 유휴 상태의 이송 자원을 이송 요청에 배정할 수 있어야 한다.[기능]시스템은 유휴 상태의 이송 자원을 식별하여 신규 이송 요청에 배정할 수 있어야 한다.시스템은 이송 자원 배정 시 자원의 상태, 동력 수준, 거리 등의 조건을 종합적으로 고려하여 적절한 자원을 선택해야 한다.시스템은 이송 자원 배정 완료 시 이송 상태를 [배정 전]에서 [출발 위치로 이동]으로, 자원 상태를 [유휴]에서 [작업 중]으로 즉시 변경해야한다.시스템은 동일한 이송 자원이 동시에 복수의 요청에 배정되지 않도록 관리해야 한다. |   |
****

- 

- 

- 
| SR-TR-02-03 |   | 이송 자원 충전 및 복귀 기능 | 시스템은 작업 종료 또는 저전력 상태의 이송 자원을 충전 위치 또는 대기 위치로 이동시킬 수 있어야 한다.[기능]시스템은 이송 자원의 동력 수준이 설정된 기준 이하로 떨어질 경우 해당 자원을 대기 위치로 이동시킬 수 있어야 한다.시스템은 작업이 종료된 이송 자원을 대기 위치로 복귀시킬 수 있어야 한다.시스템은 충전 또는 복귀 결과를 자원 상태에 반영할 수 있어야 한다. |   |
****

- 

- 

- 

- 
| SR-TR-02-04 |   | 출발 조건 확인 기능 | 시스템은 이송 작업 시작 전, 출발 위치에서 이송이 가능한 상태인지 검증하고 그 결과를 이송 요청 상태에 반영할 수 있어야 한다.[기능] 시스템은 출발 위치의 물품 종류 및 물품 식별 정보가 이송 요청 정보와 일치하는지 확인할 수 있어야 한다.시스템은 출발 조건 검증 결과를 이송 요청 상태에 반영할 수 있어야 한다.시스템은 출발 조건이 일정 시간 내 충족되지 않을 경우 timeout을 발생시키고 예외 상태로 처리해야 한다.[비기능]시스템은 출발 조건 검증을 1초 이내에 수행할 수 있어야 한다. |   |
****
| SR-TR-03 | 이송 수행 |   | 시스템은 배정된 이송 자원을 이용하여 물품을 출발 위치에서 도착 위치까지 이송하고, 인계 및 인수 결과를 반영할 수 있어야 한다. |   |
****

- 

  - 

- 

  - 

- 

  - 

  - 

  - 

- 

- 
| SR-TR-03-01 |   | 물품 인계, 인수 확인 기능 | 시스템은 출발 위치와 도착 위치에서 물품의 인계 및 인수 과정이 정상적으로 수행되었는지 검증하고, 그 결과를 이송 요청 상태에 반영할 수 있어야 한다.[기능] 출발 위치 (인계)시스템은 출발 위치에서 이송 대상 물품이 이송 자원에 정상적으로 인계되었는지 확인할 수 있어야 한다.도착 위치 (인수) 시스템은 도착 위치에서 이송 대상 물품이 정상적으로 인수되었는지 확인할 수 있어야 한다.공통 검증 시스템은 인계 및 인수된 물품의 종류와 수량이 이송 요청 정보와 일치하는지 검증할 수 있어야 한다.시스템은 인계 및 인수 결과를 이송 요청 상태에 반영할 수 있어야 한다.시스템은 인계 및 인수 과정에서 발생한 이벤트 및 결과를 로그로 기록해야 한다.[비기능] 시스템은 인계 및 인수 검증 결과를 1초 이내에 반영해야 한다.시스템은 물품 정보 및 수량 데이터의 무결성을 보장해야 한다. |   |
****

- 

- 

- 

- 

- 
| SR-TR-03-02 |   | 이동 기능 | 시스템은 이송 자원을 구역 간에 안전하게 이동시킬 수 있어야 한다.[기능]시스템은 이동 경로를 따라 이송 자원을 지정된 위치까지 제어할 수 있어야 한다.[비기능]시스템은 이송 중 충돌 위험이 없는 안전하고 유효한 경로를 따라 이동해야 한다.시스템은 지정된 도착 위치에 대해 위치 오차 ±5 cm 이내를 만족해야 한다.시스템은 지정된 도착 위치에 대해 자세 오차 ±5° 이내를 만족해야 한다.시스템은 이송 자원의 주행 속도를 직진 시 1.0 m/s 이하, 회전 시 0.5 m/s 이하로 제한해야 한다. |   |
****

- 

  - 

  - 

  - 

  - 

  - 

- 

  - 

  - 

  - 

- 

  - 

  - 

- 

- 

- 
| SR-TR-04 | 이송 수행 중 예외 처리 |   | 시스템은 이송 수행 중 발생하는 예외 상황을 감지하고, 적절한 처리 및 상태 전환을 수행할 수 있어야 한다.[기능] 예외 감지 시스템은 이송 자원 배정 실패출발 조건 검증 실패출발 위치에서 물품 인계 실패이동 중 장애 또는 이송 실패 상황도착 위치에서 물품 인수 실패예외 처리 및 상태 전환 시스템은 예외 상황 발생 시 이송 요청 상태를 대기, 재시도, 실패 상태로 전환할 수 있어야 한다.시스템은 예외 상황 발생 시 실패 사유를 기록할 수 있어야 한다.시스템은 기록된 실패 사유를 조회할 수 있어야 한다.알림 및 복구 시스템은 복구 불가능한 예외 상황 발생 시 관리자에게 알림을 제공할 수 있어야 한다.시스템은 시스템 전체 정지 상황 발생 시 진행 중인 이송 작업을 안전하게 종료할 수 있어야 한다.[비기능]시스템은 예외 상황을 1초 이내에 감지하고 처리할 수 있어야 한다.시스템은 특정 이송 요청에서 예외가 발생하더라도 다른 이송 요청 처리에는 영향을 주지 않아야 한다시스템은 다양한 예외 유형에 대해 확장 가능하도록 설계되어야 한다. |   |

### 
| [주물 품질 분류 및 제어] |
****
| SR-INS-01 | 주물 품질 검사 및 결과 관리 |   | 시스템은 완성된 주물의 품질을 검사하여 양품 또는 불량품으로 판정하고, 판정 결과에 따라 주물을 적절한 위치로 분류할 수 있어야 한다. |   |
****

- 

- 

- 

- 

- 

- 
| SR-INS-01-01 | 주물 품질 검증 기능 | 시스템은 완성된 주물의 품질을 검사하여 양품 또는 불량품으로 판정 할 수 있어야 한다. [기능]시스템은 검사 대상 주물을 인식할 수 있어야 한다.시스템은 주물의 외관, 형상 또는 정의된 품질 기준을 바탕으로 양품 여부를 판정할 수 있어야 한다.시스템은 양품 / 불량품의 개수를 셀 수 있어야 한다.[비기능]품질 검증 정확도는 95% 이상이어야 한다.시스템은 1초 이내에 검증 결과를 반환해야 한다.시스템은 양품 및 불량품 수량을 1초 이내 갱신해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
| SR-INS-01-02 | 검증 결과 관리 기능 | 시스템은 주물의 품질 판정 결과를 저장하고, 관련 통계 및 추적 정보를 관리할 수 있어야 한다.[기능]시스템은 각 주물의 검증 결과를 저장할 수 있어야 한다.시스템은 양품 및 불량품 수량을 누적 관리할 수 있어야 한다.시스템은 검증 시각 및 판정 이력을 기록할 수 있어야 한다.시스템은 불량 판정 시 실패 사유 또는 불량 유형을 기록할 수 있어야 한다.[비기능]시스템은 결과 데이터의 무결성을 보장해야 한다시스템은 실시간 조회가 가능하도록 결과 데이터를 갱신해야 한다. |   |
****

- 

- 

- 

- 

- 

- 

- 
| SR-INS-02 | 주물 분류 실행 기능 |   | 시스템은 검증 결과에 따라 양품 주물과 불량품 주물을 서로 다른 위치로 분류할 수 있어야 한다.[기능]시스템은 검증 결과를 입력받아 분류 동작을 결정할 수 있어야 한다.시스템은 양품 판정 시 주물을 양품 적재 위치로 분류할 수 있어야 한다.시스템은 불량품 판정 시 주물을 불량품 적재 위치로 분류할 수 있어야 한다.시스템은 분류 장치의 상태를 제어할 수 있어야 한다.[비기능]분류 정확도는 99% 이상이어야 한다.시스템은 검증 완료 후 1초 이내에 분류 준비 상태가 되어야 한다.시스템은 다음 검증 결과가 입력될 때까지 현재 분류 상태를 안정적으로 유지해야 한다. |   |
****

- 

- 

- 
| SR-INS-03 | 분류 장치 제어 기능 |   | 시스템은 분류 결과에 따라 주물의 배출 방향을 결정할 수 있어야 한다.[기능]시스템은 양품 판정 시 분류 장치를 양품 배출 위치로 제어할 수 있어야 한다.시스템은 불량품 판정 시 분류 장치를 불량품 배출 위치로 제어할 수 있어야 한다.시스템은 분류 장치의 현재 각도 또는 상태를 확인할 수 있어야 한다. |   |

### ****
| [컨베이어 이송 제어] |
****
| SR-CONV-01 | 컨베이어 운전 제어 |   | 시스템은 주물을 검사 구간까지 이송하기 위해 컨베이어 벨트를 구동, 정지 및 제어할 수 있어야 한다. |   |
****

- 

- 

- 

- 

- 
| SR-CONV-01-01 |   | 컨베이어 구동 및 정지 기능 | 시스템은 입력된 명령에 따라 컨베이어 벨트를 구동하거나 정지할 수 있어야 한다.[기능] 시스템은 Start 명령에 따라 컨베이어 벨트를 구동할 수 있어야 한다.시스템은 Stop 명령에 따라 컨베이어 벨트를 정지할 수 있어야 한다.시스템은 주물 존재 여부에 따라 벨트 구동 여부를 판단할 수 있어야 한다.시스템은 벨트의 현재 구동 상태를 확인할 수 있어야 한다.[비기능]시스템은 구동 및 정지 명령에 대해 1초 이내에 반응해야 한다. |   |
****

- 

- 

- 

- 
| SR-CONV-01-02 |   | 이송 속도 제어 기능 | 시스템은 검사 공정 조건과 Takt Time을 고려하여 컨베이어 벨트의 이송 속도를 제어할 수 있어야 한다.[기능]시스템은 속도 설정값을 입력받을 수 있어야 한다.시스템은 주물의 종류 또는 Takt Time에 따라 벨트 속도를 제어할 수 있어야 한다.시스템은 현재 벨트 속도 상태를 확인할 수 있어야 한다.[비기능]시스템은 이송 속도를 1~100% 범위 내에서 설정 가능해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
| SR-CONV-01-03 |   | 운전 모드 전환 기능 | 시스템은 생산 및 유지보수 상황에 따라 컨베이어 벨트의 운전 모드를 전환할 수 있어야 한다.[기능] 시스템은 Auto Mode와 Manual Mode를 전환할 수 있어야 한다.시스템은 생산 중에는 Auto Mode를 사용할 수 있어야 한다.시스템은 고장 점검, 테스트 또는 수동 조작이 필요한 경우 Manual Mode를 사용할 수 있어야 한다.시스템은 현재 운전 모드를 표시할 수 있어야 한다.[비기능]시스템은 모드 전환 시 현재 상태 정보를 유지하거나 안전한 초기 상태로 전환해야 한다.시스템은 모드 전환 중 오동작이 발생하지 않도록 해야 한다. |   |
****
| SR-CONV-02 | 검사 구간 제어 |   | 시스템은 주물이 검사 구간에 도착했는지 감지하고, 검사 조건에 따라 정지, 신호 전달 및 후속 이송을 제어할 수 있어야 한다. |   |
****

- 

- 

- 

- 
| SR-CONV-02-01 |   | 검사구간 도착 감지 및 정지 기능 | 시스템은 주물이 검사 구간에 도착했는지 감지하고, 필요한 경우 컨베이어 벨트를 정지시킬 수 있어야 한다.[기능]시스템은 주물이 검사 구간에 도착 신호를 수신하고 벨트를 정지할 수 있어야 한다.시스템은 검사 스킵 조건에 따라 정지 없이 후속 구간으로 이송할 수 있어야 한다.[비기능]시스템은 도착 센서 감지 후 0.5초 이내에 벨트를 정지해야 한다.시스템은 검사 구간 정지 위치에 대해 위치 오차 ±5cm 이내를 만족해야 한다. |   |
****

- 

- 

- 

- 
| SR-CONV-02-02 |   | 검사 시스템 연동 기능 | 시스템은 검사 시스템 및 관제 시스템과 연동하여 컨베이어 이송 상태와 검사 수행 조건을 공유할 수 있어야 한다.[기능] 시스템은 검사 구간 도착 완료 신호를 상위 시스템 또는 검사 시스템에 전달할 수 있어야 한다.시스템은 검사 결과 또는 검사 가능 여부에 따라 벨트 정지 또는 재이송 동작을 수행할 수 있어야 한다.시스템은 상위 관제 시스템으로부터 구동, 정지 및 상태 관련 명령을 수신할 수 있어야 한다.시스템은 단독 운전과 관제 연동 운전을 모두 지원할 수 있어야 한다. |   |
****
****

- 

- 
| SR-CONV-02-03 | 안전 및 예외 정지 관리 | 비상정지 및 예외 정지 기능 | 시스템은 비상 상황 또는 정의된 예외 조건 발생 시 컨베이어 벨트를 안전하게 정지시키고, 정지 후 재기동 전 안전 상태를 관리할 수 있어야 한다.[기능] 컨베이어 벨트는 시스템이 보낸 비상정지 신호를 수신할 수 있어야 한다.컨베이어 벨트는 비상정지 신호 입력 시 즉시 벨트를 정지할 수 있어야 한다. |   |

### 
| [적재 및 창고 관리] |
****
****
| SR-STO-01 | 적재 전략 및 위치 최적화 |   | 시스템은 제품 특성과 물류 빈도 데이터를 분석하여 공간 활용률과 작업 동선을 최적화하는 지능형 위치 할당할 수 있어야 한다 |   |
****

- 

- 

- 

- 

- 

- 
| SR-STO-01-01 |   | 최적 위치 할당 기능 | 시스템은 제품 특성과 물류 흐름을 고려하여 공간 효율과 작업 효율을 극대화할 수 있는 적재 위치를 산출할 수 있어야 한다.[기능]시스템은 출고 빈도 기반으로 제품을 ABC 등급으로 분류할 수 있어야 한다.시스템은 출고 빈도,제품 종류, 동선, 거리 등을 고려하여 적재 위치를 결정할 수 있어야 한다.시스템은 위치 할당 요청에 대해 최적 위치를 반환할 수 있어야 한다.[비기능]응답성: 위치 할당은 1초 이내 수행되어야 한다.공간 효율성: 창고 공간 활용률은 90% 이상을 목표로 해야 한다.확장성: 제품군 및 적재 구역 확장 시 추가 수정 없이 대응 가능해야 한다. |   |
****

- 

- 

- 

- 
| SR-STO-01-02 |   | 제품 재배치 기능 | 시스템은 공간 효율 및 작업 효율을 향상시키기 위해 기존 적재된 제품의 위치를 변경하거나 교환(Swap)할 수 있어야 한다.[기능]시스템은 재배치 필요성을 감지하면 재배치 대상 제품의 현재 위치 정보를 확인하고 최적 위치 할당 기능을 호출할 수 있어야 한다.시스템은 목적지가 이미 점유된 경우 대체 위치를 할당하거나 제품 간 Swap 작업을 수행할 수 있어야 한다.[비기능]응답성: 재배치 요청 후 위치 할당까지 1초 이내 수행안정성: Swap 중 데이터 유실이 없어야 하며, 실패 시 이전 상태로 복구 가능해야 한다. |   |
****
| SR-STO-02 | 적재 실행 및 예외 관리 |   | 시스템은 결정된 위치로 제품을 물리적으로 이동시키는 과정을 제어하고, 이 과정에서 발생하는 다양한 돌발 상황과 오류를 감지하여 대응할 수 있어야 한다 |   |
****

- 

  - 

- 

- 

- 

- 

- 

- 
| SR-STO-02-01 |   | 제품 적재 기능 | 시스템은 식별된 제품을 목표 위치에 안전하게 적재하고, 작업 상태를 실시간으로 관리할 수 있어야 한다.[기능] 시스템은 제품 정보를 식별할 수 있어야 한다.제품 ID, 규격, 수량시스템은 제품을 지정된 위치에 적재할 수 있어야 한다.시스템은 기존 물품과의 간섭을 방지하기 위해 안전 거리를 유지할 수 있어야 한다.시스템은 적재 작업 상태(입고 시작 / 적재 중/적재 완료 / 장애 발생)를 실시간으로 갱신할 수 있어야 한다.시스템은 적재 완료 시 시스템 및 관리자에게 알림을 제공할 수 있어야 한다.데이터베이스 연결이 일시적으로 끊겨도 로컬 데이터를 활용해 최소한의 적재 작업은 지속 가능해야 한다.[비기능]가상 시스템상의 위치 데이터와 실제 물리적 적재 위치가 오차 없이 일치해야 한다. |   |
****

- 

- 

- 

- 
| SR-STO-02-02 |   | 적재 예외 처리 기능 | 시스템은 적재 및 재배치 과정에서 발생하는 물리적 및 논리적 오류를 감지하고, 프로세스를 중단하거나 우회할 수 있어야 한다.[기능] 시스템은 시스템 데이터와 실제 현장의 점유 상태가 일치하지 않는 경우를 즉시 감지할 수 있어야 한다.(비어있음 ↔ 실제 점유 불일치)시스템은 공간 부족 또는 규격 미달,식별 불가 제품 발생 시 프로세스를 중단하고 즉시 관리자에게 알릴 수 있어야 한다.시스템은 감지된 예외 상황을 관리자에게 알림으로 제공할 수 있어야 한다.[비기능]신뢰성: 예외 처리 과정에서 기존 데이터는 보호되어야 한다. |   |
****

- 

- 

- 

- 

- 
| SR-STO-03 | 실시간 적재 지도 (Map) 모니터링 제어 |   | 시스템은 창고 내부의 모든 적재 공간 상태를 데이터화하여 관리할 수 있어야 한다.[기능] 시스템은 각 적재 위치의 상태를 관리할 수 있어야 한다.(비어있음 / 점유 / 예약 / 작업중 / 사용불가 / 상태불일치 / 할당제한)시스템은 적재 및 이동 이벤트 발생 시 지도상의 상태 데이터를 즉시 갱신해야 한다.시스템은 모든 상태 변경 이력을 로그로 기록할 수 있어야 한다.[비기능]데이터 일치성: 물리적 상태와 시스템 상태는 항상 일치해야 한다.응답성: 상태 변경 발생 시 1초 이내 반영되어야 한다. |   |

### ****
| [출고 관리] - 구분 |
****
| SR-OUT-01 | 출고 관리 기능 |   | 시스템은 출고 지시 생성부터 출고 수행, 이력 관리까지 전 과정을 통합적으로 관리하여 정확하고 효율적인 출고를 지원해야 한다. |   |
****

- 

- 
| SR-OUT-01-01 |   | 출고 지시서 생성 기능 | 관리자는 원격으로 출고 지시서를 생성하고, 출고 조건을 설정할 수 있어야 한다.[기능]관리자는 제품 종류/출고 일자/납품 회사/출고 수량를 지정할 수 있어야 한다.시스템은 출고 지시서를 생성하고 식별 ID를 부여할 수 있어야 한다.. |   |
****

- 

  - 

  - 

  - 

- 

  - 

- 

  - 

  - 

- 

- 
| SR-OUT-01-02 |   | 출고 수행 기능 | 시스템은 출고 지시서를 기반으로 제품 식별, 수량 검증, 위치 조회 및 이송을 요청하여 출고를 완료할 수 있어야 한다.[기능]준비 및 검증 시스템은 출고 대상 제품을 식별할 수 있어야 한다.시스템은 출고 대상 제품의 수량을 검증할 수 있어야 한다.시스템은 적재 위치 및 실제 재고를 조회할 수 있어야 한다.이송 요청 시스템은 출고를 위한 이송을 요청할 수 있어야 한다.완료 처리 시스템은 출고 완료 시 재고를 차감할 수 있어야 한다.시스템은 출고 완료 상태를 시스템에 반영할 수 있어야 한다.[비기능]시스템은 정의된 출고 정책(LIFO)을 적용할 수 있어야 한다.시스템은 물리적 재고와 시스템 재고 간 일치성을 유지해야 한다. |   |
****

- 

- 

- 

- 
| SR-OUT-02 | 출고 이력 관리 기능 |   | 시스템은 출고 과정에서 발생한 정보를 기록하고, 이를 조회 및 추적할 수 있어야 한다.[기능]사용자가 출고 이력을 조회할 수 있어야 한다.시스템은 출고 이력을 저장할 수 있어야 한다.시스템은 출고 제품, 수량, 시간 등의 정보를 기록할 수 있어야 한다.[비기능]시스템은 이력 데이터를 안정적으로 저장해야 한다. |   |

### ****
| [후처리 공정] |
****
| SR-POST-01 | 후처리 공정 운영 및 흐름 제어 |   | 시스템은 작업자가 수행하는 후처리 공정과 청소 작업을 지원하고, 공정 상태를 관리하며, 컨베이어 및 적재 시스템과 연동하여 작업 흐름을 제어할 수 있어야 한다. |   |
****
****

- 

- 

- 

- 
| SR-POST-01-01 |   | 후처리 작업(수작업 기반) | 작업자는 후처리 구역에서 제품 후처리 작업을 수행하며, 시스템은 해당 작업 상태를 관리할 수 있어야 한다.[기능]시스템은 후처리 작업 상태(후처리 대기 / 후처리 작업 중 / 후처리 완료)를 관리할 수 있어야 한다.시스템은 작업 완료 여부를 입력 또는 감지하여 상태를 갱신할 수 있어야 한다.[비기능]시스템은 후처리 작업 상태를 실시간으로 갱신해야 한다.시스템은 작업 과정에서 오류 또는 누락이 발생하지 않도록 상태 일관성을 유지해야 한다. |   |
****
| SR-POST-01-02 |   | 청소 요청 | 시스템은 후처리 공정이 끝나면 청소를 요청할수있도록 해야한다. |   |

### 
| [청소 공정] |
****
| SR-CLN-01 | 청소 스케줄링 및 실행 |   | 시스템은 공장 전체적으로 청소를 할 수 있어야 한다. |   |
****

- 

- 

- 
| SR-CLN-01-01 |   | 구역별 맞춤 청소 관리 | [기능]공정별(주조/이송/적재) 특성에 따른 정기/수시 청소 작업 생성오염도가 높은 구간(주조 구역 등)에 대한 집중 청소 모드 수행[비기능]설정된 청소 대상 면적 대비 실제 청소 완료율 70% 이상 달성 |   |
POST: 후처리

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

### Terminology (3407906)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407906
**최종 수정**: v36 (2026-04-18 sync)

통일된 언어 사용 지향을 위해 용어 정리해놓았습니다. 문서 작성시에 이 페이지에 정리된 용어 사용 부탁드립니다!

****
****
****
****
| 한글 | 영어 | 약어 | 설명 - 프로젝트 기준 |
|---|---|---|---|
****
| 관제 | FMS |   | 다수의 로봇의 작업 할당 및 경로를 제어하는 시스템 |
| 자율주행로봇 | AMR | AMR |   |
| 로봇팔 | Robot Arm | RA |   |
| 컨베이어 벨트 | Conveyor |   |   |
| 로딩 | Loading |   | 컨베이어벨트에 반입 |
| 언로딩 | Unloading |   | 컨베이어벨트에 반출 |
| 포토 센서 | Photo Sensor |   | 맨홀 감지 역할 |
| 고유번호 | Identifier |   |   |
| 이름 | Name |   |   |
| 상태 | Status |   |   |
| 메시지 |   |   |   |
| 요청 |   |   |   |
| 주문 |   |   |   |
| 현재 |   |   |   |
| 목적지 |   |   |   |
| 출발지 |   |   |   |
| 시간 |   |   |   |
| 작업자 |   |   |   |
| 자원 |   |   |   |
****
| 생산      (process) | Manufacture |   | 주조부터 검사까지 모든 과정 |
| 주조 | Casting / cast |   | 금속을 녹여 주형에 부어 형상을 만드는 공정 |
| 주형제작 | Mold Making |   | 맨홀을 만들기 위한 틀을 제작하는 과정 |
| 주탕 | Pouring |   | 용탕을 주형에 붓는 과정 |
| 패턴 | Pattern |   | 주형을 만들기 위한 원형 모델 |
| 냉각 | Cooling |   | 용탕이 식으면서 고체로 변하는 과정 |
| 탈형 | Demolding | DM | 냉각된 맨홀에서 주형을 제거하는 과정 |
| 후처리 | PostProcessing |   | 맨홀의 표면을 다듬고 불필요한 부분을 제거하는 과정 |
| 검사 | Inspection | INSP | 제품의 품질을 확인하는 과정 |
| 작업중 |   |   |   |
| 검사 |   |   |   |
| 후처리 |   |   |   |
| 재질 |   |   |   |
| 백분율 |   |   |   |
| 설비 |   |   |   |
****
| 이송      (process) | Transport |   | AMR이 물건을 가지고 이동하는 모든 과정 |
| 상차 | Loading / load | LD | 로봇팔이 AMR위에 맨홀을 올리는 행위 |
| 하차 | Unloading / unload | DLD | 로봇팔/사람이 AMR위에서 맨홀을 내리는 행위 |
| 이송 |   |   |   |
| 배터리 |   |   |   |
|   |   |   |   |
****
| 적재       (process) | Stacking |   | 적치와 출고과정을 통칭함 |
| 적치 | Putaway | PUT | ​적치하는 process / 맨홀을 보관 랙에 넣는 행위 |
| 출하용으로 꺼내는 작업 |   | PICK | Putaway의 반대말로, WMS 표준으로 보관 위치에서 출하용으로 꺼내는 작업을 의미 |
| 보관 |   |   |   |
| 임시 대기 |   |   | 다음 공정(여기선 출하)을 위해 임시로 모아두는 구역 |
| ​출고 | Shipping | SHIP | 출고하는 process |
| 파지 |   |   | 로봇arm이 무언가를 집는 행위 |
| 보관 선반 | Storage Rack |   | 맨홀을 보관하는 랙 |
| 슬롯형 보관함 | Slotted storage |   | AMR 위에 있는 보관함 |
| 수량 | Quantity |   |   |
****
| 주물 | Casting Product |   |   |
| 양품 | Good product |   |   |
| 불량품 | defect (n) / defective (adj) product |   |   |
| 제품 |   |   |   |
| 패턴 |   |   |   |
| 기타 (공통/범용) |   |   |   |
| 코드 | code |   |   |
| 카테고리 |   |   |   |
| 옵션 |   |   |   |
| 주문 |
|   | Purchase Order | PO | 고객의 입장에서 고객 발주 ERP 표준 |
| (발주를) 수주 (제조사 입장), |   | SO, RCVD | 제조사가 수주, ERD entity는 SO, 상태표현시에는 RCVD |
| 발주 (행위) | Order Placement |   |   |
|   |   |   |   |

# 주조 (Casting) 
“주조 공정은 용탕을 주형에 주탕한 뒤 냉각·탈형을 거쳐 제품을 만드는 과정이며, 특히 주탕과 물류 과정은 자동화가 가장 필요한 핵심 구간입니다.”

- 
주조 (Casting): 금속을 녹여 주형에 부어 형상을 만드는 공정

- 
용탕 (Molten Metal): 녹은 금속 상태

- 
재료: 주형을 제작하기 전 상태

- 
조형(Molding): 틀을 만드는 행위 (Process)

- 
주형 (Mold): 재료에서 만들어진 금속을 붓는 틀. 쇳물을 붓는 ‘형’의 통칭. 모래(사형), 금속(금형), 석고, 세라믹 등 다양한 재료로 만들 수 있다.

  - 
금형 (Die/Metal Mold): 금속을 깍아 제작한 고강성의 틀이다. 영구적으로 사용 가능함.

  - 
사형 (/Metal Mold): 모래로 만든 주형은 제품을 꺼낼 때 틀을 파괴해야 하므로 1회성

- 
주형사 (molding sand): 주조에서 금속을 부어 모양을 만들기 위해 사용하는 모래 

  - 
일반 모래는 그냥 흩어지느데, 모양 유지 + 고온 견딤 + 부서짐 조절 가능 (탈형 가능)의 특징을 가져야 한다. 

  - 
구성 요소:

    - 
모래 (Silica sand)

      - 
기본 골격

    - 
결합제 (Binder)

      - 
점토(벤토나이트) 등 → 모양 유지

    - 
수분 (Water)

      - 
점착력 조절

    - 
(옵션) 첨가제

      - 
표면 품질, 강도 개선

- 
주물 (Casting Product): 최종 결과물

- 
용해 (Melting): 금속을 고온에서 녹여 액체 상태로 만드는 과정

- 
주괴 (Ingot): 용해로에 투입하여 용탕을으로 만들어지는 것

- 
용해로 (Melting Furnace): 금속 등을 녹이는 설비를 총칭

- 
합금 (Alloy): 두 가지 이상의 금속(또는 금속 + 비금속)을 혼합한 재료

- 
슬래그 (Slag): 용해 과정에서 발생하는 불순물로, 표면에 떠올라 제거됨

- 
주형 제작 (Mold Making): 주물을 만들기 위한 틀을 제작하는 과정

  - 
패턴 (Pattern): 주형을 만들기 위한 원형 모델

  - 
코어 (Core): 3D 형태의 복잡한 주물 내부의 빈 공간을 형성하기 위한 구조물

  - 
사형 주조 (Sand Casting): 모래를 이용해 주형을 만드는 방식

  - 
금형 주조 (Die Casting): 금속 금형을 사용하는 고정밀 주조 방식

- 
주탕 시스템 (Pouring System): 용탕이 주형 내부로 흐르는 경로 시스템

  - 
주탕 (Pouring): 용탕을 주형에 붓는 과정

  - 
도가니 (Crucible):  금속을 녹이는 용기

    - 
용해로 내부에서 금속을 녹이는 역할. 고정 또는 반고정 형태

  - 
래들 (Ladle): 용탕을 운반하고 주입하는 용기

    - 
용해로 외부에서 용탕을 옮기고 붓는 역할. 이동 가능한 형태

  - 
탕구 (Sprue): 용탕이 처음 들어가는 수직 통로

  - 
러너 (Runner): 용탕을 여러 방향으로 분배하는 수평 통로

  - 
게이트 (Gate): 실제 제품 형상으로 용탕이 들어가는 입구

  - 
게이트 시스템 (Gating System): 용탕 흐르는 통로

  - 
압탕 (Riser): 수축 보정용 저장 공간, 응고 시 수축을 보완하기 위한 용탕 저장부

    - 
금속이 굳으면서 수축할 때 발생하는 부피 감소를 보완하기 위해 용융 금속을 추가 공급하는 조장소이다. 보통 압력을 가해서 수축공 (shinkage cavity) 발생을 방지하고 쇳물의 압력으로 조직을 치밀하게 하며 가스를 배출하는 역할을 한다.

- 
냉각/탈형

  - 
냉각/응고 (Cooling / Solidification): 용탕이 식으면서 고체로 변하는 과정

  - 
탈형(Demolding): 냉각된 주물에서 주형을 제거하는 과정

- 
후처리 (Postprocessing): 주물의 표면을 다듬고 불필요한 부분을 제거하는 과정

  - 
페틀링 (Fettling): 주물 표면 정리 작업

  - 
디버링 (Deburring): 날카로운 모서리 제거

  - 
샷 블라스트 (Shot Blasting): 표면 청소, 표면의 불순물 제거 및 마감 처리

- 
검사 (Inspection): 제품의 품질을 확인하는 과정

  - 
외관 검사 (Visual Inspection): 눈으로 결함을 확인

  - 
비파괴 검사 (NDT, Non-Destructive Testing): X-ray, 초음파 등을 이용해 내부 결함 검사

- 
결함 (Defect): 주조 과정에서 발생하는 품질 문제

  - 
기공 (Porosity): 내부에 기포나 구멍이 생기는 현상

  - 
수축 결함 (Shrinkage): 응고 과정에서 부피 감소로 발생하는 결함

  - 
콜드 셧 (Cold Shut): 주조 공정에서 용융된 금속의 두 흐름이 서로 만날 때, 온도가 낮아 완전히 융합되지 못하고 표면이나 내부에 선 모양의 이음새나 틈새가 생기는 결함을 말합니다. 주로 주형 내 유동성 부족, 낮은 쇳물 온도, 빠른 응고로 인해 발생

  - 
미스런 (Misrun): 용탕이 주형을 끝까지 채우지 못한 현상

- 
설비 및 자동화 관련

  - 
로봇 셀 (Robot Cell): 로봇을 중심으로 구성된 작업 단위 시스템

  - 
AMR (Autonomous Mobile Robot): 자율주행 기반 물류 이동 로봇

  - 
비전 시스템 (Vision System): 카메라 기반 인식 및 검사 시스템

  - 
공정 모니터링 (Process Monitoring): 센서를 통해 공정 상태를 실시간으로 확인하는 시스템

  - 
택트 타임 (Takt Time): 요구하는 생산 목표를 달성하기 위해 제품 하나를 생산하는데 필요한 시간

# 물류 (Logistics) 
“물류는 원자재, 반제품, 완제품을 공급망 전반에서 이동·보관·관리하는 과정이며, 특히 이송·적치·재고 동기화 구간은 자동화가 핵심이 되는 영역이다.”

- 
물류 (Logistics): 제품 및 자원의 흐름(이동·보관·처리)을 효율적으로 관리하는 활동

- 
공급망 (Supply Chain): 원자재 → 생산 → 유통 → 고객까지 이어지는 전체 흐름

- 
물류 자동화 (Logistics Automation): 인력 대신 시스템·로봇·소프트웨어로 물류 작업을 수행하는 것

- 
물류 최적화 (Logistics Optimization): AI, 자동화 기술, 데이터 분석을 활용해 공급망 전반(조달, 생산, 보관, 운송)의 비용을 최소화하고 효율성을 극대화하는 과정

- 
슬로팅 (Slotting): 창고 내 상품의 배치/적재를 최적화 하기 위한 전략적 재고 관리 프로세스

- 
물류(Logistics) 용어

  - 
적치(putaway): 입고된 원자재나 제품을 창고 내 지정된 위치에 보관하는 과정

  - 
출고 (Shipping / Outbound): 창고에서 제품을 고객 또는 다음 공정으로 보내는 과정

  - 
이송 (Transport / Transfer): 물류 거점 간 또는 공정 간 제품을 이동시키는 작업

  - 
적치 (Storage / Put-away): 제품을 지정된 위치에 보관하는 과정

  - 
파지 (Picking): 주문에 맞게 필요한 제품을 선택·수집하는 작업

  - 
패킹 (Packing): 제품을 출하를 위해 포장하는 과정

  - 
검수 (Checking): 입고/출고 검증 단계

  - 
반품 (Return): 고객 또는 공정에서 제품이 다시 돌아오는 행위

  - 
재고 (Inventory / Stock): 현재 보유 중인 자재 및 제품의 수량

  - 
재고 동기화 (Inventory Synchronization): 실제 재고와 시스템(WMS)의 데이터를 일치시키는 과정

  - 
Cross Docking: 입고 후 보관 없이 바로 출고로 연결하는 방식

- 
물류 관리 시스템

  - 
WMS (Warehouse Management System): 창고 내 재고 및 작업 흐름을 관리하는 시스템

  - 
FMS (Fleet Management System): 다수의 로봇/AGV/AMR의 작업 할당 및 경로를 제어하는 시스템

- 
AMR (Autonomous Mobile Robot): 자율적으로 경로를 판단하여 이동하는 물류 로봇

- 
AGV (Automated Guided Vehicle): 정해진 경로를 따라 이동하는 자동 운반 장치

- 
컨베이어 (Conveyor): 제품을 일정 경로로 연속적으로 이동시키는 설비

- 
Scan Lane: 이동 중 바코드/RFID를 통해 재고를 실시간 인식하는 구간

- 
Golden Zone: 작업 효율이 가장 높은 적치 위치 (허리~가슴 높이 구간)
 [스마트공장 수준별 5단계 정의](https://blog.naver.com/cochain_ltd/222086733907)

### HW_Research (8552537)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8552537
**최종 수정**: v2 (2026-04-13 sync)

#### AMR (7438566)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7438566
**최종 수정**: v20 (2026-04-19 sync)

[AMR Test videos](https://drive.google.com/drive/u/3/folders/10c74G67AuYK0-SMn9AxSpje51DOSSGYU)

#### Conveyor (7700525)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7700525
**최종 수정**: v33 (2026-04-19 sync)

#### 컨베이어 벨트 비전 검사 & 상위 통신 연동 테스트 (16580646)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/16580646
**최종 수정**: v21 (2026-04-19 sync)

# Conveyor Belt Controller — Final Wiring Diagram
**구성**: ESP32 DevKitC V4 + L298N + TOF250 (ASCII UART) × 2 + JGB37-555 Motor
✅ **Verified Working** — 2026-04-06 (firmware v3.0.0)
각 센서에서 **White 와이어만 데이터를 전송**합니다 (ASCII UART @ 9600 baud). Yellow / Blue / Green은 **연결하지 않습니다 (NC)**.

## 1. 시스템 개요

| 항목 | 내용 |
|---|---|
| MCU | ESP32 DevKitC V4 |
| 모터 드라이버 | L298N (Dual H-Bridge) |
****
| 거리 센서 | Taidacent TOF250 × 2 (Entry / Exit) |
| 모터 | JGB37-555 DC 12V 167RPM |
****
****``
| 센서 통신 | ASCII UART @ 9600 baud (SERIAL_8N1) |
| 전원 | DC 12V (모터), USB 5V (ESP32 본체) |
| 펌웨어 버전 | v3.0.0 (검증 완료 2026-04-06) |
``
| Arduino FQBN | esp32:esp32:esp32doit-devkit-v1 |

## 2. 배선표

****
****
****
****
| 명칭 | 센서 | 센서 브라켓 | 설치 이미지 |
|---|---|---|---|
| 이미지 |   |   |   |

### 2.1 ★ TOF250 센서 배선 (각 센서 공통)
핵심: **6선 중 GND / VIN / White만 사용**합니다. 나머지 3선(Yellow / Blue / Green)은 PCB에 신호가 없으므로 연결하지 않습니다.

| 와이어 색상 | 기능 | 연결 | 비고 |
|---|---|---|---|
| Black (검정) | GND | ESP32 GND | 두 센서 공유 |
****
| Red (빨강) | VIN | ESP32 3.3V | 두 센서 공유 |
****
| Yellow (노랑) | — | NC (미연결) | 신호 없음 |
****
****
****
****
| White (백색) ★ | UART TX | TOF1 → GPIO 16, TOF2 → GPIO 17 | 유일한 데이터 와이어 |
****
| Blue (파랑) | — | NC (미연결) | 신호 없음 |
****
| Green (녹색) | — | NC (미연결) | 신호 없음 |
펌웨어 매핑 (`conveyor_controller.ino`):

### 2.2 Motor Control (ESP32 → L298N → DC Motor)

| ESP32 핀 | L298N 핀 | 설명 |
|---|---|---|
``****
| GPIO 25 | ENA | PWM 속도 제어 (1 kHz, 8-bit, MOTOR_SPEED = 180) — ENA 점퍼 캡 제거 필수 |
| GPIO 26 | IN1 | 방향 A (HIGH = forward) |
| GPIO 27 | IN2 | 방향 B (HIGH = reverse) |
| GND | GND | ESP32 + 12V PSU와 공통 GND |
| — | OUT1 / OUT2 | → JGB37-555 모터 적/흑 리드선 |
PWM 초기화:

### 2.3 Power Supply

| From | To | 설명 |
|---|---|---|
| DC 12V (+) | L298N +12V | 모터 전원 (외부 어댑터) |
| DC 12V (−) | L298N GND ⟷ ESP32 GND | 모든 디바이스 공통 GND |
| USB | ESP32 | PC / RPi5에서 USB로 ESP32 + 센서 전원 공급 |

## 3. 와이어 색상 범례

| 색상 | 용도 |
|---|---|
| 🔴 Red | VIN / +12V |
| ⚫ Gray/Black | GND (공통) |
****
| ⚪ White ★ | UART TX (유일한 데이터 와이어) |
| 🟠 Orange | Motor PWM/DIR |
| 🚫 Yellow / Blue / Green | NC (연결하지 않음) |

## 4. ★ Critical Protocol Discovery (2026-04-06)
이 **Taidacent TOF250** 모듈(AliExpress listing `1005010253988126`)은 대부분의 온라인 문서가 시사하는 것과 달리 **I2C도, 바이너리 UART 프레이밍도 사용하지 않습니다**.

- 
**실제 프로토콜**: ASCII 텍스트, **9600 baud**

- 
**포맷**: 거리값(mm) + CR/LF 종결자

- 
**데이터 와이어**: **White 와이어 1개만 활성** — Yellow, Blue, Green은 PCB 상에 패드가 5개뿐이며 신호가 출력되지 않음

- 
**펌웨어 파싱**: 바이트 단위로 누적하여 `\r` 또는 ` ` 만나면 `String.toInt()`로 파싱 (바이너리 프레임 파싱 ❌)
⚠️ v1/v2 문서에서 I2C(VL53L0X) 기반으로 작성되었던 내용은 **모두 폐기**합니다. 실제 모듈은 ASCII UART 전용입니다.

## 5. Conveyor State Machine (firmware v3.0.0)

| 항목 | 코드 상수 | 값 |
|---|---|---|
``
| Debounce | DEBOUNCE_MS | 500 ms (양 센서, 연속 감지 필요) |
````
| Detection range | DETECT_MIN_MM–DETECT_MAX_MM | 5–80 mm (이외 거리는 무시) |
``
| Inspection wait | STOP_WAIT_MS | 5 000 ms (STOPPED 상태) |
``
| Post-run drive | POST_RUN_MS | 2 000 ms (POST_RUN) |
``
| Safety timeout | CLEAR_TIMEOUT_MS | 5 000 ms (CLEARING) |
``
| Status report 주기 | REPORT_MS | 300 ms (주기 JSON 출력) |
``
| Motor PWM duty | MOTOR_SPEED | 180 / 255 |

## 6. Serial Channels (두 개의 독립 채널)
⚠️ ESP32는 **2개의 서로 다른 baudrate**로 동시에 동작합니다. 두 채널을 혼동하지 마세요.

### 6.1 ① USB Serial (ESP32 ↔ PC) — **115200 baud**
사용자 명령 입력 및 JSON 이벤트/상태 로그 출력 (Arduino IDE Serial Monitor 또는 RPi5 에이전트가 사용).

| 명령 | 동작 |
|---|---|
````
| start / stop | 모터 강제 제어 |
``
``
| reset | IDLE 복귀, objCount 초기화 |
````
| sim_entry / sim_exit | 센서 감지 시뮬레이션 (실물 객체 없이 테스트) |
``
| status | 현재 상태 JSON 즉시 응답 요청 |

### 6.2 ② TOF250 UART (Sensor → ESP32) — **9600 baud**
각 센서가 ESP32로 거리값을 단방향 전송 (ASCII 형식 `"NNN\r "`). 양방향 통신 없음 — TX만 사용.

| 센서 | ESP32 핀 | UART 번호 | 활성 와이어 |
|---|---|---|---|
| TOF1 (Entry) | GPIO 16 | UART1 RX | White |
| TOF2 (Exit) | GPIO 17 | UART2 RX | White |

### 6.3 출력 JSON 예시
부팅 메시지:
주기 상태 (300 ms 간격):
이벤트:

## 7. ESP32 핀 요약

| GPIO | 기능 | 연결 대상 |
|---|---|---|
| 3V3 | Power | TOF1 VIN, TOF2 VIN |
| GND | Ground | TOF1/TOF2 GND, L298N GND, 12V PSU (−) |
| GPIO 16 | UART1 RX (TOF1) | TOF1 White |
| GPIO 17 | UART2 RX (TOF2) | TOF2 White |
| GPIO 25 | PWM (ENA) | L298N ENA |
| GPIO 26 | DIR A (IN1) | L298N IN1 |
| GPIO 27 | DIR B (IN2) | L298N IN2 |

## 8. ✅ Verification Log
**2026-04-06**: 실제 센서 + 모터 검증 완료.

- 
실제 객체로 **2 사이클 연속 성공**

- 
모터 회전 정상 동작 확인

- 
TOF1 readings: idle 190 mm → 객체 감지 시 5 mm

- 
TOF2 readings: idle 208 mm → 객체 감지 시 6 mm

- 
State transition 전 구간 정상

- 
500 ms debounce 정상 작동

## 9. 최종 테스트 결과
**2026-04-10: **PC간 MQTT 통신 테스트 완료

- 
통신 메시지
**출처**:

- 
`firmware/conveyor_controller/conveyor_controller.ino` (v3.0.0)

- 
`firmware/conveyor_controller/wiring_diagram.html` (v3 FINAL)

- 
`firmware/conveyor_controller/sketch.json` (FQBN: `esp32:esp32:esp32doit-devkit-v1`)
**20260416** : PC간 시리얼 연결 통신 테스트 완료

- 
Esp32, Camera server(Jetson) 코드는 Github에 업로드 

- 
동영상은 [https://drive.google.com/file/d/1shBCUnkBgMjy4xyBRVMsIUMtFpk0VkEc/view?usp=drive_link](https://drive.google.com/file/d/1shBCUnkBgMjy4xyBRVMsIUMtFpk0VkEc/view?usp=drive_link)
[https://drive.google.com/drive/folders/1SekZkiMBD7PlWhrS6tMRgcBgH7D6TilF](https://drive.google.com/drive/folders/1SekZkiMBD7PlWhrS6tMRgcBgH7D6TilF)

#### Robot_Arm (7438542)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7438542
**최종 수정**: v12 (2026-04-19 sync)

### 1. 목표: 
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7471562/?draftShareId=92edda25-601a-4e04-82ae-c7f1612abc65](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7471562/?draftShareId=92edda25-601a-4e04-82ae-c7f1612abc65)

### 2. 조사 주제:

#### 2-1. 기본 주제

- 
Spec 분석 : 

  - 
Payload test : 최대 moment 지점에서의 payload 측정 (팔을 쭉 편 상태에서 최대 가반 하중 테스트/ 실질적인 범위에서 최대 가반 하중 테스트)

  - 
Reachability test : 작업 위치별 도달 가능 여부 (단순 도달 가능 영역을 확인하여 표현할 예정)

  - 
Repeatability test : 반복 정밀도 테스트(동일 동작을 반복 시켰을 때 오차율을 측정)

  - 
DoF test : 로봇의 기구 구조 한계로 인한 회전각의 제한 범위를 확인

  - 

  - 

- 

  - 

  - 

  - 

  - 

#### 

- 

  - 

  - 

  - 

  - 

- 
****

- 

- 

### 3. 결과 활용 

- 
레이아웃 확정

- 
로봇 base 위치 결정

- 
필요한 arm 길이/자유도 결정

- 
“1대 로봇으로 가능한지 / 2대로 분할해야 하는지” 판단

### 4. 실험 페이지 
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7766050/?draftShareId=553135fa-cbf8-402a-bd10-64e8218dfe22](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7766050/?draftShareId=553135fa-cbf8-402a-bd10-64e8218dfe22)
​일정
3/31 - 로봇팔 자유도 테스트 및 결과 기록
4/1 - 로봇팔 payload 테스트, reach                       준비물) 추 또는 저울 
4/2 - 오리엔 테이션 테스트 , 싸이클 테스트(거리-무게-경로 순서대로)
4/3 - 
추후 - 싸이클 타임 테스트

#### Sensor (7929882)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7929882
**최종 수정**: v31 (2026-04-19 sync)

# 목적 
시스템에 적용하고자 하는 각종 센서 기술조사
시스템에 적용하고자 하는 각종 센서들의 적용가능성을 조사하고 조사 자료를 토대로 시스템 적용 가능성을 판단하고자 함

# 조사 내용 

## 스펙 

### 카메라 

****
****
****
****
| 항목\모델명 | Osmo Poket 3 | Realsense D435if | C920 |
|---|---|---|---|
| ​종류 | 짐벌카메라 | 뎁스 카메라 | 웹캠 |
| 센서타입 | 스테레오 IR +RGB | CMOS | CMOS |
| 최대해상도 | 1280×720 (Depth)1920×1080 (RGB) | 4K | 1080p |
| 인터페이스 | USB 3.0 | USB / SD | USB |
| 무게 | 72g | 179g | 162g |
| 촬영 | 웹캠모드지원 | 웹캠모드지원, SDK | 웹캠 |

### 레이저 센서 

****
****
| 항목/모델명 | TOF10120 |
|---|---|
| 사진 |   |
| 측정범위 | 100~1800mm |
| 오차범위 | 5%이내 |
| 통신방식 | 시리얼통신(UART, I2C) |
| VCC(V) | 3~5 |

- 

# 실험 

## 카메라 

- 
뎁스카메라를 활용해 주물 형상의 depth map 데이터를 받아 point cloud 형상을 제작

- 
뎁스카메라에는 두가지 모드(RGB,Stereo)가 있으며, 각 모드별 물리적 센서의 위치가 다르기 때문에 프레임이 다름 (RGB 기준좌표와 Depth 기준좌표가 다름)

- 
추가적으로 Depth를 3D좌표로 변환한 후 RGB 카메라 기준으로 재투영해서 새로운 Depth 이미지를 생성해야되는 작업이 필요

- 
RGB와 Detph 좌표를 매칭하여 마우스지점의 거리를 출력하는 실험을 진행

|   |   |   |
|---|---|---|
|   |   |   |

- 
yolo 오픈소스 모델을 활용하여 사람의 객체를 탐지하고 탐지된 사람의 거리를 표시

- 
xy값은 픽셀위치가 출력되기 때문에 카메라를 기준으로(또는 기준점을 기반으로) x,y,z의 거리값이 산출되어야 함.

- 
RGB모드와 Depth모드를 매칭하여 특정 객체를 탐지하고 객체의 x,y,z 좌표정보를 파악할 수 있다면 로봇그리퍼의 위상차이를 통해 값을 보정하여 원하는 위치에 로봇팔이 도달하는 것이 가능

- 
x,y픽셀좌표를 거리값으로 보정하여 실제거리로 환산 후 출력

- 
파란점을 기준으로 x좌표 거리와 y좌표거리의 정확도를 평가하였음. 

- 

****
****
****
| 거리\축 | x | y |
|---|---|---|
| 10cm |   |   |
| 20cm |   |   |

## 레이저 센서

- 
시스템에서는 완성된 주물을 컨베이어 벨트를 통해 이송하면서, 주물이 검사 위치에 도달하면 컨베이어 벨트를 정지시킨 후 검사를 수행.

- 
주물이 검사 위치에 도달했을 때 이를 감지하여 컨베이어를 정지시킬 수 있는 신호 생성 방법이 필요.

- 
레이저 거리 센서를 통해 주물의 도달 여부를 확인하고, 해당 정보를 기반으로 컨베이어 벨트의 ON/OFF를 제어하고자 함.

- 
실험에서는 작동되는 컨베이어에 두깨 5mm의 주물을 이송시키고 고정된 위치에 있는 레이저 센서가 주물을 감지할 수 있는지 검증실험을 진행함

****
****
| 검증 시료의 평면도 | 검증 시료의 정면도 |
|---|---|
|   |   |

- 
실험 결과 5mm 두깨의 주물을 감지하는 것을 확인

- 
두 번째 실험에서는 레이저 거리센서를 활용하여 용탕의 냉각 상태를 확인할 수 있는지 검증

- 
용탕은 실온에서 응고가 진행되며, 물을 제외한 모든 물질은 응고가 진행될수록 부피가 감소

- 
이러한 특성을 이용하여 레이저 거리센서를 통해 용탕의 냉각 상태를 확인할 수 있는지에 대한 실험을 진행

****
****
****
| 용탕 투여 전 | 투어 직후 | 투여된 용탕 냉각 |
|---|---|---|
|   |   |   |

- 
실험 결과 시간이 지나고 냉각상태에 따라서 거리값의 범위가 증가하는것을 확인

- 
비접촉식 센서의 특성상 값이 일정하지 않지만 범위값이 점점 증가

****
****
****
| 초기 거리값 | 5분경과 거리값 | 10분경과 거리값 |
|---|---|---|
| 55~60mm 범위 | 65~70mm 범위 | 75~80mm 범위 |

# 적용 가능성 

- 
컨베이어를 통해 이송되는 주물을 감지하는 레이저 센서는 얇은 두께의 대상물에서도 안정적으로 감지가 가능함을 확인. 따라서 해당 센서는 주물의 이송 여부를 판단하고, 컨베이어의 일시 정지를 제어하는 신호 입력 장치로서 충분히 적용 가능하다고 판단.

- 
주물의 냉각 상태를 파악하기 위한 레이저 센서의 경우, 주형에 투입되는 용탕의 양에 따라 측정 데이터가 유의미하게 변화하는지에 대한 검증이 필요. 또한, 비접촉식 센서의 고유 오차 범위가 측정값에 미치는 영향을 고려할 때, 이를 극복하고 냉각 상태를 신뢰성 있게 판단할 수 있는지에 대한 추가 실험이 요구됨.

#### Embedded board (13500437)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13500437
**최종 수정**: v19 (2026-04-19 sync)

### 1. 스펙

****
****
****
****
****
| 항목\보드 | ESP32 | Jetson Orin NX(16GB) | Raspberry Pi 4(4GB) | Raspberry Pi 5(8GB) |
|---|---|---|---|---|
| 사진 |   |   |   |
| 구분 | MCU 보드 | SBC 보드 | SBC 보드 | SBC 보드 |
| CPU | Xtensa LX6 | ARM Cortex-A78AE | ARM Cortex-A78AE | ARM Cortex-A76 |
| 클럭 | ~240MHz | ~2.2GHz | ~1.5GHz | ~2.4GHz |
| ​Core | 2 | 8 | 4 | 4 |
| RAM | ~520KB | 16GB | 4GB | 8GB |
| OS | X | Jetpack(우분투) | Raspbian(우분투) | Raspbian(우분투) |
| ROS | O | O | O | O |
| 용도 | 컨베이어 제어 | 관제서버 | AMR 제어 | Robot arm 제어 |

### 2. 사용법

#### 2.1. ESP32

- 
와이파이 사용의 경우 아두이노 IDE에 EXAMPLE 예제 있음

#### 2.2. Pinout

- 
본 실험에서 사용할 레이저센서가 사용 가능한 시리얼 통신은 UART, I2C

- 
해당 보드에는 UART(TX,RX) 포트 3세트, I2C 포트 2세트

### 3. 실험

- 
아두이노 ide를 활용하여 ESP32 와이파이 접속

- 
Esp32-노트북 와이파이 연결 후 브라우저를 통해 메시지 전송

- 
노트북 브라우에서 전송한 값을 ESP32로 전송

|   |   |
|---|---|
|   |   |

- 
같은 공유기 wifi 에 연결된 서버에서 브로커를 통해 제어보드로 메시지를 보내고 ESP32에서 수신

- 
서버(구글 코랩) → 브로커(Hive MQ) → 보드(ESP32)로 메시지 전송

- 
1초간격으로 ‘Hello’를 전송하고 시리얼 모니터로 확인

****
****
| 서버 | 제어보드 |
|---|---|
|   |   |

#### RFID (30343222)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30343222
**최종 수정**: v1 (2026-04-19 sync)

#### RFID 태그 기반 식별 시스템 개요 (30179373)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30179373
**최종 수정**: v2 (2026-04-19 sync)

## [제안] 스마트 팩토리 맨홀 공정: 개별 식별 시스템 최적화 방안

### 1. 서론: 주물 공장의 식별 번호 관리 현황
전형적인 주조 공장에서는 제품의 신뢰성과 사후 관리(Traceability, 추적성)를 위해 각 맨홀마다 식별 번호를 부여하는 것이 업계의 표준

- 
**주요 방식:** 

  - 
**주물 각인 (Casting Mark):** 쇳물을 부을 때 거푸집 자체에 모델명, 하중 등급, 제조사명을 새겨 넣는 방식입니다. 이는 영구적이지만 개별 일련번호를 매번 바꾸기는 어렵습니다.

  - 
**개별 식별 번호 (Serial Number/QR/RFID):** 제작 직후 또는 후처리 단계에서 각 제품에 고유 번호를 부여합니다.

    - 
**타각(Stamping):** 금속 표면에 직접 번호를 찍어 누르는 방식.

    - 
**QR 코드/바코드:** 금속용 라벨을 부착하거나 레이저 마킹을 통해 부여.

    - 
**RFID 태그:** 고온과 충격에 강한 특수 태그를 부착하여 물류 흐름을 자동 추적.

- 
**필요성:**

  - 
**품질 추적 (Traceability):** 특정 맨홀에 균열이 발생했을 때, 그 제품이 **"언제, 어떤 용해로(Furnace)에서 나온 쇳물로 만들어졌는지"** 역추적하여 같은 시기에 생산된 제품들을 전수 조사하기 위함

  - 
**납품 및 이력 관리:** 맨홀은 설치 장소에 따라 하중 등급이 다르기 때문에, 엉뚱한 곳에 설치되지 않도록 관리

  - 
**유지 보수:** 지자체나 관리 주체에서 도로 정비를 할 때, 식별 번호를 조회하여 교체 주기나 상세 사양을 즉시 파악

### 2. 본론: 우리 프로젝트의 문제점 및 해결 설계

#### **2.1 현재 프로젝트의 문제점**

- 
**물리적 식별 수단의 부재:** DB상에는 아이템 ID가 존재하지만, 실제 로봇이 옮기는 맨홀에는 식별 장치가 없어 **물리적 실체와 데이터가 단절**되어 있음.

- 
**공정 환경의 제약:** 주조 직후나 후처리(연마 등) 도중에는 강한 마찰과 열로 인해 태그를 부착해도 훼손될 가능성이 매우 높음.

#### **2.2 우리 프로젝트에 맞는 부여 방식 및 순서**
생산 중이나 직후에 부여할 수 없음.후처리 과정이 필요해 도중에 훼손될 가능성 있음
→ 훼손 가능성을 최소화하고 데이터 동기화를 극대화하기 위해 **'후처리 직후 부착'** 공정을 제안함
전제 ) 후처리 작업자가 도착한 순서대로 보관하고 작업을 진행한다

1. 
**[생산] **생산 시작 시 DB에 고유 ID 생성. (item id)

1. 
**[이송 및 도착]** AMR이 후처리 구역 도착 시 아니면 미리, 해당 ID가 담긴 태그 자동 출력.(프린터기 같은걸로)

1. 
**[후처리 작업]** 작업자가 **FIFO(선입선출)** 순서로 보관,연마 작업 진행.

1. 
**[후처리 작업]** 깨끗해진 제품 표면에 식별 태그 부착.

1. 
**[후처리 완료 및 비전 검사 시작]** 태그 스캔 후 컨베이어 투입 → DB 상태 자동 갱신 (후처리 작업 끝)+비전 검사 시작.
=> 작업자는 큐티를 확인하고 완료신호를 보내고 하는 과정이 필요하지 않음.순서대로 작업만 진행하면됨
=>  사람이 amr에서 하차 후 하차 완료 신호를 보내는 작업은 스위치를 추가해서 하차완료 신호를 받는다

#### **2.3 기술별 구현 방식 비교**

- 
**RFID / QR / 바코드**
식별용 카메라를 별도로 추가하는 방식과 전용 모듈 방식을 비교

- 
**QR 코드 (별도 카메라):** 비전 검사용 외에 식별용 카메라를 또 설치해야 함. 일반 카메라는 초점 및 조명 민감도가 높아 인식 오류가 잦고 CPU 자원을 많이 소모함.

- 
**바코드 (전용 모듈):** 인식 성능은 확실하나, 단순 ID 읽기 기능 대비 모듈 단가가 비싸 예산 효율성이 떨어짐.

****
****
****
****
| 구분 | RFID (RC522) | QR 코드 (별도 카메라) | 바코드 (전용 모듈) |
|---|---|---|---|
****
****
****
****
| 핵심 하드웨어 | RFID 리더기 + 태그(칩) | 일반 웹캠 / 카메라 모듈 | 광학 스캔 엔진 (GM65 등) |
****
****
****
| 예상 비용 | 매우 저렴 (약 5천 원대) | 보통 (웹캠 1~2만 원대) | 비쌈 (약 4~5만 원대) |
****
****
****
****
| 구현 난이도 | 쉬움 (라이브러리 활용 단순 ID 매칭) | 매우 어려움 (OpenCV/이미지 처리 코딩 필수) | 매우 쉬움 (시리얼 통신으로 데이터 수신) |
****
****
| 시스템 효율성 | 매우 높음 (먼지/오염에 강하고 인식 명확) | 낮음 (CPU 자원 소모 및 인식 오류 가능성) | 높음 (인식 속도가 빠르고 정확함) |
****
****
****
| 구현의 한계점 | 태그를 직접 부착해야 하는 소모품 비용 발생ㅗ | 비전 검사용 카메라와 별도로 설치 시 중복 투자, 초점/조명 세팅이 매우 까다로움 | 기능 대비 하드웨어 단가가 비싸 프로젝트 예산 부담 가중 |
****
****
| 산업 환경 적합성 | 최적 (주조 공장의 먼지/열에 강함) | 낮음 (렌즈 오염 및 조명 간섭에 취약) | 보통 (레이저/광학 방식이라 렌즈 관리 필요) |

### 3. 결론: RFID(NFC) 태그 기반 시스템의 합리성
적용한다면 우리 프로젝트에는 **RFID(NFC) 방식이 가장 합리적**인 선택 **(시연 기준)**

- 
**비용의 압도적 우위:** 리더기(RC522 등) 가격이 카메라나 전용 스캐너의 **1/10 수준**으로 매우 저렴함.

- 
**RFID 내에는 원하는 데이터를 입력,수정 가능함**

- 
**구현의 간결함:** 복잡한 이미지 프로세싱(OpenCV) 없이 아두이노와의 시리얼 통신만으로 즉각적인 데이터 획득 가능.

- 
**현장 최적화:** 주물 공장의 분진이나 조명 변화에 영향을 받지 않으며, 비접촉 방식으로 작업자가 갖다 대기만 하면 공정 상태가 전환되는 명확한 인터페이스 제공.

#### RFID 기초 통신 및 UID 추출 실험 (30539816)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30539816
**최종 수정**: v9 (2026-04-19 sync)

목적: ESP32와 RC522 간의 SPI 통신 정상 작동 확인.
내용: Ntag 213 스티커를 태깅했을 때 고유 UID가 시리얼 모니터에 정확히 출력되는지 테스트.
참고 [https://blog.naver.com/pongpong319/223101992823](https://blog.naver.com/pongpong319/223101992823)
오늘해야하는 일 
**프로세스**
AMR이 맨홀을 가지고 후처리 구역에 도착 → 사람이 꺼내고 하차 완료 스위치를 누름 → 해당 맨홀의 태그가 출력됨 → 후처리 작업 진행 → 맨홀에 태그 부착 → 리더기에 스캔하고 컨베이어 벨트에 올림
사람이 꺼내고 하차 완료 스위치를 누름 

- 
작업자가 스위치를 누르면 ‘하차완료’ 데이터가 시리얼 통신을 통해 서버로 전달

- 
서버에서 디비로 전달 ,UPDATE DATA
해당 맨홀의 태그가 출력됨 

- 
맨홀의 ITEM ID가 담긴 태그가 출력되어야함

- 
RFID에 미리 아이템 번호를 넣어놓는다  - 디비 만들어져있어야됨
맨홀에 태그 부착
**CASE 1**
NFC 스티커 이용
**CASE2**
바코드 이용 - 아이템 아이디 바코드로 변환해서 프린터 출력해야됨
리더기에 스캔하고 컨베이어 벨트에 올림
**CASE 1**
NFC 스티커 이용

- 
UID(NFC 스티커의 고유번호)를 읽는게 아닌 그 안의 ITEM ID를 읽어와 시리얼 통신으로 보냄
**CASE2**
바코드 이용

- 
바코드 번호 읽어서 시리얼 통신으로 보냄

### 실험 1: NFC 스티커를 이용한 시리얼 통신

- 
실험을 위해 아두이노 보드와 노트북 연결 후 준비된 코드 업로드

- 
모듈은 ESP32 Dev Module

- 
업로드 결과 UID만 출력될 뿐 ITEM_ID가 출력되지 않음

- 
UID, HEX, HEX를 변환시킨 ASCII를 출력하는코드 수정

- 
- 
​재업로드 결과를 분석하여 인식시킨 NFC 데이터 뒷쪽의 order_1_item_20260417_1의 앞부분만 출력되는 것을 확인

| 구간 | 의미 |
|---|---|
| ABCD4 | RAW 데이터 |
| 03 ~ | NDEF 시작 |
| D1 | NDEF 레코드 |
| 54 | Text 타입 |
| ko | 언어 코드 |
| or | 텍스트 일부 |

- 
인식하는 페이지를 늘리고 다시 재업로드시 TLV(0x03) 위치를 오류 발견

- 
오류 수정 후 다시 재업로드 후 정상적으로 출력됨을 학인
**최종 버전**

- 
불필요한 코드들 제거
결과화면 다시 찍어서 추가하기

#### End-to-End Data_Link_Test (31260691)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31260691
**최종 수정**: v1 (2026-04-19 sync)

실험 내용: RFID 스캔 → ESP32 위파이 전송 → 서버 수신 → PostgreSQL DB 상태값(Status) 변경 확인.
목적: 식별 번호 인식이 실제 비전 검사 시스템 가동(Trigger)으로 이어지는 시스템 전체 효율성(Efficiency) 검증.

#### 후처리 작업구역 스위치 도입 시나리오 (37160520)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/37160520
**최종 수정**: v4 (2026-04-19 sync)

## **전제**

- 
**amr은 하차 완료되면 바로바로 떠나줘야됨 자리 차지 X**

- 
**먼저 후처리 구역 도착 상태가 된 amr부터 시작**

## **논의**

- 
**후처리 zone에 AMR이 한대만 존재해야 한다.(후처리 주차 구역?location은 1칸만) 2대 이상인 경우에는 zone 밖에서 대기한다. 이유 선입 선출을 명확하게 하기 위함.**

- 
**하차 중 상태는 꼭 필요한가.. 도착지 도착상태가 너무 짧음 도착해서 도착상태로 바꾸자마자 하차상태 됨.그냥 도착지 도착-(유지)-하차완료 하는건 어떤지,,?**

### **스위치 있는 버전**

- 
특징 : amr이 대기하는 시간이 짧음

****
****
****
****
****
| 순서 | 공정 단계 | AMR 상태 | 아이템 상태 | 관제 데이터 조회 및 판별 로직 (Key) |
|---|---|---|---|---|
****
****
****
``
````
| 1 | 공정 이동 | 도착지로 이동 | DM | amr_id가 item_id를 싣고 후처리 구역으로 경로 배정 중 |
****
****
****
``
````
| 2 | 구역 도착 | 도착지 도착 | DM | AMR의 도착 신호 수신. DB에서 해당 amr_id에 매칭된 item_id 파악,'아이템 태그' 프린터로 출력 시작진행중인 item id = 1 |
****
****
****
``
| 3 | 맨홀 내림 | 하차 중 | DM | 작업자가 맨홀을 꺼냄후처리 구역에 주차된 amr id = 1진행중인 item id = 1 |
****
****
****
``
| 4 | 스위치 누름 | 하차 완료 | DM->PP | PP로 업데이트후처리 구역에 주차된 amr id = 1진행중인 item id = 1 |
****
****
****
``
| 5 | AMR 복귀 | 대기 장소로 출발 | PP | 하차 완료된 AMR에게 다음 목적지 혹은 대기소 명령 하달후처리 구역에 주차된 amr id = null진행중인 item id = 1 |
****

- 

| 모든 단계에서 일어날수있음 |
****
****
****
``
| 6 | [큐티] 검색&내용 확인 | - | PP | 진행중인 item id = 1 |
****
****
****
``
| 7 | 후처리 종료 & 태그 부착 | - | PP | 진행중인 item id = 1 |
****
****
****
````
| 8 | 태그 스캔 &컨베이어 위에 올림 | - | PP->IP | 작업자가 완료 후 태그 스캔. 시리얼 통신으로 넘어온 item_id를 DB에서 검색하여 상태를 IP(검사대기)로 전환진행중인 item id = null |
****
****
****
``
``
| 9 | 검사 진입 | - | IP | 비전 검사기 진입 시 item_id를 재조회하여 검사 결과 데이터와 매칭 시작 |

### **스위치 없는 버전**

- 
특징 : amr 대기 시간이 길어짐 - 검색하고 후처리 확인하고 후처리 시작 누를때까지 기다려야됨

****
****
****
****
****
| 순서 | 공정 단계 | AMR 상태 | 아이템 상태 | 관제 데이터 조회 및 판별 로직 (Key) |
|---|---|---|---|---|
****
****
****
``
````
| 1 | 공정 이동 | 도착지로 이동 | DM | amr_id가 item_id를 싣고 후처리 구역으로 경로 배정 중 |
****
****
****
``
````
| 2 | 구역 도착 | 도착지 도착 | DM | AMR의 도착 신호 수신. DB에서 해당 amr_id에 매칭된 item_id 파악'아이템 태그' 프린터로 출력 시작후처리 구역에 주차된 amr id = 1진행중인 item id = 1 |
****
****
****
``
| 3 | 맨홀 내림 | 하차 중 | DM | 작업자가 맨홀을 꺼냄후처리 구역에 주차된 amr id = 1진행중인 item id = 1 |
****
****
****
``
| 4 | [큐티] 검색 + 내용 확인 | 하차 중 | DM | 후처리 구역에 주차된 amr id = 1진행중인 item id = 1 |
****
****
****
``
| 5 | [큐티]후처리 시작 버튼 누름 | 하차 중 | DM → PP | 하차중->하차완료PP로 업데이트 |
****
****
****
``
| 6 | AMR 복귀 | 하차 완료 | PP | 하차 완료된 AMR에게 다음 목적지 혹은 대기소 명령 하달후처리 구역에 주차된 amr id = null진행중인 item id = 1 |
****

- 

| [Interrupt] 모든 단계에서 일어날수있음후처리 구역에  item id 2 가지고 2번 amr 도착 (하차 먼저 하거나 후처리 끝나고 하차 시키거나,,근데 하차를 보통 먼저하겠지 item2번은 어디 보관해두고 ‘FIFO’ 근데 태그는 이미 나와있겠지 그럼….)후처리 구역에 주차된 amr id = 2 /보관중인 item id =2(시스템에 저장되는 정보는 ㄴㄴ) |
****
****
****
``
| 7 | 후처리 종료 & 태그 부착 | - | PP | 진행중인 item id = 1 |
****
****
****
````
| 8 | 태그 스캔 &컨베이어 위에 올림 | - | PP->IP | 작업자가 완료 후 태그 스캔. 시리얼 통신으로 넘어온 item_id를 DB에서 검색하여 상태를 IP(검사대기)로 전환진행중인 item id = null |
****
****
****
``
``
| 9 | 검사 진입 | - | IP | 비전 검사기 진입 시 item_id를 재조회하여 검사 결과 데이터와 매칭 시작 |

### 3.2 SW_Research (8552545)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8552545
- **빈 페이지** (2026-03-31 생성, 내용 없음)

#### Vision (7405777)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7405777
**최종 수정**: v16 (2026-04-19 sync)

###

#### VLA (Tech_Research) (7405754)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7405754
**최종 수정**: v4 (2026-04-19 sync)

#### LLM/VLM (tech_research) (7438588)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7438588
**최종 수정**: v2 (2026-04-19 sync)

### 1. 역할 
운영자 보조, 자연어 질의응답, 리포트 생성, 룰 설명, 예외 상황 해석.

### 2. 적용 가능 예시 

- 
“현재 어느 공정에서 병목이 생겼는가?”

- 
“출고 불가 이유 요약”

- 
“작업 로그를 사람 친화적으로 설명”

- 
“매뉴얼/도면/발주서 기반 Q&A”

### 3. 사용 위험 예시 

- 
하드 리얼타임 장비 제어

- 
safety-critical stop decision 단독 판단

### 4. 모델 선택 

- 
**작은 현장형 LLM**: 로컬 배포, 빠름, edge 쪽

- 
**중간~큰 서버형 LLM**: 운영자 보조/리포트/분석

- 
vLLM은 GPU 추론 엔진으로 널리 쓰이며 Linux와 CUDA GPU(컴퓨트 capability 7.0+)를 지원한다. Meta 계열 Llama 3는 8B가 consumer-size GPU 개발/배포에 적합하고, 70B는 대규모 애플리케이션용으로 소개된다. Meta의 모델 컬렉션 페이지에는 Llama 3.2의 1B/3B 소형 계열과 Llama 3.3 70B가 함께 제공된다.

### 5. 필요 실험 

- 
공정 로그 요약 정확도

- 
질의응답 응답시간

- 
hallucination rate

- 
tool calling 안정성

- 
edge deploy 가능 여부

- 
dataset 

  - 
완전 pretraining 말고 **instruction tuning / domain adaptation** 관점

  - 
작업 로그, 매뉴얼, Q&A, 장애 사례를 모아 task-specific set 구성

  - 
추천 실험:

    - 
zero-shot

    - 
few-shot prompt

    - 
LoRA fine-tuning

    - 
RAG only
이 4개 비교

### 6. 활용 예시 

- 
“LLM을 어디까지 production에 넣을지” 결정

- 
RAG/DB 연결 필요성 판단

#### Storage_System (12124168)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/12124168
**최종 수정**: v9 (2026-04-19 sync)

생각해야하는거

1. 
완성된 주물을 어떤 방식으로 보관할것인가
실제공장 적용방식보다는 우리가 로봇팔로 잘 적재할수있는 방법을 우선으로 생각

  1. 
보관하지않고 썡으로 보관

  1. 
박스에 보관

  1. 
파레트에 보관

  1. 
밀봉???

1. 
적재방법

  1. 
보관함을 밑에서부터 들어서 넣을지

  1. 
리프트로 올려서 밀어넣을지

1. 
로봇팔이 이송된 주물의 위치를 어떻게 인식하는가

  1. 
amr 주차위치를 고정해두고 해당 위치에만 접근?

  1. 
카메라로 인식

  1. 

1. 

시스템 데이터와 실제 현장의 점유 상태가 일치하지 않는 경우

  1. 
카메라로 인식

  1. 
센서값으로 인식(무게…)

1. 
로봇팔이 적재위치를 어떻게 찾을 것이냐

  1. 
카메라

  1. 
위치 좌표 입력

#### Tailscale-Ros communication (26083935)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26083935
**최종 수정**: v12 (2026-04-19 sync)

# 개요

- 
우리는 5대의 로봇(각 로봇 내부에는 여러 ROS 노드가 존재)과 관제 서버가 ROS 2로 통신하는 환경이다.

- 
그리고 Tailscale을 통해 네트워크를 연결하려고 한다.

- 
기본적으로 DDS는 서로를 찾고 연결하는 과정에서 multicast를 사용하기 때문에,

- 
Tailscale처럼 multicast 기반 discovery (상대를 찾고 endpoint를 연결하는 것)가 어려운 환경에서도,

  - 
endpoint discovery protocol: topic과 데이터 타입 확인 및 연결 
정리하면, Tailscale에서 ROS를 사용하는 방식은 두 가지가 있다.

1. 
Discovery Server를 이용하면 unicast 기반으로 discovery를 중개하기

1. 
FastDDS 설정에 initialPeersList로 연결할 IP들을 설정하기

# Discovery Server

## 조사

1. 
**Discovery Server를 안 쓸 때**

- 
각 로봇과 관제 노드가 서로를 직접 찾아야된다

- 
PDP, EDP 과정에서 각 참여자가 더 많은 discovery 메타트래픽을 주고받는다

- 
노드 수가 늘수록 discovery 교환 상대가 많아져서 확장성이 떨어지기 쉽다

1. 
**Discovery Server를 쓸 때**

- 
각 로봇은 discovery server에 자기 정보를 보내고,

- 
server가 매칭에 필요한 discovery 정보만 다시 전달한다

- 
그래서 전체 망에서 난잡하게 오가는 discovery 메타트래픽이 줄어든다.
[공식 문서](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Discovery-Server/Discovery-Server.html)

## 환경
`RMW_IMPLEMENTATION` = rmw_fastrtps_cpp
`ROS_DOMAIN_ID` = 99
`ROS_DISCOVERY_SERVER` = 100.114.89.93:11811(tailscale의 yong-ubuntu-2204)

## 방법
 multicast가 아닌 unicast 형태의 client-server로 중계하는 discovery server를 사용해서 연결하기

## [**시연 영상**](https://drive.google.com/file/d/17ToGg5pJmFVL7b4REzbSL4mL5Ot7iOv9/view?usp=sharing)
영상에서 discovery server를 껐다 켰다가 하면서 서버 연결 상태에 따른 동작을 보여주는데

- 
이미 pdp와 edp가 끝나서 통신 상대 정보가 각자에게 있는 경우에는,

  - 
 discovery server가 꺼져도 기존 통신이 일정 시간 계속 유지될 수 있다**.**

- 
하지만 discovery 정보 갱신이나 새 participant/endpoint 발견은 서버가 없으면 진행되지 않는다.

- 
자동으로 다시 켜는 방식이나, 백업 서버가 있는 게 좋다!

# Initial peer list 방식

## 조사
[https://github.com/tailscale/tailscale/issues/11972](https://github.com/tailscale/tailscale/issues/11972) 
[https://danaukes.com/notebook/ros2/30-configuring-ros-over-tailscale](https://danaukes.com/notebook/ros2/30-configuring-ros-over-tailscale) 
두 번째 방식인 FastDDS config 설정을 제안하는 github comment와 블로그가 있다.
→ 둘 다 fastdds의 config.yaml을 수정하는 방식을 제안한다.

## 환경 및 방식
initial peer list에 ip를 미리 작성해두면, unicast로 pdp를 보내는 구조이다.

# 비고
어떤 방식을 사용할지 몰라 했다.
강사님께서는, VPN까지 사용하는 것보다 공유기를 나눠줄테니 고정 IP 설정을 하라고 말해주셨다. 
로봇과 관제 서버 사이에는 Tailscale을 사용하지 않기로 결정.
*Tailscale을 사용하니 로봇과 통신 문제가 있기도 했다.*

#### DevOps (32964741)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32964741
**최종 수정**: v1 (2026-04-19 sync)

#### Docker 기술 조사 및 도입 검토 (30802539)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30802539
**최종 수정**: v4 (2026-04-19 sync)

작성일:  
목적: SmartCast_Robotics 프로젝트 내 Docker 도입 검토 
후속 문서: [https://dayelee313.atlassian.net/wiki/pages/resumedraft.action?draftId=28803114](https://dayelee313.atlassian.net/wiki/pages/resumedraft.action?draftId=28803114) 

## 1. Docker란?
Docker는 애플리케이션을 **컨테이너**라는 독립된 실행 환경에 패키징하여 어디서든 동일하게 실행할 수 있도록 하는 플랫폼이다.

### 핵심 가치: "내 환경에서는 됐는데"를 없앤다
개발 환경과 운영 환경의 차이(OS, 라이브러리 버전, 환경변수 등)로 인한 문제를 컨테이너로 완전히 격리함으로써 해결한다.

## 2. 핵심 개념 및 구성 요소

### 2.1 이미지 (Image)
컨테이너를 만들기 위한 **읽기 전용 템플릿**이다. OS, 런타임, 라이브러리, 코드가 모두 포함된다.

### 2.2 컨테이너 (Container)
이미지를 실행한 **인스턴스**다. 이미지 1개로 컨테이너를 여러 개 실행할 수 있다.

### 2.3 볼륨 (Volume)
컨테이너가 삭제되어도 데이터를 유지하기 위한 **영속적 저장소**다.
볼륨으로 모델 파일을 마운트하면 컨테이너를 재빌드하지 않고 모델만 교체할 수 있다.

### 2.4 네트워크 (Network)
같은 Docker 네트워크 안의 컨테이너끼리는 **서비스 이름으로 통신**할 수 있다. Docker Compose로 실행하면 네트워크가 자동으로 구성되며 별도 설정이 불필요하다.

## 3. Docker Compose

### 3.1 개념
여러 컨테이너를 하나의 `docker-compose.yml` 파일로 정의하고 **한 번에 실행/중지**할 수 있는 도구다.

### 3.2 주요 옵션

| 옵션 | 설명 | 예시 |
|---|---|---|
``
``
| image | 사용할 이미지 지정 | image: postgres:15 |
``
``
| build | Dockerfile로 이미지 빌드 | build: ./ai-server |
``
``
| ports | 포트 매핑 (호스트:컨테이너) | ports: ["8080:8080"] |
``
``
| volumes | 볼륨 또는 경로 마운트 | volumes: ["./models:/app/models"] |
``
``
| restart | 재시작 정책 | restart: always |
``
``
| depends_on | 실행 순서 의존성 | depends_on: [db-server] |
``
``
| environment | 환경변수 설정 | environment: [DB_HOST=db-server] |

### 3.3 restart 정책
`restart: always` 설정만으로 컨테이너 자동 복구가 가능하다.  
단, 소프트웨어 크래시만 복구되며 서버 자체 장애 시에는 무중단이 보장되지 않는다.

## 4. Docker와 Kubernetes의 관계
Docker와 Kubernetes는 대체 관계가 아닌 **역할이 다른 상호보완적 도구**다.

| 도구 | 역할 | 사용 시점 |
|---|---|---|
****
| Docker | 컨테이너 이미지 빌드 및 실행 | 개발, 테스트 |
****
| Docker Compose | 다중 컨테이너 로컬 관리 | 개발, 단일 머신 운영 |
****
| Kubernetes | 다중 머신 컨테이너 운영 | 운영, 멀티 라인 확장 |
본 프로젝트는 **개발 단계에서 Docker + Docker Compose**, **운영 단계에서 Kubernetes**를 사용하는 방식으로 진행한다.

## 5. 프로젝트 아키텍처 적용 분석

### 5.1 현재 아키텍처 구성
통신 프로토콜: HTTP, Serial, TCP, ROS2(DDS)  
총 노드 수: **13개**

### 5.2 레이어별 Docker 적용 가능성

#### Server Layer — 적극 권장 ✅

| 서버 | 도입 이유 |
|---|---|
| AI Server (3대) | CUDA, Python 패키지, AI 라이브러리 의존성 복잡 → 환경 격리 필수 |
| Main Server | 서비스 단위 독립 실행, 빠른 재배포 가능 |
| DB Server | 볼륨으로 데이터 영속성 보장, 버전 고정 용이 |

#### HW Layer — 선택적 적용 ⚠️
ROS2 기반 Controller와 HW Controller는 실제 하드웨어 디바이스와 직접 연결되므로 컨테이너화 시 추가 설정이 필요하다.
ROS2 DDS 통신은 멀티캐스트를 사용하므로 Docker 브리지 네트워크와 충돌할 수 있다.  
초기 개발 단계에서는 **네이티브 실행을 권장**하며, 안정화 이후 Docker 적용을 검토한다.

#### UI Layer — 불필요 ❌
PyQt5 기반 데스크탑 앱은 GUI 환경이 필요하므로 컨테이너화의 이점이 적다.  
웹 기반 UI로 전환 시에는 Docker 적용이 가능하다.

## 6. AI Server 설계 분석

### 6.1 Pod 구성
Pod 1개에 모델 1개를 올린다. 각 AI Server는 담당 모델에 해당하는 Pod 2개를 실행한다.

### 6.2 평상시 라우팅
정상 상태에서 Main Server는 분류 결과에 따라 Primary Pod로 요청을 보낸다.

### 6.3 장애 시 자동 폴백 (K8s)
서버 1대가 완전히 다운되어도 모든 모델이 나머지 서버에 살아있다.  
K8s가 장애를 감지하고 Fallback Pod로 자동 라우팅한다.

### 6.4 모델 사전 로드
매 요청마다 모델을 Load하면 수십 초의 지연이 발생하므로, 서버 시작 시점에 담당 모델을 GPU 메모리에 미리 올려두고 추론 요청만 처리한다.

## 7. 도입 전략 및 권고사항

### 7.1 단계별 전략

### 7.2 최종 권고사항

| 레이어 | 권고 | 이유 |
|---|---|---|
****
| Server Layer | ✅ 즉시 도입 | 환경 통일, 의존성 격리, 자동 재시작 |
****
| HW Layer | ⚠️ 추후 검토 | 디바이스 마운트, ROS2 네트워크 설정 필요 |
****
| UI Layer | ❌ 미적용 | GUI 환경 필요, 이점 없음 |

### 7.3 참고 자료

- 
[Docker 공식 문서](https://docs.docker.com/)

- 
[Docker Compose 공식 문서](https://docs.docker.com/compose/)

- 
[NVIDIA Container Toolkit (GPU 지원)](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html)

#### Kubernetes 기술 조사 및 도입 검토 (28803114)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/28803114
**최종 수정**: v7 (2026-04-19 sync)

작성일: 
목적: SmartCast_Robotics 프로젝트 내 Kubernetes 도입 검토
선행 문서: [https://dayelee313.atlassian.net/wiki/x/awLWAQ](https://dayelee313.atlassian.net/wiki/x/awLWAQ) 

## 1. Kubernetes란?
Kubernetes(K8s)는 컨테이너화된 애플리케이션의 **배포, 확장, 운영을 자동화**하는 오픈소스 플랫폼이다.  
Google이 내부 시스템 Borg를 기반으로 개발하였으며, 현재는 CNCF(Cloud Native Computing Foundation)에서 관리한다.

### 핵심 철학: 선언적 관리 (Declarative Management)
직접 명령을 내리는 방식이 아닌, **"원하는 상태"를 선언하면 K8s가 그 상태를 유지**하는 방식으로 동작한다.

## 2. 핵심 개념 및 역할

### 2.1 구성 요소

| 구성 요소 | 설명 |
|---|---|
****
| Pod | 컨테이너의 최소 실행 단위. 본 프로젝트에서는 Pod 1개 = 모델 1개 |
****
| Node | Pod가 실행되는 물리 머신 (AI Server 1, 2, 3) |
****
| Cluster | Node들의 집합 |
****
| Deployment | Pod의 배포 및 업데이트 관리 |
****
| Service | Pod에 접근하기 위한 네트워크 엔드포인트 |
****
| Ingress | 클래스별 요청을 해당 모델 Pod로 라우팅하는 규칙 |
****
| Node Selector | Pod를 특정 노드(서버)에 고정 배치하는 설정 |
****
| ConfigMap / Secret | 설정값 및 민감 정보 관리 |

### 2.2 주요 역할 5가지

#### ① 자동 복구 (Self-healing)
Pod가 크래시되면 K8s가 자동으로 감지하고 재시작한다.

#### ② 장애 시 자동 폴백
Node(서버) 장애 감지 시 해당 서버의 Pod로 가던 트래픽을 Fallback Pod로 자동 전환한다.

#### ③ 롤링 배포 (무중단 업데이트)
기존 Pod를 유지하면서 새 버전으로 순차 교체한다.

#### ④ 서비스 디스커버리
Pod IP가 변경되어도 서비스 이름으로 통신이 유지된다.

#### ⑤ 리소스 관리
서버별 GPU, 메모리 사용량을 제한하여 Pod 간 리소스 충돌을 방지한다.

## 3. Docker vs Kubernetes 비교

### 3.1 개념적 차이

| 구분 | Docker | Kubernetes |
|---|---|---|
****
| 역할 | 컨테이너 이미지 빌드 및 실행 | 컨테이너 운영 및 관리 |
****
| 범위 | 단일 머신 | 다중 머신 (클러스터) |
****
| 사용 시점 | 개발, 테스트 | 운영, 멀티 라인 확장 |
****
| 비유 | 화물 컨테이너 박스 | 컨테이너 선박 + 항만 관제 시스템 |
Docker와 Kubernetes는 경쟁 관계가 아닌 **역할이 다른 상호보완적 도구**다.  
Docker로 이미지를 만들고, Kubernetes가 그 이미지를 운영한다.

### 3.2 기능 비교

| 항목 | Docker + Compose | Kubernetes |
|---|---|---|
| 운영 규모 | 단일 머신 | 다중 머신 클러스터 |
``
| 자동 복구 | restart: always로 가능 | ✅ 자동 재시작 |
| 장애 시 자동 폴백 | ❌ 수동 전환 필요 | ✅ 자동 감지 및 전환 |
| 자동 스케일링 | ❌ 수동 | ✅ HPA 지원 |
| 롤링 배포 | ❌ (서비스 중단 발생) | ✅ 무중단 지원 |
| 서비스 디스커버리 | 제한적 | ✅ CoreDNS 기반 |
| 멀티 라인 확장 | 관리 복잡 | ✅ 노드 추가로 용이 |
| 설정 복잡도 | 낮음 | 높음 |
| 학습 곡선 | 완만 | 가파름 |

### 3.3 컨테이너 런타임 관계
K8s 1.24부터 Docker 런타임 지원이 공식 제거되었으며, 현재 기본 런타임은 **containerd**다.
단, **이미지 빌드 도구로는 Docker가 여전히 범용적으로 사용**된다.

## 4. 프로젝트 아키텍처 적용 분석

### 4.1 현재 아키텍처 구성
통신 프로토콜: HTTP, Serial, TCP, ROS2(DDS)  
총 노드 수: **13개**

### 4.2 K8s 도입 배경
본 프로젝트는 **실제 운영 환경에서의 무중단 운영**과 **향후 멀티 라인 확장**을 목표로 한다.  
Docker Compose만으로는 아래 상황에서 무중단을 보장할 수 없어 K8s 도입이 필요하다.

| 상황 | Docker Compose | Kubernetes |
|---|---|---|
| AI Server 장애 시 폴백 | ❌ 수동 전환 필요 | ✅ 자동 감지 및 전환 |
| 모델 업데이트 배포 | 서비스 중단 발생 | 롤링 배포로 무중단 |
| 멀티 라인 확장 | 관리 복잡 | 노드 추가로 용이 |

### 4.3 AI Server Pod 배치 전략
Pod 1개에 모델 1개를 올린다. 각 AI Server는 Primary Pod 1개와 Fallback Pod 1개를 실행한다.

#### 평상시 라우팅

#### 장애 시 자동 폴백

### 4.4 Node Selector 설정
Pod가 항상 지정된 노드에 배치되도록 고정한다.

### 4.5 K8s Ingress 라우팅 구조
Main Server는 단일 엔드포인트만 바라보고, K8s Ingress가 클래스별 라우팅과 장애 시 폴백을 자동으로 처리한다.

### 4.6 멀티 라인 확장 시 K8s 이점
공장 라인이 추가되어 Main Server가 복수화되는 경우, K8s 클러스터에 노드만 추가하면 된다.

### 4.7 HW Layer — K8s 미적용
ROS2 DDS 통신 특성상 K8s 네트워크와 충돌할 수 있으며, 실제 하드웨어에 직접 바인딩되므로 K8s 적용 대상에서 제외한다.

## 5. 도입 전략 및 권고사항

### 5.1 단계별 전략

### 5.2 최종 권고사항

| 기술 | 권고 | 이유 |
|---|---|---|
****
| Docker | ✅ 개발 단계 즉시 도입 | 환경 통일, 의존성 격리, 이미지 빌드 |
****
| Kubernetes | ✅ 운영 전환 시 도입 | 무중단 운영, 자동 폴백, 멀티 라인 확장 |
****
| HW Layer | ❌ K8s 미적용 | ROS2 DDS 충돌, HW 직접 바인딩 |

### 5.3 참고 자료

- 
[Kubernetes 공식 문서](https://kubernetes.io/docs/)

- 
[NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

- 
[CNCF Landscape](https://landscape.cncf.io/)

### 3.3 DB_Research (8585277)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8585277
- 다른 페이지로의 링크만 존재 (page 7471353 참조)

#### 관계형 데이터베이스 공유 자료 (7471353)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7471353
**최종 수정**: v7 (2026-04-19 sync)

관계형 데이터베이스 (RDBMS, Relational Database Management System)에 대해 학습해보자.  
우리가 시스템이나 서비스를 만들때, 여러 컴포넌트들은 다양한 형태의 데이터를 주고받는다. 예를 들어 사용자 입력 데이터, 기계 동작 중 생성되는 로그 데이터, 그리고 ROS 환경에서는 topic, service, action등을 통해 교환되는 메시지 데이터가 있다.  
이때, 데이터를 중복되거나 비효율적인 방식으로 저장하지 않도록, 관련 있는 데이터들을 테이블 단위로 구조화하고, 각 테이블 사이의 관계를 정의하여 데이터를 체계적으로 저장하고 관리한다. 
즉, 관계형 데이터베이스는 데이터를 여러 테이블로 나누어 저장하고, 테이블 간의 관계를 기반으로 필요한 데이터를 효율적으로 조회하고 관리할 수 있도록 하는 방식이다. 
이러한 데이터 구조를 설계하고 데이터베이스 구축을 위해서는 보통 다음과 같은 과정을 거친다. 
현재 단계에서는 우선 Schema와 ERD를 작성하는 과정을 이해하는 것이 중요하다.  
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7373302/?draftShareId=0b9403fa-f511-43f6-b9c0-18beac8d06e7](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7373302/?draftShareId=0b9403fa-f511-43f6-b9c0-18beac8d06e7)
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7438863/?draftShareId=a5a49d55-cd32-4b6a-9f16-6b7fd74eb5c8](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7438863/?draftShareId=a5a49d55-cd32-4b6a-9f16-6b7fd74eb5c8)
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/15007823/?draftShareId=8c8ab548-2dcf-4205-ada2-9e71ecf51903](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/15007823/?draftShareId=8c8ab548-2dcf-4205-ada2-9e71ecf51903)

#### ERD (Entity-Relationship Diagram) & Schema (7373302)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7373302
**최종 수정**: v10 (2026-04-19 sync)

# 기본 개념

## Table = Entity (개체)

- 
ERD에서 Entity는 SQL의 Table과 동일합니다. 

  - 
즉, 하나의 테이블은 = 하나의 개념이라고 생각하시면 되는데,

    - 
예를 들어 저희 서비스에서, 새로운 고객이 원격 발주 웹사이트에서, 

      - 
고객은 가입을 위해 이메일, 전화번호, 생년월일, 로그인 아이디, 로그인 비밀번호를 생성하고 저장했다고 가정해봅시다. 

      - 
이 때, 위의 데이터 종류를 `User` 라는 하나의 개념으로 묶을 수 있습니다. 

    - 
또한, 고객이 발주를 했다고 가정하면,

      - 
발주를 위해 원하는 제품 정보, 수량, 납기일, 원하는 디자인과 같은 데이터를 입력해서 발주를 했다고 해봅시다. 

      - 
그러면, 이러한 데이터의 종류를 `Order`라는 하나의 개념으로 묶을 수 있습니다. 

  - 
이렇게 Entity (Table)은 특정 고유한 개념에 속하는 데이터들을 한 데 묶어주는 역할을 합니다. 

- 
그렇다면, Table 안에 있는 컬럼은 `속성 (Attribute)`라고 칭합니다. 

- 
SQL에서 테이블은 다음과 같이 생성할 수 있습니다. 
Q. 위의 테이블에서 ERD에서 Entity와 Attribute는 각각 어떤 것인가요? 

## Primary Key (PK)
ERD를 구성할 때 가장 중요한 것은 반드시 Primary key (PK) 를 지정해야하는 것입니다. (PK는 필수는 아니지만, 데이터 식별과 무결성을 위해 반드시 사용하는 것이 권장됩니다.) 그 이유는 사람을 시스템상에서 구분할때 우리는 주민등록번호를 사용하는데, DB system에서 PK는 (테이블 자체를 구분하기 위한 것이 아니라),
해당 테이블 내부에서 각 “row”를 유일하게 식별하기 위한 값입니다. 따라서, PK는 다음과 같은 조건을 만족해야합니다. 
Primary Key 조건 3가지 

1. 
각 row를 유일하게 식별 가능 

1. 
Unique (중복 불가)

1. 
NOT NULL  
SQL에서 테이블을 생성할 때 primary key를 지정하는 방법은 다음과 같습니다. 
위의 코드를 실행하면, user_id attribute를 PK로 가진 User table이 형성됩니다. 혹은 아래 코드처럼 테이블 생성 후 PK를 지정할 수 있습니다. 
설계를 할 때, “이 데이터를 유일하게 구분하는 값이 무엇인가?” 라는 질문을 하면 PK attribute가 무엇이 되어야 하는지 쉽게 파악할 수 있습니다. 

## Foreign Key (FK)
우리는 스키마를 구성할 때 테이블을 분리하는데, 그 이유는 중복 데이터를 줄이고, 데이터의 일관성을 유지하기 위함입니다. 생성된 각 테이블에서 특정 데이터를 추출하고 싶을 때 테이블들이 연결되어 있지 않으면, 원하는 데이터를 얻기 어렵습니다. 
이때 서로 다른 테이블 간의 관계를 정의하기 위해 Foreign Key를 사용합니다. 따라서, 테이블간의 연결은 필수이며, 이를 Foreign Key(FK)를 이용해 연결할 수 있습니다. 
즉, FK는 ERD의 관계 (Relationship)를 만드는 핵심으로,  다른 테이블의 PK를 참조합니다. (참고로, FK는 일반적으로 다른 테이블의 PK를 참조하지만, UIQUE 제약이 있는 컬럼도 참조할 수 있음) 
<FK의 역할>

1. 
다른 테이블의 PK를 참조

1. 
테이블 간 관계 정의 
위의 SQL 코드는 Order 테이블을 생성하는데, `Order` 테이블은 `User` 테이블에 속하는 것을 확인할 수 있습니다. 

## Types of Relationships 
위에서 FK를 통해 두 테이블의 관계를 지정할 수 있었는데, 이러한 관계에는 어떤 타입이 있을까요? 총 3가지로 분류할 수 있습니다. 

### 1:1 관계 
이 관계는 말그대로 하나의 개념이 가질 수 있는 다른 개념은 오직 하나입니다. 예를 들어, 위에서 생성한 `User` 테이블에 대해서 해당 사용자의 `Profile` 테이블이 있다고 가정하면, 이 둘은 1:1 관계여야합니다. 한 사용자에 대한 profile을 여러개 가지고 있는 상황은 별로 없겠죠

### 1:N 관계
테이블의 관계는 대부분 이 관계에 속합니다. 우리의 프로젝트에서 하나의 고객은 여러 개의 발주를 할 수 있듯, 하나의 레코드(예: 한 User)는 여러 개의 다른 테이블의 레코드(예: 여러 Order)를 가질 수 있습니다.. 이때 User:Order = 1: N 관계가 성립됩니다. 
구현을 할 때는 일반적으로 1:N 관계에서는 N쪽 테이블에 FK를 둡니다. 

### N:M 관계 
학교 수강 신청 시스템을 생각했을 때, 학생은 여러개의 수업을 들을 수 있고, 여러 학생들이 하나의 수업을 듣습니다. 즉, 이는 N:M 관계로 다대다 관계입니다. ERD 에선 이 관계를 “중간 테이블”을 통해 다대다 관계로 연결할 수 있습니다. 
위의 코드에선 `Enrollment` 테이블을 만드는데, student_id와 course_id를 묶어서 PK를 지정합니다. 즉, Enrollment table은 `Student` 와 `Course` 테이블을 연결하기 위한 중간  테이블이며, 이를 통해 앞선 두 테이블에 연결된 정보를 추출할 수 있습니다. 

#### PRIMARY KEY ( attribute from table 1, attribute from table 2) 
위의 코드에서 `PRIMARY KEY (student_id, course_id)` 를 통해 같은 학생이 같은 수업을 중복 신청하지 못하게 합니다. 

#### Foreign Key (attribute_type in the table) REFERECES OTHER_TABLE_NAME(attribute_type)
위에서 `FOREIGN KEY (student_id) REFERENCES Student(student_id)` 라인은, Enrollments 테이블의 student_id 값은 Students table에 실재로 존재하는 student_id 만 쓸 수 있다는 뜻입니다. 즉, `Enrollments.student_id` 값은 반드시 `Students.student_id`에 있는 값이여야 하고, 아무 숫자이면 안됩니다. REFERENCES 사용을 통해, 존재하지 않는 학생-수업 관계를 저장하지 못하게 합니다. (데이터의 무결성) 
ERD 관점에서 보면, `Enrollments.student_id` → `Students.student_id` 와 `Enrollments.course_id` → `Course.course_id` 가 선으로 연결되게 됩니다. 
PRIMARY KEY (student_id, course_id) = 같은 조합 중복 금지 제약 조건 
FOREIGN KEY = 존재하는 학생/수업만 참조하게 함. 

## 정규화 (Normalization) 
이제까지 배운 ERD 개념을 통해 이제 ERD 설계를 해야하는데, 핵심은 “중복을 줄이고 구조를 깔끔하게” 하는 것입니다. 다음 규칙을 활용하면 좋은 ERD 설계를 할 수 있습니다. 

1. 
같은 데이터는 반복하지 않는다. 

1. 
쪼갤 수 없는 데이터를 컬럼 (attribute)로 사용한다. (원자값(Atomic Value))

1. 
의미 단위로 테이블을 분리한다. 

# ERD 설계 팁 
만들고자 하는 서비스에 대한 System Architecture나 GUI등이 결정되었다면, 이러한 ERD를 만들기 쉽습니다. 또한 시나리오에서 각 component간에 어떤 데이터들을 주고 받아햐는지 보면 더 명확히 ERD를 그릴 수 있습니다. 다음은 어떻게 ERD를 잘 설계할 수 있는지 Tip을 공유합니다. 

1. 
Entity 찾기: 명사 `User` , `Order`, `Product` 

1. 
PK 정하기: 각 table의 PK 지정 

1. 
관계 정의: 테이블마다 관계 정의 (1:1, 1:N, N:M)

  1. 
N:M 관계는 중간 테이블 필수 

1. 
FK 배치: 항상 N쪽에 FK 배치 

1. 
정규화: 중복 제거 
마지막으로 자주 조회되는 데이터 기준으로 관계를 설계하면 성능과 확장성 측면에서도 유리합니다.

# Data Type 
Schema를 설계할 때, 알면 유용한 데이터 타입 정리. 

## category 

****
****
****
|   | 장점 | 단점 | 사용 |
|---|---|---|---|
| ENUM | DB 레벨에서 값 제한 강제 | 카테고리 추가/삭제 시 ALTER TABLE 필요 → 운영 시 번거로움 | 값이 절대 안 바뀜 (성별) |
| VARCHAR + CHECK 제약조건 | 유연, 어떤 DB에서든 동작 | CHECK 제약을 안 쓰면 아무 값이나 들어갈 수 있음 | 값이 가끔 바뀌고 UI라벨 불필요 |
| 별도 코드 테이블 | 확장성이 큼 |   | 값이 자주 바뀌거나 다국어/라벨 필요 |

# Reference 

- 
[geeksforgeeks DBMS](https://www.geeksforgeeks.org/dbms/rdbms-full-form/)

- 
[스키마 설계](https://dev-novel.tistory.com/91)

#### SQL 기본 문법 정리 (7438863)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7438863
**최종 수정**: v5 (2026-04-19 sync)

# SQL 이란?
SQL (Structured Query Language)은 데이터베이스에서 데이터를 생성, 조회, 수정, 삭제하기 위한 언어입니다. 관계형 데이터베이스(RDBMS)에서는 테이블(Table)형태로 데이터를 저장하고, SQL를 통해 이를 다룬다. 

# 테이블 생성 (CREATE TABLE)
데이터를 저장하기 위해 먼저 테이블을 정의해야 합니다. 
`CREATE TABLE {Table name} ();` 키워드를 통해 테이블을 정의할 수 있습니다. 각 column (attribute)는 {attribute name} {data type} {property}로 정의할 수 있으며, 이 순서를 지켜야합니다. 
<column/attribute 정의 문법> 

- 
Column (컴럼): 데이터의 속성 (student_id, name, age)

- 
Data Type (자료형): INT, VARCHAR 등 

- 
Property: PRIMARY KEY, UNIQUE, NOT NULL, … 

# 데이터 삽입 (INSERT)

# 데이터 조회 (SELECT)

# 데이터 수정 (UPDATE)

# 데이터 삭제 (DELETE)

# 키 (KEY)

# 테이블 간 관계 (N:M 관계)

# 테이블 연결 (JOIN)

# INDEX / 성능 최적화

# Reference
 [https://www.w3schools.com/sql/sql_comments.asp](https://www.w3schools.com/sql/sql_comments.asp)

#### DB Cloud (30638152)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30638152
**최종 수정**: v5 (2026-04-19 sync)

# DB Cloud 서비스 (DBaaS)

## 개념
DB를 직접 설치/운영하지 않고 클라우드 인프라 위에서 서비스 형태로 제공하는 모델. 즉 DBaaS (Database as a Service)를 의미

## 구조

### Client Layer (접속 계층)

- 
애플리케이션 / 서비스 / 툴

- 
예:

  - 
DBeaver

  - 
백엔드 서버 (Spring, Node.js)

  - 
IoT 디바이스

- 
역할:

  - 
SQL 요청 전송

  - 
데이터 조회 요청

### Connection / API Layer

- 
DB Endpoint (URL, Port)

- 
인증 (ID / Password, IAM)

- 
기능:

  - 
접속 제어

  - 
트래픽 분산 (로드밸런싱)

  - 
보안 (SSL/TLS)

### Compute Layer (DB Engine)

- 
핵심:

  - 
실제 DBMS가 실행되는 영역

- 
예:

  - 
MySQL

  - 
Microsoft SQL Server

- 
기능:

  - 
SQL 실행

  - 
트랜잭션 처리

  - 
캐싱 (Buffer Pool)

- 
특징:

  - 
필요 시 Scale Up / Down 가능

  - 
Read Replica 구성 가능

### Storage Layer(분산 스토리지)

- 
특징:

  - 
데이터를 여러 노드에 분산 저장

- 
기능:

  - 
데이터 복제 (Replication)

  - 
장애 대비 (Multi-AZ)

  - 
고가용성 확보

- 
예:

  - 
SSD 기반 분산 스토리지

  - 
로그 기반 저장 (WAL)

### Management & Control Plane

- 
기능:

  - 
자동 백업

  - 
장애 감지 및 Failover

  - 
모니터링

  - 
Auto Scaling

- 
제공 주체:

  - 
Amazon Web Services

  - 
Google Cloud Platform

  - 
Microsoft Azure

## 데이터 흐름

## 서비스 유형

### 관계형 DB (RDBMS)

- 
MySQL, PostgreSQL 기반

- 
트랜잭션 중심 서비스

- 
대표:

  - 
Amazon RDS

  - 
Google Cloud SQL

  - 
Azure SQL Database

### NoSQL

- 
비정형 데이터 처리

- 
확장성 중심

- 
대표:

  - 
MongoDB Atlas

  - 
Amazon DynamoDB

### NewSQL / 분산 DB

- 
확장성 + ACID 트랜잭션

- 
글로벌 트랜잭션 처리

- 
대표:

  - 
Spanner

  - 
Google Spanner

  - 
CockroachDB

## 핵심 기능

### 자동 확장 (Auto Scaling)

- 
트래픽 증가 → 자동 자원 증가

### 고가용성 (High Availability)

- 
장애 시 자동 복구

### 백업 / 복구

- 
스냅샷 자동 생성

- 
Point-in-time recovery

### 보안

- 
암호화 (at rest / in transit)

- 
접근 제어 (IAM)

## 스마트 팩토리 적용 구조
핵심 포인트:

- 
 실시간 제어 → Edge 

- 
 데이터 저장 / 분석 → Cloud DB

#### DB Cloud 실제 적용 가능성 (30277849)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30277849
**최종 수정**: v19 (2026-04-19 sync)

# 권장 범위

- 
로봇 1~2대 (ROS2 / Nav2)

- 
센서 1~3개 (온도, 거리 등)

- 
DB Cloud 1개

- 
간단한 대시보드

# 검증 포인트

- 
데이터 수집 가능 여부

- 
DB 저장 구조 정상 동작

- 
분석/조회 가능 여부

# 최소 구성 아키텍처
핵심:

- 
제어는 로컬 

- 
데이터만 클라우드로 전송 

# DB Cloud 선택

### [Amazon Web Services](https://aws.amazon.com/ko/?nc2=h_home&refid=011f28e3-1dfa-405d-894f-3e05b14038a6)

- 
구성:

  - 
 RDS (t3.micro) 

    - 
t3.micro:

      - 
약 **$0.017/시간** 
→ 약 **$12 ~ $20 / 월**

    - 
Free Tier:

      - 
750시간 무료 + 20GB 제공

  - 
 Free Tier 활용 

- 
특징:

  - 
 크레딧 제공 (초기 무료) 

### [Google Cloud Platform](https://cloud.google.com/)

- 
구성:

  - 
 Cloud SQL (소형 인스턴스) 

    - 
b-n1-standard-1:

      - 
약 **$0.0685/시간**
→ 약 **$50 / 월**

- 
특징:

  - 
 크레딧 제공 (초기 무료) 

### [Microsoft Azure](https://azure.microsoft.com/ko-kr?ocid=cmm4r4ppnhp)

- 
 Azure SQL (Basic tier) 

  - 
약 **$5 ~ $30 / 월 (Basic tier)**

- 
특징:

  - 
최초 12개월 무료

# 실제 추천 DB 스펙
실증용 기준:

- 
 vCPU: 1 

- 
 RAM: 1GB 

- 
 Storage: 10~20GB 
→ 충분함

# 적용 성공 기준

1. 
 ROS2 데이터 DB 저장 성공 

1. 
 DBeaver로 조회 가능 

## 그 외

- 
[Amazon Aurora](https://www.youtube.com/watch?v=5TVtFdiXVSE)

- 
개인 노트북을 DB Server로 사용

- 
MySQL 설치

- 
MySQL 버전 확인

1. 
**MySQL 접속**

- 
MySQL 실행

- 
root 유저로 MySQL 서버 접속

### 3.4 SW_Control (15433852)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15433852

#### Confluence 원문 팩트
- 단일 링크: **https://github.com/addinedu-ros-4th/ros-repo-2**
- 다른 팀/과거 ROS 레포 참조 (본 프로젝트와 직접 관련 낮음)

#### 관제 기술조사_0407 (17956894)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/17956894
**최종 수정**: v10 (2026-04-19 sync)

### reference

- 
[AMR Logistics Automation system](https://github.com/addinedu-ros-4th/ros-repo-2)
**흐름**

1. 
출고는 소비자 GUI가 주문을 DB에 저장한 뒤 `/outbound`로 웹소켓 publish 합니다. 시작점은 `ui_main.py`, ROS 진입은 `ui_main.py`입니다.

1. 
입고는 관제 GUI의 바코드 스캐너가 `Inbound`와 재고를 갱신하고 `/inbound`로 publish 합니다. 시작점은 `barcode_scanner.py`, ROS publish는 `barcode_scanner.py`입니다.

1. 
서버의 `OrderReceiver`가 `/inbound`, `/outbound`를 받아 `TaskList`로 변환합니다. 단일 주문 해석은 `order_receiver.py`, 출고 상품의 선반 위치 매핑은 `order_receiver.py`입니다.

1. 
`TaskAllocator`는 `/task_list`, `/robot_status`, `/task_completion`을 보고 transaction 단위로 묶습니다. 묶는 로직은 `task_allocator.py`, 입출고용 보정 태스크 생성은 `task_factory.py`입니다. 출고는 `O2 Up -> 상품 위치 -> O2 Down`, 입고는 `입고지점 -> 최종 적치 위치` 형태입니다.

1. 
할당은 `task_allocator.py`에서 가능한 로봇을 찾고, `task_allocator.py`에서 `/allocate_task_<robot_id>` 서비스로 넘깁니다. 현재 transaction 상태는 `task_allocator.py`, 미할당 대기열은 `task_allocator.py`로 GUI에 보냅니다.

1. 
로봇 쪽 `RobotController`는 `/allocate_task_<ID>`를 서비스 서버로 열고, 요청을 받으면 `robot_controller.py`에서 `follow_path()`를 수행합니다. 실제 실행은 `robot_controller.py`이고, stopover 경로계획은 `robot_controller.py`, 리프트/아루코 연동은 `robot_controller.py`와 `robot_controller.py`입니다.

1. 
출고는 사람이 물건을 꺼내는 확인 단계가 들어갑니다. 로봇은 `robot_controller.py`에서 `/complete_picking`을 기다리고, 실제 버튼 입력은 `button_lcd_control.py`와 `button_lcd_control.py`입니다.

1. 
관제 GUI는 메인 페이지에서 미할당 작업과 로봇 상태를 보고, 로봇 페이지에서 카메라/정지 제어를 하고, 입고/주문 페이지에서 DB 기반 리스트를 보여줍니다. 각각 `manager_main.py`, `manager_main.py`, `manager_main.py`입니다.
**코드베이스 분석**

- 
구조 자체는 나쁘지 않습니다. `task_msgs`로 계약을 분리하고, 서버는 orchestration, 로봇은 execution, GUI는 visualization/control로 역할이 나뉘어 있습니다.

- 
DB도 관제 축에 직접 들어갑니다. `ProductInventory`, `ProductOrder`, `ProductInfo`, `Inbound`, `RobotStatus`가 핵심 테이블입니다. 정의는 `create_table.sql`입니다.

### 코드 흐름
코드상에서 `하나의 Task`는 보통 `transaction` 안의 한 단계로 실행됩니다. 즉, 서버는 여러 Task를 묶어도 로봇에게는 한 번에 하나씩 보냅니다. 핵심은 `TaskAllocator.assign_task()` -> `RobotController.task_callback()` -> `/task_completion` 순서입니다.

1. 
Task가 만들어집니다.
출고/입고 요청이 들어오면 `OrderReceiver.process_single_order()`에서 `task_id`, `task_type`, `priority`, `location`, `lift`가 채워진 `Task`가 생성됩니다.

1. 
서버가 그 Task를 transaction에 넣습니다.
`TaskAllocator.receive_task_list()`가 `TaskList`를 받고, `bundle_tasks()`에서 묶습니다.
출고면 `TaskFactory.create_outbound_tasks()`가 `O2 initial`, `상품 위치`, `O2 final` 형태로 만들고, 입고면 `create_inbound_tasks()`가 `입고 위치`, `최종 적치 위치`로 만듭니다.

1. 
가용 로봇이 선택됩니다.
`allocate_transaction()`에서 `available` 로봇을 고르고, 상태를 `busy`로 바꾼 뒤 첫 Task를 보냅니다.

1. 
그 Task가 로봇 서비스로 전달됩니다.
`assign_task()`가 `AllocateTask.Request`를 만들고 `/allocate_task_<robot_id>`를 호출합니다.

1. 
로봇은 Task를 받자마자 실제 작업을 수행합니다.
`task_callback()`에서 요청값을 내부 상태로 저장하고 `follow_path()`를 바로 실행합니다.
여기서:
`location`으로 목표 좌표를 찾고
`real_time_stopover_planning()`으로 중간 경로를 잡고
`move_pose()`로 nav2 이동을 하고
필요하면 `service_call_lift()`, `service_call_marker()`를 호출합니다.
출고 작업이면 `checking_task_is_out()`에서 사람의 픽업 버튼 완료를 기다립니다.

1. 
Task가 끝나면 로봇이 완료를 알립니다.
작업이 끝나면 `send_complete_task_topics()`가 `/task_completion`을 발행합니다.
중요한 점은, 현재 구현에서는 `/allocate_task` 서비스 응답도 이 작업이 끝난 뒤에 반환됩니다. 즉 이 서비스는 “할당 요청”이라기보다 “실행 완료까지 포함한 동기 호출”에 가깝습니다.

1. 
서버가 다음 단계로 넘어갑니다.
`process_task_completion()`이 완료를 받고,
같은 transaction에 다음 Task가 있으면 다시 `assign_task()`를 호출하고,
없으면 로봇을 `available`로 되돌립니다.

1. 
관제 화면이 갱신됩니다.
서버는 `/current_transactions`, `/unassigned_tasks`, `/robot_status`를 갱신하고, 관제 GUI는 이를 받아 현재 진행 상황을 표시합니다. 관련 코드는 `TaskSubscriber`, `PendingTaskSubscriber`, `RobotStatusSubscriber`입니다.
짧게 줄이면 이렇게 됩니다.
`주문/입고 입력 -> Task 생성 -> transaction에 편입 -> 가용 로봇 선택 -> /allocate_task_<id> 호출 -> 로봇이 실제 이동/리프트/아루코/픽업대기 수행 -> /task_completion 발행 -> 서버가 다음 Task 또는 종료 처리 -> 관제 화면 갱신`

### UI 분리

- 
소비자 주문페이지/관리자 주문관리 페이지 - 웹 (소비자/관리자 )

- 
모니터링 페이지 - Qt로 구현

- 
수정내용 (분리)
**관리자 페이지 (웹)**
-생산계획,주문관리
-품질검사 
-입출고내역
**모니터링 페이지** **Qt파트**
-대시보드 -다있어어도됨(주문 포함)
-생산모니터링
-품질검사 
-물류이송

### 결정

- 
PYQT5 사용

### 관제가 하는 일

- 
작업 생성 후 우선순위 정렬

- 
로봇할당

- 
에러 호출에 반응

- 
로봇 상태 모니터링 

- 
공정 상태 모니터링

#### 관제 기술조사_0408 (20774933)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20774933
**최종 수정**: v11 (2026-04-19 sync)

참고

| 항목 | Task Manager | Task Allocator | Traffic Manager |
|---|---|---|---|
| 역할 | 작업 생성·관리·상태 추적 | 어떤 로봇에 배정할지 결정 | 로봇 간 경로 충돌 방지 |
| 입력 | 작업 지시 (UI / 외부 시스템) | Task Manager의 할당 요청 | 로봇들의 위치·경로 정보 |
| 출력 | Task Allocator에 할당 요청 | 특정 로봇에 명령 전달 | 이동 허가 / 대기 신호 |
| 핵심 결정 사항 | 작업 우선순위 알고리즘 | 배정 알고리즘 (최적화?) | 충돌 회피 알고리즘 |
| 주요 리스크 | 작업 실패 시 재시도 정책 | 로봇 가용성 판단 기준 | 데드락 처리 |

# 관제에 필요한 컴포넌트

## [Task Manager](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20742182/Task+Manager?draftShareId=1b15ae16-9f57-483b-8b89-7352afa9edff)

### 역할 정의
큰 단위의 작업(`work_order`)을 작은 단위의 작업(`Task`)으로 나누어 Task Allocator에게 넘기는 일을 수행한다.

### 기능 정의

### 인터페이스 정의

### 기술 스택 후보

### 미결 사항 / 리스크

## [Task Allocator](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21332000/Task+Allocator?draftShareId=174fbd23-4cf2-4b38-b13a-a36df38e5c15)(Task Manager 하위)

### 역할 정의

- 
가용가능 로봇 목록과 작업 조건을 받아 최적의 로봇을 선택하여 작업을 할당한다.

### 기능 정의

### 인터페이스 정의

### 기술 스택 후보

### 미결 사항 / 리스크

## [Traffic Manager](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21037116/Traffic+Manager?draftShareId=2774255b-19a6-446b-b03e-ecc3317bd2d1)

### 역할 정의

### 기능 정의

### 인터페이스 정의

### 기술 스택 후보

### 미결 사항 / 리스크
**Task Flow**
생산 요청 or 출고 요청이 들어왔다.
`customer_order`: 검토 중인 주문(사무실)
`work_order`: 승인된 주문(공장 관리자)
`Task:`work_order의 한 item을 만들기 위해 진행해야 하는 작은 실행 단위
**공장 관리자**

1. 
사무실에서 넘어온 `work_order`가 pyqt에 우선순위가 반영된 상태로 띄움

1. 
`work_order` 중에 생산할 제품을 checkbox로 선택하고, 생산 시작 버튼을 누르기
**관제 시스템**

1. 
`work_order`들의 우선순위에 따라서 시작한다.

1. 
`work_order`를 세부적인 Task들로 나눈다.

1. 
각 Task를 상황에 맞는 로봇에게 할당한다.

1. 
Task 진행 중에 AMR들의 위치를 확인하고, 교착 상태를 해결한다.
**A제품 10개 생산 시나리오** 
work_order: A제품 10개 생산
item_id: A제품 1개
Task: 생산 Task(5개), 적재 Task(2개)
**Task manager**

- 
work_order에서 A제품 10개에 대한 item_id를 만들어요.

- 
item_id별로 task 단위로 쪼개요.

- 
Task allocator한테 넘겨줘요

- 
이 task를 누가 할지 정해요
동일한 item_id는 아래 진행 순서를 지켜야한다.

생산 Task

1. 
주형 제작(로봇팔), 주조 구역 이동(AMR)

1. 
탈형 & 상차(로봇팔)

1. 
후처리 구역 이동(AMR)

1. 
자동 수거 위치 이동(AMR)

1. 
적재 구역 이동(AMR)
적재 Task(AMR이 적재구역에 도착한 상태)

1. 
하차(로봇팔)

1. 
적재(로봇팔), 대기구역으로 이동(AMR)
출고 Task

1. 
적재 구역 이동(AMR)

1. 
출고 & 상차(로봇팔)

1. 
출고구역으로 이동(AMR)
후처리 비전 노드 - 검사 완료 상태를 바꾸기
사람 - 하차(후처리 중으로 상태 전환), 후처리, 비전 검사 투입(컨베이어에 올리기)
올리고, 지나가고, 멈추고, 비전검사하고, 언로딩, 4초 뒤에 끝나는 신호를 보낸다.

#### 관제 기술조사_0414 (27525538)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/27525538
**최종 수정**: v2 (2026-04-19 sync)

### 초안
'만들어진 제품 10개가 모두 양품이라고 장담 못함'
주문 10개 → 
양품 + 불량품 = 총 개수 
양품 개수 >= 발주 정보 수량 → 관제 시스템안에서, 수량을 하나씩 생산하도록 짜야겠네요. 한번에 10개 x, 1개씩 
**구체화**

### 1. 관제 시스템의 핵심 워크플로우 (Task Dispatching)
관제 서버는 전체 주문(Order)을 로봇이 수행 가능한 최소 단위의 태스크(Task)로 쪼개고, 공정 상태에 따라 이를 실시간으로 배분합니다.

- 
**Task Manager vs Task Dispatching**

  - 
**Task Manager (주체/컴포넌트):** "누가 하는가?"에 대한 답입니다. 전체 생산 공정을 관리하고, 어떤 작업이 남았는지, 어떤 로봇이 노는지 감시하는 **소프트웨어 모듈** 그 자체를 의미합니다.

  - 
**Task Dispatching (행위/프로세스):** "무엇을 하는가?"에 대한 답입니다. 태스크 매니저가 가지고 있는 작업 목록 중 하나를 특정 로봇에게 '전달하고 실행 명령을 내리는 구체적인 동작'을 의미합니다.

- 
**Allocator vs Dispatcher**
엄밀히 따지면 단계가 다르지만, 이번 프로젝트 수준에서는 **하나의 모듈**로 보셔도 무방합니다.

- 
**Task Allocator (할당):** **선택**의 단계입니다. 여러 대의 로봇 중 가장 적합한 로봇을 고르는 알고리즘(예: 가장 가까운 로봇, 배터리가 많은 로봇 등)에 집중합니다.

- 
**Task Dispatcher (배차/전송):** **실행**의 단계입니다. 선택된 로봇에게 실제로 MQTT 메시지를 보내고, 로봇이 수락했는지 확인하는 통신 과정에 집중합니다.
**💡 팁:** 발표 자료에는 **`Task Dispatcher`**라는 용어를 쓰면서 "상태에 따른 최적 할당(Allocation) 로직을 포함한다"고 설명하는 것이 가장 깔끔합니다.

****
****
****
| 단계 | 명칭 | 설명 |
|---|---|---|
****
****
| Step 1 | Order Entry | 외부(MES/ERP)로부터 발주 정보(제품명, 총 수량) 수신 |
****
****
| Step 2 | Task Decomposition | 10개 묶음이 아닌, **'1개 단위'**의 독립적인 생산 태스크로 분할 |
****
****
| Step 3 | Task Queueing | 생성된 태스크들을 **우선순위 큐(Priority Queue)**에 삽입 |
****
****
| Step 4 | Feedback Loop | 검사 결과(양품/불량)에 따라 큐를 동적으로 업데이트 |

### 2. 생산 관리 알고리즘 (Pseudo Code)
제시하신 로직을 바탕으로, 불량 발생 시 즉시 보충 생산이 가능한 구조로 정리했습니다.

### 3. 우선순위 큐(Priority Queue)의 활용
B제품 생산 중 A제품의 불량이 발생했을 때, 관제 서버는 **작업의 긴급도**를 판단해야 합니다.

- 
**Heap 구조 활용:** `heapq.heappush(q, (priority_level, timestamp, task_id))`

  - 
**1순위 (Priority Level):** 재작업(Rework)인 경우 일반 작업보다 낮은 숫자(높은 우선순위) 부여.

  - 
**2순위 (Timestamp):** 우선순위가 같다면 먼저 들어온 주문부터 처리(FIFO).

- 
**의미:** "B제품을 만드는 중이라도, A제품의 불량 보충이 공정 효율상 더 급하다면 관제가 즉시 순서를 바꿔 로봇에게 전달"하는 역할을 수행합니다.

### 관제 시스템의 핵심 모듈

### ① Task Manager (작업 관리자)

- 
**역할:** "무엇을 언제 할 것인가?"를 결정합니다.

- 
**기능:** 

  - 
**태스크 분할:** 큰 주문(예: 제품 10개)을 로봇이 수행할 수 있는 최소 단위 태스크(예: 1개 생산/이동)로 쪼갭니다.

  - 
**우선순위 스케줄링:** 작업의 긴급도에 따라 순서를 정합니다. 특히 **불량 발생 시 재작업**이나 **긴급 주문**을 처리하기 위해 **우선순위 큐(Priority Queue)**를 관리하는 것이 핵심입니다.

### ② Task Allocator / Dispatcher (배차 담당자)

- 
**역할:** "이 일을 **누구**에게 줄 것인가?"를 결정하고 **명령**을 내립니다.

- 
**기능:** 

  - 
**Allocator (할당):** 현재 가동 가능한 로봇 중 **가장 적합한 대상**을 선정합니다. (거리, 배터리 잔량, 현재 상태 등 고려)

  - 
**Dispatcher (배차):** 선정된 로봇에게 실제 명령(MQTT/ROS 2 메시지)을 보냅니다. 단순히 던지는 게 아니라 로봇이 명령을 잘 받았는지, 실행을 시작했는지까지 확인합니다.

### ③ State Manager (상태 관리자)

- 
**역할:** "지금 로봇들이 어디서 뭐 하고 있는가?"를 기록합니다.

- 
**기능:** 

  - 
**실시간 모니터링:** 각 로봇의 위치(x, y), 속도, 작업 진행률, 에러 상태 등을 수집합니다.

  - 
**데이터 동기화:** 수집된 상태 데이터를 DB에 저장하거나 대시보드(UI)에 뿌려주어 사용자가 현재 상황을 알 수 있게 합니다.

### ④ Traffic Manager (교통 제어/스케줄러)

- 
**역할:** 로봇끼리 마주쳤을 때 "1호기가 먼저 가고 2호기는 대기해"라고 우선순위를 정해주는 역할을 합니다. (이것이 관제의 핵심 역량 중 하나입니다.)

- 
**기능:** 

  - 
**경로 간섭 체크:** 로봇들의 이동 경로가 겹치는지 실시간으로 계산합니다.

  - 
**교통 정리:** 교차로나 좁은 길에서 "A 로봇 정지, B 로봇 우선 통과" 같은 하위 명령을 내려 교착 상태(Deadlock)를 방지합니다.

## 데이터 흐름 (Workflow)
관제 시스템 내부에서 데이터는 다음과 같은 순서로 흐릅니다.

1. 
**Input:** 주문(Order)이 들어오면 `Task Manager`가 태스크를 생성하여 큐에 쌓습니다.

1. 
**Matching:** `Task Allocator`가 `State Manager`를 통해 노는 로봇을 확인한 후 작업을 배정합니다.

1. 
**Command:** `Task Dispatcher`가 로봇에게 명령을 쏩니다. (이때 외부 통신은 주로 **MQTT**를 사용합니다.)

1. 
**Feedback:** 로봇이 작업을 수행하며 상태를 보고하면 `State Manager`가 기록합니다. 만약 '불량'이나 '에러' 보고가 들어오면 다시 `Task Manager`로 보내 재작업을 계획합니다.

### Q 이렇게 역할을 세분화 시켜야 하는가
=> **시스템의 규모와 복잡도**에 따라 다름
 하지만 지금 진행하시는 프로젝트(AMR 3대, 로봇 팔 2대 협업) 수준에서는 이 역할들을 **논리적으로는 구분하되, 실제 코드는 하나로 합쳐서 구현**하는 것이 가장 현실적입니다.
반드시 '파일을 3~4개로 쪼개야 한다'는 압박을 가질 필요는 없지만, **코드 내에서 함수나 클래스 단위로라도 역할을 나누어야 함**
**장점**

- 
**예외 상황 처리가 쉬워짐:** 단순히 "로봇아 가라"라고만 짜면, 가던 중에 로봇이 고장 나거나 불량이 발생했을 때 시스템이 멈춰버립니다. 역할을 나눠두면 `State Manager`가 에러를 감지하고, `Task Manager`가 즉시 다른 로봇에게 일을 넘기는 처리가 가능해집니다.

- 
**유지보수:** "로봇을 고르는 기준(Allocator)"만 바꾸고 싶을 때, 전체 코드를 건드리지 않고 해당 로직만 수정할 수 있습니다.

- 
**확장성:** 나중에 로봇이 3대에서 10대로 늘어나도 관제 시스템의 기본 틀(두뇌)은 그대로 쓸 수 있습니다.
시나리오3

## Q. 배터리 임계치를 두 단계로 나누어 관리할 것인가

- 
**Warning (예: 20%):** 현재 수행 중인 task까지만 마치고 충전소로 이동.

- 
**Critical (예: 10%):** 즉시 task를 중단하고 재할당 후 충전소 이동.
Q. AMR이 모두 사용중일때 재할당을 어떻게 할 것인가
-1순위 유휴중인 로봇
-2순위 일이 빨리 끝나는 로봇[유휴중인 로봇이 없을때]
그러면 일이 얼마나 진행중인가도 다 모니터링해야됨
-3순위 가장 가까운 로봇
-모든 로봇이 바쁘다면 대기열에 추가하고 대기
-1,2,3 순위는 가중치를 부여하여 계산
IF 생산 구역에서  상차 직후 배터리가 부족해진다면?

- 
이상황까지 고려할 필요는 없긴함

- 
대신 가상데이터 작성시 조건 넣고 구현해야됨
AMR1,2,3이 이동하면서 경로 점유당하는 상황은 어디서 보여줄거임 그냥 자연스럽게 흘러가도 발생함?

### 4.1 VLA (3276898)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3276898
- **빈 페이지**

> 주: `3276898` 은 초기 구조에서 생성된 placeholder 로 현재는 빈 페이지. 실제 VLA 자료는
> §3.2 하위 `VLA (Tech_Research) (7405754)` 에 있음.

---

### 4.2 LLM (3703098)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3703098
- **빈 페이지**

> 주: 실제 LLM/VLM 자료는 §3.2 하위 `LLM/VLM (tech_research) (7438588)` 에 있음.

---

### 연동테스트 (21856283)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21856283
**최종 수정**: v41 (2026-04-19 sync)

- 
UI 레벨부터 HW 레벨까지 정의된 통신 프로토콜로 통신 완료

- 
UI (Monitoring Service-PyQt) ↔︎ HW (Image Publishing Service-Jstson) 연동 Test 완료

- 
UI (Monitoring Service-PyQt) ↔︎ HW (AMR) 배터리 모니터링 완료 (SSH-Ok, ROS2-Fail)

  - 
해결: 팀별 공유기 할당 받으면 고정 IP로 사용하면 ROS2 통신 가능

****
****
****
****
****
****
****
****
****
| Test Case ID | Task Name | From | To | Protocol | Description | Method / Topic | P/F | 받을 데이터 타입 (ex) json) |
|---|---|---|---|---|---|---|---|---|
| Ordering Management Service <-> Interface Service |
| Test-001-A |   | Ordering Management Service | Interface Service | HTTP | Ordering Management Service의 요청을 API로 Interface Service에 전달 |   |   |   |
[](https://drive.google.com/file/d/1vzfgrG4yUtE0_vO37reJsaOHHZfdAkhv/view?usp=drive_link)
| Test-001-B |   | Interface Service | Ordering Management Service | HTTP | Interface Service의 처리 결과를 API로 Ordering Management Service에 전달테스트 영상 |   |   |   |
| Ordering Service <-> Interface Service |
| Test-002-A |   | Ordering Service | Interface Service | HTTP | Ordering Service의 요청을 API로 Interface Service에 전달 |   |   |   |
[](https://drive.google.com/file/d/1CXnswfK-R2axemyW8WOl0sna0jTduVjC/view?usp=drive_link)
| Test-002-B |   | Interface Service | Ordering Service | HTTP | Interface Service의 처리 결과를 API로 Ordering Service에 전달테스트 영상 |   |   |   |
| Interface Service -> Management Service |
[](https://drive.google.com/file/d/1iEA3b8O_URi006H89IK_rldrxPV3uZbk/view?usp=drive_link)
| Test-003-A |   | Interface Service | Management Service | TCP | Interface에서 Management Service로 주문 정보 전송테스트 영상 |   |   |   |
| Monitoring Service <→ Management Service |
| Test-004-A |   | Monitoring Service | Management Service | TCP | Monitoring Service에서 Management Service로 명령 전송 |   |   |   |
[](https://drive.google.com/file/d/1WvYxoO2Y1IH8-kacYJCpd5dQt0880a_O/view?usp=drive_link)
| Test-004-B |   | Management Service | Monitoring Service | TCP | Management Service에서 Monitoring Service로 상태 데이터 전송테스트 영상 |   |   |   |
| DB Service → Interface Service |

[](https://drive.google.com/file/d/1qAic2qEVWcMRbSHRP4KemHbTu-XliHNH/view?usp=drive_link)
| Test-005-A |   | DB Service | Interface Service | TCP(Postgresql  protocol) | Interface Service에서 DB에 있는 주문 정보를 조회테스트 영상 |   |   |   |
| DB Service <→ Management Service |

| Test-006-A |   | DB Service | Management Service | TCP(Postgresql protocol) | Management service에서 DB로 쓰기 |   |   |   |

[](https://drive.google.com/file/d/1frbXpcOM7PmvjW8qPlBiptRKpUzugRRm/view?usp=drive_link)
| Test-006-B |   | Management Service | DB Service | TCP(Postgresql protocol) | Management service에서 DB로 각종 로봇 상태 읽기테스트 영상 |   |   |   |
| Management Service <→ AI Service |
| Test-007-A |   | Management Service | AI Service | TCP | Management Service에서 AI Service로 이미지와 함께 추론 요청 |   |   |   |
[](https://drive.google.com/file/d/1vl5o6pdy8xXYvuLX3o2882_4-arq4bI3/view?usp=drive_link)
| Test-007-B |   | AI Service | Management Service | TCP | AI Service에서 Management Service로 추론 결과 반환테스트 영상 |   |   |   |
| Image Publishing Service -> Management Service |
[](https://drive.google.com/file/d/1pU2Z49eIee0FHWyrr_Td90jDU8-kRlkf/view?usp=drive_link)
| Test-008-A |   | Image Service | Management Service | TCP | Image Service에서 Management Service로 이미지와 metadata 전송테스트 영상 |   |   |   |
| HW Controller <-> Management Service |
``
| Test-009-A |   | HW Controller | Management Service | MQTT | HW Controller(Publisher)가 Broker에 메시지를 Publish | motor/ |   |   |
[](https://drive.google.com/file/d/16JBiMS1KXCqay4B5HxZ6eCjgP4YoWh3m/view?usp=drive_link)
``
| Test-009-B |   | Management Service | HW Controller | MQTT | Management Service(Subscriber)가 Broker의 topic을 Subscribe테스트 영상 | motor/ |   |   |
| Management Service <→ Robot Arm |
| Test-010-A |   | Management Service | Manufacturing Service | ROS2 | Management Service에서 Manufacturing Arm으로 데이터 전송 |   |   |   |
| Test-010-B |   | Manufacturing Service | Management Service | ROS2 | Manufacturing Arm에서 Management Service로 데이터 전송 |   |   |   |
| Test-010-C |   | Management Service | Stacking Service | ROS2 | Management Service에서 Stacking Arm으로 데이터 전송 |   |   |   |
| Test-010-D |   | Stacking Service | Management Service | ROS2 | Stacking Arm에서 Management Service로 데이터 전송 |   |   |   |
| Management Service <→ Transport Service |
[](https://drive.google.com/file/d/14nMD1h357-WxBtBT_S3JENpxlLYWOsmM/view?usp=drive_link)
| Test-011-A |   | Management Service | TransportService | ROS2 | Management Service에서 Transport Service(AMR)로 데이터 전송테스트 영상 |   |   |   |
[](https://drive.google.com/file/d/1lnR-_RJwO0vsEVZdoG4Ad1rNWGJbjsNB/view?usp=drive_link)
| Test-011-B |   | TransportService | Management Service | ROS2 | Transport Service(AMR)에서 Management Service로 데이터 전송테스트 영상 |   |   |   |

:50051) 로 공장 상태 실시간 스트림 수신

- 
**Admin/Customer 웹** — HTTP REST (:8000) + 일부 WebSocket 로 브라우저와 통신
**이유:**

- 
gRPC 는 브라우저 직접 지원이 약함 → 웹은 HTTP REST 가 간편

- 
공장 현장은 저지연 실시간 스트림이 필요 → gRPC 가 적합

- 
한 서비스(Interface + Management) 가 두 스택을 함께 서비스하면 트래픽·책임 섞임 → **별도 프로세스로 분리**

## 1. Monitoring Service (PyQt) ↔ Management Service

### 1.1 개요
**Monitoring Service** 는 공장 현장 PC 에 설치된 **PyQt5 데스크톱 앱**입니다. 작업자가 실시간으로 생산 상태·알람·카메라 영상을 보고 생산 시작 버튼을 누르는 용도입니다.
서버 쪽은 **Management Service**(gRPC :50051)로, PyQt 와 `.proto` 로 정의된 메시지 규약으로 통신합니다.
**왜 gRPC 인가?**

- 
HTTP REST 로는 "서버가 먼저 알려주는" 방식을 구현하기 어려움 (폴링 필요)

- 
gRPC **server streaming** 은 서버에서 이벤트가 생기면 즉시 클라이언트로 밀어줌

- 
Protobuf 스키마로 타입 안전 — 서버/PyQt 양쪽에서 자동 생성된 코드 사용

### 1.2 제공 RPC (8개)

| RPC | 종류 | 역할 |
|---|---|---|
``
``
| Health | unary | 연결 확인 — health_check() |
``
| StartProduction | unary | 승인된 주문을 생산 시작 → work_order + items 생성 |
``
| ListItems | unary | 현재 진행 중 item 목록 (order_id/stage 필터) |
``
| AllocateItem | unary | 로봇 배정 스코어링 |
``
| PlanRoute | unary | Traffic Manager — Waypoint + Dijkstra + Backtrack Yield |
``
| ExecuteCommand | unary | 로봇에 명령 발행 (ROS2/MQTT 어댑터로 분기) |
``
****
| WatchItems | stream | items.cur_stage 전이 이벤트 (1Hz polling 기반) |
``
****
| WatchAlerts | stream | alerts 테이블 신규 row → 즉시 push |
``
****
| WatchCameraFrames | stream | 카메라 JPEG 프레임 (condvar pub/sub 기반) |
프로토 파일: `backend/management/proto/management.proto`

### 1.3 PyQt 측 핵심 구성요소

| 파일 | 역할 |
|---|---|
``
| monitoring/app/management_client.py | gRPC 채널 생성(keepalive 4 옵션) + 스텁 래핑 |
``
``
| monitoring/app/workers/item_stream_worker.py | WatchItems 구독 QThread, 자동 재연결 3s |
``
``
| monitoring/app/workers/alert_stream_worker.py | WatchAlerts 구독 QThread |
``
``
| monitoring/app/workers/camera_frame_worker.py | WatchCameraFrames 구독 QThread (Stage B) |
``
``
| monitoring/app/workers/start_production_worker.py | StartProduction 비동기 호출 (UI 프리즈 방지) |
``
| monitoring/app/pages/dashboard.py | 대시보드 (FastAPI 일부 수치 + gRPC 이벤트) |
``
| monitoring/app/pages/production.py | 공정 단계 + item 진행 테이블 (WatchItems) |
``
| monitoring/app/pages/schedule.py | 승인 주문 풀 + 생산 시작 버튼 |
``
| monitoring/app/pages/quality.py | 카메라 라이브 뷰 + 불량 통계 (WatchCameraFrames) |
````
| monitoring/app/pages/logistics.py, map.py | 이송·맵 |
``
| monitoring/app/widgets/camera_view.py | QPixmap 렌더 + PASS/FAIL 오버레이 |

### 1.4 스트리밍 워커 패턴 (공통)

- 
Qt 메인 스레드는 UI 만 담당, 워커는 QThread 에서 gRPC 소비 → 화면 프리즈 없음

- 
signal/slot 으로 스레드 경계 안전하게 넘김

### 1.5 Stage A → Stage B 진화 (2026-04-15)
**Stage A:** `GetLatestFrame` unary RPC + QTimer 1Hz polling

- 
구현 간단했지만 **최대 1초 지연**, 같은 프레임 중복 수신

- 
이후 Stage B 전환으로 `GetLatestFrame` RPC **완전 제거**됨
**Stage B (현재):** `WatchCameraFrames` server streaming + `threading.Condition.notify_all()` pub/sub

- 
**첫 프레임 지연 2ms** — Jetson 이 push 하는 즉시 PyQt 에 전달

- 
재연결 시 `after_sequence` 로 끊긴 지점부터 이어받기

### 1.6 gRPC keep-alive (2026-04-15)
서버 재기동 후 PyQt 카메라 뷰가 멈추는 이슈를 해결하기 위해 HTTP/2 ping 을 전 구간에 적용:
이후 네트워크 단절 시 **최대 40초** 내 예외 발생 → worker 자동 재연결.

### 1.7 실시간 UX 개선

- 
**생산 시작 비동기화:** `_do_start` 가 `StartProductionWorker(QThread)` 를 spawn 하여 UI 프리즈 제거

- 
**Critical alert 모달:** severity=critical 은 토스트 대신 `QMessageBox.critical()` 로 ack 보장 (같은 alert_id 는 1회만)

- 
**사이드바 토글:** `Ctrl+B`

- 
**카메라 영상:** `CameraLiveView.set_frame_bytes()` 로 JPEG → QPixmap 렌더 + 기존 PASS/FAIL 오버레이 유지

### 1.8 검증 수치

- 
gRPC 채널 keepalive 4 옵션 전 구간 적용

- 
smoke test: `stub.WatchCameraFrames` 5프레임 수신, 첫 프레임 2ms

- 
E2E: 승인 주문 → 생산 시작 → item 150개 생성 → WatchItems 로 셀 갱신 확인

## 2. Ordering Management Service (Admin PC) ↔ Interface Service

### 2.1 개요 (초보자 설명)
**Ordering Management Service** 는 Admin PC 의 관리자용 **Next.js 웹페이지**입니다. 주문 목록을 조회·승인·거절, 대시보드 KPI, 품질·물류 모니터링을 제공합니다.
**Interface Service** 는 `backend/app/` 의 **FastAPI REST 서버**(:8000)로, Admin/Customer 모두 공용으로 사용합니다.

### 2.2 Admin 페이지 구성 (Next.js)
`src/app/` 경로 기준:

| 라우트 | 용도 |
|---|---|
``
| /admin/login | 관리자 게이트 (env 비밀번호, 모르는 사람 차단 수준) |
``
| /admin | 주문 관리 — 목록/필터/상태 변경 |
``
| /orders | 관리자용 주문 상세 조회 |
``
| /production | 생산 현황 대시보드 (KPI 차트) |
``
| /quality | 품질 검사 현황 (불량률·검사 이력) |

### 2.3 REST 엔드포인트 (FastAPI include_router)
`backend/app/main.py` 에 등록된 라우터:
**대표 API 예:**

| Method | Path | 용도 |
|---|---|---|
``
| GET | /api/orders | 주문 목록 (필터링) |
``
| POST | /api/orders | 주문 생성 |
``
| GET | /api/orders/{id}/details | 주문 상세 |
``
| PATCH | /api/orders/{id} | 상태 변경 (approve/reject 등) |
``
| GET | /api/products | 제품 카탈로그 9종 |
``
| GET | /api/production/live | 실시간 공정 현황 |
``
| GET | /api/quality/stats | 품질 KPI |
``
| GET | /api/alerts | 알람 최근 N건 |
``
| WS | /ws/dashboard | 대시보드 실시간 업데이트 (선택, V6 에서 gRPC 로 대체 진행 중) |

### 2.4 Next.js → FastAPI 호출 방식
**방법 1: Next.js rewrite (동일 오리진)**

- 
브라우저가 `/api/*` 호출 → Next.js 가 FastAPI 로 프록시

- 
CORS 이슈 없음 · API base URL 을 환경마다 바꿀 필요 없음
**방법 2: 절대 URL (필요 시)**

- 
기본 `API_BASE = ""` (상대 경로) 사용 → rewrite 기반

- 
`src/lib/api.ts` 가 fetch 헬퍼 (`fetchOrdersByEmail`, `fetchOrderDetails` 등)

### 2.5 Pydantic v2 스키마 검증
FastAPI 는 요청 본문을 Pydantic 모델로 자동 검증:
잘못된 요청은 자동으로 **422 Unprocessable Entity** + 자세한 에러 JSON 반환 — 관리자 웹에서 그대로 토스트 표시.

### 2.6 2026-04-14~15 Admin 관련 변경

- 
레거시 제품 4종 삭제 → 관리자 제품 관리 페이지에서 9종만 노출

- 
`/api/production/live`, `/api/quality/stats` 등은 Mgmt gRPC 로 점진 이전 가능하도록 추상화 유지

- 
WebSocket `/ws/dashboard` 는 V6 에서 점진 단종 중 (PyQt 쪽은 이미 `CASTING_WS_ENABLED=0` 기본) — 관리자 웹은 당분간 유지

## 3. Ordering Service (Customer PC) ↔ Interface Service

### 3.1 개요 (초보자 설명)
**Ordering Service** 는 고객이 브라우저로 접속하는 **주문 포털**입니다 (`src/app/customer/`). 카테고리 선택부터 주문 완료까지 5단계 플로우.
**Interface Service** 는 관리자와 동일한 FastAPI (:8000) — 같은 API 위에 다른 프론트엔드가 얹힌 형태.

### 3.2 고객 포털 구성

| 라우트 | 용도 |
|---|---|
``
| /customer | 주문 작성 (5단계 플로우) |
``
| /customer/lookup | 주문 번호/이메일 조회 |
``
| /customer/orders | 주문 이력 리스트·상세 |

### 3.3 주문 5단계 플로우
페이지: `src/app/customer/page.tsx` (1200+ 줄의 대형 단일 페이지 컴포넌트 — 모든 단계 상태 로컬 보관)

### 3.4 제품 카탈로그 9종 (현재 UI)

| ID | 이름 | category |
|---|---|---|
| R-D450 / R-D500 / R-D550 | 원형 맨홀뚜껑 KS D-450 / 500 / 550 | round |
| S-400 / S-450 / S-500 | 사각 맨홀뚜껑 KS S-400 / 450 / 500 | square |
| O-450 / O-500 / O-550 | 타원형 맨홀뚜껑 KS O-450 / 500 / 550 | oval |
각 카테고리 대표 이미지(round.jpg / square.jpg / oval.jpg) 하나로 카드 표시.
스펙 옵션은 `products.option_pricing_json`·`diameter_options_json`·`thickness_options_json`·`materials_json`·`load_class_range` 에 저장.

### 3.5 고객용 주요 API
직접 호출 예:

### 3.6 국제화 방향 / 다국어 (메모)
현재 한국어 고정. 향후 i18n 도입 시 `next-intl` 또는 `react-i18next` 검토.

### 3.7 UX 개선 이력 (2026-04-14)

- 
제품 카드 배경 `bg-gray-100` → `bg-white` (시각적 깔끔함)

- 
카테고리 필터 버튼 위치 상단 고정

- 
카테고리별 대표 이미지 적용

- 
30종 초안 → UI 복잡도 고려해 9종으로 축소 (최종)

## 4. 공통 운영 사항

### 4.1 Next.js 개발 환경 주의점

- 
**allowedDevOrigins** 를 `next.config.ts` 에 LAN IP 등록 (메모리 기록됨)

- 
기본 API base URL 은 빈 문자열(`""`) — rewrite/proxy 기반 동일 오리진 호출

### 4.2 포트·환경변수

| 서비스 | 포트 | env |
|---|---|---|
``
| Interface Service (FastAPI) | :8000 | DATABASE_URL 필수 |
````
| Management Service (gRPC) | :50051 | DATABASE_URL + MGMT_* |
``
| Next.js (Admin+Customer) | :3000 (dev) | NEXT_PUBLIC_ADMIN_PASSWORD (관리자 게이트) |

### 4.3 WebSocket 단종 방향

- 
PyQt 쪽은 **완전히 gRPC 로 전환** 완료 (`CASTING_WS_ENABLED=0` 기본)

- 
Admin 웹의 `/ws/dashboard` 는 당장 유지하지만 추후 `WatchItems`/`WatchAlerts` gRPC-Web 으로 이전 검토

### 4.4 mTLS 옵션 (운영 권장)

- 
gRPC 전 구간 mTLS 스위치: `MGMT_GRPC_TLS_ENABLED=1`

- 
`scripts/gen_certs.sh` 로 자체 CA + server/client cert 발급

### 4.5 인증 수준

- 
Admin 웹: 단순 env 비밀번호 게이트 (기본 방지용, 실제 인증 아님)

- 
Customer 웹: 인증 없음 — 이메일만 제공, 주문 번호로 조회

- 
PyQt: 내부망(Tailscale) 전제, 별도 인증 없음 (운영 시 mTLS 권장)

### 4.6 작업 로그 (로컬 웹)

- 
`docs/worklog/index.html` — 일별 진행 로그 인덱스

- 
`docs/worklog/2026-04-14_v6_migration.html` — PyQt gRPC 직결 Phase 1~4

- 
`docs/worklog/2026-04-15_stageA_live_camera.html` — 카메라 뷰 1차 (폴링)

- 
`docs/worklog/2026-04-15_stageB_stream.html` — 카메라 Server Streaming

- 
`docs/worklog/2026-04-15_post_stream_hw_integration.html` — keepalive, cleanup

- 
`docs/worklog/2026-04-14_15_full_report.html` — 이틀 전체 상세 보고서

## 5. 요약

| # | UI | 서버 측 | 프로토콜 | 포트 | 핵심 라이브러리 |
|---|---|---|---|---|---|
****
****
| ① | PyQt Monitoring (공장 현장) | Management Service | gRPC (server streaming) | :50051 | grpcio 1.80, protobuf 6.33, PyQt5 5.15 |
****
| ② | Admin PC Next.js (관리자) | Interface Service | HTTP REST + WebSocket | :8000 | Next.js 16, FastAPI, Pydantic v2 |
****
| ③ | Customer PC Next.js (주문) | Interface Service | HTTP REST | :8000 | Next.js 16, FastAPI, Pydantic v2 |
**핵심 설계 메시지:**

- 
공장 현장은 **실시간 스트림**이 최우선 → gRPC

- 
웹(Admin/Customer) 은 브라우저 친화성 최우선 → HTTP REST

- 
두 스택이 **같은 PostgreSQL** 을 공유하지만 **프로세스는 분리** → 한쪽 장애가 다른 쪽을 멈추지 않음

#### Server <--> HW 통신 인터페이스 구현 (31228367)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31228367
**최종 수정**: v6 (2026-04-19 sync)

# Server <--> HW 통신 인터페이스 구현
**작업 기간:** 2026-04-14 ~ 2026-04-15
**정리 관점:** Management Service(서버) 가 공장 하드웨어 3종(검사 카메라 · 컨베이어 · 협동로봇)과 어떤 방식으로 통신하도록 구현했는지, 왜 그 방식을 골랐는지.

## 0. 전체 그림 한 장

- 
**①** Management ↔ Jetson (Image Publisher)

- 
**④** Jetson ↔ ESP32 (HW Control, 컨베이어 제어)

- 
**③** Management ↔ JetCobot (Stacking, 협동로봇) — 과도기 SSH, 추후 ROS2
각 구간은 서로 독립된 기술 스택으로, 한 구간이 고장나도 다른 구간에 전파되지 않도록 설계했습니다.

## 1. Management Service ↔ Image Publishing Service (Jetson)

### 1.1 개요
**목적:** 검사 카메라(USB, Logitech C920) 로 촬영한 주물 영상을 서버로 실시간 전송하고, PyQt 모니터링 앱 "품질 검사" 페이지에서 같이 볼 수 있게 함. 더불어 IP(검사) 공정 진입 순간의 스냅샷을 AI Server 로 업로드해 학습 데이터셋을 축적.
**하드웨어:**

- 
**Jetson Orin NX 16GB** (JetPack R35.5, Ubuntu 20.04, Python 3.8)

- 
Tailscale IP `100.77.62.67`

- 
USB 카메라 Logitech HD Pro Webcam C920 → `/dev/video0`
**프로토콜 선택:** **gRPC** (HTTP/2 위에서 동작하는 바이너리 RPC 프레임워크)

### 1.2 왜 gRPC 인가?

| 후보 | 장점 | 단점 | 채택? |
|---|---|---|---|
| HTTP REST | 단순, 디버그 쉬움 | polling 구조 → 지연 큼 | ❌ |
| WebSocket | 양방향 | 스키마 없음, 로드밸런서 까다로움 | ❌ |
| MQTT | pub/sub 간결 | 이미지(수십 KB) 에 낭비, Broker 의존 | ❌ |
****
****
| gRPC | 서버 스트리밍, .proto 스키마, HTTP/2 다중화 | 학습 곡선 | ✅ |

### 1.3 두 단계로 구현 — 폴링 → 스트리밍
**Stage A (2026-04-15 오후):** `GetLatestFrame` 단발 RPC + PyQt 에서 1Hz polling

- 
동작은 했지만 **최대 1초 지연**, 같은 프레임 중복 수신 문제
**Stage B (현재 방식):** `WatchCameraFrames` server-streaming RPC + Jetson push 시점에 즉시 전달

- 
**첫 프레임 지연 2ms** (측정치), 2fps Jetson push 를 그대로 전달

- 
핵심: 서버 내부에 `threading.Condition` 기반 pub/sub 도입 (`image_sink.push` → `notify_all`)
→ Stage A 의 `GetLatestFrame` RPC 는 호출 지점이 0이 되어 **완전 제거** (코드 140줄 감소, LatestFrameResponse → CameraFrameResponse 이름 정리).

### 1.4 구체적인 통신 흐름

### 1.5 안정화 — keepalive
처음 구현 후 "서버 재기동하면 PyQt 카메라 뷰가 멈춘다" 이슈 발생. 원인은 TCP 가 silently dead 상태여도 클라이언트가 모름.
해결: **HTTP/2 ping** 을 클라이언트·서버 모두에 설정.
이후 서버 재기동·Tailscale 일시 단절 시 **최대 40초** 내 예외 발생 → worker 자동 재연결.

### 1.6 관련 파일

| 경로 | 역할 |
|---|---|
``
````
| backend/management/proto/management.proto | ImagePublisherService.PublishFrames, ManagementService.WatchCameraFrames 정의 |
``
| backend/management/server.py | gRPC 서버 + keepalive + ThreadPool 32 |
``
``
| backend/management/services/image_sink.py | Condition.notify_all() 기반 pub/sub |
``
| backend/management/services/image_forwarder.py | IP 진입 시 스풀 + 배치 업로드 |
``
| backend/management/services/ai_client.py | AI Server SSH/SCP 업로더 (paramiko) |
``
| jetson_publisher/publisher.py | OpenCV → JPEG → gRPC client stream |
``
| jetson_publisher/systemd/casting-image-publisher.service | Jetson 자동 기동 |
``
| monitoring/app/workers/camera_frame_worker.py | PyQt QThread stream consumer |
``
| monitoring/app/widgets/camera_view.py | QPixmap 렌더 + PASS/FAIL 오버레이 |

### 1.7 검증 수치

- 
**첫 프레임 지연:** 2 ms (RTT 포함)

- 
**프레임률:** 2 fps (Jetson 2Hz 송신 그대로)

- 
**프레임 크기:** JPEG 100~120 KB

- 
**IP 진입 → AI Server 도착:** 22 초 (배치 flush 10s 기준)

## 2. Image Publishing Service (Jetson) ↔ HW Control Service (ESP32)

### 2.1 왜 Jetson 이 중간에 끼는가?
이전 V6 설계는 Management → ESP32 를 MQTT 로 직결할 계획이었으나, **새 V6 다이어그램**에서 Jetson 이 USB Serial 로 ESP32 를 갖도록 변경됨. 이유:

1. 
카메라와 컨베이어가 물리적으로 같은 공정 위치에 있음 (검사 순간 = 정지 순간)

1. 
Management 서버는 Mac/Linux 서버 역할만 — USB 포트·GPIO 없음

1. 
Jetson 이 이미 이미지 publisher 로 가동 중 → 추가 비용 0

### 2.2 하드웨어 구성

| 부품 | 값 | 비고 |
|---|---|---|
``
| ESP32 DevKitC V4 | CP2102 USB-UART | Jetson → /dev/ttyUSB0 |
****
| Baud | 115200 | 2026-04-15 에코 테스트로 확정 |
| TOF250 (Taidacent) × 2 | ASCII UART 9600 bps | TOF1 → GPIO16 (진입 감지), TOF2 → GPIO17 (카메라 앞) |
| 모터 JGB37-555 12V DC | L298N 드라이버 | ENA=GPIO25 (PWM), IN1=26, IN2=27 |

### 2.3 센서 주도 시나리오 (사용자 요구)
**중요:** Management 서버는 이 루프에 직접 관여하지 않음. 이미지만 별도 경로(①) 로 받음.

### 2.4 ESP32 펌웨어 v5.0
기존 v4.0 (`firmware/conveyor_controller/conveyor_controller.ino`) 의 성숙한 센서 로직을 그대로 재사용하면서 외부 통신만 Serial 로 교체:

- 
**유지:** TOF250 ASCII 파서, **500ms debounce**, **anti-crosstalk (raw2 && !raw1)** — TOF1 IR 940nm 가 TOF2 를 오염시키는 하드웨어 문제 대응

- 
**유지:** `MIN_RUN_MS 1초` — 모터 start 직후 TOF2 false trigger 차단

- 
**유지:** 5-state machine (IDLE → RUNNING → STOPPED → POST_RUN → CLEARING)

- 
**변경 1:** WiFi/MQTT 비활성 (`#define ENABLE_WIFI_MQTT 0`)

- 
**변경 2:** `ST_STOPPED` 의 5초 자동 탈출 제거 → Jetson 의 RUN 수신 시에만 POST_RUN 진입

- 
**변경 3:** Serial 라인 프로토콜 추가
**Serial 프로토콜**

| 방향 | 메시지 | 의미 |
|---|---|---|
``
| ESP → Jetson | BOOT:conveyor_v5_serial 1.1.0 | 부팅 완료 |
``
| ESP → Jetson | STATE:<NAME> | 상태 전이 (IDLE/RUNNING/STOPPED/POST_RUN/CLEARING) |
``
| ESP → Jetson | STOPPED | 센서2 감지 → 정지 완료 (촬영 요청) |
``
| ESP → Jetson | STARTED | RUN 수신 → 모터 ON 완료 |
``
| ESP → Jetson | DONE | POST_RUN 4s 경과 → 자동 정지 |
| Jetson → ESP | `RUN |   |
|   | \| | 터 재시작 명령 \| |
``
| Jetson → ESP | PING / STATUS / STOP / reset | 진단·수동 제어 |
``
| Jetson → ESP | sim_entry / sim_exit | 센서 없이 상태기 테스트 |
경로: `firmware/conveyor_v5_serial/conveyor_v5_serial.ino`

### 2.5 Jetson Serial Bridge 구현
`jetson_publisher/esp_bridge.py` — publisher 와 **같은 프로세스** 에서 독립 스레드로 실행.

- 
**환경변수 opt-in:** `ESP_BRIDGE_ENABLED=1`

- 
**자동 재연결:** Serial 끊기면 10초 backoff

- 
**단위 테스트:** `jetson_publisher/tests/test_esp_bridge.py` (mock serial, 6 tests 통과)

### 2.6 원격 업로드·검증 방법
Jetson 에 물리 접근 없이 Mac → Jetson SSH 로 펌웨어 업로드:
**검증 (2026-04-15):** PING → PONG, sim_entry → STATE:RUNNING, RUN → ack:run, ST_STOPPED 3초 대기 후 STARTED 미발생 ✅
실제 TOF 센서/모터는 **배선 대기 중**. 배선 후 바로 E2E 가능.

## 3. Management Service ↔ Stacking Service (JetCobot)

### 3.1 대상 하드웨어

| 항목 | 값 |
|---|---|
****
| 모델 | Elephant Robotics MyCobot 280 (JetCobot 에디션, 6-axis 협동로봇) |
| 컨트롤러 | Raspberry Pi, Ubuntu 24.04 aarch64 |
``
| Tailscale IP | 100.94.152.67 |
``
| SSH 계정 | jetcobot / 1 |
````
| 로봇 통신 | UART 시리얼 — /dev/ttyJETCOBOT (→ /dev/ttyUSB0, CH340 USB-Serial) |
****
| Baud | 1,000,000 bps |
``````
| 파이썬 SDK | pymycobot 4.0.4 + pyserial 3.5 (venv ~/venv/mycobot/) |
**카메라:** `/dev/jetcocam0` (USB Microdia, 별도 웹캠) — Stacking 공정의 비전 피드백 용도 (아직 미사용).

### 3.2 통신 방식 선정 과정

1. 
**ROS2 DDS (원래 계획):** mycobot_ros2 드라이버 + Jazzy. 하지만

  - 
RPi 에 `mycobot_ros2` 패키지 **미설치**

  - 
`rclpy` 미설치

  - 
DDS 도메인에 이미 Open RMF demo 노드들이 참여 중 (다른 기기의 publish) → 도메인 충돌 가능

  - 
Mac 에서 ROS2 Jazzy 네이티브 지원 제한적

1. 
**pymycobot 직접 (현재 사용 중):** RPi 에서 Jupyter Lab 으로 이미 동작 중인 검증된 방식.
**결론:** 과도기적으로 **SSH + pymycobot 원격 호출** 을 택해 즉시 동작 확보. ROS2 경로는 `mycobot_ros2` 빌드·systemd 등록이 완료되는 시점에 `ros2_adapter` 로 전환.

### 3.3 어댑터 구현
파일: `backend/management/services/adapters/jetcobot_adapter.py`
동작 원리 (초보자 시각):

1. 
Management 서버가 `JetCobotAdapter.get_angles()` 호출

1. 
paramiko 로 RPi SSH 접속

1. 
`~/venv/mycobot/bin/python` 실행 → `mc.get_angles()` 결과를 JSON 으로 print

1. 
Mac 측에서 JSON 파싱 → 리스트 반환
**제공 API:** `get_angles / get_coords / is_power_on / send_angles / send_coords / power_on / power_off / health_check`

### 3.4 환경변수
`backend/.env.local` 에 아래 항목이 이미 저장되어 있고 `.gitignore` 로 보호됨:

### 3.5 제약·한계

- 
**왕복 지연 ~2.3초** — SSH open + venv python 기동 + pymycobot import 포함. 단발 호출엔 충분하지만 실시간 제어 루프엔 느림.

  - 
개선 예정: 긴 SSH 세션 유지(커넥션 풀) 로 ms 단위로 단축

- 
ROS2 필요 기능(JointTrajectory, /tf) 은 아직 없음 → mycobot_ros2 드라이버 설치 후 단계적 이전

### 3.6 다음 단계

1. 
**커넥션 풀링** — 매 호출마다 SSH open/close 하지 않음

1. 
**Mgmt gRPC 연결** — `robot_id` prefix `ARM-JETCOBOT-*` 를 jetcobot_adapter 로 라우팅 (이미 `services/adapters/__init__.py::select_adapter` 에 분기 추가 가능)

1. 
**mycobot_ros2 빌드** — colcon workspace 만들고 systemd 에 등록. 그 다음 `ros2_adapter` 로 교체

1. 
**Stacking 웹캠 활용** — `/dev/jetcocam0` 로 파지 지점 비전 피드백 (선택)

## 4. 공통 보안·안정화 정책

- 
**암호는 개발 중 **`.env.local` 평문 허용. 프로덕션 배포 직전에만 SSH 키 / macOS Keychain 으로 일괄 전환.

- 
**gRPC mTLS** 는 환경변수 `MGMT_GRPC_TLS_ENABLED=1` 로 언제든 활성 가능. `scripts/gen_certs.sh` 로 자체 CA + server/client cert 발급.

- 
**keepalive ping** 은 서버·PyQt·Jetson publisher 전 구간 동일 옵션 적용 (30s / 10s).

## 5. 관련 작업 로그 (웹)

- 
`docs/worklog/index.html` — 일별 진행 로그 인덱스

- 
`docs/worklog/2026-04-14_v6_migration.html` — V6 아키텍처 마이그레이션 Phase 1~8

- 
`docs/worklog/2026-04-15_image_pipeline.html` — AI 학습 이미지 파이프라인 (Jetson → Mgmt → AI)

- 
`docs/worklog/2026-04-15_stageA_live_camera.html` — PyQt 카메라 뷰 1차 (폴링)

- 
`docs/worklog/2026-04-15_stageB_stream.html` — 카메라 Server Streaming (지연 2ms)

- 
`docs/worklog/2026-04-15_post_stream_hw_integration.html` — JetCobot + ESP32 통합 (오늘 저녁)

- 
`docs/worklog/2026-04-14_15_full_report.html` — 이틀 전체 상세 종합 보고서

## 6. 요약

| # | 구간 | 프로토콜 | 프레임워크 | 상태 |
|---|---|---|---|---|
| ① | Mgmt ↔ Jetson Image Publisher | gRPC server streaming (HTTP/2) | grpcio, protobuf | ✅ E2E 동작 (2ms 지연) |
| ④ | Jetson ↔ ESP32 HW Control | USB UART 115200 ASCII | pyserial, Arduino | ✅ 펌웨어 플래시 완료. 실 센서/모터 배선 대기 |
| ③ | Mgmt ↔ JetCobot Stacking | SSH + pymycobot 원격 호출 | paramiko | ✅ 라이브 응답 확인. ROS2 이전은 추후 |
모든 구간이 **Tailscale 내부망** 안에서 동작하므로 외부에서 직접 접근 불가. 서버는 단일 PostgreSQL (TimescaleDB, `100.107.120.14:5432`) 을 공유하지만 이 페이지의 3 구간은 각각 독립된 통신 스택으로 분리되어 있어, 한 구간 장애가 다른 구간에 전파되지 않습니다.

#### DB Server <--> Main Server <--> AI Server 통신 인터페이스 구현 (31228379)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31228379
**최종 수정**: v7 (2026-04-19 sync)

# DB Server <--> Main Server <--> AI Server 통신 인터페이스 구현
**작업 기간:** 2026-04-14 ~ 2026-04-15
**정리 관점:** Main Server 안에 같이 있는 Interface Service(FastAPI)와 Management Service(gRPC)가 각각 DB Server·AI Server 와 어떤 방식으로 통신하는지, 왜 그렇게 설계했는지를 정리.

## 0. 전체 그림
세 서비스는 **각자 다른 목적·다른 프로토콜**을 쓰지만 **DB 는 하나**를 공유합니다. 이렇게 해야 Interface 장애 시 공장 가동이 멈추지 않고, Mgmt 가 AWS 로 이관돼도 배선을 바꿀 필요가 없습니다.

## 1. Interface Service ↔ DB Service

### 1.1 개요
**Interface Service** 는 Next.js 웹 UI(관리자·고객)가 호출하는 **HTTP REST API 서버**입니다. 주문 생성·주문 조회·제품 카탈로그·대시보드 같은 "웹 업무" 를 담당합니다.
**DB Service** 는 PostgreSQL 16 (+ TimescaleDB 확장) 으로, 모든 영속 데이터(주문·제품·items·alerts·등)를 보관합니다.
둘 사이는 특별한 메시지 프로토콜 없이 **SQLAlchemy ORM** 이 만든 SQL 쿼리를 psycopg 드라이버로 직접 보냅니다.

### 1.2 기술 스택

| 항목 | 값 |
|---|---|
****
| DB 엔진 | PostgreSQL 16 + TimescaleDB |
``
| DB 호스트 | 100.107.120.14:5432 (Tailscale 내부망) |
``
| DB 이름 | smartcast_robotics |
````
| DB 롤 | team2 (Addteam2!) |
| ORM | SQLAlchemy 2.0 |
``
| 드라이버 | psycopg[binary] 3.2+ |
``
| 접속 URL | postgresql+psycopg://team2:****@100.107.120.14:5432/smartcast_robotics |
| 프레임워크 | FastAPI + Pydantic v2 |

### 1.3 왜 PostgreSQL 단독인가 (2026-04-14 결정)
이전에는 개발 편의로 SQLite 도 폴백(fallback) 으로 지원했지만, 개발·운영 사이 스키마 drift·마이그레이션 사고 가능성이 크다는 판단으로 **완전 제거**했습니다.

- 
`DATABASE_URL` 환경변수 **필수**. 미설정 시 `backend/app/database.py` 에서 **fail-fast** (`RuntimeError`)

- 
`DATABASE_URL=sqlite:...` 으로 시작해도 동일하게 거부

- 
기존 `casting_factory.db` / `migrate_sqlite_to_pg.py` 삭제

### 1.4 DB 연결 코드 위치

- 
`pool_pre_ping=True` — 유휴 커넥션이 죽었는지 매번 짧게 ping (Tailscale 일시 단절 대응)

- 
`pool_recycle=300` — 5분마다 커넥션 재생성 (stale 방지)

### 1.5 REST → DB 패턴 예

### 1.6 Interface Service 가 담당하는 테이블 (대표)

| 테이블 | 용도 |
|---|---|
``
| orders | 주문 header |
``
| order_details | 품목별 spec (두께·하중·재질·후처리) |
``
| products | 제품 카탈로그 9종 (원형·사각·타원 각 3) |
``
| alerts | 알람 이력 |
``
| production_jobs | (레거시) 과거 생산 현황 — V6 이후 items/work_orders 로 점진 이전 |

### 1.7 2026-04-15 데이터 정리 작업
UI 에 보이지 않던 **레거시 4종 제품**(D450/D600/D800/GRATING) 과 이를 참조하는 과거 주문 전부를 DB 에서 계단식(cascade) 삭제:

- 
products 13 → **9**, orders 43 → 20, items 862 → 712, production_jobs 7 → 0

- 
단일 BEGIN/COMMIT 트랜잭션 + git tag `pre-legacy-delete-20260415_154643` + `pg_dump` 백업 후 진행

## 2. Management Service ↔ DB Service

### 2.1 개요
**Management Service** 는 공장 현장의 PyQt 모니터링 앱이 호출하는 **gRPC 서버**(`:50051`)입니다. 생산 시작, 로봇 할당, 경로 계획, 알람 스트림 같은 "공장 가동" 업무를 담당합니다.
Interface 가 HTTP 라면 Mgmt 는 gRPC — 그러나 **DB 는 같은 PostgreSQL 을 공유**합니다. 이게 핵심 설계: 두 서비스는 프로세스는 다르지만 같은 DB 로 느슨하게 결합(loosely coupled).

### 2.2 같은 DB 를 쓰되, 커넥션은 각자
Interface 와 Mgmt 는 별도 프로세스이므로 각자 자기 **SQLAlchemy engine** 을 만들어야 합니다. 같은 engine 을 공유하려 하면 프로세스 분리 이점이 사라집니다.
**중요:** gRPC 서버는 `ThreadPoolExecutor(max_workers=32)` 으로 동작 — 각 워커 스레드가 `SessionLocal()` 로 자기 세션을 만들고 `with` 블록 끝나면 자동 반환합니다. 글로벌 단일 세션 공유는 금지(thread-local 안전성).

### 2.3 Mgmt Service 가 주로 만지는 테이블

| 테이블 | 쓰임 |
|---|---|
``
| items | 공정 진행 중인 주물 1개 단위 — cur_stage (QUE/MM/DM/TR_PP/PP/IP/TR_LD/SH) |
``
| work_orders | 주문 1건 → 여러 items 로 분해된 생산 명령 |
``
| alerts | 기기 이상·SLA 초과·품질 알람 |
``
``
| orders(읽기) | 생산 시작 요청 시 orders.status 를 in_production 으로 업데이트 |
````
| resources·robots | AMR·Cobot 자원 배정 시 조회 |

### 2.4 RPC 와 DB 의 연결 고리 (예)

### 2.5 실시간 스트림도 DB 기반
Mgmt 는 두 개의 **server-streaming RPC** 를 제공합니다 — PyQt 가 구독하면 공장 상태가 실시간으로 흘러옵니다.

| RPC | 소스 | 방식 |
|---|---|---|
``
``
``
| WatchItems | items.cur_stage 변화 | 1초 polling + snapshot diff → ItemEvent |
``
``
``
| WatchAlerts | alerts 테이블 신규 row | seen_ids set 기반 신규 감지 → AlertEvent |
두 스트림 모두 공통으로 `services/execution_monitor.py` 안에서 돕습니다.

### 2.6 DB 부담 완화 — Adaptive Polling
매 1초 DB 쿼리는 개발 편의는 좋지만 운영 시 부담이 될 수 있습니다. **P-001 개선 (2026-04-14)**:

- 
quiet cycle(변화 없음) 5회 누적 → interval × 2

- 
1s → 2s → 4s → **8s 상한**

- 
변화 감지 시 즉시 base interval(1s) 로 복귀
환경변수 `MGMT_ADAPTIVE_POLLING=1`, `MGMT_POLL_QUIET_CYCLES=5`, `MGMT_MAX_POLL_INTERVAL_SEC=8`.

### 2.7 seed 데이터 사고 (학습 포인트)
2026-04-15 오전에 `items.mfg_at` 을 "NOW() - random()*48h" 로 시드한 것이 원인이 되어:

- 
모든 item 이 SLA 초과 상태로 인식됨

- 
1초마다 수백 건 `alerts` INSERT → PyQt AlertStreamWorker 포화 → GUI CPU 98%
**조치:** mfg_at 을 `NOW() ± 30초` 로 수정. `feedback_seed_mfg_at.md` 메모리에 규칙 등록.

## 3. Management Service ↔ AI Service

### 3.1 현재 상태 (Phase 1 완료)
**AI Server** 는 원격 Tailscale 호스트 `100.66.177.119 (team2)` 입니다. **검사 카메라로 찍은 주물 이미지를 학습 데이터셋으로 축적**하는 용도이며, 앞으로 여기에 학습된 모델을 얹어 Mgmt 에서 **추론 결과(PASS/FAIL)** 를 받아오는 게 목표입니다.

| Phase | 내용 | 상태 |
|---|---|---|
****
****
| Phase 1 | Mgmt → AI Server 로 이미지 파일 SSH 업로드 | ✅ 완료 (2026-04-15) |
| Phase 2 | AI Server 추론 gRPC 엔드포인트 + Mgmt 클라이언트 | ⏳ 모델 준비 후 |
즉, 지금은 "데이터를 쌓는 단계" 만 구현되어 있고, "추론 받는 단계" 는 AI Server 측 준비 후 별도 작업으로 진행됩니다.

### 3.2 왜 SSH/SCP 인가 (프로토콜 선정)

| 후보 | 이유 | 채택 |
|---|---|---|
****
| SSH + SCP | 파일 덩어리 전송에 표준, 인증 간단, Tailscale 내부라 안전 | ✅ Phase 1 |
| S3 / MinIO | 오브젝트 스토리지 장점 | — AI Server 아직 스토리지 없음 |
| gRPC 스트리밍 | 연속 전송엔 좋지만 학습 데이터는 배치 성격 | — Phase 2 추론용 |

### 3.3 데이터 플로우

### 3.4 코드 구조

| 파일 | 역할 |
|---|---|
``
````
| backend/management/services/ai_client.py | AIServerConfig + AIUploader — paramiko 로 SCP 업로드 |
``
| backend/management/services/image_forwarder.py | 스풀 디렉터리 + 배치 타이머 + oldest-drop 한도 관리 |
``
``
| backend/management/services/execution_monitor.py | item IP 전이 감지 시 image_forwarder.snapshot() 트리거 |
핵심 코드 발췌:

### 3.5 환경변수 (backend/.env.local)

### 3.6 안정성 고려

- 
**AI Server 장애 시:** 스풀이 차서 결국 5000장 한도 넘으면 oldest drop → 자동 복구 후 이어서 업로드

- 
**업로드 실패:** 개별 파일 예외 시 스풀에 파일 보존 → 다음 배치에서 재시도

- 
**중복 방지:** 파일명에 `seq{n}` 포함, AI Server 디렉터리는 동일 이름 덮어쓰기 안 함(`sftp.put` 기본 동작)

### 3.7 검증 (2026-04-15)

- 
`AIUploader.health_check()` → `True` (SSH echo ok)

- 
probe 업로드 `hello_from_mgmt.jpg` → `/home/team2/datasets/inspection/_probe/` 도착

- 
E2E: item 156 IP 전이 → 2.3초 만에 spool → 10초 배치 flush → AI Server 파일 확인

- 
파일명 예: `CAM-INSP-01_IP_item156_20260415T042452.176793+0000_seq103.jpg` (84,454 B)

### 3.8 다음 단계 (Phase 2 — AI Server 준비 후)
AI Server 측 추론 엔드포인트가 확정되면 Mgmt 에 **AIInferenceClient** 를 추가할 예정.
두 가지 접근 중 선택 예상:

1. 
**AI 가 Mgmt 에 gRPC 서버를 띄움** — Mgmt 가 호출하는 구조 (표준적)

1. 
**IP snapshot 업로드 이벤트에 AI 가 자동 반응** — fanout-inotify 형태 (비표준이지만 인프라 단순)
결과(PASS/FAIL, 신뢰도, 불량 유형) 는 DB `inspection_result` 테이블에 기록되고, PyQt 품질 페이지 카메라 뷰 오버레이(`CameraLiveView.set_result()`) 로 노출됩니다.

## 4. 공통 운영 사항

### 4.1 Tailscale 내부망 기반

- 
Mgmt Server ↔ DB ↔ AI Server 전부 Tailscale 100.x.x.x 대역

- 
외부 인터넷 직접 노출 없음 → 방화벽·인증 단순화

- 
Tailscale 일시 단절 → SQLAlchemy `pool_pre_ping=True` + gRPC keepalive(30s ping) 로 빠르게 복구

### 4.2 비밀번호 정책

- 
개발 단계: `backend/.env.local` 평문 허용 (git `.env*` 무시)

- 
프로덕션 배포 직전: SSH 키 / macOS Keychain / 1Password CLI 로 일괄 전환 (S-003)

### 4.3 mTLS
Mgmt 의 gRPC 는 옵션으로 mTLS 를 지원 (`MGMT_GRPC_TLS_ENABLED=1`) — `scripts/gen_certs.sh` 로 자체 CA + server/client cert 발급. 현 개발 단계에서는 insecure 로 동작하지만 운영 시 한 줄 환경변수로 mTLS 전환 가능.

### 4.4 관련 작업 로그 (로컬 웹)

- 
`docs/worklog/index.html` — 일별 로그 인덱스

- 
`docs/worklog/2026-04-14_v6_migration.html` — V6 Phase 1~8 (Mgmt 분리 + PG 단독 + SQLite 제거)

- 
`docs/worklog/2026-04-15_image_pipeline.html` — AI Server SSH 업로드 Phase 1

- 
`docs/worklog/2026-04-15_post_stream_hw_integration.html` — keepalive, cleanup, ESP32 통합

- 
`docs/worklog/2026-04-14_15_full_report.html` — 이틀 전체 상세 보고서

## 5. 요약

| # | 구간 | 프로토콜 | 드라이버/라이브러리 | 상태 |
|---|---|---|---|---|
| ① | Interface ↔ DB | PostgreSQL wire protocol (TCP 5432) | SQLAlchemy 2.0 + psycopg 3 | ✅ V6 단독 정책, fail-fast |
| ② | Management ↔ DB | 동일 (프로세스만 분리) | 별도 engine, thread-local session | ✅ ThreadPool 32, adaptive polling |
````
| ③ | Management ↔ AI Server | SSH + SCP (paramiko) | AIUploader + ImageForwarder | ✅ Phase 1 완료. Phase 2 (추론) 대기 |
세 통신 모두 **Tailscale 내부망** 안에서 동작하며, **PostgreSQL 16 + TimescaleDB** 한 대(`100.107.120.14:5432`) 를 Main Server(Interface + Management) 가 공유합니다. AI Server 는 현재 저장 대상지일 뿐이며, 학습 모델이 확정되면 추론 RPC 가 추가 연결됩니다.

### 사형 주조 주제 가능성 검증 테스트 (3407954)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407954
**최종 수정**: v8 (2026-04-16 sync)

### DB (5898574)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5898574
**최종 수정**: v58 (2026-04-16 sync)

#### DB Schema and ERD (32342045)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32342045
**최종 수정**: v59 (2026-04-19 sync)

# INFO: DB Schema 작성 요령 
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7471353/?draftShareId=06a0aaa7-f832-4ddc-a47e-e03a51e82bb9](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7471353/?draftShareId=06a0aaa7-f832-4ddc-a47e-e03a51e82bb9)

# 발표용 특징 정리 
<우리 프로젝트안에서 특별히 신경쓴 것이 있다면?>

- 
master, transaction, stat, log, mapping table 정의: 필요에 따라 적절히 사용 

- 
ord (발주)와 item 의 한 사이클에 대하여 equip (conv, ra) 과 trasn_res 에 대한 ord table (transaction table) 들을 정하고, 필요에 따라 stat, log table 들을 만들어 사용하였다. 

  - 
stat table 예시: inspection_stat table 

- 
equip (RA, CONV)와 trans (AMR) 모두 에러가 났을 때 오류에 대하여 좀 더 세밀하게 저장하도록 하였다. (stat table에 해당 task에 대한 세밀 상태 저장 ) 

  - 
또한, **error_log에서는 error 가 난 경우**에만 failed_msg 와 함께 저장하게 하여 DB 부하가 없도록 함. 

****
****
****
| 테이블 | 커버하는 것 | 상태 |
|---|---|---|
| trans_task_txn.task_type | 큰 작업 | ToPP / ToSTRG / ToSHIP / ToCHG |
| trans_task_txn.task_stat | 큰 작업 진행도 | QUE → PROC → SUCC  / FAIL |
| trans_stat.cur_stat | 세밀한 상태 | IDLE → MV_SRC → AT_SRC → WAIT_LD → MV_DEST → WAIT_DLD →  SUCC / FAIL |

- 
item 은 한 번에 두 가지 stat에 존재할 수 있음 

  - 
두 컬럼으로 분리 (공정 위치, 이송 중)으로 분리함. 

# 결과물: SQL Table 작성 코드 
아래의 코드를 .sql 로 저장하고 다음 psql 커맨드를 terminal 에서 사용해 전체 테이블을 한번에 만들 수 있다. <user>는 맥북의 경우 `whoami` 커맨드로 알 수 있다. db 는 dbeaver 에서 새로운 db (SmartCast)를 만들어놓으면 된다. 
(GUI ↔︎ DB 연동) 아래 코드로 DB SmartCast 만들어서 테이블 만들어서 넣어주세요!   

# 결과물: ERD Image 

# **약어 사전**

# User 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| ord_id | SERIAL | 주문 번호 | PK |
| user_id | INT | 주문자 id | REF  user_account(user_id) |
| created_at | TIMESTAMP | 주문 생성 일자 | DEFAULT now() |

## ord_detail
주문 받은 제품 옵션 관리 테이블

- 
가정 

  - 
(GUI) 고객이 발주할 때 비고란 제거 

  - 
고객이 주문한 정보에서 변경 불가능해서, 발주 입력 완료 순간 특히 가격을 포함한 모든 정보가 변동없음 

  - 
`ord`와 **1:1 관계** 가짐. 따라서  `ord_id` 자체를 PK이자 FK로 사용하는 것이 관리하기 좋음

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|

| ord_id | VARCHAR | 주문 번호 | PK,FK REF ord(ord_id) |
| prod_id | INT | 선택한 표준 제품 | REF product(prod_id) |
| diameter | DECIMAL | 직경 |   |
| thickness | DECIMAL | 두께 |   |
| material | VARCHAR(30) | 재질 |   |
| load | VARCHAR(20) | 하중 등급 |   |
| qty | INT | 주문 수량 |   |
| final_price | DECIMAL | 확정 금액 |   |
| due_date | DATE | 확정납기일 |   |
| ship_addr | VARCHAR | 배송지 주소 |   |

## ord_pp_map
어떤 주문에 어떤 후처리들이 선택되었는지 기록하는 테이블 (ord.ord_id : pp_options.pp_id = N:M 관계)

- 
후처리가 없는 ord_id는 행 자체가 없다. NULL 처리 불필요 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| map_id | SERIAL | mapping ID | PK |
| ord_id | INT | 주문 번호 | REF ord(ord_id) |
| pp_id | INT | 후처리 ID | REF pp_options(pp_id) |

# Admin

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| pp_id | SERIAL | 후처리 ID | Primary Key |
| pp_nm | VARCHAR | 후처리 명칭 | 표면 연마/방청 코팅/ 아연 도금/로고*문구 삽입 |
| extra_cost | DECIMAL | 추가 단가 |   |

# Operator 
 (오른쪽 그림) 에서 총 6개 위치가 있는데, 관리자가 pattern을 제작하고 나면 해당 패턴을 화면에 발주 아이디와 위치를 입력하면 아래 테이블에 데이터가 들어가야 합니다. 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| ptn_id | INT | 주문 번호 | PK, REF ord(ord_id) |
| ptn_loc | INT | 패턴위치 | (1~6번 위치) |

## pp_task_txn  
후처리 작업 관련 transaction table 

- 
(GUI) PyQT 페이지에 관리자가 해당 item을 보고 어떤 후처리 작업이 필요한지 볼 수 있어야 함.  order_pp_map table 을 통해 조회 가능. 

- 
시나리오: 

  - 
FMS 에서는 주물을 싣고 온 AMR 의 ‘도착시간’을 기준으로 **REID tag 를 출력**해준다. 

  - 
pp 작업자는 해당 item 에 대해 필요한 후처리 작업을 다 마친 후 생성된 REID tag를 바코드에 찍고 conveyor belt에 올린다. (이때 바코드를 찍는 순간 **후처리 완료와 동시에 inspection ord req_at 요청 시간**이 된다) 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| txn_id | SERIAL | txn ID | PK |
| ord_id | INT | 발주 정보 ID | REF ord(ord_id) |
| map_id | INT | 발주 id 와 해당 pp_id 매핑 ID | FK (ord_pp_map) |
| pp_nm | VARCHAR | 후처리 이름task_type 역할을 함 | REF pp_options(pp_nm) |
| item_id | INT | 후처리 대상 아이템 | REF item(item_id) |
| operator_id | INT | 담당 작업자 ID | REF user_account(user_id) |
````````
| txn_stat | VARCHAR | 후처리 상태 | CHECK( QUE, PROC , SUCC, FAIL ) |
| req_at | TIMESTAMP | 요청 시각 | Default now() |
| start_at | TIMESTAMP | 실제 시작 시각 | NULL 가능 (QUE 상태일때) |
| end_at | TIMESTAMP | 실제 종료 시각 | NULL 가능 (SUCC/FAIL 전) |

## zone
공장 내 각 구역을 관리하는 마스터 테이블

- 
`CHECK` 제약 조건

  - 
CAST 생산 구역 

  - 
PP: 후처리 구역 

  - 
INSP: 검사 구역 

  - 
STRG: 적재 구역 

  - 
SHIP: 출고 구역 

  - 
CHG: 충전 구역

- 
세부적인 좌표는 로봇 안에 있음 구역 이름만 알면 됨

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| zone_id | SERIAL | 구역 고유 ID | Primary Key |
| zone_nm | VARCHAR | 구역 유형 | CHECK ('CAST','PP','INSP', ‘STRG’,'SHIP','CHG') |

## chg_location_stat 
charging zone 의 각 위치 관리 stat 테이블

- 
`zone` table의 상태가 `CHG` 인 경우, chg_location이 zone 테이블 참조 

- 
3개의 charing location 존재 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| loc_id | SERIAL | charing location ID | Primary Key |
| zone_id | INT | 적재구역 ID | REF zone(zone_id) |
| res_id | VARCHAR | AMR ID | REF res(res_id) |
| loc_row | INT | (1x3) 행렬 중 row | (row, column)을 저장하고, 실제 (x, y, z)위치는 하드 코딩 |
| loc_col | INT | (1x3) 행렬 중 col |   |
``````
| status | VARCHAR | 위치 상태 | empty \| occupied \| reserved |
| stored_at | TIMESTAMP | 적재된 시간 | Default now() |

## strg_location_stat
적재 구역 각 적재 장소 위치 마스터 테이블
`zone` table의 상태가 `STRG` 인 경우, storage_location이 zone 테이블을 직접 참조. 
`STRG` zone 안에 실제로 구현한 map 상 적재 구역 (현재 18칸 (3x6)): 사진 속 검정 reck하나가 loc_id 만약, 해당 `loc_id` 는 `empty` | `occupied` | `reserved` 상황에 있을 수 있는데, `reserved` 상황이 필요한 이유는 이미 AMR 이 테스크를 받아 주물을 실고 오거나, 로봇암이 적재 중일 수도 있기 때문이다. 특정 `loc_id` 의 상태가 `occupied` 인 경우는 DB CHECK constraint 로 강제한다. 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| loc_id | SERIAL | 적재 위치 id | Primary Key |
| zone_id | INT | 적재구역 id | REF zone(zone_id) |
| loc_row | INT | (3x6) 행렬 중 row | (row, column)을 저장하고, 실제 (x, y, z)위치는 하드 코딩 |
| loc_col | INT | (3x6) 행렬 중 col |   |
``````
| status | VARCHAR | 위치 상태 | empty \| occupied \| reserved |
| stored_at | TIMESTAMP | 적재된 시간 | Default now() |

##  ship_location_stat 

- 
출고 구역 (zone)안에 세부 location, 현재는 1x5 로 가정 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| loc_id | SERIAL | 출고 위치 ID | Primary Key |
| zone_id | INT | 구역 ID | REF zone(zone_id) |
| ord_id | INT | 어떤 발주에 포함되는 지 ID | REF ord(ord_id) |
| item_id | INT | 아이템 id (낱개) | REF item(item_id) |
| loc_row | INT | (1x5) 행렬 중 row | (row, column)을 저장하고, 실제 (x, y, z)위치는 하드 코딩 |
| loc_col | INT | (1x5) 행렬 중 col |   |
``````
| status | VARCHAR | 위치 상태 | empty \| occupied \| reserved |
| stored_at | TIMESTAMP | 적재된 시간 | Default now() |

# 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| stat_id | SERIAL |   | PK |
| ord_id | INT | 주문 번호 | REF ord.ord_id |
| user_id | INT | 주문자 id | REF user_account.user_id |
``
| ord_stat | VARCHAR | 현재 주문 상태 | CHECK  ('RCVD', 'APPR', 'MFG', 'DONE', 'SHIP', 'COMP', 'REJT', 'CNCL') |
| updated_at | TIMESTAMP | 상태 변경 일시 | Default now() |

## ord_log → 현재는 없어도 괜찮

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| log_id | SERIAL | 로그 ID | PK |
| ord_id | INT | 주문 번호 | REF ord.ord_id |
``
| prev_stat | VARCHAR | 과거 주문 상태 | CHECK  ('RCVD', 'APPR', 'MFG', 'DONE', 'SHIP', 'COMP', 'REJT', 'CANCELLED') |
``
| new_stat | VARCHAR | 과거 주문 상태 | CHECK  ('RCVD', 'APPR', 'MFG', 'DONE', 'SHIP', 'COMP', 'REJT', 'CANCELED') |
| changed_by | INT | 누가 변경했는지 | REF user_account(usr_id) |
| logged_at | TIMESTAMP | 상태 변경 일시 | Default now() |

## item
생산된 모든 제품의 "실시간 공정 단계” 와 “불량품 판단 결과"를 관리하는 스테이트 테이블 (stat table)

- 
현재 공정 단계 12단계

1. 
`MM` : Mold Making, `POUR` : Pouring , `DM` : Demolding, `PP` : Post-processing, `ToINSP` : transported from PP to INSP, `PA` : Putaway, `PICK` : pick , `SHIP` : Shipping 

1. 
`ToPP` : transported from DM to PP, `INSP`: Inspection , `ToSTRG` : transported from INSp to STRG, `ToSHIP`: Shipping zone 으로 이동 

- 
is_defective 란이 update 되는 순간 

  - 
AI 검사 완료 

    - 
→ inspection_log INSERT (item_id FK → item 참조)

    - 
→ item.is_defective UPDATE (TRUE/FALSE 값 직접 씀) 

  - 
위처럼 두 테이블을 채운다. 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| item_id | SERIAL | 아이템 고유 ID | PK |
| ord_id | VARCHAR | 주문 번호 | REF  ord(ord_id) |
| equip_task_type | VARCHAR (10) | NULL/MM/POUR/DM/PP/ToINSP/PA/PICK/SHIP | REF equip_task_txn(task_type) |
| trans_task_type | VARCHAR (10) | NULL/ToPP/ToINSP/ToSTRG/ToSHIP | REF trans_task_txn(task_type) |
| cur_stat | VARCHAR(10) |   | CHECK(12개 label) |
``
| cur_res | VARCHAR(10) | 점유 자원 ID | FK (res 참조),  NULL 가능 (PP 상태 일 때 점유 자원 없음) |
| is_defective | BOOLEAN | 불량 여부 | NULL = 미검사, TRUE = 불량, FALSE = 양품 |
| updated_at | TIMESTAMP |   |   |

## 설비

##  
생산 작업지시 관리 테이블로 생산 시작 조건이 되면, 자동으로 관제 시스템을 통해 로봇팔 / 컨베이어 벨트에 작업 할당이 되며 데이터 INSERT가 된다. 

- 
데이터 흐름 (DB는 상태 기록만, 위치/trajectory 계산은 전부 FMS + ROS 레이어에서 처리)

  - 
(GUI) PyQT에 operator가 어떤 발주를 생산 시작할 지 클릭하는 것 만들어주세요! 위에서 패턴 정보를 입력하고 난 후에만 누를 수 있습니다. (패턴 입력과 같은 페이지에 만들어주세요!) 

    - 
→ 이 작업으로 ord_txn 테이블이 채워짐 

  - 
FMS: 작업 지시 생성, equip_task_txn에  작업 생성

  - 
FMS: `QUE` 감지 → 장비 배정, 특정 equip 에 작업 할당 

  - 
FMS: ROS 명령 발행 (pattern위치나 load_spec 조회 → ROS action goal 발행) 

  - 
equip: 실행 완료 → FMS 수신 

  - 
FMS: SUCC 업데이트 + item.cur_stage 업데이트 

  - 
FMS: 다음 equip_type, equip_task_txn 자동 생성 (QUE)

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| txn_id | SERIAL | 작업지시 id | PK |
``
| res_id | VARCHAR (10) | 담당 장비 id | NULL 가능 (아직 QUE 상태이고 작업만 만들어놓은 상태), REF res(res_id) |

- 

- 
``

- 
``

- 

  - 
``

  - 
``

  - 
``

  - 
``

  - 
``

  - 
``

  - 
``

  - 
``

- 

  - 
``
| task_type | VARCHAR | 작업 유형 | 공통 ERR : error IDLE : idle RAMM : Mold MakingPOUR : Pouring DM : Demolding PP : postprocessing PA_GP (Putaway good product): 위에서 picking 이 끝난 후 해당 item_id가 양품 판정난 물건인 경우, good product storage rack 18칸 중 어디에 놓을지 판단후, 옮기기 PA_DP: PA task에서 DP는 버리기.  위에서 picking 이 끝난 후 해당 item_id가 불량품인 경우, defective box 에 옮기기 (한곳에 몰기 때문에, 세부 위치 파악 불필요)  PICK: SHIP을 위해 SHIP : 실제 밖으로 배달 CONVToINSP : 컨베이어 가동 |
````````
| txn_stat | VARCHAR | transaction 상태 | CHECK ('QUE', ‘PROC', 'SUCC', 'FAIL') |
| item_id | INT | item_id | REF item(item_id)cf) ord_id는 item_id를 통해 item table에서 유추 가능하므로 불필요 |
``
| strg_loc_id | INT | STRG zone 안의 location dest | REF strg_location_stat(loc_id)NULL 가능, PA_GP 인 경우에만 값 존재 |
``
| ship_loc_id | INT | SHIP zone 안의 location dest | REF ship_location_stat(loc_id)NULL 가능, SHIP |
| req_at | TIMESTAMP | 요청 시각 | Default now() |
| start_at | TIMESTAMP | 실제 시작 시각 | NULL 가능 (QUE 상태일때) |
| end_at | TIMESTAMP | 실제 종료 시각 | NULL 가능 (SUCC/FAIL 전) |

### equip_stat 
로봇팔/컨베이어의 최신 상태 확인

- 
현재 res_id 는 뭐하고 있어? 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| stat_id | SERIAL | 설비 상태 이력 id | PK |
| res_id | VARCHAR(10) | 로봇팔 설비 id | REF res(res_id) |
| item_id | INT | 현재 할당된 item id | REF item(item_id) |
| txn_type | VARCHAR | 현재 진행하고 있던 task | REF equip_task_txn(txn_type) |

- 

  - 

  - 

  - 

  - 

  - 

- 

  - 

  - 
| cur_stat | VARCHAR | 현재 상태 | RA MV_SRC: pick 위치로 이동GRASP: gripper 잡기 MV_DEST: place 위치로 이동 RELEASE: gripper 놓기RETURN : 기본 위치 복귀CONV:ON: 동작OFF: 멈춤 |
| updated_at | TIMESTAMP | 변경 시각 | Default now() |
| err_msg | VARCHAR | 마지막 상태변경 시각 (디버깅, 감사용) | NULL 가능, task_stat = ERR 일 때 실패 원인 기록 |

### equip_err_log 
equip에서 에러가 났을 때 로깅하는 테이블 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| err_id | SERIAL | 에러 ID | PK |
| res_id | VARCHAR (10) | 현재 res id | REF res(res_id) |
| task_txn_id | INT | 어떤 테스크를 하고 있었는지 | REF equip_task_txn(txn_id) |
| failed_stat | VARCHAR | 어느 단계에서 실패? | REF equip_stat(cur_stat) |
| err_msg | VARCHAR | 로봇이 보낸 에러 메시지 |   |
| occured_at | TIMESTAMP | 에러가 일어난 시각 | DEFAUT now() |

## 이동 설비 

### trans
이송 자원 (AMR) 마스터 테이블, res table 참조 및 전용 속성만 따로 저장 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| res_id | VARCHAR(10) | 자원 고유 ID | PK, REF res(res_id) |
| slot_count | INT |   | 적재 가능 item 개수 |
| max_load_kg | NUMERIC |   |   |

### 
AMR 이송 작업에 대한 transaction table, AMR 에 할당된 task (task 종류 4가지) 에 대해 (QUE → PROC → SUCC → FAIL)로 transaction을 INSERT 한다. 

- 
생각해보니 DP 모으는 박스는 버리는 건 사람이? 아니면 AMR 이용? 

- 
특징:

  - 
PP로 옮겨지는 task_type 의 경우에는 task 완료 시간을 받으면 FMS 가 RFID tag 를 발행해준다. 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| trans_task_txn_id | SERIAL | 이송 요청 id | PK |
| trans_id | VARCHAR | 이송 자원 id | NULL 가능, 할당 전까지 NULL FK (transport_res 참조) |

- 
``

- 
``

- 
``

- 
``
| task_type | VARCHAR | 이송 작업 유형 | ToPP = CAST→ PP 구역으로 이동 ToSTRG = INSP → STRG 구역으로 이동 ToSHIP : STRG → SHIP 구역으로 이동 ToCHG : 현재 위치 → Charging zone 으로 이동 |
````````
| txn_stat | VARCHAR | 작업 상태 | CHECK ('QUE', ‘PROC', 'SUCC', 'FAIL') |
| chg_loc_id | INT | CHG zone 안의 location dest | REF chg_locatoin_stat(loc_id)NULL 가능 (dest loc이 chg zone이 아닌 경우) |
| item_id | INT | 할당받은 아이템 id | REF item(item_id) |
| ord_id | INT | 발주 id | REF ord(ord_id) |
| req_at | TIMESTAMP | 요청 시각 | Default now() |
| start_at | TIMESTAMP | 시작 시각 | NULL 가능, AMR 출발 시 UPDATE |
| end_at | TIMESTAMP | 종료 시각 | NULL 가능, AMR 이송 완료 시 UPDATE |

### trans_stat 

- 
transport res stat table. 이동 설비는 현재 남은 충전량이 중요하다. charging 을 하러가야할 수 있는 예외 상황이 생기기 때문이다. 따라서, 별도의 stat table 을 만들어 중간에 예외 상황에서 바로 charing 하러 갈 수 있도록 stat table 을 따로 배치한다. 

- 
<FMS 충전 판단>
    → transport_res_stat 조회 (battery_pct < 20)
    → 해당 res_id에 battery 가 얼마나 남았지? → stat table을 통해 빠른 조회가 가능하다. 

- 
`trans_task_txn` 테이블은 큰 task 에 대해 수행 과정 (QUE → ..) 를 보여주고, stat table 에서는 세부 stat에 대한 정보를 저장한다. 

  - 
[작업 상태, task 가 있는 상태] mv_src (move to source) → wait_ld (waiting for loading) → mv_dest (move to destination) → wait_dld (waiting fr deloading) → SUCC / FAIL

  - 
[비작업 상태] CHG, idle, return_idle

****
****
| trans_stat.cur_stat | trasn_task_txn.txn_stat |
|---|---|
| IDLE | 없음 / 또는 QUE 대기 |
| RETURN_IDLE | 없음 |
| CHG | CHG task QUE/PROC |
| MV_SRC ~ WAIT_DLD | PP/STRG/SHIp task PROC |
| SUCC | task SUCC |
| FAIK | task FAIL |
  위의 테이블에선, cur_stat과 txn_stat을 매칭시켰다. 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| res_id | VARCHAR | 자원 고유 ID | PK, REF res(res_id) |
| item_id | INT | 현재 할당된 item ID | REF item(item_id) |

- 

- 
| cur_stat | VARCHAR |   | chg, idle, return_idlemv_src, wait_ld, mv_dest, wait_dld, succ, fail |
| battery_pct | INT | 배터리 잔량 (% ) |   |

| cur_zone_type | VARCHAR | 현재 위치 구역 | FK (zone 참조) |
| updated_at | TIMESTAMP | 갱신 시각 | DEFAULT now() |

### trans_err_log 
trans resouce 에 할당된 task에 관해, 에러가 났거나 fail 한 경우에 그 원인 파악을 위해 저장하는 log table 

****
****
****
****
| 필드명 | 데이터 타입 | 설명 | 비고 |
|---|---|---|---|
| err_id | SERIAL | 에러 ID | PK |
| res_id | VARCHAR(10) | 현재 res id | REF res(res_id) |
| task_txn_id | INT | 어떤 테스크를 하고 있었는지 | REF trans_task_txn(txn_id) |
| failed_stat | VARCHAR | 어느 단계에서 실패? | REF trans_stat(cur_stat) |
| err_msg | VARCHAR | 로봇이 보낸 에러 메시지 |   |
| battery_pct | INT | 당시 배터리 (저배터리 에러 추적) |   |
| occured_at | TIMESTAMP | 에러가 일어난 시각 | DEFAUT now() |

## 품질 검사 관리

#### 가상 데이터 (31981841)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31981841
**최종 수정**: v1 (2026-04-19 sync)

### GUI (6389916)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6389916
**최종 수정**: v27 (2026-04-10 sync)

#### GUI 디자인 (22413329)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22413329
**최종 수정**: v13 (2026-04-19 sync)

## 
디자인
수정부분

1. 
한번 정해진 가격,납기일(주문자가 입력)은  관리자에 의해 변경되지않는다
=관리자는 수정 권한이 없다
희망 납기일->납기일

1. 
가격 변동 가능 알림 삭제 ,예상~ 다 수정 확정된것만 있음

1. 
예상 합계 / 예상 납기일 삭제
확정 합계 / 확정 납기일만 남음

1. 
관리자 웹 페이지에서 접수중인 주문에 대힌 ‘수정요청 삭제’
승인/반려 만 남김

1. 
주문 페이지가 지금은 접속하자 마자 바로연결됨
수정 ) 메인페이지 ->소비자 이메일 입력페이지(로그인과 같은 역할)->주문페이지
관리자는 메인페이지 → 비밀번호 입력페이지 → 관리페이지
메인페이지가 [http://192.168.0.16:3000/](http://192.168.0.16:3000/quality) 이 되겠죠?

1. 
주문 시작과정은 주문자 정보 입력 단계부터 시작
***이메일 입력 필수로 수정

1. 
주문관리 탭 신규주문 → 접수로 변경
검토중 상태 삭제
접수 → 승인 → 생산 → 출고 → 완료

1. 
검토중 삭제,예상생산기간 삭제,(요청납기+확정납기) → 납기일,비고란 삭제
캡쳐이미지
종합 모니터링
[http://192.168.0.16:3000](http://192.168.0.16:3000/production)
고객 주문용
[http://192.168.0.16:3000/customer](http://192.168.0.16:3000/customer)

## PyQt5 GUI-관제 대시보드
버전 1.0

### 버전 1.1

## 페이지 구성 (8개 라우트)

## 백엔드 API 전체 목록 (27개 + WebSocket)

### 버전 1.2(위에서 언급한 9가지 UI/UX) 

## 웹 관리자 페이지

## 웹 고객 페이지

- 
조회하기

## PyQt 관제 페이지

### 버전 1.3

## PyQt 관제 페이지

#### 클라이언트 -> 백엔드 -> DB (27525158)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/27525158
**최종 수정**: v11 (2026-04-19 sync)

# 데이터 플로우 요약
**Client → Backend → Database** 주문 데이터 처리 흐름
SmartCast Robotics · casting-factory v3.4.0 · 2026-04-13

- 
TimescaleDB: PostgreSQL 확장(Extension)                                                  

  - 
PostgreSQL = 기반 DB (메인 시스템)                                                                                        

  - 
TimescaleDB = PostgreSQL 위에 얹는 플러그인으로, 시계열 데이터 (센서 로그, 시간별 상태 변화 등) 처리에 최적화된 확장 

## 1. 시스템 아키텍처 개요

### 4계층 구조

### 기술 스택 요약

| 계층 | 기술 | 역할 |
|---|---|---|
****
| Client | Next.js 16.2.1, React 19.2.4, TypeScript | 주문 폼 UI, 사용자 입력 수집, 클라이언트 검증 |
****
| Proxy | Next.js Rewrites (next.config.ts) | /api/* 요청을 백엔드로 프록시 (CORS 우회) |
****
| Backend | FastAPI, Uvicorn, SQLAlchemy ORM | REST API, 비즈니스 로직, 데이터 검증 (Pydantic) |
****
| Database | PostgreSQL 16 + TimescaleDB | 영구 저장, 트랜잭션 관리, 인덱싱 |

## 2. 전체 데이터 플로우차트

### 주문 데이터 처리 흐름

### 요청 경로 상세

| 단계 | 출발 | 도착 | 설명 |
|---|---|---|---|
``
| 1 | 브라우저 | Next.js (3000) | fetch('/api/orders') 호출 |
``
| 2 | Next.js Rewrite | FastAPI (8000) | next.config.ts rewrites로 프록시 전달 |
``
| 3 | FastAPI Route | Pydantic | OrderCreate 스키마로 자동 타입/필드 검증 |
``
| 4 | Route Handler | SQLAlchemy | Order(**payload.model_dump()) ORM 매핑 |
````
| 5 | SQLAlchemy | PostgreSQL | db.add(order) → db.commit() |
``
| 6 | PostgreSQL | FastAPI | db.refresh(order) — DB 생성 값 반영 |
````
| 7 | FastAPI | 브라우저 | 201 Created + OrderResponse JSON 반환 |

## 3. 계층별 상세 분석

### 3.1 Client — 주문 폼 흐름
**파일**: `src/app/customer/page.tsx`
5단계 스텝 위저드로 구현:

| Step | 이름 | 수집 데이터 |
|---|---|---|
| 1 | 주문자 정보 | 회사명, 담당자, 연락처, 이메일, 주소 |
| 2 | 제품 선택 | 제품 ID (D450, D600, D800, GRATING) |
| 3 | 사양 입력 | 직경, 두께, 하중등급, 재질, 수량, 납기, 후처리 |
| 4 | 견적 확인 | 단가·합계 계산 확인 (입력 없음) |
| 5 | 주문 완료 | 서버 응답 표시 (입력 없음) |
**핵심 동작**: Step 4 → 5 전환 시 `handleNext()`가 2번의 순차 `fetch()` 호출로 주문 헤더 + 품목 상세를 백엔드에 전송합니다.

### 3.2 Proxy — Next.js Rewrite 설정
**파일**: `next.config.ts`
클라이언트의 `/api/*` 요청을 동일 도메인에서 보내므로 CORS 문제 없이 백엔드로 프록시됩니다. 브라우저 네트워크 탭에서는 `localhost:3000/api/orders`로 표시됩니다.

### 3.3 Backend — FastAPI 처리 흐름
**파일**: `backend/app/routes/orders.py`
처리 순서:

1. 
**요청 수신**: Uvicorn이 HTTP POST 수신

1. 
**Pydantic 검증**: `OrderCreate` 스키마로 자동 타입/필드 검증

1. 
**중복 체크**: 동일 ID 주문 존재 시 409 Conflict 반환

1. 
**ORM 매핑**: `Order(**payload.model_dump())`

1. 
**DB 저장**: `db.add(order)` → `db.commit()`

1. 
**응답 반환**: `db.refresh(order)` 후 201 Created

### 3.4 Database — 저장 구조
**운영 DB**: PostgreSQL 16 + TimescaleDB (개발 시 SQLite 폴백)

| 테이블 | 용도 | 레코드 생성 시점 |
|---|---|---|
``
| orders | 주문 헤더 (고객·금액·상태) | Step 4 → 5 첫 번째 fetch |
``
| order_details | 품목 상세 (제품·사양·가격) | Step 4 → 5 두 번째 fetch |
`orders.id`는 클라이언트에서 생성한 `ORD-YYYYMMDD-XXXX` 형식. `order_details.order_id`가 FK로 연결됩니다.

### 3.5 데이터 변환 매핑

#### orders 테이블

| 폼 필드 (camelCase) | API 필드 (snake_case) | DB 컬럼 | 변환 |
|---|---|---|---|
| contactPerson | customer_name | orders.customer_name | 이름 변경 |
| companyName | company_name | orders.company_name | snake_case 변환 |
| phone | contact | orders.contact | 이름 변경 |
| email | email | orders.email | 동일 |
| address | shipping_address | orders.shipping_address | 이름 변경 |
| (계산값) | total_amount | orders.total_amount | 단가 x 수량 |
| desiredDelivery | requested_delivery | orders.requested_delivery | 이름 변경 |
| — | customer_id | orders.customer_id | 클라이언트 생성: CUST-XXXXXX |
[](http://orders.id)
| — | id | orders.id | 클라이언트 생성: ORD-날짜-랜덤 |
| — | status | orders.status | 항상 "pending" |
| — | — | orders.created_at | 서버 자동 생성 (UTC ISO) |
| — | — | orders.updated_at | 서버 자동 생성 (UTC ISO) |

#### order_details 테이블

| 폼 필드 | API 필드 | DB 컬럼 | 변환 |
|---|---|---|---|
| selectedProduct | product_id | order_details.product_id | PRODUCTS 배열 lookup |
[](http://selectedProduct.name)
| selectedProduct.name | product_name | order_details.product_name | PRODUCTS 배열 lookup |
| quantity | quantity | order_details.quantity | 동일 |
| diameter + thickness + loadClass | spec | order_details.spec | 문자열 조합 |
| material | material | order_details.material | 동일 |
| postProcessing[] | post_processing | order_details.post_processing | 배열 → 쉼표 join 문자열 |
| (계산값) | unit_price | order_details.unit_price | base + 후처리 합산 |
| (계산값) | subtotal | order_details.subtotal | unit_price x quantity |

### SmartCast Robotics GitHub 폴더 구조 초안 (20217883)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20217883
**최종 수정**: v17 (2026-04-16 sync)

# SmartCast Robotics GitHub 폴더 구조 초안

## 폴더 초안 구조

## 폴더별 역할

- 
`docs/` — 요구사항, 아키텍처, DB, API, 장비 문서 정리

- 
`backend/` — 관제, 주문, 이송, 검사, 적재, 출고 로직 구현

- 
`frontend/` — 관리자 화면, 현장 모니터링 화면, 주문 화면 구현

- 
`database/` — 스키마 초기화, 마이그레이션, 시드 데이터 관리

- 
`plc/` — PLC 로직, 태그 정의, HMI 관련 파일 관리

- 
`edge/` — 센서/설비 데이터 수집, 프로토콜 연동, 메시지 브로커 연결

- 
`ai/` — 품질 검사 모델, 이상 감지, 예측 모델 실험 및 배포 코드

- 
`simulation/` — 공정 흐름, 이송 동선, 레이아웃 검토용 시뮬레이션 자료

- 
`data/` — 원천 데이터, 전처리 데이터, 외부 샘플 데이터 보관

- 
`scripts/` — 환경 세팅, 데이터 적재, 유지보수용 스크립트

- 
`configs/` — 개발/운영 환경 설정 파일 분리

- 
`infra/` — Docker, 배포, 인프라 구성 파일 관리

- 
`.github/` — CI/CD, 이슈 템플릿, PR 템플릿 관리

# v0.2 — 실제 프로젝트 기반 팀 협업 구조
작성일: 2026-04-10 | 기준: casting-factory 프로젝트
v0.1(초안)은 범용 스마트팩토리 템플릿이었고, v0.2는 **실제 프로젝트 기반**으로 `ui / server / device` 3분류 체계로 재구성한 팀 협업 구조입니다.
프로젝트 문서(설치 가이드, 아키텍처, DB 스키마 등)는 **Confluence 위키**에서 관리합니다.

## v0.1 → v0.2 주요 변경점

| 항목 | v0.1 (초안) | v0.2 (실제 반영) |
|---|---|---|
****
| 최상위 분류 | 기능별 13개 폴더 | ui / server / device 3분류 |
| 프론트엔드 | frontend/ | ui/web/ (Next.js 16 App Router) |
| 모니터링 | 없음 | ui/monitoring/ (PyQt5 데스크톱 앱) |
| 백엔드 | backend/ | server/main_service/ (FastAPI) |
| AI 서비스 | ai/ | server/ai_service/ (Jetson Orin NX) |
| 데이터베이스 | database/ | server/smart_cast_db/ (SQL 마이그레이션) |
| 협동로봇 | 없음 | device/cobot/ (MyCobot280 + RPi5) |
| AMR | 없음 | device/amr/ (Pinkypro + RPi4) |
| 컨베이어 | edge/ | device/conveyor_controller/ (ESP32) |
| PLC | plc/ | 해당 없음 (ESP32 기반 제어) |
| docs | docs/ (Git 내 문서) | Confluence 위키로 이전 |
[](http://README.md)
****
| README.md | 폴더마다 존재 | 최상위 1개만 |

## 폴더 구조 v0.2

## 3분류 체계 설명

| 분류 | 폴더 | 담당 | 하드웨어 | 역할 |
|---|---|---|---|---|
****
``
| UI | ui/web/ | 프론트엔드 | — | Next.js 16 웹 앱 (관리자 + 고객 포털) |
****
``
| UI | ui/monitoring/ | 현장 SW | — | PyQt5 데스크톱 관제 앱 (6페이지) |
****
``
| Server | server/main_service/ | 백엔드 | — | FastAPI REST API (31개 엔드포인트 + WebSocket) |
****
``
| Server | server/ai_service/ | AI | Jetson Orin NX 16GB | YOLO + PatchCore 품질 검사 추론 |
****
``
| Server | server/smart_cast_db/ | 백엔드 | — | DB 마이그레이션 SQL 스크립트 |
****
``
| Device | device/cobot/ | 로봇 | MyCobot280 x2 + RPi5 | 주탕/탈형/후처리 협동로봇 제어 |
****
``
| Device | device/amr/ | 물류 | Pinkypro x3 + RPi4 | 자율주행 물류 이송 (Nav2) |
****
``
| Device | device/conveyor_controller/ | 임베디드 | ESP32 + TOF250 x2 | 컨베이어 벨트 제어 (Arduino + MQTT) |

## 하드웨어 구성

| 카테고리 | 모델 | 수량 | 컨트롤러 | 용도 |
|---|---|---|---|---|
| 협동로봇 | MyCobot280 (Elephant Robotics) | 2대 | Raspberry Pi 5 | 주탕/탈형/후처리 |
| AMR | Pinkypro | 3대 | Raspberry Pi 4 | 자율주행 물류 이송 |
| 컨베이어 | 자체 제작 (L298N + JGB37-555) | 1대 | ESP32-WROOM-32 | 벨트 이송 + TOF250 센서 |
| 비전 AI | Jetson Orin NX 16GB | 1대 | — | YOLO/PatchCore 추론 |
| 비전 카메라 | USB Web Camera | 1대 | Jetson 연결 | 품질 검사 촬영 |

## 문서 관리 정책
프로젝트 문서는 **Confluence 위키**에서 중앙 관리합니다. Git 저장소에는 코드만 유지합니다.

| 문서 유형 | 관리 위치 |
|---|---|
| 설치 가이드 | Confluence |
| 아키텍처 설계 | Confluence |
| DB 스키마/ERD | Confluence |
| API 명세 | Confluence |
| GUI 페이지 목록 | Confluence |
[](http://README.md)
| 코드 설명 | README.md (Git 루트) |

## 기술 스택 (2026-04 기준)

| 레이어 | 기술 | 버전 |
|---|---|---|
| 프론트엔드 프레임워크 | Next.js + React + TypeScript | 16.2 / 19.2 / 5 |
| UI 스타일링 | Tailwind CSS | 4 |
| UI 차트 | Recharts | 3.8 |
| UI 아이콘 | Lucide Icons | 1.7 |
| 백엔드 프레임워크 | FastAPI | 0.115 |
| ORM | SQLAlchemy | 2.0 |
| 데이터 검증 | Pydantic | 2.9 |
| DB 드라이버 | psycopg | 3.2 |
| 데이터베이스 | PostgreSQL (Tailscale VPN 원격) | 16 |
| 실시간 통신 | WebSocket (FastAPI) + MQTT (ESP32) | — |
| 모니터링 앱 | PyQt5 (데스크톱) | 5 |
| 로봇 미들웨어 | ROS2 Jazzy | — |
| AMR 네비게이션 | Nav2 | — |
| AI 추론 | YOLO + PatchCore | — |
| 펌웨어 | Arduino (ESP32-WROOM-32) | v4.0 |

## 아키텍처 개요

## 주문 상태 파이프라인

## Git 브랜치 전략 (팀 협업용)
**브랜치 규칙:**

| 브랜치 | 용도 | 머지 대상 |
|---|---|---|
``
| main | 안정 배포 버전 | develop → main (PR 필수) |
``
| develop | 팀원 작업 통합 | feature/fix/docs → develop (PR 필수) |
``
| feature/* | 새 기능 개발 | develop에서 분기 |
``
| fix/* | 버그 수정 | develop에서 분기 |
``
| docs/* | 문서 작업 | develop에서 분기 |

## 팀원 온보딩 절차
**1단계 — 저장소 클론**
**2단계 — **[**README.md**](http://README.md)** 읽기**
프로젝트 개요, 아키텍처, 기술 스택 파악
**3단계 — Confluence 위키 확인**
상세 설치 가이드, DB 접속 설정, 아키텍처 문서 참조
**4단계 — 담당 영역 환경 구성**

| 담당 | 실행 명령 |
|---|---|
````
| 프론트엔드 (ui/web) | npm install → npm run dev (포트 3000) |
````
| 백엔드 (server) | cd server && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt → uvicorn main_service.main:app --reload (포트 8000) |
````
| 모니터링 (ui/monitoring) | cd ui/monitoring && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt → python main.py |
````
| 협동로봇 (device/cobot) | RPi5에서 ROS2 Jazzy 환경 설정 → colcon build → ros2 launch |
````
| AMR (device/amr) | RPi4에서 ROS2 Jazzy + Nav2 환경 설정 → colcon build → ros2 launch |
````
| 펌웨어 (device/conveyor) | config.example.h → config.h 복사 후 WiFi/MQTT 인증정보 입력, Arduino IDE에서 업로드 |
**5단계 — 브랜치 생성 및 작업**
**6단계 — Pull Request 생성**
GitHub에서 develop 브랜치 대상으로 PR 생성 → 팀원 리뷰 → 머지

---

<!-- CURATED:START -->
## 프로젝트 로컬 회귀 테스트 스위트 (Git 관리)

> **맥락**: Confluence READ-ONLY 정책상 이 섹션은 자동 동기화 대상이 아니며, Git 저장소 내부에서만 관리되는 큐레이션 블록이다.

### SPEC-RC522-001 — RC522 안정성 회귀 테스트 스위트 (2026-04-18)

- **목적**: v1.5.1 (`dd4c4eb`) 에서 수정된 RC522 카드 감지 버그 재발 방지.
- **산출물**:
    - `scripts/test_rc522_regression.py` — Jetson HW-in-loop Serial 로그 파서 기반 자동 회귀 하네스.
    - `scripts/tests/test_rc522_regression.py` — 51 unit tests, coverage 99 % (목표 85 %).
    - `docs/testing/rc522_regression_checklist.md` — 한국어 수동 운영 체크리스트.
- **대상 펌웨어**: `firmware/conveyor_v5_serial/conveyor_v5_serial.ino` v1.5.1 (블랙박스 검증, 수정 금지).
- **임계값 계약**: UID 감지율 ≥ 99 % / NDEF 파싱율 ≥ 95 % (100-탭 롤링 윈도우).
- **회귀 차단**: 주기 `PCD_ReadRegister(VersionReg)` healthcheck 재도입 시 UID 99 % 미달이면 `failure_category: "healthcheck_regression"` 으로 exit 1.
- **HW 제약**: Mac 호스트에서 L298N 모터 커맨드 차단 (`feedback_motor_brownout_mac_usb`).
- **Deferred**: AC-E2 (no-NDEF 카드), AC-E3 (UTF-8 깨짐 카드), `rc522_standalone_test.ino` report mode.
- **참조**: `.moai/specs/SPEC-RC522-001/`, GitHub Issue #1, PR (branch `feat/SPEC-RC522-001-rc522-regression-suite`).
<!-- CURATED:END -->
