# Confluence Fact Reference — casting-factory

> **addinedute(addinedu_team_2)** space 주요 설계/기술 문서의 팩트 체크 정리본
> 원본 페이지 변경 시 이 파일을 업데이트해야 함
> **마지막 업데이트**: 2026-04-22 (cron sync: 10건)
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

> 2026-04-19 최종 업데이트: homepage **753829** 하위 **모든 페이지를 추적**한다 (총 **232 섹션** 등록). Standup / 회의록 / 멘토링일지 / Sprint 회의·발표 / 실험 sub-page / Forms & Templates 등 전달성 자료까지 모두 포함. 다만 v2 API 의 storage format 미지원으로 본문 fetch 가 실패하는 **whiteboard 6 페이지 + draft 1 페이지** (5505054, 6914067, 5311612, 2850917, 20152370, 5144703) 는 URL 만 보존. 상세는 § 9 전체 페이지 참조.

1. [01_Project_Design](#1-01_project_design)
   - [1.1 System Architecture (3375131)](#11-system-architecture-3375131)
   - [1.2 Detailed Design (6651919)](#12-detailed-design-6651919) — 하위 8 페이지 (HW, SW, Class/ER/Sequence Diagram, GUI 화면 구성도, State Diagram, Interface Specification) 추가
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
   - [3.1 HW_Research (8552537)](#31-hw_research-8552537) — 하위 11 페이지 (AMR, Conveyor, Robot_Arm, Sensor, Embedded board, RFID 시리즈 5개) 추가
   - [3.2 SW_Research (8552545)](#32-sw_research-8552545) — 하위 8 페이지 (Vision, VLA, LLM/VLM, Storage_System, Tailscale-Ros, DevOps, Docker, Kubernetes) 추가
   - [3.3 DB_Research (8585277)](#33-db_research-8585277) — 하위 5 페이지 (관계형 DB 공유, ERD/Schema, SQL, DB Cloud, DB Cloud 적용 가능성) 추가
   - [3.4 SW_Control (15433852)](#34-sw_control-15433852) — 하위 3 페이지 (관제 기술조사 0407/0408/0414) 추가
4. [04_Implementation](#4-04_implementation)
   - [4.1 VLA (3276898)](#41-vla-3276898) — 빈 페이지 (실 내용은 §3.2 의 VLA Tech_Research)
   - [4.2 LLM (3703098)](#42-llm-3703098) — 빈 페이지 (실 내용은 §3.2 의 LLM/VLM tech_research)
   - [4.3 연동테스트 (21856283)](#43-연동테스트-21856283) — **신규**, 3 개 통신 계약 (UI↔Server, Server↔HW, DB↔Main↔AI)
   - [Prototypes (3407954)](#사형-주조-주제-가능성-검증-테스트-3407954)
   - [DB (5898574)](#db-5898574) — 하위 2 페이지 (DB Schema and ERD, 가상 데이터) 추가
   - [GUI (6389916)](#gui-6389916) — 하위 2 페이지 (GUI 디자인, 클라이언트→백엔드→DB) 추가
   - [SmartCast Robotics GitHub 폴더 구조 초안 (20217883)](#smartcast-robotics-github-폴더-구조-초안-20217883)
5. [통합 팩트 시트 (Quick Reference)](#통합-팩트-시트-quick-reference)
6. [알려진 Confluence ↔ 코드 불일치](#알려진-confluence--코드-불일치)
7. [참조 정책](#참조-정책)
8. [페이지 ID 빠른 참조](#페이지-id-빠른-참조)
9. [전체 페이지 (추적 확장)](#9-전체-페이지-추적-확장) — Standup / 회의록 / 멘토링일지 / Sprint / 실험 sub-page / 0_Topic_Selection / 04_Implementation root / 05_Meetings_and_Logs / 06_Deliverables 등 전부 (168 페이지)

---

## 1. 01_Project_Design

Root page: **3145739** (`01_Project_Design`)

### System Architecture (3375131)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3375131
**최종 수정**: v50 (2026-04-21 sync)

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
주물 제작 과정,능이 다르기 때문에 나눔

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

- 
AMR 

  - 
라즈베이파이 ↔︎ motor board ↔︎ controller 

  - 
라즈베리파이에서 nav library 로 신호보내면 motor boar → controller → motor board → nav 안에서 완료 도착 신호 판단 가능. 

## V7

1. 
 **Serial 양방향 화살표로 변경**

  1. 
Management Service에서 컨베이어 출발 신호를 보내서 컨베이어(HW Control Service)를 움직일 수 있어야 함.

1. 
**Image Publisher 이름 변경**

  1. 
불량 검사를 위한 HW, SW제어를 담당하고 데이터 전송 역할까지 하게 되므로, **Vision Controller**로 변경하였음.

  1. 
따라서 Service 명도 **Vision Control Service**로 변경

  1. 
네이밍 대안: Vision Node

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
**최종 수정**: v40 (2026-04-21 sync)

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
**최종 수정**: v20 (2026-04-21 sync)

# **Class Diagram**
주조공장 스마트팩토리에서 서버, 센서, 컨베이어, 카메라, 로봇 등이 어떤 역할을 하고 서로 어떻게 연결되는지를 객체지향적으로 정리한 시스템 구조도
시스템을 구성하는 객체들의 역할, 속성, 메서드, 객체간 관계를 표현한 것으로 각 클래스는 이름,속성,메서드로 구성되며 클래스간 연결선과 화살표를 통해 관계를 나타낸다.
속성(Attribute) - 클래스가 가지는 정보, 상태, 데이터를 의미한다. 에를들어 센서의 ID,기준거리, 현재거리 등이 속성에 해당된다. 
메서드(Method) - 클래스가 수행하는 기능이나 동작을 의미한다. 예를들어 객체감지, 신호전송과 같은 행위가 메서드에 해당된다.

1. 
**Association**
Association은 두 클래스가 서로 연관되어 있음을 나타낸다. 연관 관계는 일반적으로 클래스 간의 참조 관계를 의미하며, 다이어그램에서는 두 클래스를 직접 연결하는 화살표로 표시한다.

1. 
**Ingeritance**
Inheritance는 한 클래스가 다른 클래스의 속성과 메서드를 상속받는 관계를 나타낸다. 상속을 통해 코드의 재사용성과 확장성을 높일 수 있으며, 객체 지향 언어에서 매우 중요한 개념입니다. UML 다이어그램에서는 상속 받는 클래스와 상속하는 클래스를 화살표로 연결하며, 화살표 끝에는 빈 삼각형이 위치한다.

1. 
**Realization**
인터페이스를 상속하여 클래스에서 실제 기능을 실현화 할 때 사용한다.

1. 
**Dependency**
클래스간 참조 관계를 나타낼 때 사용한다. Association과의 차이점으로는 Association은 변수로 다른 클래스와 연관이 있을 때, 사용하고 Dependency는 메소드의 파라미터나 반환에 사용되는 클래스 관계를 나타낼 때 사용한다.

1. 
**Aggregation**
집합관계를 나타낼때 사용

1. 
**Composition**
Aggregation과 비슷하게 전체-부분의 집합 관게를 나타낼때 사용하지만 Aggregation 보다는 더 강력한 집합을 의 미할때 사용
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
**최종 수정**: v34 (2026-04-21 sync)

# **Sequence Diagram이란?**

- 
UML(통합 모델링 언어)에서 시스템 구성 요소들이 시간의 흐름에 따라 서로 어떤 메시지를 주고받으며 상호작용하는지를 시각적으로 보여주는 동적 다이어그램

## 그리는 법 

- 
component box : SA 

- 
Par 

- 
lifespan 

- 
점선 

- 
실선 

## 특징

- 
 및 보고한다.

- 
컨베이어 벨트 시스템 : 컨베이어 벨트 위에 주물 투입 → 첫 번째 포토센서에 주물 감지 후 벨트 동작 → 두 번째 포토센서 인식 후 벨트 정지 → 상단의 카메라가 비전 검사 시작 → 검사 종료 후 수동으로 벨트 동작 버튼 클릭 → 4-5초 동작 → 하단 대기 중인 AMR위로 자동 적재

- 

- 
Storgae zone은 양품이 종류별로 적재되는 곡선형 보관 랙과, 불량품이 한 곳에 모이는 박스로 구성

# SD v1 

# SD v2 

## Ordering Process
고려해야할 것 

****
****
****
| diagram | 고려할 점 | 해야할 일 |
|---|---|---|
| 주문 |   |   |

## Manufacturing & Postprocessing Process

****
****
****
| diagram | 고려할 점 | 해야할 일 |
|---|---|---|
| 제조 후처리 |   |   |

## Inspection & Storage Process

## SHIP

# Question

- 
출고, 예외 상황과 같이 비동기인 이벤트들도 한 다이어그램에 표현해야 하는지

- 
Mold making에서 발생되는 세부 Task들도 나눠야 하는지(패턴 집기, 사형에 패턴 찍기, 패턴 제자리에 두기)

-

#### Interface Specification(ver.02) (22806540)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22806540
**최종 수정**: v35 (2026-04-22 sync)

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
| 🟢 ROS2 (DDS) | Real-time Action/Topic/Service | Management Service ↔ Manufacturing, Stacking, Transfer Service |

# UI Layer (Customer / Admin / Factory PC)
고객(Customer)과 관리자(Admin)가 시스템과 상호작용하는 인터페이스 계층

## 

| From | To | Protocol |   | Message Format |
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

###  `POST /api/orders` 

### Request (Admin PC → Interface Service)

### Response (Interface Service → Admin PC)

## Monitoring Service (UI) ↔ Management Service (Server)
공장 운영자 PC의 공정 모니터링 화면과 Main Server 간 실시간 상태 공유 및 장비 제어

| From | To | Protocol | Message | Message Format |
|---|---|---|---|---|
``
````
| Management Service | Monitoring Service | 🟠 TCP ↔ | start, get_status | (실시간 공정 모니터링/상태 공유/장비 제어) |

### `start, get_status` (서버 ↔ UI)

# Server Layer (Main / Interface / AI / DB)
관제 시스템과 이와 연동된 AI(Artificial Intelligence), DB(Database)의 서버들간의 통신

## Interface Service → Management Service (TCP, 단방향)
 Main Server로 작업 할당을 단방향으로 푸시하는 채널

| From | To | Protocol | Message | Message Format |
|---|---|---|---|---|
``
``
| Interface Service | Management Service | 🟠 TCP → | create_order | JSON (단방향 작업/주문 할당 스트림) |

### `create_order` (Interface → Management, 단방향 푸시)

## Management Service ↔ AI / DB Service (TCP)
비전 시스템(Vision System)을 통한 검사(Inspection) 요청과 주문/작업/이력 데이터의 저장·조회를 처리하는 서버 간 통신

| From | To |   | Message | Message Format |
|---|---|---|---|---|
``````
``````
| Management Service | AI Service | 🟠TCP ↔ | DetectionResult,ImageData, Ack | JSON(DetectionResult), Binary(ImageData), Text/JSON(Ack) |
``
| Management Service | DB Service | 🟠TCP(Postgresql protocol)↔ |   | Binary(이진) Protocol |

### `DetectionResult` (비전 시스템 검출 결과 (객체 수, 이상 여부))

****
| Direction | AI Service → Management Service |
|---|---|
****
| Protocol | TCP |
****
| Format | JSON |
****
``
| Example | {"검출 수": 1, "anomaly": false} |

| 필드 | 타입 | 설명 |
|---|---|---|
``
| 검출 수 | int | 검출된 객체 수 |
``
| anomaly | bool | 이상 여부 (false=정상, true=이상) |

### `ImageData`(실제 이미지 데이터)

| 항목 | 내용 |
|---|---|
****
| Direction | AI Service → Management Service |
****
| Protocol | TCP |
****
| Format | Binary (이미지 데이터) |
****
| Example | shape = (225, 225, 3), 225x225 픽셀, RGB 3채널 |

| 필드 | 타입 | 설명 |
|---|---|---|
``
| shape | (int, int, int) | (높이, 너비, 채널) |
``
| data | bytes | 실제 이미지 바이너리 |

### `Ack`(수신 확인 응답)

| 항목 | 내용 |
|---|---|
****
| Direction | Management Service → AI Service |
****
| Protocol | TCP |
****
| Format | 단순 신호 (또는 JSON) |
****
````
| Example | ACK 문자열 또는 {"status": "received"} |

### `DataRow` (주문/작업/이력 데이터 처리)
SELECT 쿼리 결과의 실제 행 데이터 반환

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

## Sensors/Image pipeline ()
포토 센서(Photo Sensor) 트리거부터 이미지 캡처, 전송까지의 단방향 데이터 파이프라인으로 비전 시스템(Vision System)의 검사(Inspection) 공정의 자동화를 지원. **V6 아키텍처**

| From | To | Protocol | Interface Item | Message Format |
|---|---|---|---|---|
``
``
| HW Control Service | Image Publishing Service | 🟠 TCP → | TriggerStream | Binary/JSON (센서 트리거 + 메타데이터) |
``
``
| Image Publishing Service | Management Service | 🔵  → | /factory/vision/trigger | MQTT Payload (이미지 참조/버퍼 + Job ID) |

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

### v_model (3506182)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3506182
**최종 수정**: v7 (2026-04-20 sync)

[애자일 방법론](https://www.atlassian.com/ko/agile)

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
**최종 수정**: v40 (2026-04-21 sync)

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
| 컨베이어 벨트 | Conveyor | CONV |   |
| 포토 센서 | Photo Sensor |   | 맨홀 감지 역할 |
| 고유번호 | Identifier | id |   |
| 이름 | Name | nm |   |
| 상태 | Status | stat |   |
| 메시지 | Message | msg |   |
| 요청 | Request | req |   |
| 주문 | Order | ord |   |
| 현재 | Current | cur |   |
| 목적지 | Destination | dest |   |
| 출발지 | Source | src |   |
| 시각 | Date/Time | at |   |
| 작업자 | Operator | op |   |
| 자원 | Resource | res |   |
| 배터리 | Battery | bat |   |
****
| 생산      (process) | Manufacture | mfg | 주조부터 검사까지 모든 과정 |
| 주조 | Casting / cast |   | 금속을 녹여 주형에 부어 형상을 만드는 공정 |
| 주형제작 | Mold Making |   | 맨홀을 만들기 위한 틀을 제작하는 과정 |
| 주탕 | Pouring |   | 용탕을 주형에 붓는 과정 |
| 패턴 | Pattern | ptn | 주형을 만들기 위한 원형 모델 |
| 냉각 | Cooling |   | 용탕이 식으면서 고체로 변하는 과정 |
| 탈형 | Demolding | DM | 냉각된 맨홀에서 주형을 제거하는 과정 |
| 후처리 | Post-Processing | pp | 맨홀의 표면을 다듬고 불필요한 부분을 제거하는 과정 |
| 검사 | Inspection | INSP | 제품의 품질을 확인하는 과정 |
| 작업중 | Processing | proc |   |
****
| 이송      (process) | Transport | trans | AMR이 물건을 가지고 이동하는 모든 과정 |
| 상차 | Loading / load | LD | 로봇팔이 AMR위에 맨홀을 올리는 행위 |
| 하차 | Unloading / unload | DLD | 로봇팔/사람이 AMR위에서 맨홀을 내리는 행위 |
****
| 적재       (process) | Stacking |   | 적치와 출고과정을 통칭함 |
| 적치 | Putaway | pa | ​적치하는 process / 맨홀을 보관 랙에 넣는 행위 |
| 출하용으로 꺼내는 작업 |   | PICK | Putaway의 반대말로, WMS 표준으로 보관 위치에서 출하용으로 꺼내는 작업을 의미 |
| 보관 | Storage | strg |   |
| 임시 대기 |   |   | 다음 공정(여기선 출하)을 위해 임시로 모아두는 구역 |
| ​출고 | Shipping | SHIP | 출고하는 process |
| 파지 |   |   | 로봇arm이 무언가를 집는 행위 |
| 보관 선반 | Storage Rack |   | 맨홀을 보관하는 랙 |
| 슬롯형 보관함 | Slotted storage |   | AMR 위에 있는 보관함 |
| 수량 | Quantity | qty |   |
****
| 주물 | Casting Product |   |   |
| 양품 | Good product | GP |   |
| 불량품 | defect (n) / defective (adj) product | DP |   |
| 제품 | product | prod |   |
| 재질 | material | mat |   |
| 기타 (공통/범용) |   |   |   |
| 코드 | code | cd |   |
| 카테고리 | category | cate |   |
| 옵션 | Option | opt |   |
| 설비 | equip | equip |   |
| 구역,위치 | zone,location | zone, loc |   |
| 퍼센트 | Percent | pct |   |
| 트랜잭션 | transaction | txn |   |
| 주문 |
|   | Purchase Order | PO | 고객의 입장에서 고객 발주 ERP 표준 |
| (발주를) 수주 (제조사 입장), |   | SO, RCVD | 제조사가 수주, ERD entity는 SO, 상태표현시에는 RCVD |
| 발주 (행위) | Order Placement |   |   |
| 승인 | approved | APPR |   |
| 반려 | rejected | REJT |   |
| 취소 | cancelled | CNCL |   |

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
**최종 수정**: v2 (2026-04-22 sync)

#### [개요]RFID 태그 기반 식별 시스템 개요 (30179373)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30179373
**최종 수정**: v3 (2026-04-21 sync)

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

#### [실험]RFID / 바코드 통신 및 UID 추출 실험 (30539816)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30539816
**최종 수정**: v10 (2026-04-21 sync)

목적: ESP32와 RC522 간의 SPI 통신 정상 작동 확인.
내용: Ntag 213 스티커를 태깅했을 때 고유 UID가 시리얼 모니터에 정확히 출력되는지 테스트.
참고 [https://blog.naver.com/pongpong319/223101992823](https://blog.naver.com/pongpong319/223101992823)
**프로세스**
AMR이 맨홀을 가지고 후처리 구역에 도착 → 사람이 꺼내고 하차 완료 스위치를 누름 → 해당 맨홀의 태그가 출력됨 → 후처리 작업 진행 → 맨홀에 태그 부착 → 리더기에 스캔하고 컨베이어 벨트에 올림
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

#### [시나리오]후처리 작업구역 스위치 도입 시나리오 (37160520)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/37160520
**최종 수정**: v7 (2026-04-21 sync)

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

- 
푸시 버튼 설치 이미지

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
**최종 수정**: v11 (2026-04-22 sync)

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

### 3.3 
`restart: always`를 설정하는 이유는 예상치 못한 크래시나 서버 재부팅 시에도 자동으로 복구되기 위함이다.

## 4. Docker와 Kubernetes의 관계
D****

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
|   | CUDA, Python 패키지, AI 라이브러리 의존성 복잡 → 환경 격리 필수 |
| Main Server | 서비스 단위 독립 실행, 빠른 재배포 가능 |
| DB Server | 볼륨으로 데이터 영속성 보장, 버전 고정 용이 |

#### HW Layer — 선택적 적용 ⚠️
ROS2 기반 Controller와 HW Controller는 실제 하드웨어 디바이스와 직접 연결되므로 컨테이너화 시 추가 설정이 필요하다.
ROS2 DDS 통신은 멀티캐스트를 사용하므로 Docker 브리지 네트워크와 충돌할 수 있다.  
초기 개발 단계에서는 ****하며, 안정화 이후 Docker 적용을 검토한다.

#### UI Layer — 불필요 ❌
PyQt5 기반 데스크탑 앱은 GUI 환경이 필요하므로 컨테이너화의 이점이 적다.  
웹 기반 UI로 전환 시에는 Docker 적용이 가능하다.

## 6. AI Server 설계 분석

### 6.1 컨테이너 구성
컨테이너 1개에 모델 1개를 올린다. 각 AI Server는 담당 모델에 해당하는 컨테이너 2개를 실행한다.

### 6.2 모델 사전 로드
매 요청마다 모델을 Load하면 수십 초의 지연이 발생하므로, 컨테이너 시작 시점에 담당 모델을 GPU 메모리에 미리 올려두고 추론 요청만 처리한다.

### 6.3 장애 시 동작
Docker Compose 단계에서는 장애 감지와 자동 폴백을 직접 구현하거나 수동으로 처리해야 한다.  
운영 단계에서 Kubernetes로 전환하면 자동 폴백이 가능하다.

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
**최종 수정**: v10 (2026-04-22 sync)

작성일: 
목적: SmartCast_Robotics 프로젝트 내 Kubernetes 도입 검토
선행 문서:  

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

#### Pod란?
Pod는 K8s에서 컨테이너를 실행하는 최소 단위다. Docker의 컨테이너와 거의 같은 개념이며, K8s가 관리하는 단위라고 보면 된다.
K8s는 Pod 단위로 장애 감지, 자동 재시작, 라우팅 전환을 처리한다.

#### 배치 전략
Pod 1개에 모델 1개를 올린다. 각 AI Server는 Primary Pod 1개와 Fallback Pod 1개를 실행한다.

#### 평상시 라우팅

#### 장애 시 자동 폴백

### 4.4 Node Selector 설정
Pod가 항상 지정된 노드에 배치되도록 고정한다.
nodeSelector를 설정하지 않으면 k8s가 알아서 배치한다.

- 
ex) 모델 A Pod → AI Server 1, 2, 3 중 여유 있는 곳 아무데나

### 4.5 K8s Ingress 라우팅 구조
Main Server는 단일 엔드포인트만 바라보고, K8s Ingress가 클래스별 라우팅과 장애 시 폴백을 자동으로 처리한다.

### 4.6 멀티 라인 확장 시 K8s 이점
공장 라인이 추가되어 Main Server가 복수화되는 경우, K8s 클러스터에 노드만 추가하면 된다. 아래는 예시

### 4.7 HW Layer — K8s 미적용
ROS2 DDS 통신 특성상 K8s 네트워크와 충돌할 수 있으며, 실제 하드웨어에 직접 바인딩되므로 K8s 적용 대상에서 제외한다.

## 5. 도입 전략

### 5.1 단계별 전략

### 5.2 참고 자료

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
**최종 수정**: v27 (2026-04-22 sync)

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

# 

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
[Amazon Aurora](https://www.youtube.com/watch?v=5TVtFdiXVSE)를 중점으로 적용

# 
Amazon Web Servise 가입 후 [Aurora and RDS](https://ap-northeast-2.console.aws.amazon.com/rds/home?region=ap-northeast-2#GettingStarted:)(관리형 관계형 데이터베이스 서비스)를 통해 데이터베이스 생성

### RDS 데이터베이스 생성

- 
Postgres 기반 DB 인스턴스 생성

- 
**Public access 활성화**

- 
관리자 계정 및 비밀번호 설정

### 보안 그룹 설정

- 
초기 상태:

  - 
인바운드 규칙 없음 → 외부 접속 차단

- 
조치:

  - 
Postgres 포트 개방

| 항목 | 설정 |
|---|---|
| Protocol | TCP |
| Port | 5432 |
| Source | 0.0.0.0/0(전체개방) |

### 네트워크 연결 확인
결과

### DBeaver 연결 설정

| 항목 | 값 |
|---|---|
| Host | teamdb.ct4cesagstqf.ap-northeast-2.rds.amazonaws.com |
| Port | 5432 |
| Database | Casting |
| Username | postgres |
| Password | team21234 |

## 실험 결과

- 
RDS 인스턴스 정상 생성 완료

- 
외부 네트워크에서 DB 접속 성공

- 
DBeaver를 통한 DB 관리 가능

- 
데이터베이스 생성 및 조회 정상 동작 확인

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
**최종 수정**: v61 (2026-04-21 sync)

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
| FAIL | task FAIL |
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
**최종 수정**: v23 (2026-04-22 sync)

# GUI 디자인 — 버전별 정리
GitHub: [kiminbean/casting-factory](https://github.com/kiminbean/casting-factory)
기술 스택: **Next.js 16 + TypeScript + Tailwind CSS + FastAPI + PostgreSQL + Three.js + PyQt5**
종합 모니터링: [http://192.168.0.16:3000](http://192.168.0.16:3000/production)
고객 주문용: [http://192.168.0.16:3000/customer](http://192.168.0.16:3000/customer)

## 📑 버전 요약

| 버전 | 범위 | 주요 변경 |
|---|---|---|
****
| v1.4 | PyQt 관제 페이지 | 운영페이지 추가 (4건) |
****
| v1.3 | PyQt 관제 페이지 | 관제 대시보드 재디자인 |
****
| v1.2 | 웹(관리자+고객) + PyQt 전반 | UI/UX 9건 반영 · 주문 상태 파이프라인 개편 |
****
| v1.1 | 웹 + PyQt 초기 통합 | 8개 라우트 + 27개 REST API + WebSocket |
****
| v1.0 | PyQt5 관제 대시보드 | 초기 디자인 |

# 🟢 버전 1.4 — PyQt 관제 페이지 재디자인 (최신)

- 
운영 페이지 추가 (참조 :  - 4개 수정)

# 🟢 버전 1.3 — PyQt 관제 페이지 재디자인
**작업 시점**: 최신 반영
**대상**: PyQt 관제 대시보드

### PyQt 관제 페이지

# 🟡 버전 1.2 — UI/UX 9가지 개선 (2026-04-17)
**작업 시점**: 2026-04-17
**대상**: 웹 관리자 · 웹 고객 · PyQt 관제

## 변경 사항 9건

### 1. 비고 삭제

### 2. 가격·납기일은 주문자 입력값이며 관리자 수정 권한 없음

- 
한번 정해진 가격, 납기일(주문자가 입력)은 관리자에 의해 변경되지 않는다

- 
**= 관리자는 수정 권한이 없다**

- 
"희망 납기일" → "납기일" 로 명명 통일

### 3. 가격 변동 가능 알림 삭제, '예상~' 항목 전부 수정, 확정된 것만 표시

### 4. 예상 합계 / 예상 납기일 삭제 → 확정 합계 / 확정 납기일만 유지

### 5. 관리자 웹 접수 주문: '수정요청 삭제', 승인/반려 만 유지

### 6. 주문 흐름 개편 — 메인 페이지 도입

- 
**이전**: 접속 즉시 주문 페이지로 바로 연결

- 
**변경 (고객)**: 메인 페이지 → 소비자 이메일 입력 페이지(로그인과 같은 역할) → 주문 페이지

- 
**변경 (관리자)**: 메인 페이지 → 비밀번호 입력 페이지 → 관리 페이지

- 
메인 페이지 URL: [http://192.168.0.16:3000/](http://192.168.0.16:3000/quality)

### 7. 주문 시작 과정: 주문자 정보 입력 단계부터 시작 · 이메일 입력 필수

### 8. 주문관리 탭: 신규주문 → 접수, 검토중 상태 삭제
상태 흐름: **접수 → 승인 → 생산 → 출고 → 완료**

### 9. 검토중·예상생산기간·비고란 삭제, (요청납기 + 확정납기) → 납기일 통합

## 적용 결과

### 웹 관리자 페이지

### 웹 고객 페이지 — 주문하기

### 웹 고객 페이지 — 조회하기

### PyQt 관제 페이지

# 🔵 버전 1.1 — 웹 통합 + 백엔드 API 공개
**작업 시점**: 2026-04 초
**대상**: Next.js 웹 8개 라우트 + FastAPI 27 REST + WebSocket

## 페이지 구성 (8개 라우트)

| # | 라우트 | 페이지명 | 레이아웃 |
|---|---|---|---|
``
| 1 | / | 대시보드 | 관리자 (사이드바) |
``
| 2 | /production | 생산 모니터링 | 관리자 (사이드바) |
``
| 3 | /production/schedule | 생산 계획 | 관리자 (사이드바) |
``
| 4 | /orders | 주문 관리 | 관리자 (사이드바) |
``
| 5 | /quality | 품질 검사 | 관리자 (사이드바) |
``
| 6 | /logistics | 물류/이송 | 관리자 (사이드바) |
``
| 7 | /customer | 고객 발주 (5단계 폼) | 독립 레이아웃 |
``
| 8 | /customer/orders | 고객 주문 조회 | 독립 레이아웃 |

## 백엔드 API (27개 + WebSocket)

| Method | Endpoint | 설명 |
|---|---|---|
``
| GET | /api/dashboard/stats | 대시보드 요약 통계 |
``
| GET | /api/orders | 전체 주문 목록 |
``
| POST | /api/orders | 신규 주문 생성 |
``
| PATCH | /api/orders/{id}/status | 주문 상태 변경 (승인/반려) |
``
| PATCH | /api/orders/{id} | 주문 필드 수정 (견적/납기/비고) |
``
| GET | /api/orders/{id}/details | 주문 상세 품목 |
``
| POST | /api/orders/{id}/details | 주문 품목 추가 |
``
| GET | /api/products | 제품 마스터 목록 |
``
| GET | /api/production/stages | 공정 단계 목록 |
``
| PATCH | /api/production/stages/{id} | 공정 단계 업데이트 |
``
| GET | /api/production/metrics | 일별 생산 지표 |
``
| GET | /api/production/equipment | 설비 목록 |
``
| POST | /api/production/schedule/calculate | 우선순위 계산 |
``
| POST | /api/production/schedule/start | 생산 개시 (배치 상태 전환) |
``
| GET | /api/production/schedule/jobs | 생산 작업 목록 |
``
| POST | /api/production/schedule/priority-log | 우선순위 변경 이력 |
``
| GET | /api/production/schedule/priority-log/{id} | 주문별 변경 이력 |
``
| GET | /api/quality/inspections | 검사 기록 |
``
| GET | /api/quality/stats | 품질 통계 |
``
| GET | /api/quality/standards | 검사 기준 |
``
| GET | /api/quality/sorter-logs | 분류기 로그 |
``
| GET | /api/logistics/tasks | 이송 작업 목록 |
``
| POST | /api/logistics/tasks | 이송 작업 생성 |
``
| PATCH | /api/logistics/tasks/{id}/status | 이송 상태 변경 |
``
| GET | /api/logistics/warehouse | 창고 랙 목록 |
``
| GET | /api/logistics/outbound-orders | 출고 주문 목록 |
``
| PATCH | /api/logistics/outbound-orders/{id}/complete | 출고 완료 처리 |
``
| GET | /api/alerts | 알림 목록 |
``
| WS | ws://localhost:8000/ws/dashboard | 실시간 브로드캐스트 (5초) |
**주의**: 현재 V6 canonical 아키텍처(Phase A–SPEC-C3 머지 이후)는 REST 48건 + Management gRPC 14 RPC 로 진화함. 본 표는 **v1.1 시점 스냅샷**이며, 최신 인벤토리는  참조.

## 캡처 이미지

# ⚪ 버전 1.0 — 초기 PyQt5 관제 대시보드
**작업 시점**: 초기 릴리즈
**대상**: PyQt5 GUI 관제 대시보드 최초 디자인

## 📚 연관 문서

- 
 — 웹(관리자/고객) + PyQt 계층 분리 감사 결과

- 
[GitHub · kiminbean/casting-factory](https://github.com/kiminbean/casting-factory)
*문서 재구성 2026-04-21 — 버전 요약 추가 · 변경 사항과 스크린샷을 각 버전 섹션으로 재구성 · 이미지 참조 전부 보존*
*이미지 크기 통일 2026-04-21 — v1.2 §9 기준 이미지(*`991d1ece642b`)의 크기(912 × 744)로 43개 이미지 일괄 조정

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

---

## 9. 전체 페이지 (추적 확장)

> 2026-04-19 사용자 요청으로 homepage **753829** 하위 모든 페이지를 팩트 인덱스에 등록 완료.
> 추가된 168 섹션 — Standup 19 / 회의록 6 / 멘토링일지 9 / Sprint 11 / 기타 (실험·root·sub-page) 115 / Whiteboard 6 / Draft 2.
> Whiteboard / 일부 Draft 는 v2 API storage format 미지원이라 URL 만 보존하고 본문 fetch 는 404 처리됨.

### 9.1 기타 페이지 (root / intermediate / sub-experiment)

#### Notice (3768381)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3768381
**최종 수정**: v50 (2026-04-22 sync)

**Team2 전용 공유기 정보**

- 
SSID: t2_5G

- 
PW : Addteam2!

- 
공유기 관리자 접속 주소: 192.168.1.1

  - 
관리자 ID: admin

  - 
관리자 PW: admin
**외부 접속을 위한 **[**Tailscale**](https://tailscale.com/download)** 정보**

- 
사용 방법 문의:  

- 
ID: `addineduteam2@gmail.com` (구글 로그인)

- 
PW: `Addteam2!`
앱을 다운로드 혹은 terminal에서 다운하고 터미널을 연결해서 다음 코드를 친다. 
→ 위의 구글 이메일로 로그인
로그인 후 서버 연결은 다음과 같이 합니다:
아래 코드로 Tailscale 상태 확인 (100.66.177.119가 보여야 함)
SSH 연결
 

# 비밀번호: Addteam2!

****
****
****
****
| description | ip | user_name | password |
|---|---|---|---|
| Tailscale |
| AI 서버 | 100.66.177.119 | team2 | Addteam2! |
| DB Server(예진) | 100.107.120.14 | - | - |
| Control Server(용석) | 100.87.158.76 | - | - |
| Jetson | 100.77.62.67 | jetson | jetson |
| 공유기 |
| pinky_1c47 | 192.168.1.20 | pinky | 1 |
| pinky_2ab2 | 192.168.1.21 | pinky | 1 |
| pinky_0522 | 192.168.1.22 | pinky | 1 |
| jectobot_aa3b | 192.168.1.30 | jetcobot | 1 |
| jectobot_aab4 | 192.168.1.31 | jetcobot | 1 |

1. 
DB 접속 명령 실행

1. 
비밀번호
Addteam2!

#### Forms & Templates (851969)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/851969
**최종 수정**: v5 (2026-04-19 sync)

#### 자료 공유 (2162711)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/2162711
**최종 수정**: v9 (2026-04-19 sync)

##  업무자료
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/3407874/?draftShareId=76f3c67f-1950-49f4-803d-240392655139](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/3407874/?draftShareId=76f3c67f-1950-49f4-803d-240392655139)

## 스터디
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/3702796/?draftShareId=7420cae0-6f2d-4ed2-8a41-5e37481611de](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/3702796/?draftShareId=7420cae0-6f2d-4ed2-8a41-5e37481611de)

#### [2026.04.14] Jira 및 2팀 전달 사항 (25855451)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/25855451
**최종 수정**: v2 (2026-04-19 sync)

Jira 관련 전달했던거 스크립트 확인 해주세용~

### 스탠드업 미팅 관련

- 
스탠드업 미팅 jira task 베이스로 하기

- 
confluence 문서는 그대로 작성하고, 링크를 Jira 링크로 달기.(confluence는 jira task에 연결 가능함)

  - 
어제 한 일, 오늘 할 일 이런거 Jira Task 이름으로 하면 될 것 같음. → 이름 잘 지어야겠지?

### Jira 관련

- 
Task status(TO DO, IN PROGRESS, DONE)는 Assignee만 변경하는 것을 기본으로 한다. Assignee 부재시 Co-worker중 한명이 관리한다. **단, 변경시 팀장(이다예)에게 반드시 진행 상황 확인 및 공유 할것. 팀장 없으면 대행한테 확인…. → 대행 정해야함. → 팀장 부재기간동안 진행 사항이나 변동사항 있는 경우 팀장 돌아오면 공유**

- 
Assignee=정, Co-workers=부 개념으로 생각하시면 될듯.

- 
더 필요한 Status 있으면 추가할 수 있음(TO DO, IN PROGRESS, DONE, …) → 의견 필요

- 
Custom field, filter 만들었음. 자기 이름 누르면 자기에게 할당된 Task 확인 가능(Co-worker로 참여하는 Task 포함)

  - 
TBD는 아직 할당되지 않은 Task를 확인하기 위한 필터

- 
`Description`에 간단한 설명, 요약등 적어주면 확인하기 좋습니다. 어차피 Confluence 문서도 있을거니까 너무 길게 적지 말기! → 최대 2~3줄

- 
작업을 나눠야 하는 경우 Assignee가 `Subtask`를 추가해서 활용해도 좋음.

  - 
AI 모델 학습 Task로 예를 들면, 1. Data 수집, 2. 모델 학습, 3. 추론 이런식으로 진행상황 확인이 용이하도록 `Subtask`를 나눠도 됨. → 아니면 그냥 Description에 적어도 되고 자유. 기록, 추적이 잘 되도록 둘 중 하나에는 적어주시면 좋음

- 
특정 Task에 종속 되는 경우 → Task A가 끝나야 Task B를 진행할 수 있으면 `is blocked by`로 연결한다. 이를 위해 Start Date-Due Date를 Task마다 설정해놓으면 좋음

- 
지금은 어제, 오늘 Task만 적어놓긴 했는데, 원래 월요일마다 일주일치를 Backlog에 넣어놓고 Task 할당하는 식으로 진행하면 될 것 같다.

- 
Task 이름 적을때 포맷이나 형식을 정해놓으면 좋을 것 같다.

### 기타

- 
**확인 했으면 이모지 누르기.** → 내용 전달 확인 했는지 안했는지 모름.

  - 
모든 메세지에 대해서 할 필요는 없고, 본인 이름 멘션 되어 있거나 채널 전체 멘션인 경우에만

- 
자주 사용하는 PC에 슬랙 알림 켜주세요. **알람 시간 (09:00~18:00)으로 설정**하기.

  - 
기본 설정이 17:00까지라 이후에 알람 안울림ㅠ

- 
팀 전체에게 공지 필요한 경우 `@channel` 멘션 해주시면 좋음~

- 
기술 조사 하는 분들 좀 해보다가 너무 오래 걸릴 것 같다. 안 될 것 같다 하는 경우 과감하게 버리고 다른거 하는 방향으로 하는게 좋을듯 → 폐기하는 경우에도 하던 문서 작업은 마무리 해주기(안 될 것 같은 경우 대안 있는지 찾기)

#### 0_Project_Topic_Selection (32047347)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32047347
**최종 수정**: v3 (2026-04-19 sync)

#### 업무자료 (3407874)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407874
**최종 수정**: v4 (2026-04-19 sync)

3/25
 [스마트공장 수준별 5단계 정의](https://blog.naver.com/cochain_ltd/222086733907)
 
[애자일 방법론](https://www.atlassian.com/ko/agile)

#### 과거 BM 판넬 (2424858)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/2424858
**최종 수정**: v2 (2026-04-19 sync)

#### 맨홀 패턴 디자인 (9666579)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9666579
**최종 수정**: v4 (2026-04-19 sync)

## 1. 원형 디자인

## 2. 사각형 디자인

## 3. 타원형 디자인

#### 사형 주조 시뮬레이션 (6520887)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6520887
**최종 수정**: v2 (2026-04-19 sync)

#### 로봇팔 압력 테스트 (4096056)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/4096056
**최종 수정**: v2 (2026-04-19 sync)

#### 사형 주조 테스트 (9568288)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9568288
**최종 수정**: v1 (2026-04-19 sync)

#### 1차 (5899172)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5899172
**최종 수정**: v2 (2026-04-19 sync)

[사형 재료] 색모래
[사형 재료] 세제
패턴으로 사용한 것
[주형 재료] 위에서 아래로, 세제, 색모래, 고양이 모래

#### 2차 (5768077)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5768077
**최종 수정**: v1 (2026-04-19 sync)

3월27일 시연 
밀가루 표시 오류 → 튀김가루

#### 3차 (11600284)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11600284
**최종 수정**: v1 (2026-04-19 sync)

**양초로 만든 프로토타입 **
레시피 : 양초를 잘게 다져 녹인후에 양초가 식을때까지 기다린후 모래 주형틀에 붓는다.
**3d 프린터로 제작한 프로토타입 **
총 3가지 모형 제작 목표 : 원형, 사각형, 타원형 
현재 가지고 있는 모형 : 원형 , 사각형

#### 01_Project_Design (3145739)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3145739
**최종 수정**: v8 (2026-04-19 sync)

|   | v-model 개념 정리 및 정의 |
|---|---|
|   | 사용자 관점 요구사항 |
|   | 시스템이 해야 하는 기능, 동작의 품질/제약에 대한 명세 |
[](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3276821)
| https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3276821 | 사용자가 시스템과 상호작용하는 과정들(실제 동작 흐름) |
|   | 전체적인 시스템 구조(관제, 중간계층 layer..) |
|   | HW/SW 설계 |
[](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/4915220/?draftShareId=21cc275f-8a1c-475c-b337-bf89ae08b83b)
| https://dayelee313.atlassian.net/wiki/spaces/753667/pages/4915220/?draftShareId=21cc275f-8a1c-475c-b337-bf89ae08b83b | 맵 레이아웃 |
|   | 작업 우선순위 결정 |
|   | 시나리오 |

#### State diagram 그리는 법 (24412161)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/24412161
**최종 수정**: v2 (2026-04-19 sync)

UML 기준으로 그리는 법을 공부한다. 

# Transition

- 
상태와 상태를 잇는 화살표 실선 자체가 transition입니다.

- 
즉, 선 전체가 transition이고, 그 위에 붙는 글자는 그 transition의 상세 표기입니다.

# Event

- 
transition을 발생시키는 트리거입니다.

- 
보통 선 위에 제일 앞에 씁니다.

- 
예: tooCold

#  Action

- 
transition이 수행될 때 실행되는 동작입니다.

- 
event 뒤에 /를 써서 구분합니다.

- 
예: ready / turnOn()

- 
여기서 ready는 event, turnOn()은 action입니다.

#   UML 표준 표기 형태
  event(parameters) [guard] / action
  예시
  tooCold(desiredTemp)

- 
event: tooCold

- 
parameter: desiredTemp

- 
action: 없음
  ready / turnOn()

- 
event: ready

- 
action: turnOn()
  tooHot(desiredTemp) [fanEnabled] / startCooling()

- 
event: tooHot

- 
parameter: desiredTemp

- 
guard: [fanEnabled]

- 
action: startCooling()
  정리하면

- 
실선 화살표 = transition

- 
화살표 위의 앞부분 = event

- 
/(슬래시) 뒤 = action

- 
[ ] 안 = guard condition

- 
( ) 안 = event parameter
  즉, 질문하신 그림에서 ready / turnOn()은

- 
선: transition

- 
ready: event

- 
turnOn(): action
입니다.

#### Description Document for Class Diagram (32669814)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32669814
**최종 수정**: v9 (2026-04-19 sync)

개요
동작 흐름
주요 인터페이스 설명
주요 표기법

1. 
개요
본 클래스다이어그램은 주물의 투입부터 이송, 검사, 분류, 적재,청소까지 전체공정을 구성하는 시스템의 정적구조를 나타낸다. 
이 다이어그램의 목적은 각 클래스와 인터페이스가 가지는 책임을 보여주고, 이들이 어떤 방식으로 연결되어 전체 시스템 공정을 수행하는지 설명하는 데 있다. 특히 관제서버를 중심으로 작업지시, 검사요청, 로봇제어, 결과수신 및 자원할당이 이루어지는 구조를 표현하고 있다.

1. 
동작 흐름
이 시스템의 전체 흐름은 다음과 같이 이해할 수 있다.

- 
작업자가 시스템에 주문받은 내용을 입력한다.

- 
제어서버는 입력된 작업 지시에 따라 전체 공정의 수행 순서를 결정하고, 각 장치에 필요한 제어 명령을 전달한다.

- 
Robot Arm_1은 제어서버의 명령에 따라 패턴을 집어 지정된 위치로 이동시키고, 주형사에 패턴을 통해 주형을 생성한다.

- 
이후 용탕이 들어있는 도가니를 들고 주형에 용탕을 투입한다.

- 
용탕이 냉각되어 주물이 생성되면 작업자는 주물을 컨베이어벨트의 시작지점에 적재한다.

- 
레이저센서_1로부터 물체를 감지하면 모터로 명령을 전달하여 컨베이어벨트는 구동된다.

- 
주물이 검사 위치에 도달하면 레이저센서_2로부터 물체를 감지하고 컨베이어벨트를 정지시킨 후 Image Publisher에게 물체가 검사위치에 도달함을 알린다.

- 
Publisher는 웹카메라를 통해 영상을 획득하고, 비전 모델을 이용해 대상물의 상태를 판별한 뒤 검사 결과를 제어서버로 전송한다.

- 
제어서버는 검사 결과를 바탕으로 다음 작업을 수행할 장치를 결정하고, 필요한 제어 명령을 전달한다.

- 
TransferAMR은 제어서버의 할당에 따라 대상물을 픽업하여 다음 공정 위치 또는 RobotArm_2로 이송한다.

- 
RobotArm_2는 전달받은 대상물을 분류하고, 분류 결과에 따라 적절한 Bin에 적재한다.

- 
CleaningRobot은 제어서버의 스케줄에 따라 공장 내부를 순찰하거나 청소 작업을 수행한다.

- 
이와 같이 본 시스템은 작업 지시 입력을 시작으로 성형, 이송, 감지, 검사, 분류, 적재 및 청소의 전 과정을 통합적으로 수행한다.

1. 
주요 인터페이스 설명
1 ) Sensor
시스템 내 센서장치가 공통적으로 수행해야 하는 기능을 정의. 인터페이스에는 물체를 감지하는 기능과 감지 결과를 외부로 전달하는 기능이 포함된다. 즉, 센서 종류가 달라지더라도 시스템은 동일한 방식으로 객체 감지와 신호 전달 기능을 사용할 수 있다.
2 ) Device
Device 인터페이스는 시스템에 포함된 각종 장치들이 공통적으로 가질 수 있는 기본 동작을 정의한다. 일반적으로 전원 인가, 전원 차단과 같은 장치 수준의 기본 제어 기능을 공통화하기 위한 목적으로 사용된다. . 이를 통해 서로 다른 물리 장치라도 동일한 방식으로 시작 및 종료 동작을 다룰 수 있으며, 시스템 관리 측면에서도 일관성을 확보할 수 있다.
3 ) Server
시스템 제어를 담당하는 서버 계층의 기본 기능을 정의한다. 데이터 수신과 명령 전송과 같은 기능을 공통적으로 포함하며, 이를 통해 서버는 다른 장치나 하위 시스템과 정보를 주고받고 제어 명령을 전달할 수 있다.
4 ) Robot
시스템에 포함된 로봇 장치들이 공통적으로 가져야 하는 기본 동작을 정의한다. 일반적으로 특정 위치로 이동하는 기능과 할당된 작업을 수행하는 기능이 포함된다. 이를 통해 로봇팔, 자율이송로봇, 청소로봇과 같이 형태와 목적이 서로 다른 로봇들도 동일한 제어 개념 아래에서 다룰 수 있다. 본 시스템에서는 RobotArm1, RobotArm2, TransferAMR, CleaningRobot이 이러한 공통 로봇 동작 개념과 관련된다.

1. 
주요 표기법
1 ) 화살표 표기법

#### 이전 버전 (9568274)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9568274
**최종 수정**: v1 (2026-04-19 sync)

#### System_Requirements (3211286)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3211286
**최종 수정**: v10 (2026-04-19 sync)

| SR ID | SR Name | Description | Priority | 관련 UR ID |
|---|---|---|---|---|
|   | 주형 생성 | [사전 조건] 고객이 발주를 한다. [수행] 발주 관리자가 UI로 주문 정보를 등록한다. |   | UR_01 |
|   |   | [사전 조건] 관리자 UI로 시작 버튼을 누른다. [수행] 일정 주괴를 도가니에 넣고 용해로로 투입한다. |   | UR_01(UI) |
|   |   | [사전 조건] 관리자 UI로 시작 버튼을 누른다. [수행] 패턴을 사형에 눌러서 주형을 만든다. |   |   |
|   |   | [사전 조건] 주형 제작이 완료된다.[수행] 카메라가 실시간으로 주형 완성을 감시한다. |   |   |
|   |   | [사전 조건] 용해로에 도가니 투입이 완료된다. [수행] 시간을 잰다. |   |   |
|   |   | [사전 조건] 주형이 완성된 것과 도가니에 용융된 상태를 확인한다.[수행] 용해로에서 도가니를 뺀다. |   |   |
|   |   | [사전 조건] 용해로에서 도가니는 뺀다.[수행] 용탕을 주형에 붓는다. |   |   |
|   |   | [사전 조건] 주형에 있는 용탕의 온도를 실시간으로 확인한다. [수행] 시스템이 온도를 실시간 감시한다. |   |   |
|   |   | [사전 조건] 주형에 용탕이 부어져있다. [수행] 시스템의 온도가 특정 온도 아래임을 확인한다. |   |   |
|   |   | [사전 조건] 주물이 완성이 된다. [수행] 주조 구역의 저장 용기 유무를 확인한다. |   |   |
|   |   | [사전 조건] 주조 구역 저장 용기 위치가 비어져있다.[수행]  냉각 완료된 주물을 주형과 분리한 후 저장 용기에 적재한다. |   |   |
|   |   | [사전 조건] 관리자 UI로 시작 버튼을 누른다.[수행] 특정 알고리즘에 의해 후처리 구역 이송 신호를 보낸다. |   |   |
|   |   | [사전 조건] 후처리 관리자가 신호를 보낸다.  [수행] 주조 구역에 주물이 적재된 저장 용기를 후처리 구역으로 옮긴다. |   |   |
|   |   | [사전 조건] 주조 구역의 저장 용기 위치가 비어져있다. [수행] 주조 구역의 저장 용기 위치에 채운다. |   |   |
|   |   | [사전 조건] 후처리 관리자가 청소 요청을 한다. [수행] 청소를 한다. |   |   |
|   |   | [사전 조건] 관리자 UI로 시작 버튼을 누른다. [수행] 컨베이어 벨트가 돌아간다. |   |   |
|   |   | [사전 조건] 주물은 컨베이어 벨트 위를 따라서 이동한다. [수행] 컨베이어 벨트의 photo sensor가 주물을 감지한다. |   |   |
|   |   | [사전 조건] [수행] 불량품 검사를 한다. |   |   |
|   |   | [사전 조건][수행] |   |   |
|   |   | [사전 조건][수행] |   |   |
|   |   | [사전 조건][수행] |   |   |

- 
SR 작성 시 유의 사항 

  - 
UR_ID:SR_ID = 다:다 

  - 
보통, condition → action 으로 작성한다. 

    - 
예를 들어, UR의 기능이 단골이 들어오면 인사를 한다. 

      - 
SR_01 : 사람이 들어오면 단골인지를 확인한다. 

      - 
SR_02: 단골인지 확인되면, 인사를 한다. 

  - 
냉장고 설명서처럼 작성한다. = “원리가 들어가지 않으며” 기능 자체의 설명만 존재해야한다. 

  - 
시간의 흐름으로 작성한다. 

  - 
개발자의 관점에서, 특정 계산이나 개발이 필요한 것들을 작성하면된다. 
[2026.03.27] 

- 
회사 a: 발주내역 

- 
회사 b
[2026.03.28] 

- 
회사 c 

- 
발주 관리자, 공장 관리자 

- 
발주 (A 제품 3개, B제품 2개, C제품 3개)

- 
pattern 이 각자 정해진 위치에 존재한다. (pattern_pos_A, pattern_pos_B, pattern_pos_C)

- 
다품종 소량 생산 작업은 sequential 작업 예정 
참고 [https://narup.tistory.com/70#google_vignette](https://narup.tistory.com/70#google_vignette) \

#### System_Requirements_v2 (5341497)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5341497
**최종 수정**: v35 (2026-04-19 sync)

- 
03.27 ~ 03.29 다음주 월요일까지

  - 
꼭 해야할 것: [Description]

    - 
Description 파트는 크게, 줄글, 타입 분류, 기능, 비기능으로 구성되어 있습니다. 

    - 
[2026.03.27 노미승 강사 피드백](https://dayelee313.atlassian.net/wiki/x/4ABM) 부분에 설명 적어두었습니다.  

  - 
깊게 생각한 부분 혹은 공유할 부분 작성: 토글 안에 [discussion], [input], [output], [자료조사 링크]

    - 
모여서 토론 후 프로젝트를 더욱 구체화하기 위함입니다. 

    - 
 `/expand` 안에 적어놓기 

      - 
조사 내용이라면, `domain_research/Casting` 혹은 `domain_research/logistics` 문서에 잘 정리해서 링크로 걸어주기 

      - 
아래 예시 확인 부탁드려요! (cf) 추가 논의 사항 있으시면 `오픈 카톡방`이나 `슬랙`으로 부탁드려요)

      - 
예시) 

****
| 기능별 예시 |
|---|

- 
[](https://dayelee313.atlassian.net/wiki/x/4ABM)

- 

  - 

    - 

  - 

    - 

  - 

    - 

    - 
``

- 

- 

- 

- 

- 

- 

- 

- 

- 
| 2026.03.27 노미승 강사 피드백 페이지 설명 읽고 와주세요!SR_NAME: FR-01, 작업자 상태 인식Description:작업자의 상태를 인식한다.Functional: 정상 / 쓰러짐 / 보호장비 미착용 분류 (분류 타입)Non-functional:응답 시간: 1초 이내정확도: 95% 이상여기서부터는 /expand 기능 이용해서 토글 안에 작성 부탁드립니다! (title은 details 로 해주세요)[Discussion] = 아직 고민 중인 것, 토의 원하는 내용 팔레트 기준을 5개로 할지 6개로 할지?후처리 queue limit 몇 으로 설정할지? [Input]대기 제품 수대기시간후처리 queue[Output] Task ID [Decision Rule]waiting > 10 min → 개별 이송batch size ≥ 3 → 소배치[자료 조사] 하이퍼링크 |

| SR ID | SR Name | Description | Priority | 관련 UR ID |
|---|---|---|---|---|

- 
| 다예 | 원격 발주 기능 | 고객이 표준화된 주조 제품을 선택하고, 규격/수량/납기/후처리 옵션을 입력하여 발주할 수 있는 원격 주문 시스템을 제공한다. |   |   |
****
****

- 

- 

- 

- 
****

- 

- 

- 

- 
****

- 
|   |   | [SR-01] 표준 제품 탐색/조회/ 기능Description 사용자는 원격으로 주문 가능한 표준 주조 목록을 조회할 수 있어야한다. 세부 요구사항시스템은 제품 카테고리를 제공해야 한다.시스템은 각 제품의 기본 이미지, 이름, 규격, 재질, 기본 가격 범위를 표시해야 한다.시스템은 맨홀 뚜껑과 같은 표준 제품을 규격별로 분류해 보여줘야 한다.시스템은 제품별 상세 페이지를 제공해야 한다.입력 제품 종류제품 규격재질하중 등급비기능 | ↓ |   |

- 

- 

- 

- 

- 

- 

- 
|   |   | [SR-02] 제품 옵션 선택 기능[Description] 사용자는 선택한 제품에 대해 규격, 수량, 재질, 후처리 조건의 주문 사양을 입력할 수 있어야 한다.[세부 요구사항]시스템은 직경, 두께, 하중 등급의 규격 옵션을 선택할 수 있어야 한다.시스템은 재질 옵션을 선택할 수 있어야 한다.시스템은 후처리 옵션을 선택할 수 있어야 한다.시스템은 수량과 희망 납기일을 입력받아야 한다.시스템은 비고란을 제공해야 한다.[기준 옵션] 직경, 두께, 재질, 표면 마감, 로고/문구 삽입 여부, 수량, 납기 요청일 [비기능]제품 옵션 변경 후 가격 및 주문 요약은 즉시 또는 짧은 기간 내 갱신되어야 한다. |   |   |

- 

- 

- 

- 

- 
|   |   | [SR-03] 도면/디자인 정보 확인 기능 [Description] 사용자는 주문 제품의 기본 디자인과 선택 사양을 주문 전에 확인할 수 있어야 한다. [세부 요구사항]시스템은 선택한 규격과 옵션에 따른 제품 요약 정보를 보여줘야 한다.시스템은 기본 디자인 시안을 표시해야 한다.시스템은 텍스트 삽입, 마크 삽입 등의 옵션 선택 결과를 미리보기 형태로 보여줄 수 있어야 한다.시스템은 자유형 복잡 설계가 아닌 표준 템플릿 기반 입력을 지원해야 한다.[비기능]사용자는 전문 CAD 지식 없이도 주문할 수 있어야 한다. |   |   |

1. 

1. 

1. 

1. 

1. 

1. 

1. 

- 

- 
|   |   | [SR-04] 주문 가능 여부 검증 기능 [Description] 시스템은 사용자가 입력한 주문 조건이 생산 가능한 범위인지 검증해야 한다.[세부 요구사항]시스템은 최소/최대 수량 조건을 확인해야 한다.시스템은 선택 가능한 규격 조합만 허용해야 한다.시스템은 생산 불가능한 옵션 조합 입력 시 오류 메시지를 제공해야 한다.시스템은 희망 납기일이 비현실적인 경우 경고를 제공해야 한다.[검증 예시]선택 불가능한 재질 + 규격 조합최소 주문 수량 미달제작 리드타임보다 짧은 납기 요청[비기능]허용되지 않는 옵션 조합은 제출 전에 차단되어야 한다. 주문 정보는 누락 없이 저장되어야 한다. |   |   |
****
****
****

- 

- 

- 

- 

- 
|   |   | SR Name예상 견적 및 납기 안내 기능Description시스템은 사용자가 입력한 주문 조건을 바탕으로 예상 견적과 예상 납기를 제공해야 한다.세부 요구사항시스템은 제품 기본 단가를 기반으로 예상 가격을 계산해야 한다.시스템은 옵션에 따라 추가 비용을 반영해야 한다.시스템은 수량에 따른 가격 변동을 반영할 수 있어야 한다.시스템은 예상 납기 범위를 표시해야 한다.시스템은 최종 견적은 관리자 검토 후 확정됨을 안내해야 한다. |   |   |
****
****
****

- 

- 

- 

- 
****

- 
|   |   | SR NameDescription사용자는 입력한 제품 정보와 주문 조건에 따라 주문 요청서를 제출할 수 있어야 한다.세부 요구사항시스템은 주문자 정보를 입력받아야 한다.시스템은 회사명, 연락처, 배송지 정보를 입력받아야 한다.시스템은 주문 요약을 확인한 후 제출할 수 있어야 한다.시스템은 제출 완료 후 주문 번호를 생성해야 한다.비기능 주문 절차는 5단계 이내로 완료 가능해야 한다. |   |   |
****
****
****

- 

- 

- 

- 
|   |   | SR Name주문 상태 조회 기능Description사용자는 제출한 주문의 처리 상태를 조회할 수 있어야 한다.세부 요구사항시스템은 주문 접수 상태를 표시해야 한다.시스템은 검토 중, 승인됨, 생산 중, 출하 준비, 완료 상태를 표시해야 한다.시스템은 주문 상세 내역을 다시 확인할 수 있어야 한다.시스템은 상태 변경 시 알림을 제공할 수 있어야 한다. |   |   |
****
****
****

- 

- 

- 

- 
****

- 

- 
|   |   | SR Name관리자 주문 검토 및 승인 기능Description관리자는 접수된 주문 요청을 검토하고 승인 또는 수정 요청할 수 있어야 한다.세부 요구사항관리자는 주문 상세 사양을 확인할 수 있어야 한다.관리자는 생산 가능 여부를 검토할 수 있어야 한다.관리자는 예상 견적과 납기를 조정할 수 있어야 한다.관리자는 주문 승인, 반려, 수정 요청 처리를 할 수 있어야 한다.비기능주문자 정보와 연락처는 안전하게 저장되어야 한다.관리자 기능은 권한이 있는 사용자만 접근 가능해야 한다. |   |   |
****
****
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

- 

  - 

  - 
| 진성 | 관제 기능 | SR NAME:모니터링 기능Description:전체 공정 데이터에 대해 모니터링 할 수 있어야 한다.Functional:시스템은 용해 상태를 표시해야 한다.녹음 / 녹지 않음시스템은 주형 제작 상태를 표시해야 한다.정상 / 비정상시스템은 주조 상태를 표시해야 한다.주조 중응고(냉각) 중완료시스템은 후처리 상태를 표시해야 한다.후처리 작업 중청소 중완료시스템은 불량품 통계를 제공해야 한다.총 생산량양품/불량품 개수불량률시스템은 적재/출고 상태를 표시해야 한다.주물 수량출고 가능 여부 |   |   |
****
****
****

- 

- 

- 

  - 
|   |   | SR NAME:공정 제어 기능Description:각 공정의 장비를 제어할 수 있는 기능Functional:관리자가 공정 구열별로 시작 / 중지 / 재개할 수 있어야 한다.관리자는 모든 장비를 빠짐없이 제어할 수 있어야 한다.관리자가 이상 상황을 즉시 해결할 수 있어야 한다.관리자가 장비에게 명령을 내리면 명령을 받은 장비는 하던 행동을 즉시 멈추고 관리자의 명령을 실행해야 함. |   |   |
****
****
****

- 

  - 

  - 

  - 
|   |   | SR NAME:이상 감지 및 알림 기능Description:공정에 대한 이상 상태를 감지하고 알림 발생하는 기능Functional:이상이 발생하면 관리자에게 알림 전송 기능장비 오류공정 지연불량률 이상 |   |   |
********
****
****

- 

- 

- 

- 
****

- 

- 
| 성수, 대현 | 주물 생산 자동화 공정 기능 | [SR Name] 원재료 준비 및 투입 기능 [실제 시연 가능? 및 필요성 여부 검토]Description시스템은 준비된 원재료를 도가니로 투입할 수 있어야 한다. Details원재료의 물성과 맞지 않는 이물질을 분리할 수 있어야 한다.원재료가 도가니에 투입될 수 있는 크기인지 파악해야 한다.도가니에 투입된 원재료가 정량인지 파악할 수 있어야한다.시스템은 원재료를 도가니에 투입할 수 있어야 한다.Non-Functional원재료와 이물질을 2단으로 분리 가능한 시스템이 있어야 한다.도가니에 투입할 원재료는 도가니 부피의 80% 수준이어야 한다. |   |   |
****
****
****

- 

- 

- 

- 
****

- 

- 
|   |   | SR Name원재료 용융 기능Description시스템은 원재료를 용탕으로 만든다.Details시스템은 도가니 내부의 원재료를 열을 가해 용융할 수 있어야 한다.시스템은 용융 소요 시간을 측정할 수 있어야 한다.  시스템은 용융이 완료된 후 용해로 속 주탕을 등온 상태(Isothermal)를 유지할 수 있어야 한다.시스템은 용융 과정에서 주탕의 온도를 측정할 수 있어야 한다.Non-Functional용탕의 용융 상태는 100%로 녹아서 고체성분이 남지 않아야 한다.시스템의 용해로는 상온 25도에서부터 가열이 시작될 수 있어야 한다. |   |   |
****
****
****

- 

- 

- 

- 

- 

- 
****

- 

- 

- 
|   |   | SR Name주형 제작 기능Description시스템은 패턴을 이용해 재료에 압력을 가하여 주형을 제작할 수 있어야 한다.Details시스템은 패턴의 형태 및 유형을 식별할 수 있어야 한다.시스템은 식별된 패턴을 물리적으로 들어올릴 수 있어야 한다.시스템은 주형을 제작할 수있도록 패턴의 위치 및 방향을 조정할 수 있어야 한다.시스템은 들어올린 패턴으로 주형사(Molding Sand)에 압력을 가해 주형을 제작할 수 있어야 한다.시스템은 패턴으로 주형을 만든 뒤, 주형에서 패턴을 제거할 수 있어야 한다.시스템은 주형 제작 후 사용된 패턴의 자료를 저장할 수 있어야 한다.Non-Functional시스템은 패턴의 방향과 위치를 패턴 중심의 좌표점을 기반으로 조정해야 한다.주형사에 패턴으로 압력을 가하는 방향은 수직이어야 한다.주형사에 새겨진 패턴의 완성도는 원형과 동일한 90 - 100%이어야 한다. |   |   |
****
****
****

- 

- 

- 

- 
****

- 
|   |   | SR Name주탕 기능Description시스템은 용해로에 용융된 용탕을 주형으로 부을 수 있어야 한다.Details시스템은 용해로 속 도가니의 위치와 주형의 위치를 파악할 수 있어야 한다.​시스템은 파악된 위치를 통해 도가니를 주형으로 이송시킬 수 있어야 한다.시스템은 도가니 내부에 있는 용탕을 주형에 부을 수 있어야 한다.시스템은 용해로 속 용탕이 모두 주형에 부어질 수 있도록 하고, 주탕 후 용해로를 원래 위치로 이동할 수 있어야 한다.Non-Functional시스템은 주탕 과정에서 이동 경로상에 인력 및 장비손상이 없도록 이동경로가 최적화되야 한다. |   |   |
****
****
****

- 

- 

- 
****

- 
|   |   | SR Name 주물 완성 감지 기능 Description시스템은 주물의 냉각 여부를 확인할 수 있어야 한다.Details 시스템은 사용자로부터 제품 별 냉각에 걸리는 시간을 입력받고 저장할 수 있어야 한다.시스템은 사용자로부터 입력받은 냉각에 걸리는 시간정보를 제작되는 주형에 대입하고 계산할 수 있어야 한다.시스템은 센서를 통해 취득한 정보를 통해 냉각 진행상태를 파악할 수 있어야 한다. Non-Functional​시스템은 센서를 통해 취득한 정보를 통해 냉각 진행상태를 파악할 수 있어야 한다. |   |   |
****
****
****

- 

- 

- 
****
|   |   | SR Name탈형 기능Description시스템은 완성된 주물을 탈형할 수 있어야 한다.Details시스템은 냉각된 주물의 위치 정보를 파악할 수 있어야 한다.시스템은 주물의 손상없이 주물을 탈형할수 있어야 한다.주물의 탈형 후, 시스템은 주물의 모양과 유형을 기록할 수 있어야 한다.Non-Functional |   |   |
|   |   | 여기에서 “원재료 용해, 주형 제작, 주탕, 탈형” 과정을 위주로 자동화 프로세스를 구상함.중간에 Underline으로 표시된 영역들은 각 SR에 맞는 로봇팔의 Adapter를 추가로 3D printer로 제작할 필요성의 유무를 검토해야 함. 논의가 필요. .→ 3D printer 로 ladle/ 도가니 중 하나 사용  에 의하면 용해로에 잉곳을 넣는 작업은 사람이 작업하는 것으로 가정해도 무방. 그러나 나머지 자동화 구간(ex: 원재료 용해 기능)에서 용융 소요 시간 및 용융 전후 온도 관리의 필요성(품질은 고려 안할경우) 검토 필요. |   |   |
| 용석 | 구역 간 이송 기능 | 이송 자원으로 구역 간 이송 대상 물품을 이송하는 기능 |   |   |

- 

  - 

  - 

  - 

  - 

- 

  - 

- 

- 
|   | 이송 요청 생성 기능 | Description시스템은 이송 요청을 생성할 수 있어야 한다.Functional시스템은 생성된 이송 요청에 대해 고유 식별 번호(task id)를 부여해야 한다.출발 위치와 도착 위치 정보를 저장해야 한다.이송 대상 물품의 종류와 수량 정보를 저장해야 한다.요청 시각, 이송 상태, 배정된 이송 자원을 저장해야 한다.Non-functional이송 요청은 기본적으로 요청 순서대로 처리되어야 한다.단, 우선순위에 따라 순서가 조정될 수 있어야 한다.이송 요청 정보는 누락 없이 저장되어야 한다.여러 이송 요청이 동시에 생성되더라도 독립적으로 처리될 수 있어야 한다. |   |   |

- 

- 

- 

- 

- 

- 
|   | 이송 요청 상태 관리 기능 | Description시스템은 각 이송 요청의 진행 상태를 조회하고 관리할 수 있어야 한다.Functional시스템은 이송 요청 식별 번호로 각 이송 요청의 현재 진행 상태를 조회할 수 있어야 한다.시스템은 상세 정보(출발/도착 위치, 물품 종류, 수량)를 조회할 수 있어야 한다. 시스템은 각 이송 요청의 진행 상태와 단계를 추적할 수 있어야 한다.시스템은 이송 상태 변경 시각을 기록할 수 있어야 한다.시스템은 완료된 이송 요청의 결과를 조회할 수 있어야 한다.시스템은 실패한 이송 요청의 실패 사유를 조회할 수 있어야 한다.Non-functional |   |   |

- 

- 

- 

- 

- 

- 

- 
|   | 이송 자원 관리 기능 | Description시스템은 유휴 상태의 이송 자원을 대기 위치로 복귀시키거나 이송 요청에 배정 할 수 있어야 하고, 각 이송 자원 별 상태를 관리해야 한다.Functional시스템은 각 이송 자원의 상태를 확인할 수 있어야 한다.시스템은 유휴 상태의 이송 자원을 이송 요청에 배정할 수 있어야 한다.시스템은 이송 자원 배정 결과를 이송 상태에 반영해야 한다.시스템은 배정된 이송 자원을 출발 위치에 호출할 수 있어야 한다.시스템은 동일한 이송 자원이 동시에 복수의 요청에 배정되지 않도록 해야 한다.시스템은 이송 자원의 동력이 일정 수준 이하로 떨어지면 대기 장소로 호출하여 보충할 수 있어야 한다.Non-functional 배정된 이송 자원은 유휴 상태이며, 동력이 충분하고, 출발 위치로부터 다른 이송자원보다 가까운 거리에 있어야 한다. |   |   |

- 

- 

- 

- 

- 

- 
|   | 출발 조건 확인 기능 | Description시스템은 이송 작업 시작 전, 출발 위치에서 이송이 가능한 상태인지 확인해야 한다.Functional시스템은 이송 자원이 출발 위치에 있는지 확인해야 한다.시스템은 이송 자원에 이송 대상 물품의 적재가 완료되었는지 확인해야 한다.시스템은 이송 자원에 이송 대상 물품이 존재하는지(적재되어있는지) 확인해야 한다.시스템은 출발 위치의 물품 정보가 이송 요청과 동일한지 확인해야 한다.시스템은 요청한 수량이 맞는지 확인해야 한다.시스템은 출발 조건 확인 결과를 이송 상태에 반영해야 한다.Non-functional |   |   |

- 

- 

- 

- 

- 
|   | 물품 인계 확인 기능 | Description시스템은 출발 위치와 도착 위치에서 물품 인계와 인수가 정상적으로 이루어졌는지 확인할 수 있어야 한다.Functional시스템은 출발 위치에서 이송 대상 물품이 이송 자원에 인계 되었는지 확인해야 한다.시스템은 도착 위치에서 이송 대상 물품이 도착 위치에 인수되었는지 확인해야 한다.시스템은 인계/인수된 물품의 종류/수량이 이송 요청과 일치하는지 확인해야 한다.시스템은 인계/인수 결과를 이송 상태에 반영해야 한다.시스템은 인계/인수 실패 시 예외 처리 상태로 전환할 수 있어야 한다.Non-functional |   |   |

- 

- 

- 

- 

- 

- 

- 
|   | 도착 위치 이동 기능 | Description시스템은 이송 자원이 이송 대상 물품을 출발 위치에서 도착 위치까지 이송할 수 있어야 한다.Functional시스템은 배정된 이송 자원이 도착 위치로 이동할 수 있어야 한다.시스템은 도착 위치 도착 후 이송 상태를 변경해야 한다.Non-functional이송 간에는 충돌 위험이 없는 안전하고 유효한 경로로 이동해야 한다.지정된 위치에 도착 시 위치 오차 ± 5cm 이내를 만족해야 한다.지정된 위치에 도착 시 자세 오차 ± 5° 이내를 만족해야 한다.이송 간에는 물품이 파손, 낙하하지 않아야 한다이송 자원의 속도는 직진 시 1.0m/s, 회전 시 0.5m/s이하여야 한다. |   |   |

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
|   | 이송 예외 처리 기능(이송 아래에, 그리고 관제는 general하게) | Description시스템은 구역 간 이송 수행 중 발생하는 예외 상황을 감지하고 적절한 처리 상태로 전환할 수 있어야 한다.Functional시스템은 이송 자원 배정 실패를 감지할 수 있어야 한다.시스템은 출발 조건 확인 실패를 감지할 수 있어야 한다.시스템은 출발 위치에서 인계 실패를 감지할 수 있어야 한다.시스템은 이동 중 실패를 감지할 수 있어야 한다.시스템은 도착 위치의 인수 실패를 감지할 수 있어야 한다.시스템은 예외 상황 발생 시 실패 사유를 기록해야 한다.시스템은 기록된 실패 사유에 대한 조회가 가능해야 한다.시스템은 예외 상황 발생 시 이송 요청 상태를 대기, 재시도, 실패 상태로 전환할 수 있어야 한다.시스템은 복구 불가능한 예외 상황 발생 시 관리자에게 알릴 수 있어야 한다.시스템은 전체 시스템이 정지되었을 경우, 진행 중인 이동까지 완료한다.Non-functional |   |   |

- 

  - 

- 

  - 

- 

  - 

  - 

  - 
| 규정 | 주물 검증 기능 | Description:만들어진 주물의 상품성을 검증한다.Functional:주물이 양품인지 불량품인지 검증한다.Non-functional:정확도 : 품질 검증 정확도는 95%이상 이어야 한다.응답 시간 : 시스템은 1초 이내에 검증 결과를 반환해야 한다.양품, 불량품 개수를 시스템에 실시간으로 갱신해야 한다. |   |   |

- 

  - 

- 

  - 

- 

  - 

  - 

  - 
|   | 주물 분류 기능 | Description:양품 주물과 불량품 주물을 분류한다.Functional:양품은 양품 박스에, 불량품은 불량품 박스에 분류하여 넣는다.Non-functional:정확도 : 분류 정확도는 99%이상이어야 한다.응답 시간 : 검증이 완료된 후 1초 이내로 분류 준비 완료 상태이어야 한다.유지 시간 : 다음 검증 결과가 나올 때까지 현재 분류 상태로 대기한다. |   |   |

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
| 기수 | 컨베이어 벨트 기능 | Description:주물이 검사구간까지 이동한다.Functional: 벨트 구동벨트 정지Auto / Manual (Mode)Non-functional:이동 속도 : 1~100%검사구간 도착 처리설정된 Takt Time 내 이송 완료 |   |   |

- 

- 

- 

- 

- 

- 

- 

- 
|   |   | SR-01 조건에 따른 컨베이어 벨트 구동 [Description]주물 유무 상태에 따라 정지 구동하고, 비상정지, 검사구간 도착상태에서 정지한다.[details]주물 도착 감지주물이 없으면 벨트는 정지한다.비상정지 신호가 발생하면 즉시 정지한다.검사구간에 도착 감지되면 정지한다.생산중일때 Auto Mode 사용한다.고장 및 테스트 중일때는 Manual mode 사용한다.[Non-funtional] 컨베이어 벨트 구동 상세 조건 (검사 스킵 조건이면 바로 언로딩) |   |   |

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
| 예진 | 적재 기능 | 제품 적재 기능Description:식별된 제품을 지정된 위치에 물리적으로 배치하고, 작업 단계별 상태를 시스템에 동기화해야 한다.세부 요구사항제품을 식별(제품 ID,규격,수량)할 수 있어야 한다.작업 상태를 실시간으로 갱신할 수 있어야 한다.적재 완료시 시스템 및 관리자에게 알릴 수 있어야 한다.기존 물품과의 간섭을 방지하기 위한 안전 거리를 유지할 수 있어야 한다.작업 상태 :  입고 시작/적재 완료 / 장애 발생Non-functional:정확성 : 가상 시스템상의 위치 데이터와 실제 물리적 적재 위치가 오차 없이 일치해야 한다.안전성 : 최적 동선 이동 중 충돌 방지 및 물품 파손 방지를 위한 가감속 제어가 이루어져야 한다.가용성 : 데이터베이스 연결이 일시적으로 끊겨도 로컬 데이터를 활용해 최소한의 적재 작업은 지속 가능해야 한다. |   |   |

- 

  - 

- 

  - 

  - 

- 

  - 

  - 

  - 
|   |   | 최적 위치 할당 기능Description:제품의 속성과 창고 내 물류 흐름을 복합적으로 분석하여 공간 효율과 작업 속도를 극대화할 수 있는 최적의 지점을 도출해야 한다.Functional: 출고 빈도에 따라 ABC 등급으로 분류하고 우선순위 할당할 수 있어야한다.동선 및 제품 종류를 고려한 위치 선정할 수 있어야 한다.(슬로팅 최적화)Non-functional:응답성 : 위치 할당 요청 시 1초 이내에 배치 완료 지점 산출공간 효율성: 빈틈없는 적재를 통해 창고 수용량의 90% 이상 활용확장성 : 다른 제품군이 추가되거나 적재 구역이 늘어나도 알고리즘 수정 없이 대응 가능해야 함. |   |   |

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
|   |   | 제품 재배치 기능(swap)Description:보관 효율성을 높이기 위해 기존에 적재된 박스의 위치를 변경하거나, 새로운 적재를 위해 목적지에 있는 물품을 다른 빈 공간으로 안전하게 이동 시켜야 한다.Functional: 재배치 이벤트가 발생하면 즉각적으로 인지할 수 있어야 한다.최적 위치 할당을 요청할 수 있어야 한다.목적지가 점유 상태일 경우, 위치 재할당 요청할 수 있어야 한다.SWAP 작업을 실시할 수 있어야 한다.Non-functional:응답 지연 시간 : 재배치 요청 후 새로운 위치를 할당 받기까지의 통신 대기 시간은 1초 이내여야 한다.안정성: Swap 중 데이터 유실이 없어야 하며, 실패 시 이전 상태로 복구되어야 한다. |   |   |

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
|   |   | 예외 처리 기능Description:적재 및 재배치 과정에서 발생하는 물리적 장애, 데이터 불일치, 하드웨어 오류를 실시간으로 감지하여 시스템과 물품의 피해를 최소화하고 관리자에게 알린다Functional: 데이터상 '비어 있음'인 칸에 물체가 있거나, 점유인 칸이 비어 있는 경우를 감지하여 상태 갱신할 수 있어야 한다(상태 불일치 검증 )공간 부족, 규격 미달 공간, 식별 불가 제품 발생 시 해당 프로세스를 정지하고 관리자에게 알릴 수 있어야한다.자가 복구가 불가능한 치명적 오류 발생 시 관리자에게 알릴 수 있어야한다.세부 요구 사항상태공간 부족/규격 미달 공간/상태 불일치/식별 불가Non-functional:실시간성: 장애 상황 발생 시 즉각적인 감지 및 보고가 이루어져야 한다.신뢰성: 예외 처리 로직 실행 시 기존 정상 데이터가 파손되지 않도록 보호해야 한다. |   |   |

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
|   |   | 실시간 적재 지도(Map) 관리Description:모든 적재 구역의 상태를 파악하고, 위치별 상태 변화를 즉각적으로 업데이트하여 최신 적재 현황을 유지해야 한다.Functional: 각 적재 위치 별로 7가지 상태값을 정의하고 실시간으로 관리할 수 있어야 한다.적재 구역 상태 : 비어있음/점유중/예약됨/작업중/사용불가/상태 불일치/할당제한(특정 종류 물품만 들어올수있도록 필터링된 상태)물리적 적재/이동 이벤트 발생 시 지도상의 상태 데이터를 동기화할 수 있어야 한다.상태별로 구분된 색상을 적용해 시각적으로 적재 구역 상태를 제공할 수 있어야 한다.(빈칸-흰색, 점유-청색,사용불가-적색)모든 상태 변경 이력은 시간과 전/후 상태를 포함하여 로그(Log)로 기록해야 한다.Non-functional:데이터 일치성 : 물리적 위치 변화와 시스템 데이터 간의 일치율은 100%를 유지해야 하며, 주기적으로 전체 스캔을 통해 정정 로직을 수행해야 한다.업데이트 지연 시간: 적재 후 적재 지도에 반영되기까지의 시간은 1초 이내여야 한다 |   |   |

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
| 정원 | 출고 기능 | 출고지시 생성Description:사용자는 원격으로 출고지시를 생성한다.Functional:제품 종류 지정출고 일자 지정납품 회사 지정출고 갯수 지정 및 제품 재고와 비교출고지시 생성Non-functional:출고 갯수가 제품 재고 이하이어야 함 |   |   |

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
| 출고 지시 수행Description:출고를 위해 제품 수량 검증, 이적재 위치 확인, 차량 매칭 및 출고 완료 처리, 출고 이력 저장을 수행한다.Functional:차량 매칭이적재 위치 조회 및 출고 경로 최적화제품 식별제품 수량 검증출고 완료 처리 및 재고 차감Non-functional:출고지시서의 제품 종류에 맞춰 출고할 재고 분류​쌓여있는 재고를 후입선출(LIFO)방식으로 출고적재위치의 실수량과 재고데이터가 동일해야 함 |   |   |

- 

- 

  - 

- 

  - 

- 

  - 
| 출고 이력 저장Description:​출고 이력 저장을 수행한다.Functional:출고 이력 저장Non-functional:사용자가 출고 이력을 조회할 수 있어야 함 |   |   |
|   |   |   |

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
| 정연 | 후처리 기능 (사람) | SR_NAME: 후처리 구역 청소Description:후처리 구역을 청소한다 Functional:컨베이어 벨트 청소 before/cleaning/done후처리 공정 진행 (하나의 맨홀 기준) before / processing / done팔레트 적재 요청컨베이어 벨트 한칸 전진/정지 Non-functional:전체 청소시간은 3초 이내로 설정후처리 공정완료된 결과물은 팔레트에 3초이내로 적재(불량품도 예외없이 전용 팔레트에 적재) |   |   |
[2026.03.27] 

- 
회사 a: 발주내역 

- 
회사 b
[2026.03.28] 

- 
회사 c 

- 
발주 관리자, 공장 관리자 

- 
발주 (A 제품 3개, B제품 2개, C제품 3개)

- 
pattern 이 각자 정해진 위치에 존재한다. (pattern_pos_A, pattern_pos_B, pattern_pos_C)

- 
다품종 소량 생산 작업은 sequential 작업 예정 
참고 [https://narup.tistory.com/70#google_vignette](https://narup.tistory.com/70#google_vignette)

#### Copy of System_Requirements_v3 (5345066)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5345066
**최종 수정**: v2 (2026-04-19 sync)

****
****
****
****
| SR ID | SR Name | Description | Priority |
|---|---|---|---|
****
|   | 원격 발주 기능 | 고객이 표준화된 주조 제품을 선택하고, 규격/수량/납기/후처리 옵션을 입력하여 발주할 수 있는 원격 주문 시스템을 제공한다 |   |
****

- 

- 

  - 
|   |   | [하위 기능] 표준 제품 조회 기능사용자는 원격으로 주문 가능한 표준 주조 목록을 조회할 수 있어야한다.  [기능]제품 카테고리 조회제품별 상세 페이지 제공 규격별 기본 이미지, 이름,  재질, 기본 가격 범위, 하중 등급 |   |
****

- 

  - 

- 

- 

- 

  - 
|   |   | [하위 기능] 제품 옵션 선택 기능사용자는 선택한 제품에 대해 규격, 수량, 재질, 후처리 조건의 주문 사양을 입력할 수 있어야 한다.[기능]규격 옵션 직경, 두께, 하중 등급, 표면 마감, 로고/문구 삽입 여부, 재질 옵션, 후처리 옵션수량, 희망 납기일 비고란 제품별 상세 페이지 제공 규격별 기본 이미지, 이름,  재질, 기본 가격 범위, 하중 등급 |   |
****

- 

- 

- 

- 

- 
|   |   | [하위 기능] 도면/디자인 정보 확인 기능사용자는 주문 제품의 기본 디자인과 선택 사양을 주문 전에 확인할 수 있어야 한다. [기능]시스템은 선택한 규격과 옵션에 따른 제품 요약 정보를 보여줘야 한다.시스템은 기본 디자인 시안을 표시해야 한다.시스템은 텍스트 삽입, 마크 삽입 등의 옵션 선택 결과를 미리보기 형태로 보여줄 수 있어야 한다.시스템은 자유형 복잡 설계가 아닌 표준 템플릿 기반 입력을 지원해야 한다.사용자는 전문 CAD 지식 없이도 주문할 수 있어야 한다. |   |
****

- 

- 

- 
|   |   | [하위 기능] 주문 가능 여부 검증 기능시스템은 사용자가 입력한 주문 조건의 유효성을 검증해야 한다. [기능]시스템은 허용된 규격 조합인지 검증할 수 있어야 한다시스템은 최소/최대 수량 조건을 검증할 수 있어야 한다시스템은 유효하지 않은 입력에 대해 오류를 반환해야 한다 |   |
****

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 예상 견적 및 납기 안내 기능시스템은 사용자가 입력한 주문 조건을 바탕으로 예상 견적과 예상 납기를 제공해야 한다.[기능]시스템은 제품 기본 단가를 기반으로 예상 가격을 계산해야 한다.시스템은 옵션에 따라 추가 비용을 반영해야 한다.시스템은 수량에 따른 가격 변동을 반영할 수 있어야 한다.시스템은 예상 납기 범위를 표시해야 한다.시스템은 최종 견적은 관리자 검토 후 확정됨을 안내해야 한다.시스템은 주문 정보를 저장할 수 있어야 한다시스템은 주문 ID를 생성할 수 있어야 한다 |   |
****

- 

- 

- 
|   |   | [하위 기능: 원격 주문서 제출 기능]사용자는 입력한 제품 정보와 주문 조건에 따라 주문 요청서를 제출할 수 있어야 한다.[기능]주문자 회사명, 연락처, 배송지 정보시스템은 주문 요약서 생성 및 사용자는 확인 후 제출할 수 있어야 한다. [비기능]주문 절차는 5단계 이내로 완료 가능해야 한다. |   |
****

- 

- 

- 

- 
|   |   | [하위 기능: 주문 상태 조회 기능]사용자는 제출한 주문의 처리 상태를 조회할 수 있어야 한다[기능]시스템은 주문 접수 상태를 표시해야 한다.시스템은 검토 중, 승인됨, 생산 중, 출하 준비, 완료 상태를 표시해야 한다.사용자는 주문 상세 내역을 다시 확인할 수 있어야 한다.시스템은 상태 변경 시 알림을 제공할 수 있어야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능: 관리자 주문 검토 및 승인 기능]관리자는 접수된 주문 요청을 검토하고 승인 또는 수정 요청할 수 있어야 한다.[기능]관리자는 주문 상세 사양을 확인할 수 있어야 한다.관리자는 생산 가능 여부를 검토할 수 있어야 한다.관리자는 예상 견적과 납기를 조정할 수 있어야 한다.관리자는 주문 승인, 반려, 수정 요청 처리를 할 수 있어야 한다.[비기능]주문자 정보와 연락처는 안전하게 저장되어야 한다.관리자 기능은 권한이 있는 사용자만 접근 가능해야 한다. |   |
|   | 관제 기능 | 시스템은 전체 주조 공정과 이송 시스템을 통합적으로 관리하기 위해 공정 상태, 장비 상태 및 이송 자원의 상태를 실시간으로 모니터링하고, 관리자가 이를 기반으로 제어 및 대응할 수 있도록 지원해야 한다. 또한 시스템은 전체 공정 레이아웃(Map) 상에서 로봇 및 이송 자원의 위치와 상태를 시각적으로 표시하여, 운영 상황을 직관적으로 파악할 수 있어야 한다. |   |
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
|   |   | [하위 기능] 공정 Map 기반 실시간 모니터링 기능 시스템은 공정 레이아웃(Map) 상에서 이송 자원 및 주요 설비의 위치와 상태를 실시간으로 시각화하여 관리자가 전체 운영 상황을 직관적으로 파악할 수 있도록 해야 한다.[기능] 시스템은 공장 전체 레이아웃(Map)을 화면에 표시할 수 있어야 한다.시스템은 이송 자원의 현재 위치를 Map 상에 표시할 수 있어야 한다.시스템은 각 이송 자원의 상태(유휴, 이동 중, 작업 중, 오류 등)를 시각적으로 표시할 수 있어야 한다.시스템은 주요 공정 설비(용해로, 주형 제작 장비, 검사 구간 등)의 위치와 상태를 Map 상에 표시할 수 있어야 한다.시스템은 공정 상태에 따라 색상, 아이콘 등의 시각적 요소로 상태를 구분하여 표시할 수 있어야 한다.시스템은 특정 자원 또는 설비를 선택하면 상세 정보를 조회할 수 있어야 한다.[비기능] 시스템은 위치 및 상태 정보를 실시간 또는 준실시간으로 갱신해야 한다.시스템은 다수의 이송 자원 및 설비를 동시에 표시하더라도 성능 저하 없이 동작해야 한다.시스템은 사용자가 직관적으로 상태를 인식할 수 있도록 UI를 구성해야 한다. |   |
****
|   |   | [하위 기능] 공정 모니터링 기능관리자는 전체 공정의 상태 및 생산 데이터를 실시간으로 모니터링할 수 있어야 한다.[기능] |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능: 공정 제어 기능] 관리자는 공정 장비를 제어하여 전체 생산 공정을 관리할 수 있어야 한다.[기능]시스템은 장비별 상태(시작 / 중지 / 재개)를 제어할 수 있어야 한다.시스템은 관리자의 제어 명령을 각 장비에 전달할 수 있어야 한다.시스템은 장비의 현재 상태를 확인할 수 있어야 한다.[비기능]시스템은 관리자의 명령을 즉시 반영해야 한다.시스템은 긴급 상황 시 장비를 즉시 정지할 수 있어야 한다.시스템은 제어 명령 수행 중에도 시스템 안정성을 유지해야 한다. |   |
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
|   |   | [하위 기능: 이상 감지 및 알림 기능] 시스템은 공정 중 발생하는 이상 상태를 감지하고 관리자에게 알림을 제공할 수 있어야 한다. [기능]시스템은 용해 공정 상태(용해 중 / 미용해)를 표시해야 한다.시스템은 주형 제작 공정 상태(정상 / 비정상)를 표시해야 한다.시스템은 주조 공정 상태(주조 중 / 응고 중 / 완료)를 표시해야 한다.시스템은 후처리 공정 상태(작업 중 / 청소 중 / 완료)를 표시해야 한다.시스템은 불량품 통계를 제공해야 한다.총 생산량양품/불량품 수량불량률시스템은 적재 및 출고 상태를 표시해야 한다.주물 수량출고 가능 여부[비기능] 시스템은 이상 상태를 실시간 또는 준실시간으로 감지해야 한다.시스템은 알림 정보를 명확하게 전달할 수 있어야 한다.시스템은 다수의 알림 발생 시에도 우선순위를 구분할 수 있어야 한다. |   |
|   | 주물 생산 자동화 공정 기능 |   |   |
****

- 

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능: 원재료 준비 및 투입 기능]시스템은 원재료를 선별 및 검증한 후, 적정 조건을 만족하는 경우 도가니 또는 레이들에 투입할 수 있어야 한다.[기능]시스템은 원재료에서 물성과 맞지 않는 이물질을 분리할 수 있어야 한다.시스템은 원재료가 도가니에 투입 가능한 크기인지 판단할 수 있어야 한다.시스템은 도가니에 투입된 원재료의 양이 적정량인지 확인할 수 있어야 한다.시스템은 검증된 원재료를 도가니 또는 레이들에 자동 또는 반자동으로 투입할 수 있어야 한다.[비기능]시스템은 원재료와 이물질을 최소 2단계 이상의 분리 공정을 통해 선별할 수 있어야 한다.시스템은 도가니 부피 대비 원재료 투입량이 약 80% 수준을 유지하도록 제어되어야 한다.시스템은 원재료 투입 과정에서 안전 기준을 만족하도록 설계되어야 한다.시스템은 다양한 원재료 종류 및 물성 변화에 대응할 수 있도록 확장 가능해야 한다. |   |
****

- 

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 원재료 융용 기능 시스템은 원재료를 가열하여 완전한 용탕 상태로 용융하고, 해당 상태를 안정적으로 유지할 수 있어야 한다.[기능] 시스템은 도가니 내부의 원재료에 열을 가하여 용융할 수 있어야 한다.시스템은 용융 과정에서 용탕의 온도를 측정할 수 있어야 한다.시스템은 용융 소요 시간을 측정할 수 있어야 한다.시스템은 용융 완료 후 용탕의 온도를 일정하게 유지(등온 상태)할 수 있어야 한다.[비기능]시스템은 용탕 내 고체 성분이 남지 않도록 완전 용융 상태를 유지해야 한다.시스템은 상온(약 25°C)에서 가열을 시작할 수 있어야 한다.시스템은 목표 온도 범위 내에서 안정적인 온도 제어가 가능해야 한다.시스템은 온도 측정 및 제어 과정에서 허용 오차 범위를 만족해야 한다. |   |
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
|   |   | [하위 기능] 주형 제작 기능시스템은 패턴을 이용하여 주형사에 압력을 가해 주형을 제작하고, 해당 공정을 자동으로 수행할 수 있어야 한다.[기능] 시스템은 패턴의 형태 및 유형을 식별할 수 있어야 한다.시스템은 식별된 패턴을 파지(grasp) 및 이송할 수 있어야 한다.시스템은 주형 제작을 위해 패턴의 위치와 방향을 정밀하게 정렬할 수 있어야 한다.시스템은 패턴을 주형사에 수직 방향으로 압입하여 주형을 제작할 수 있어야 한다.시스템은 주형 제작 완료 후 패턴을 주형으로부터 안전하게 분리할 수 있어야 한다.시스템은 주형 제작에 사용된 패턴 정보 및 공정 데이터를 저장할 수 있어야 한다.[비기능]시스템은 패턴의 위치 및 방향을 기준 좌표계(패턴 중심 좌표)를 기반으로 정렬해야 한다.시스템은 주형사에 대한 압입 방향을 수직으로 유지해야 한다.시스템은 제작된 주형의 형상이 패턴 원형 대비 90% 이상 정밀도를 만족해야 한다.시스템은 반복 공정 수행 시에도 일관된 품질을 유지할 수 있어야 한다. |   |
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
|   |   | [하위 기능] 주탕 기능 시스템은 용융된 용탕을 주형으로 안전하고 정확하게 주입(주탕)할 수 있어야 한다.[기능]시스템은 도가니(또는 레이들)와 주형의 위치를 인식할 수 있어야 한다.시스템은 인식된 위치 정보를 기반으로 도가니를 주형 위치로 이송할 수 있어야 한다.시스템은 주형과 도가니의 상대 위치를 정렬하여 정확한 주입이 가능하도록 해야 한다.시스템은 도가니 내 용탕을 주형에 안정적으로 주입할 수 있어야 한다.시스템은 주탕 완료 후 도가니를 원래 위치로 복귀시킬 수 있어야 한다.[비기능]시스템은 주탕 과정에서 작업자 및 장비와의 충돌을 방지할 수 있도록 안전한 이동 경로를 확보해야 한다.시스템은 이송 경로를 최적화하여 작업 시간을 최소화해야 한다.시스템은 용탕 주입 과정에서 넘침, 부족 주입 등의 오류를 방지할 수 있어야 한다.시스템은 고온 환경에서도 안정적으로 동작해야 한다. |   |
****

- 

- 

- 

- 
|   |   | [하위 기능] 주물 냉각 완료 탐지 기능 시스템은 주물의 냉각 여부를 확인할 수 있어야 한다.[기능]시스템은 사용자로부터 제품 별 냉각에 걸리는 시간을 입력받고 저장할 수 있어야 한다.시스템은 사용자로부터 입력받은 냉각에 걸리는 시간정보를 제작되는 주형에 대입하고 계산할 수 있어야 한다.시스템은 센서를 통해 취득한 정보를 통해 냉각 진행상태를 파악할 수 있어야 한다. [비기능] ​시스템은 센서를 통해 취득한 정보를 통해 냉각 진행상태를 파악할 수 있어야 한다. |   |
****

- 

- 

- 
|   |   | [하위 기능] 탈형 기능 시스템은 냉각이 완료된 주물을 주형으로부터 분리(탈형)하고, 해당 결과를 기록할 수 있어야 한다.[기능]시스템은 냉각된 주물의 위치 정보를 파악할 수 있어야 한다.시스템은 주물의 손상없이 주물을 탈형할 수 있어야 한다.주물의 탈형 후, 시스템은 주물의 모양과 유형을 기록할 수 있어야 한다. |   |
|   | 구역 간 이송 기능 | 이송 자원으로 구역 간 이송 대상 물품을 이송하는 기능 |   |
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
|   |   | [하위 기능] 이송 요청 생성 기능 시스템은 이송 요청을 생성할 수 있어야 한다.[기능]시스템은 생성된 이송 요청에 대해 고유 식별 번호(task id)를 부여해야 한다.출발 위치와 도착 위치 정보를 저장해야 한다.이송 대상 물품의 종류와 수량 정보를 저장해야 한다.요청 시각, 이송 상태, 배정된 이송 자원을 저장해야 한다.[비기능]이송 요청은 기본적으로 요청 순서대로 처리되어야 한다.단, 우선순위에 따라 순서가 조정될 수 있어야 한다.이송 요청 정보는 누락 없이 저장되어야 한다.여러 이송 요청이 동시에 생성되더라도 독립적으로 처리될 수 있어야 한다. |   |
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
|   |   | [하위 기능] 이송 요청 상태 관리 기능 관리자는 각 이송 요청의 진행 상태 및 이력을 조회하고, 이를 기반으로 작업을 관리할 수 있어야 한다.[기능] 관리자 기능 관리자는 이송 요청 식별 번호를 통해 각 요청의 현재 진행 상태를 조회할 수 있어야 한다.관리자는 이송 요청의 상세 정보(출발 위치, 도착 위치, 물품 종류, 수량)를 조회할 수 있어야 한다.관리자는 완료된 이송 요청의 결과를 조회할 수 있어야 한다.관리자는 실패한 이송 요청의 실패 사유를 조회할 수 있어야 한다.시스템 기능 시스템은 각 이송 요청의 진행 상태 및 단계(예: 대기, 배정, 이송 중, 완료, 실패)를 추적할 수 있어야 한다.시스템은 이송 요청의 상태 변경 시각을 기록할 수 있어야 한다.시스템은 이송 요청의 상태 이력을 저장하고 관리할 수 있어야 한다.[비기능] 시스템은 이송 요청 상태 정보를 실시간 또는 준실시간으로 갱신해야 한다.시스템은 상태 정보 조회 시 빠른 응답 속도를 제공해야 한다.시스템은 다수의 이송 요청을 동시에 처리하더라도 안정적으로 상태를 관리할 수 있어야 한다.시스템은 상태 이력 데이터의 무결성을 보장해야 한다. |   |
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
|   |   | [하위 기능] 이송 자원 관리 및 배정 기능시스템은 유휴 상태의 이송 자원을 대기 위치로 복귀시키거나 이송 요청에 배정 할 수 있어야 하고, 각 이송 자원 별 상태를 관리해야 한다.[기능] 시스템은 각 이송 자원의 상태(유휴, 작업 중, 충전 필요 등)를 확인할 수 있어야 한다.시스템은 유휴 상태의 이송 자원을 이송 요청에 배정할 수 있어야 한다.시스템은 이송 자원 배정 결과를 이송 작업 상태에 반영할 수 있어야 한다.시스템은 배정된 이송 자원을 출발 위치로 호출할 수 있어야 한다.시스템은 동일한 이송 자원이 동시에 복수의 요청에 배정되지 않도록 관리해야 한다.시스템은 이송 자원의 동력이 일정 수준 이하로 떨어질 경우, 해당 자원을 충전 또는 대기 위치로 이동시킬 수 있어야 한다.시스템은 작업이 종료된 이송 자원을 대기 위치로 복귀시킬 수 있어야 한다.[비기능] 시스템은 이송 자원 배정 시 자원의 상태(유휴 여부), 동력 수준, 거리 등을 종합적으로 고려하여 최적의 자원을 선택해야 한다.시스템은 자원 배정 및 상태 갱신을 실시간 또는 준실시간으로 수행해야 한다.시스템은 다수의 이송 요청이 동시에 발생하더라도 안정적으로 자원 배정이 가능해야 한다.시스템은 자원 충돌 및 비효율적인 경로 할당을 방지할 수 있도록 설계되어야 한다. |   |
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
|   |   | [하위 기능] 출발 조건 확인 기능 시스템은 이송 작업 시작 전, 출발 위치에서 이송이 가능한 상태인지 검증하고 그 결과를 반영할 수 있어야 한다.[기능] 시스템은 이송 자원이 출발 위치에 도착해 있는지 확인할 수 있어야 한다.시스템은 이송 자원에 이송 대상 물품이 정상적으로 적재되어 있는지 확인할 수 있어야 한다.시스템은 출발 위치의 물품 정보가 이송 요청 정보와 일치하는지 확인할 수 있어야 한다.물품 종류물품 식별 정보시스템은 요청된 수량과 실제 적재된 수량이 일치하는지 확인할 수 있어야 한다.시스템은 출발 조건 검증 결과를 이송 요청 상태에 반영할 수 있어야 한다.[비기능]시스템은 출발 조건이 일정 시간 내 충족되지 않을 경우, timeout을 발생시키고 예외 상태로 처리해야 한다.시스템은 출발 조건 검증을 실시간 또는 준실시간으로 수행해야 한다.시스템은 검증 실패 시 원인을 식별할 수 있도록 로그를 기록해야 한다.시스템은 다양한 물품 유형 및 이송 조건에 대해 확장 가능해야 한다. |   |
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
|   |   | [하위 기능] 물품 인계, 인수 확인 기능 시스템은 출발 위치와 도착 위치에서 물품의 인계 및 인수 과정이 정상적으로 수행되었는지 검증하고, 그 결과를 반영할 수 있어야 한다.[기능] 출발 위치 (인계)시스템은 출발 위치에서 이송 대상 물품이 이송 자원에 정상적으로 인계되었는지 확인할 수 있어야 한다.도착 위치 (인수) 시스템은 도착 위치에서 이송 대상 물품이 정상적으로 인수되었는지 확인할 수 있어야 한다.공통 검증 시스템은 인계 및 인수된 물품의 종류와 수량이 이송 요청과 일치하는지 검증할 수 있어야 한다.시스템은 인계 및 인수 결과를 이송 요청 상태에 반영할 수 있어야 한다.시스템은 인계 또는 인수 실패 시 해당 요청을 예외 처리 상태로 전환할 수 있어야 한다[비기능] 시스템은 인계 및 인수 검증 결과를 실시간 또는 준실시간으로 반영해야 한다.시스템은 인계 및 인수 과정에서 발생한 이벤트 및 결과를 로그로 기록해야 한다.시스템은 물품 정보 및 수량 데이터의 무결성을 보장해야 한다.시스템은 반복적인 인계/인수 작업에서도 일관된 검증 정확도를 유지해야 한다. |   |

- 

- 

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 도착 위치 이동 기능 시스템은 이송 자원이 이송 대상 물품을 출발 위치에서 도착 위치까지 안전하게 이동시킬 수 있어야 한다.[기능] 시스템은 배정된 이송 자원이 이송 대상 물품을 적재한 상태로 도착 위치까지 이동할 수 있어야 한다.시스템은 도착 위치까지의 이동 경로를 따라 이송 자원을 제어할 수 있어야 한다.시스템은 이송 자원이 도착 위치에 도착했는지 확인할 수 있어야 한다.시스템은 도착 위치 도착 후 이송 요청 상태를 변경할 수 있어야 한다.[비기능]시스템은 이송 중 충돌 위험이 없는 안전하고 유효한 경로를 따라 이동해야 한다.시스템은 지정된 도착 위치에 대해 위치 오차 ±5 cm 이내를 만족해야 한다.시스템은 지정된 도착 위치에 대해 자세 오차 ±5° 이내를 만족해야 한다.시스템은 이송 중 물품의 파손 또는 낙하가 발생하지 않도록 해야 한다.시스템은 이송 자원의 주행 속도를 직진 시 1.0 m/s 이하, 회전 시 0.5 m/s 이하로 제한해야 한다. |   |

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

- 
|   |   | [하위 기능] 이송 예외 처리 기능 시스템은 이송 수행 중 발생하는 예외 상황을 감지하고, 적절한 처리 및 상태 전환을 수행할 수 있어야 한다.[기능] 예외 감지 시스템은 이송 자원 배정 실패를 감지할 수 있어야 한다.시스템은 출발 조건 검증 실패를 감지할 수 있어야 한다.시스템은 출발 위치에서 물품 인계 실패를 감지할 수 있어야 한다.시스템은 이동 중 장애 또는 실패 상황을 감지할 수 있어야 한다.시스템은 도착 위치에서 물품 인수 실패를 감지할 수 있어야 한다.예외 처리 및 상태 전환 시스템은 예외 상황 발생 시 이송 요청 상태를 대기, 재시도, 실패 상태로 전환할 수 있어야 한다.시스템은 예외 상황 발생 시 실패 사유를 기록할 수 있어야 한다.시스템은 기록된 실패 사유를 조회할 수 있어야 한다.알림 및 복구 시스템은 복구 불가능한 예외 상황 발생 시 관리자에게 알림을 제공할 수 있어야 한다.시스템은 시스템 전체 정지 상황 발생 시, 진행 중인 이송 작업을 안전하게 종료할 수 있어야 한다.[비기능]시스템은 예외 상황을 실시간 또는 준실시간으로 감지하고 처리해야 한다.시스템은 예외 상황 발생 시 데이터의 일관성과 상태 무결성을 보장해야 한다.시스템은 예외 처리 과정에서 추가적인 시스템 장애가 발생하지 않도록 안정적으로 동작해야 한다.시스템은 다양한 예외 유형에 대해 확장 가능하도록 설계되어야 한다. |   |

- 
|   | 주물 검사 및 분류 기능 | 시스템은 완성된 주물의 품질을 검사하여 양품 또는 불량품으로 판정하고, 판정 결과에 따라 주물을 적절한 위치로 분류할 수 있어야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 주물 품질 검증 기능 시스템은 완성된 주물의 상품성을 검증하여 양품 또는 불량품으로 판정할 수 있어야 한다.[기능] 시스템은 검사 대상 주물을 인식할 수 있어야 한다.시스템은 주물의 외관, 형상 또는 정의된 품질 기준을 바탕으로 양품 여부를 판정할 수 있어야 한다.시스템은 주물의 검증 결과를 양품 또는 불량품으로 반환할 수 있어야 한다.[비기능] 품질 검증 정확도는 95% 이상이어야 한다.시스템은 1초 이내에 검증 결과를 반환해야 한다.시스템은 검증 결과를 바탕으로 양품 및 불량품 수량을 실시간 또는 준실시간으로 갱신해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 검증 결과 관리 기능 시스템은 주물의 품질 판정 결과를 저장하고, 관련 통계 및 추적 정보를 관리할 수 있어야 한다.[기능]시스템은 각 주물의 검증 결과를 저장할 수 있어야 한다.시스템은 양품 및 불량품 수량을 누적 관리할 수 있어야 한다.시스템은 검증 시각 및 판정 이력을 기록할 수 있어야 한다.시스템은 불량 판정 시 실패 사유 또는 불량 유형을 기록할 수 있어야 한다.[비기능]시스템은 결과 데이터의 무결성을 보장해야 한다.시스템은 실시간 조회가 가능하도록 결과 데이터를 갱신해야 한다. |   |
****

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 주물 분류 실행 기능 시스템은 검증 결과에 따라 양품 주물과 불량품 주물을 서로 다른 위치로 분류할 수 있어야 한다.[기능]시스템은 검증 결과를 입력받아 분류 동작을 결정할 수 있어야 한다.시스템은 양품 판정 시 주물을 양품 적재 위치로 분류할 수 있어야 한다.시스템은 불량품 판정 시 주물을 불량품 적재 위치로 분류할 수 있어야 한다.시스템은 분류 장치의 상태를 제어할 수 있어야 한다.[비기능]분류 정확도는 99% 이상이어야 한다.시스템은 검증 완료 후 1초 이내에 분류 준비 상태가 되어야 한다.시스템은 다음 검증 결과가 입력될 때까지 현재 분류 상태를 안정적으로 유지해야 한다. |   |

- 

- 

- 

- 

- 
|   |   | [하위 기능] 분류 장치 제어 기능 시스템은 분류 결과에 따라 모터 또는 액추에이터를 제어하여 주물의 배출 방향을 결정할 수 있어야 한다.[기능]시스템은 양품 판정 시 분류 장치를 양품 배출 위치로 제어할 수 있어야 한다.시스템은 불량품 판정 시 분류 장치를 불량품 배출 위치로 제어할 수 있어야 한다.시스템은 분류 장치의 현재 각도 또는 상태를 확인할 수 있어야 한다.[비기능]시스템은 지정된 제어 각도 오차 범위 내에서 동작해야 한다.시스템은 반복 동작 시에도 안정적으로 분류 상태를 유지해야 한다. |   |

- 

- 

- 
|   | 컨베이어 이송 제어 기능 | 시스템은 주물을 검사 구간까지 이송하기 위해 컨베이어 벨트를 구동, 정지 및 제어할 수 있어야 한다.[비기능(공통)]시스템은 설정된 Takt Time 내에 주물을 검사 구간까지 이송할 수 있어야 한다.시스템은 검사 시스템 및 상위 관제 시스템과 연동 가능하도록 설계되어야 한다.시스템은 안전 정지 및 비상정지를 우선적으로 처리해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 컨베이어 구동 및 정지 기능 시스템은 입력된 명령 및 센서 상태에 따라 컨베이어 벨트를 구동하거나 정지할 수 있어야 한다.[기능] 시스템은 Start 명령에 따라 컨베이어 벨트를 구동할 수 있어야 한다.시스템은 Stop 명령에 따라 컨베이어 벨트를 정지할 수 있어야 한다.시스템은 주물 존재 여부에 따라 벨트 구동 여부를 판단할 수 있어야 한다.시스템은 벨트의 현재 구동 상태를 확인할 수 있어야 한다.[비기능]시스템은 구동 및 정지 명령에 대해 즉시 또는 정의된 응답 시간 내 반응해야 한다.시스템은 반복적인 구동 및 정지 상황에서도 안정적으로 동작해야 한다. |   |
****

- 

- 

- 

- 

- 
|   |   | [하위 기능] 이동 속도 제어 기능 시스템은 검사 공정 조건과 Takt Time을 고려하여 컨베이어 벨트의 이송 속도를 제어할 수 있어야 한다.[기능]시스템은 속도 설정값을 입력받을 수 있어야 한다.시스템은 설정된 레시피 또는 운전 조건에 따라 벨트 속도를 제어할 수 있어야 한다.시스템은 현재 벨트 속도 상태를 확인할 수 있어야 한다.[비기능]시스템은 이송 속도를 1~100% 범위 내에서 설정 가능해야 한다.시스템은 설정된 Takt Time 내 이송 완료를 만족하도록 속도를 제어해야 한다. |   |

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 운전 모드 전환 기능 시스템은 생산 및 유지보수 상황에 따라 컨베이어 벨트의 운전 모드를 전환할 수 있어야 한다.[기능] 시스템은 Auto Mode와 Manual Mode를 전환할 수 있어야 한다.시스템은 생산 중에는 Auto Mode를 사용할 수 있어야 한다.시스템은 고장 점검, 테스트 또는 수동 조작이 필요한 경우 Manual Mode를 사용할 수 있어야 한다.시스템은 현재 운전 모드를 표시할 수 있어야 한다.[비기능]시스템은 모드 전환 시 현재 상태 정보를 유지하거나 안전한 초기 상태로 전환해야 한다.시스템은 모드 전환 중 오동작이 발생하지 않도록 해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 검사구간 도착 감지 및 정지 기능 시스템은 주물이 검사 구간에 도착했는지 감지하고, 필요한 경우 컨베이어 벨트를 정지시킬 수 있어야 한다.[기능]시스템은 검사구간 도착 센서 신호를 수신할 수 있어야 한다.시스템은 주물이 검사 구간에 도착한 경우 벨트를 정지할 수 있어야 한다.시스템은 검사구간 도착 완료 신호를 상위 시스템 또는 검사 시스템에 전달할 수 있어야 한다.시스템은 검사 스킵 조건에 따라 정지 없이 후속 구간으로 이송할 수 있어야 한다.[비기능]시스템은 도착 센서 감지 후 정의된 시간 내 벨트를 정지해야 한다.시스템은 검사구간 정지 위치에 대해 허용 오차 범위를 만족해야 한다. |   |

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 비상정지 및 예외 정지 기능 시스템은 비상 상황 또는 정의된 예외 조건 발생 시 컨베이어 벨트를 안전하게 정지시킬 수 있어야 한다.[기능] 시스템은 비상정지 신호를 수신할 수 있어야 한다.시스템은 비상정지 신호 입력 시 즉시 벨트를 정지할 수 있어야 한다.시스템은 주물이 없는 경우 벨트를 정지할 수 있어야 한다.시스템은 예외 정지 발생 시 알람 상태 신호를 출력할 수 있어야 한다.[비기능]시스템은 비상정지 신호를 최우선으로 처리해야 한다.시스템은 정지 후 재기동 전 안전 상태 확인 절차를 지원해야 한다. |   |

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 검사 시스템 연동 기능 시스템은 검사 시스템 및 관제 시스템과 연동하여 컨베이어 이송 상태와 검사 수행 조건을 공유할 수 있어야 한다.[기능] 시스템은 검사 시작을 위한 상태 신호를 제공할 수 있어야 한다.시스템은 검사구간 도착 완료 신호를 외부 시스템에 전달할 수 있어야 한다.시스템은 검사 결과 또는 검사 가능 여부에 따라 벨트 정지 또는 재이송 동작을 수행할 수 있어야 한다.시스템은 상위 관제 시스템으로부터 구동, 정지 및 상태 관련 명령을 수신할 수 있어야 한다.[비기능] 시스템은 외부 시스템과의 신호 연동 시 데이터 지연 없이 안정적으로 동작해야 한다.시스템은 단독 운전과 관제 연동 운전을 모두 지원할 수 있어야 한다. |   |
|   | 적재 관리 기능 | 시스템은 주물 및 제품을 효율적으로 적재하기 위해 적재 위치를 관리하고, 최적의 위치를 할당하며, 필요 시 재배치를 수행하고, 전체 적재 상태를 실시간으로 관리할 수 있어야 한다. |   |
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
|   |   | [하위 기능] 제품 적재 기능 시스템은 식별된 제품을 지정된 위치에 안전하게 적재하고, 작업 상태를 실시간으로 관리할 수 있어야 한다.[기능] 시스템은 제품 정보를 식별할 수 있어야 한다.제품 ID, 규격, 수량시스템은 제품을 지정된 위치에 물리적으로 적재할 수 있어야 한다.시스템은 기존 물품과의 간섭을 방지하기 위해 안전 거리를 유지할 수 있어야 한다.시스템은 적재 작업 상태(입고 시작 / 적재 완료 / 장애 발생)를 관리할 수 있어야 한다.시스템은 작업 상태를 실시간 또는 준실시간으로 갱신할 수 있어야 한다.시스템은 적재 완료 시 시스템 및 관리자에게 알림을 제공할 수 있어야 한다.[비기능]가상 시스템상의 위치 데이터와 실제 물리적 적재 위치가 오차 없이 일치해야 한다.최적 동선 이동 중 충돌 방지 및 물품 파손 방지를 위한 가감속 제어가 이루어져야 한다.데이터베이스 연결이 일시적으로 끊겨도 로컬 데이터를 활용해 최소한의 적재 작업은 지속 가능해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 최적 위치 할당 기능 시스템은 제품 특성과 물류 흐름을 고려하여 공간 효율과 작업 효율을 극대화할 수 있는 적재 위치를 산출할 수 있어야 한다.[기능]시스템은 출고 빈도 기반으로 제품을 ABC 등급으로 분류할 수 있어야 한다.시스템은 제품 종류, 동선, 거리 등을 고려하여 적재 위치를 결정할 수 있어야 한다.시스템은 위치 할당 요청에 대해 최적 위치를 반환할 수 있어야 한다.[비기능]응답성: 위치 할당은 1초 이내 수행되어야 한다.공간 효율성: 창고 공간 활용률은 90% 이상을 목표로 해야 한다.확장성: 제품군 및 적재 구역 확장 시 추가 수정 없이 대응 가능해야 한다. |   |
****

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 제품 재배치 기능 시스템은 공간 효율 및 작업 효율을 향상시키기 위해 기존 적재된 제품의 위치를 변경하거나 교환(Swap)할 수 있어야 한다.[기능]시스템은 재배치 이벤트를 감지할 수 있어야 한다.시스템은 재배치 대상 제품의 위치 정보를 확인할 수 있어야 한다.시스템은 최적 위치 할당 기능을 호출할 수 있어야 한다.시스템은 목적지가 점유된 경우 대체 위치를 할당할 수 있어야 한다.시스템은 제품 간 Swap 작업을 수행할 수 있어야 한다.[비기능]응답성: 재배치 요청 후 위치 할당까지 1초 이내 수행안정성: Swap 중 데이터 유실이 없어야 하며, 실패 시 이전 상태로 복구 가능해야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 적재 예외 처리 기능 시스템은 적재 및 재배치 과정에서 발생하는 물리적 및 논리적 오류를 감지하고, 적절한 대응을 수행할 수 있어야 한다.[기능] 시스템은 적재 상태 불일치를 감지할 수 있어야 한다.(비어있음 ↔ 실제 점유 불일치)시스템은 공간 부족 또는 규격 미달 상황을 감지할 수 있어야 한다.시스템은 식별 불가 제품 발생 시 프로세스를 중단하고 관리자에게 알릴 수 있어야 한다.시스템은 치명적 오류 발생 시 관리자에게 알림을 제공할 수 있어야 한다.[비기능]실시간성: 예외 상황은 즉시 감지되어야 한다.신뢰성: 예외 처리 과정에서 기존 데이터는 보호되어야 한다. |   |
****

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 실시간 적재 지도 (Map) 관리 기능 시스템은 모든 적재 위치의 상태를 실시간으로 관리하고, 이를 시각적으로 제공하여 전체 적재 현황을 파악할 수 있어야 한다.[기능] 시스템은 각 적재 위치의 상태를 관리할 수 있어야 한다.(비어있음 / 점유 / 예약 / 작업중 / 사용불가 / 상태불일치 / 할당제한)시스템은 적재 및 이동 이벤트 발생 시 지도 상태를 갱신할 수 있어야 한다.시스템은 상태별 색상 또는 UI 요소를 통해 시각적으로 표시할 수 있어야 한다.시스템은 모든 상태 변경 이력을 로그로 기록할 수 있어야 한다.[비기능]데이터 일치성: 물리적 상태와 시스템 상태는 항상 일치해야 한다.응답성: 상태 변경은 1초 이내 반영되어야 한다. |   |
|   | 출고 관리 기능 | 시스템은 출고 지시 생성부터 출고 수행, 이력 관리까지 전 과정을 통합적으로 관리하여 정확하고 효율적인 출고를 지원해야 한다. |   |

- 

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 출고 지시서 생성 기능 사용자는 원격으로 출고 지시서를 생성하고, 출고 조건을 설정할 수 있어야 한다.[기능]시스템은 제품 종류를 지정할 수 있어야 한다.시스템은 출고 일자를 지정할 수 있어야 한다.시스템은 납품 회사를 지정할 수 있어야 한다.시스템은 출고 수량을 입력받을 수 있어야 한다.시스템은 입력된 출고 수량과 현재 재고를 비교할 수 있어야 한다.시스템은 출고 지시서를 생성하고 식별 ID를 부여할 수 있어야 한다.[비기능]시스템은 출고 수량이 재고 이하인 경우에만 출고 지시를 생성해야 한다.시스템은 출고 지시 생성 시 데이터 무결성을 보장해야 한다. |   |

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
|   |   | [하위 기능] 출고 수행 기능 시스템은 출고 지시서를 기반으로 제품 식별, 수량 검증, 위치 조회 및 이송을 수행하여 출고를 완료할 수 있어야 한다.[기능]준비 및 검증 시스템은 출고 대상 제품을 식별할 수 있어야 한다.시스템은 출고 대상 제품의 수량을 검증할 수 있어야 한다.시스템은 적재 위치 및 실제 재고를 조회할 수 있어야 한다.이송 및 처리 시스템은 출고를 위한 차량을 매칭할 수 있어야 한다.시스템은 출고 경로를 최적화하여 제품을 이송할 수 있어야 한다.완료 처리 시스템은 출고 완료 시 재고를 차감할 수 있어야 한다.시스템은 출고 완료 상태를 시스템에 반영할 수 있어야 한다.[비기능]시스템은 출고 지시서의 제품 조건에 맞는 재고만을 선택해야 한다.시스템은 정의된 출고 정책(예: LIFO 등)을 적용할 수 있어야 한다.시스템은 물리적 재고와 시스템 재고 간 일치성을 유지해야 한다.시스템은 출고 과정에서 오류가 발생하지 않도록 안정적으로 동작해야 한다. |   |
****

- 

- 

- 

- 

- 
|   |   | [하위 기능] 출고 이력 관리 기능 시스템은 출고 과정에서 발생한 정보를 기록하고, 이를 조회 및 추적할 수 있어야 한다.[기능]시스템은 출고 이력을 저장할 수 있어야 한다.시스템은 출고 지시 ID를 기반으로 이력을 조회할 수 있어야 한다.시스템은 출고 제품, 수량, 시간 등의 정보를 기록할 수 있어야 한다.[비기능]시스템은 이력 데이터를 안정적으로 저장해야 한다.시스템은 사용자가 출고 이력을 조회할 수 있어야 한다. |   |
|   | 후처리 작업 및 청소 기능 (수작업 기반) | 시스템은 작업자가 수행하는 후처리 공정과 청소 작업을 지원하고, 공정 상태를 관리하며, 컨베이어 및 적재 시스템과 연동하여 작업 흐름을 제어할 수 있어야 한다. |   |
****

- 

- 

- 

- 

- 

- 

- 
|   |   | [하위 기능] 후처리 작업 및 청소 기능 작업자는 후처리 구역에서 제품 후처리 작업과 컨베이어 청소를 수행하며, 시스템은 해당 작업 상태를 관리할 수 있어야 한다.[기능] 시스템은 후처리 작업 상태를 관리할 수 있어야 한다.(before / processing / done)시스템은 컨베이어 벨트 청소 상태를 관리할 수 있어야 한다.(before / cleaning / done)시스템은 작업자가 후처리 작업을 수행할 수 있도록 작업 상태를 표시할 수 있어야 한다.시스템은 작업 완료 여부를 입력 또는 감지하여 상태를 갱신할 수 있어야 한다.[비기능]시스템은 후처리 작업 상태를 실시간 또는 준실시간으로 갱신해야 한다.시스템은 작업 상태를 직관적으로 인식할 수 있도록 UI를 제공해야 한다.시스템은 작업 과정에서 오류 또는 누락이 발생하지 않도록 상태 일관성을 유지해야 한다. |   |
****

- 

- 

  - 

  - 

- 

- 

- 
|   |   | [하위 기능] 컨베이어 연동 제어 기능 시스템은 후처리 공정 상태에 따라 컨베이어 벨트의 이동을 제어할 수 있어야 한다.[기능]시스템은 컨베이어 벨트를 한 칸 전진 또는 정지시킬 수 있어야 한다.시스템은 다음 조건이 모두 만족된 경우에만 벨트를 전진시킬 수 있어야 한다:현재 위치의 제품이 처리 완료되었을 것이전 공정이 완료 상태일 것시스템은 조건이 충족되지 않은 경우 벨트를 정지 상태로 유지해야 한다.[비기능]시스템은 컨베이어 제어 조건을 안정적으로 판단해야 한다.시스템은 작업 흐름이 끊기지 않도록 적절한 타이밍으로 벨트를 제어해야 한다. |   |
****

- 

- 

- 

- 

- 
|   |   | [하위 기능] 팔레트 적재 요청 기능 시스템은 후처리 완료된 제품을 팔레트에 적재하기 위해 적재 요청을 생성할 수 있어야 한다.[기능]시스템은 후처리 완료된 제품에 대해 팔레트 적재 요청을 생성할 수 있어야 한다.시스템은 양품 및 불량품을 각각 지정된 팔레트로 적재 요청할 수 있어야 한다.시스템은 적재 가능 여부를 확인하고 결과를 반환할 수 있어야 한다.[비기능]시스템은 후처리 완료 후 3초 이내에 적재 요청을 생성해야 한다.시스템은 적재 요청이 누락되지 않도록 보장해야 한다. |   |
|   |   |   |   |
|   |   |   |   |

#### 대시보드 (5144642)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5144642
**최종 수정**: v3 (2026-04-19 sync)

[https://dayelee313.atlassian.net/wiki/spaces/addinedute/whiteboard/5505054](https://dayelee313.atlassian.net/wiki/spaces/addinedute/whiteboard/5505054)
[주물 임시 대시보드](http://192.168.0.16:3000)
[https://www.figma.com/design/KKiKy1mCImYdFhoirpOzbd/Dashboard-Template-Kit--Community-?node-id=289-1621&p=f&t=7xmFpVmLdRoKTnye-0](https://www.figma.com/design/KKiKy1mCImYdFhoirpOzbd/Dashboard-Template-Kit--Community-?node-id=289-1621&p=f&t=7xmFpVmLdRoKTnye-0)

#### Jetcobot 작업 공간 (3276832)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3276832
**최종 수정**: v2 (2026-04-19 sync)

Mycobot280의 작업 공간 분석 자료입니다.

- 
스펙상 작업공간 vs 실제 작업 공간. 특히 공식 카탈로그에는 최대 작업공간만 나오고 로봇이 도달할 수 없는 dead space(더 좁혀질 수 없는 구간)에 대한 설명이 없어서 로봇팔 부품과 Base판 및 wire의 간섭을 최소화할 수 있는 구간을 임의로 피해서 작업공간을 정했습니다.

- 
하중은 280이라 나온 것은 Gripper포함 무게인지라 실제 그리퍼가 집을 수 있는 무게는 약 150g입니다.

#### MAP (9699349)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9699349
**최종 수정**: v2 (2026-04-19 sync)

#### Map_v2 (6848543)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6848543
**최종 수정**: v8 (2026-04-19 sync)

# 시나리오 1 

## 목적 
다품종 소량 생산에서 제품별 공정 시간 차이로 인해 발생하는 병목 현상 해결   

- 
가정:

  - 
다품종 소량 생산 공장  

  - 
사용할 수 있는 로봇들의 개수가 무한하다. 

- 
구체적인 시나리오: 

  - 
3가지 제품 발주 요청 이후, 생산 동시 시작 

  - 
주물 완성 과정에서 냉각 과정에서만 시간 차이를 줌 → 다른 과정은 걸리는 시간이 거의 동일하다고 가정하여 계산을 용이하게 함. 

  - 
주문 수량도 일단 동일하게 가져간다. 

****
****
****
****
****
****
****
| 시간 (min) | 주형 제작 | 주탕 | 냉각 | 탈형 | 후처리 (사람) | 주문 수량 |
|---|---|---|---|---|---|---|
| 제품 A | 3 | 2 | 30 | 5 | 15 | 100 |
| 제품 B | 3 | 2 | 120 | 5 | 15 | 100 |
| 제품 C | 3 | 2 | 240 | 5 | 15 | 100 |

- 
기존 layout 문제점: 

  - 
기존 layout은 다품종을 동시에 생산할때를 가정하지 않아 생산 라인을 달리하지 않음. 

  - 
공정 시간 차이가 큰데, 

    - 
모든 제품이 같은 경로를 공유 → 틀을 찍고 주형을 만드는 과정에서 복잡 → 하나의 제품당 다른 주조 구역 설정 

    - 
모든 제품이 같은 경로를 공유 → 느린 공정이 전체 흐름을 막음 → 병렬화 (parallelization) 

  - 
현재 Map에서는 AMR ID tag가 안되어 있어서 어떤 구역을 어떤 AMR이 담당하는지 모호 (나중에 시연때 생각)  

- 
최적화 방법:

  - 
작업 시간이 긴 제품 (느린 공정) → 병렬로 구성 

    - 
느린 공정은 병렬화 

  - 
제품 마다 주조 시간 상이 → Finishing zone 바로 옆에 buffer → Inspection 병목 현상 완화 

- 
Map: Casting (병렬) → Buffer → Finishing & Inspection (병렬) → Storage → Shipping

- 
설계 철학 

  - 
이동 최소화보다 병목 제거가 우선 

  - 
모든 공정을 빠르게 하는 것이 아니라 가장 느린 공정을 기준으로 시스템을 설계 

  - 
Buffer는 저장 공간이 아니라 흐름 제어 장치 

  - 
경로는 단순하게, 라우팅을 다이나믹하게! 

    - 
각 공정 간에는 routing을 적용하여, 가용한 라인으로 작업을 분산하도록 설계했습니다.

## 시나리오 디테일  - 시연 가능성 검토 
“발주부터 출고까지 하나의 End-to-End 자동화 사이클을 설계했습니다.”

1. 
발주: 원격 발주 → 관리자 발주 승인 → 관리자 생산 시작 알림 → 공정 시작 

1. 
전체 공정: 원재료 투입 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형 → 후처리 → 검사 → 적재 → 출고

  1. 
Casting Zone: 원재료 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형

    1. 
**제품 생산 시작 관리자의 signal → 용융 + 주형 제작 (병렬진행) **

      1. 
Ingot 을 컨테이너 (Ladle/도가니)에 넣기: 

        1. 
필요 로봇: 로봇팔1

        1. 
 로봇팔1: 원재료를 바닥에 있는 컨테이너 (ladle / crucile)  에 넣고 (컨테이너 수급은 불분명)→ 로봇팔1 컨테이너를 용광로에 넣기 → 용융 시작 

      1. 
**용융: 기다리면서 대기 **

    1. 
**주형 제작**:

      1. 
필요 로봇: 로봇팔2 

      1. 
로봇팔2: 

  1. 
Inspection Zone: 후처리 → 검사

    1. 
후처리 (사람) 

    1. 
검사 존에서 카메라 이미지로 검사 

      1. 
제품 종류 검사 (모델1) : 현재 생산되는 제품 class에 대한 classification (양품/불량품 전이므로, 그 둘다에 대한 classification 필요) 

      1. 
각 제품에 대한 양품/불량 검사 (모델2) : 

        1. 
디자인 검사: 첫 번째 모델에서 받은 class 정보 → 각 제품에 대한 양품/불량품 classifier 선택 → 양품/불량품 판정 

      1. 
규격 검사 (알고리즘1) : RGB-D camera로 depth map에서 depth map GT 와 비교 

  1. 
Storage Zone: 적재 

  1. 
Shipping Zone: 출고 

# 시나리오 2

## 목적 

- 
기존 시나리오 문제: 자원이 무한하다고 가정

- 
layout 상에서 정해진 자원 (로봇 개수)를 고려하여 map layout 작성 
가정: 

## 시나리오 디테일 - 시연 가능성 검토  

# Canva Link
[https://canva.link/j1x20wqwlz8co6h](https://canva.link/j1x20wqwlz8co6h)

#### Map_v3 (33947720)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/33947720
**최종 수정**: v12 (2026-04-20 sync)

#  

# Map with abbreviation

#### 관계자 인터뷰 (6258752)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6258752
**최종 수정**: v2 (2026-04-19 sync)

#### 주조 공정 실무자 인터뷰 (4849666)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/4849666
**최종 수정**: v1 (2026-04-19 sync)

[안정성, 위험작업]

### **어떤 부분에서 안전 상 위험한지?**

- 
용해로에 놓고 알루미늄 녹이고 굳히는 과정에서 액상에서 고체로 바뀌면서 수축할때 표면에 기공 발생, 잉곳을 보관할때 눈이나 비를 맞게 하거나 물 쏟거나 하면 알루미늄 기공 내부에 수분이 흡수되면 **물이 증기로 변하는 과정에서 부피가 커져 폭발사고가 발생**하여 작업자가 화상 발생할 가능성 높음, **예방하기 위해선 보관을 잘해야함**

- 
금형 내부에 작업물이 박힐 경우 기계를 끄고 사람이 들어가서 빼는 작업해야 하는데, 전원스위치 끄지 않고 작업하다가 기계 오작동 혹은 **다른 작업자의 실수로 금형이 닫힐때 사람이 압사함**

- 
제품 취출과정에서 **안전펜스 내부에 사람이 들어가면 작동하는 로봇으로 인해 사고 **발생함

- 
형압이 맞지 않을 경우 주조과정에서 고속 고압 주조시 금형 내부 알루미늄 비산이 되어 화상 입을수 있음
[물리적 측면]

### **작업자의 피로도 높은구간은 어디인가?**

- 
전부 높음 거의 다 기계가 자동화 잘되어있다 해도 **뭘 하든 힘든건 매한가지**
[물류 이동]

### **주조 이후 제품 이동과정?**

- 
**로봇팔이 끄집어내서 컨베이어에 올려놓음** 이동과정에서 **팬으로 냉각**시키고 **수작업으로 팔레트에 적재하거나 박스에 포장함**
[자동화 적용 공정]

### **자동화가 적용된 공정은 어디인가?**

- 
용해로에 잉것 투입 작업, 제품이 나와서 팔레트에 올려놓는것 제외한 거의 모든 작업이 기계로 대체됨

### **불량품은 다시 녹이는지?**

- 
다시 녹임

#### 주조 공장 관계자 인터뷰 (5899138)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5899138
**최종 수정**: v1 (2026-04-19 sync)

목표: 주물제작(주조 공정)의 자동화 시스템을 구현해 데모데이때 스마트 팩토리 전환 사업의 '가능성'을 보인다.
타깃: 다품종 소량생산하는 영세 주조 공장
배경: 3D업계인 탓에 인력난이 극심화되고있고 국가에서 스마트 팩토리 전환을 위한 지원이 이뤄지고있음
-> 위의 내용을 봤을때 가능성있는 사업아이템같음. 하지만 정확한 요구 분석이 필요함(공장 인터뷰,견학을 해볼것.당장은 도장 박람회가 송도에서 금요일까지 진행됨-혹시 핑크랩도 로봇만드니까 아는 공장이 있을까..?있다면 연결해 줄수있는지..)
-"주조 공정": 자동화가 필요한 부분은 트리밍(후처리)공정보다 주형 제작과 고온 주탕

- 
카메라로 불량품 검사를 한다면 형상 불량 검사+크고 미세한 기공이 '몇 개'있는지 파악하는 검사를 진행하는 수준은 되어야함(기공에 따른 불량품 기준은 공장의 클라이언트 마다 요구하는 정도가 다르기때문에 매번 다르게 적용됨)

- 
주물 제작 과정이 궁금하면 주물 공장 영상 참고(많음)

-가마솥 제작 [https://www.youtube.com/watch?v=6XuadzAIH-s](https://www.youtube.com/watch?v=6XuadzAIH-s) 
-주물팬 제작 [https://www.youtube.com/watch?v=aWKzJjDYV0A](https://www.youtube.com/watch?v=aWKzJjDYV0A) 
-자동차 부품 공장 영상(자동차는 수요가 많아서 자동화가 되어있음)
[https://www.youtube.com/watch?v=LzRLM1jHNpc](https://www.youtube.com/watch?v=LzRLM1jHNpc) 

- 
보통의 영세 공장들은 10명 정도의 소규모 공장임. 주문수량이 많지 않기때문에 모래로 틀을 제작함. 모래를 채우고 다지는 과정이 사람이 하기에 어려움.

- 
고온 주탕은 쇳물을 어떻게 부을것인지(각도,속도-숙련자의 기술을 알고리즘으로 로봇에 학습 시키는 과정이 필요함-실제 공장에 적용한다면..)

-아니면 차라리 도장 공정은 어떤가..이건 구현하기 단순하다. 스프레이만 뿌리면 된다. 도장 공정도 자동화된 곳이 많지만 영세 공장은 여전히 사람이 하는중..

- 
주물을 제작하는 제작물??은 굉장히 다양하다.조선,방산업계의 기어,,케이스(껍데기..?)도 다 주물 제작에 속함. 크고 작은 정말 다양한 제품이 많음

#### 시연 시나리오 (17629251)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/17629251
**최종 수정**: v18 (2026-04-19 sync)

## 시연 시나리오 구상

### 최종 시연 목표

- 
+파트별로(한 파트에 로봇 몰아서 시연)+예외 처리 상황\

- 
우선 순위 

  1. 
파트별 구현 먼저

  1. 
예외처리 상황 시연

  1. 
시간 여유 있으면 원테이크 버전 구현

## **시나리오 PART 1: 주조+이송+검사 **

- 
전체 과정

  - 
주형 제작-주탕-탈형-상차-이송-후처리-검사

- 
특이사항

  - 

    - 
기존 쇠컵을 3D 프린팅으로 교체하고 중탕기 꺼놓은 상태에서 녹인 양초를 인위로 보충하여 진행

  - 
탈형이후로는** **3D프린팅으로 대체

  - 
(주조와 적재,후처리에 사용 x)

  - 
슬롯 적재함은 항상 AMR 위에 장착된 상태

  - 
이송함을 전제로 함

- 
시나리오

  - 
로봇팔 / AMR / 사람 / 센서 & AI 모델 

  - 
주형 제작 → 1개 분량 주탕 → 탈형  → 상차 →  이송 → 후처리 (사람이 AMR 에서 맨홀 1개 내림) → 사람이 1개씩 컨베이어 위에 올림 →  검사 진행 ( 컨베이어 위에 여러개 있어도 되지만 검사는 1개씩 진행) → 이 받음 →

  - 
상황 : 맨홀A 5개와 맨홀B 8개를 제작해야한다.

****
****
****
****
****
| 순번 | 공정 단계 | 주체 (Actor) | 상세 동작 | 비고 |
|---|---|---|---|---|
****
| 1 | 주문 들어옴 | Interface → Control service | 주문을 로봇팔 A,B에 할당 |   |
****
****
****
| 2 | 주형 | 로봇팔1,2 | 주문에 해당하는 패턴을 찍어서 주형을 제작 |   |
****
****
****
| 3 | 주탕 | 로봇팔1,2 | 주형에 준비된 양초를 붓는다 | 양초 보충은 수동(컷편집) |
****
****
****
| 4 | 탈형 | 로봇팔1,2 | 맨홀을 집어 탈형 | 3D 모형 사용 |
****
****
****
| 5 | 상차 | 로봇팔1,2 | 탈형한 맨홀을 AMR 위 슬롯함에 상차 |   |
****
****
****
| 6 | 1차 이송 | AMR 1,2,3 | 상차 완료 신호 수신 후 후처리 구역으로 이동 |   |
****
****
****
| 7 | 후처리 하차 | 사람 | 도착한 AMR에서 맨홀 1개를 수동으로 내림 |   |
****
****
****
| 8 | 검사 투입 | 사람 | 맨홀을 컨베이어 벨트 위에 투입 | 컨베이어 구동 시작 |
****
****
****
| 9 | 비전 검사 | 비전 시스템 | 양품/불량품 검사 진행 |   |
****
****
****
| 10 | 검사 완료 | 컨베이어 | 검사가 끝난 맨홀을 끝단으로 이송 | AMR은 하단에서 대기 상태 |
****
****
****
| 11 | 자동 수거 | AMR 1,2,3 | 컨베이어에서 떨어지는 맨홀을 적재함으로 받음 |   |
****
****
****
| 12 | 최종 이송 | AMR 1,2,3 | 수거된 맨홀을 싣고 적재구역으로 이동 |   |

- 
맵 구성

  - 
로봇팔 2대

  - 
AMR 3대

  - 

## 

시나리오 PART2: **적재 +출고 시나리오**

- 
전체 과정

  - 
이송 → 적재 / 출고 → 이송

- 
특이 사항

  - 
보관 랙에 양품 구역과 불량품 구역이 나눠져 있다.

  - 
모든 공정은 1회 진행시 1개만 이송,적재,출고함을 전제로 함

### 적재 상황

- 
로봇팔 / AMR

- 
적재
으로 이송 → 로봇 팔이 이송된 맨홀을 꺼내 할당 받은 위치에 적재함

- 
출고  
로봇 팔이 할당 받은 위치에서 맨홀을 꺼냄 → AMR 위에 상차 → 출고 구역으로 이송

- 
상황1 :  검사완료된 맨홀A 3개,맨홀B 2개를 적재한다
맨홀A,B 적재는 동시에 이뤄짐. 꼭 AMR1-로봇팔1이 매칭되는것은 아님

****
****
****
****
****
| 순번 | 공정 단계 | 주체 (Actor) | 상세 동작 | 비고 |
|---|---|---|---|---|
****
****
****
| 0 | 적재구역 이송 지시 | 관제 | 관제가 AMR1에게 적재구역으로 이동하라고 지시함 |   |
****
****
****
| 1 | 이송 | AMR1 | AMR1이 검사완료된 맨홀A를 가지고 적재 구역 도착 |   |
****
****
****
| 2 | 적재 지시 | 관제 | AMR1 도착을 확인하고 로봇팔1에게 맨홀A 1개 적재 지시함 |   |
****
****
****
| 3 | 하차 | 로봇팔1 | 로봇팔1이 상차된 맨홀을 꺼냄 |   |
****
****
****
| 4 | 적재 | 로봇팔1 | 로봇팔1이 할당받은 위치에 맨홀A를 적재함 | 3번 반복 |
****
****
****
| 5 | 이송 | AMR2 | AMR2이 검사완료된 맨홀B를 가지고 적재 구역 도착 |   |
****
****
****
| 6 | 적재 지시 | 관제 | AMR2 도착을 확인하고 로봇팔2에게 맨홀B 1개 적재 지시함 |   |
****
****
****
| 7 | 하차 | 로봇팔2 | 로봇팔2이 상차된 맨홀을 꺼냄 |   |
****
****
****
| 8 | 적재 | 로봇팔2 | 로봇팔2이 할당받은 위치에 맨홀B를 적재함 | 2번 반복 |

### 출고 상황
:  맨홀A 3개,맨홀B 2개 출고 요청이 들어왔다.
맨홀A,B 출고는 동시에 이뤄짐. 꼭 AMR1-로봇팔1이 매칭되는것은 아님

****
****
****
****
****
| 순번 | 공정 단계 | 주체 (Actor) | 상세 동작 | 비고 |
|---|---|---|---|---|
****
****
| 0 | 출고구역 이송 지시 | 관제 | 관제가 AMR1에게 출고구역으로 이동하라고 지시함 |   |
****
****
****
| 1 |   |   | AMR1이 출고 구역 도착 |   |
****
****
****
| 2 | 출고 지시 | 관제 | AMR1 도착을 확인하고 로봇팔1에게 맨홀A 1개 출고 지시함 |   |
****
****
****
| 3 | 출고 | 로봇팔1 | 로봇팔1이 할당받은 위치에서 맨홀A를 꺼냄 |   |
****
****
****
| 4 | 상차 | 로봇팔1 | 로봇팔1이 AMR1에 맨홀A를 상차 |   |
****
****
****
| 5 | 이송 | AMR1 | AMR1이 맨홀A를 가지고 이송 | 3번 반복 |
****
****
****
| 6 | 상차 준비 | AMR2 | AMR2이 출고 구역 도착 |   |
****
****
****
| 7 | 출고 지시 | 관제 | AMR2 도착을 확인하고 로봇팔2에게 맨홀B 1개 출고 지시함 |   |
****
****
****
| 8 | 출고 | 로봇팔2 | 로봇팔2이 할당받은 위치에서 맨홀B를 꺼냄 |   |
****
****
****
| 9 | 상차 | 로봇팔2 | 로봇팔2이 AMR2에 맨홀B를 상차 |   |
****
****
****
| 10 | 이송 | AMR2 | AMR2이 맨홀B를 가지고 이송 | 2번 반복 |
적재와 출고가 동시에 일어나는 상황은 없는지한대는 적재,그다음에 오는 애는 출고….

**시나리오 PART 2: 적재 + 출고 (통합 버전)**

****
****
****
****
****
| 순번 | 공정 단계 | 주체 (Actor) | 상세 동작 | 비고 |
|---|---|---|---|---|
****
****
****
| 1 | 적재 지시 | 관제 | AMR1에게 적재구역 이송 지시 및 로봇팔에게 적재 좌표 전송 | 작업 예약 상태 |
****
****
****
| 2 | 이송 및 도착 | AMR1 | 검사 완료된 맨홀을 싣고 적재 구역 도착 | AMR: 도착 완료 |
****
****
****
| 3 | 하차 및 적재 | 로봇팔 | AMR에서 맨홀 파지지정된 랙 좌표에 적재 | 로봇: 작업 중 |
****
****
****
``
| 4 | 적재 완료 | 로봇팔 | 제품 안착 후 즉시 Idle 상태로 복귀 | 로봇: 대기 상태 |
****
****
****
| 5 | 출고 지시 | 관제 | AMR2에게 출고구역 이송 지시 및 로봇팔에게 출고 대상 좌표 전송 | 작업 예약 상태 |
****
****
****
| 6 | 이송 및 대기 | AMR2 | 빈 슬롯 상태로 출고 구역 도착 후 상차 대기 | AMR: 상차 대기 |
****
****
****
| 7 | 추출 및 상차 | 로봇팔 | 랙에서 대상 제품 파지 AMR2 슬롯에 제품 상차 | 로봇: 작업 중 |
****
****
****
``
| 8 | 출고 완료 | 로봇팔 | 상차 완료 후 즉시 Idle 상태로 복귀 | 로봇: 대기 상태 |

|   |
|---|
|   |

## **시나리오 PART 3: 예외상황 처리 시나리오 - 이송**

- 
전체 과정

  1. 
AMR 이동 → 예외 상황 발생 → 관제 호출 → 재할당 → 문제 해결

- 
특이 사항

  1. 
보관 랙에는 양품을 보관하고 

  1. 
모든 공정은 1회 진행시 1개만 이송,적재,출고함을 전제로 함

- 
시나리오

  - 
상차 요청을 받고, 이동 중이던 AMR1의 배터리가 일정 수준 이하로 떨어짐(상차한 맨홀 없는 상태) → 관제가 이를 감지함 → AMR2에게 상차 작업을 재할당 → AMR1은 charging zone으로 이동, AMR2가 해당 task를 넘겨받아 수행 

  - 
상황 : 상차 요청을 받고, 이동 중이던 AMR1의 배터리가 일정 수준 이하로 떨어짐

****
****
****
****
****
| 순번 | 공정 단계 | 주체 (Actor) | 상세 동작 | 비고 |
|---|---|---|---|---|
****
****
****
| 1 | 출발 위치로 이동 | AMR1 | AMR1이 상차 지시를 받고 상차 구역으로 이동 | 작업중 상태 |
****
****
****

| 2 | 예외 상황 발생 | 관제 | 관제가 AMR1의 배터리 잔량 저하(30%)를 감지함 | 작업중 상태 → 충전 필요 상태 |
****
****
****
****
| 3 | 에러 확인&재할당 | 관제 | AMR2에게 상차 작업을 재할당 |   |
****
****
****
| 4 | 충전 위치로 이동 | AMR1 | AMR1은 충전 구역으로 이동 |   |
****
****
****
| 5 | 출발 위치로 이동 | AMR2 | AMR2는 상차 구역으로 이동 |   |

## 의논

1. 
제작한 맨홀을 실은 AMR이 후처리 하차 지점에 도착한 후에, 

1. 
후처리가 끝난 후 컨베이어 벨트에 올릴 때, 해당 주물의 item_id가 몇인지 신호를 보낸 후 올려줘야 함.

#### 시나리오3 예외 처리 시스템 (30965829)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30965829
**최종 수정**: v2 (2026-04-19 sync)

## [AMR 이송 중 배터리 부족 및 재할당]

### 1. 시나리오 개요

- 
**상황:** 상차 요청을 받고 이동 중인 AMR1의 배터리가 **30% 이하(Critical)**로 하락.

- 
**목표:** 관제 시스템이 이를 실시간 감지하여 미수행된 작업을 가용 로봇에게 재할당하고, 에너지 부족 로봇을 안전하게 충전소로 복귀시킴.

- 
**전제 조건:** 모든 이송은 1회 1개 원칙, 상차 전(Empty-load) 상태, 총 3대의 AMR 운용.

### 2. 단계별 프로세스 (Workflow)

1. 
**[감지]** **State Manager**가 AMR1으로부터 배터리 잔량(29% 등)을 수신하고 즉시 Critical 알람을 발생시킴.

1. 
**[중단]** **Task Manager**가 AMR1에 할당된 '상차 이동' 명령을 즉시 중단하고, AMR1의 상태를 '가용 불가'로 전환.

1. 
**[재할당]** 

  1. 
**1순위:** 유휴(IDLE) 상태인 로봇(예: AMR2)에게 즉시 작업 할당.

  1. 
**2순위:** 유휴 로봇이 없으면 **Job Queue**에 작업을 대기시킨 후, 현재 작업을 가장 먼저 끝내는 로봇에게 할당.

1. 
**[복귀 및 투입]** 

  1. 
**AMR1:** 가장 가까운 Charging Zone으로 복귀 경로 생성.

  1. 
**재할당 로봇:** 원래의 상차지로 이동하는 경로 생성.

1. 
**[교통 관제]** 

  1. 
**Traffic Manager**가 두 로봇의 경로 간섭을 확인. 복귀 중인 AMR1에게 우선권을 부여하거나 우회 경로를 지정하여 데드락(Deadlock) 방지.

### 통합 시나리오 (데이터 + 관제 + 이동)

****
****
****
****
| 단계 | 상황 및 관제 로직 (Control Logic) | AMR 물리적 이동 (Movement) | 데이터베이스/메시지 변화 (Data) |
|---|---|---|---|

1. 
****
****
****
``
``
``
| 정상 수행 | Task Manager: AMR1에게 맨홀 상차지(A구역) 이동 명령 하달. | AMR1: 정해진 경로를 따라 상차지로 주행 중. | AMR1_Stat: DrivingAMR1_task: 'Moving_to_Load'AMR1_Bat: 35% → 31% |

1. 
****
****
``
``

``
****
| 예외 감지 | State Manager: 배터리 30% 이하 감지. |   | AMR1_Stat: EmergencyAMR1_Bat: 29% (Critical), Event: State Manager Low_Battery_Alarm |

1. 
****
****
****
``
``
| 작업 중단 | Task Manager즉시 AMR1에 '작업 중단' 및 '긴급 복귀' 명령 발행. | AMR1: 즉시 정지 후 가장 가까운 Charging Zone으로 경로 재계산. | AMR1_task: NullAMR1_Stat 'Emergency_Return |

1. 
****
****
| 타겟 검색 | Task Manager:운영 중인 AMR 3대 상태 전수 조사 (AMR2: IDLE 확인) |   |   |

1. 
****
****
****
``
``
``
| 작업 재할당 | Task Manager: 미수행된 '상차 작업'의 주체를 유휴 로봇인 AMR2로 변경. | AMR2: IDLE 상태에서 즉시 '상차지(A구역)'로 이동 시작. | Task_Log: Assigned_Robot (1→2)AMR2_Stat: DrivingAMR2_task: 'Moving_to_Load' |

1. 
****
****
****
``
``
| 교통 제어 | Traffic Manager: AMR1(복귀)과 AMR2(투입)의 경로 교차점 발견. AMR1에게 우선 통행권 부여.(미정) | AMR2: 교차 지점 직전 노드에서 일시 정지 후 AMR1 통과 대기. | Node_Lock: Node_25 (Locked by AMR1)Traffic_Status: Waiting(AMR2) |

1. 
****
****

****
****
``
``
``
| 미션 완료 | State Manager: 각 로봇의 목적지 도착 확인.DB 업데이트? | AMR1: 충전 시작.AMR2: 상차지 도착 후 상차 작업 시작. | AMR1_Stat: ChargingAMR2_Stat: LoadingTask_Log : "AMR1 배터리 부족으로 인한 AMR2 재할당 완료" |

### 관제 시스템 내부  (Pseudo-Logic)

1. 
**Status Monitoring (Loop):**

  - 
모든 AMR로부터 `JSON` 패킷 수신 (`id`, `battery`, `pose`, `state`)

  - 
`if battery <= 30 && state != 'Charging'`: **Emergency_Handler** 호출

1. 
**Emergency_Handler:**

  - 
`Cancel_Current_Path(amr_id)`: 현재 경로 삭제

  - 
`Get_Closest_Charger(amr_id)`: 최단거리 충전소 계산 및 경로 하달

  - 
`Trigger_Reallocation(task_id)`: 중단된 작업을 재할당 큐로 전송

1. 
**Task Re-allocator:**

  - 
`target = Find_Robot(state == 'IDLE')`

  - 
`if target == None`: `Job_Queue.push(task_id)`

  - 
`else`: `Assign_Task(target, task_id)`

1. 
**Traffic Manager (Conflict Check):**

  - 
`if Path_Overlap(AMR1, AMR2)`:

  - 
`Compare_Priority(AMR1.task, AMR2.task)` -> 배터리 복귀(AMR1)가 상차 이동(AMR2)보다 우선순위 높음 판정

  - 
`Send_Wait_Command(AMR2)`

### **Task_History 테이블**

- 
`task_id`: 1001

- 
`original_robot`: AMR1

- 
`final_robot`: AMR2

- 
`status`: SUCCESS (Reassigned)

- 
`remark`: "AMR1 Low Battery(29%) - Reallocated to AMR2"

### 필요한 데이터

#### 1. 로봇 상태 데이터 (AMR Status)
실시간으로 변하며 관제 시스템의 `State Manager`가 구독(Subscribe)할 데이터

- 
**Robot ID:** `AMR_1`, `AMR_2`, `AMR_3`

- 
**Battery Level:** 100%에서 시작해 이동 거리에 따라 감소 (구현 시 초당 0.5%씩 감소하게 설정하여 30% 도달 상황 연출)

- 
**Pose (Location):** 실시간 좌표 `(x, y, theta)` 또는 현재 위치한 노드 번호

- 
**Status:** `IDLE`(대기), `DRIVING`(이동 중), `EMERGENCY`(배터리 부족 등 예외), `CHARGING`(충전 중)

- 
**Velocity:** 현재 이동 속도 (경로 점유 및 도착 시간 계산용)

#### 2. 작업 관리 데이터 (Task Data)
`Task Manager`가 관리하고 DB에 기록할 데이터

- 
**Task ID:** 작업을 식별하는 고유 번호

- 
**Assignment:** 현재 이 작업을 맡은 `Robot ID` (재할당 시 이 값이 변경됨)

- 
**Task Type:** `LOAD`(상차), `UNLOAD`(하차), `MOVE`(이동)

- 
**Priority:** 작업 우선순위 (재할당 시 큐에서 순서를 정하는 기준)

- 
**Status:** `PENDING`(대기), `IN_PROGRESS`(진행 중), `REASSIGNED`(재할당됨), `COMPLETED`(완료)

#### 3. 환경 및 트래픽 데이터 (Environment & Traffic)
`Traffic Manager`가 경로 점유를 판단하기 위한 데이터

- 
**Node/Edge Occupancy:** 특정 경로를 어떤 로봇이 점유하고 있는지 (`is_occupied: True/False`)
Q. 배터리 임계치를 두 단계로 나누어 관리할 것인가

- 
Warning (예: 20%): 현재 수행 중인 task까지만 마치고 충전소로 이동.

- 
Critical (예: 10%): 즉시 task를 중단하고 재할당 후 충전소 이동.
 
Q. AMR이 모두 사용중일때 재할당을 어떻게 할 것인가
-1순위 유휴중인 로봇
-2순위 일이 빨리 끝나는 로봇[유휴중인 로봇이 없을때]
그러면 일이 얼마나 진행중인가도 다 모니터링해야됨
-3순위 가장 가까운 로봇
-모든 로봇이 바쁘다면 대기열에 추가하고 대기
-1,2,3 순위는 가중치를 부여하여 계산
 Q.경로 재할당 우선 순위는 어떻게 정할 것인가

- 
배터리 충전 급한거

- 
작업 먼저

- 
…..
IF 생산 구역에서  상차 직후 배터리가 부족해진다면?

- 
이상황까지 고려할 필요는 없긴함

- 
대신 가상데이터 작성시 조건 넣고 구현해야됨
Q. AMR1,2,3이 이동하면서 경로 점유당하는 상황은 어디서 보여줄거임 모든 시나리오에서 그냥 자연스럽게 흘러가도 발생함?

#### 02_Domain_Research (3342354)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3342354
**최종 수정**: v6 (2026-04-19 sync)

## 조사 / 설계 근거 결과물

|   | domain 전체에 대한 간략한 개요 |
|---|---|
|   | 주조 공정에 대한 조사 결과 및 기술조사보고서 |
|   | 물류 흐름에 대한 조사 결과 및 기술조사보고서 |
|   | 용어 표준화 |

#### Jetcobot 그리퍼 사진(용해로 작업용) (5866067)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5866067
**최종 수정**: v3 (2026-04-19 sync)

해당 용해로의 손잡이 두께는 약 10mm. 그러나 그리퍼의 Stroke 범위: [20-45mm](https://www.elephantrobotics.com/en/mycobot-accessories-grippers-en/) 
용해로와 로봇 그리퍼 사이에 활용할 수 있는 Adapter 필요유무? 3D printer? 검토 요망.

#### 자료 (6225927)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6225927
**최종 수정**: v1 (2026-04-19 sync)

#### 공정 조사 (3276953)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3276953
**최종 수정**: v7 (2026-04-19 sync)

- 
공정 프로세스 초안 -  시연한 영상 기반으로.

  - 
1. Core pressing: 코어로 모래에 주형을 만듬. Jetcobot1 이 코어를 집은 뒤 찍어서 만듬.

  - 
2. Pouring(주탕): 용광로(Furnace)에 있는 용탕을 Jetcobot 1이 찍어낸 주형에 투입.

  - 
3. Finishing on front side(주물 전면부 후처리): 냉각된 주물을 탈형시킨 뒤 Jetcobot1이 들어서 고정시키고, 반대편의 Jetcobot2가 청소도구로 이물질 및 찌꺼기를 제거. 

  - 
4. Finishing on rear side(주물 후면부 후처리): 주물의 반대면으로 뒤집은 뒤, 아까의 후처리과정을 통해 반대면 세척.

  - 
5. Inspection: Jetcobot2가 세척된 주물을 컨베이어 벨트에 올린 뒤, 카메라가 검사를 통해 양품/불량품 검증.

  - 
6. Product pass(양품 처리): Pinky bot(AMR)이 양품을 컨베이어 벨트에서 받은 뒤, 이를 Jetcobot1에 전달하면 Jetcobot1은 이를 Tray에 보관.

  - 
7. Product Fail(불량품 처리): Pinky bot(AMR)이 불량품을 컨베이어 벨트에서 받은 뒤, 이를 Jetcobot1에 전달하면 Jetcobot1은 이를 재활용하기 위해 Furnace에 재투입. 

- 
주력 회사: Big vs Small company

  - 
영세 회사가 주목적 → 주조 작업에서의 자동화가 긴급(1순위: 주탕, 2순위: 물류 이동. 3순위: 단순 반복 작업)

  - 
주탕 작업의 자동화: Robotic arm-based pouring system(로봇팔 기반의 주탕 시스템) vs Automated tilting ladle(자동화된 틸팅 래들)

    - 
Robotic arm-based pouring system: 가장 현실적. 현재 Jetcobot 으로도 비슷하게 모사가능. [KUKA 의 주탕작업 자동화 사례가 존재. ](https://www.youtube.com/watch?v=r3EYPbte4P4)

    - 
Automated tilting machine: 로봇팔 대신 거대한 용광로 같은 컨테이너를 축을 중심으로 기울여서 주탕작업을 수행하는 방식. 그러나 컨베이어 벨트 같이 교실이나 랩에서 구현가능하며 저렴하게 구매할 수 있는 자동화된 틸팅 머신이 존재하지 않음. [참고 문헌](https://www.researchgate.net/figure/Tilting-ladle-type-automatic-pouring-machine-in-laboratory_fig2_349744845) , [참고문헌1](https://onlinelibrary.wiley.com/doi/full/10.1002/cite.202000225) 사례에서 보듯이 랩 기반으로 프로토타입을 만들 경우 추가 장비를 더해 자동화머신 구축해야 함. 현행 장비상 다소 비현실적.

- 
총괄된 주조 프로세스 

-

#### 주조공정 자동화 프로젝트 구현 범위 및 자동화 우선순위 (3964952)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3964952
**최종 수정**: v10 (2026-04-19 sync)

1. 
**전체흐름 및 세부사항**
원재료준비 → 원재료 이송 → 원재료 용해 → 주형 제작 → 주탕 → 탈형 → 이물질 제거 → 검사 → 판별 후 목적지로 이송
원재료 준비 - 설정된 중량의 양초 조각을(코어 하나 만들정도) 준비                미정
원재료 이송 - 계량된 양초 조각을 도가니로 이송                                            미정
원재료 용해 - 도가니를 가열하여 내부에 있는 양초조각 용해                          중탕기
주형 제작 - 모래판위에 패턴으로 압력을 가하여 주형 제작                           Jetcobot
주탕 - 도가니에 담겨있는 용해된 양초를 주형으로 주탕                               Jetcobot
탈형 -  융고된 코어를 주형으로부터 탈형                                                    Jetcobot
이물질 제거 - 브러쉬를 이용해 제작된 코어의 이물질 제거                           Jetcobot
검사 - 컨베이어 벨트를 통해 이송되는 코어를 양품/불량품 판별              Camera, Computer
판별 후 목적지로 이송

#### 자료조사 (6225938)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6225938
**최종 수정**: v2 (2026-04-19 sync)

#### 04_Implementation (3703084)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3703084
**최종 수정**: v6 (2026-04-19 sync)

## 코드 / 실험 결과

****
|   | VLA 관련 모델조사, 실험 결과, 적용 방법 |
|---|---|
|   | LLM 관련 모델조사, prompt 설계, 사용 시나리오, 테스트 결과 |
|   | 실제 구현 결과 ( 코드 실행 결과, demo 영상, 테스트 성공 결과 )  ex. YOLO 실험 코드, 로봇팔 demo, 센서 테스트.. |
|   | DB 설계 |
|   | 사용자 인터페이스 설계 |

#### 05_Meetings_and_Logs (3407968)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407968
**최종 수정**: v4 (2026-04-19 sync)

## 기록물 관리

****
|   | 회의록 |
|---|---|
|   | 데일리 스크럼 |
|   | 개인 작업 기록 ex. yolo 실험 결과, 문제 해결 과정 |
|   | 피드백 / 강사 의견 |

#### Meeting_Notes (3407983)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3407983
**최종 수정**: v5 (2026-04-19 sync)

###

#### 주제 선정 (3277035)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3277035
**최종 수정**: v1 (2026-04-19 sync)

#### TODO (6258900)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6258900
**최종 수정**: v1 (2026-04-19 sync)

UI (깃헙에 존재) → DB (다예, 진성) → Techinical Research (이번 주 목요일 완성 목표) 

- 
정연, 다예 (SR, MAP) 내일까지 → 오늘밤까지!

  - 

- 
이번주 목요일 자정까지 Technical Research (팀장에게) 보고 완료 

- 
DB는 수요일까지 

  - 
UI깃헙 & SR 같이 보면서 → 수정 

  - 
 ERD 만들기 

    - 
(진성) table 하고 계시면 

    - 
(다예) 끝내고 테이블 정리 및 연결 

- 
LLM, VLA (다예, 진성): 화요일 저녁 ~ 목요일 (금요일~주말) 

  - 
데이터셋 양식, comparative study (우리 HW 사양에 맞는 모델 및 

  - 
할 수 있는 테스크가 뭔지 정리 

  - 
fine-tuning dataset 만드는 방법 

  - 
우리 시스템에 적용가능하지 여부 

- 
적재팀 (금요일 자정 예외)

-

#### 3월 (3113223)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3113223
**최종 수정**: v2 (2026-04-19 sync)

#### 4월 (8650965)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8650965
**최종 수정**: v4 (2026-04-19 sync)

#### 0401~0415 (30507091)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30507091
**최종 수정**: v1 (2026-04-19 sync)

#### Work_Logs (3309630)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3309630
**최종 수정**: v2 (2026-04-19 sync)

#### Mentoring_Logs (3145788)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3145788
**최종 수정**: v3 (2026-04-19 sync)

[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/4980960/?draftShareId=7b5c5e97-8e87-44cb-ae04-78331ae1d426](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/4980960/?draftShareId=7b5c5e97-8e87-44cb-ae04-78331ae1d426)

#### Agile & Scrum & Jira (13926473)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13926473
**최종 수정**: v5 (2026-04-19 sync)

(~4/10) 컴포넌트 파일 만들고 → 1차 연동 까지 계획 하길 바람 

# Agile 하게 일하기 
Sprint로 나눠서 단계적으로 완성!

- 
sprint 는 시간이다. 즉, 시간이므로 sprint는 딜레이할 수 없다. 완성을 다 못했으면 그렇게 끝낸것이다. 

# Scrum

- 
Project Vision - 프로젝트 최종 목표 정의 

- 
Project Roadmap  - 주요 단계를 시각화(Timeline)

- 
Project Backlog - 작업목록 (기능, 작업, 개선사항, 버그수정 등)

  - 
누구나 만들 수 있음

  - 
생각났을 때 오류 등을 여기에 저장 

- 
Release Planning - 출시 계획 (일정 조정 및 백로그 우선순위)

  - 
스프린트 일정과 반드시 일치하지 않음 

  - 
계획은 없지만 

- 
Sprint Planning - 스프린트 시작 시점 회의, 작업 우선순위를 정하고 역할 분담 등을 계획

  - 
전체 sprint 일정은 이미 짜있는데, 각 스프린트 안에서 할 계획 작성 

- 
Sprint Backlog - 스프린트 동안 수행할 작업 목록 (스프린트 목적을 이해하고 효율적으로 관리)

  - 
다음주 스프린트는 아직 계획이 안 정해져있음. 

  - 
언제쯤 이거 해야겠다는 sprint backlog 에 넣어짐.  (project backlog는 그냥 프로젝트 안이고, 언제쯤 예상이되면 sprint backlog에 넣으면 됨) 

- 
Sprint - 1~4주동안의 개발 주기. 끝날때마다 작동 가능한 소프트웨어가 릴리즈 되어야 한다.

  - 
산출물 필요 

  - 
위의 release는 배포 

  - 
보통 1~2주안으로 개발 주기를 잡는다. 

- 
Daily Scrum - 15분 이내의 짧은 미팅. 어제했던 작업 + 오늘할 작업 + 작업에 방해가 되는 문제 공유 등

  - 
길어지면 안됨.

  - 
논의가 필요한 부분은 스크럼 회의가 끝나고 필요한 인원끼리만 할 것.

- 
Increment - 작동 가능한 스프린트 결과물

  - 
데모 필요 

- 
Review - 스프린트 완료 시점 회의. 스프린트 작업을 검토하고 데모를 진행

  - 
반성 

  - 
원래 해려고 했던 기능 중 2개만 하고 몇 개는 못하고 끝난 경우 회고를 하면서, 다음 번에는 문제 해결을 위해 필요한 것을 논의 

- 
Retrospective - 스프린트 동안의 작업방식과 프로세스 평가(회고). 잘된 점과 개선이 필요한 점을 논의

  - 
ex) 이슈를 정확하게 적지 않아서. 서로 다른 생각을 가짐 → 원래 A라는 작업을 해야하는데 B라는 작업을 했다 → 다음엔 이슈를 정확하게 적어야겠다.

# Jira 

- 
space 단위로 작업 함. 

- 
create spce → software development (template 이 뜬다)

  - 
Kanban: 짧은 프로젝트에서 뺑글뺑글 돌듯이, 할일이 쌓여있으면 처리하는 상태. 연습용으로 사용 

  - 
Scrum: 아래 이미지 

  - 
다른 것: 우리 회사의 규칙에 맞게 custom 하겠다. (Top-level planning, Cross-team planning..) 

- 
이슈 타입

  - 
Task: 구체적으로 뭘 해야하는지 알고 있을 때, Task로 적음

    - 
하위에 Sub task 존재

  - 
Bug: 오류 났던 일들

  - 
Story: Task로 쓰기에는 너무 두루뭉술할 때, Story로 적음

  - 
Epic: 이슈를 관리하기 위한 그룹

    - 
1. 컴포넌트 별로 묶는 방법

    - 
2. 기술별로 묶는 방법

    - 
3. 프로세스별로 묶는 방법

    - 
4. 적절하게 알아서 그룹화…

- 
스프린트 회의

  - 
회의는 30분 이내로 진행.

  - 
그러기 위해 회의 준비를 해와야됨.

#### 06_Deliverables (3113021)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3113021
**최종 수정**: v7 (2026-04-19 sync)

## 제출 / 발표하는 최종 결과물

****
|   | 발표 자료 |
|---|---|
|   | 시연 영상 |
|   | 최종 보고서 |
|   | 스프린트 일지 |

## 주차별 계획 및 산출물

****
****
****
| 주차 | 진행내용 | 산출물 |
|---|---|---|

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
| 2주차 | 개발환경 세팅Jira,Confluence,GitHub세팅프로젝트 기획주제 선정 및 사용자 요구사항 정리프로젝트 설계System requirementsSystem architecture기술조사기술조사 항목 수집 및 선정 | System requirements수행일지(스프린트 회의록,설계검토) |

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
| 3주차 | 프로젝트 설계데이터,시나리오,GUI 설계프로젝트 코드 구조팀 규칙 수립(코딩 컨벤션)프로젝트 개발 계획스프린트 별 목표 및 이슈정의기술조사딥러닝 모델 선정 및 학습데이터 수집 | 프로젝트 설계문서프로젝트 개발 계획서GitHub Repository 구성팀 규칙서기술조사 보고서수행일지(스프린트 회의록,설계검토) |

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
| 4주차 | 프로젝트 설계인터페이스 설계프로젝트 구현코드 베이스 구성DB 구축 완료GUI 디자인 구현 완료기술조사딥러닝 학습 및 테스트 완료검증1차 연동 테스트 | 프로젝트 설계 문서프로젝트 코드 리뷰: v0.1기술조사 보고서수행일지(스프린트 회의록,1차 연동 테스트 보고서) |

- 

  - 

- 

  - 

- 

- 
| 5주차 | 프로젝트 구현전체 기능의 30%검증2차 연동 테스트 | 프로젝트 코드 리뷰: v0.2수행일지(스프린트 회의록,2차 연동 테스트 보고서) |

- 

  - 

- 

  - 

- 

- 
| 6주차 | 프로젝트 구현전체 기능의 60%검증3차 연동 테스트 | 프로젝트 코드 리뷰: v0.3수행일지(스프린트 회의록,3차 연동 테스트 보고서) |

- 

  - 

- 

  - 

- 

- 
| 7주차 | 프로젝트 구현전체 기능의 80%검증4차 연동 테스트 | 프로젝트 코드 리뷰: v0.4수행일지(스프린트 회의록,4차 연동 테스트 보고서) |

- 

  - 

- 

  - 

- 

- 
| 8주차 | 프로젝트 구현전체 기능의 100%검증5차 연동 테스트 | 프로젝트 코드 리뷰: v1.0수행일지(스프린트 회의록,5차 연동 테스트 보고서) |

- 

- 

- 

- 

- 

- 
| 9주차 | 프로젝트 안정화최종 검증발표자료 작성 | 프로젝트 코드 리뷰: v1.1수행일지(스프린트 회의록,최종검증 보고서)발표자료 |

- 

- 
| 10주차 | 발표자료 작성 | 발표자료 |

#### Presentations (3768374)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3768374
**최종 수정**: v2 (2026-04-19 sync)

#### Demo_Videos (3211361)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3211361
**최종 수정**: v2 (2026-04-19 sync)

#### Reports (3342397)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3342397
**최종 수정**: v2 (2026-04-19 sync)

#### 제출 이름 logging (22151320)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22151320
**최종 수정**: v19 (2026-04-22 sync)

****
****
****
****
****
| 구글폼 | 마지막 제출 버전 이름 | 제출일 | Confluence 링크 | 클래스룸 링크 |
|---|---|---|---|---|
[](https://classroom.google.com/c/ODQ4MTkyMDc0Nzc1/a/ODQ4ODAxMjc3MDQz/details)
| SA (HW) | 2팀_HardwareArchitecture_05 |   |   | 제출 |
| SA (SW) | 2팀_SoftwareArchitecture_05 |   |   |
| TR | 2팀_TechnicalResearch_05 |   |   |
[](https://classroom.google.com/c/ODQ4MTkyMDc0Nzc1/a/ODU4NjYwOTk4MzE4/details)
| Standup | Standup_260421_2팀 |   |   | 제출 |
[](https://classroom.google.com/c/ODQ4MTkyMDc0Nzc1/a/ODQ5MDAxNzU5ODUw/details)
| Github FolderStructure | 2팀_FolderStructure_02 |   |   | 제출 |
| Sprint Presentation | 2팀_발표자료_Sprint4 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/EABbAQ)
[](https://classroom.google.com/c/ODQ4MTkyMDc0Nzc1/a/ODU4OTUxOTA4ODYy/details)
| State Diagram | 2팀_StateDiagram_RobotArm_02 |   | https://dayelee313.atlassian.net/wiki/x/EABbAQ | 제출 |
| 2팀_StateDiagram_AMR_02 |   |   |
| 2팀_StateDiagram_Manhole_02 |   |   |
[](https://dayelee313.atlassian.net/wiki/x/CABeAQ)
| Sequence Diagram | 2팀_SequenceDiagram_02 |   | https://dayelee313.atlassian.net/wiki/x/CABeAQ |
[](https://dayelee313.atlassian.net/wiki/x/DABcAQ)
| Interface Specificaiton | 2팀_InterfaceSpecification_01 |   | https://dayelee313.atlassian.net/wiki/x/DABcAQ |
| ERD |   |   |   |
| GUI Design |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/UABTAQ)
| Class diagram | 2팀_ClassDiagram_02 |   | https://dayelee313.atlassian.net/wiki/x/UABTAQ |
| 연동 테스트 | 2팀_TestReport_01 |   |   |   |

#### 03_Technical_Research (6488246)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6488246
**최종 수정**: v40 (2026-04-19 sync)

****
****
****
****
****
****
****
****
****
****
| HW/SW | Device/Model | Research Area | 담당자 | 실험 리스트 | Page | Priority | Status | Start Date | End Date |
|---|---|---|---|---|---|---|---|---|---|
****
| HW |
|   | Robot_Arm | Spec test, 실제 시나리오 상 시연 가능성 테스트 |   | Payload test |   | 1 |   |   |   |
|   |   | Reachability_test |   | 1 |   |   |   |
|   |   | Repeatability_test Dots Marking test) |   | 1 |   |   |   |
|   |   | Repeatability_test (Dots 한붓 그리기 실험) |   | 1 |   |   |   |
|   |   | DoF Test & Orientation Edge Case |   |   |   |   |   |
|   |   | Mold Making - Cycle Time Test & Real Process Test |   |   | cycle time test           Quality 비교 실험 |   |   |
|   |   | Pouring - Cycle Time & Real Process Test |   |   |   |   |   |
|   |   |   |   | Camera Matching |   |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/HwD)
|   | AMR | Mapping, Navigation test, Navigation Accuracy Validation |   | Mapping Test | https://dayelee313.atlassian.net/wiki/x/HwD | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/AQCd)
|   |   | Navigation Test | https://dayelee313.atlassian.net/wiki/x/AQCd | 1 |   |   |   |
|   |   | Docking Server |   | 2 |   |   |   |
|   | Gripper | Spect Test, Types_comparison, Grasp_test, Failure_cases |   | Gripper Holding Test |   | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/UYDy)
|   | Conveyor | Spec 조사, 실제 시연 적용 가능성 조사 |   | 적용가능성 조사 | https://dayelee313.atlassian.net/wiki/x/UYDy | 1 |   |   |   |
|   |   | 비전 검사 & 상위 통신 연동 테스트 |   | 2 |   |   |   |
|   | Sensor | Sensor spec, detection_test, reliability |   | 사용 센서 |   | 1 |   |   |   |
|   |   | RGB-D camera |   | 1 |   |   |   |
|   |   | 레이저 센서 |   | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/FQDO)
|   | Embedded Board | HW_type, System_type, Spec |   | 스펙 조사 | https://dayelee313.atlassian.net/wiki/x/FQDO | 2 |   |   |   |
|   | Layout | Workspace_design, Collision_Analysis |   |   |   |   |   |   |   |

|   | RFID | Spec_Test,ID_Detection_Test ,System_Efficiency |   | RFID 기초 통신 및 UID 추출 실험 |   |   |   |   |   |
|   | 네트워크 연결 및 서버 데이터 전송 실험 |   |   |   |   |   |
|   | PostgreSQL 데이터베이스 연동 및 쿼리 실행 실험 |   |   |   |   |   |
|   | End-to-End Data_Link_Test |   |   |   |   |   |
****
| SW |
****
****
|   | 제어/시스템 SW |   |   |   |   |
|   | State_Machine | Design, Edge_Cases |   |   |   |   |   |   |   |
|   | Transport_System | Allocation_Strategy, Simulation_Test |   |   |   |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/12124168/?draftShareId=4e04722a-201a-4594-ae2a-52bfe921ced3)
|   | Storage_System | Slotting, Reallocation, Edge_cases |   |   | https://dayelee313.atlassian.net/wiki/spaces/753667/pages/12124168/?draftShareId=4e04722a-201a-4594-ae2a-52bfe921ced3 | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/fIDr)
|   | Control_System | Logic_Design, Exception_Handling |   |   | https://dayelee313.atlassian.net/wiki/x/fIDr | 2 |   |   |   |
****
|   | AI 모델 SW |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/IwB1)
|   | Vision | Image Classification, Object Detection |   | YOLO26 기초조사 | https://dayelee313.atlassian.net/wiki/x/IwB1 | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/C4Ca)
|   |   |   |   | 이미지, 영상 픽셀 좌표 추출(YOLO26) | https://dayelee313.atlassian.net/wiki/x/C4Ca |   |   |   |   |
|   |   |   |   | 데이터셋으로부터 위치 좌표 추출 |   |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/eADC)
|   |   |   |   | Camera Calibration를 통한 좌표 변환 | https://dayelee313.atlassian.net/wiki/x/eADC | 2 |   |   |   |
|   |   | Object Detection |   | 맨홀 목업 샘플 라벨링 작업(YOLO) |   |   |   |   |   |
|   |   | Image Classification |   | 이미지 분류를 위한 YOLO 이미지 데이터셋 추출(images only)-컨베이어 벨트에서 진행 |   |   |   |   |   |
|   |   | Object Detection |   | 객체 탐지를 위한 적재함 위 맨홀 샘플의 이미지 데이터셋 추출(images, labels) |   |   |   |   |   |
|   |   | Image Classification |   | YOLO 이미지 분류 진행(컨베이어 벨트 위 샘플) |   |   |   |   |   |
|   |   | Image Classification |   | [부적합] 적재함 위 맨홀 샘플에 대해 이미지 분류 진행 |   |   |   |   |   |
|   |   | Object Detection |   | YOLO 객체 탐지 진행(적재함 위 맨홀 샘플) |   |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/9QCG)
|   |   |   |   | Anomaly Detection with PatchCore | https://dayelee313.atlassian.net/wiki/x/9QCG | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/LACS)
|   |   |   |   | Binary Classifier via Transfer Learning with YOLOv26 nano model | https://dayelee313.atlassian.net/wiki/x/LACS | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/MwC-/)
|   |   |   |   | AD Comparative Study with PatchCore & RGDB-AD | https://dayelee313.atlassian.net/wiki/x/MwC-/ | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7438588/?draftShareId=6283774c-2071-4234-aada-f8a6fc89f2be)
|   | LLM/VLM |   |   |   | https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7438588/?draftShareId=6283774c-2071-4234-aada-f8a6fc89f2be | 3 |   |   |   |
|   | VLA |   |   | AI Server에서 사용 가능한 VLA 모델 탐색 |   |   |   |   |   |
|   |   |   |   | VLA Octo, LeRobot(Diffusion policy, |   |   |   |   |   |
****
| DB System |
[](https://dayelee313.atlassian.net/wiki/x/_QBy)
|   | Database_System | ERD_design, State_management, Transaction_consistency, Event_flow, Latency_test |   | ERD, SQL, Tools 자료 조사 및 공유 | https://dayelee313.atlassian.net/wiki/x/_QBy | 1 |   |   |   |
|   |   | Schema 작업 |   | 2 |   |   |   |
|   | Cloud Service |   |   | DB Cloud 서비스 & 실제 적용 가능성 조사 |   | 3 |   |   |   |
|   | Cache_System | Redius_usage, Task_queue, State_cache |   |   |   |   |   |   |   |
|   | Loggin_System | Sensor_logs, Time_series, Monitoring |   |   |   |   |   |   |   |
****
| Server |
|   | Kubernetes |   |   |   |   | 2 |   |   |   |
|   | AWS, GCP |   |   |   |   |   |   |   |   |
 

- 
priority 1: sprint 2 ~ 3 마무리 필요

- 
priority 2: sprint 3 조사 마무리 필요

#### Mapping (12582943)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/12582943
**최종 수정**: v29 (2026-04-20 sync)

# 
Map의 품질은 Localization과 Navigation의 성능을 좌우하는 큰 요소이기 때문에 고품질의 map을 제작하는 것이 중요하다.
따라서 실제 운용 환경과 유사한 조건에서 SLAM 성능을 검증하고,
파라미터를 사전에 조정함으로써 위치 추정과 주행에 유리한 고품질의 map을 제작하는 것을 목적으로 한다.

# 실험 개요
Map으로 사용될 공간을 다른 팀과 나눠 사용하여 절반 크기의 환경에서 초기 mapping 실험을 수행하였다.(실험 1)
이후 전체 공간을 확보한 뒤, 동일한 으로 full map mapping 실험을 수행하였다.(실험 2)
각 실험에서는  변경, 고정 장애물 배치, 을 통해 map 품질을 개선하고,
Map의 품질과 Localization을 중점적으로, 주행 가능 여부를 간단하게 검증하였다.

# 

- 
****
Map이 단순해서

- 
**고정 장애물 추가 (Fig. 2)**
Localization은 잘 되는데, map이 너무 작아서 주행 테스트가 어려웠음

- 
**고정 구조물 이동 & resolution 변경 후 편집 (Fig.3)**
고정 구조물 이동 후 작은 map을 더 세밀하게 표현하고자 resolution을 낮추고, 노이즈 제거와 경계를 정리
Localization이 잘 되는 것을 확인했고, 팀원들이 공간을 비워주어 이후 실험 2로 이어서 진행함
0.01
이에

1. 
odometry 계산을 어떻게 하고 있는지

1. 
wheel radius가 올바른지
에 대해서 분석하여  하고, 답변을 바탕으로 실험 2를 진행하였다.

# 실험 2. Mapping - full map

- 
full map에서 작성한 map (Fig. 4)

- 
Fig. 4의 map을 편집한 map (Fig. 5)

## 2.1 full map 1
로 작성된 map
comment 완료 시 삭제 예정!!

comment가 완료 시 삭제 예정!!
]()
**함종수 강사님 피드백**:
**고찰**

- 
첫 scan은 초기 map 기준을 만드는 출발점이라서 중요하다.

- 
시작 자세가 벽이나 복도 축과 맞으면 첫 scan부터 직선 구조가 반듯하게 들어가고

  - 
이후 scan도 더 안정적으로 붙는다.
**조사**

- 
slam toolbox에서는 [첫 node의 x, y, θ 값을 pose graph에서의 기준점으로 고정](https://github.com/SteveMacenski/slam_toolbox/blob/ros2/solvers/ceres_solver.cpp#L237-L239)한다.

- 
기준점으로 고정되면, 최적화에서 제외되고 값이 변하지 않는다.

- 
이후 node들은 첫 node를 기준으로 하여

  - 
odometry와 scan matching으로 추정된 pose 위치에 새로운 scan을 순차적으로 배치한다.

  - 
scan matching은 use_scanmatching이라는 파라미터를 false로 설정하면 반영하지 않는다.
그래서 사선 계단 현상이나 초기 map 기울어짐이 덜해진다.

## 

- 
피드백을 바탕으로 로봇을 map의 기준 축에 맞춰 정렬한 후 작성한 map (Fig. 6)

- 
Fig. 4의 map을 편집한 map (Fig. 7)

- 
resolution은 map의 정보를 더 잘 표현하여

  - 
Navigation의 세밀한 주행과

  - 
amcl의 성능을 높이기 위해 0.025로 설정했다.

- 
실제 운용 환경과 유사한 조건에서도 SLAM Toolbox 기반으로 안정적인 Mapping이 가능함을 확인했다.

- 
고정 장애물 배치, resolution 조정, map 편집, 초기 자세 정렬 등의 요소가 map의 품질과 Localization 성능에 직접적인 영향을 준다는 점을 확인했다.
이를 바탕으로 실제 주행에 활용 가능한 map을 작성할 수 있으며, 이후 Navigation test를 위한 기반을 마련했다.

#### 강사님께 Odometry 질문 (12156934)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/12156934
**최종 수정**: v17 (2026-04-19 sync)

# 

### 질문 전 사전 조사

1. 
odometry 계산을 어떻게 하는지
→ pinky pro는 imu가 있음에도 encoder만 사용한 wheel odometry를 사용하고 있었다.

1. 
바퀴 크기가 올바른지
→ wheel radius 설정은 0.028m로 되어있었는데 실제로 측정한 크기는 0.027m였다.

### *최종태 강사님께 질문*
보통 odometry는 encoder + imu 값을 robot_localization 패키지의 ekf_odom을 사용하여 품질을 높이는데, pinky pro는 왜 imu를 사용하지 않는지?
강사님께 질문했을 때는

- 
dynamic cell로 모터가 변경되면서 encoder 품질 향상으로 인해 imu를 제거했다.

- 
imu를 통해 얻는 주행 품질이 미미해서 제거했다.
라고 하셨다.

### pinky pro를 개발하셨다는 민경환 강사님께 재질문
의문
→ 지도 품질이 좋지 않아서, mapping할 때 scan matching을 끄고 천천히 회전했는데, lidar가 밀린다.
확인해본 건

1. 
pinky bringup쪽 코드를 보니 imu를 사용하지 않고 있었고,

1. 
wheel radius가 0.028m로 되어있었는데 실제로 0.027m였다.
그래서 질문은
imu를 사용하지 않고 wheel odometry만 사용하시는 이유
대답은
encoder로도 odometry 측정이 어느 정도 안정적이라고 생각했다.
그래서 wheel radius 얘기(*설정과 실제 크기의 0.001m 차이*)를 해드렸더니 해당 부분은 문제가 맞다고 하시고,
코드를 수정했더니 odometry가 더 정확해지는 것을 확인할 수 있었다.
반영해서 [깃허브를 수정](https://github.com/pinklab-art/pinky_pro/commit/84a1137f022518eb202839a19654590dc8bef3f2)하셨다.

#### Navigation (10289153)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/10289153
**최종 수정**: v42 (2026-04-20 sync)

# 실험 목적
주어진 AMR의 크기와 속도, 하드웨어 성능에 맞추어, 작은 map에서 원활한 경로 생성과 안정적인 경로 추종이 가능하도록 파라미터 조정을 통해 Navigation 성능을 개선하는 것을 목적으로 한다.

# 실험 개요 
이를 위해 **장애물 사이의 좁은 경로 통과 성능**과 목표 지점 접근 시 **정확한 위치 도달 및 자세 정렬 성능**을 중점적으로 확인하며, AMCL, planner, controller, costmap 파라미터를 중심으로 실험을 수행한다.

# BackGround 

# 실험 환경
실험에서 거리 단위는 m, 각도 단위는 rad이다. 이외의 단위는 파라미터 설명에 별도로 작성한다.
map file name: `fullmap_modified2`
map resolution: `0.025`
pinky footprint: `0.12x0.12`
가장 좁은 통로의 기준을 0.24로 가정한다.

# 실험 1. 파라미터 튜닝
**작은 map과 RPP 알고리즘의 동작 방식을 반영하여 파라미터를 튜닝한다.**
파라미터 파일: `~/pinky_pro/src/pinky_pro/pinky_navigation/params/nav2_params.yaml`

## Localization 관련
라이다의 관측 주기가 있는데, 그 주기를 튜닝을 하면서, 관측 주기를 경험적으로 튜닝한다. 
**amcl:**
**update frequency:** AMCL이 필터 업데이트를 수행하기 위해 필요한 최소 회전량(a) & 이동량(d)

- 
`update_min_a: 0.02`

- 
`update_min_d: 0.015`

## **Costmap 관련**
costmap에서 0으로 가까운 쪽으로 path planner가 경로를 만든다.  따라서, `global_costmap` 관련한 파라미터 튜닝을 통해 길의 중앙으로 AMR이 이동할 수 있게 한다. 
**global_costmap : 전체 맵 관련 튜닝**
Global planner가 global costmap 을 이용해 Path planning 을 한다. 

- 
`footprint_padding: 0.02`

  - 
경로 계획이나 충돌 계산에서 로봇의 크기에 포함되고 로봇 주위로 둘러지는 padding 영역

  - 
global planner는, 최대한 중앙으로 경로를 생성해야 하기 때문에 0.02의 paddnig을 줌

- 
`resolution: 0.025`

  - 
global costmap은 map의 resolution과 동일하게 설정된다. 

- 
`inflation_radius: 0.075`

  - 
planner는 복도의 중앙으로 global plan을 생성하게끔 0.075로 설정

  - 
가장 좁은 통로 기준 중앙에 free space가 0.09m만큼 있음 →  

    - 
복도 전체 길이: 0.24m, 한쪽 벽면으로 부터의 inflation:  0.075

    - 
남은 통로 구간 길이: 0.09m

    - 
→ 따라서, 길의 중앙으로 갈 수 있게 한다. 
**local_costmap: **
global planner가 전역 path plan을 계산한 후, 실제 주행할때 local costmap을 보고 controller가 AMR을 제어하는데, 이때 local costmap만 참고하여 (즉, 당장 가야하는 짧은 경로에 대해서만 봄) controller가 주행 제어를 신호를 발행한다. 

- 
`footprint_padding: 0.0`

  - 
0.0으로 설정 → 좁은 통로를 지나가야 해서 padding을 주지 않음.

- 
`resolution: 0.01`

  - 
RPP 파라미터의 collision detection 파라미터 특성 상 resolution은 매우 중요하다.

  - 
collision detection은 obstacle의 lethal costmap을 보기 때문에, 아주 세밀하게 표현하기 위해 0.01로 설정했다.

  - 
최대한 줄여서, 섬세한 제어를 가능하게 한다. 대한 

- 
`inflation_radius: 0.2`

  - 
inflation radius는 RPP에게 장애물과의 거리에 대한 정보를 주기 때문에, 장애물로부터 충분한 거리까지 설정했다.

- 
`cost_scaling_factor: 3.0`

  - 
기본값으로 사용

- 
`width, height: 1`

  - 
*int type, *`1`*이 최솟값*

  - 
맵이 작기 때문에 최솟값으로 줄임

## Controller 관련

### 속도
컨트롤러 파라미터 튜닝
RPP는 pure pursuit 계열로, 전역 경로를 추종하며 최대 선속도에서 곡률 기반, 장애물 근접, 목표 접근에 따라서 감속을 적용한다.
우리는 오버슈팅, 경로 이탈이 나지 않는 낮은 속도로 주행하기에, 곡률 기반 감속을 제외한 장애물 근접, 목표 접근에 따른 감속만 적용한다.
또한, 경로 추종 전 회전을 사용하여, 방향과 크게 틀어진 자세에서 생기는 초기 오차와 불안정성을 줄였다.
**controller_server.FollowPath**
**최대 선속도**

- 
`desired_linear_vel: 0.1`

  - 
맵의 크기와 RPP의 동작 방식에 따라 최대 선속도를 0.1로 설정
**lookahead 거리**

- 
`lookahead_dist: 0.12`

  - 
0.1m 앞에 carrot을 고정

- 
`use_velocity_scaled_lookahead_dist: false`

  - 
lookahead dist를 고정으로 사용하기 때문에 false로 설정
**곡률 기반 감속**

- 
`use_regulated_linear_velocity_scaling: false`

  - 
곡선 진입 시 감속을 하지 않도록 설정
**장애물 근접 감속**

- 
`use_cost_regulated_linear_velocity_scaling: true`

  - 
장애물 근접 감속을 할 것인지

- 
`inflation_cost_scaling_factor: 3.0`

  - 
local_costmap의 cost_scaling_factor와 맞추어, 장애물까지의 거리 측정에 사용한다.

- 
`cost_scaling_dist: 0.1`

  - 
장애물과의 거리가 dist보다 가까워지면 감속을 시작한다.

- 
`cost_scaling_gain: 2.0`

  - 
gain으로 감속을 얼마나 할 것인지 계산한다

  - 
gain이 커지면 감속량이 작아진다.

  - 
(gain * 장애물까지의 거리) / cost_scaling_dist = x배로 속도 감속
**목표 접근 감속**

- 
`min_approach_linear_velocity: 0.03`

  - 
목표 근처에서의 하한 속도

- 
`approach_velocity_scaling_dist: 0.1`

  - 
목표 접근 감속 시작 거리
**경로 및 목표 방향 정렬**

- 
`use_rotate_to_heading: true`

  - 
경로 방향 또는 목표 방향 정렬을 위해 제자리 회전을 사용할지

- 
`rotate_to_heading_min_angle: 0.785 `

  - 
경로 방향과의 각도 차이가 이 값보다 크면 제자리 회전, 약 45deg

- 
`rotate_to_heading_angular_vel: 1.0`

  - 
제자리 회전 시 목표 각속도

- 
`max_angular_accel: 2.0`

  - 
제자리 회전 시 각가속도 제한

- 
`allow_reversing: false`

  - 
경로에 후진 구간이 있을 때 후진 추종을 허용할지
**충돌 감지**

- 
`use_collision_detection: true`

- 
`max_allowed_time_to_collision_up_to_carrot: 0.1`

  - 
현재 발행되는 속도로 몇 초까지 시뮬레이션을 할 것인지

### **목표 도달**
최종적으로 목표에 도달했을 때의 조건 (목표에 어느 정도 이내& 방향 threshold) 에 도달하면, 도착으로 판단 
**controller_server.general_goal_checker**
둘 다 만족해야 도착으로 판단한다.

- 
`xy_goal_tolerance: 0.03`

  - 
위치가 0.03m 이내라면 도착으로 판단.

- 
`yaw_goal_tolerance: 0.1`

  - 
방향이 5.72deg 이내라면 도착으로 판단.

# 결과 
좁은 맵 환경과 소형 AMR의 물리적 한계를 고려하여 파라미터를 최적화하였다.
좁은 통로에서의 안정적인 주행과 충돌 문제를 해결하고, 목표 지점에서의 정밀한 자세 정렬을 통해
실제 운용 환경에서도 안정적인 주행이 가능할 것으로 판단된다.

# 비고

### 함종수 강사님과 스몰토크
파라미터 튜닝 중 함종수 강사님께서 어제 wheel radius 이슈가 있었다고 하시며 잘 되는지 물어보셔서

- 
wheel odom에서 ekf odom(wheel odom + imu)으로 변경하는 것에 대한 질문을 했는데,

- 
covariance 설정이 어렵지만 잘 할 수 있다면 사용하는 것도 좋다고 말씀해주셨다.

#### Navigation parameters (11895081)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11895081
**최종 수정**: v19 (2026-04-20 sync)

## [Regulated Pure Pursuit Parameters](https://docs.nav2.org/configuration/packages/configuring-regulated-pp.html)

## [Costmap2D ROS Parameters](https://docs.nav2.org/configuration/packages/configuring-costmaps.html)

## [AMCL Parameters](https://docs.nav2.org/configuration/packages/configuring-amcl.html)

#### ArUco Marker (12517441)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/12517441
**최종 수정**: v26 (2026-04-19 sync)

# 실험 목적
주어진 AMR의 카메라 성능과 주행 특성에 맞추어, ArUco Marker를 안정적으로 인식하고 이를 기반으로 정확한 위치 추정 및 목표 지점 정렬이 가능하도록 제어 및 인식 파라미터를 조정하여 마커 기반 Navigation 성능을 개선하는 것을 목적으로 한다.

# 실험 개요 
이를 위해 다양한 거리 및 각도 조건에서 ArUco Marker 인식 안정성과 위치 추정 정확도를 평가하고, 마커를 기준으로 한 접근 및 정렬 과정에서의 주행 안정성과 제어 성능을 중점적으로 확인한다.

# 실험환경
 

# 실험1: ArUco Marker 테스트
**실험 내용**
실험 1에서는 ArUco Marker를 독립적으로 인식하고, 검출된 마커의 상대 위치를 기반으로 AMR이 목표 거리와 중심 정렬 상태에 도달하도록 제어하는 실험을 수행하였다.
이 단계에서는 다양한 거리와 각도에서 마커 인식이 얼마나 안정적인지, 그리고 마커 중심과의 오차를 이용한 단순 추종 제어가 실제로 안정적으로 동작하는지를 확인하는 데 중점을 두었다.
**중점 확인 항목**
마커 인식 안정성
거리와 각도 변화에 따라 마커가 지속적으로 검출되는지 확인하였다.
위치 추정 일관성
검출된 marker pose 값이 거리 변화에 따라 일관되게 변하는지 확인하였다.
추종 제어 안정성
마커 중심 오차와 거리 오차를 기반으로 전진 및 회전 명령을 생성했을 때, 급격한 진동 없이 목표 위치로 수렴하는지 확인하였다.

## 아루코 마커 정보
 

# 실험2: Docking Server 테스트
**문제 상황**
초기 실험에서는 docking_server가 detected dock pose를 사용하지 못하고 `cannot transform camera_link to odom` 오류를 반복적으로 출력하였다.
또한 Aruco follower 단독 시험에서는 marker를 향해 접근해야 하는 상황에서도 후진 명령이 발생하였다.
이는 detector pose의 기준 좌표계와 추종 제어식이 서로 다른 축 기준을 사용하고 있었기 때문이다.
**조정한 항목**

1. 
detector pose 기준 frame 정렬
Aruco detector가 퍼블리시하는 `/detected_dock_pose`의 frame이 실제 TF 트리에서 변환 가능한 값과 일치하도록 조정하였다.
이를 통해 docking_server가 marker pose를 odom 기준으로 해석할 수 있도록 하였다.

1. 
marker pose 기준 도킹 목표 오프셋 조정
follow-only 실험을 통해 marker가 “정답 위치”에서 어떻게 보이는지 확인한 뒤, 그 값을 바탕으로 docking 목표 오프셋을 설정하였다.
특히 marker 기준 전방 목표 거리를 반영하기 위해 external_detection_translation_x를 조정하였다.

1. 
docking 완료 판정 허용 범위 조정
좁은 공간과 소형 AMR의 위치 흔들림을 고려하여 docking_threshold_x, docking_threshold_y를 완화하였다.
이를 통해 실질적으로 도킹이 완료된 상태에서도 지나치게 엄격한 기준 때문에 실패로 판정되는 문제를 줄이도록 하였다.

1. 
마커 손실 시 pose 유지 시간 조정
근접 구간에서는 마커가 일시적으로 시야에서 벗어날 수 있으므로, 마지막으로 검출된 pose를 짧은 시간 유지하여 최종 접근이 끊기지 않도록 하였다.

## 도킹 서버 정보
 

# 결과
ArUco Marker 기반 주행에서 카메라 인식 성능과 AMR의 물리적 제어 한계를 고려하여 파라미터를 최적화하였다.
마커 인식이 불안정하거나 일시적으로 손실되는 상황에서도 안정적인 정지 및 재추적이 가능하도록 제어 로직을 구성하였으며,
마커 중심을 기준으로 한 정렬과 거리 제어를 통해 목표 지점에서의 정밀한 위치 도달을 구현하였다.
이를 통해 실제 환경에서도 ArUco Marker를 활용한 안정적인 위치 정렬 및 도킹이 가능할 것으로 판단된다.

# 발표용 정리
ArUco Marker 기반 정밀 주행을 위해 다음과 같은 기준으로 파라미터를 설정하였다.

- 
마커 인식 및 추종 기준

  - 
특정 ID를 타겟으로 선정

  - 
전진은 x축, 좌우 정렬은 y축 기준으로 제어 수행

- 
안정적인 주행을 위한 제어 설정

  - 
linear_gain: 전후 거리 x 오차에 대한 선속도 제어

  - 
angular_gain: 좌우 편차 y 오차에 대한 각속도 제어

  - 
turn_ratio를 제한하여 급격한 회전 방지

  - 
min_drive_speed를 설정하여 저속 구간에서의 정지 현상 방지

- 
정밀한 도착을 위한 조건 설정

  - 
x_tolerance, z_tolerance 범위 내 진입 시 목표 도달로 판단

  - 
도달 시 모터 정지(REACHED 상태)

- 
마커 손실 대응

  - 
검출 손실 시 마지막 dock pose 를 일정 시간 유지하여 docking_server 의 최종 접근 안정성을 확보

- 
연산 및 안정성 고려

  - 
필요한 최소 해상도(640x480)로 처리하여 연산량 최적화

  - 
marker_length 및 카메라 calibration 값 기반 pose 추정 정확도 확보

#### Docking Server (28049473)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/28049473
**최종 수정**: v18 (2026-04-20 sync)

# 목적
만으로도 정밀한 주행은 가능하지만,
로봇팔과의 원활한 연동을 위해 최종 도착 자세의 정밀도를 더욱 높이고자 Docking server를 구현한다.

# 개요
[https://github.com/ros-navigation/navigation2/tree/main/nav2_docking](https://github.com/ros-navigation/navigation2/tree/main/nav2_docking)
위 패키지를 기반으로 Docking 기능을 구현하고, 정적 pose 기반 방식과 AprilTag 기반 방식으로 각각 검증한다.

1. 
외부 센서를 사용하지 않고, odom 좌표계 기준의 고정 dock pose를 이용해 도킹을 테스트한다.

1. 
AprilTag를 검출하는 패키지를 구현한 뒤 docking server와 연동하여, 센서 기반 도킹을 테스트한다.

# 환경

- 
pinky_pro의 카메라

  - 
width: 640

  - 
height: 480

  - 
fps: 10

  - 
rotate_180: true

- 
[https://chev.me/arucogen/](https://chev.me/arucogen/)

  - 
Dictionary: 4x4

  - 
Marker ID: 0

  - 
Marker size, mm: 50

  - 

# 실험 1. 외부 센서를 사용하지 않고 도킹
실험 1에서는 외부 센서를 사용하지 않고, 고정 dock pose를 이용해 도킹을 테스트했다.

1. 
외부 센서를 사용하지 않았기 때문에, refined pose는 입력된 dock_pose와 동일하다.

1. 
이후 docking server는 보정된 pose를 로봇 기준 좌표계로 변환하여 controller에 전달하고

1. 
controller는 이를 기반으로 cmd_vel 및 충돌 검사를 계산한다.
[시연 영상](https://drive.google.com/file/d/1vg2jXsDDRxLheDAUijNwY0vnEjuN6ITG/view?usp=drive_link)

# 실험 2. April tag를 외부 센서로 사용하여 도킹
실험 2에서는 AprilTag를 외부 센서로 사용하여 센서 기반 도킹을 테스트했다.
AprilTag 검출용 외부 노드에 대한 설명은 를 참고!

- 
aruco_node가 카메라 영상에서 AprilTag의 위치를 검출하고,

- 
docking server는 해당 검출 결과를 이용해 근접 도킹 단계에서 사용할 refined pose를 지속적으로 갱신한다.

- 
이후 docking server는 보정된 pose를 로봇 기준 좌표계로 변환하여 controller에 전달하고

- 
controller는 이를 기반으로 cmd_vel 및 충돌 검사를 계산한다.

- 
odometry 좌표계 기준으로 목표에 도달하면, 성공을 반환한다.
고정된 dock_pose가 아니라 AprilTag로 실제 검출된 dock 위치를 반영하여 정밀하게 도킹을 수행했다.
[시연 영상 - rviz](https://drive.google.com/file/d/1jEU0yb4JVcO2rzNul6_-mXtTdpxwExpk/view?usp=sharing)
[시연 영상 - camera](https://drive.google.com/file/d/18KYeE_BQOnbGKOto5bGOYH4wAUWTspb6/view?usp=sharing)

# 결과
Docking server를 통해서 1cm 내외의 오차로 정밀하게 도착하는 것을 확인할 수 있었다.

#### 강사님께 Docking Server 질문 (29360157)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/29360157
**최종 수정**: v7 (2026-04-20 sync)

# Docking Server Calibration

1. 
[https://pinkwink.kr/1427](https://pinkwink.kr/1427) 

### 질문은

1. 
현재 캘리브레이션하는 과정이 올바른지

1. 
핑크랩 혹은 다른 수강생들은 docking server를 사용하셨는지?

### 민경환 강사님의 대답은

1. 
[calibration 강의 자료](https://github.com/pinklab-art/pinky_study/wiki/2.2-Pinky-Pro(part2))를 보고 진행하는 것을 추천

1. 
핑크랩에서는 직접 개발해서 사용했고,

#### AMR Fundamentals (15007947)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15007947
**최종 수정**: v5 (2026-04-19 sync)

#### Localization? (14942421)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/14942421
**최종 수정**: v14 (2026-04-19 sync)

# Odometry
odometry는 시간 경과에 따른 로봇의 상대적 위치를 추정하는 방법을 의미한다.

## Wheel Odometry
wheel odom은 encoder로 측정한 바퀴의 회전량을 이용해 로봇의 상대적인 위치와 자세 변화를 추정한 값이다.

- 
바퀴의 회전량

- 
바퀴 반지름

- 
바퀴 사이 간의 간격

- 
로봇의 기구학적 구조, motion model

  - 
differential - 좌우 바퀴의 회전 속도 차이를 이용해 직진과 회전을 수행하는 방식

    - 
pinky는 differential

  - 
omni - omni wheel을 사용하여 전방향 이동이 가능한 방식

  - 
mecanum - mecanum wheel을 사용하여 전방향으로 이동할 수 있는 방

  - 
ackermann - 자동차같이 앞바퀴의 조향각을 바꿔서 회전하며 주행하는 방식

## EKF Odometry
EKF odometry는 wheel odometry, IMU 등 여러 센서 데이터를 입력으로 받아,
로봇의 위치, 속도, 자세 등의 상태를 추정한 odometry이다.

### EKF(Extended Kalman Filter)
EKF는 비선형 시스템에서 상태를 추정하기 위해 사용하는 필터다.
선형 Kalman Filter는 선형 시스템을 가정하여 상태를 추정하지만,
로봇의 이동 모델과 센서 측정 모델이 비선형인 경우가 많다.
EKF는 이런 비선형 모델을 현재 추정 상태 주변에서 선형화해서, 예측과 보정을 통해 상태를 추정한다.
EKF는 1차 테일러 급수 전개를 통해 비선형 시스템을 근사하여 그 결과로 얻는 자코비안 행렬을 칼만 필터에 적용한다.

### 간단하게 동작을 보면

1. 
motion model로 현재 상태를 예측하고

1. 
관측된 sensor data의 측정값으로 그 예측값을 보정하는 방식
Kalman gain은 motion model의 예측값과 sensor model의 측정값 중 어느 쪽을 더 신뢰할지에 대한 가중치.
`robot_localization`이라는 패키지는 sensor 데이터들을 추가하면 이 계산을 수행해준다.
odometry와 imu의 어떤 정보들을 사용할지 config에서 정하고,
[odometry](https://docs.ros.org/en/noetic/api/nav_msgs/html/msg/Odometry.html)와 [imu](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/Imu.html)의 메세지에는, 각 데이터와 함께 covariance(공분산)을 추가해주면 된다.

### [ekf config file](https://docs.nav2.org/setup_guides/odom/setup_robot_localization.html)

# AMCL(Adaptive monte carlo localization)

## 동작 방식(단계 적을 예정)

1. 
Map이 존재하고, 초기 위치가 주어졌을 때, 현재 위치를 가정하는 (x,y,theta) 정보를 가진 입자(파티클)을 그 주변으로 퍼트린다.

1. 
로봇이 이동하면, odometry 이동량을 받아, 노이즈(alpha)를 섞고, 각 파티클에 이동량을 반영한다.

1. 
지도에서 해당 파티클 위치들을 기준으로, 예상되는 라이다 스캔(map을 아니까)을 현재 스캔과 비교한다.

1. 
현재 스캔과 비교 결과가 잘 맞는 파티클은 가중치를 높게 주고, 잘 안 맞는 파티클은 가중치를 낮게 준다.

1. 
위 단계가 끝나면, 각 파티클 별로 가중치가 생긴다. (0.001, 0.5, 0.0827…) 이 값을 그대로 사용하는 게 아니라, 모든 파티클의 가중치의 합이 1이 되도록 정규화한다.

1. 
이 단계가 중요한데, 가중치가 높은 파티클들은 많이 남기고, 가중치가 낮은 파티클들은 제거한다.

1. 
이 단계를 거치면, 지도와 실제 센서가 잘 맞는 파티클들은 점점 많아지고, 틀린 파티클들은 점점 사라진다.

1. 
살아남은 파티클들을 가까운 것들끼리 군집으로 묶고, 그 군집의 평균을 내서 최종 pose를 만든다.

1. 
이 과정을 반복하며 위치를 추정한다.

### alpha
odometry의 이동량과 회전량에 비례해 오차 분산을 만드는 계수를 조절하는 파라미터

- 
AMCL의 motion update 단계에서 odometry를 바탕으로 파티클을 이동시킬 때, 얼마나 노이즈를 섞을지

- 
`alpha1:`회전 때문에 발생하는 회전 오차

- 
`alpha2:`직진 때문에 발생하는 회전 오차

- 
`alpha3:`직진 때문에 발생하는 직진 오차

- 
`alpha4:`직진 때문에 발생하는 회전 오차

- 
`alpha5:`전방향 이동 움직으로 인한 오차, OmniMotionModel을 위한 파라미터

### update frequency
의미 없이 초당 수백 수천번 계산하는 게 아닌, 로봇이 의미있게 움직였을 때만 계산하게끔 최소 이동량을 정한 것.
계산: motion(odometry)와 sensor값을 받아서 업데이트

- 
`update_min_a: `몇 rad마다 업데이트할지

- 
`update_min_d: `몇 m마다 업데이트할지

#### Mapping? (14975186)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/14975186
**최종 수정**: v10 (2026-04-19 sync)

# 용어 설명
**occupancy map(점유 맵)**
공간을 격자(cell) 단위로 나누고 각 셀을 점유 영역, 빈 공간, 미확인 영역으로 구분하여 표현한 지도

- 
보통 ros2의 2D map에서는 occupancy map(점유 맵)을 사용한다.
**cell(격자 셀)**
occupancy map을 구성하는 기본 격자 단위

- 
각 cell은 공간의 작은 한 칸에 해당한다.
**resolution**
제작된 map에서 하나의 cell을 실제 공간에서 몇 m를 나타내는지를 의미

- 
resolution이 0.05라면 cell 1칸은 5cm

- 
resolution이 0.01이라면 cell 1칸은 1cm

- 
resolution에 따라서 map의 세밀한 표현을 조절할 수 있다.

  - 
resolution이 높다 → map이 거칠게 표현된다 → 해상도가 낮다.

  - 
resolution이 낮다 → map이 세밀하게 표현된다 → 해상도가 높다. 

# [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox)

- 
LiDAR 등의 센서 데이터를 이용해 현재 로봇의 위치를 추정하며 2D Map을 생성하는 ROS2 패키지

- 
pose graph 기반의 Karto 계열 SLAM을 이용해 지도 생성과 loop closure 보정을 수행한다.

## pose graph
로봇이 이동하면서 지나온 node(pose)들과, 그 node들 사이의 edge(관계)를 그래프로 표현한 것

- 
Node: 로봇의 특정 시점의 자세

  - 
위치 x,y와 방향 θ로 표현한다.

  - 
로봇의 pose 정보를 담고 있다고 생각하면 된다.

- 
Edge: 두 자세 사이의 상대적 관계

  - 
한 자세에서 다음 자세로 얼마나 이동했고 얼마나 회전했는지 나타낸다.

## loop closure

- 
odometry는 움직일수록 오차가 누적된다.

- 
따라서 odometry만 사용하면, 실제로는 출발점 근처로 돌아왔음에도** **다른 위치로 인식할 수 있다.
loop closure를 사용한다면, 이런 상황에서

- 
과거 pose와 현재 pose가 동일한 장소라는 정보를 pose graph에 추가한다.

- 
전체 그래프를 다시 조정하고 오차를 보정한다.

#### 그냥 보정이라고 하면 되는데 왜 최적화라고 할까?
edge마다 조금 틀릴 수도 있고, 어떤 edge는 믿을만할 수도 있다.
그래서 정답이 하나가 아니고, 오차가 전체적으로 가장 작아지는 해를 찾는 것이기 때문에 최적화라고 한다.
*pinky pro에서는 *[*CeresSolver로 최적화를 하도록 설정*](https://github.com/pinklab-art/pinky_pro/blob/main/pinky_navigation/params/mapper_params.yaml#L5)*되어있다.*

### 무조건 쓰는 게 좋을 것 같은데?
**loop closure가 항상 좋은 건 아니다.**
기본적으로 과거에 본 장소가 현재 장소임을 인식했을 때, 강한 제약을 거는 방식이어서

- 
비슷한 scan data가 쌓이는 복도

- 
비슷한 문이 계속 나오는 구조

- 
대칭적인 실내 공간
위와 같이 비슷한 환경이 반복되는 구조에서는 잘못된 인식을 할 수도 있다.
**굳이 사용하지 않아도 될 때도 있다**

- 
공간이 작거나

- 
주행 거리가 짧거나

- 
odometry의 drift가 크지 않을 때

# Map editing
AMR에서 사용하는 2D map은 보통 **Occupancy Grid Map** 형태로 표현된다.
LiDAR 스캔 데이터가 반복적으로 누적되면서 특정 위치가 장애물로 관측되면 해당 셀은 점유된 공간으로 표현된다.
일반적으로

- 
**검정색(100)**은 점유 영역(장애물),

- 
**흰색(0)**은 주행 가능한 빈 공간,

- 
**회색(-1)** 아직 관측되지 않았거나 불확실한 영역을 의미한다.
색상 옆의 각 숫자는

- 
**0 (free)** → 지나갈 수 있음

- 
**100 (occupied)** → 장애물 → 못 지나감

- 
**-1 (unknown)** → 상황에 따라 다름

  - 
안전하게 주행해야 할 경우 unknown 영역을 장애물로 취급해서 못 지나갈 수도 있고,

  - 
탐사 또는 미지 영역의 주행이 필요한 경우 경로 생성이 가능한 영역으로 볼 수도 있다.
하지만 실제 mapping 결과에는 센서 노이즈나 일시적인 장애물의 흔적이 포함될 수 있으므로,
주행에 더 적합한 형태로 map을 일부 수정할 필요가 있다.
이때 GIMP와 같은 이미지 편집 도구를 사용하면 map의 노이즈를 직접 제거하거나 경계를 정리할 수 있다.

###### 다양한 얘기가 있지만 그건 나중에 적기

### Gimp
Photoshop과 같은 그림 및 사진 편집 도구이며, 비슷한 프로그램으로는 [Krita](https://namu.wiki/w/Krita)가 있다.

#### Costmap? (15040713)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15040713
**최종 수정**: v10 (2026-04-19 sync)

# Cost 설명
**0**(free space): 안전한 구간
**1~252**: 장애물 근처의 완충 구간
**253**(inscribed inflated obstacle): robot의 inscribed radius 내에 있는 장애물에 거의 닿는 위험 구간

- 
inscribed radius: 로봇 중심에서 footprint의 각 내접 반지름과 외접 반지름까지의 최소 거리

  - 
pinky는 0.12x0.12니까 0.06, 대각선은 0.08 정도
**254**(lethal obstacle): 장애물 본체
*0-cost 영역이라는 건, cost가 없는 안전한 구간이라고 이해하면 된다!*

# Cost 계산

- 

  - 
: 장애물로부터의 거리

  - 
: inscribed radius

  - 
: cost scaling factor

    - 
는 cost scaling factor, 코스트가 얼마나 감소할지 정하는 계수

    - 
는 로봇이 거의 닿는 경계부터 얼마나 떨어져있는가

    - 
은 inflation cost가 가질 수 있는 일반 cost

      - 
는 253

      - 
계산식은 위에 Cost 설명에서 작성된 “장애물 근처의 완충 구간”의 장애물과 가장 가까운 곳, 252

  - 
그래서 결국 장애물로부터 거리가 멀어질수록 cost가 지수적으로 감소한다는 뜻!!!!

# Costmap

## Global costmap
전역 지도와 실시간으로 들어오는 장애물 정보를 바탕으로 생성되는 비용 지도로, planner가 목표 지점까지 이동할 전체 경로를 계획할 때 사용된다. 
일반적으로 static layer, obstacle(voxel) layer, inflation layer를 기반으로 구성된다.

## Local costmap
로봇을 중심으로, 로봇 주변의 장애물 정보를 반영하여 지속적으로 갱신되는 비용 지도로, controller가 현재 주행에 필요한 속도를 계산할 때 참고한다.
일반적으로 obstacle(voxel) layer와 inflation layer를 기반으로 구성된다.

# Costmap Plugins
Costmap은 하나의 정보로만 만들어지는 것이 아니라, 여러 plugin layer를 조합하여 구성된다.
각 layer는 지도, 장애물, 장애물 근처의 위험 구역 같은 서로 다른 정보를 costmap에 반영한다.

## Static layer
기존의 정적 지도를 costmap에 반영하는 layer다.
벽, 기둥, 고정 

## Obstacle layer
센서 데이터를 받아 관측된 장애물을 costmap에 반영하는 layer다.

## Inflation layer
Static layer의 고정 장애물이나, Obstacle layer의 동적 장애물 주변에 비용(cost)를 퍼트려, 장애물에 가까울수록 더 높은 cost를 부여하는 layer다.

#### Navigation? (15040664)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15040664
**최종 수정**: v9 (2026-04-19 sync)

# Planner
global costmap을 참고하여 전역 경로를 생성

# Controller
Controller는 전역 경로를 추종하며 현재 로봇의 상태를 반영하여,
로봇 주변의 장애물 정보가 반영된 local costmap을 참고해 현재 발행해야할 속도를 계산하는 제어기다.

### RPP
RPP는 Pure pursuit 계열의 controller로, 스스로 경로를 만들고 장애물을 회피하지 않고 경로를 추종한다.
pure pursuit 계열의 controller는, 전역 경로 위의 목표인 carrot을 따라간다!
carrot은 전역 경로 위에서 로봇이 가야하는 방향으로, 로봇으로부터 일정 거리만큼 떨어진 lookahead point다.

### 동작 방식을 간단하게 설명하면,

#### **지역 경로 얻어내기**

1. 
전역 경로에서 현재 로봇과 가장 가까운 점을 찾고, 그 점 이전의 궤적은 삭제한다.

1. 
local costmap의 최대 반경 범위를 넘어가는 전역 경로는 임시로 무시한다.

1. 
잘라낸 전역 경로를 로봇 프레임 기준으로 변환한다.
````.
변환된 로봇 프레임 기준의 경로는 지역 경로라고 하겠다!

#### ****

1. 
변환된 지역 경로를 순회하면서, 로봇에서 바라보는 사전 설정된 거리에 맞는 지점을 찾는다.
사전 설정된 거리는

- 
`use_velocity_scaled_lookahead_dist`라는 파라미터를

- 
`false`로 설정하면 `lookahead_dist`라는 파라미터에 설정된 고정값을 사용하거나

- 
`true`로 설정하면

  - 
`lookahead_time`이라는 파라미터에 현재 속도를 곱해서 `lookahead_dist`를 정한다.

  - 
`min_lookahead_dist`와 `max_lookahead_dist`로 상하한을 제한할 수 있다.

  - 
만약 정확한 거리의 점이 없으면, 선형 보간으로 가장 가까운 Carrot 지점을 찾는다.

1. 
Carrot으로 가기 위해 얼마나 회전해야 할 지 곡률(Curvature)로 환산한다.

#### **속도 계산하기**

1. 
`desired_linear_vel` 값으로 시작해서, 각 상황에 따라 추가적으로 감속하는 식으로 계산한다.

- 
곡률이 크면 감속

  - 
`use_fixed_curvature_lookahead`파라미터를

    - 
`false`로 설정하면 아까 계산한 Curvature을 그대로 사용하고,

    - 
`true`로 설정하면 `curvature_lookahead_dist`라는 파라미터에 설정된 고정값으로 다시 계산한다.

      - 
`use_velocity_scaled_lookahead_dist`와 밀접한 관계를 갖고 있는데,

      - 
높은 속도 → `lookahead_dist` 증가 → 멀리 있는 큰 곡률 확인 → 속도 감속 →
`lookahead_dist` 감소 →  짧아서 곡률 감소 → 속도 증가 → 높은 속도 ….

      - 
이런 악순환이 반복되기 때문에, 곡률 계산은 고정값으로 할 수 있도록 파라미터가 존재한다.

- 
에 따라서 장애물이 가까우면 감속

- 
목표점 근처면 감속

- 
rotate to heading 상황이면 선속도보다 각속도(회전) 우선

  - 
rotate to heading: carrot이 pose와 설정된 각도 이상 차이가 나면 전진하지 않고 회전하는 파라미터
에 따라서 속도를 감속한다.
이렇게 최종적으로 계산된 속도는 선속도이고, 각속도는 아래와 같이 계산한다.
  

#### **충돌 감지!!**
**속도 계산하기**에서 계산된 속도를 가지고 충돌 감지 시뮬레이션을 돌린다!
`collision detection` 파라미터를 true로 설정하면,
`max_allowed_time_to_collision_up_to_carrot`라는 파라미터 값의 시간만큼 미래로 시뮬레이션을 돌려서
lethal obstacle(장애물 본체)에 로봇 footprint가 닿으면 제어를 멈추고 정지한다!!
시간 파라미터를 아주 크게 줘도, carrot보다 멀리 간 시뮬레이션에 대해서는 무시한다.

# Behavior Tree(BT)

#### ArUco Marker? (15695980)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15695980
**최종 수정**: v3 (2026-04-19 sync)

1. 
기준 마커

- 
일정한 포맷으로 만들어진 인공적인 랜드마크

- 
N x N 크기

- 
정사각형 형태

1. 
2차원의 비트 패턴

- 
흰색 셀과 검은색 셀의 조합

- 
마커의 고유 ID를 표현

- 
마커를 식별하는데 사용

1. 
ArUCo 마커에서 N x N이 의미하는 것

- 
2차원 비트 패턴의 크기

- 
DICT_4X4의 경우, 가로 4, 세로 4인 격자 내에서 존재할 수 있는 16개의 셀을 사용하여 마커 ID를 표현

- 
실제로는 검은색 테두리 영역까지 포함해서 6X6으로 생성

1. 
ArUCo 마커를 활용한 3차원 자세 추정

- 
이미지 내에 있는 마커를 검출

- 
4개의 코너에 대한 좌표를 구함

- 
해당 코너 좌표와 카메라 캘리브레이션을 활용하여, 카메라 좌표계 기준의 마커의 3차원 자세 추정

1. 
보통 주행에서는 아래와 같이 사용한다.

- 
**정밀도킹**

- 
절대 위치 보정

- 
구역 식별

- 
맵 기준점(anchor)

## ArUco maker를 활용한 3차원 자세 추정 알고리즘

1. 
3차원 자세 추정 알고리즘 개요

- 
ArUCo 마커 이미지 업로드

  - 
3차원 자세 추정에 사용할 ArUCo 마커의 이미지를 업로드

- 
ArUCo 마커의 유형에 대한 딕셔너리 업로드

  - 
ArUCo 마커의 유형을 딕셔너리 형태로 정의

- 
ArUCo 마커 검출에 대한 파라미터 정의

  - 
adaptiveThreshWinSizeMin

  - 
adaptiveThreshWinSizeMax

  - 
adaptiveThreshWinSizeStep

  - 
이 외에도 총 29종류의 파라미터(위 파라미터 포함) 존재

- 
ArUCo 마커 검출 수행

  - 
ArUCo 마커를 검출해서, 3차원 자세 추정에 필요한 정보인 코너 좌표를 추출

  - 
마커 검출에 필요한 핵심 기술은 칸투어(Contour)(등고선)

  - 
openCV의 cv2.aruco.detectMarkers 함수를 사용해서 구현할 수 있다.

- 
3차원 자세 추정

  - 
ArUCo 마커의 코너 좌표를 활용해서 3차원 자세를 추정

  - 
openCV의 cv2.aruco.estimatePoseSingleMarkers 함수를 사용해서 구현할 수 있다.

  - 
해당 정보는 카메라의 파라미터를 추정하는 과정인 카메라 캘리브레이션을 통해 구할수 있다.

## OpenCV를 활용한 카메라 캘리브레이션

- 
카메라 캘리브레이션 개요

  - 
‘월드(실제 세상) 좌표계’를 ‘카메라 좌표계’로 변환하기 위해 변환 행렬을 구하는 것이 카메라 캘리브레이션의 목적

- 
카메라 캘리브레이션 알고리즘의 입출력

  - 
입력

    - 
다양한 각도 및 위치에서 촬영한 체커보드 이미지 

  - 
출력

    - 
내부 카메라 행렬, 렌즈 왜곡 계수, 회전 벡터(3X1), 이동 벡터(3X1)

- 
카메라 캘리브레이션 방법

  - 
체커보드 패턴으로 월드 좌표 정의

  - 
다양한 시점에서 체커보드를 여러장 촬영

  - 
체커보드의 2D좌표 찾기

    - 
openCV 함수인 findChessboardCorners를 사용하면 2D 좌표를 구할 수 있다.

1. 
이제 코너의 좌표를 더욱 정교하게 얻기 위해 openCV의 cornerSubPix라는 함수를 통해 구할수 있다.

1. 
카메라 캘리브레이션

  1. 
openCV의 calibrateCamera함수를 통해 카메라 파라미터 정보를 받는다.

## ArUco Marker 실습

1. 
환경구성

- 
Python 가상환경

- 
필수 라이브러리 설치

1. 
실행 절차

- 
ArUco 마커 생성

  - 
입력

    - 
id는 생성할 ArUCo 마커의 ID(ex. 23)

    - 
type은 생성할 ArUCo 마커의 타입(ex. DICT_5X5_100)

    - 
output은 ArUCo 마커의 이미지를 저장할 폴더의 경로(ex. aruco_marker/)

  - 
출력

    - 
ArUCo 이미지

- 
마커 검출

  - 
입력

    - 
image는 검출하고자 하는 마커 이미지의 경로(ex. aruco_marker/test_image_1.png)

    - 
type은 검출하고자 하는 마커의 타입(ex. DICT_5X5_100)

    - 
output은 검출된 마커에 대한 이미지를 저장할 경로(ex. aruco_marker/)

  - 
출력

    - 
marker ID

    - 
중앙점

- 
카메라 캘리브레이션

  - 
준비

    - 
체커보드 출력 (A4)

    - 
7~10장 촬영 후 폴더 이동

  - 
입력

    - 
dir은 촬영한 체커보드 이미지가 들어있는 폴더(ex. calibration_checkerboard/)

    - 
width는 체커보드의 너비 픽셀 수(ex. 8)

    - 
height는 체커보드의 높이 픽셀 수(ex. 6)

    - 
square_size는 체커보드 한 셀의 실제 길이(m 단위)(ex. 0.03)

  - 
출력

    - 
calibration_matrix.npy(카메라 내부 행렬이 저장된 파일)

    - 
distortion_coefficients.npy(렌즈 왜곡 계수 값이 저장된 파일)

- 
3D Pose 추정

  - 
입력

    - 
K_Matrix는 내부 카메라 행렬에 대한 파일 경로(ex. calibration_matrix.npy)

    - 
D_Coeff는 렌즈 왜곡 계수에 대한 파일 경로(ex. distortion_coefficients.npy)

    - 
type은 검출하고자 하는 마커의 타입(ex. DICT_5X5_100)

  - 
출력

    - 
ArUCo marker의 3차원 자세

    - 
4_pose_estimation.py에서 아래의 변수에 6차원 자세 값이 저장됨

      - 
rvec:회전 벡터(3X1)

      - 
tvec:이동 벡터(3X1)

## **nav2와 같이 사용하는 방법**

- 
Nav2가 ArUco marker를 직접 사용하는 게 아니라,

  - 
아루코마커를 인식하는 노드가 만든 위치/이벤트 정보를 Nav2에 연결하는 구조

- 
Nav2 바깥에서 감지한 뒤, 그 결과를 아래에 연결하는 과정이 일반적이다.

  - 
초기 위치 보정

  - 
외부 위치 센서 융합

  - 
**도킹 전환 트리거**

  - 
**최종 정밀 제어**

    - 
nav2의 docking server

## 그래서 우리는

- 

  - 

    - 

  - 

- 

-

#### Docking Server? (16810083)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/16810083
**최종 수정**: v6 (2026-04-20 sync)

# 설명
Nav2의 설계 범위로는 해결할 수 없는 문제를 별도의 제어 계층에서 처리하기 위해서 Docking Server가 필요하다. ArUco Marker와 연계하여 에서 보다 더 정교한 위치조정이 가능하다.

# **Docking Server**
Nav2의 **Docking Server**는 자율로봇이 충전 스테이션이나 기타 도킹 스테이션에 자동으로 도킹할 수 있도록 해주는 프레임워크이다. 이 서버는 `ChargingDock`/`NonChargingDock` 플러그인을 통해 도크 인식과 충전 상태 감지 등의 로직을 캡슐화하며, 도크 데이터베이스를 이용해 여러 도킹 지점을 관리한다.

# 핵심 개념 및 구성 요소

- 
**Docking Server 노드:** Nav2 스택의 구성 요소 중 하나로, `DockRobot`/`UndockRobot` 액션 서버를 제공한니다. 로봇이 도킹을 요청하면 도크 종류와 위치를 조회하고, 스테이징(staging)* *자세로 이동한 뒤 비전 제어(vision-control) 과정을 통해 도크로 접근시킨다.

- 
**ChargingDock/NonChargingDock 플러그인:** 도크 유형별 커스텀 로직을 구현한 컴포넌트로, 도크 검출, 충전/접촉 판단 등을 수행한다. 로봇은 `sensor_msgs/JointState`, `sensor_msgs/BatteryState`, `geometry_msgs/PoseStamped` 토픽을 통해 플러그인에 정보(관절 회전, 전류, 감지된 도크 포즈)를 공급해야 한다.

- 
**도크 데이터베이스(Dock Database):** 환경에 존재하는 도킹 지점들의 목록과 각 도크 인스턴스의 좌표/타입 정보를 저장한다. 설정 파일에 도크 플러그인(예: `nova_carter_dock`)과 인스턴스(예: `home_dock`, `flex_dock1` 등)를 정의하여, 사용자는 도크 ID(`dock_id`)로 도킹 요청할 수 있다. 데이터베이스를 사용하지 않을 경우 `use_dock_id=false`로 하고, 목표 도크의 포즈(`dock_pose`)와 유형(`dock_type`)을 직접 지정해야 한다.

- 
**Nav2 내비게이터 및 컨트롤러:** 도킹 절차에서 도킹 서버는 필요 시 Nav2의 `NavigateToPose` 기능을 사용해 로봇을 스테이징 포즈로 이동시키며, 이후 제어 루프에서는 순환형 컨트롤러(spiral-based controller)로 로봇을 도킹 자세로 유도한다.

- 
**도킹 액션 API:** `DockRobot` 액션에는 도크 ID, 목표 포즈, 최대 스테이징 시간, 스테이징 여부 등 필드가 있고, 실행 결과로 `success`(성공 여부), `error_code`, `num_retries`(재시도 횟수)가 반환된다. `UndockRobot` 액션은 도킹 해제 요청을 수행하며, 성공 여부만 응답으로 준다.

# 파라미터

| 파라미터 | 예시 값 | 설명 |
|---|---|---|
``
| docking_threshold | 0.05 (m) | 도킹 포즈와의 거리 오차 한계; 이내 위치에 도달하면 도킹 완료로 간주 |
``
| staging_x_offset | -0.7 (m) | 도크 기준 스테이징 위치의 축 이동량 (뒤로 0.7m) |
``
| staging_yaw_offset | 0.10 (m) | 현재 로봇이 스테이징 근처에 이미 와 있다고 볼 허용 반경 |
``
| dock_prestaging_tolerance | 0.5 (m) | 로봇과 스테이징 포즈 간 거리 허용범위; 이내라면 바로 도킹 실행 |
``
````
| dock_backwards | false | true 시 후진 도킹, false 시 전진 도킹 |
``
``
| use_external_detection_pose | true | 외부 시각 검출 포즈 사용 여부 (true 면 Apriltag 등 사용) |
``
| use_battery_status | true | 배터리 전류 정보로 충전 상태 감지 사용 여부 |
``
| use_stall_detection | false | 관절 모터 토크(정지) 신호로 도크 접촉 감지 사용 여부 |
``
| max_retries | 3 | 도킹 재시도 최대 횟수 |
``
| initial_perception_timeout | 5.0 (s) | 최초 도크 검출 대기 시간 |
``
| undock_linear_tolerance | 0.05 (m) | 언도킹 후 목표 위치 오차 허용범위 |
``
| v_linear_min, v_linear_max | 0.15 (m/s) | 도킹 접근 시 선속도 제한 |

#### 적용 가능성 조사 Test (15892561)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15892561
**최종 수정**: v2 (2026-04-19 sync)

# 컨베이어 벨트 기술 조사

1. 
목적 : 주조 공정에서 컨베이어 벨트 시스템 적용 필요 및 가능성 조사

# 모델 스펙 

****
****
| 항목\모델명 | 데모 : 미니 CV-500 |
|---|---|
| 형식 | 우레탄 계열 수지 컨베이어 |
| 유효 길이 | 490mm |
| 유효 너비 | 90mm |
| 최고 속도 | 76mm/s |
| 가장 느린 속도 | 18mm/s |
| 최대 하중 | 5KG |
| 모터 속도 | 116RPM |
| 전압 | DC 12V |
본 평가는 **맨홀뚜껑 등 중·대형 철계 주물 생산 라인**을 가정하였다.

# 적용 가능성

- 
**적용 적합 구간**

  - 
탈형 후 검사 구간 이동

  - 
탈형 후 주물(양초)의 굳기 시작하는 온도가 50 ~ 70도

  - 
우레탄계 컨베이어 벨트 내열 온도가 100도 이내

  - 
주조 탈형 이후 공정에 적용 가능

- 
**부적합 구간**

  - 
용탕 직접 취급 구간

  - 
매우 급격한 낙하/충격이 반복되는 구간에서 일반 고무벨트 사용

# 한계 

- 
주물 크기가 80mm 이상은 컨베이어 벨트 이송 불가

- 
주물 두께가 2mm 이하는 레이저 센서 감지 불가 (레이저 센서 감지 불가로 컨베이어 벨트 제어 불가)

# 테스트 결과

****
****
****
****
| No | 항목 | 결과 | 비고 |
|---|---|---|---|
| 1 | 이송 성공률(%) | 100% (10/10) | 최대 속도 |
| 2 | 정렬 안정도 (로딩 - 주물 낙하 시험)주물이 컨베이어 벨트 중심에서 이탈 정도 | 100% (10/10)70% (10/7) | 높이 5cm높이 10cm |
| 3 | 주물 표면 손상/파손률(%) | 0% (10/0) | 높이 10cm |
| 4 | 설비 정지 횟수비전 검사 & 상위 통신 조건 | 0% (10/0)예정 | 단독 사용시연동 테스트 |
| 5 | 주물 감지 레이저 센서 테스트 | 100% (10/10) | 속도 38mm/s주물 두께 5mm |

- 
항목 2 보충 참고 이미지

# 대책(테이블 No. 2)

- 
정렬 안정도 높이기 위해 컨베이어 벨트 중심에 센터라인 표시

  - 
3D 프린터 가이드 설치를 위한 여유 공간 (1.5 cm) 이 작음. 

- 
작업자 교육 (주물 로딩시 센터라인 로딩 교육)

# 추후 작업 예정 
(비전 검사 & 상위 통신을 위한 작업) 2026/04/06 예정

- 
레이져 센서를 컨베이어 벨트에 고정 (브라켓 제작 필요)

- 
ESP32 보드에 miro-ROS 설치

#### 전체 시스템 (19988547)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/19988547
**최종 수정**: v11 (2026-04-19 sync)

- 
컨베어벨트 시스템 플로우차트는 아래와 같음
[https://dayelee313.atlassian.net/wiki/spaces/addinedute/whiteboard/20152370](https://dayelee313.atlassian.net/wiki/spaces/addinedute/whiteboard/20152370)

- 
전체 시스템을 구현할 수 있는 모의실험을 진행하였음.

- 
앞서 도출한 플로우차트를 기반으로 시스템의 동작과정을 모사하였으며, 관제 서버에서 영상데이터를 이용해 불량 여부를 판단 후 , 해당 결가를 제어보드로 전달하는 과정은 모의 관제서버에서 명령을 주면 멈춰있는 컨베이어 벨트를 5초간 구동할 수 있도록 제작.

- 
제어보드-서버 간 연결은 MQTT 프로토콜 사용

- 
클라이언트 - esp32, 브로커 - HiveMQ, 서버 - Google colab 가상환경 사용.

#### Arm_Spec_Test (7766050)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7766050
**최종 수정**: v63 (2026-04-19 sync)

## **1. 목적**

- 
시스템에 적용할 **로봇팔과 그리퍼의 성능을 평가·분석**하여, 로봇팔의 **설치 위치**와 **역할**을 **결정하기 위한 판단** 자료로 활용하고자 함.

## 2. Background 

- 
none

## **3. 연구 내용**

### 3-1. Jecotbot Robot Arm Spec

#### 3-1-1. Robot Arm Payload Test 

- 
연구 방법

  - 
Payload 측정을 위해  그리퍼에 물체를 고정한 상태로 실험 진행 (왜? 그리퍼의 파지력이 강화될 여력이 있기 때문)

    - 
파지: 물체를 잡는 행위

    - 
파지력: 물체를 놓치지 않도록 잡는 힘

  - 
생수통에 물의 양을 늘려가며 Payload를 측정

  - 
물체를 홀딩 1번 조인트(베이스)부터 6번 조인트까지 0~90도 까지 동작시키며 최대 모멘트가 걸리게끔 진행

- 
연구 결과

  - 
400g의 하중까지 모든 관절에서 정상적인 움직임이 가능

  - 
그럼** 왜** Spectification 상에서는 왜 250인가? → **엔드이펙터의 파지력이 250g이 한계**

****
****
****
| 250g | 300g | 400g |
|---|---|---|
|   |   |   |

#### **3-1-2. Robot Arm Reachability**

- 
연구 방법

  - 
로봇팔의 관절 범위에 따라 실물 조작과 을 바탕으로 작업 영역의 해를 구함

- 

  - 
모델링 툴의 바닥에 실제 시연할 공간의 그리드를 동일하게 표시 

  - 
제조사의 제품 사양서 기준 작업 반경 280mm → 그리퍼X, 기구 구조로 인해 은 매우 제한적임

    - 
자유자재 (Dextrous) 작업 영업: 엔드 이펙터가 어떤 방위(Orientation)에서도 도달할 수 있는 공간

  - 
실제 작업 반경 → 그리퍼O, 그리퍼 길이로 인해 작업 반경이 70mm 증가

  - 
실제 작업 반경은 아래의 파란색 반구 형태와 같이 베이스 좌표계 기준으로 350mm의 구를 그리나 다양한 각도로 접근 할 수 있는 영역은 한정적

- 
****
|   |
|---|
|   |   |

- 
****
| Robot Arm의 작업 반경(그리퍼O) : 실측 기반 수치 base coordinate system 기준 350mm의 작업 반경 |
|   |   |
+ 실제 map의 grid를 구현하여 비교한 모습

****
****
| CAD | Real Map |
|---|---|
|   |   |

#### **3**

##### 연구 방법 1) 5 Dots Marking Test

- 
그리퍼에 마커를 장착하여 5개의 임의의 점을 정한 후 로봇팔에 교시시킴

- 
1번 마킹 → 초기 위치 → 2번 마킹 → 초기 위치 ~~~ 5번 마킹 → 초기 위치 → 동작 종료 (3회 반복)

- 
각 회차마다 마커장착한 의 색상을 다르게 하여 반복 수행 (검정, 파랑, 빨강) 

- 
1회차에 마킹된 지점을 기준으로 2회차, 3회차 마킹 포인트와의 오차 거리를 측정

##### 연구 결과 1) 5 Dots Marking Test

- 
오차 범위는 

- 
원인은 엔드 이펙터와 마커와의 고정력이 완전하지 않아 누르는 힘에 의해 발행하는 마커의 짓눌림으로 확인

- 

****
****
****
| 1차 | 2차 | 3차 |
|---|---|---|
|   |   |   |

##### 연구 방법 2) 6 Dots 한붓그리기 실험

- 
5 Dots Marking Test과 마찬가지로 마커를 장착한 로봇팔에게 6개의 점을 정해 교시시킨 뒤 초기 위치 이동 없이 동작시켜 (ㄹ)형태의 문자를 그리도록 실험 진행

- 
각 회차마다 마커장착한 의 색상을 다르게 하여 반복 수행 (검정, 파랑, 빨강) 

##### 연구 결과 2) 6 Dots 한붓그리기 실험

- 
0.5~1.5mm 오차 확인(오차 증가)

- 
위 실험과 같은 원인(엔드 이펙터와 마커와의 고정력이 완전하지 않아 누르는 힘에 의해 발행하는 마커의 흔들림)으로 확인

- 

- 
마찬가지로 시나리오에 구현에는 충분한 정밀도

#### **3-1-3. Robot Arm DoF Test**

- 
연구 방법

  - 
모든 관절을 하나씩 동작시켜 자유도를 확인

  - 
제한되는 Orientation Case를 찾는 과정

- 
연구 결과

  - 

  - 
제한되는 Orientation Case를 표현하는 좋은 방법을 찾는 중…

****
****
****
****
****
****
****
| ​Motor no. | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| 실험 스펙 | -168~168 | -120~150 | -150~150 | -150~150 | -150~150 | -180~180 | 0~100 |
| 공식 스펙 | -168~168 | -150~150 | -150~150 | -150~150 | -150~150 | -180~180 | 0~100 |

#### **3-1-4. Mold Making - Cycle Time Test & Real Process Test**

##### 연구 방법 1) 작업 시간 확인

- 
작업 시간을 확인하기 위해 작업 유사 실험을 수행

- 
아래의 사진과 같이 Robot Arm, 패턴, 주형사틀을 배치하고 부분 시나리오 진행

- 
시나리오: 여러 

- 
초기 위치(그리퍼 Open) → 베이스 -90도 회전 → 패턴 피킹 → 그리퍼 Close → 초기 위치 → 주형사에 패턴 각인 → 초기 위치 →  베이스 -90도 회전 → 패턴 원위치 → 초기 위치

##### 연구 결과 1) 작업 시간 확인

- 
동작 사이 Delay를 1초로 하여 시연한 결과 약 40초의 Cycle Time 소요

##### 연구 방법 2) 적용 가능성 확인

- 
시연 결과로 만들어진 주형과 직접 손으로 만들어진 주형 사이의 Quality 비교

##### 연구 결과 2) 적용 가능성 확인

- 
단일 패턴과 다중 패턴으로 각각 만들어진 주형은 아래와 같음

- 
Robot Arm이 누르는 힘은 한정적 + 모래와 닿는 표면적이 넓을수록 힘 분산 → 형상 불완전

- 
****

****
****
****
****
| 실험 \ 비교군 | 패턴 형상 | 수작업 | Robot Arm |
|---|---|---|---|
| 단일 패턴(Single Pattern) |   |   |   |
| 다중 패턴(Multi Pattern) |   |   |   |

#### **3-1-5.  Pouring - Cycle Time Test & Real Process Test**
4주차에 진행 예정

- 
연구 방법

  - 
작업 시간을 확인하기 위해 작업 유사 실험을 수행

  - 
아래의 사진과 같이 Robot Arm, 도가니, 주형을 배치하고 부분 시나리오 진행

  - 
시나리오: 용탕이 들어있는 도가니를 들어 주형에 붓고 도가니를 제자리에 둔다.

  - 
초기 위치(그리퍼 Open) → 베이스 90도 회전 → 도가니 피킹 → 그리퍼 Close → 초기 위치 → 도가니를 수평으로 천천히 내림 → 주형에 주탕 → 수평을 유지하며 초기위치로 이동 →  베이스 90도 회전 → 도가니 원위치 → 초기 위치

- 
연구 결과

  - 
동작 사이 Delay를 1초로 하여 시연한 결과 약 60초의 Cycle Time 소요

## 4. 

- 
250g의 Payload를 내기위해 모터의 토크는 충분 (다중 패턴 무게 = 40g)

- 
반복 정밀도 오차 범위 0.5mm 시나리오에 반영하여 설계

- 
주형 제작(Mold Making) 가능 But 엔드 이펙터 물체 고정력 보강 필수

- 
위의 조건에 맞추어 필요한 파츠를 설계하여 시나리오에 투입

#### Robot Arm Study (13565993)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13565993
**최종 수정**: v2 (2026-04-19 sync)

- 

### 1. 로봇 '스펙' 기본 용어
로봇의 카탈로그를 볼 때 가장 먼저 나오는 핵심 단어

- 
**자유도 (Degrees of Freedom, DoF):** 로봇이 얼마나 자유롭게 움직이는지를 나타내는 '관절의 개수'입니다. 6자유도라면 사람의 팔처럼 6개의 관절이 있어 웬만한 각도는 다 잡을 수 있다는 뜻입니다.

- 
**Payload (가반 하중):** 로봇이 **최대로 들 수 있는 무게**입니다. (그리퍼 무게 + 물건 무게)

- 
**Reach (작업 반경):** 로봇 팔을 쭉 뻗었을 때 닿는 **최대 거리**입니다.

- 
**Repeatability (반복 정밀도):** 똑같은 곳으로 다시 가라고 했을 때, 얼마나 오차 없이 정확하게 가는지입니다. (스마트 팩토리에서 중요함)

- 
**Base Footprint:** 로봇의 **바닥 면적**입니다. 

### 2. 용어

- 
**Payload Test (무게 테스트):** 팔을 구부렸을 때보다 **팔을 쭉 펴고 물건을 들 때** 로봇 관절에 가장 큰 무리(**Moment**)가 갑니다. 가장 힘든 자세에서도 물건을 놓치거나 꺾이지 않는지 확인하는 겁니다.

- 
**Reachability & Orientation (도달 및 각도):** 단순히 손이 닿는 게 중요한 게 아니라, "내가 원하는 각도(Orientation)로 집을 수 있는가"가 핵심입니다. 예를 들어, 컵을 집을 때 옆에서 집어야 하는데 위에서만 닿는다면 실패인 거죠.

- 
**TCP (Tool Center Point):** 로봇 팔 끝에 달린 **그리퍼의 정중앙 지점**입니다. 모든 계산은 이 점을 기준으로 이루어집니다.

- 
**Cycle Time (작업 주기):** 물건 하나를 집어서 옮기고 돌아오는 데 걸리는 시간입니다.

- 
**Singularity (특이점):** 로봇 관절이 일직선으로 펴지거나 꼬여서 "수학적으로 계산이 안 되어 멈춰버리는 현상"입니다. 팔을 너무 쭉 펴거나 특정 각도에서 갑자기 로봇이 먹통이 될 수 있는데, 이 영역을 미리 찾아내서 피해야 합니다.

- 
**Clearance (여유 공간):** 로봇이 움직일 때 주변 장비(용광로 모형, 컨베이어)와 부딪히지 않는 최소한의 안전거리입니다.

- 
**** 작업 영역을 바둑판처럼 쪼개서 어디는 닿고(Reachable), 어디는 안 닿는지(Unreachable)를 시각화해서 로봇의 배치 장소를 결정하겠다는 뜻입니다.

#### Gripper_Spec_Test (15499335)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15499335
**최종 수정**: v4 (2026-04-19 sync)

# 목적 

# Gripper Spec

## **Gripper Holding Test**

- 
연구 방법

  - 
그리퍼의 Holding Torque를 실험

  - 
마찰력이 좋은 편인 인형과 스펀지 사이 마찰력으로 Spec 상의 홀딩 토크인 250g을 낼 수 있는지 확인

  - 
인형에 물이 담긴 생수병을 연결하여 물의 양을 달리하여 실험

- 
연구 결과

  - 
250g의 물체를 파지한 뒤 유지하는 모습을 보였지만 시간이 지남에 따라 Holding이 풀려버림

  - 
마찰계수가 조금 더 좋았다면 끝까지 유지 가능

  - 
**Jecotbot의 그리퍼의 마찰 계수를 높이던**, 잡는 물체의 **마찰 계수를 높여 **그리퍼가 물체를** 안정적으로 Hold할 수 있도록 해야함**

  - 
혹은 마찰 계수를 높여 안정적으로 Hold거나 250g보다 작은 제품으로 시연 필요

#### Gripper Upgrade (25198690)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/25198690
**최종 수정**: v6 (2026-04-19 sync)

## 1. 적재 로봇팔 그리퍼

### 1-1. 연구 목적

- 
2.5cm ~ 5cm의 물체 파지 범위를 가진 기존의 그리퍼는 용도가 매우 제한적

- 
스펀지 재질의 물체 접촉 부위는 마찰력이 낮아 파지에 부적절

### 1-2. 연구 방법

- 
얇은 주물(7.5mm)을 세로로 잡을 수 있도록 그리퍼에 보조 장치를 추가하여 파지 범위를 0 ~ 2.5cm로 바꿈

- 
접촉 부위 마찰력을 높이기 위해 미끄럼 방지 실리콘 스티커와 고무줄을 부착함

- 
적재 공정에서 사용될 슬롯형 적재함에서 로봇팔이 주물을 꺼내는 실험을 반복

### 1-3. 연구 결과

- 
랜덤하게 놓여진 3종의 주물을 100% 집어냄

****
****
| 기존 그리퍼 | Upgrade 그리퍼 |
|---|---|
|   |   |
|   |   |

## 2. 주조 로봇팔 그리퍼

### 2-1. 연구 목적

- 
주형 제작, 주탕, 탈형 모든 공정이 가능해야하나 기존 그리퍼의 범위는 탈형(주물 크기 5cm)에 부적합

- 
주물 패턴, 완성된 주물은 가볍지만 도가니 같은 비교적 무거운 물체도 들어야 하므로 충분한 마찰력이 요구됨

### 2-2. 연구 방법

- 

### 2-3. 연구 결과

#### Camera Matching (24773037)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/24773037
**최종 수정**: v3 (2026-04-19 sync)

- 
노트북에 연결된 Realsense 카메라로 지점의 위치좌표를 jetcobot에 실시간으로 전송

#### Coordinate Transformation (26443829)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26443829
**최종 수정**: v16 (2026-04-19 sync)

1. 
Robot arm Gripper 정보

- 
길이는 11cm지만 주물을 집기위해

- 
TCP의 거리는 엔드이펙터(11cm)로부터 1~1.5cm 거리(플렌지로부터 9.5 ~10cm)

- 
Robot arm 기준 +x 방향으로 플렌지와 접합되어있음

1. 
Robot arm 좌표제어 방식

- 
????에서 → mc.send_coords()에서 각 모터들의 각도정보를 내부 펌웨어로 전송 → 펌웨어에서 수신받은 각 모터정보를 기반으로 x,y,z좌표를 계산

- 
각 모터의 각도를 토대로 x,y,z값 계산, 

- 

1. 
Task에 따라 고정 그리퍼자세를 가지면서 작업

- 
물체를 집는 작업을 할 시에는 그리퍼의 자세는 아래를 향해야 함

- 
Robot arm과 유사한 높이에 있는 적재함에 주물을 적재할 때 그리퍼이 자세는 적재자리와 수평을 이루어야 함

- 
따라서 작업에 따라서 그리퍼의 자세에대한 구속이 필요함
Task 1. 이송용 핑키에 적재된 주물의 좌표위치정보를 기반으로 Robot arm의 그리퍼가 파지
Task 1.을 수행하기위해 단계적으로 제어함수를 개발
단계 1에서는 핑키에 적재된 주물의 높이 내에서 직선 거리좌표를 입력하면 
종조건

- 
1, 5, 6번 모터축은 구속시킨 상태에서(0도) 세개의 모터를 가지고 19cm 높이에 있는 물체를 그리퍼로 파지할수있는 함수를 구한다

- 
2 ,3, 4번과 그리퍼 끝단간의 거래는 그림과 같으며, 세 모터의 합이 -90도를 유지해야 한다.

- 
 
위에그림 14 → 18cm로 수정
세개의 모터의 각도범위를 지정해도 안되고, 범위로 주는게 좋음
특히 2번모터의 경우 +값이 나오면 링크간에 충돌이 발생하기 때문에, 되도록 +값이 나오지 않도록
로봇좌표확인
그리퍼 길이 확인
그리퍼 방향에따른 그리퍼 위치함수 수정

#### [실험]PostgreSQL 데이터베이스 연동 및 쿼리 실행 실험 (31260684)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31260684
**최종 수정**: v2 (2026-04-21 sync)

목적: 전송된 UID를 기반으로 실제 DB의 테이블 정보를 갱신하거나 조회.
내용: 수신된 UID가 item_table에 존재하는지 조회하고, 성공 시 after_treatment_status를 '완료(True)'로 자동 업데이트하는 로직 검증
**프로세스**
AMR이 맨홀을 가지고 후처리 구역에 도착 → 사람이 꺼내고 하차 완료 스위치를 누름 → 해당 맨홀의 태그가 출력됨 → 후처리 작업 진행 → 맨홀에 태그 부착 → 리더기에 스캔하고 컨베이어 벨트에 올림
리더기에 스캔하고 컨베이어 벨트에 올림
**CASE 1**
NFC 스티커 이용

- 
UID(NFC 스티커의 고유번호)를 읽는게 아닌 그 안의 ITEM ID를 읽어와 시리얼 통신으로 보냄
**CASE2**
바코드 이용

- 
바코드 번호 읽어서 시리얼 통신으로 보냄

#### Object Detection with YOLOv26 (7667747)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7667747
**최종 수정**: v40 (2026-04-19 sync)

# 목적 
주조 과정 자동화에서 생산 예정인 맨홀 뚜껑의 탐지

# Background 

1. 
Background: 현존 최신 YOLO 모델은 [YOLO26](https://docs.ultralytics.com/models/yolo26/)이다. YOLO는 대표적인 [단일 객체 탐지기](https://www.ultralytics.com/ko/glossary/one-stage-object-detectors)로서, [2단계 객체 탐지기](https://www.ultralytics.com/ko/glossary/two-stage-object-detectors)와 비교한다면 사용자 접근성이 쉽다. 2단계 객체 탐지기는 1. 영역 제안(1단계에서 모델이 객체가 존재할 만한 영역을 식별) 2.분류 및 식별화(CNN을 이용해 모델이 영역으로부터 특징을 추출하고 물체를 탐지)를 거치는지라 정확도는 높으나 속도가 느리다. 반면 YOLO는 단일 객체 탐지기로서 1단계 하에서 이미지가 네트워크를 통과하면서 CNN을 통해 모델이 객체의 존재와 경계상자(Bounding Box)를 예측하여 낮은 추론 지연 시간을 가진다. 정확도는 2단계 객체 탐지기와 비교해 다소 떨어지나 속도가 빠르며, 비교적 사용하기 쉽다.

1. 
조사 내용

  1. 
스펙

  1. 
적용 가능성: YOLO26 최신판을 기반으로, 5개의 항목을 중점으로 모델 시험을 해봄.

    1. 
[Detection](https://docs.ultralytics.com/datasets/detect/): 단순 이미지 분류를 넘어서, 객체의 클래스와 공간 위치(Spatial Location)을 추가로 제공하는 것.(인간, 개, 고양이든 이름이 붙는 단계)

    1. 
[Segmentation](https://docs.ultralytics.com/datasets/segment/):  탐지된 이미지 내에서 이미지를 상세하게 표현하는 기법으로, 이미지의 각각의 픽셀들을 그 픽셀이 속한 클래스로 정밀하게 재분류하는 작업이다.

    1. 
[Pose Estimation](https://docs.ultralytics.com/datasets/pose/): 객체의 물리적 방향과 인체공학적 방향 등을 추가로 포착하는 방식

    1. 
[Classification](https://docs.ultralytics.com/datasets/classify/): 전체 이미지들을 이미 포착된 객체의 클래스 중 하나로 분류하는 작업.

    1. 
[Oriented Bounding Boxes(OBB)](https://docs.ultralytics.com/datasets/obb/): 기존 Bounding Box에 기울어진 형태의 bounding box 포맷을 제공. 항공기나 선박의 탐지에 특화됨.

  1. 
한계 : Pre-trained model vs training

    1. 
Pre-trained model: 기존의 학습된 모델을 활용할 시 하드웨어 가용자원의 최소화 및 개발시간 단축이 가능하나, 원하는 목적의 개발이 불가능한(데이터셋에 포함된 객체만 제한적으로 활용가능) 수준.

    1. 
Training hierarchy

      1. 

    1. 
Training Method=> **학습 방식은 TBD(To be determined..)**

      1. 
[](https://www.ultralytics.com/ko/glossary/model-weights) 사전 학습된 가중치 없이 무작위 가중치로 모델을 초기화하고 YAML 설정 파일을 사용하여 사용자 지정 데이터 세트로 처음부터 학습시키는 걸 의미. 가장 시간이 많이 소요됨.

      1. 
[Transfer Learning(전이학습)](https://www.ultralytics.com/ko/glossary/transfer-learning): 전이학습은 특정 작업을 위해 개발된 모델을 비슷하거나 연관된 다른 작업에 응용하기 위해 활용하는 방식. 기존 도메인으로부터 학습된 데이터를 활용하여 커스텀 데이터셋 학습 시 주로 사용되는 방법.

        1. 
[Fine-tuning(미세조정)](https://docs.ultralytics.com/guides/model-evaluation-insights/#accessing-yolo26-metrics): 전이학습의 하위 분야(Parent: 전이학습, Child: 미세조정)로, 사전 학습된 모델을 기반으로 특정 데이터셋을 활용하는 것은 동일하나 모델의 가중치(Weight)를 미세하게 조정하는 방법이 추가된다. [전체 모델 미세조정 혹은 효율적 미세조정](https://wikidocs.net/120208) 중 선택할 수 있으며 가용 자원을 고려하면 후자도 추천된다. 특히 LoRA는 효율적 미세조정의 대표적인 사례로 상대적으로 적은 자원으로도 파인 튜닝이 가능한 장점이 있다.

    1. 
학습 소요 시간 추정: 전이학습이 제일 적게, 미세조정은 중간, Training 는 것으로 추정.

# 실험 

1. 
장비: 

  1. 
Jetcobot 보드: Raspberry pi 5 (Ram: 8GB)

  1. 
Pinkybot 보드: Raspberry pi 4 (Ram: 4GB)

  1. 
Laptop: RTX 4060 (VRAM: 8GB), RAM 16GB

1. 
맵/레이아웃

1. 
입력 데이터 :

1. 
측정 기준

1. 
**평가 지표 => Draft(초안)**

  1. 
**정의 : 모델 훈련에 앞서, YOLO의 최신 모델 YOLO26의 에 기반한 5개의 모델에 이미지와 영상을 테스트해본다.**

  1. 
**각 평가 지표 의미: 먼저 항목의 사항을 이미지와 영상에 테스트해봄으로서 작동 유무를 파악한다. 여기서 작동이 원활하지 않은 방식은 이후 훈련 방식을 거칠 경우에도 원활하지 않을거라 가설을 세운다.(변경 가능)**

# 결과 

## **실험 1. YOLO26의 목표별 모델의 정성적 성능 평가  **
****[****](https://docs.ultralytics.com/datasets/detect/coco/)
특징: 다양한 객체 범주에 대한 연구에 최적화되어 있으며, 80개의 객체 class가 있어 범용적인 객체 탐지에 유용하다. 모델 성능 비교에 자주 쓰이는 데이터셋이기도 하다.
**에 대해 yolo26n(Detection), yolo26n-seg(Segmentation), yolo26n-cls(Classification), yolo26n-pose(Pose Estimation), yolo26n-obb(Oriented Bounding Boxes)의 모델을 적용해보고 그 전후의 이미지들을 바탕으로 각 모델의 정의와 기능에 부합하는지 정성적 판단을 한다. **

****
****
****
****
****
| model | Purpose | Params(M) | Result(Quality) | Comment |
|---|---|---|---|---|
| Original image |   |   |   |   |
| yolo26n | Detection | 2.4 |   | detection |
| yolo26n-seg | Segmentation | 2.4 |   | detection with segmentation |
| yolo26n-cls | Classification | 2.4 |   | yolo26n or yolo26n-seg seems enough |
| yolo26n-pose | Pose Estimation | 2.4 |   | Not feasible for manhole |
| yolo26n-obb | Oriented Bounding Box | 2.4 |   | Not feasible for manhole |
해당 코드로 구현 가능

## 실험 2. YOLO26의 webcam test
webcam port check command: 
webcam  포트 번호 확인
해당 코드로 YOLO26의 각 모델을 Webcam 으로 테스트할수 있다.
실험결과
 
 

#  
주조 과정 자동화에서 생산 예정인 맨홀 뚜껑을 탐지할 수 있는 객체 탐지 방법을 조사하였고, 사용자 접근성과 속도를 고려하여 단일 객체 탐지 방식인 YOLO26를 사용할 예정이다. YOLO로는 Detection, Segmentation, Pose Estimation, Classification, Oriented Bounding Boxes(OBB) 등의 다양한 비전 task를 수행할 수 있는데, 이번 조사에서는 이를 범용적 데이터셋인 COCO 데이터셋을 이용하여 Ultralytics의 예시 사진에 검증해보았다. 그 결과는 **실험 1**의 표를 통해 각 task별 정성평가를, **실험 2**를 통해 Webcam에 대해서도 YOLO의 성능을 검증해 보았으며, 기본적인 Detection 성능이 충분하다고 판단된다. 그러나 **Background**의 **2.c.한계** 항목에서 정리했듯이, 기존 데이터셋에 없는 객체에 대해서는 학습을 진행해야 하는데, 이 경우는 사전 학습된 가중치에서부터 시작하는 것이 유리하다(ex: 파인튜닝 중 적은 자원으로도 가능한 LoRA). 맨홀 뚜껑 샘플의 추후 학습과정에 있어서도 YOLO의 학습방법 중 사전 학습된 가중치에서 시작된 방법들 중 고민하는 것이 더 유리할 것으로 판단된다. 

# 참고 문헌

1. 
[https://universe.roboflow.com/create-dataset-for-yolo/manhole-cover-dataset-yolo/](https://universe.roboflow.com/create-dataset-for-yolo/manhole-cover-dataset-yolo/) 

1. 
[https://universe.roboflow.com/sideseeing/manhole-cover-dataset-yolo-62sri](https://universe.roboflow.com/sideseeing/manhole-cover-dataset-yolo-62sri) 

1. 
[https://universe.roboflow.com/tugas-akhir-icad/proyek-akhir-icad](https://universe.roboflow.com/tugas-akhir-icad/proyek-akhir-icad)

#### Pixel coordinate extraction from Image and Video with Yolov26 (10125323)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/10125323
**최종 수정**: v31 (2026-04-19 sync)

# 목적
YOLO로 객체를 탐지하기 위해 훈련을 거친 뒤(ex: Fine tuning) 모델이 추론한 결과값들을  Robot arm과 동기화를 위해 필요한 데이터 값(좌표, Class confidence)들을 추출해낸다.

# Background:
(있다면) 기존 baseline 모델이나 연구 주제에 대한 간략한 정리

# 평가 지표

1. 
평가 지표: 

  1. 
Class ID(숫자), Class name(어떤 객체인가), Confidence score, Bounding Box의 정규화된 좌표값(x center, y center, width, height), Bounding Box의 객체별 pixel(x center, y center, width, height, x min, y min, x max, y max), CPU, RAM, GPU, GPU RAM: Percentage from 0 to 100%, 전체 용량 대비 사용량.

1. 
정의 :  

  1. 
Class ID(숫자): 객체의 고유 식별 번호. YOLO 모델이 학습할 때 각 객체 유형에 부여한 숫자.

  1. 
Class name(어떤 객체인가): 검출된 객체의 유형을 사람이 읽을 수 있는 텍스트로 변환. 예: "person", "bus", "chair" 등.

  1. 
Confidence score: 모델이 해당 객체가 정확하다고 판단하는 확신 정도를 0에서 1 사이의 값으로 나타낸 것

  1. 
Bounding Box의 정규화된 좌표값(x center, y center, width, height): 이미지 크기에 관계없이 0에서 1 사이의 값으로 표현된 좌표. 카메라 해상도나 이미지 크기가 변경되어도 동일한 비율을 유지하므로 로봇 팔 제어에 적합.

    1. 
**x_center**: 바운딩 박스 중심점의 x 좌표 (0=이미지 왼쪽 가장자리, 1=이미지 오른쪽 가장자리)

    1. 
**y_center**: 바운딩 박스 중심점의 y 좌표 (0=이미지 위쪽 가장자리, 1=이미지 아래쪽 가장자리)

    1. 
**width**: 바운딩 박스의 너비 (이미지 전체 너비 대비 비율)

    1. 
**height**: 바운딩 박스의 높이 (이미지 전체 높이 대비 비율)

  1. 
Bounding Box의 객체별 pixel(x center, y center, width, height, x min, y min, x max, y max): 이미지 내 실제 픽셀 단위로 표현된 좌표값. 이 값들은 이미지 내에서 객체의 절대적인 위치와 크기를 나타냄. 실제 이미지 상의 절대 위치를 알 수 있어 시각화나 디버깅에 유용.

    1. 
**x_center**: 바운딩 박스 중심점의 x 좌표 (픽셀 단위)

    1. 
**y_center**: 바운딩 박스 중심점의 y 좌표 (픽셀 단위)

    1. 
**width**: 바운딩 박스의 너비 (픽셀 단위)

    1. 
**height**: 바운딩 박스의 높이 (픽셀 단위)

    1. 
**x_min**: 바운딩 박스의 왼쪽 위 모서리 x 좌표

    1. 
**y_min**: 바운딩 박스의 왼쪽 위 모서리 y 좌표

    1. 
**x_max**: 바운딩 박스의 오른쪽 아래 모서리 x 좌표

    1. 
**y_max**: 바운딩 박스의 오른쪽 아래 모서리 y 좌표

  1. 
CPU, RAM, GPU, GPU RAM: 각 사용량에 대한 비율(%)

1. 
각 평가 지표가 어떤 것을 의미하는지 설명

  1. 
Class ID(숫자): number

  1. 
Class name(어떤 객체인가): name(person, bus, etc…)

  1. 
Confidence score: 1에 가까울수록 정확함. 0에 가까울수록 부정확.

  1. 
Bounding Box의 정규화된 좌표값(x center, y center, width, height): 0과 1 사이의 상대값.

  1. 
Bounding Box의 객체별 pixel(x center, y center, width, height, x min, y min, x max, y max): pixel unit.

  1. 
CPU, RAM, GPU, GPU RAM: 각 사용량에 대한 비율(%)

# 실험 및 결과 

## 실험 1 : pixel coordinate extraction with Image 

1. 
실험 1 내용: YOLO26n(최소 경량화) 모델을 기반으로 이미지 파일을 YOLO로 탐지하고, 이에 대한 모델 추론 결과 및 자원 사용량을 도출해냈다. (pixel coordinate extraction)

  1. 

## 실험 2 Pixel coordinate extraction with Video

1. 
해당 YOLO를 영상 파일에도 확장시켜 봄. => 프레임 별 객체의 정보 및 영상의 객체편집 후 소모자원 표기.

1. 
[https://drive.google.com/file/d/155stjWK3vVeTWB_A4apsdhYnI_s9Yd-o/view?usp=drive_link](https://drive.google.com/file/d/155stjWK3vVeTWB_A4apsdhYnI_s9Yd-o/view?usp=drive_link) 

## 실험 3 Pixel coordinate extraction with Video Streaming 

1. 
실험 3 내용: 해당 기능을 video streaming에 확장. Camera가 촬영한 video는 이미지와 달리 매 순간을 포착하기 보다는 원할때 스냅샷(press s key)을 찍고, 그 순간 탐지된 객체들의 json 파일 및 소요 자원을 파악함.

# Source Codes 

# 우리 프로젝트 적용 판단

1. 
채택/보류/제외 기준

1. 
우리 프로젝트 적용 판단 (아래는 예시)

  1. 
어느 공정에 넣을지

  1. 
실시간 가능 여부

  1. 
추가 하드웨어 필요 여부

  1. 
데이터 수집 필요량

#### Position coordinates extraction from our Dataset (11927712)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11927712
**최종 수정**: v60 (2026-04-19 sync)

# 목적
Conveyor 벨트에 Manhole 목업 샘플을 배치한 뒤, 이들이 기존의 YOLO26의 pre-trained 데이터셋을 활용할 경우 최대한 어떤 유사한 class를 탐지할 수 있는지 파악하고, 이 경우 bounding box의 정보 및 HW 소요자원 정보를 읽어올 수 있는지 파악한다.
[전제조건] YOLO26의 default dataset(COCO) 사용, 학습과정을 거치지 않은 Manhole 목업 샘플 탐지.
=>추후에는 학습예정.

# Background:
보통 인공지능 업계에서는 특정 모델에 의해 훈련되지 않은 객체가 그 모델의 dataset에 의해 유사한 물체로 탐지되는 경우를 Hallucination(환각), [Out-of-distribution](https://briana-ai.tistory.com/39)(OOD) Detection(학습되지 않은 데이터 분포가 AI모델에 입력되는 현상)이라 하며, 이를 걸러내는 작업이 일반적이다. 그러나 여기서는 이를 역이용하여, 훈련 이전의 상황에서도 환각에 의해 탐지되는 물체 역시 기존의 dataset 물체와 같이 해당 bounding box 좌표값 및 픽셀값을 얻어올 수 있는지를 파악하고, 이러한 방법을 추후 학습을 거친 manhole 샘플에 적용해 bounding box의 정보(Class name, Confidence Score, 정규화된 좌표값(x_center, y_center, width, height), 픽셀의 좌표값(x_center, y_center, width, height, x_min, y_min, x_max, y_max) 및 HW 소요자원을 탐지할 수 있다고 추정된다.

# 조사 내용

1. 
스펙

1. 
적용 가능성: 보통 인공지능 업계에서는 특정 모델에 의해 훈련되지 않은 객체가 그 모델의 dataset에 의해 유사한 물체로 탐지되는 경우를 Hallucination(환각), [Out-of-distribution](https://briana-ai.tistory.com/39)(OoD) Detection(학습되지 않은 데이터 분포가 AI모델에 입력되는 현상)이라 하며, 이를 걸러내는 작업이 일반적이다. 그러나 여기서는 이를 역이용하여, 훈련 이전의 상황에서도 환각에 의해 탐지되는 물체 역시 기존의 dataset 물체와 같이 해당 bounding box 좌표값 및 픽셀값을 얻어올 수 있는지를 파악하고, 이러한 방법을 추후 학습을 거친 manhole 샘플에 적용해 bounding box의 정보 및 HW 소요자원을 탐지할 수 있다고 추정된다.

1. 
한계: 실제 Manhole샘플로 Fine Tuning을 할 경우에는, 논문에 나오는 대로 목표 객체 외의 객체들에 대해 OoD Detection을 최소화할 수 있는지는 실제 실험을 해봐야 알 수 있다.

1. 
대안: 

1. 
실험 환경

  1. 
장비: Webcam, Laptop(RTX 4060)

  1. 
측정 기준: Webcam으로 YOLO객체를 탐지하고, YOLO의 연산은 Laptop에서 수행.

# Hyperparamter 

1. 
Hyperparamter: YOLO26 parameter, Distance, Contrast, Surface, Resolution, Similarity between dataset and object

  1. 
Parameter: YOLO 모델의 **크기(용량)** 를 나타내는 숫자로, 모델이 학습하는 **가중치(weight)의 총 개수**

  1. 
Distance: 카메라와 manhole 샘플간의 수직 거리

  1. 
Contrast: manhole 샘플과 주위 사물간의 색채 대비

  1. 
Surface: manhole 샘플의 앞면(패턴 모양)과 뒷면(평평)

  1. 
Resolution: 카메라 해상도

1. 
Hyperparameter 의미 설명

  1. 
Parameter: 어떤 모델이 더 최적일까(낮은 파라미터: 속도 우위, 높은 파라미터: 성능 우위)

  1. 
Distance: 거리가 너무 멀어도, 너무 가까워도 객체 탐지가 잘 안됨. 최적의 거리를 찾아야 함.

  1. 
Contrast: 샘플과 주위 환경간의 색채 대비는 YOLO객체에 어떤 영향을 미칠지 판단.

  1. 
Surface: 패턴이 새겨진 앞면과 평평한 뒷면의 경우에는 객체 탐지에 어떤 영향이 있을까?

  1. 
Resolution: 카메라 해상도는 HD(1280 * 720)으로.

# 실험 및 결과 

## 실험 1 내용 + 결과: (YOLO26n: parameters: 2.4M, 카메라 해상도: 1280 * 720)

****
****
****
****
****
****
****
| Factor | Parameters | Result(photo) | Result(환각 Class) | Bounding Box 정보(json) | H/W 소요자원(CPU, GPU, 램) | 참고자료 |
|---|---|---|---|---|---|---|
| Distance(거리) | Long(Approx. 20cm) |   | N/A | N/A | CPU: 4%RAM: 69%GPU: 7% | 주물 샘플(3D 프린터) |
|   | Short(Approx. 15cm) |   | N/A | N/A | CPU: 4%RAM: 70%GPU: 7% | 주물 샘플(3D 프린터) |
| Contrast(대비) | 비슷한 색상의 물체와 대비 |   | N/A | N/A | CPU: 4%RAM: 70%GPU: 7% | 주물 샘플(3D 프린터) |
|   | 대립된 색상의 물체와 대비 |   | N/A | N/A | CPU: 4%RAM: 70%GPU: 6% | 주물 샘플(3D 프린터) |
| Surface(표면) | 정면 |   | N/A | N/A | CPU: 8%RAM: 69%GPU: 7% | 주물 샘플(3D 프린터) |
|   | 후면 |   | mouse |   | CPU: 4%RAM: 69%GPU: 7% | 주물 샘플(3D 프린터) |
| variable shape | 정면 |   | mouse | N/A | CPU: 4%RAM: 72%GPU: 7% | 주물 샘플(3D 프린터) |
|   | 후면 |   | mouse |   | CPU: 4%RAM: 72%GPU: 7% | 주물 샘플(3D 프린터) |

## 실험 2 내용 + 결과(YOLO26x: parameters: 55.7M, 카메라 해상도: 1280 * 720)

****
****
****
****
****
****
****
| Factor | Parameters | Result(photo) | Result(환각 Class) | Bounding Box 정보(json) | H/W 소요자원(CPU, GPU, 램) | 참고자료 |
|---|---|---|---|---|---|---|
| Distance(거리) | Long(Approx. 20cm) |   | cake |   | CPU: 6%RAM: 64%GPU: 22% | 주물 샘플(양초) |
|   | Short(Approx. 15cm) |   | bowl, oven |   | CPU: 4%RAM: 64%GPU: 22% | 주물 샘플(양초) |
| Contrast(대비) | 비슷한 색상의 물체와 대비 |   | N/A | N/A | CPU: 4%RAM: 67%GPU: 22% | 주물 샘플(3D 프린터) |
|   | 대립된 색상의 물체와 대비 |   | N/A | N/A | CPU: 4%RAM: 68%GPU: 20% | 주형 샘플(3D 프린터) |
| Surface(표면) | 정면 |   | N/A | N/A | CPU: 4%RAM: 68%GPU: 22% | 주형 샘플(3D 프린터) |
|   | 후면 |   | mouse |   | CPU: 9%RAM: 68%GPU: 22% | 주형 샘플(3D 프린터) |
| variable shape | 정면 |   | N/A | N/A | CPU: 4%RAM: 72%GPU: 21% | 주형 샘플(3D 프린터) |
|   | 후면 |   | mouse |   | CPU: 8%RAM: 72%GPU: 22% | 주형 샘플(3D 프린터) |

# **결론**
파인튜닝이나 전이학습을 하지 않은 이상, 학습되지 않은 맨홀 샘플에 대해서는 기존 COCO 데이터셋으로는 직접적인 탐지는 어렵다. 그러나 실험 결과, 비슷한 모양의 물체(mouse, cake) 등에 대해서는 일종의 OoD현상을 제한적으로 보이며, 이 경우에는 기존의 훈련된 모델들과 같이 동일한 형식의 관측 데이터 포맷을 보여줌을 알수 있다(bounding box의 정보(Class name, Confidence Score, 정규화된 좌표값(x_center, y_center, width, height), 픽셀의 좌표값(x_center, y_center, width, height, x_min, y_min, x_max, y_max). 또한, 맨홀 샘플의 정면과 후면의 표면 처리에 따라 다양한 관측 결과를 보여줌으로서, 향후 파인튜닝이나 전이학습 시에 객체의 모양 뿐만 아니라 표면의 상태도 학습에서 고려요소임을 알 수 있다. 
추가 기술자료:

- 
[Revisiting Out-of-Distribution Detection in Real-time Object Detection: From Benchmark Pitfalls to a New Mitigation Paradigm ](https://arxiv.org/pdf/2503.07330)

  - 
특히 이 논문에서는 Out-of-Distortion(OoD)현상(객체가 기존 데이터셋과 다른 물체를 기존 데이터셋과 비슷한 물체로 착각하는 현상)을 Fine-tuning을 통해 최소화한 근거를 제시함(Fig. 11)으로서, 향후 Fine-tuning을 통해 Manhole모델을 학습시 OoD현상을 최소화할 수 있는 방안 중 하나를 제시해주는 의미가 있음.

# 우리 프로젝트 적용 판단

1. 
채택/보류/제외 기준

1. 
우리 프로젝트 적용 판단 (아래는 예시)

  1. 
어느 공정에 넣을지

  1. 
실시간 가능 여부

  1. 
추가 하드웨어 필요 여부

  1. 
데이터 수집 필요량

#### Camera Calibration를 통한 좌표 변환 (12714104)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/12714104
**최종 수정**: v32 (2026-04-19 sync)

# 목적
YOLO의 Bounding Box 픽셀 값들을 실제 세계의 수치 값(미터)과 매칭해야 한다. 실제 manhole mockup 샘플을 이용해 camera intrinsic parameter 보정 (calibration)을 통해 real-world coordinates로 기하학적 변환을 한다. 

# Background 

## 좌표계 정리

| 좌표계 | 표기 | 단위 | 설명 | 예시 |
|---|---|---|---|---|
****
``
``
| 이미지 좌표계 | (u, v) | 픽셀 (px) | 이미지 왼쪽 상단이 원점. 우측/하단으로 증가 | YOLO 출력: bbox_center = (320, 240) |
****
``
****
``
| 카메라 좌표계 | (Xc, Yc, Zc) | 미터 (m) 또는 mm | 카메라 광학 중심이 원점. 광축 방향이 +Z | 깊이 d=0.5m일 때, 3D 공간상의 점 |
****
````
| 월드/로봇 좌표계 | (Xw, Yw, Zw) 또는 (Xr, Yr, Zr) | mm | 작업대 모서리 또는 로봇 베이스가 원점 | 로봇이 이동해야 할 실제 목표 위치 |

## 내부 파라미터 (Intrinsic): 카메라의 "스펙"
카메라가 3D 공간을 2D 이미지로 투영하는 방식을 정의함. 3×3 행렬 `K` 로 표현.

| 파라미터 | 물리적 의미 | 단위 | 혼동 주의점 |
|---|---|---|---|
``****``
****
``
``
| fx, fy | 초점거리의 픽셀 환산값 | 픽셀 (px) | ❌ 실제 초점거리 f(mm) 와 다름!✅ fx = f(mm) × 이미지폭(px) / 센서폭(mm) |
``****``
``
| Cx, Cy | 주점 (Principal Point): 광축이 이미지와 만나는 점 | 픽셀 (px) | ❌ 항상 이미지 중심 (W/2, H/2) 이 아님!✅ 제조 오차로 약간 벗어날 수 있음 |

## 외부 파라미터 (Extrinsic): 카메라의 "위치/자세"
카메라 좌표계 → 월드 좌표계 변환을 정의합니다. 회전** **`R`(3×3)로 구성:

| 파라미터 | 의미 | 단위 | 프로젝트에서의 역할 |
|---|---|---|---|
``
| R (Rotation) | 카메라가 월드 기준 어떻게 회전했나 | 라디안 (또는 쿼터니언) | 카메라가 기울어지면 2D 좌표도 왜곡됨 → 보정 필요 |
``
| t (Translation) | 카메라 원점의 월드 좌표 | mm 또는 m | "카메라가 로봇 베이스에서 300mm 위에 있다" 같은 정보 |

## **Homographic transformation(호모그래피 변환)**
투영 변환(Projective Transformation)이라고도 부르며, 한 평면의 점들을 다른 평면의 점들로 매핑하는 기하학적 변환으로, 픽셀과 실제 좌표간의 변환을 하나의 행렬로 간단히 계산할 수 있게 한다. 
대표 함수: `cv2.findHomography`

## 좌표 변환 공식 (With Homography Matrix)

# 실험 결과

## 실험 1: 카메라 Intrinsic parameter
카메라 보정을 통해 카메라 내부 파라미터  얻는 것을 목표로 한다. 
과정은 다음과 같다. 

- 
체커보드 패턴 출력

- 
여러 각도/위치에서 15~20장 촬영

  - 
[https://dayelee313.atlassian.net/wiki/spaces/753667/pages/15042271/?draftShareId=522962a6-232b-4aae-8dd2-1eb3d2466eea](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/15042271/?draftShareId=522962a6-232b-4aae-8dd2-1eb3d2466eea)

- 
OpenCV `calibrateCamera()` 사용
얻은 **cameraMatrx**와 **disCoeffs** 값으로 렌즈 왜곡 보정이 가능하고, focal length를 포함한 내부 파라미터 확보 가능하다. 해당 단계 →  ground truth 임. 

## 실험 2: 카메라 Extrinsic parameter
카메라 보정을 통해 카메라 외부 파라미터(회전 벡터, 이동 벡터) 얻는 것을 목표로 한다. 
과정은 다음과 같다.

- 
실험 1에서 얻은 내부 파라미터 값을 불러온다.

- 
원하는 위치로 카메라를 이동시킨 뒤, Intrinsic 보정에 활용한 체스 보드를 촬영한다.
결과값:  
얻은 결과값을 바탕으로 카메라의 위치와 자세를 파악할 수 있다.

## 실험 3: 실제 좌표 변환 정확도 평가
위의 방법에서 1번 스텝 →  ground truth 임. 
2D와 3D 간의 객체 변환:  

# 카메라 설치 환경 

### 카메라 Spec
카메라 모델명: 로지텍 C920 HD Pro Webcam
Spec: [링크](https://www.logitech.com/en-ch/shop/p/c920-pro-hd-webcam)

- 
**Max Resolution**: 1080 p/30 fps - 720p/ 30 fps

- 
**Camera mega pixel**: 3

- 
**Focus type**: Autofocus

- 
**Lens type**: Glass

- 
**Built-in mic**: Stereo

- 
**Mic range**: Up to 1 m

- 
**Diagonal field of view (dFoV)**: 78°

- 
**Tripod-ready universal mounting clip fits laptops, LCD or monitors**

###  카메라 설치 방법 ->변동 가능

| 항목 | 조건 |
|---|---|
****
| 카메라 종류 | 단안(Monocular) 카메라 |
****
****
| 설치 각도 | 90도 (수직 하향) - 천장이나 높은 곳에서 바닥을 수직으로 내려다봄 |
****
****
| 카메라 높이 | 자로 직접 측정 가능 (cm) |
****
| 촬영 대상 | 바닥면 위에 놓인 객체들 |

1. 
**카메라 각도 = 90도** (바닥면을 수직으로 내려다봄)

1. 
**카메라 높이 H를 자로 직접 측정** 가능

1. 
**바닥면은 평평함**

1. 
****
****립.

## 바닥 기준면 

- 
바닥이나 작업 테이블 위에 **기준 평면** 확보

- 
 본 실험에서는 체커보드를 사용하였다. 

## 기준 물체

- 
크기를 아는 맨홀 mockup 이용

  - 
디자인 spec:두께 5mm, Radius 2.5 cm

  - 
실제 spec: 두께 7.5mm, Radius 2.5 cm

#### Chessboard image dataset for calibration on Intrinsic parameters (15042271)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15042271
**최종 수정**: v7 (2026-04-19 sync)

# Chessboard 정보
체스보드 내부 코너 수: 가로 9칸, 세로 7칸
체스보드 내 정사각형 한 변의 길이: 28.7mm

# Image dataset
총 이미지 수: 53장.

# 카메라 보정 정보
보정 일시: 2026-04-06 18:52:03
사용한 이미지 수: 53장
체스보드 크기: 8x6
정사각형 크기: 28.7mm
===== 내부 파라미터 =====
fx: 634.904, fy: 635.294
cx: 331.361, cy: 231.250
===== 왜곡 계수 =====
k1: 0.068245, k2: -0.367761
p1: -0.002421, p2: 0.001096
k3: 0.459561
===== 재투영 오차 =====
평균 오차: 0.0265 픽셀

# 원본(좌) vs 왜곡보정 이미지(우)

# 활용된 알고리즘

| 단계 | 알고리즘/기술 | 설명 |
|---|---|---|
****
``
| 코너 검출 | cv2.findChessboardCorners() | 체커보드 패턴의 내부 코너 검출 (Zhang의 방법) |
****
``
| 서브픽셀 정밀도 | cv2.cornerSubPix() | 코너 위치를 서브픽셀 수준으로 정밀화 |
****
``
****
| 카메라 보정 | cv2.calibrateCamera() | Zhang의 카메라 보정 알고리즘 (1999년 논문) |
****
``
| 재투영 오차 | cv2.projectPoints() | 보정 결과의 정확도 평가 |

# Source Code

#### Chessboard image data for calibration on Extransic parameters (15042386)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15042386
**최종 수정**: v8 (2026-04-19 sync)

# Chessboard 정보
  와 동일.

# Image data

# 카메라 보정 정보
===== 외부 파라미터 추정 중 =====
체커보드 세계 좌표 범위:
  X: 0 ~ 0.230 m
  Y: 0 ~ 0.172 m
  Z: 0 m (바닥 평면)
✅ 외부 파라미터 추정 성공!
회전 벡터 (rvec): [ 0.01828119 -0.02303896 -0.00569356]
이동 벡터 (tvec): [-0.10748796 -0.07063441  0.30707854]
카메라 위치 (세계 좌표계):
  X: 0.100 m
  Y: 0.066 m
  Z: -0.311 m
⚠️ 참고: 카메라 Z좌표가 음수입니다.
   이는 카메라가 바닥 아래에 있는 것으로 계산된 것입니다.
   실제 거리 계산 시 절대값을 사용합니다.
📏 실제 카메라 높이 (절대값): 0.311 m

# 활용된 알고리즘

| 단계 | 알고리즘/기술 | 설명 |
|---|---|---|
****
``
| 체커보드 코너 검출 | cv2.findChessboardCorners() | intrinsic과 동일 |
****
``
****
| PnP 문제 해결 | cv2.solvePnP() | Perspective-n-Point 알고리즘 |
****
``
| 회전 벡터 변환 | cv2.Rodrigues() | 회전 벡터 ↔ 회전 행렬 변환 |
****
``
| 재투영 검증 | cv2.projectPoints() | 보정 정확도 확인 |

# Source Code

#### Calibrated Monocular 2D-to-3D Object Localization (16449726)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/16449726
**최종 수정**: v7 (2026-04-19 sync)

# 목적
 ,   에서 도출된, 체스보드를 활용한 카메라의 Intrinsic, Extransic 파라미터들을 보정하고, 이를 기반으로 3D 객체의 bounding box의 파라미터 값들을 2D 이미지에 표현해줄 수 있다.

# 실험결과 이미지

# 실험결과 이미지

# 활용된 알고리즘

| 단계 | 알고리즘/기술 | 설명 |
|---|---|---|
****
| 객체 탐지 | YOLO (Ultralytics) | 2D 바운딩 박스 검출 |
****
``
| 왜곡 보정 | cv2.undistortPoints() | 렌즈 왜곡 제거 |
****
****
| 광선-평면 교차 | Ray-Plane Intersection | 픽셀 → 3D 세계 좌표 변환 |
****
``
| PnP 업데이트 | cv2.solvePnP() (동적) | 실시간 외부 파라미터 갱신 |

# Source Code

#### Suggestion for the purpose of YOLO (18907191)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/18907191
**최종 수정**: v2 (2026-04-19 sync)

현재 YOLO 진행 방향: 

1. 
**카메라 각도 = 90도** (바닥면을 수직으로 내려다봄)

1. 
**카메라 높이 H를 자로 직접 측정** 가능

1. 
**바닥면은 평평함**

1. 
**이미지 평면은 바닥면과 평행함**
의 조건에서 단안카메라를 이용하여 카메라의 Intrinsic, Extrinsic 파라미터를 보정하고, 이를 통합하여 고정된 높이에서 YOLO의 이미지 픽셀값과 실제 객체의 크기 값을 실시간으로 볼 수 있게 한다.
수정 제안 방향:
(강사들 피드백 고려) YOLO는 객체인식을 위한 것으로, 단안카메라로는 깊이를 알기에는 다소 기술적 난이도가 있음(Depth Camera나 Stereo Camera를 활용해야). 높이를 고정시켜서 Calibration을 진행하면 단안카메라로도 가능해서 이를 통해 카메라와 객체의 측정 거리 검증, 객체의 크기값 추출 등을 시도해보았으나, 현재 결과는 오차가 큼. 이 경우는 추가 장비에 대해 기술조사를 하거나, 혹은 YOLO를 높이나 객체 크기 값이 아닌 Bounding Box의 Class, 위치정보 파악 용도로 활용하고, 이를 Robot에 좌표값을 전달하는 방향으로 진행하는 경우가 추천됨. 
이 경우는 거리값, 객체 크기가 아닌 객체의 좌표값을 구하는 과정이므로 기존의 Calibration 자료를 최대한 활용하면서 가능하며, 향후 미세조정이나 전이학습을 통해 학습된 맨홀 샘플 bounding box의 좌표값 및 class confidence에도 적용 가능할거라 추정된다.

#### HW resource estimation solely on YOLO usage (18645142)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/18645142
**최종 수정**: v1 (2026-04-19 sync)

## 실험목적
측정 H/W 자원: CPU, RAM, GPU
시에 YOLO 프로그램만의 HW자원 소모량을 추가로 계산하는 기능을 더함.

## 실험결과 예시

## Source Code

#### Segmentation with SAM2 (7962627)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7962627
**최종 수정**: v15 (2026-04-19 sync)

## 목적

- 
SAM2 사용 가능성 검증

## Background

- 
SAM2: 이미지 + prompt를 넣으면 `객체 마스크`를 만들어주는 모델

  - 
Prompt (Optional Parameter, 답에 대한 힌트를 알려주는 것으로 생각하면 됨)

    - 
점 (Point): 좌표 + 라벨로 입력하며, 해당 좌표가 객체 안에 있는지 밖에 있는지 모델에게 알려줌

    - 
박스 (Box):  bbox 형태(`[x_min, y_min, x_max, y_max]`)로 입력. 객체 위치를 모델에게 알려줌

    - 
마스크 (Mask): 이전 마스크(`numpy.ndarray`)를 그대로 입력. 객체의 형태를 모델에게 알려줌

  - 
Training dataset: [SA-V Dataset](https://ai.meta.com/datasets/segment-anything-video/)

- 
**장점**: 특정 도메인에 한정되지 않고 어떤 객체든 분할할 수 있음

  - 
학습 데이터 규모

    - 
SA-1B

      - 
1100만장 이미지, 11억개 마스크, 다양한 도메인 포함

    - 
SA-V(비디오)

      - 
5만개 비디오, 64만개 마스크, 다양한 객체 움직임 포함

  - 
학습 방식: 특정 태스크를 학습한 것이 아니라, 객체란 무엇인가를 학습

  - 
다양한 도메인을 포함해서 학습

- 
**단점**: 객체 마스크만 생성 → classification 모델 따로 필요

- 
SAM2는 Instance Segmentation에 해당

## 조사 내용

### 스펙
`sam2.1_hiera_large` 기준 **VRAM 6138MiB**

### 적용 가능성

- 
불량 검사 단계에서 사용할 수 있음. 아래는 시나리오

  - 
컨베이어 벨트 위에서 레이저 센서로 주물을 감지한다.

  - 
주물이 감지되면 컨베이어 벨트가 멈춘다.

  - 
카메라로부터 이미지를 얻는다.

  - 
이미지에서 주물을 탐지하고(Detection), 불량 검사(Anomaly Detection)한다.

### 한계

- 
**Inference time: 약 3~4초**

- 
분할만 해주는 모델이므로 단독 사용 어려움. 텍스처가 비슷(경계가 불분명)한 경우 제대로 분할되지 않음
**→ 실험 결과 참고**

### 대안
(테스트 필요)

- 
[FastSAM](https://github.com/CASIA-LMC-Lab/FastSAM)

- 
[MobileSAM](https://github.com/chaoningzhang/mobilesam)

- 
아니면 아예 AD 모델 쓰는게 나을수도? → **정상 이미지만 가지고 학습 가능**

  - 
라이브러리: [Anomalib](https://github.com/open-edge-platform/anomalib)

  - 
모델: [Patchcore](https://github.com/amazon-science/patchcore-inspection), EfficientAD 등

## 실험 환경

### 장비(시스템 환경)

****
| OS | Ubuntu 24.04.4 LTS |
|---|---|
****
| CPU | 13th Gen Intel(R) Core(TM) i7-13620H |
****
| GPU | GeForce RTX 4060 Max-Q |
****
| RAM | 15GiB |
****
| VRAM | 8GB |
****
| Python | 3.12.3 |
****
| CUDA | 12.0 |

### 테스트 데이터

#### **MVTec AD**

- 
사용 이유: 주조 공정과 유사한 카테고리를 포함하고 있어 프로젝트 적용 가능성 검증에 적합할 것으로 판단됨

- 
[논문 리뷰 참고](https://hoya012.github.io/blog/MVTec-AD/)

- 
[데이터셋 다운로드](https://www.mvtec.com/research-teaching/datasets/mvtec-ad/downloads)

- 
사용한 데이터(Class)

  - 
모양: Bottle, Capsule, Metal Nut, Screw

  - 
표면: Tile, Wood

- 
데이터 특징 

  - 
전체 데이터: 2671

  - 
Bottle: `Train: 209 / Test: 148 / Total: 357`

    - 
good / broken_large / broken_small / contamination

  - 
Capsule: `Train: 219 / Test: 243 / Total: 462`

    - 
good / crack / faulty_imprint / poke / scratch / squeeze

  - 
Metal Nut: `Train: 220 / Test: 210 / Total: 430`

    - 
good / bent / color / flip / scratch

  - 
Screw: `Train: 320/ Test: 281 / Total: 601`

    - 
good / manipulated_front / scratch_head / scratch_neck / thread_side / thread_top

  - 
Tile: `Train: 230 / Test: 203 / Total: 433`

    - 
good / crack / glue_strip / gray_stroke / oil / rough

  - 
Wood: `Train: 247 / Test: 141 / Total: 388`

    - 
good / color / combined / hole / liquid / scratch

## 평가 지표

### Stability_score

- 
마스크 경계가 얼마나 안정적인가 측정하는 지표(threshold를 약간 바꿔도 마스크가 유지되는지 확인)

- 
예시:

- 
코드:

### IoU

## 실험 및 결과

****
****
****
****
| 항목 | 결함 종류 | stability_score | predicted_IoU |
|---|---|---|---|
****
| Bottle | good | 0.9545 | 0.9724 |
| broken_large | 0.9607 | 0.9607 |
| broken_small | 0.9594 | 0.9624 |
| contamination | 0.9578 | 0.9648 |
****
| Capsule | good | 0.9750 | 0.9696 |
| crack | 0.9742 | 0.9648 |
| faulty_imprint | 0.9753 | 0.9675 |
| poke | 0.9744 | 0.9637 |
| scratch | 0.9747 | 0.9662 |
| squeeze | 0.9756 | 0.9700 |
****
| Metal Nut | good | 0.9658 | 0.9527 |
| bent | 0.9631 | 0.9573 |
| color | 0.9656 | 0.9579 |
| flip | 0.9598 | 0.9335 |
| scratch | 0.9649 | 0.9628 |
****
| Screw | good | 0.9659 | 0.9310 |
| manipulated_front | 0.9664 | 0.9332 |
| scratch_head | 0.9669 | 0.9305 |
| scratch_neck | 0.9675 | 0.9381 |
| thread_side | 0.9665 | 0.9359 |
| thread_top | 0.9651 | 0.9261 |
****
| Tile | good | 0.9640 | 0.9123 |
| crack | 0.9652 | 0.9261 |
| glue_strip | 0.9651 | 0.9127 |
| gray_stroke | 0.9633 | 0.9117 |
| oil | 0.9637 | 0.9123 |
| rough | 0.9644 | 0.9189 |
****
| Wood | good | 0.9761 | 0.9459 |
| color | 0.9672 | 0.9303 |
| combined | 0.9643 | 0.9108 |
| hole | 0.9677 | 0.9268 |
| liquid | 0.9657 | 0.9281 |
| scratch | 0.9648 | 0.9217 |

## Future Work

#### [MVTec AD] 샘플 이미지 (9109620)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9109620
**최종 수정**: v7 (2026-04-19 sync)

****
| Bottle |   |   |   |   |   |   |
|---|---|---|---|---|---|---|
****
| Capsule |   |   |   |   |   |   |
****
| Metal Nut |   |   |   |   |   |   |
****
| Screw |   |   |   |   |   |   |
****
| Tile |   |   |   |   |   |   |
****
| Wood |   |   |   |   |   |   |

#### Anomaly Detection with PatchCore (8782069)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8782069
**최종 수정**: v26 (2026-04-19 sync)

link: [https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/models/image/patchcore.html](https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/models/image/patchcore.html)  

# 목적

# Background

- 
문제 정의: 이상 탐지 (Anomaly Detection)

  - 
핵심 상황:

    - 
정상 데이터 많음

    - 
이상 데이터 거의 없음 or 정의하기 어려움

  - 
핵심 개념

    - 
one-class learning: 정상 이미지로만 학습

    - 
out-of-distribution detection: 정상 분포와 얼마나 다른지 거리로 계산하여 이상 탐지

      - 
테스트 이미지의 패치 벡터 `q`를 뽑은 뒤, 에서 **가장 가까운 이웃(KNN)까지의 거리**를 anomaly score로 사용.

- 
**잘 동작하기 위한 필요 조건**

  - 
정상의 범위가 좁고 일관적이여야 함. → 촬영 환경이 고정되어 있고 정상 샘플들이 서로 비슷할수록 좋음

  - 
결함이 시각적으로 두드러져야 한다. → 색상 미세 차이나 맥락적 의미 변화 같은건 탐지하기 어려움

    - 
맥락적 의미 변화 예시: 나사 자체는 정상이지만, 잘못된 위치에 조립되었다.

- 
특징

  - 
 → 정상 데이터의 feature 분포만 저장하고 거리 기반으로 이상 판단

  - 
fine-tuning을 하지 않고 사용 가능

    - 
Memory Bank에 내가 가진 정상 이미지를 구성하는 단계만 거치면 됨.

    - 
이후, Memory Bank와 거리를 비교해서 멀면 이상, 가까우면 정상으로 판정

      - 
이상 판단 기준 거리(Threshold)는 직접 설정 가능

# Model - PatchCore

## 모델 정보

- 
`Backbone`: Wide ResNet-50. 

- 
`Pre-trained Dataset`: ImageNet dataset

- 
`PatchCore`는 구조적으로 **memory bank 크기 + 이미지 크기 + patch 수**에 따라 자원 사용량이 결정된다.

  - 
Memory Bank: 정상 이미지들의 특징(feature)을 저장해 둔 데이터베이스(메모리에 올라가있는 텐서)

  - 

- 
`PatchCore`는 데이터와 설정에 따라 요구 자원이 달라지는 구조라서 문서에도 스펙이 명시되지 않음

## 한계

- 
객체 위치가 랜덤하게 변하는 경우 성능이 저하될 수 있음

- 
객체마다 결함 패턴이 완전히 다른경우, 카테고리별 모델을 따로 학습

## 대안

- 
[](https://github.com/m-3lab/awesome-industrial-anomaly-detection?tab=readme-ov-file#34-rgbd-ad)

## 실험환경

### 장비(시스템 환경)

****
| OS | Ubuntu 24.04.4 LTS |
|---|---|
****
| CPU | 13th Gen Intel(R) Core(TM) i7-13620H |
****
| GPU | GeForce RTX 4060 Max-Q |
****
| RAM | 15GiB |
****
| VRAM | 8GB |
****
| Python | 3.12.3 |
****
| CUDA | 12.0 |

### 사용한 데이터

#### 

- 
[Github](https://github.com/amazon-science/spot-diff) | [Paper](https://arxiv.org/pdf/2207.14315) | [Dataset](https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar)

- 
사용 이유: 산업용 이상탐지 데이터셋이기 때문에, 주조 공정과 유사한 카테고리를 포함하고 있음

- 
데이터 특징

#### MVTec AD  

- 
참고:  

# 실험 및 결과

## 평가 지표

### F1 Score

- 
특정 임계값(threshold)에서의 성능을 평가한다.

- 
Precision, Recall 사이의 균형을 반영한다.

- 
클래스 불균형 데이터에서 `Accuracy`보다 유용하다.

- 
**값의 범위는 0~1 이며, 1에 가까울수록 좋다.**

****
``
| Precision | TP / (TP + FP) |
|---|---|
****
``
| Recall | TP / (TP + FN) |
****
``
| Accuracy | (TP + TN) / (TP + FN + FP + TN) |
****
``
| F1 Score | 2 * (Precision * Recall) / (Precision + Recall) |
****
``
| FRP(False Positive Rate) | FP / (FP + TN) |
****
``
| TPR(True Positive Rate) | TP / (TP + FN) |

- 
Recall: 높을수록 아닌 사람을 아니라고 잘 대답함. 

  - 
높을수록 → FN 가 낮음 → 실제 전염병이 아닌 사람 (False)이 실험 결과 아니라고 나옴. (Test negative) → 실제 아닌 사람을 아니라고 잘 대답함. → (불량품이 낮으니까 False) 불량품을 불량품이라고 잘 대답함. 

- 
Precision: 높을수록 False → False 라고 잘 잡음  

  - 
높을수록 → FP가 낮음 → 전염병이 아닌 사람을 전염병이라고 예측 잘 x → 불량품을 불량품이 아니라고 예측하지 않음

  - 
단점: 만약 다 불량품이라고 하면, precision이 높게 나온다. 

### AUROC (Area Under Receiver Operating Characteristic Curve)

- 
ROC(Receiver Operating Characteristic) Curve의 곡선 아래 면적

- 
TPR vs. FPR

  - 
비율 (Rate)으로 계산하여, 모델과 데이터셋이 달라도 비교 가능 

  - 
TPR =   , 실제 정상 데이터 중에서 얼마나 정상을 잘 맞췄는지 비율 (높아야 좋음)

  - 
FPR = , 실제 이상 데이터 중 얼마나 틀렸는지 비율 (낮아야 좋음)

- 
임계값(threshold) 0~1 까지를 바꿔보며 모델 전체 성능을 평가된다.

- 
**값의 범위는 0~1이며, 1에 가까울수록 좋다.**

****
****
| 값 | 의미 |
|---|---|
| 1.0 | 완벽한 분류 |
| 0.5 | 랜덤 추측과 동일한 성능 |
| <0.5 | 랜덤보다 성능 나쁨 |

## 실험1 (VisA)

### Parameter

****
| image_size | (256, 256) |
|---|---|
****
| batch_size | 32 |
****
| backbone | Resnet18 |
****
|   | 0.01 |

### 결과(Score)

- 
저성능 카테고리: capsules / macaroni 1 / macaroni 2

  - 
모두 하나의 이미지에 여러개의 객체 존재

- 
Inference time:** 0.0149sec** per image (fryum 데이터 100장 기준)

****
****
****
| Category | AUROC | F1 Score |
|---|---|---|
| candle | 0.9632 | 0.8478 |
| cashew | 0.9306 | 0.8544 |
| capsules | 0.7873 | 0.6593 |
| chewinggum | 0.9796 | 0.9592 |
| fryum | 0.9080 | 0.8350 |
| macaroni 1 | 0.8760 | 0.7500 |
| macaroni 2 | 0.8038 | 0.6202 |
| pcb1 | 0.9496 | 0.8037 |
| pcb2 | 0.9300 | 0.8125 |
| pcb3 | 0.9311 | 0.8431 |
| pcb4 | 0.9968 | 0.9515 |
| pipe_fryum | 0.9972 | 0.9804 |

### 결과(Image) 예시

- 

## 실험2 (MVTec AD)

### Parameter

****
| image_size | (256, 256) |
|---|---|
****
| batch_size | 32 |
****
| backbone | resnet18 |
****
| coreset_sampling_ratio | 0.01 |

### 결과(Score)

- 
Inference Time: **0.0240sec** per image (bottle 83장 기준)

- 
image_AUROC, image_F1 Score는 단순히 불량 여부를 판단하기 위해 사용

- 
pixel_AUROC, pixel_F1 Score는 결함 위치, 범위까지 정확히 찾아야 할때 사용

****
****
****
****
****
| category | image_AUROC | image_F1 Score | pixel_AUROC | pixel_F1 Score |
|---|---|---|---|---|
****
| bottle | 1.0000 | 0.9920 | 0.9856 | 0.7264 |
****
| cable | 0.9831 | 0.9727 | 0.9849 | 0.6393 |
****
| capsule | 0.9920 | 0.9725 | 0.9901 | 0.5159 |
****
| carpet | 0.9868 | 0.9718 | 0.9908 | 0.6059 |
****
| grid | 0.9883 | 0.9649 | 0.9820 | 0.3839 |
****
| hazelnut | 1.0000 | 0.9928 | 0.9883 | 0.6300 |
****
| leather | 1.0000 | 0.9945 | 0.9922 | 0.4381 |
****
| metal_nut | 0.9971 | 0.9838 | 0.9869 | 0.8386 |
****
| pill | 0.9433 | 0.9458 | 0.9809 | 0.7201 |
****
| screw | 0.9594 | 0.9421 | 0.9894 | 0.3760 |
****
| tile | 1.0000 | 0.9940 | 0.9558 | 0.6200 |
****
| toothbrush | 0.9167 | 0.9355 | 0.9888 | 0.5939 |
****
| transistor | 0.9937 | 0.9500 | 0.9727 | 0.6084 |
****
| wood | 0.9860 | 0.9587 | 0.9314 | 0.4689 |
****
| zipper | 0.9779 | 0.9791 | 0.9814 | 0.5441 |

### 결과(Image) 예시

## 실험 3 (Manhole Custom Dataset)

### Parameter

****
| image_size | (256, 256) |
|---|---|
****
| batch_size | 32 |
****
| backbone | wide_resnet50_2 |
****
| coreset_sampling_ratio | 0.1 |

### 결과(Score)

****
****
| Test Metric | Score |
|---|---|
| image_AUROC | 0.6868130564689636 |
| image_F1Score | 0.9853479862213135 |

### 결과(Image) 예시

- 
전체 데이터: 1,358장

  - 
Train: 238장

    - 
Train(Memory Bank에 저장할) 데이터가 많을수록 GPU 사용량이 높아짐

    - 
촬영된 정상 이미지를 0~359도 회전시키면서 데이터 생성(원형 맨홀 정상 제품 2개, **전체 720장**)

    - 
이 중 **랜덤으로 샘플링하여 238장** 사용

  - 
Test: 1,120장

    - 
`broken | distortion | overflow` 3가지 불량 케이스를 각각 0~359도 회전 시키면서 데이터 생성**(360*3=1,080장**)

    - 
Train dataset에서 랜덤으로 **43장**을 Test dataset으로 사용

****
| broken |   |
|---|---|
****
| distortion |   |
****
| good |   |
****
| overflow |   |

## 실험 3-1 (Manhole Custom Dataset)

### Parameter

****
| image_size | (256, 256) |
|---|---|
****
| batch_size | 32 |
****
| backbone | wide_resnet50_2 |
****
| coreset_sampling_ratio | 0.1 |

### 결과(Score)

****
****
| Test Metric | Score |
|---|---|
| image_AUROC | 1.0 |
| image_F1Score | 0.9995368123054504 |

### 결과(Image) 예시

- 
전체 데이터: 1,800장

  - 
Train: 720장

    - 
원형 맨홀 정상 제품 2개를 0~359도 회전시키면서 데이터 생성

  - 
Test: 1,080장

    - 
원형 맨홀 불량 제품 3개(`broken | distortion | overflow`)

****
| broken |   |
|---|---|
****
| distortion |   |
****
| good |   |
****
| overflow |   |

# 적용 가능성 판단

1. 
불량 검사 단계에서 적용가능

1. 
VisA 기준 이미지당 약 0.0149초, MVTec AD 기준 이미지당 약 0.0240초로 실시간 적용 가능

1. 
**조도(밝기)가 변하는 경우 불량 판단 기준이 달라질 수 있어서 실제 주물 데이터로 확인 필요**

1. 

  1. 
[https://drive.google.com/file/d/17Lc2JExkMVYFaNLgYN3OEQDrmzCGjhL9/view?usp=drive_link](https://drive.google.com/file/d/17Lc2JExkMVYFaNLgYN3OEQDrmzCGjhL9/view?usp=drive_link)

#### [VisA] 샘플 이미지 (11632875)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11632875
**최종 수정**: v1 (2026-04-19 sync)

- 
이 데이터 셋은 Anomaly 종류에 대해 따로 분류하지 않음.

- 
Anomaly가 다양해서 확인이 필요한 경우 아래 링크 확인

  - 
[Github](https://github.com/amazon-science/spot-diff) | [Paper](https://arxiv.org/pdf/2207.14315) | [Dataset](https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar)

### 이미지 샘플

****
| candle |   |   |
|---|---|---|
****
| capsules |   |   |
****
| cashew |   |   |
****
| chewinggum |   |   |
****
| fryum |   |   |
****
| macaroni1 |   |   |
****
| macaroni2 |   |   |
****
| pcb1 |   |   |
****
| pcb2 |   |   |
****
| pcb3 |   |   |
****
| pcb4 |   |   |
****
| pipe_fryum |   |   |

#### Binary Classifier via Transfer Learning with YOLOv26 nano model (9568300)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9568300
**최종 수정**: v8 (2026-04-19 sync)

# 목적
우리 시나리오에서, 각 제품에 대한 양품/불량품 판정을 한다고 가정해보면,
컨베이어 벨트위에서 (1) 제품의 종류를 확인 (2) 각 제품의 종류에 따라 양품/불량품 binary classifier 를 불러와 검증해야한다. 
이러한 단계에서 (2)의 모델을 만들고자 한다. 실제 시연에서 사용할 샘플의 (양품/불량품)을 모아 사전에 학습이 필요하다. 

# Background 

## Yolov26 
[https://arxiv.org/pdf/2602.14582](https://arxiv.org/pdf/2602.14582) 

## Transfer Learning 
Transfer learning 이란 기존의 사전 학습된 큰 모델을 feature extractor로 사용하고 뒷단에 classifier를 새로 붙여 학습한다. 즉, 사전학습된 모델에 저장된 큰 데이터에 대한 general prior knowledge 를 활용하여, 실제 classifier 입력으로 들어가는 정보가 훨씬 풍부하여 학습시간이 짧게 걸린다는 특징이 있다. 
문제는 학습 데이터와 실제 transfer learning에 사용되는 domain이 매우 다른 경우에는 사용할 수 없으며,  이러한 prior knowledge가 few-shot training data에 잘 적용될지는 미지수이다. 

## Binary Classifier 
우리는 양품/불량품으로 binary class로 나누면 된다. 이때, binary classifier에선 logistic regression처럼 FC layer 뒤에 sigmoid로 연결된 작은 구조를 사용한다. 입력데이터는 앞서 사전 학습된 YOLO 모델에서 뽑은 feature embedding vector이다. YOLOv26 nano model을 사전 학습 모델로 사용하여 (CNN layer + sigmoid) 구조로 classifier 를 구성할 예정이다. 

# Dataset 

## MVTec-AD 

## ViSA 

## Our Dataset 
각 shape 마다 양품 1개와 불량품 3개 (Broken, Distortion, Overflow)가 존재하며, 하나의 주물마다 컨베이어 벨트위에서 총 6개씩 데이터를 제작하였다. (3* 4 * 6 = 72 개) 

# Code

#### Anomaly Detection Comparative Study with PatchCore, RGBD-AD (12517427)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/12517427
**최종 수정**: v1 (2026-04-19 sync)

#### Integration RobotArm with Yolov26 (21397529)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21397529
**최종 수정**: v6 (2026-04-19 sync)

1. 
위치를 메인서버에 보내기(이후 메인서버가 로봇에게 전달. → 용석님과 같이 통신 작업)

1. 
클래스 분류 3개(원형, 타원형, 네모)

#### YOLO Bounding Box labeling with labelImg on manhole mock-up samples(rev.02) (21037107)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21037107
**최종 수정**: v36 (2026-04-19 sync)

# 실험목적
YOLO 기반 객체 탐지(Object Detection)를 위해, Manhole Mock-up 제품을 대상으로 라벨링 작업을 수행하였다. COCO 데이터셋에는 Manhole 클래스가 정의되어 있지 않으므로, 컨베이어 벨트 상에서 각 제품의 유형, 위치, 양품/불량품 상태를 웹캠으로 취득한 후, labelImg 툴을 활용하여 어노테이션(annotation)을 진행하였다.

# Background
[labelImg](https://github.com/HumanSignal/labelImg)는 이미지 내 관심 영역(ROI, Region of Interest)에 Bounding Box를 지정하여 객체의 위치와 클래스를 동시에 라벨링할 수 있는 도구이다. 이를 활용해 각 Manhole Mock-up 제품에 대해 클래스 라벨과 바운딩 박스를 동시에 지정하는 어노테이션을 수행할 수 있다.
labelImg의 annotation은 각 Manhole Mock-up 제품의 이미지에 대해 객체의 클래스(종류, 양/불량 상태)와 바운딩 박스 좌표를 함께 지정할 수 있고, 그 결과 YOLO 학습에 필요한 라벨이 생성되며, 해당 포맷은 이미지 한 장당 하나의 텍스트 파일(.txt)로 저장된다.

# 실험과정
실험 샘플
Manhole 목업 샘플 Rectangle, Circle, Ellipse (3종)
샘플 종류별 상태 분류
good(양품), bad_broken(내부 파열 불량), bad_distortion(외부 파열 불량), bad_overflow(주물 과다 투입 불량) (4종)
실험 도구 및 스펙: 
Top-view camera(경기장 내 위치고정): 해상도 1280*720, 바닥으로부터의 높이는 15cm.
Conveyor 벨트: 정지 상태.
Laptop(RTX 4060)
실험 방법
샘플 3종 각각에 대해 추가로 4종류의 상태를 제작하였다(총 샘플 개수:3*4=12)
이를 위해 Top-view camera를 Conveyor belt 중간에 위치시켰으며, 이 지점에 샘플을 놓고 해당 카메라를 통해 image를 촬영하고 데이터셋을 만드는 것이 우선이다. 각 샘플에 대한 추가적인 위상(phase) 고려사항은 다음과 같다.
Phase: 컨베이어 벨트 위, 중간, 가운데, 제품 90도 회전 뒤 벨트 위, 중간, 가운데. (6 위치)
동일한 샘플, 동일한 위상에서는 샘플 촬영을 3회 진행한다.
따라서 샘플의 총 촬영된 사진 수: 3*4*6*3=216장.
Annotation을 위한 이미지들의 파일명 부여는 다음과 같다.
sample name_status_numbering.txt
sample name: r: rectangle, c: circle, e: ellipse.
status: good, bad_broken, bad_distortion, bad_overflow
numbering: 001부터 시작해서 순차적으로.
ex: 
r_bad_broken_001.txt (r: rectangle, bad_broken: 불량품 상태, 001: 제품의 촬영 사진 순번)
c_good_002.txt(c: circle, good: 양품, 002: 제품의 촬영 사진 순번) 
촬영을 완료하면 생성된 이제 labelImg를 실행해야 한다.
[labelImg](https://github.com/HumanSignal/labelImg) 하위 폴더에 가보면, data폴더 안에 predefined_classes.txt파일이 있는데, 여기서는 labelImg프로그램이 annotation하고자 하는 class name 지정할 수 있다. 여기에 다음의 순서로 작성한다. 첫 단어는 class에 0을 할당, 그 다음 단어부터는 1씩 더해서 할당된다.
이제 labelImg프로그램을 통해 annotation을 진행하면 된다.
객체 사진에서 bounding box로 규정하기 원하는 영역을 Create Rectbox클릭후 drag해서 지정해준 뒤, 이에 대해 class name을 선택한다. 이후 저장하면 각 촬영된 샘플마다 지정한 bounding box에 해당하는 txt파일이 label 데이터로 지정되는데, 각 라벨 파일은 객체별로 한 줄씩 아래와 같은 형식으로 구성된다. 
labelImg로 생성되는 labeling 양식은 정규화 좌표 (Normalized Coordinates)를 따른다. 

#### 🔹 정규화좌표
이미지 너비(`W`)와 높이(`H`)로 나누어 `0.0 ~ 1.0` 범위로 매핑한 상대 좌표. YOLO 아키텍처가 학습 시 기본적으로 사용하는 표준 형식이다.
구체적인 포맷은 다음과 같다.
각 항목의 필드값에 대한 설명은 다음과 같다.

| 필드 | 설명 | 값 범위 / 비고 |
|---|---|---|
``
| class_id | 객체 클래스에 할당된 정수형 ID. 아까 predefined_classes.txt에서 저장된 class name 중 하나를 선택하면, 0부터 시작해 할당된다. | Rectangle: 0, Circle: 1, Ellipse: 2 |
``
| x_center | 바운딩 박스 중심점의 x 좌표 (이미지 너비 대비 정규화) | 0.0 ~ 1.0 |
``
| y_center | 바운딩 박스 중심점의 y 좌표 (이미지 높이 대비 정규화) | 0.0 ~ 1.0 |
``
| width | 바운딩 박스의 너비 (이미지 너비 대비 정규화) | 0.0 ~ 1.0 |
``
| height | 바운딩 박스의 높이 (이미지 높이 대비 정규화) | 0.0 ~ 1.0 |
모든 좌표값은 0~1 사이로 정규화(normalization)되며, 이는 YOLO 모델이 다양한 해상도의 입력 이미지를 일관되게 처리할 수 있도록 하는 표준 방식이다.
추가로 classes.txt 파일도 생성이 되는데, 이는 라벨링에 사용된 모든 class name를 총괄한 것.

# 평가지표
이미지 데이터셋(폴더구조 추가)
이미지 데이터셋에 대해 annotation을 진행하면 각 맨홀 객체(rectangle, circle, ellipse) 폴더 하에 images, labels가 생성되게 하였으며, images 폴더에는 annotation된 이미지 파일(jpg), labels에는 annotation된 이미지 파일의 라벨 데이터(.txt)가 저장된다.

# 실험결과
labels, images 폴더에 각 샘플별 annotation된 .txt와 image가 생성되었고, 위의 폴더구조를 보면
이미지는 images 폴더에, .txt파일은 labels에 샘플 구조에 따라 annotation이 잘 진행되었음을 알수 있다. annotation파일들은 train.zip으로 업로드하였다(버전은 향후 이미지 추가에 따라 달라질 수 있음)
아래는 annotation결과물들의 개정 사항이다.

## 개정사항(rev.01)
Rectangle, Circle, Ellipse 객체에 대해 부여된 class ID 숫자를 규격화
Rectangle: 0
Circle: 1
Ellipse: 2
그 외 중심 x,y좌표,  너비 및 높이는 이전과 동일.  
모든 샘플들은 카메라로부터 수직으로 위치해 있으며, 컨베이어벨트에 수평하게 놓인 샘플들이다.
[https://drive.google.com/file/d/12_WNB4v3wbltSViwuonoPMX_6juCIIa7/view?usp=drive_link](https://drive.google.com/file/d/12_WNB4v3wbltSViwuonoPMX_6juCIIa7/view?usp=drive_link) 

## 개정사항(rev.02)
요청받은 Ellipse 재작업 제품으로 다시 데이터셋 제작 후 라벨링. 
재작업 내용: Ellipse 치수 증가(그리퍼가 더 쉽게 Pinkybot의 슬롯형 보관함으로부터 집기 쉽도록). 이전 작은 Ellipse는 사용안할예정. 나머지 Rectangle, Circle은 변함없음.
모든 샘플들은 카메라로부터 수직으로 위치해 있으며, 컨베이어벨트에 수평하게 놓인 샘플들이다.
[https://drive.google.com/file/d/1P4vcy0YOgI3UN74dqFjbtc3Fl4pt6wxR/view?usp=drive_link](https://drive.google.com/file/d/1P4vcy0YOgI3UN74dqFjbtc3Fl4pt6wxR/view?usp=drive_link) 

# 변경사항
초기에는 컨베이어벨트의 샘플에 대해서 객체탐지용과 이미지 분류 모두를 위한 목적으로 이미지 데이터셋에 대해 labelImg를 통한 라벨링 작업 후 images와 labels를 모두 얻은 뒤 객체탐지에 활용하고, classification을 위해서는 이들 데이터셋 중 images만 추출하는 것이 목적이었으나, 컨베이어벨트의 비전검사에서는 객체탐지가 아닌 이미지 분류 작업만 진행하기로 함. 따라서 컨베이어벨트에서의 이미지들에 대해서는 imageImg를 통한 bounding box 작업이 무의미하므로 이번 조사로부터는 이미지만 추출하여 Image Classification에 활용하는 것으로 함.
 
그러나 슬롯형 보관함 위의 슬롯에 맨홀 샘플을 탑재한 뒤, 로봇팔이 슬롯형 보관함으로부터 샘플을 탐지하여 보관 선반으로 이송하는 경우에는 객체탐지(Object Detection)가 필요하다. 이 경우는 bounding box를 통해 labeling을 하는 방법을 바탕으로  항목에서 슬롯형 보관함 위의 맨홀 샘플에 대해 새로운 labeling을 할 예정이다. 이후 얻어진 새로운 데이터셋은  항목에서 훈련을 진행하고, 추론을 통해 검증 예정이다.

#### [Classification]YOLO Image dataset(only images) extracted from labelImg dataset(images, labels) on conveyor belt (31096872)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31096872
**최종 수정**: v7 (2026-04-19 sync)

# 실험목적
  에서 얻은 데이터셋은 images, labels라는 이미지, 텍스트파일로 구성된 객체탐지용임. 이 경우 Image Classification을 위해서는 labels 정보는 필요없으며, 이미지 정보만이 요구된다. 즉, images 파일들만 따로 class별로 분류된 데이터셋이 필요하다.

# Background
[https://docs.ultralytics.com/ko/datasets/classify/#folder-structure-example](https://docs.ultralytics.com/ko/datasets/classify/#folder-structure-example) 
이미지 분류 작업의 디렉토리는 기존의  디렉토리와 비교해보면, labels의 txt파일들 및 폴더만 제외된다는 점만 제외하면 큰 뼈대는 거의 비슷하다.
단, 이 경우에도 classification을 위해서는 이미지들도 train, val 폴더를 추가하여 훈련용, 검증용으로 나눈 뒤, 이미지들을 할당하는 과정이 여전히 요구된다.

# 실험과정
 으로부터 얻은 detection용 데이터셋에서 이미지파일만 추출한 뒤, train과 val 폴더로 나눈뒤(이미지수 비율은 8:2) 각각에 대해 class별로(rectangle, circle, ellipse) 이미지들을 저장한다.

# 평가지표
Classification용 이미지 데이터셋 폴더구조, 데이터셋

# 실험결과
Classification용 이미지 데이터셋 폴더구조
Image Classification용 이미지 데이터셋은 다음과 같다.
[https://drive.google.com/file/d/1wjfVbe0jpl_fcwpKmVNM-wsStIl50Aq8/view?usp=drive_link](https://drive.google.com/file/d/1wjfVbe0jpl_fcwpKmVNM-wsStIl50Aq8/view?usp=drive_link) 

# 우리 프로젝트 적용 판단
해당 결과물은   항목을 위한 데이터셋으로 활용될 예정이다.

#### [Detection]YOLO Image dataset(images, labels) of manhole samples on slotted storage(슬롯형 보관함) (31228237)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31228237
**최종 수정**: v13 (2026-04-19 sync)

# 실험목적
앞서  포스트에서 언급했던 바와 같이, AMR위의 슬롯형 보관함의 맨홀 샘플은 Detection 이 진행되어야 한다. 특히 로봇팔이 AMR위의 샘플을 카메라로 탐지하는 경우에는 새로운 데이터셋이 필요한데, 슬롯형 보관함 위의 맨홀 샘플을 여러 조건에서 촬영한 뒤 이미지들을 확보하고, 이를 labeling하여 객체탐지용 데이터셋을 만드는 것이 이 포스트의 목적이다. 제작된 데이터셋은 이후 객체탐지 훈련 및 추론에 활용될 예정이다.()

# Background
[https://docs.ultralytics.com/ko/datasets/detect/](https://docs.ultralytics.com/ko/datasets/detect/) 
Ultralytics에서 규정하는 객체 탐지 데이터 세트 개요에서 보듯이, 객체탐지용 데이터는 이미지 하나당 `.txt ` 형식의 레이블이 추가된다. 해당 `.txt `파일은 객체당 한 행으로 `class x_center y_center width height` 형식으로 지정해야 한다. 상자 좌표는 크게 정규화된 좌표와, 픽셀 좌표. 둘로 나뉠 수 있다. 데이터 라벨링을 위해서는,  에서 언급했듯이, 정규화된 좌표를 얻는 과정이 필요하다. 언급된 포스팅 중 정규화 좌표에 대한 내용만 정리하면 다음과 같다.
bounding box를 찾고, 이를 정하는 과정은 기존의 방식과 동일하다.

# 실험과정
먼저 슬롯형 보관함 위의 샘플 종류는 Rectangle, Circle, Ellipse 3 종류로 이전과 같으나, 분류 Class는 manhole 하나로 통일한다. 왜냐면 적재 과정에서 로봇팔은 다양한 거리와 각도에서 AMR 위의 슬롯형 보관함 위의 맨홀 샘플들을 파지(Picking)하는데, 이때 맨홀 샘플이 Rectangle, Circle, Ellipse 중에서는 어떤 종류인지는 컨베이어 벨트 시스템에서 Classification 을 통해 전달받기 때문이다. 따라서 적재 과정에서 로봇팔에 필요한건 AMR이 주차한 후에 로봇팔의 카메라가 AMR 슬롯형 보관함 위의 맨홀 샘플의 위치를 파악한 뒤, 이를 추적해서 샘플을 집는 것이다. 이때 활용되는 Detection의 class는 manhole하나만 입력한다(종류 무관).
labelImg를 실행하고 샘플의 bounding box를 사각형으로 지정하면, 각 라벨들에 대한 이미지들과 이미지 내 샘플들의 정규화된 bounding box좌표값들을 추출한 .txt파일들을 얻을 수 있다.

# 평가지표
폴더구조: 이미지들과 이에 대한 데이터들의 txt파일들이 있어야 한다. 그리고 이들을 학습과 추론, 그리고 이미지와 라벨에 대해 각각 할당되야 한다.
Detection의 데이터셋이 확보되야 한다.

# 실험결과
Detection을 위한 슬롯형 보관함의 맨홀 샘플들의 데이터셋은 다음과 같다.
[https://drive.google.com/file/d/15eaUsWZ5AQxbJsaXq06AZ7B-sQYOp7Ol/view?usp=drive_link](https://drive.google.com/file/d/15eaUsWZ5AQxbJsaXq06AZ7B-sQYOp7Ol/view?usp=drive_link)
폴더구조는 다음과 같다.
data.yaml 내용은 다음과 같다.
학습(train)에는 416장, 추론(val)에는 104장 사용해 총 520장의 이미지가 사용되었다. 
지정된 class는 앞서 언급했듯이 manhole 하나이다.

# 우리 프로젝트 적용 방안
얻어진 데이터셋을 이제  에 적용해서 학습시키도록 한다.

#### [Classification]YOLO Image classification with image dataset of manhole mock-up samples on conveyor belt (22184111)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/22184111
**최종 수정**: v33 (2026-04-19 sync)

# 실험목적
Image Classification 항목에서는 전체 이미지를 미리 정의된 클래스 집합 중 하나로 분류하는 작업으로, 사전학습된 모델을 활용해 훈련시키는 과정이 일반적이다. Conveyor belt 위의 맨홀 샘플 감지에서는 이미지 분류 작업을 진행하는 것이 목적이다. 따라서 대표적인 사전 학습된 모델인 ImageNet 중에서 [yolo26n-cls.pt](http://yolo26n-cls.pt)의 가중치(Weights)를 초기 모델로 사용하여  항목에서 얻은 images 데이터셋에 적용해 classification training을 진행하고 맨홀 목업 샘플에 대해 파인튜닝된 모델(`best.pt`)을 얻는 것이 image classification의 목적이다. 

# Background
먼저 Image Classification과 Object Detection의 경우 요구되는 데이터 종류가 다르다.

- 
객체 탐지 (Object Detection)**:** `labelImg`로 바운딩 박스(bounding box)를 그리고 `*.txt` 파일을 얻은 것은 "사진 속에서 맨홀이 어디에 위치하는가?" 를 알려주는 과정임. 이때 라벨 파일에는 객체의 클래스 ID와 좌표 정보(x, y, w, h)가 담김.

- 
이미지 분류 (Image Classification): "이 사진 전체는 맨홀이다." 라고 판단하는 작업. 이 경우 바운딩 박스 좌표는 필요 없으며, 이미지 전체와 해당 이미지의 클래스(맨홀) 정보만 있으면 됨.
앞서  에서는 객체 탐지를 위한 데이터들이 있는데, 이 중에서 바운딩 박스 좌표값을 제외하고 이미지 전체와 클래스 정보만 추출하면 된다. 객체탐지를 위한 데이터는 추후 Object Detection 항목에서 진행하면 된다. 추가로 Image Classification을 위한 데이터셋 변환이 필요하며, 폴더 구조를 변경하는 것도 추가로 요청된다.
학습방법으로는 파인튜닝을 진행할 것이며, 이미 Ultralytics에 의해 사전학습된 ImageNet이라는 데이터셋을 활용할 예정이다. ImageNe은 약 1,200만 장의 일반 사물(개, 고양이, 자동차 등)으로 학습된 거대한 데이터셋이다. 해당 데이터셋은 YOLO26에 의해 사전 학습되었는데, 이때 모델은 사전 학습과정을 통해 가중치 파라미터를 조정하게 된다. 모델 가중치란 학습된 데이터들 내 패턴, 특징, 관계를 인식함으로서 AI는 일종의 기억 및 지식을 갖추는데, 이러한 기억들을 체계화 및 저장한 것이다. 가중치는 수많은 파라미터들로 형성되어 있고 어떤 데이터를 썼는지에 따라 가중치 값은 달라질 수 있으며, Image Classification을 위한 모델 가중치로는 [yolo26n-cls.pt](http://yolo26n-cls.pt) 가 있다. 이 가중치는 이미지의 가장자리, 질감, 기본 형태를 인식하는 능력을 갖추고 있다. 파인튜닝을 통해 맨홀 샘플을 사전학습된 모델로 학습하게 되면 해당 맨홀 샘플에 맞는 새로운 가중치(.pt파일)를 얻는 것이 이번 실험의 목적 중 하나이다. 학습을 진행하면 best.pt, last.pt 파일을 얻을 수 있는데, 전자는 검증 데이터셋에서 손실 정도가 가장 낮은 Epoch에서의 모델 가중치 정보이다. 후자는 학습 이후 마지막 epoch에서의 모델 가중치 정보이다. 일반적으로는 best.pt를 활용한다.
여기서 모델은 훈련 과정 중에 데이터셋을 여러번 통과해야 하는데, 훈련 데이터셋을 완전히 통과하는 1번의 과정을 1 에포크라 한다. 50 에포크는 50번의 통과를 의미.

# 실험과정
먼저  로부터 classification을 위한 이미지 정보만 추출하기 위해 다음의 코드를 실행한다.
실행하면 dataset_cls안에 train, val 두 폴더가 생성되며, 각각의 폴더에는 class name을 한 폴더들(circle, rectangle, ellipse)가 생성되어 그 안에 이미지 파일들이 저장될 것이다. 여기서 train과 val의 비율은 80:20으로 지정하였다.
이제 얻어진 dataset_cls의 이미지 자료를 바탕으로 사전학습된 모델 가중치를 불러오고, 이에 대해 학습을 실행하여  classification을 진행하면 된다.
학습이 완료되면 안내문구와 동시에 weights 폴더에 best.pt파일이 생성됨을 알수 있다.
생성된 best.pt파일은 1. confusion matrix와 result 결과값, 2. 학습에 활용되지 않은 이미지들을 활용해 학습된 모델을 검증하는 방식으로 검증이 가능하다.

# 평가지표

1. 
dataset_cls가 잘 생성되었는가?

1. 
best.pt파일이 잘 생성되었는가?

1. 
confusion matrix와 result 결과값이 잘 도출되었는가?

1. 
학습에 활용되지 않은 이미지로 관찰된 객체들이 학습될 모델로 image classification이 잘 수행되는가?

# 실험결과

## 분류한 dataset_cls 파일 및 폴더구조: 
dataset_cls5는 classification에 활용된 train, val 폴더의 이미지들을 class별로 분류한 파일들이다. 이러한 폴더구조로 되어있어야 Image Classification이 가능하기 때문이다.
분류된 dataset_cls5 폴더는 다음과 같다.
[https://drive.google.com/file/d/1afahSOjuvdlXVi1lXREzjfp-ee1Jo4WJ/view?usp=drive_link](https://drive.google.com/file/d/1afahSOjuvdlXVi1lXREzjfp-ee1Jo4WJ/view?usp=drive_link) 

## Image Classification 결과

### classification_training.py 실행결과
여기서 사전학습된 모델인 YOLO26의 가중치 yolo26n-cls.pt는 불러온 데이터셋을 확인 후(train 171장, val 45장, 총 3개 클라스) 클라스 수를 3개(rectangle, circle, ellipse)로 자동조정한 뒤, 이에 맞는 모델 구조를 출력하고 사전학습 가중치를 가져옴을 알 수 있다.
이제 학습을 지정한 Epoch수에 따라 진행하면 
최적의 결과값을 얻었다 판단하면 모델은 일정 Epoch 지점에서 멈추고 학습을 종료한 뒤, best.pt파일 및 관련 결과자료들을 얻을 수 있다.
최종 결과값은 터미널에서도 볼 수 있다.
학습된 classifier의 weight 파일(best.pt)은 다음과 같이 얻어진다.
 

## Image Classification 검증

### Confusion matrix와 results.png
결과값은 classification_training.py 실행시 run 폴더 안에 위치한다. [https://drive.google.com/file/d/11uO840CEKn7SxR7MthO-ToVd3BPO87mO/view?usp=drive_link](https://drive.google.com/file/d/11uO840CEKn7SxR7MthO-ToVd3BPO87mO/view?usp=drive_link) 

#### results.png
Loss 그래프 (train/loss, val/loss)
의미: 모델의 오차가 얼마나 줄어드는지 보여줌.

- 
train/loss (좌상단):

  - 
초기: 1.2 → 최종: 0.01 정도로 급격히 감소

  - 
모델이 학습 데이터를 잘 학습하고 있음 

- 
val/loss (좌하단):

  - 
초기: 0.7 → 최종: 0에 가까움

  - 
검증 데이터에서도 오차가 거의 없음

- 
해석:

  - 
두 그래프 모두 급격히 감소 후 안정화 → 학습이 잘 됨

  - 
train loss와 val loss의 차이가 작음 → 과적합(overfitting) 없음
Accuracy 그래프 (metrics/accuracy_top1, top5)
의미: 모델의 정확도를 보여줌.

- 
accuracy_top1 (우상단):

  - 
초기: 0.62→ 5번째 epoch부터 1.0 (100%) 도달

- 
accuracy_top5 (우하단):

  - 
처음부터 1.0 (100%) 유지

  - 
상위 5개 예측 안에 정답이 항상 포함됨

#### Confusion matrix
Confusion Matrix (혼동 행렬)
의미: 모델이 각 클래스를 얼마나 정확히 예측했는지 보여줌.
x축: True(Ground Truth) classes라 부르며, 실제 정답을 의미한다. 즉, 객체가 실제로 원인지, 타원인지, 사각형인지를 의미.
y축: Predicted classes라 부르며, 모델이 예측한 답을 의미한다. 즉, 객체에 대해 모델이 훈련을 통해 예측한 class를 나열한 것이다. 
대각선의 class들은 실제 정답을 각 경우에 대해 모델이 정확히 맞추었다는 것을 의미한다. 

- 
대각선(왼쪽 상단 → 오른쪽 하단): 정확히 예측한 갯수

  - 
circle: 15개 정확 예측 

  - 
ellipse: 15개 정확 예측 

  - 
rectangle: 15개 정확 예측 

- 
해석:

  - 
대각선에만 값이 있고, 나머지는 모두 0이므로 오분류가 없음.
우측의 bar는 colorbar로서, 개별 class에 대한 모델의 최소 예측값(하얀색)부터 최대 예측값(짙은 파란색)을 의미한다. 예를 들어 circle의 경우는 15개에 대해 모두 정확히 예측했기 때문에 짙은 파란색을 나타낸 것이며, 만일 15개 중 10개를 예측했다면  옅은 파란색 네모로 표시되었을 것이다.
참고로 Background는 class가 아니며, 모델이 어느 것도 아닌 객체에 대해 무조건 circle/ellipse/rectangle 중 하나로 잘못 분류하는 것을 방지(즉, false detection을 방지하기 위한 것)->[참고링크](https://github.com/ultralytics/ultralytics/issues/4479)

### 학습에 활용되지 않은 이미지를 활용한 모델 검증
결과값
[https://drive.google.com/file/d/1CwVcWx_UBktYug34QrPYCrrviQZt2BlC/view?usp=drive_link](https://drive.google.com/file/d/1CwVcWx_UBktYug34QrPYCrrviQZt2BlC/view?usp=drive_link) 
위의 predict 폴더는 각 테스트 이미지들을 추론한 결과 이미지들을 모아놓은 폴더이다. 터미널에서는 해당 이미지들에 추론 결과를 터미널로 알려주고 있다. 컨베이어 벨트에 아무 맨홀도 없을 경우는 Background/unknown으로 표기되며, 나머지 Ellipse, Rectangle, Circle의 경우에는 정상적으로 추론이 이루어지고 있음을 알 수 있다.
이번 YOLO image classification은 콘베이어 벨트에 주물을 적재하는 시나리오에 대해 적용될 예정인데, 이때는 콘베이어 벨트 위에서 카메라가 Rectangle, Circle, Ellipse의 class들의 수직 방향 이미지만 탐지할 예정이다.

# 프로젝트 적용방향
콘베이어 벨트에 주물을 적재하는 시나리오에서 비전검사

#### (미완성) [Classification] 맨홀 분류 모델 실험 (26084135)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26084135
**최종 수정**: v2 (2026-04-19 sync)

# 목적

# 실험

## 요약

****
****
| 항목 | 내용 |
|---|---|
| 분류 클래스 | circle / ellipse / rectangle |
| 모델 | EffieienctNet-V2-S (ImageNet pretrained) |
| 프레임워크 | PyTorch + timm |

## 데이터셋

### 구성

- 
이미지 형식: JPG

****
****
| 클래스 | 이미지 수 |
|---|---|
| circle | 72장 |
| ellipse | 72장 |
| rectangle | 72장 |
****
****
| 합계 | 216장 |

### 데이터 분할

- 
Stratified Split으로 3분할 하여 클래스 비율 유지

****
****
****
| 세트 | 비율 | 용도 |
|---|---|---|
| Train | 70% | 모델 학습 |
| Validation | 15% | Early Stop / Best Model 선정 |
| Test | 15% | 최종 성능 평가 |

## 모델

| 모델 | 발표 | ImageNet Top-1 | 파라미터 | 비고 |
|---|---|---|---|---|
****
****
****
| EfficientNet-V2-S | 2021 (ICML) | 83.9% | 21.5M | 최종 선정 |
| ConvNeXt-Tiny | 2022 (CVPR) | 82.1% | 28M | 대안 1 |
| YOLO26s-cls | 2026 (Ultralytics) | 76.0% | 6.7M | 대안 2 |

### 모델 선정 이유

- 
**소규모 데이터에서 과적합 억제**: Progressive Learning 기반 pretrained weight → 과적합 억제

- 
**맨홀 형태 분류**: CNN의 지역→전역 계층 학습이 외곽선 형태 구분에 적합

- 
**정확도 우선**: 후보 모델 중 ImageNet Top-1 **83.9%**로 가장 높음

- 
**파라미터 효율**: ConvNeXt-Tiny 대비 파라미터 6.5M 적으면서 정확도는 높음

### 대안 1 (ConvNeXt)

- 
장점: ViT의 장점을 CNN 구조로 흡수하여 안정적인 소규모 데이터 학습 가능.

- 
단점: EfficientNet-V2보다 무겁지만, 정확도는 소폭 낮음.

### 대안 2 (YOLO26-cls)

- 
장점: 가장 가벼워 추론 속도가 우수 → 실시간 처리가 필요한 경우 엣지 디바이스 배포에 유리

- 
단점: ImageNet Top-1 76.0%로 EfficientNet-V2-S 대비 7.9%p 낮음

# 실험 및 결과

## 파라미터

****
****
| 항목 | 값 |
|---|---|
****
| 입력 이미지 크기 | 224 × 224 |
****
| Batch Size | 16 |
****
| Phase 1 학습률 | 1e-3 |
****
| Phase 2 학습률 | 1e-4 |
****
| Phase 1 Epoch | 10 |
****
| Phase 2 Epoch | 40 (Early Stop 적용) |
****
| Early Stop Patience | 10 |
****
| Weight Decay | 1e-4 |
****
| Optimizer | AdamW |
****
| Scheduler | CosineAnnealingLR |
****
| Random Seed | 42 |

## 학습 전략
(정량 & 정성적 결과 포함)

1. 
실험 1 내용 + 결과

1. 
실험 2 내용 + 결과

# 우리 프로젝트 적용 판단

1. 
채택/보류/제외 기준 

1. 
우리 프로젝트 적용 판단 (아래는 예시)

  1. 
어느 공정에 넣을지

  1. 
실시간 가능 여부

  1. 
추가 하드웨어 필요 여부

  1. 
데이터 수집 필요량

#### [Unfit for Classification] YOLO Image classification of manhole mock-up samples on slotted storage(슬롯형 보관함) (26738902)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26738902
**최종 수정**: v8 (2026-04-19 sync)

이번 테스트에서는  에 나온 결과를 바탕으로 컨베이어 벨트 위에 수직으로 놓인 카메라로 맨홀 샘플 이미지를 분류하는 과정이 아닌, AMR 위의 슬롯형 보관함의 홈(slot)에 맨홀 샘플이 무작위로 떨어질 경우, 이를 단일 class(manhole)로 분류한 뒤, 이를 동일하게 image classification을 진행할 수 있는지를 검증한다. 카메라의 측정 방향이 거리가 일정한 수직 방향이 아닌, 다양한 각도와 거리에서 바라본 경우라 가정하므로(왜냐면 AMR의 적재함 경우에는 로봇팔이 맨홀 샘플을 집으므로) 다소 다른 결과가 나올거라 예상된다.
 와 훈련 및 추론 과정은 거의 동일하나, 데이터셋의 종류와 샘플의 위치 및 class 종류 등이 다르다.
데이터셋 폴더 및 파일구조는 다음과 같다.
dataset_cls4는 Image Classification에서 학습에 사용된 데이터셋의 이미지 모음이다.
[https://drive.google.com/file/d/1oHLS-hc3rEsKaUdYM7LlXcM0x1B2o7RN/view?usp=drive_link](https://drive.google.com/file/d/1oHLS-hc3rEsKaUdYM7LlXcM0x1B2o7RN/view?usp=drive_link) 
학습된 최종 best.pt파일은 다음과 같다.
실험결과는 다음과 같다.
그러나 얻은 best.pt를 바탕으로 이를 학습에 사용되지 않은 이미지에 추론을 적용하면, 결과는 다음과 같다.
학습된 해당 추론 과정에 사용된 데이터 테스트 샘플은 [https://drive.google.com/file/d/1LoNQK8oMIK9WmAhTIfAiEpgu13FS6-8J/view?usp=drive_link](https://drive.google.com/file/d/1LoNQK8oMIK9WmAhTIfAiEpgu13FS6-8J/view?usp=drive_link) 인데, 이를 보면 manhole_test_024부터 manhole_test_029까지는 AMR의 슬롯형 보관함에 샘플이 없는 경우인데도 전부 맨홀로 추론됨을 알 수 있다.
이는   경우와 달리 로봇팔에 적용되는 카메라가 다양한 각도와 거리에서 적재함의 샘플을 탐지하는 경우에는 Image Classification이 유효하지 않음을 알 수 있다.

#### [Detection] YOLO Object Detection with manhole mock-up image dataset on slotted storage(슬롯형 보관함) (31064096)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/31064096
**최종 수정**: v20 (2026-04-22 sync)

# 실험목적
앞서  에서 진행한 데이터셋을 바탕으로, AMR의 슬롯형 보관함 위의 맨홀 샘플들에 대해 객체 탐지를 위한 학습을 진행한다. 이를 통해 맨홀 샘플을 학습한 모델의 가중치 파일을 얻고, 이를 이미지와 카메라를 통해 검증한다.

# Background
파인튜닝:  에서 Background 항목의 2.c.iii. Training Method 항목 참고.
이제 객체탐지를 위해 1. 사전학습된 모델 가중치(yolo26n.pt)를 불러와서 2. 레이어 동결 없이(`model.freeze()` 호출 없음 → 전체 레이어 학습 가능) 3. 사용자 정의된(여기서는 AMR의 슬롯형 보관함 위의 맨홀 샘플 이미지) 데이터셋을 활용하여 4. 학습률을 설정하는 방식(`lr0=0.01`)으로 진행하는 파인튜닝을 진행할 예정이다. 즉, 사전학습 가중치를 초기값으로 사용 + 전체/대부분 레이어에 새 데이터로 추가 학습을 적용하는 것이다.
파라미터: 모델 파라미터라고도 부르며, 모델이 주어진 샘플에 대해 예측을 할때 필요한 것이 파라미터이다. 파라미터는 데이터로부터 추정되는 것이며, 임의로 조정이 불가능하다. 또한 학습 후에, 모델의 일부로서 저장되는 것도 특징이다. 대표적인 것이 모델의 가중치(weights)이다. [https://ittrue.tistory.com/42#google_vignette](https://ittrue.tistory.com/42#google_vignette) 
하이퍼파라미터: 모델에 설정하는 변수로서, 학습률(learning rate), 가중치 초기화, 에포크 수(훈련 반복 횟수) 등이 있다. 파라미터와 결정적 차이는 개발자에 의해 임의로 조정이 가능하다는 것이다. 대표적인 예로는 학습률, 에포크 수, 가중치 초기화 등이 있다. 
[https://ittrue.tistory.com/42#google_vignette](https://ittrue.tistory.com/42#google_vignette) 
픽셀 좌표 및 정규화된 좌표 추출 및 계산:  참고.

# 실험과정
먼저 실험에 쓸 라벨링된 데이터셋을 불러온다.
[https://drive.google.com/file/d/15eaUsWZ5AQxbJsaXq06AZ7B-sQYOp7Ol/view?usp=drive_link](https://drive.google.com/file/d/15eaUsWZ5AQxbJsaXq06AZ7B-sQYOp7Ol/view?usp=drive_link)
이제 이 데이터셋을 파인튜닝 방식으로 학습시킨다.
training.py 코드를 실행시킨다.
여기서 하이퍼파라미터를 지정하여 다음과 같은 변수들을 모델에 적용할 수 있다.

- 
batch: 한번에 학습하는 이미지 수

- 
epoch: 전체 데이터셋에 대해 모델이 몇번 학습을 완료했는지를 나타내는 척도.

- 
lr0 & lrf: 학습률(Learning Rate) 조정

  - 
lr0(Initial Learning Rate): 시작시의 학습률. 0.01이 일반적.

  - 
lrf(Final Learning Rate Factor): 최종 학습률을 결정하는 비율이다. 최종 학습률은 lr0 * lrf로 계산된다.

  - 
초기에는 높은 학습률(0.01)로 시작해 최적점 근처를 찾고, 후반에는 학습률을 감소시켜(lr0 * lrf, ex: 0.01*0.01=0.0001)수렴하는 지점을 정밀하게 찾는다.

- 
데이터 증강(Augmentation) 파라미터: 모델이 다양한 각도/거리/조명에 강인해지도록 데이터를 "인위적으로 변형"하는 설정. 색상, 기하학적 증강등이 있다.

  - 
색상 증강: 조명 변화에 영향을 덜 받도록 학습시킴.

    - 

  - 
기하학적 증강: 카메라 각도 및 거리변화 등 기하학적 변화에 영향을 덜 받도록 학습시킴.

    - 
이후 학습한 모델의 가중치(weight) 파일을 얻은 뒤, 이를 바탕으로 결과값들을 평가 지표에 따라 분석한 뒤, 이를 훈련에 사용되지 않은 동일 클래스에 대한 이미지들과, 카메라로 객체 사진을 실제 촬영해서 탐지가 되는지를 확인하여 검증한다.

# 평가지표
mAP, Precision, Recall, F1, IoU 등이 있다.

- 
IoU (Intersection over Union)

  - 
  - 
의미: 예측한 bounding box와 실제 bounding box의 겹치는 정도

  - 
범위: 0.0(완전 불일치) - 1.0(완전 일치)

  - 
임계값: 보통  이면 True Positive 로 간주.

- 
Precision(정밀도)

  - 
  - 
의미: 탐지했다고 한 것들 중 실제로 맞은 비율. 높을수록 오탐지(False Positive)가 적다.

- 
Recall(재현도)

  - 
  - 
의미: 실제 객체 중 제대로 찾아낸 비율. 높을수록 미탐지(False Negative)가 적음.

- 
F1 score

  - 
  - 
정밀도와 재현도의 조화평균으로 오탐지와 미탐지의 균형을 맞추는 역할을 한다.

- 
mAP(mean Average Precision)

  - 
AP(Average Precision): Precision-Recall(정밀도-재현율) 곡선 아래의 면적으로, 면적이 클수록 모델이 더 많은 객체 탐지시에도 예측을 정확하게 한다는 의미.

  - 
mAP: 모든 클라스들에 대한 AP 평균값으로, 전체적인 탐지 성능을 나타낸다. 해당 실험의 경우 class는 1개(manhole)이므로, mAP와 AP는 동일한 값을 지닌다.
여기서 mAP를 파악하려면 Precision-Recall Curve에 대해 알아야 한다.

- 
Precision-Recall Curve(정밀도-재현율 곡선)

  - 
**평균 정밀도(Average Precision):** 정밀도-재현율 곡선(Precision-Recall Curve) 아래의 면적을 계산하여 나온 값으로, 모델의 정밀도 및 재현율 성능을 통합하여 하나의 값으로 제공한다.

  - 
**성능 측정:** 모델이 특정 클래스를 정확하게, 빠짐없이 탐지하는지를 하나의 값(0~1 사이)으로 나타낸다.
추가적으로는  에서도 활용되었던 혼동행렬(Confusion Matrix)도 평가지표에 들어가는데, 모델이 각 클라스를 예측하는 상황에서 나올 수 있는 경우수인 TP, TN, FP, FN에 대한 정보를 제시한다. Class가 1개인 경우의 각 항목은 다음과 같다.

- 
TP(True Positive): 학습한 모델이 맨홀 샘플의 class를 정확하게 탐지함.

- 
TN(True Negative): 학습한 모델이 맨홀 샘플이 아닌 것을 맨홀 샘플이 아니라 정확히 탐지함.

- 
FP(False Positive): 학습한 모델이 맨홀 샘플이 아닌 것을 맨홀 샘플이라 탐지함.

- 
FN(False Negative): 학습한 모델이 맨홀 샘플인 것을 맨홀 샘플이 아니라 분류함.

# 실험결과
학습 후 결과값은 다음과 같다.
학습한 모델의 가중치: 
학습 후 모델의 가중치(weight), 혼동 행렬, 기타 결과 graph 등의 폴더(train3)는 다음과 같다.
[https://drive.google.com/file/d/1Tsm1vB3_3QElxAZwiE6Q1Z5t5N58fxEp/view?usp=drive_link](https://drive.google.com/file/d/1Tsm1vB3_3QElxAZwiE6Q1Z5t5N58fxEp/view?usp=drive_link) 
폴더 내 각 지표들을 분석해보면 다음과 같다.

## **Precision-Recall Curve** (정밀도-재현율 곡선)
현재 overfitting(과적합) 이슈 발생.
현재 mAP값은 거의 100%에 가깝게 보여 이론적으로는 우수한 모델로 판단될 수 있으나, 실제 논문이나 산업 현장에서는 노이즈, 조명 변화, 배경 다양성 등으로 인해 곡선이 다소 둥글게 나오거나 계단 형태를 띠는 것이 일반적. 
이 경우는 Overfitting(과적합)이 발생했다 봐야 하는데, 그 근거는 다음과 같다.
학습(train) 데이터와 검증(val)데이터가 지나치게 비슷한 경우, 학습 데이터에서는 높은 정밀도와 재현율을 보이지만, 이는 달리 말해 학습 데이터의 패턴을 지나치게 세부적인 것까지 학습하는 부작용을 낳게 된다. 즉, 모델이 작은 변화에도 민감해지게 되어, 실제 환경의 작은 변화에도 예측이 흔들리는 결과를 낳게 된다.
해결방안: 
train, val, test 폴더 분할
현존 val 데이터 대신에 실제 로봇팔이 있는 세트장에 슬롯형 보관함을 두고, 거기에 맨홀 샘플을 두어 측정한 걸 val자료로 쓴다. test 폴더도 그러한 방식으로 자료 준비. 단, train, val, test 어느 경우도 동일 이미지를 재사용하는 것은 절대 금물.
이 경우는 Overfitting 이슈를 해결할 수 있으나, 예상되는 mAP가 지나치게 낮아질 가능성도 있다(Underfitting). 실험을 해봐야 알수 있음.(정밀도-재현율 곡선뿐만 아니라 혼동 행렬도 현재는 Recall이 1.0으로 지나치게 높음.)

- 
실제 환경에서는 조명 변화, 가림, 각도, 배경 복잡도 등으로 인해 **어떤 모델도 100% Recall 을 지속적으로 달성하기 어렵다.**

- 
특히 학습 초기 (epoch 1~10) 부터 Recall=1.0 이라는 것은 **검증 세트가 학습 세트와 지나치게 유사**하거나 **너무 쉬워서** 모델이 "외운" 결과일 가능성이 높음.)
=>결정사항(회의 이후)
현재 학습 및 추론 결과로 프로젝트 진행(Overfiting 이슈가 크게 중요하지 않을것으로 추정)

# 우리 프로젝트 적용 방안
[https://drive.google.com/file/d/10-FloCtZD8872mcU385cBycNSjgiIQzU/view?usp=drive_link](https://drive.google.com/file/d/10-FloCtZD8872mcU385cBycNSjgiIQzU/view?usp=drive_link) 
이미지 추론폴더 자료.
나머지 내용은 추후 갱신예정.

#### LLM 도입 시나리오 (1769555)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/1769555
**최종 수정**: v3 (2026-04-19 sync)

### 어디에 연동할 수 있는가?

- 
LLM은 응답 속도가 느리기 때문에 **실시간성이 중요한 단계에서는 적용하기 어려움**(로봇 제어 같은 부분)

- 
이를 고려하면 아래와 같은 항목에서 사용할 수 있을 것으로 예상

- 

### Text-To-SQL 테스트
install Ollama
Requirements

### 참고
[https://vanna.ai/docs](https://vanna.ai/docs)  
[https://ollama.com/](https://ollama.com/)

#### Exploring various VLA models (26248375)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26248375
**최종 수정**: v13 (2026-04-19 sync)

**VLA 모델 비교 문서**
작성일:  
목적: 사형 주조 공정 VLA 적용을 위한 모델 선정 검토
현재 환경: AI 서버 GPU VRAM 12GiB / Raspberry Pi + 로봇팔

## 0. 서버 제약 정리 

****
| 서버 제약 정리 |
|---|
****
****
****
| 항목 | 스펙 | 영향 |
| GPU | RTX 2080 Ti | 7B 모델은 4-bit 양자화 필요 |
| RAM | 32GB | 모델 로딩/추론 충분 |

## 1. 모델 개요 비교

****
****
****
****
****
| 항목 | openpi (π0) | OpenVLA-7B | RT-2 | RoboVLMs | Octo | ACT | Diffusion Policy | SmolVLA |
|---|---|---|---|---|---|---|---|---|
****
| 개발처 | Physical Intelligence | Stanford / UC Berkeley | Google DeepMind | 커뮤니티/연구 | UC Berkeley 외 | Hugging Face (LeRobot) | Hugging Face (LeRobot) | Hugging Face (LeRobot) |
****
****
| 공개 여부 | 오픈소스 | 오픈소스 | 비공개 | 오픈소스 | 오픈소스 | 오픈소스 | 오픈소스 | 오픈소스 |
****
| 파라미터 수 | ~3B | 7B | 55B | 백본에 따라 다름 | ~90M | ~80M | ~300M | 450M |
****
| 구조 | VLM + Flow Matching | LLaMA 기반 VLM | PaLI-X / PaLM-E | VLM + Action Head | 소형 Transformer |   |   | SmolVLM2 + Flow Matching |
****
| 라이선스 | Apache 2.0 | MIT | 비공개 | 모델별 상이 | Apache 2.0 |   |   | Apache 2.0 |
****
| 파인튜닝 지원 | ✅ | ✅ |   | ✅ | ✅ |   |   | ✅ |
****
| 구현 프레임워크 | JAX (PyTorch 포트 존재) | PyTorch | 비공개 | PyTorch | JAX / PyTorch |   |   | PyTorch (LeRobot) |

- 
비교적 경량 모델 (100M ~ 450M)인 Octo와 huggingface LeRobot (ACT, Diffusion Policy, SmolVLA) 에 대해서 실험 예정 

## 2. 모델별 상세

### 2-1. openpi (π0)
**개요**
Physical Intelligence가 자사 로봇 플랫폼용으로 개발한 VLA 모델. 7개의 PI 로봇 플랫폼 + Open X-Embodiment 데이터로 사전학습. Flow Matching 기반 Action 생성 방식 채택.
**두 가지 변형**

- 
`π0 base`: 표준 사전학습 모델, Zero-shot 추론 및 파인튜닝 모두 지원

- 
`π0-FAST base`: 더 높은 언어 지시 추종 성능, 추론 비용 약 4~5배 증가
**장점**

- 
Flow Matching으로 부드러운 연속 동작 생성

- 
파인튜닝에 1~20시간 분량의 데이터로 충분

- 
PyTorch 포트를 통한 접근 가능
**단점**

- 
원래 Physical Intelligence 자사 로봇 기준으로 개발 → 타 플랫폼 일반화 불확실

- 
기본 구현이 JAX 기반 (PyTorch 포트는 비공식)

- 
~3B 파라미터로 fp16 기준 약 6GiB, 추론 오버헤드 포함 시 12GiB에서 빠듯
**12GiB 환경 사용 가능 여부**
⚠️ **조건부 가능** — fp16 로드 시 경계선. bfloat16 + device_map 설정 필요. π0-FAST는 추론 비용이 높아 불리.

### 2-2. OpenVLA-7B
**개요**
Stanford + UC Berkeley가 개발한 7B 파라미터 VLA 모델. LLaMA 기반 언어 모델에 시각 인코더를 결합. Open X-Embodiment 데이터셋으로 사전학습.
**장점**

- 
풍부한 언어 이해 능력 (7B LLM 백본)

- 
오픈소스 가중치 + 파인튜닝 스크립트 공식 제공

- 
다양한 로봇 플랫폼 데이터로 사전학습
**단점**

- 
**bitsandbytes 양자화와 호환되지 않음** (모델 내부에서 `.to()` 호출)

- 
fp16 기준 약 14GiB → 12GiB 서버에서 전량 GPU 적재 불가

- 
추론 속도가 Octo 대비 느림
**12GiB 환경 사용 가능 여부**
⚠️ **조건부 가능** — `max_memory` 설정으로 CPU 오프로드 필요. 추론 속도 저하 감수해야 함. 양자화 미지원으로 메모리 최적화에 제약.

- 
`max_memory={0: "10GiB", "cpu": "48GiB"}`

### 2-3. RT-2
**개요**
Google DeepMind가 개발한 55B 파라미터 VLA 모델. 웹 스케일 데이터로 사전학습된 PaLI-X / PaLM-E를 백본으로 사용. 웹 지식을 로봇 행동으로 직접 전이하는 능력이 핵심.
**장점**

- 
웹 지식 기반의 높은 일반화 능력

- 
본 적 없는 물체에 대한 추론 가능 ("썩은 음식을 골라내라" 등)

- 
가장 높은 수준의 언어-행동 연결 성능
**단점**

- 
**모델 가중치 비공개** → 직접 사용 불가

- 
**API도 공식 제공 없음**

- 
55B 파라미터 → 추론에 고사양 멀티 GPU 인프라 필요

- 
파인튜닝 불가
**12GiB 환경 사용 가능 여부**
 **불가** — 비공개 모델로 접근 자체가 불가능. 논문 및 벤치마크 참고용으로만 활용.

### 2-4. Octo
**개요**
UC Berkeley 외 공동 연구팀이 개발한 소형 VLA 모델 (~90M 파라미터). Open X-Embodiment 데이터셋으로 사전학습. 비트랜스포머 기반 경량 구조.
**추론 속도 (NVIDIA 4090 기준)**

| 모델 | 추론 속도 |
|---|---|
| Octo-Base | 13 it/s (13 Hz) |
| Octo-Small | 17 it/s (17 Hz) |
**장점**

- 
매우 작은 모델 크기 → 12GiB에서 여유롭게 실행

- 
추론 속도 빠름 → 실시간 로봇 제어에 적합

- 
파인튜닝 파이프라인 잘 정비됨

- 
다양한 로봇 폼팩터 지원 (Action Head 교체 방식)
**단점**

- 
모델이 작은 만큼 언어 이해/추론 능력이 VLM 기반 대비 낮음

- 
복잡한 언어 지시 처리 한계

- 
VLM 수준의 일반화는 어려움
**12GiB 환경 사용 가능 여부**
✅ **가능** — fp32에서도 여유롭게 실행. 현재 환경에서 가장 안정적으로 운용 가능한 모델.

### 2-5. RoboVLMs
**개요**
단일 모델이 아닌 **프레임워크**. LLaVA, InternVL 등 기존 VLM을 백본으로 선택하고 Action Head를 붙여 VLA를 구성하는 방식. 백본 교체가 자유로워 연구/실험에 적합.
**학습 방식**
모방학습(Behavior Cloning) 기반. VLM 백본의 사전학습 지식을 활용하여 상대적으로 적은 시연 데이터로 파인튜닝 가능.
**장점**

- 
백본을 자유롭게 교체 → 작은 모델 선택 시 12GiB 환경에서도 실행 가능

- 
최신 VLM 발전을 즉시 로봇에 적용 가능

- 
강한 언어 이해 능력 활용 가능 (불량 판단 등 추론 태스크에 유리)
**단점**

- 
완성된 모델이 아니라 직접 구성해야 함

- 
사전학습된 로봇 가중치 없음 → 처음부터 학습 필요

- 
문서화 및 커뮤니티 지원 부족

- 
백본 크기에 따라 VRAM 요구량이 크게 달라짐
**12GiB 환경 사용 가능 여부** 
⚠️ **조건부 가능** — 경량 백본(3B 이하) 선택 시 가능. 단, 처음부터 학습이 필요해 시연 데이터 구축 부담이 큼.

- 
Backbone: OpenGVLab/InternVL2-2B

### 2-6. SmolVLA
**개요**
Hugging Face LeRobot 팀이 개발한 450M 파라미터 소형 VLA 모델. SmolVLM2-500M을 VLM 백본으로 사용하고, Flow Matching 기반 Action Expert(~100M)를 결합. 소비자 하드웨어에서도 실행 가능하도록 설계.
**아키텍처 특징**

- 
시각 토큰을 프레임당 64개로 제한 (일반 VLM 대비 1/16)

- 
VLM 중간 레이어 특징만 사용 (전체의 약 50%) → 연산량 절반

- 
비동기 추론 지원 → 일반 추론 대비 태스크 완료 시간 30% 단축
**성능 (실물 로봇 기준)**

- 
Pick-place, Stacking, Sorting 태스크에서 약 78% 성공률

- 
사전학습 없이 파인튜닝 시 51.7% → 사전학습 후 파인튜닝 시 78.3%
**장점**

- 
450M으로 매우 작음 → CPU, 단일 GPU, MacBook에서도 실행 가능

- 
LeRobot 프레임워크 기반으로 파인튜닝 파이프라인이 잘 정비됨

- 
비동기 추론으로 실시간 응답성 우수

- 
커뮤니티 데이터셋 기반 → 다양한 로봇 환경에 적용 가능

- 
30k 에피소드 미만으로 사전학습 → 재현 가능한 데이터 규모
**단점**

- 
모델이 작은 만큼 복잡한 언어 추론은 VLM 기반 대형 모델보다 떨어짐

- 
비교적 최신 모델로 실사용 레퍼런스가 적음

- 
JAX가 아닌 PyTorch/LeRobot 생태계에 의존
**12GiB 환경 사용 가능 여부**
✅ **가능** — 450M으로 VRAM 여유가 매우 크며, 파인튜닝도 12GiB 내에서 가능.

## 3. 종합 비교표

| 항목 | openpi (π0) | OpenVLA-7B | RT-2 | Octo | RoboVLMs | SmolVLA |
|---|---|---|---|---|---|---|
| 12GiB 추론 가능 | ⚠️ | ⚠️ |   | ✅ | ⚠️ | ✅ |
| 12GiB 파인튜닝 가능 | ⚠️ |   |   | ✅ | ⚠️ | ✅ |
| 언어 이해 능력 | 중 | 상 | 최상 | 하 | 백본 의존 | 중 |

- 
| 추론 속도 | 중 | 하 |   | 상 (13~17Hz) | 백본 의존 | 상 |
| 파인튜닝 난이도 | 중 | 중 | 불가 | 하 | 상 | 하 |
| 필요 시연 데이터 | 소 (1~20h) | 중 | 불가 | 중 | 대 | 소 |

- 
| 커뮤니티/문서 | 중 | 상 |   | 상 | 하 | 상 |
| 오픈소스 | ✅ | ✅ |   | ✅ | ✅ | ✅ |

## 4. 현재 환경 기준 사용 가능 여부 요약

| 모델 | 판정 | 이유 |
|---|---|---|
****
| SmolVLA | ✅ 권장 | 450M으로 VRAM 여유, 파인튜닝까지 12GiB 내 가능, LeRobot 파이프라인 정비 |
****
| Octo | ✅ 가능 | ~90M으로 가장 가볍고 안정적, 추론 속도 13~17Hz로 실시간 제어 적합 |
****
| ACT (LeRobot) |   | Huggin |
****
| openpi (π0) | ⚠️ 조건부 | fp16 약 6GiB이나 오버헤드 포함 시 경계선, 타 플랫폼 일반화 불확실 |
****
| OpenVLA-7B | ⚠️ 조건부 | bitsandbytes 미지원, CPU 오프로드 필요, 추론 속도 저하 |
****
| RoboVLMs | ⚠️ 조건부 | 경량 백본 선택 시 가능하나 처음부터 학습 필요 |
****
| RT-2 | 불가 | 비공개 모델, 가중치 접근 불가 |

## 5. 권장 적용 방향

## 6. 시스템 구성 (Raspberry Pi + AI 서버 환경)

- 
추론은 AI 서버에서 담당, Raspberry Pi는 실행만 수행

- 
유선 LAN 환경 권장 (네트워크 지연 최소화)

- 
SmolVLA 비동기 추론 활용 시 제어 응답성 개선 가능

# 7. VLA 적용 가능한 포인트 

****
****
****
| 이거 위치 | 현재 문제 | VLA 로 해결 가능한 것 |
|---|---|---|
| RobotArm - 패턴집기 | 여러 패턴 종류마다 파지 방식이 다름 | 시각 정보로 패턴 종류 인식 후 자동으로 grasp 조정 |
| AMR 위 적재된 주물 인식 | AMR 이 고정된 위치로 도착한다는 보장이 없음. (docking server 로 어느 정도 해결 가능) | RGB-D 카메라로 주물의 실제 위치/자세를 실시간 인식 후 로봇 팔 접근 경로 보정 |
| 적재 선반 특정 위치에 적재 | 똑같이 하드코딩으로 적재 선반 특정 위치를 지정해서 명령해도 (같은 각도의 높이만 다른 위치) 안 되는 기술적 문제 | 시각 피드백으로 선반의 현재 빈 위치와 높이를 인식, 좌표 하드코딩 없이 동적으로 적재 위치 결정 |

#### VLA 적용 가능성 간이 실험 로드맵 (26869945)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26869945
**최종 수정**: v3 (2026-04-19 sync)

# 모델 
선택 모델: Octo, LeRobot (ACT, DiffusionPolicy)
선택 이유: 

- 
언어 지시 불필요, 시연 데이터만으로 학습                                                                                  

- 
11GB VRAM에서 양자화 없이 바로 돌아감     

- 
RealSense D435if 이미 있어서 파이프라인 연결 쉬움   

# 실험 

## 환경 세팅 

- 
  확인할 것:                                                                                                                  

  - 
RealSense D435if → RGB + Depth 동시 스트림 테스트

  - 
Robot Arm ↔ ROS2 ↔ LeRobot 토픽 연결       

## 데모 데이터 수집 
목표: 50~100개 demonstration 

****
****
| 항목 | 내용 |
|---|---|
| 방법 | 텔레오퍼레이션으로 직접 시연 녹화 |
| 입력 | RGB-D 이미지 + 로봇 팔 joint 상태 |
| 출력 | 각 시점의 action (joint angle) |

- 

- 
| 다양성 | 선반 높이 3~4 단계좌우 위치 변화 포함 |

## 학습 

- 
RTX 2080 Ti 기준 약 2~4시간 소요 

## 양자화 (Optimization)
ACT 자체는 ~80M params라 11GB에서 양자화 불필요하지만, 추론 속도 개선 목적으로는 적용 가능: 

# 평가 지표

#### [기술 검증 계획서] 주물 이송-적재 공정 단계별 최적화 방안 (13435172)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13435172
**최종 수정**: v5 (2026-04-19 sync)

### 1. 검증 개요

- 
**목적:** 이송 후 로봇 암의 파지 안정성(1단계)과 최종 적재 시 공간 및 제어 효율성(2단계)을 단계별로 검증하여 전체 자동화 공정의 신뢰성을 확보함.

### 2. [STEP 1] 이송 후 파지(Grasping) 효율화 검증
**상황:** 이송된 주물을 보관 구역에서 로봇팔이 정확하게 집을 수 있도록 하는 방안 검토

- 
**검증 대상:** ****

**

1. 
**위치 정밀도(Positioning Accuracy):** 이송 완료 후 슬롯 내 주물의 유격 발생 범위 측정.

1. 
**파지 성공률(Pick Success Rate):** 비전 센서나 사전 정의된 좌표를 통해 슬롯 내 주물을 집어 올릴 때의 에러율 분석.

1. 
****

실제 layout에서 벽면과 얼마정도로 떨어졌는지 로봇팔의 위치는 어디에 있어야 안전한지, 실험 보고서 최대한 자세히 작성

### 3. [STEP 2] 주물 보관 랙(Rack) 적재 방식 검증
**상황:** 보관함에서 꺼낸 주물을 최종적으로 랙에 적재하는 아키텍처 비교

#### **안 A. 선반형 적재 (직선형)**

- 
**특징:** 실제 공장의 표준 방식이나 로봇 가동 범위 제약 존재.

- 
**검증 포인트:** * **도달 범위(Reachability):** 제코봇의 관절 각도 한계 내에서 선반의 모든 층과 깊이에 적재가 가능한지 확인.

  - 
**기하학적 분석:** 특정 높이나 깊이에서 발생하는 특이점(Singularity) 구간 식별.
관절 각도와 범위를 생각했을때 구현 가능한지 검증 
필요함
보관 랙
관절 각도와 범위를 생각했을때 구현 가능한지 검증 
필요함

#### 슬롯형 바구니를 활용한 맨홀 적재 시나리오 검증 (13631684)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13631684
**최종 수정**: v19 (2026-04-19 sync)

## 1. 목적

- 
Jetcobot의 반복 정밀도 오차(약 0.5~1.5mm)와 낮은 페이로드(250~400g)를 고려할 때, 수직 적재 방식은 누적된 오차로 인해 전체 적재물이 도미노 처럼 무너질 위험이 큼. 따라서 맨홀을 개별적으로 수납할 수 있는 **슬롯형 바구니(Slotted Basket)** 방식을 도입하여, 로봇의 오차를 물리적으로 수용하고 적재 안정성을 확보하기 위함.

# 2. Background

### 2.1 기존 방식의 한계 (Stacking)

- 
**내용:** 산업용 로봇은 고정밀 제어를 통해 팔레트 위에 물체를 층층이 쌓는 '단순 적재' 방식을 주로 사용함.

- 
**문제점:** Jetcobot과 같은 경량 로봇은 정밀도가 낮아 층이 높아질수록 오차가 누적됨. 또한, 물체가 가벼워 적재 시 미세한 충격에도 전체 적재물이 쉽게 이탈하거나 무너지는 붕괴 위험이 큼.

### 2.2 본 프로젝트의 특이점 (Slotting)

- 
**전략:** '쌓기(Stacking)'가 아닌 **'끼우기(Slotting)'** 방식으로 접근함.

- 
**원리:** 바구니 내부에 독립된 격자(Slot)를 생성하여 맨홀을 하나씩 삽입함. 이는 물리적 벽면이 가이드 역할을 수행하여 이탈을 원천 차단하고 안정성을 최우선으로 확보함.

## 3. 기술 스펙 및 적용 가능성

- 
****

- 
**파지 방식 (Side-Gripping):** 맨홀의 넓은 윗면 대신 좁은 원형 측면(직경 방향)을 가로로 파지하는 방식 채택.

- 
**보관 방식 (Multi-Slotting):** 다수의 칸막이가 있는 대형 슬롯형 적재 바구니 채택.

  - 
**적용 가능성:** 슬롯 벽면이 가이드 역할을 하여 적재물이 서로 부딪히지 않으며, 수직 적재 시 발생하는 '누적 오차에 의한 붕괴' 위험을 근본적으로 제거함.

- 
**한계 및 대안:** 슬롯형은 공간 효율이 낮을 수 있으나, AMR 상단 2단 적재 프레임 설계를 통해 처리량을 극대화할수있음. 

## 4. 실험 환경 및 평가 지표

- 
**장비:** Jetcobot, 측면 파지용 커스텀 그리퍼 팁, 대용량 다단 슬롯 바구니, 맨홀 프로토타입(250g), AMR(Pinkypro), AprilTag

- 
**입력 데이터:** ?

### 4.1 평가 지표 정의

- 
**파지 성공률 (Gripping Success Rate):** 측면 파지 시 미끄러짐 없이 안정적으로 들어 올린 비율.

- 
**적재 정확도 (Placement Accuracy):** 슬롯 내부 정중앙에 안착된 정도 (그리퍼의 Self-centering 성능 확인).

- 
**관절 부하 (Motor Torque):** 측면 파지 시 관절 4, 5, 6번에 가해지는 토크량 (수직 압착 대비 부하 감소율 측정).

- 
**적재 용량 (Storage Capacity):** 바구니 규격 내 슬롯 최적화를 통한 최대 적재 수량.

### 4.2 실험 내용

- 
**실험 1 (측면 파지 안정성):** 다양한 오차 범위(0~10mm)에서 그리퍼가 맨홀 중심을 잡아내는 '자기 중심화' 범위 측정.

- 
**실험 2 (슬롯 삽입 테스트):** 슬롯 유격(5~15mm) 변화에 따른 삽입 성공률 및 하역(Picking) 시의 간섭 여부 검증.

## 5. 우리 프로젝트 적용 판단

- 
**최종 적용 판단:** **채택** (측면 파지를 통해 8mm 오차 수용 및 250g 안정적 이송 가능 확인).

- 
**공정 위치:** 공정 최종 단계인 '출하 대기 및 다량 적재' 파트.

- 
**추가 하드웨어:** * **커스텀 그리퍼 팁:** 측면 곡면을 감싸 쥘 수 있는 형태의 3D 프린팅 팁.

  - 
**대형 슬롯 바구니:** 다수의 맨홀을 세워서 보관할 수 있는 격자형 구조체.

  - 
**센서:** 창고 슬롯별 점유 상태 확인용 적외선/초음파 센서 어레이.

- 
**데이터 수집:** 측면 파지 시 그리퍼와 맨홀 테두리의 정렬 상태 인식을 위한 학습 데이터 확보 필요.

#### [실험 보고서] 로봇 암 정밀도 보완 및 슬롯형 보관 시스템 실효성 검증 (14976297)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/14976297
**최종 수정**: v24 (2026-04-19 sync)

1 공정 1 제작 1 상차가 정해져서 실험2,3번은 수행하지 않아도 됨 (다중 적재 실험)

### **1. 실험 목적 **
로봇암이 파지할때 발생하는 물리적 오차를 최소화하고 효율적인 맨홀 수납을 고려한 맨홀 보관함 채택을 위해 **슬롯형 보관함 도입의 타당성 검증이 필요**하다. 

### **2. [실험 1] 단일 맨홀 파지/적재 정밀도 검증 (Case A)**
지지 구조 없이 단일 맨홀을 **로봇암이 안정적으로 집고 정확하게 제어할 수 있는지**를 선확인하는 실험이다. 

### 2.1 실험 개요

- 
**실험 목적:** 지지 구조물이 없는 상태에서 로봇 팔이 맨홀 1개를 안정적으로 집고 정확하게 움직일 수 있는지 확인한다.

  - 
**실험 환경:** 평평한 작업대, 단일 맨홀(Target Object), 로봇 팔 및 그리퍼.

  - 
**실험 방법:** 평평한 바닥에 맨홀 1개를 세워두고, 미리 정해둔 좌표를 기준으로 총 5회 반복하여 집고 지정 위치에 내려놓는다.

### 2.2 실험 절차
본 실험은 랙 상단에 있는 장애물에 부딪히지 않도록, 먼저 내려놓고 이후 밀어서 위치를 맞추는 방식을 사용한다.

- 
**초기화:** 로봇 팔을 시작 위치로 이동시키고, 맨홀을 정해진 위치에 똑바로 세운다.

- 
**접근(Approach Phase):** 미리 정해진 대기 위치에서 맨홀이 있는 위치까지 이동한다.

- 
**파지(Grasping Phase):** 그리퍼를 이용해 맨홀을 잡는다.

- 
**반송 (Grasping & Transport):** 맨홀을 잡은 상태로 목표 위치 위까지 이동한다.

- 
****

  - 
1차 안착**:** 랙 내부로 직접 진입하는 대신, 입구 근처 바닥면에 맨홀을 먼저 내려놓음.

  - 
수평 푸싱/정렬 : 그리퍼로 맨홀 옆면을 살짝 밀어 최종 위치에 맞춘다.

- 
**이탈 및 복귀:** 맨홀을 놓은 후, 로봇을 시작 위치로 되돌린다.

- 
**반복:** 위 과정을 총 5회 반복

### **2.3 실험 영상**

[https://drive.google.com/file/d/1ZxIkhuOGsIdaJUsLBcoxGUpDwWxeoyRh/view?usp=drive_link](https://drive.google.com/file/d/1ZxIkhuOGsIdaJUsLBcoxGUpDwWxeoyRh/view?usp=drive_link)  [https://drive.google.com/file/d/1N7DaPj3MuQpmzdkG7X6ylm-rhkIN7D-K/view?usp=drive_link](https://drive.google.com/file/d/1N7DaPj3MuQpmzdkG7X6ylm-rhkIN7D-K/view?usp=drive_link)  

### 2.3 실험 결과 (검증 항목별 분석) 
시도 횟수 20회 기준
설정한 오차 범위 : 육안으로만 확인했을때 테이프 밖으로 크게 벗어나지않음

| 그리퍼 좌우 압력 불균형에 의한 미끄러짐 및 튕김 현상 → 없음로봇이 접근할 때의 진동이 맨홀이 쓰러지는 데 영향이 있는가? → 없음 관절 잔류 진동이 최종 안착 각도 및 좌표 오차에 미치는 영향 → 없음로 바닥면과의 마찰로 인해 맨홀이 기울어지거나 튕기는 현상 →  없음 |
|---|
결과 : 지지 구조 없이 수직으로 서있는 맨홀의 파지 및 적재가 안정적으로 수행 가능함을 확인하였음.

### 2.4 종합 결론 및 개선 사항
본 실험을 통해 지지 구조물(렉)이 없는 상태에서, 미리 설정한 위치를 기준으로 맨홀 1개를 안정적으로 집고 옮길 수 있음을 확인하였다.
특히 접근, 파지, 이송, 적재 및 정렬 전 과정에서 맨홀이 쓰러지거나 미끄러지는 등의 문제 없이 작업이 수행되었으며,로봇 팔이 단일 물체를 다루는 데에는 충분한 정확도와 안정성을 가지고 있음을 확인하였다.
또한 맨홀을 내려놓은 후 밀어 정렬하는 방식으로, 정밀도가 완벽하지 않아도 원하는 위치에 안정적으로 맞출 수 있음을 확인하였다.

### ■ 개선 사항

####      하드웨어 측면

- 
파지 안정성 향상 및 고정을 위해, 그리퍼 핑거 끝단에 추가 파츠를 장착하여 파지 가능 크기 범위를 확장하는 방안을 검토한다.

- 
랙 구조로 인한 공간 제약 및 간섭 요소를 고려하여, 충돌 방지를 위한 로봇 암의 경로 및 동작 제어가 요구된다.

### **3. [실험 2] 슬롯형 적재 공간 + 로봇팔 선반 랙 적재 검증 (Case B)**

- 
**방법:**  슬롯형 적재 공간에 상차된 주물을 로봇팔이 Picking한 후 적재 공간(1,2,3층)에 적재시킴

- 
**확인 사항:**

  - 
적재 공간에 주물을 랜덤하게 던지듯 상차해도 잡기 충분한 형태로 적재되는지

  - 
로봇팔이 랜덤하게 배치된 주물을 안정적으로 Picking하는지

  - 
로봇팔이 선반 랙에 주물 적재시 안정적으로 Place되는지

- 
**실험 결과:**

  - 
**Picking 안정성:** 하드 코딩된 좌표 기반의 제어임에도 불구하고, 슬롯형 구조의 가이드 효과 덕분에 주물이 랜덤하게 배치된 상황에서도 높은 Picking 성공률을 보임.

  - 
**적재(Place) 정확도:** 단층 및 1층부터 3층까지의 높이별 적재 실험 결과, 각 층의 선반 랙 위치에 주물을 이탈 없이 안정적으로 안착시킴

  - 
**공정 연속성:** 단층 적재에서 한 단계 나아가, 다층 랙 구조에서의 수직 이동 및 적재 공정의 유효성을 확인함.

****
****
| 단층 실험 | 3->2->1층순으로 적재 실험 |
|---|---|
[](https://drive.google.com/file/d/1Cs73EebpUdhLph3V7aMUcJP6DTbzRm6e/view?usp=drive_link)
[](https://drive.google.com/file/d/1JckQ7FNd_5RqcnnaiuD6-BwPZA5IepZI/view?usp=drive_link)
| https://drive.google.com/file/d/1Cs73EebpUdhLph3V7aMUcJP6DTbzRm6e/view?usp=drive_link | https://drive.google.com/file/d/1JckQ7FNd_5RqcnnaiuD6-BwPZA5IepZI/view?usp=drive_link |

- 
**확인 사항 **

****
****
****
| 확인 항목 | 결과 | 비고 |
|---|---|---|
****
| 주물이 랜덤하게 배치된 상황에서 시 파지 가능 형태 | 양호 | 슬롯 구조가 주물의 유동 범위를 제한하여 집는 확률 높임. |
****
| 랜덤 배치 주물에 대한 로봇팔 Picking의 안정성 | 높음 | 안정적인 그리핑 수행 |
****
| 선반 랙 단층 및 1~3층 연속 적재 시 안착 상태 | 성공 | 고층(3층)부터 저층(1층)까지 순차적 적재 시 간섭 없이 안착 |

### **4. [실험 3] 적재 효율성 및 용량 검증 (Optimization)**
**"시스템 안정성을 유지하며 최대 몇 개까지 보관 가능한가?"**

- 
**방법:** 슬롯 간 격벽 두께와 맨홀 간격을 조정하며 Jetcobot의 가동 범위(Reach) 내 최적 배치도 작성.

- 
**확인 사항:**

  - 
**최대 가동 반경($R$):** Jetcobot의 유효 작업 반경 내에서 로봇 암의 관절이 꺾이지 않고(Singularity 방지) 도달 가능한 가장 먼 슬롯 위치 확인.

  - 
**격벽 두께 최적화:** 맨홀 간 간섭을 막으면서도 공간을 최소화할 수 있는 격벽 두께(제안: 3~5mm) 결정.

  - 
**최종 용량 산출:** * 단층 배치 시: 가로 202mm 보관함 기준 4개.

    - 
다단(Multi-layer) 배치 시: AMR 상단 프레임을 활용하여 2단 적재 시 최대 8개~12개 가능 여부 검토.

### **5. 결과 요약 및 평가 지표**

****
****
****
****
| 검증 항목 | Case A (무지대) | Case B (슬롯형) | 평가 기준 |
|---|---|---|---|
****
****
| 파지 성공률 | 로봇 오차에 매우 민감 (낮음) | 물리적 보정으로 높음 | 95% 이상 성공 시 합격 |
****
****
| 장애물 간섭 | 없음 | 수직 경로 제어로 해결 | 충돌 횟수 0회 목표 |
****
****
| 최대 보관량 | 제한 없음 (불안정) | 규격화된 수량 (안정) | 공간 대비 적재 밀도 산출 |

#### [실험 보고서] 맨홀 주물 이송 및 적재 실험 (슬롯형 바구니 기반) (19071189)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/19071189
**최종 수정**: v3 (2026-04-19 sync)

## 실험 개요
본 실험은 로봇암이 실제 작업 환경에서 맨홀 주물을 안정적으로 이송 및 적재할 수 있는지를 확인하기 위해 수행하였다.
실험에서는 AMR(자율주행 로봇) 위에 슬롯형 바구니를 설치하고,
그 내부에 맨홀 주물을 세로로 끼워 정렬된 상태로 배치하였다.
이후 로봇암이 슬롯 내부의 맨홀을 하나씩 집어
적재 위치로 옮기는 작업을 수행하였다.

## 실험 방법
아직 실제 적재함이 제작되지 않은 상태이므로,
로봇암의 도달 범위를 기준으로 1층, 2층, 3층 높이를 가상으로 설정하였다.
각 층의 높이는 로봇암 관절 기준으로 도달 가능한 위치를 고려하여 설정하였으며,
로봇암은 슬롯형 바구니에서 맨홀을 꺼낸 후
3층 → 2층 → 1층 순서로 각각 적재를 수행하였다.

## 실험 목적
본 실험의 목적은 다음과 같다.

- 
슬롯형 바구니에서 맨홀을 안정적으로 꺼낼 수 있는지 확인

- 
다양한 높이(다층 구조)에서도 로봇암이 적재할 수 있는지 검증

- 
향후 실제 적재함 설계를 위한 기준 데이터 확보

## 실험 영상

## 결론
실험 결과,
로봇암은 AMR 위 슬롯형 바구니에 적재된 맨홀을 안정적으로 파지하고,
가정한 1층, 2층, 3층 위치에 문제없이 적재할 수 있었다.
이를 통해 슬롯형 구조와 다층 적재 방식이 실제 적용 가능함을 확인하였으며,
본 실험 결과를 기반으로 향후 실제 적재함 설계가 가능할 것으로 판단된다.

#### 강사님께 통신 질문 (32636945)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/32636945
**최종 수정**: v1 (2026-04-19 sync)

# Tailscale 환경에서 ROS 통신
ROS는 각 endpoint 별로 연결한다.
Tailscale은 P2P 방식이여서, multicast를 지원하지 않는 구조다.
[https://github.com/tailscale/tailscale/issues/11972](https://github.com/tailscale/tailscale/issues/11972) 
[https://danaukes.com/notebook/ros2/30-configuring-ros-over-tailscale](https://danaukes.com/notebook/ros2/30-configuring-ros-over-tailscale)
그래서 두 가지 방법이 있는데,

1. 
fastdds의 initialPeerslist에 연결할 ip들을 미리 적어두기
locator(ip)를 설정하면, discovery traffic을 그 ip들에 unicast로 보내서 통신이 된다.

1. 
Discovery Server를 구축
Discovery Server를 하나 두고, 연결할 노드들을 Discovery server에 연결하면, 서버가 연결해준다.

### 민경환 강사님의 대답
굳이 VPN까지 쓰지 않아도 된다. 
[netplan을 사용하면 고정 ip를 쓸 수 있다.](https://betwe.tistory.com/entry/Ubuntu-netplan-%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%9C-IP-%EB%B3%80%EA%B2%BD#google_vignette)
→  에 공유기를 나눠주신다고 하셔서, 공유기 받고 ip 고정할 예정

#### Docker 구현 및 테스트 (33521698)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/33521698
**최종 수정**: v8 (2026-04-22 sync)

작성일:   
목적: AI Server에서 만든 Docker 이미지를 다른 PC에서 동일하게 실행할 수 있는지 검증 
선행 문서: [https://dayelee313.atlassian.net/wiki/x/awLWAQ](https://dayelee313.atlassian.net/wiki/x/awLWAQ)

## 1. 테스트 개요

### 1.1 목적
Docker의 핵심 가치인 **환경 재현성**을 검증한다.  
AI Server에서 개발하고 빌드한 Docker 이미지를 내 PC로 가져와 동일하게 실행되는지 확인한다.
두 머신의 하드웨어 스펙이 다르더라도 본 테스트의 검증 항목(환경 재현성, 운영 편의성)에는 영향을 주지 않는다.  
성능 측정은 제외한다.

### 1.2 검증 항목

| 실험 | 검증 내용 | Docker 기대 효과 |
|---|---|---|
| 실험 1 | 환경 재현성 | AI Server 이미지를 내 PC에서 동일하게 실행 |
| 실험 2 | 크래시 자동 복구 | 프로세스 크래시 시 자동 재시작 |
| 실험 3 | 모델 파일 교체 배포 | 컨테이너 재빌드 없이 모델만 교체 |
| 실험 4 | 의존성 충돌 방지 | 라이브러리 버전 충돌 없이 실행 |

## 2. 테스트 환경 구성

### 2.1 머신 구성

| 구분 | AI Server | 내 PC |
|---|---|---|
| 역할 | 네이티브 개발 + Docker 이미지 빌드 | Docker 이미지 실행 |
| Docker 설치 | ✅ 필요 | ✅ 필요 |
| OS | Ubuntu 24.04 x86_64 | Ubuntu 24.04 x86_64 |
| GPU | GeForce RTX 2080 Ti Rev. A | GeForce RTX 4060 Max-Q / Mobile |
| RAM | 31Gi | 15Gi |

### 2.2 AI Server — 네이티브 개발 환경 구성
AI Server에서 먼저 네이티브로 실행 가능한지 확인한다.  
이 환경이 Docker 이미지로 패키징될 기준 환경이 된다.

- 
결과

  - 
curl로도 확인 가능

### 2.3 AI Server — Docker 이미지 빌드
네이티브 환경과 동일한 환경을 Docker 이미지로 패키징한다.

### 2.4 내 PC — Docker 설치

- 
Docker Engine 설치(on Ubuntu 24.04): [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)

- 
Docker Desktop 설치(on Ubuntu 24.04): [https://docs.docker.com/desktop/setup/install/linux/ubuntu/](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)

  - 
**Docker Desktop = Docker Engine + UI + 편의 기능**

## 3. 실험 1 — 환경 재현성 (이미지 이전)

### 3.1 목적
AI Server에서 빌드한 이미지를 내 PC로 가져와 동일하게 실행되는지 확인한다.  
스펙이 다른 머신에서도 추가 설치 없이 실행 가능한지가 핵심이다.

### 3.2 절차
**AI Server — 이미지 전달**
**내 PC — 이미지 실행**

- 
`Line 18`

  - 
`"내 PC포트:컨테이너 포트"`

  - 
내 PC에서 vscode가 8080포트를 사용하고 있어서 8081로 변경했고, docker container 내부에서 uvicorn으로 서버를 실행할 때 8080포트로 열어주기 때문에 포트포워딩을 해줘야 한다.

### 3.3 결과

| 항목 | AI Server (네이티브) | 내 PC (Docker) |
|---|---|---|

- 
| 추가 패키지 설치 필요 여부 |   | N |
| 설치 중 오류 발생 여부 | Y (여러 의존성 문제) | N |
| 추론 요청 정상 응답 여부 | Y | Y |

- 
| 양쪽 응답 결과 동일 여부 |   | N (GPU가 달라서 약간 다름) |
의존성 문제를 AI Server에서 해결하여 requirements.txt로 저장하고 Dockerfile에 등록하여 이미지 빌드를하면, 내 PC에서는 docker compose로 손쉽게 AI Server와 동일 환경을 세팅할 수 있다.

- 
내 PC 추론 결과

### 3.4 체크포인트

## 4. 실험 2 — 크래시 자동 복구

### 4.1 목적
AI Server 프로세스가 강제 종료되었을 때, 네이티브와 Docker의 복구 과정을 비교한다.

### 4.2 절차
**AI Server (네이티브)**
**내 PC (Docker)**
지속적인 오류인 경우 재시작이 의미 없지만, 일시적인 네트워크 오류와 같은 경우 자동 재시작이 의미 있음.
Docker 환경이 아닌 경우, 개발자가 매 번 직접 재시작 해야함.

### 4.3 결과 기록

| 항목 | AI Server (네이티브) | 내 PC (Docker) |
|---|---|---|
| 크래시 감지 방법 | 수동 확인 필요 | 자동 감지 |
| 재시작 방법 | 수동 재시작 | 자동 재시작 |
| 개발자 개입 필요 여부 | Y | N |

### 4.4 체크포인트

## 5. 실험 3 — 모델 파일 교체 배포

### 5.1 목적
새로운 불량 탐지 모델로 교체할 때, 네이티브와 Docker의 배포 절차를 비교한다.

### 5.2 절차
**AI Server (네이티브)**
**내 PC (Docker)**

### 5.3 결과

- 
다른 버전의 모델로 교체 했을때의 결과

### 5.4 체크포인트

## 5. 결론

- 
3가지 실험 모두 검증 항목을 통과 했고, Docker를 도입하는 것이 타당하다고 판단된다.

- 
AI 모델 뿐만 아니라 파이썬 환경에서 실험을 진행하는 담당자는 사용한 패키지는 반드시 **requirements.txt**로 정리해 두어야 한다. 이미지 빌드의 기준 환경이 되기 때문에, 이 작업이 누락되면 Docker의 환경 재현성 이점이 무의미해짐.

#### (~ing) Kubernetes 구현 및 테스트 (33685526)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/33685526
**최종 수정**: v3 (2026-04-19 sync)

작성일: 
목적: AI Server 3대에 Kubernetes를 적용하여 무중단 운영이 실제로 동작하는지 확인 
선행 문서: [https://dayelee313.atlassian.net/wiki/x/KoC3AQ](https://dayelee313.atlassian.net/wiki/x/KoC3AQ) 

## 1. 테스트 개요

### 1.1 목적
AI Server 3대에 Kubernetes를 적용하여, 서버 장애 상황에서도 모든 모델 추론이 중단 없이 유지되는지 확인한다.  
서버 1대의 하드웨어 스펙이 다르므로 **성능 측정은 제외**하고 무중단 운영 동작 여부 중심으로 검증한다.
본 테스트는 개발 단계에서 Docker로 검증된 이미지를 K8s로 배포하는 운영 단계를 가정한다.  
Docker 테스트 선행 후 진행을 권장한다. (docker_test.md 참고)

### 1.2 검증 항목

| 실험 | 검증 내용 | K8s 기대 효과 |
|---|---|---|
| 실험 1 | 서버 1대 장애 시 자동 폴백 | 나머지 서버의 Fallback Pod로 자동 전환 |
| 실험 2 | 롤링 배포 | 서비스 중단 없이 새 모델 버전 교체 |
| 실험 3 | 자동 복구 | Pod 크래시 시 자동 재시작 |
| 실험 4 | 서비스 디스커버리 | Pod IP 변경 시에도 통신 유지 |

## 2. 테스트 환경 구성

### 2.1 서버 구성

| 구분 | AI Server 1 | AI Server 2 | AI Server 3 |
|---|---|---|---|
| OS | (실제 OS 기재) | (실제 OS 기재) | (실제 OS 기재) |
| GPU | (실제 GPU 기재) | (실제 GPU 기재) | (실제 GPU 기재) |
| RAM | (실제 RAM 기재) | (실제 RAM 기재) | (실제 RAM 기재) |
| K8s 역할 | Worker Node 1 | Worker Node 2 | Worker Node 3 |
서버 1대의 하드웨어 스펙이 다르더라도 본 테스트의 검증 항목(장애 복구, 무중단 배포)에는 영향을 주지 않는다.

### 2.2 Pod 배치 전략
Pod 1개에 모델 1개를 올린다. 각 서버는 Primary Pod 1개와 Fallback Pod 1개를 실행한다.

#### 평상시 라우팅

#### 장애 시 자동 폴백

### 2.3 K8s 클러스터 구성

### 2.4 Deployment 설정 예시

## 3. 실험 1 — 서버 1대 장애 시 자동 폴백

### 3.1 목적
AI Server 1대가 완전히 다운되었을 때, 해당 서버의 Primary Pod가 담당하던 모델 추론이 Fallback Pod로 자동 전환되는지 확인한다.

### 3.2 절차

### 3.3 결과 기록

| 항목 | 결과 |
|---|---|
| AI Server 1 다운 전 모델 A 처리 서버 | AI Server 1 (Primary) |
| AI Server 1 다운 후 모델 A 처리 서버 | (기재) |
| AI Server 1 다운 전 모델 B 처리 서버 | AI Server 2 (Primary) |
| AI Server 1 다운 후 모델 B 처리 서버 | (기재) |
| 폴백 전환 소요 시간 | 초 |
| 폴백 중 요청 실패 발생 여부 | Y / N |
| AI Server 1 복구 후 정상 라우팅 복귀 여부 | Y / N |

### 3.4 체크포인트

## 4. 실험 2 — 롤링 배포 (무중단 모델 업데이트)

### 4.1 목적
새 버전의 모델 이미지로 교체할 때 서비스 중단 없이 배포되는지 확인한다.

### 4.2 절차

### 4.3 결과 기록

| 항목 | 결과 |
|---|---|
| 배포 소요 시간 | 초 |
| 배포 중 요청 실패 발생 여부 | Y / N |
| 실패 발생 시 실패 횟수 | 회 |
| 롤백 소요 시간 | 초 |
| 롤백 중 요청 실패 발생 여부 | Y / N |

### 4.4 체크포인트

## 5. 실험 3 — 자동 복구 (Self-healing)

### 5.1 목적
AI Server Pod가 소프트웨어 크래시로 종료되었을 때 K8s가 자동으로 재시작하고, 재시작 중 Fallback Pod로 라우팅이 전환되는지 확인한다.

### 5.2 절차

### 5.3 결과 기록

| 항목 | 결과 |
|---|---|
| Pod 종료 감지 소요 시간 | 초 |
| Pod 자동 재시작 소요 시간 | 초 |
| 재시작 중 Fallback Pod로 라우팅 여부 | Y / N |
| 재시작 후 Primary Pod로 복귀 여부 | Y / N |
| 전체 과정 중 요청 실패 여부 | Y / N |

### 5.4 체크포인트

## 6. 실험 4 — 서비스 디스커버리

### 6.1 목적
Pod IP가 변경되어도 서비스 이름으로 통신이 유지되는지 확인한다.

### 6.2 절차

### 6.3 결과 기록

| 항목 | 결과 |
|---|---|
| 재시작 전 Pod IP | (기재) |
| 재시작 후 Pod IP | (기재) |
| IP 변경 여부 | Y / N |
| IP 변경 후 서비스 이름으로 통신 성공 여부 | Y / N |
| Main Server 코드 수정 필요 여부 | Y / N |

### 6.4 체크포인트

## 7. 결과 종합

### 7.1 실험별 결과 요약

| 실험 | 기대 결과 | 실제 결과 | 성공 여부 |
|---|---|---|---|
| 서버 1대 장애 시 자동 폴백 | Fallback Pod로 자동 전환, 무중단 유지 | (기재) | Y / N |
| 롤링 배포 | 서비스 중단 없이 모델 교체 | (기재) | Y / N |
| 자동 복구 | Pod 크래시 시 자동 재시작 + 폴백 | (기재) | Y / N |
| 서비스 디스커버리 | IP 변경 시에도 통신 유지 | (기재) | Y / N |

### 7.2 결론
(테스트 완료 후 작성)

### 7.3 K8s 도입 권고
(테스트 완료 후 작성)

#### Tools Installation (15007823)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15007823
**최종 수정**: v1 (2026-04-19 sync)

# PostgreSQL 
다운을 하면, 

- 
PostgreSQL Server (눈에 안 보임 (백그라운드에서 실행됨))

- 
pgAdmin (우리가 사용하는 “앱” (GUI))

- 
psql (터미널, CLI 도구)

## pgAdmin 세팅 

# + pgvector +

#### Table 종류 (38666277)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/38666277
**최종 수정**: v3 (2026-04-19 sync)

# Table Types 
DB system에서 운영을 할 때, 마스터 테이블을 기반으로 트랜잭션 테이블에서 데이터가 발생하며, 이 과정에서 락이 발생하여 데이터 무결성을 보장하고, 상태 테이블을 통해 업무 진행 과정이 관리된다. 

****
****
****
****
| 종류 | 정의 | 특징 | 예시 |
|---|---|---|---|
| Master | 업무의 중심이 되는 주체에 대한 정보를 담고 있는 테이블 (원장성 데이터) | 데이터가 자주 바뀌지 않으며, transaction table 에서 참조 (reference)하는 기준 정보 | 고객 테이블, 상품 테이블, 부서 테이블 |

- 
| Transaction | 업무 수행 과정에서 발생한 데이터 (상태 변화)를 기록하는 테이블 commit 하는 단위. 예를 들어, 은행 거래 (deduct from account A, add to account B ) 는 하나의 transaction이다. | 데이터가 지속적으로 생성 및 변경되며, 마스터 테이블의 정보를 참조하여 거래 내용을 저장한다. | 주문 테이블, 입출금 테이블, 매출 테이블 등 |

- 

- 
| Lock | 동시성 제어를 위해 한 트랜잭션이 사용하는 데이터베이스 객체(테이블 또는 행)에 다른 트랜잭션이 접근하지 못하게 잠그는 메커니즘입니다. 목적: 데이터 일관성(Consistency) 유지 및 부정합 방지.문제점: 두 개 이상의 트랜잭션이 서로의 락을 요구하며 기대하는 교착상태 (Deadlcok) 이 발생할 수 있음. | S (Shared Lock): 읽기 락, 여러 트랜잭션이 동시에 데이터에 접근 가능 |   |
| X (Exclusive Lock): 쓰기 락, 한 트랜잭션이 배타적으로 사용, 데이터 수정 시 사용 |   |
| I (Intent Lock): 상위 계층의 잠금 의향을 표시하여 데이터 계층 구조 (부모 -자식)의 올바른 잠금을 수행 |   |
| State | 특정 엔티티나 트랜잭션의 현재 상태 (예: 주문 접수 → 배송중 → 배송 완료)를 관리하는 테이블 | 업무 프로세스 (workflow)의 흐름을 제어하기 위해 현재 상태값을 실시간으로 업데이트한다. | 프로세스 흐름 제어, 상태별 데이터 조회, 프로세스 병목 구간 파악 |

- 

- 
****

- 
****

- 
****

- 
****

- 
****````

- 
****

- 
****

- 

- 

- 
| Log | 시스템이나 사용자 행동의 변경 이력을 시간 순서대로 기록하는 테이블 개발자가 LogDB를 SELECT 하는 것 만으로도 해당 로그가 어떠한 이유에서 발생한 것인지를 명확하게 알 수 있어야 한다. | Append-only: 데이터의 추가만 이루어지며, 업데이트나 삭제는 거의 일어나지 않습니다.시간 기록: 이벤트 발생 시간(timestamp)이 핵심 필드로 포함됩니다.Raw Data: 2차 가공되지 않은 원천 데이터를 저장하여 데이터 정확성을 보장합니다.파티셔닝: 대용량 데이터 관리를 위해 일별/월별 파티셔닝(Partitioning) 처리가 필수적입니다.명명 규칙: 주로 _log, _history 등의 접미사를 사용하여 일반적인 마스터 테이블과 구분합니다.로그성(Log): "누가, 언제, 무엇을, 어떻게 했는가"에 대한 전체 기록 (예: 로그인 이력).상태성(State): "지금 상태가 무엇인가"에 대한 현재 값만 중요 (예: 현재 로그인 여부). | 사용자 행동 로그 (클릭, 페이지 이동, 구매 등).시스템 오류 및 디버깅 로그.데이터 변경 이력 (누가, 언제 회원 정보를 수정했는지). |

- 
Transaction: “업무 단위” 기록, 업무 처리 이력용 

  - 
보통 insert-only

  - 
commit 의 단위!! 

- 
State: 설비의 현재 상태 (과거 기록 x), 현재 상태 조회용

  - 
보통 update (덮어씀) 

  - 
transaction 과 state table 을 구성할때, transaction은 

- 
Log: 이미 일어난 일을 남긴다, 절대 안 바꾼다   → table 을 필수로 만들 필요는 없으며, 정말 필요한 경우에만 DB에 작성시켜서 추적한다. ‘.txt’로 저장하고 일정 시간 지나면 폐기 가능. 

  - 
state 와 log 컬럼을 구성할때, state 는 지금 이 주문이 어떤 상태이냐에 초점, log는 언제 이렇게 바뀌었나에 초점을 두고 컬럼을 구성한다. 

  - 
transaction table 과 비교를 위해 _log, 라는 이름을 붙힌다. 

# 코드로 보는 각 테이블 예시 
우리 팀 주제에서 고객이 발주를 넣었을 때, 각 테이블들이 어떻게 만들어지고, 업데이트되고 사용되는지 SQL code 로 그 용도를 알아보자. 
 핵심 포인트:                                                                                  

- 
order — 발주 내내 변하지 않음. 닻(anchor) 역할 (Master table)

- 
order_txn — admin 의사결정(RCVD/APPR/CNCL)만. FMS 공정 전환은 안 들어감 (Transaction)                    

- 
order_state — 항상 row 1개. 덮어씌워짐  (State table)                                                    

- 
order_log — 상태 바뀔 때마다 쌓임. 유일하게 이력 추적 가능 (Log table)

## DB setting 
 Step 3 — DBeaver에서 Connection 추가    

1. 
상단 메뉴 Database → New Database Connection                                               

1. 
PostgreSQL 선택 → Next                   

1. 
입력:                                                                                      

  - 
Host     : localhost               

  - 
Port     : 5432                                                                          

  - 
Database : smartcast                                                                

  - 
Username : (터미널 whoami 결과값)                                                        

  - 
Password : (없으면 비워도 됨)                                                            

1. 
Test Connection 클릭 → Connected 확인    

1. 
Finish                               
  Step 4 — SQL 파일 실행                                                                        

1. 
왼쪽 Database Navigator에서 smartcast_test 선택

1. 
File → Open File → order_table_examples.sql                                                

## SQL Code

#### Task Manager (20742182)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20742182
**최종 수정**: v2 (2026-04-19 sync)

## ① 주문 계층 구조
주문이 실제 로봇 명령이 되기까지 4단계를 거칩니다:

## ② 핵심 개념 3가지

| ✂️ 작업 분해 (Decomposition) | 📋 순서 보장 (Sequencing) | 📤 할당 요청 전달 |
|---|---|---|
| 큰 work_order를 item_id 단위로 나누고, 각 item_id마다 실행 순서가 있는 Task 목록을 생성합니다. | 같은 item_id의 Task는 앞 Task가 완료된 후에만 다음 Task가 Ready 상태가 됩니다. 선행 조건 없으면 즉시 실행 가능. | Ready 상태가 된 Task를 Task Allocator의 Ready Task Pool에 넣어줍니다. 누가 실행할지는 Allocator가 결정합니다. |

## ③ Task 실행 순서 (Confluence 정의 기준)
item_id 하나를 처리하기 위해 아래 순서를 반드시 지켜야 합니다:

### 🔥 생산 Task (A제품 1개 만들기)

1. 
**주형 제작 **(로봇팔) + 주조 구역 이동 (AMR, 병렬 가능)

1. 
**탈형 & 상차 **(로봇팔)

1. 
**후처리 구역 이동 **(AMR)

1. 
**자동 수거 위치 이동 **(AMR)

1. 
**적재 구역 이동 **(AMR)

### 📦 적재 Task (AMR이 적재구역 도착 상태에서 시작)

1. 
**하차 **(로봇팔)

1. 
**적재 **(로봇팔) + 대기구역으로 이동 (AMR, 병렬 가능)

### 🚛 출고 Task

1. 
**적재 구역 이동 **(AMR)

1. 
**출고 & 상차 **(로봇팔)

1. 
**출고 구역으로 이동 **(AMR)

## ④ 입력과 출력

| 📥 입력 (받는 것) | 설명 |
|---|---|
****
| work_order | 공장 관리자가 승인한 생산 지시 |
****
| task 완료 신호 | Execution Monitor로부터 'Task A 완료' 이벤트 |
****
| task 실패 신호 | 재시도 또는 오류 처리 필요 알림 |

| 📤 출력 (내보내는 것) | 설명 |
|---|---|
****
| Ready Task | 지금 당장 실행 가능한 Task → Task Allocator에 전달 |
****
| 상태 업데이트 | Task·work_order 진행 상황 → DB 반영, UI 갱신 |
****
| 완료 신호 | 모든 Task 완료 시 work_order를 '완료'로 전환 |

## ⑤ 3가지 관제 컴포넌트 비교

| 항목 | Task Manager (이 문서) | Task Allocator | Traffic Manager |
|---|---|---|---|
****
| 역할 | 작업 생성·분해·순서 관리 | 어떤 로봇에 배정할지 결정 | 로봇 간 경로 충돌 방지 |
****
| 입력 | work_order (생산 지시) | Ready Task (실행 가능 작업) | 로봇들의 위치·경로 정보 |
****
| 출력 | Ready Task → Allocator | 특정 로봇에 명령 전달 | 이동 허가 / 대기 신호 |
****
| 핵심 결정 | Task 순서·우선순위 결정 | 최적 로봇 배정 알고리즘 | Deadlock 방지 알고리즘 |
****
| 주요 리스크 | Task 실패 시 재시도 정책 | 로봇 가용성 판단 기준 | 교착 상태(Deadlock) 처리 |

## ⑥ 구현 순서

1. 
**work_order 감시**: 공장 관리자가 '생산 시작' 누르면 작업 대기열에 등록

1. 
**item_id 생성**: work_order의 수량(10개)만큼 item_id 분할 (item_001~010)

1. 
**Task DAG 생성**: 각 item_id에 대해 실행 순서가 있는 Task 목록 생성

1. 
**Ready Task 발행**: 선행 조건 없는 Task를 즉시 Ready Task Pool에 삽입

1. 
**완료 이벤트 수신**: Task 완료 시 다음 Task를 Ready Pool에 추가

1. 
**work_order 완료 판정**: 모든 item의 모든 Task 완료 시 work_order 종료

## ⑦ 쉬운 용어 사전

| 용어 | 설명 |
|---|---|
****
| customer_order | 고객이 사무실에 넣은 주문. 사무실 직원이 검토·승인 |
****
| work_order | 공장 관리자가 '생산 시작'을 누른 승인된 주문 (예: A제품 10개) |
****
| item_id | work_order를 개별 단위로 쪼갠 것 (A제품 1개 = 1개 item_id) |
****
| Task | 로봇이 바로 실행할 수 있는 최소 명령 단위 (주형 제작, 이송, 탈형 등) |
****
| Ready Task | 선행 Task가 완료되어 지금 당장 실행 가능한 Task |
****
| 선행 조건 | 이 Task 시작 전에 반드시 완료되어야 하는 Task (예: 탈형은 주조 후에만 가능) |
****
| DAG | 방향성 비순환 그래프 — Task들의 순서 관계를 나타내는 구조 |
****
| Task Allocator | Task를 받아서 어떤 로봇이 실행할지 결정하는 배정 엔진 |

#### Traffic Manager (21037116)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21037116
**최종 수정**: v2 (2026-04-19 sync)

# AMR 운행 관리(Fleet Traffic Management)
*우리 공장 AMR 3대가 서로 부딪히지 않고 움직이는 방법 · 2026-04-08*

### 하드웨어 스펙

| 맵 크기 | 로봇 크기 | 로봇 대수 | 구동 방식 |
|---|---|---|---|
****
****
****
****
| 1m × 2m | 0.12 × 0.12m | AMR 3대 | 차동 구동 |

## 1. 해결하려는 문제
공장에 로봇이 여러 대 있으면 자연스럽게 이런 상황이 생깁니다:

- 
**경로 충돌** — 두 로봇이 같은 복도를 쓰려고 함

- 
**교착(Deadlock)** — 두 로봇이 좁은 복도에서 정면으로 마주쳐 둘 다 멈춤

- 
**비효율** — 한 로봇이 작업 중인데 다른 로봇이 끝없이 기다림
Nav2(로봇 내비게이션 라이브러리)만으로는 로봇 *한 대의 이동*은 잘 하지만, **여러 로봇이 서로를 알고 조율하는 일**은 못 합니다. 그걸 우리가 추가로 만들어야 합니다.

## 2. 핵심 개념 3가지

| 🗺️ Waypoint + Edge 지도 | 🔒 Edge 예약 | 🤝 우선순위 양보 |
|---|---|---|
********
********
****
| 공장을 주요 지점(waypoint)과 그 사이를 잇는 길(edge)로 간단한 그래프로 표현. 예: 용해로 — 교차점 — 검사대 | 로봇이 길을 지나가려면 그 edge를 먼저 내 것이라고 예약합니다. 다른 로봇이 이미 예약했으면 다른 길로 돌아갑니다. | 정말 다른 길이 없어서 두 로봇이 막혔을 때, 우선순위가 낮은 로봇이 뒤로 한 칸 비켜줍니다. 점수가 같으면 나중에 온 쪽이 양보. |

## 3. 우리 공장 지도 예시

## 4. 실제 동작 시나리오 — AMR-A와 AMR-B
**상황**: AMR-A가 용해로 → 검사대로 이동 중. 반대편에서 AMR-B도 검사대 → 용해로로 이동해야 함.

1. 
**AMR-A 출발**: 용해로 → 좌측교차점 → 긴 복도 → 우측교차점 → 검사대. 지나갈 edge들을 하나씩 예약하며 진행.

1. 
**AMR-B가 출발하려 함**: 최단 경로는 AMR-A와 정반대 방향. 긴 복도에서 마주칠 예정.

1. 
**자동 우회**: 시스템이 AMR-A의 예약을 보고, AMR-B에게는 **충전소를 거쳐 가는 우회 경로**를 자동으로 배정. 마주칠 일이 없음.

1. 
**만약 우회로도 없다면**: 둘이 복도에서 만나고 3초 기다려도 못 지나가면 교착으로 판정.

1. 
**우선순위 비교**: AMR-A가 긴급 작업이라 점수가 높음 → AMR-A가 winner, AMR-B가 loser.

1. 
**AMR-B 양보**: 지나온 마지막 waypoint(한 칸 뒤)로 후진하여 비켜줌.

1. 
**AMR-A 통과 후**: AMR-B가 다시 원래 목적지로 출발.

## 5. 누가 무엇을 담당하나

### 우리가 직접 만드는 것

| 컴포넌트 | 역할 |
|---|---|
****
| 지도 파일 | 공장의 waypoint·edge를 GeoJSON으로 작성 |
****
| TrafficManager | 어느 edge를 어느 로봇이 쓰고 있는지 기록 |
****
| 교착 감지기 | 두 로봇이 서로 막혔는지 확인 |
****
| 양보 결정 | 누가 물러날지 우선순위로 판정 |
****
| 우선순위 점수 | 납기·긴급도 등 7요소 가중 계산 (기존 schedule.py) |

### Nav2가 자동으로 해주는 것

| 기능 | 담당 Nav2 구성 요소 |
|---|---|
****
| 경로 탐색 | 우리 그래프에서 최단 경로 계산 (nav2_route) |
****
| 예약 반영 | 차단된 edge를 피해 자동 재계산 (ReroutingService) |
****
| 실제 주행 | 제자리 회전 + 전진으로 waypoint까지 이동 (navigate_to_pose) |
****
| 장애물 회피 | LiDAR로 예상치 못한 물체 감지 및 정지 (costmap) |
****
| 속도 제한 | edge별 최대 속도 적용 (AdjustSpeedLimit) |

## 6. 우리 맵에 맞춘 주요 설정값

| 파라미터 | 값 | 의미 |
|---|---|---|
****
| 교착 감지 대기 시간 | 3초 | 이 시간 이상 못 움직이면 deadlock으로 판정 |
****
| 최대 후진 waypoint 수 | 3개 | 양보 시 최대 3칸까지만 되돌아감 |
****
| 이동 속도 | 0.1~0.15 m/s | 작은 로봇의 안전 속도 |
****
| 도착 반경 | 5cm | waypoint에 이만큼 가까우면 도착으로 판정 |
****
| Tick 주파수 | 20 Hz | 상태 갱신 빈도 (초당 20회) |

## 7. 앞으로의 진행 순서

1. 
**설치 확인**: ROS 2 Jazzy에 nav2_route 패키지가 설치 가능한지 확인

1. 
**지도 작성**: factory_graph.geojson 파일에 우리 공장 waypoint와 edge 정의

1. 
**TrafficManager 구현**: edge 예약·해제 로직 (약 150줄)

1. 
**Bridge 노드**: 예약 상태를 Nav2에 전달하는 ROS2 노드 (약 50줄)

1. 
**Priority Yield 구현**: 교착 감지와 양보 로직 (약 200줄)

1. 
**통합 테스트**: Gazebo 시뮬레이션 → 실제 AMR 3대 테스트

## 8. 쉬운 용어 사전

| 용어 | 쉬운 설명 |
|---|---|
****
| AMR | Autonomous Mobile Robot — 자율주행 이동 로봇 (Pinkypro 같은) |
****
| Nav2 | ROS 2의 로봇 내비게이션 라이브러리. 한 대 이동을 담당 |
****
| Waypoint | 공장에서 의미 있는 위치 (용해로, 검사대, 충전소 등) |
****
| Edge | 두 waypoint 사이를 잇는 길 = 로봇의 이동 구간 |
****
| 예약(Reservation) | 이 edge는 지금 내가 쓸 거야 라고 기록하는 것 |
****
| Deadlock | 두 로봇이 서로의 길을 막아서 둘 다 못 움직이는 상황 |
****
| Yield(양보) | 우선순위 낮은 로봇이 뒤로 물러나 길을 비켜주는 행동 |
****
| FIFO | First In First Out — 먼저 온 사람이 먼저 처리되는 공정한 규칙 |
****
| GeoJSON | 지도 데이터를 저장하는 표준 텍스트 포맷 (JSON 기반) |
****
| Dijkstra | 최단 경로를 찾는 유명한 알고리즘. 지하철 앱이 쓰는 것과 같은 원리 |
상세 설계 문서: `docs/fleet_traffic_management.html` (로컬 저장소 참조)

#### Task Allocator (21332000)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21332000
**최종 수정**: v2 (2026-04-19 sync)

## ① 관제 시스템 내 위치

## ② 핵심 개념 3가지

| 🎯 Capability 매칭 | ⚡ 최적 로봇 선택 | 🚦 Traffic Manager 협력 |
|---|---|---|
| '주형 제작 Task'는 로봇팔만, '이송 Task'는 AMR만 수행 가능합니다. 먼저 할 수 있는 로봇을 걸러냅니다. | 후보 로봇들 중에서 가장 가까운 + 배터리 여유 있는 + 우선순위 높은 Task에 맞는 로봇을 점수로 비교합니다. | AMR을 배정할 때는 Traffic Manager에게 경로를 확보 요청합니다. 경로가 막히면 배정을 잠시 보류합니다. |

## ③ 로봇 타입별 수행 가능 Task

| 🤖 AMR (Pinkypro × 3대) | 🦾 로봇팔 (MyCobot280 × 2대) |
|---|---|

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
| 주조 구역 이동후처리 구역 이동자동 수거 위치 이동적재 구역 이동출고 구역으로 이동충전소 복귀 | 주형 제작탈형 & 상차출고 & 상차하차적재 |

## ④ 로봇 배정 점수 (100점 만점)
Capability가 맞는 로봇들 중에서 점수가 가장 높은 로봇에 Task를 배정합니다:

| 평가 항목 | 점수 | 설명 |
|---|---|---|
****
| 🗺 거리 (가까울수록) | 40점 | 현재 위치에서 Task 시작 지점까지 유클리드 거리 (4m 이내 = 만점) |
****
| 📌 Task 우선순위 | 30점 | work_order의 7요소 가중 점수 (납기·긴급도 등)를 반영 |
****
| 🔋 배터리 여유 | 20점 | Task 완료 후 배터리 20% 이상 남으면 만점, 10% 이상이면 절반, 미달이면 0점 |
****
| 🎓 Capability 특화 | 10점 | Task 요구 capability와 정확히 일치하면 10점, 초과 포함 일치이면 5점 |

## ⑤ 배정 동작 순서

1. 
**Ready Task Pool 확인**: 대기 중인 Task가 있는지 0.5초마다 확인 (20Hz 미만)

1. 
**Capability 필터링**: 이 Task를 실행할 수 있는 로봇(AMR/로봇팔) 목록 추출

1. 
**유휴 로봇 필터링**: 현재 다른 Task 수행 중이 아닌 로봇만 남김

1. 
**점수 계산**: 각 후보 로봇에 대해 거리·우선순위·배터리·특화도 점수 합산

1. 
**Resource 예약**: 선택한 로봇의 경유 Station/Buffer 사전 예약 확인

1. 
**경로 확보 요청**: AMR인 경우 Traffic Manager에 경로 허가 요청

1. 
**명령 전달**: 모든 조건 충족 시 선택한 로봇에 Task 명령 전송

## ⑥ 배정 실패 처리

| 상황 | 원인 | 처리 방법 |
|---|---|---|
| Capability 일치 로봇 없음 | 전체 로봇팔이 사용 중 | Ready Pool에서 대기 → 다음 tick에서 재시도 |
| Resource 예약 실패 | Station/Dock 이미 점유 | Task를 Pool에 반환 → 나중에 재시도 |
| 경로 없음 (Traffic Manager 거절) | 모든 경로 막힘 | 10초 후 재시도, 반복 실패 시 관리자 경보 |
| 로봇 통신 두절 | 네트워크 장애 / 로봇 고장 | 해당 로봇 unavailable 처리 → Task 재배정 |
| 배터리 부족 | 작업 중 배터리 30% 이하 | 현재 Task 완료 후 충전 복귀 Task 긴급 삽입 |

## ⑦ 연결 관계

| 📥 입력 (연결되는 컴포넌트) | 전달받는 내용 |
|---|---|
****
| Task Manager | Ready Task 목록 (실행 가능 작업) |
****
| Robot 상태 DB | 각 로봇의 위치·배터리·현재 작업 여부 |
****
| Resource Manager | Station·Buffer·Dock 사용 가능 여부 |

| 📤 출력 (연결되는 컴포넌트) | 전달하는 내용 |
|---|---|
****
| AMR Executor | 이동·이송 명령 (ROS2 Action) |
****
| Arm Executor | 픽&플레이스 명령 (MyCobot280 SDK) |
****
| Traffic Manager | 경로 허가 요청·해제 |

## ⑧ 3가지 관제 컴포넌트 비교

| 항목 | Task Manager | Task Allocator (이 문서) | Traffic Manager |
|---|---|---|---|
****
| 역할 | 작업 생성·분해·순서 관리 | 어떤 로봇에 배정할지 결정 | 로봇 간 경로 충돌 방지 |
****
| 입력 | work_order (생산 지시) | Ready Task, 로봇 상태 | 로봇들의 위치·경로 정보 |
****
| 출력 | Ready Task → Allocator | 특정 로봇에 명령 전달 | 이동 허가 / 대기 신호 |
****
| 핵심 결정 | Task 순서·우선순위 결정 | 최적 로봇 배정 알고리즘 | Deadlock 방지 알고리즘 |
****
| 주요 리스크 | Task 실패 시 재시도 정책 | 로봇 가용성 판단 기준 | 교착 상태(Deadlock) 처리 |

## ⑨ 쉬운 용어 사전

| 용어 | 설명 |
|---|---|
****
| Ready Task | 선행 Task 완료 → 지금 당장 실행 가능한 Task |
****
| Capability | 로봇이 수행할 수 있는 작업 유형 (AMR: 이동, 로봇팔: 집고 놓기) |
****
| Idle 로봇 | 현재 아무 Task도 수행하지 않는 대기 중 로봇 |
****
| Resource 예약 | Station/Dock을 내가 쓰겠다고 미리 등록하는 것 (충돌 방지) |
****
| Traffic Manager | AMR 이동 경로의 교통 정리 담당. 충돌·교착 방지 |
****
| Executor | 실제 로봇에 명령을 전달하는 하위 모듈 (AMR용, 로봇팔용 별도) |
****
| Deadlock | 두 로봇이 서로의 경로를 막아 둘 다 못 움직이는 상황 |
****
| Greedy 알고리즘 | 매 배정마다 '지금 당장 가장 좋은' 로봇을 선택하는 단순 전략 |

#### Standup_20260000 (459018)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/459018
**최종 수정**: v14 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics - 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 9:40 - 9:50 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |   |
| To Do |   |

#### Standup_ (3342390)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3342390
**최종 수정**: v4 (2026-04-19 sync)

###  

###

#### Standup_20260331 (7275232)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/7275232
**최종 수정**: v12 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 스마트 팩토리 | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러맛집 | 참석자 |   |

- 

- 
| 팀이슈 | Technical Research - priority 기반 작업 재할당 필요 GUI 검토 담당자 필요 |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/pages/resumedraft.action?draftId=7373302&draftShareId=0b9403fa-f511-43f6-b9c0-18beac8d06e7)

- 

- 

- 

- 

- 
|   | SR v3 sprint 1 발표map 효율화 구상 RDBS 기본 DOCS (공유용) 작성 | GUI 검토 → SA (System Architecture PPT 구상) DB 구축 [Technical Research] Vision SR + MAP: classroom submit | 외출 12:20 ~ 16:20 |

- 

- 

- 
|   | SR 정리 피드백 정리 | SR 보충 마무리 |   |

- 

- 

- 

- 

- 

- 

- 
|   | GUI 구성서버 구축 완료SR 수정 | GUI에 경기장 MAP 반영센서 검증컨베이어 벨트 검증 | 오늘 오후 2:00 ~ 4:00 외출 1~2 시간 정도 |

- 

- 

- 

- 
|   | ​SR 정리DB 스키마 작성 | DB 스키마 작성 마무리ERD 작성 |   |

- 

- 

- 
|   | SR 마무리 및 정교화YOLO 조사 및 실증 검토 | AMR 기술 조사 |   |

- 

- 

- 
|   | 개인 로봇팔 기존 무제 수리 완료(이번엔 갑자기 그리퍼 문제) | 로봇팔, 그리퍼 기술 조사 | 오전에 상담 갔다가 11시 반 쯤 복귀 |

- 

- 

- 
|   | SR 정리 | AMR 기술 조사 SR 마무리 |   |

- 

- 
|   | SR 정리 | SR 보충 마무리 |   |

- 

- 

- 

- 
|   | 로봇팔 수리SR 내용수정 | 센서, 로봇팔, 그리퍼 기술조사초음파센서 양초 냉각상태 모니터링 가능여부 실증 테스트 |   |

- 

- 

- 

- 
|   | SR 마무리 및 정교화(주물 생산 자동화 공정 기능) + 주제 세분화(기능 분할)​추가 논의사항 확정(의제: Adapter, 용융 전후 무게까지 고려 여부, 중탕기와 용융 상태 조건 호환여부) | Vision(Dataset, Detection_test, Limitations) 기술조사(YOLO 기반)System Architecture 초안 참여(How?) |   |
|   | SR 마무리 및 정교화(주물 생산 자동화 공정 기능) + 주제 세분화(기능 분할)​추가 논의사항 확정(의제: Adapter, 용융 전후 무게까지 고려 여부, 중탕기와 용융 상태 조건 호환여부) | Vision(Dataset, Detection_test, Limitations) 기술조사(YOLO 기반)System Architecture 초안 참여(How?) |   |   |

- 

- 

- 

- 
| To Do | [Team leader] Sprint1 자료: SR 최종 버전 + MAP 제출 SR final version (용석, 예진, 정연) → GUI 검토(?)  → DB 구축  (다예, 진성)[Team leader] SA slides 구상 → 이거는 강의 없나?[Everyone] Technical Research (priority check) |

#### Standup_20260326 (3539008)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3539008
**최종 수정**: v10 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 |   | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러 맛집 | 참석자 |   |
| 팀이슈 | 주제 확정 필요 및 User requirements 작성 필요 |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 

- 
|   | 회의록 작성 주조 과정에 대한 기술 조사, user requirements, 기술 조사 보고서 작성 confluence directory 구성 | UR & SR 작성 회사에 물어볼 질문 작성 | 어제 늦게 자고 오늘 일찍 일어남 |

- 

- 

- 
|   | 실제 공장 사례 조사Confluence folder structure 제작 | Confluence folder structure 수정 |   |

- 

- 

- 

- 
|   | 컨베이어벨트 구매금액 11만원주조 공정 데모 시뮬레이션 연구 | 주조 공정 데모 시뮬레이션 | 고용 센터 집합교육 14~16시 |

- 

- 

- 
|   | SmolVLA 테스트 | SmolVLA 문서 작성Jetcobot에 적용하기 |   |
|   | ​프로젝트 아이디어 검증 PPT 제작주조공정 조사 |   | ​취침시간 불량 |
|   | 개인 로봇팔 수리 시도(파워선 안가져옴)PPT 제작 | 개인 로봇팔 수리 시도주조 공정 지인한테 질문 전달(자동화, 위험성 관련 질문만 추려서) |   |

- 

- 

- 

- 
|   | VLA 조사usecase 구체화, 시스템 아키텍쳐PPT 제작 |   | 어제 늦게잠 ㅠㅠ |

- 

- 
|   | 발표자료 준비 주조 공정 조사V model 숙지 | 주조 시연 재료 장보기 시연 준비 |   |
|   | ​우분투 환경에서 카메라 실행​컨베이어에 적용할 거리센서 조사주물에 사용할 대체품 조사PPT | ​사용될 소형컴퓨터에서 카메라 실행(필요에따라 SDK 설치)​주물, 컨베이어 센서 팀원들과 논의 |   |

- 

- 

- 
|   | ​Jetcobot280 작업공간 분석스마트 공장 제조라인 수정(주물공장 시나리오 반영)​Conveyor belt 시스템 조사(Distribution, 광센서) | 컨베이어 벨트 세부사항 조사(모터 유무, 타당성)주물공장 시나리오 실제 사례 조사(+alpha) VLA (SmolVLA 조사 및 적용방법) 학습 | ​ |
|   | ​Jetcobot280 작업공간 분석스마트 공장 제조라인 수정(주물공장 시나리오 반영)​Conveyor belt 시스템 조사(Distribution, 광센서) | 컨베이어 벨트 세부사항 조사(모터 유무, 타당성)주물공장 시나리오 실제 사례 조사(+alpha) VLA (SmolVLA 조사 및 적용방법) 학습 | ​ | ​ |
| To Do |   |

#### Standup_20260327 (3571922)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3571922
**최종 수정**: v16 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 |   | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러 맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 
|   | UR & SR 작성 회사에 물어볼 질문 작성 UR 업데이트 | SR 작성 발표 (있으면) |   |

- 

- 

- 

- 

- 

- 

- 
|   | 주조 시연 준비주물 제작 테스트컨플 폼 제작모래 구해옴 | 주물 제작 테스트컨플 자료 옮기기SR 작성 |   |

- 

- 

- 

- 

- 

- 
|   | 주조 시연 재료 구매패턴 형성 테스트주물 형상 테스트 (양호) | 패턴 형성 추가 테스트주물 형상 테스트SR 작성 |   |

- 

- 

- 

- 

- 
|   | 로봇팔 시연주조 회사 질문 작성UR 작성 | SR 작성주물 형상 테스트 |   |

- 

- 

- 

- 
|   | 주조공정 자료 조사 및 정리물류 용어 정리 UR 작성 | SR 작성 |   |

- 

- 

- 

- 

- 
|   | 개인 로봇팔 수리 시도 (모터 개별 테스트를 진행해야 하는데 한 명만 보조 필요)주조 공정 지인한테 질문 전달(자동화, 위험성 관련 질문만 추려서) (정리해서 업로드 완료) | 모터 개별 테스트(정상 작동 확인)3/30 대현님이 추가 점퍼선 가져오시면 바로 수리 예정SR 작성 |   |

- 

- 

- 

- 
|   | 로봇팔 시연맵 레이아웃 작성주조 회사 질문 작성 | SR 작성 |   |

- 

- 

- 

- 

- 

- 
|   | 주조 시연 재료 구매 주조 시연 준비주조 형성 테스트 | 패턴 형성 추가 테스트 주물 형상 테스트  SR 작성 | ​ |

- 

- 

- 
|   | 주조공정 자료 조사 및 정리 | SR 작성개인 로봇팔 (규정) 보조 업무 | 금일 14:30 조퇴 |

- 

- 

- 
|   | 주조공정 자료 조사()UR 작성 | SR 작성 | ​ |
|   | 주조공정 자료 조사()UR 작성 | SR 작성 | ​ | ​ |

- 

- 

- 

- 
| To Do | SR 작성 모의 사형 재료로 실험 molding making & pouring 자동화 시나리오 실험 (가능성 확인)(가능하면) logistics 부분까지 생각해서 관제 생각하기 |

#### Standup_20260330 (5310965)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5310965
**최종 수정**: v16 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 |   | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러 맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 
|   | SR 작성 - 원격 발주 부분 | DB, UI 작업회의록 작성 4주차 sprint 계획 VLA, LLM prototypes experiments |   |

- 

- 
|   | SR 작성-적재 | 컨플 자료 이동 |   |

- 

- 

- 

- 

- 

- 
|   | SR 작성주물 테스트 | 컨베이어벨트 제어 시스템 구상SR 보충중탕기 및  센서 수급 체크 | 3월 31일 고용센터 상담 및 교육 15:00~16:00 |

- 

- 

- 
|   | SR 작성(관제 기능)주조 공정 자료조사 | SR 초안 마무리 |   |

- 

- 
|   | SR 작성: 출고 관리 | SR 마무리 및 정교화 |   |

- 

- 

- 

- 

- 

- 

- 
|   | SR 작성맨홀 패턴 디자인 구상그 밖에 필요한 것들 구상 | SR 마무리로봇팔 대현님이랑 수리 마무리3D 프린터 필요한 거 계속 뽑기 | 3월 31일 오전 10시 고용센터 상담 교육(1시간 소용 예상) |

- 

- 

- 

- 
|   | SR 작성 | SR 마무리다양한 경로 반영하여 맵 작성이송 관련 리서치 |   |

- 
|   | ​SR 작성 - 후처리 | ​논의후 SR 보충 | ​11시 외출 ~ 3시 복귀 |
|   | SR 작성로봇팔 테스트 | ​로봇팔 수리 마무리SR 작성 |   |

- 

- 

- 
|   | SR 작성; “주물 생산 자동화 공정 기능” | ​SR 마무리 및 정교화​추가 논의사항 확정(Adapter, 용융 전후 무게까지 고려 여부, 중탕기와 용융 상태 조건 호환여부) | ​ |
|   | SR 작성; “주물 생산 자동화 공정 기능” | ​SR 마무리 및 정교화​추가 논의사항 확정(Adapter, 용융 전후 무게까지 고려 여부, 중탕기와 용융 상태 조건 호환여부) | ​ | ​ |

- 

- 

  - 

  - 

  - 

  - 

- 

  - 

  - 
| To Do | 3주차 sprint 계획 To be completed: SRGUI development DB setup (ERD)map layout design On-going:Deep learning model trainingComparative study |

#### Standup_20260401 (8389431)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/8389431
**최종 수정**: v2 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 시스템 구축 | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러 맛집 | 참석자 |   |

- 
| 팀이슈 | 기술 조사용 테스트 주물 필요 |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 
[](https://dayelee313.atlassian.net/wiki/x/H4Bo)

- 
[](https://dayelee313.atlassian.net/wiki/x/_QBy)

- 

- 

- 
****

- 

- 

- 
|   | Map 시나리오 완성 → 한정된 자원 안에서 시나리오 구축 필요ERD 관련 자료 마무리 | Map 시나리오 2 완성 필요 기술 조사 (Vision-PatchCore) → VLM 파트 초안 작성 (중요) SA 개요 만들기 (1) SR 및 UR 검토 필요binary classification via Transfer Learning | 12:20 ~ 16:20 외출 |

- 

- 

- 

- 

- 
|   | SR 작업 마무리SR기반 GUI 레이아웃 구성 | GUI 대시보드 프로토타입 수정프로토타입 데이터 추출(DB설계 참고용)적재 기술조사 개요 작성 |   |

- 

- 

- 

- 

- 

- 

- 

- 
|   | GUI 공장 레이아웃 데모 업데이트GUI 대시보드 업데이트(UR/SR)중탕기 테스트 (설정온도 80~90도)양초로 주물 테스트 | 컨베이어 벨트 기술 조사 진행센서 기술 조사 진행모래 구매 후 추가 테스트 진행GUI 대시보드 업데이트 |   |

- 

- 

- 

- 

- 
|   |   | SW기술 조사(Vision - PatchCore)?주물 제작 데이터 만드는 것 확인binary classification via Transfer Learning | 13:30~15:30 외출 |

- 

- 
|   | AMR 기술 조사 | AMR 기술 조사 |   |

- 

- 

- 

- 
|   | Robot Arm 기술 조사 계획서 작성원형 맨홀 디자인 3안 완성 | 맨홀 디자인 원형 & 네모 까지 최대한 제작Robot Arm 기술 조사 진행(실험) |   |

- 

- 

- 
|   | SR 마무리AMR 기술 조사 | ​AMR 기술 조사 |   |

- 

- 

- 

- 
|   | SR 마무리 | 주물 추가 테스트 다이소 물품 구매 적재 기술 조사 준비 |   |

- 

- 

- 

- 
|   | Robot arm 기술조사Sensor 기술조사 | Robot arm 기술조사Sensor 기술조사 |   |

- 

- 

- 

- 

- 
|   | YOLO 모델 평가 및 테스트(image, video) with webcamTechnical research(Vision) 항목 작성(YOLO) | YOLO training 추가 조사(전이학습, 사전학습 등)Roboflow(Manhole 샘플)추가 조사카메라 추가 테스트 |   |
|   | YOLO 모델 평가 및 테스트(image, video) with webcamTechnical research(Vision) 항목 작성(YOLO) | YOLO training 추가 조사(전이학습, 사전학습 등)Roboflow(Manhole 샘플)추가 조사카메라 추가 테스트 |   |   |

- 

- 
| To Do | 기술 조사 목요일까지 작성 하루에 틈틈이  에게 중간 점검 받기! |

#### Standup_20260402 (9634161)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/9634161
**최종 수정**: v5 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/LACS)

- 
[](https://dayelee313.atlassian.net/wiki/x/VoBf)

- 

- 
[](https://dayelee313.atlassian.net/wiki/pages/resumedraft.action?draftId=6848543)

- 
[](https://dayelee313.atlassian.net/wiki/x/D4Jx)

- 
|   | 및 제출 SA 발표 준비 [기술 조사] Binary classification via Transfer Learning | SR 및 UR 검토 확인 한정된 자원에서 → Map 시나리오 2 완성 필요 (한번에 두 개 찍고, 이게 빠를때 AMR이 효율적으로 움직이도록 하는 방향)SQL 기본 문법 설명 페이지 완성GUI 팀 완성되면 → Schema 완성 |   |

- 

- 

- 

- 

- 

- 
|   | SR 수정대시보드 프로토타입 수정 |   |   |

- 

- 

- 

- 

- 

- 
|   | 대시보드 공장 맵 업데이트대시보드 발주조회 기능 추가주조 테스트레이저 센서 기술 테스트(대현님 참조) | 대시보드 SR 수정본 반영 |   |

- 

- 

- 

- 
|   |   | PatchCore 기술조사 마무리주물 데이터셋 수집 및 테스트 |   |

- 

- 

- 

- 
|   | ​ | ​ |   |

- 

- 

- 

- 

- 

- 
|   | Robot arm 기술 조사(Payload, repeat)듀얼 패턴 스탬퍼 제작샘플 디자인 제작 및 3D 샘플 | Robot arm 기술 조사(Work-time) | 10:00~11:30 취업 지원 상담 |

- 

- 

- 

- 

- 
|   | nav2, slam toolbox parameter 분석넓은 맵에서 주행 테스트map의 1/2 구역에서 주행 테스트 | nav2 parameter 분석map에서 주행 테스트 |   |

- 

- 

- 
|   | 주물 추가 테스트 다이소 물품 구매 | 주물 추가 테스트 → (필) 실험 결과 작성 |   |

- 

- 

- 

- 

- 
|   | ) | Robot arm 기술조사서 작성 마무리Sensor 기술조사서 작성 마무리​추가실험(레이저 센서 활용) |   |

- 

- 

- 

- 
|   | 주형 샘플로 bounding box 탐지가능성 조사 | 주형 샘플로 bounding box 탐지가능성 추가조사(컨베이어 벨트에)bounding box의 픽셀 정보와 실제 환경에서의 수치를 매칭하는 방법 조사 |   |
|   | 주형 샘플로 bounding box 탐지가능성 조사 | 주형 샘플로 bounding box 탐지가능성 추가조사(컨베이어 벨트에)bounding box의 픽셀 정보와 실제 환경에서의 수치를 매칭하는 방법 조사 |   |   |

- 

  - 

  - 

  - 

- 

- 
| To Do | Pressing Issues [정연, 규정] SW AI 팀에서 사용할 양품/불량품 샘플 만들어주세요! [예진] GUI → Data list[다예] SR 검토 & 시나리오 작성 [Everyone] Technical Research 현재 하고 있는 작업 page에 inline comment |

#### Standup_20260403 (11535709)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11535709
**최종 수정**: v3 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 
[](https://dayelee313.atlassian.net/wiki/x/VoBf)

- 

- 
[](https://dayelee313.atlassian.net/wiki/pages/resumedraft.action?draftId=6848543)

- 
[](https://dayelee313.atlassian.net/wiki/x/D4Jx)

- 

- 

- 

- 

- 
|   | SR 및 UR 검토 확인 한정된 자원에서 → Map 시나리오 2 완성 필요 (한번에 두 개 찍고, 이게 빠를때 AMR이 효율적으로 움직이도록 하는 방향)SQL 기본 문법 설명 페이지 완성GUI 팀 완성되면 → Schema 완성 | (P1) 기술조사 다른 분들 inline comment SA 재작성 및 제출 기술 조사, binary classification 학습 다음주 월요일 sprint3 발표 준비 |   |

- 

- 

- 
|   |   | 시작  @정연 |   |

- 

- 

- 

- 
[](http://localhost:3000/)

- 
[](http://localhost:3000/customer)

- 
|   | 대시보드 SR 수정본 반영 | 대시보드 업데이트대시보드 링크고객 주문 페이지컨베이어 벨트 관제 시스템 통신 테스트 |   |

- 

- 

- 
|   |   | SA 수정(피드백 반영)맨홀 학습용 데이터 수집 |   |

- 

- 

  - 

- 

- 

- 

- 
|   |   | Map buildingNav2 파라미터 튜닝ArUco Marker 테스트 |   |

- 

- 

- 

- 

- 
|   |   | Pinky 적재 공간 파츠 제작양품, 불량품 계속 출력개인 로봇팔 고치기 |   |

- 

- 

  - 

- 

- 

- 

- 
|   |   | Map buildingNav2 파라미터 튜닝ArUco marker 테스트 |   |

- 

- 
|   | 주물 추가 테스트 → (필) 실험 결과 작성 | 시작  @예진 |   |

- 

- 

- 

- 

- 

- 

- 
|   | ​추가실험(레이저 센서 활용)ㅌ | 컨베이어 관제 시스템 통신 연결 및 테스트뎁스카메라 기술조사 및 실험 | 금일 14:30 조퇴4/6(월) 결석 예정 |

- 

- 

- 

- 
|   | (추가 작업 필요) | 주형 샘플 bounding box 촬영작업 마무리(사진, 영상 작업)->에 추가하기bounding box 탐지 후 추출한 실제 데이터 예시를 매칭 방법에 적용하기 |   |
|   | (추가 작업 필요) | 주형 샘플 bounding box 촬영작업 마무리(사진, 영상 작업)->에 추가하기bounding box 탐지 후 추출한 실제 데이터 예시를 매칭 방법에 적용하기 |   |   |

- 

  - 

  - 

  - 

- 

- 
| To Do | Pressing Issues [규정] SW AI 팀에서 사용할 양품/불량품 샘플 만들어주세요! → DATASET [예진] GUI → Data list[다예] SR 검토 & 시나리오 작성 [Everyone] Technical Research 현재 하고 있는 작업 page에 inline comment |

#### Standup_20260406 (13337419)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13337419
**최종 수정**: v7 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 09:45 - 10:10 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 | 시연 시나리오 1시간 정도 다같이 논의 필요 (주말에 각자 생각 어느정도) & sprint3 관련 계획 세우기 & 지라 사용법 숙지 (링크 공유) |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 

- 

- 
|   | 전체 기술 조사 커멘트 완료!SA 자료 클래스룸 재업로드Sprint3 계획 | Sprint2 발표  지라 세팅 GUI & DB list 확인 → Schema 작성 준비 Technical Research (관제 + 모델) |   |

- 

- 
|   | 적재 기술 조사 |   |   |

- 

- 

- 

- 

- 
|   | ESP32 보드 준비레이저 센서 브라켓 도면 작업 | ESP32 센서+모터 연동 |   |

- 

- 
|   |   | 기술조사(맨홀 데이터) | 아파서 결근 |

- 

- 

- 
|   | ​ | ArUco Marker 테스트Navigation 파라미터 튜닝 |   |

- 

- 

- 

- 

- 

- 

- 

- 
|   | Pinky 적재 공간 파츠 제작(1대 장착 완료)양품, 불량품 계속 출력(종류별 양품 2개 불량품 3개 제작 완료)개인 로봇팔 고치기(완료)로봇팔 기술조사서 수정 | Pinky 3대 모두 적재 공간 장착개인 로봇팔 코드 아두이노 C++ → 주피터랩으로 코드 변환 적재 로봇팔 팀 도와주기 | 10시에 취업 지원 상담 |

- 

- 

- 

- 

- 

- 

- 
|   |   | ​Navigation 파라미터 튜닝ArUco Marker 연동 테스트Map에 Keepout filter 적용Laser Filter | 20시 전 귀가 |

- 

- 

- 
|   | 적재기술조사 |   |   |
|   |   |   | 개인 사유로 결근 |

- 

- 

- 

- 
|   | 주형 샘플 bounding box 촬영작업 마무리 완료(사진, 영상 작업)->기술 조사 피드백 사항 수정완료 -> | Bounding box 매칭 관련해서 카메라 Calibration 진행이후 bounding box와 실제 데이터 매칭 진행 |   |
|   | 주형 샘플 bounding box 촬영작업 마무리 완료(사진, 영상 작업)->기술 조사 피드백 사항 수정완료 -> | Bounding box 매칭 관련해서 카메라 Calibration 진행이후 bounding box와 실제 데이터 매칭 진행 |   |   |

- 

  - 

- 
| To Do | 오늘까지 현재 작업 중인 것 완료 → 내일 시연 시나리오 1시간 정도 다같이 논의 필요 (주말에 각자 생각 어느정도) 내일: 관제 파트 시작!!!!  sprint3 관련 계획 세우기 & 지라 사용법 숙지 (링크 공유) |

#### Standup_20260407 (15207955)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15207955
**최종 수정**: v4 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 10:00 - 13:00 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 
[](https://pinkwink.kr/1228#google_vignette)

- 
|   | 어제 피드백 받은 것 토대로 SA 제출 sprint2 발표 팀원들 기술조사 관련 피드백 | confluence presentation extension app 설치 및 자료 공유 | 결석 |

- 

|   | 실험1번 | 관제 기술조사 시작스키마 작성 도움 |   |

- 

- 

- 
|   |   | 관제 시스템 리서치 |   |

- 

- 

|   |   | (patchcore - 맨홀 데이터) |   |

- 

- 
|   |   | docking server 정리 마무리 |   |

- 

- 

- 

- 

- 

- 
|   | Pinky 3대 모두 적재 공간 장착적재 로봇팔 팀 도와주기Robot Arm 그리퍼 보조장치 테스트Pouring Cycle Time test 진행 완료 | Robot Arm 그리퍼 보조장치 최적화적재 - Slot 형 컨테이너 설계 및 출력 |   |

- 

- 

- 

- 

- 
|   | Navigation param 튜닝 완료Laser Filter 필요성 검증Keepout filter 적용 | 관제 시스템 리서치 |   |

- 

- 
|   | 실험1번 | Slot 형 컨테이너 출력후 적재 실험2 진행 |   |

- 

- 
|   |   | Robot Arm 그리퍼 보조장치 최적화컨베이어 와이파이 연결 |   |

- 

- 

- 

- 

- 
|   | Bounding box 매칭 관련해서 카메라 Calibration 진행 =>  , 이후 bounding box와 실제 데이터 매칭 진행 -> | 카메라 Calibration 시 왜곡 보정의 개선 필요.Bounding Box와 실제 데이터 간의 매칭 격차 줄이기Camera Calibration 기술조사 항목 마무리 -> |   |
|   | Bounding box 매칭 관련해서 카메라 Calibration 진행 =>  , 이후 bounding box와 실제 데이터 매칭 진행 -> | 카메라 Calibration 시 왜곡 보정의 개선 필요.Bounding Box와 실제 데이터 간의 매칭 격차 줄이기Camera Calibration 기술조사 항목 마무리 -> |   |   |

- 

  - 

  - 

- 

- 
| To Do | 각 Server를 어디서 사용할 건지 필요 현재 yolo position extraction에서 Ubuntu 16GB에서CPU 4%, RAM 70%, GPU 7% 사용됨. (cuda에 올리지 않고) 시나리오 회의 필요 Technical research: 관제 파트 시작 필요 |

#### Standup_20260408 (18546979)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/18546979
**최종 수정**: v18 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 시스템 구축: 다품종 소량 생산 | 미팅시간 | 09:50 - 10:20 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/edit-v2/6389916#4.-%ED%92%88%EC%A7%88-%EA%B2%80%EC%82%AC-%EB%B0%8F-%ED%9B%84%EC%B2%98%EB%A6%AC-(Quality-%26-Post-Processing))

- 

- 

- 

- 

- 

- 
[](https://canva.link/j1x20wqwlz8co6h)

- 

- 
|   | 결근 (remote) SA 작성 | (Data 구조 확인)Github 폴더 구조 클래스룸 제출 완료.  Jira 세팅 Sprint 3 전체 상황 확인 [기술 조사] Binary Classifier with YOLOv26[기술 조사] YOLOv26 + RobotArm Message 보내기SA 검토 완료  Sprint 3 발표 자료 (app installation)관제 시스템 검토 |   |

- 
[](https://dayelee313.atlassian.net/wiki/x/QwANAQ)

- 

- 

- 

- 

- 

- 

|   | 시연 시나리오 작성(애매한거까지 싹다) 작성 ERD 작성 도움 | 관제시스템 구체화ERD (다예 초안) → 예진님 검토 같이 피드백 받은 내용 수정( , ) |   |

- 

- 

- 

- 

- 
|   | 됨웹 대시보드관제 시스템 회의 | PyQt5 관제 UI 최적화open-RMF 관제에 적용 방법 |   |

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/TgFa)

- 

- 

- 

- 

- 
|   | ​시나리오 확정 및 공유ERD 초안 작성사용할 기술 스택 정의(초안)관제 시스템 기능 정리 | (PatchCore) 맨홀 데이터 재수집 필요 → 탑뷰 카메라 사용(위치, 조명 어느정도 고정)관제 시스템 구체화 |   |

- 

- 

- 

- 

- 
|   |   | Docking server 파라미터 조정​추가 팀 협조 |   |

- 

- 

- 

- 

- 

- 
|   | Robot Arm 그리퍼 보조장치 최적화(진행중)적재 - Slot 형 컨테이너 설계 및 출력 | 적재 공간 선반 제작 도가니 제작Robot Arm 그리퍼 보조장치 최적화 |   |

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/TgFa)

- 

- 

- 
|   | 시나리오 확정ERD 초안 작성기술 스택 정리관제 시스템 조사 | 관제 시스템 구체화 |   |

- 

- 

- 

- 

- 
|   | 적재 - 선반 예상 디자인 반영 적재 실험 진행 작성 | SOLIDWORKS  설치적재 공간 선반 제작 보조를 위한 SOLIDWORKS 공부Robot Arm 그리퍼 보조장치 + 핑키 슬롯형바구니 실험 |   |

- 

- 

- 
|   | ESP32 wifi 연결 및 서버와 데이터 송수신 | MQTT를 적용하여 EPS32와 데이터 송수신컨베이어벨트 작동 전체시스템 개발 |   |

- 

- 

- 

- 

- 

- 
|   | Map 시연 시나리오 수정 회의 → Camera Calibration 기술조사 항목 추가 작성->YOLO 활용 가능성 수정방향 제안 → YOLO 프로그램만의 HW 소요자원 추적 기능 추가-> | YOLO 활용방안 구체화 → 실제 주물 + 로봇팔에 적용했을 때 일단 잘 작동하는지 확인 추가 기술조사? TBD. |   |
|   | Map 시연 시나리오 수정 회의 → Camera Calibration 기술조사 항목 추가 작성->YOLO 활용 가능성 수정방향 제안 → YOLO 프로그램만의 HW 소요자원 추적 기능 추가-> | YOLO 활용방안 구체화 → 실제 주물 + 로봇팔에 적용했을 때 일단 잘 작동하는지 확인 추가 기술조사? TBD. |   |   |

- 

- 
| To Do | 오늘 TODO 완료연동 시스템 구축 (다예 초안) → 오후에 다같이 확인 |

#### Standup_20260409 (21430278)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21430278
**최종 수정**: v6 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics | 미팅시간 | 10:00 - 10:05 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 
[](https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/edit-v2/6389916#4.-%ED%92%88%EC%A7%88-%EA%B2%80%EC%82%AC-%EB%B0%8F-%ED%9B%84%EC%B2%98%EB%A6%AC-(Quality-%26-Post-Processing))

- 

- 

- 

- 

- 

- 
[](https://canva.link/j1x20wqwlz8co6h)

- 

- 

- 

- 

- 

- 

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/G4BNAQ)
|   | (Data 구조 확인)Github 폴더 구조 클래스룸 제출 완료.  Jira 세팅 Sprint 3 전체 상황 확인 [기술 조사] Binary Classifier with YOLOv26[기술 조사] YOLOv26 + RobotArm Message 보내기SA 검토 완료  Sprint 3 발표 자료 (app installation)관제 시스템 검토 | ERD 최종본 논의[확인] UI → DB 연결 클래스룸 회의록 제출 [Implementation] Binary Classifier with YOLOv26관제 시스템 검토 깃헙 폴더 구조 만들어서 클래스룸 제출 연동 테스트 확인 |   |

- 

- 

- 

- 

- 

- 
|   | 관제시스템 구체화ERD 검토피드백 받은 내용 수정( , ) | 1차 연동 테스트ERD 수정디비랑 관제 서버 연결 |   |

- 

- 
|   |   | GUI 업데이트 (웹, PyQt5) |   |

- 

- 

- 
|   |   | 1차 연동 테스트[Implementation] YOLOv26 + RobotArm Message 보내기 |   |

- 

- 
|   |   | docking server 구현 |   |

- 

- 

- 

- 

- 

- 

- 
|   | 적재 공간 선반 제작  도가니 제작Robot Arm 그리퍼 보조장치 최적화 | 슬롯형 적재함 + 그리퍼 보조장치 테스트선반 프로토 타입 출력 후 테스트불량 주물 패턴 수정 및 출력컨베이어 벨트 패턴 정렬 가이드 설계 및 출력 |   |

- 

- 

- 
|   |   | 1차 연동 테스트docking server 구현 |   |

- 

- 

- 

- 
|   | SOLIDWORKS  설치적재 공간 선반 제작 보조를 위한 SOLIDWORKS 공부 | SOLIDWORKS - 적재 공간 선반 제작  Robot Arm 그리퍼 보조장치 + 핑키 슬롯형바구니 실험 |   |

- 

- 

- 
|   |   | 선반제작컨베이어 제어 테스트 |   |

- 

- 

- 

- 
|   | YOLO 학습용 맨홀 목업 샘플 종류, 상태, 및 위치별 촬영 및 라벨링 작업 진행->YOLO 좌표와 로봇팔 gripper 간의 좌표 매칭 진행 → 미완성 | YOLO 학습용 맨홀 목업 샘플 라벨링 Class 재설정 후 업로드TBD |   |
|   | YOLO 학습용 맨홀 목업 샘플 종류, 상태, 및 위치별 촬영 및 라벨링 작업 진행->YOLO 좌표와 로봇팔 gripper 간의 좌표 매칭 진행 → 미완성 | YOLO 학습용 맨홀 목업 샘플 라벨링 Class 재설정 후 업로드TBD |   |   |
| To Do |   |

#### Standup_20260410 (23166977)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/23166977
**최종 수정**: v3 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics | 미팅시간 | 10:00 - 10:05 |
| 팀명 | 에러맛집 | 참석자 |   |
[](https://dayelee313.atlassian.net/wiki/x/D4Bl)
[](https://dayelee313.atlassian.net/wiki/x/G4BNAQ)
| 팀이슈 | 중요! https://dayelee313.atlassian.net/wiki/x/D4Bl  작성 시작 https://dayelee313.atlassian.net/wiki/x/G4BNAQ  완성 확인 |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/TgFa)

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/G4BNAQ)

- 

- 
|   | ERD 최종본 논의[확인] UI → DB 연결 클래스룸 회의록 제출 깃헙 폴더 구조 만들어서 클래스룸 제출 | ERD 최종본 논의 (with  ) 작성 → 클래스룸 초안 제출 깃헙 폴더 구조 제출연동 테스트 확인Jira 오늘 물어보기 sprint3 발표 준비 |   |

- 

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/PYA5)

- 

- 
|   | DB 서버 만들고 control 서버랑 연동기존에 쓰던 DB(기수님꺼) 데이터 옮겨둠 (연동 된 상태)DB 서버 접속방법 적어둠(참고) | ERD 완성State Diagram |   |

- 

- 

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/G4A0AQ)
|   | SQLite에서 PostgreSQL로 DB 마이그레이션 진행메인서버와 DB서버 분리후 연동 테스트 완료 | GUI 버전 문서 업데이트Github folder structure 완성 및 만들기 |   |

- 
[](https://dayelee313.atlassian.net/wiki/x/G4BNAQ)

- 

- 
|   | 1차 연동 테스트 | 1차 연동 테스트 마무리[Implementation] YOLO26 + RobotArm Message 보내기 (정확도 실험) |   |

- 

- 

- 
|   |   | 팀 협업 ( )​AMR 점검 |   |

- 

- 

- 

- 

- 

- 
|   | 슬롯형 적재함 + 그리퍼 보조장치 테스트   진행중불량 주물 수정본 출력 및 전달 | ROS2 공부컨베이어 벨트 패턴 정렬 가이드 설계 및 출력적재 선반 랙 테스트 진행 |   |

- 
[](https://dayelee313.atlassian.net/wiki/x/G4BNAQ)

- 

- 
|   | 1차 연동 테스트 | 1차 연동 테스트 마무리State diagram |   |

- 

- 

- 

- 

****

- 
|   | SOLIDWORKS - 적재 공간 선반 제작  Robot Arm 그리퍼 보조장치 + 핑키 슬롯형바구니 실험 | 결근(remote) 실험 2 작성 | 4월 10일 개인사유로 결석 |

- 

- 

- 
|   |   | 컨베이어벨트 - 관제서버 신호 송수신뎁스카메라 데이터-로봇팔 연동 |   |

- 

- 

- 

- 

- 
|   | 재작업 타원(Ellipse) 샘플 추가하여 YOLO 맨홀 이미지에 대한 라벨링 진행->​라벨링된 데이터셋(dataset_cls)에 대해 분류(classification) 작업 진행-> | 분류 작업 완료 상황 및 추가 검증작업 진행 및 Confluence 문서 구체화->, 슬롯형 적재함(핑키봇에 탑재)에 하차용 샘플 위치에 대한 YOLO 데이터셋 확보 및 분류 작업 진행  ​이후 Classification+Localisation, Object Detection으로 진행 여부 검토. |   |
|   | 재작업 타원(Ellipse) 샘플 추가하여 YOLO 맨홀 이미지에 대한 라벨링 진행->​라벨링된 데이터셋(dataset_cls)에 대해 분류(classification) 작업 진행-> | 분류 작업 완료 상황 및 추가 검증작업 진행 및 Confluence 문서 구체화->, 슬롯형 적재함(핑키봇에 탑재)에 하차용 샘플 위치에 대한 YOLO 데이터셋 확보 및 분류 작업 진행  ​이후 Classification+Localisation, Object Detection으로 진행 여부 검토. |   |   |
| To Do |   |

#### Standup_20260413 (26050825)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26050825
**최종 수정**: v9 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 10:00 - 10:10 |
| 팀명 | 에러맛집 | 참석자 |   |

- 

- 
[](https://drive.google.com/drive/folders/1sy_DrZzGC4zW0k4P_XuPuyBOPSjV3N0q?usp=sharing)
| 팀이슈 | 각자 페이지 링크 구글 드라이브 |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 
|   |   | spinrt3 발표 준비 (완)VLA 기술 조사 (완)각종 diagram 클래스룸 제출 (완) |   |

- 

- 

- 

- 
|   |   | ERD 드라이브 폴더 구조 만들기관제 |   |

- 

- 

- 

- 

- 

- 

- 
|   | State diagram (Manhole) | PyQt5 GUI 최적화 업데이트센서 브라켓 수정 (3D) | 에드인애듀 취업 상담14:00~14:30 (3F)스탠드업 이후 병원 방문 예정(감기) |

- 

- 

- 
|   |   | [Implementation] VLA 모델 조사 |   |

- 

- 

- 
|   | ( )​Docking server 실증 | Docking server 완료 |   |

- 

- 

- 

- 

- 

- 

- 

- 

- 
|   | 컨베이어 벨트 패턴 정렬 가이드 설계 및 출력 | 물류 출고/ 심화 적재 로봇팔 Robot Arm 그리퍼 보조장치 시뮬레이션  주조 로봇팔 그리퍼 최적화 연구(주형 제작, 주탕, 탈형)  Sequence Diagram 피드백ROS2 공부 | 일요일 몸살로 고생(약 먹고 회복) |

- 

- 

- 

- 

- 

- 
|   |   | 관제 시스템 | 스탠드업 이후 병원 방문 예정(감기) |

- 

- 

****

- 

- 

- 

- 

- 
|   | 결근(remote) 실험 2 작성 | 물류 출고 및 상차 심화 적재 로봇팔 Robot Arm 그리퍼 보조장치 시뮬레이션  주조 로봇팔 그리퍼 최적화 연구(주형 제작, 주탕, 탈형)  다이소 모래 3개 구입 준비물 테이블 page | 에드인애듀 취업상담 16:00 ~ 16:30 |

- 

- 

- 

- 

- 

- 

- 

- 
|   | 컨베이어벨트 제어시스템 관제서버 연동 협조 | Robot arm 제어함수 분석(수치, 방향, 좌표 등)Class diagram 수정작업관제팀 협조요청시 협업 | ​에드인애듀 취업상담 14:30 ~ 15:00일요일 고열로 고생(39도) |

- 

- 

- 

- 

- 

- 

- 
|   | 분류 작업 완료 상황 및 추가 검증작업 진행 및 Confluence 문서 구체화->, 슬롯형 적재함(핑키봇에 탑재)용 샘플 위치에 대한 YOLO background 이미지 데이터셋 확보YOLO background cls 포함한 Image Classification 진행(Remote)Interface Specification 초안 작성-> | ​YOLO Image Classification 추가 작업(background issue)->정리 필요이후 Classification+Localisation, Object Detection으로 진행 여부 검토.Interface Specification 추가작업? |   |
|   | 분류 작업 완료 상황 및 추가 검증작업 진행 및 Confluence 문서 구체화->, 슬롯형 적재함(핑키봇에 탑재)용 샘플 위치에 대한 YOLO background 이미지 데이터셋 확보YOLO background cls 포함한 Image Classification 진행(Remote)Interface Specification 초안 작성-> | ​YOLO Image Classification 추가 작업(background issue)->정리 필요이후 Classification+Localisation, Object Detection으로 진행 여부 검토.Interface Specification 추가작업? |   |   |
| To Do |   |

#### Standup_20260414 (26248598)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26248598
**최종 수정**: v11 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics - 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 09:50 - 10:10 |
| 팀명 | 에러맛집 | 참석자 |   |

- 

  - 

  - 

- 
| 팀이슈 | 어제 민형기 강사님 MQTT 관련 피드백 이해? 로봇끼리는 ROS, 나머지 서버는 MQTT 를 구분해서 (HTTP, TCP ,… → MQTT) 슬랙에 피드백 컨펌 받고 → 드라이브에 영상/이미지 옮기기 (용석이~~~~) |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 
[](https://dayelee313.atlassian.net/wiki/x/TgFa)

- 

- 

- 
|   | VLA 모델 조사 Sprint3 발표 자료 작성 및 발표 detailed design classroom 제출 | ERD  [ Jira sprint setting | 아픔 |

- 

- 

- 

- 

- 
|   | ERD 드라이브 폴더 구조 만들기관제 | ERD 수정관제 |   |

- 

- 

- 

- 

- 

- 

- 
|   | 컨베이어 벨트 센서 브라켓 업그레드PyQt5 GUI 버그 수정(그래프 관련, 기타)고객 웹페이지 (주문 단계 위치 수정) | Docking server 관제 시스템(FMS 구현)System Architecture v6 버전의 통신규약으로 코드 수정Confluence 최신 문서를 반영해서 코드 업데이트 |   |

- 

- 

- 
|   |   | 연동 테스트 v2 canva 링크 SW 그림 (MQTT) 전환 |   |

- 

- 
|   | docking server | docking server 구현 |   |

- 

- 

- 

- 
|   | 물류 출고 / 심화 적재 로봇팔 Robot Arm 그리퍼 보조장치 시뮬레이션 | 물류 심화 적재 문제 해결주조 공정 로봇팔 시뮬레이션 | 15:00 ~ 15:30 취업 상담 |

- 

- 

- 

- 

- 
|   | ros-tailscale initial peer 테스트관제 | docking server 구현관제 |   |

- 

- 

- 

- 

- 

- 
|   | 모래구입물류 출고 / 심화 적재 로봇팔 Robot Arm 그리퍼 보조장치 시뮬레이션 | 물류 심화 적재 문제 해결주조 공정 로봇팔 시뮬레이션 비용처리 | 병원 방문예정 |

- 

- 
|   | Robot arm Gripper End effector 위치데이터 수집 | Robot arm Gripper End effector 위치이동 함수 개발 |   |

- 

- 

- 

- 

- 
|   | [YOLO Image Classification] 슬롯형 적재함(핑키봇에 탑재)용 샘플 Image Classification 진행->[YOLO Image Classification]컨베이어 벨트에서 맨홀 샘플(신규 제작된 Ellipse포함)로 훈련 후 추론(background issue 해결)-> | 슬롯형 적재함용 샘플 Image Classification 진행-> 부적합-> Object Detection으로 전환여부 검토슬롯형 적재함용 샘플의 Object Detection 진행 | 10:30 - 11:00 취업상담 |
|   | [YOLO Image Classification] 슬롯형 적재함(핑키봇에 탑재)용 샘플 Image Classification 진행->[YOLO Image Classification]컨베이어 벨트에서 맨홀 샘플(신규 제작된 Ellipse포함)로 훈련 후 추론(background issue 해결)-> | 슬롯형 적재함용 샘플 Image Classification 진행-> 부적합-> Object Detection으로 전환여부 검토슬롯형 적재함용 샘플의 Object Detection 진행 | 10:30 - 11:00 취업상담 | 10:30 - 11:00 취업상담 |

- 
| To Do | ERD 완성 (다예, 예진, GUI 기수) → 예외 상황 시나리오 dummy data 생성 → 관제 시스템 개발 |

#### Standup_20260415 (26054115)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26054115
**최종 수정**: v4 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics - 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 9:40 - 9:50 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 
[](https://dayelee313.atlassian.net/wiki/x/TgFa)

- 

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-38)

- 
[](https://dayelee313.atlassian.net/browse/SR-28)
|   | ERD  [ | standup meeting classroom 제출 ERD 초안 완료 (최소한으로 완료)[Technical Research] VLA 연동 및 학습 |   |

- 

- 

- 

- 
|   | ERD 수정 | 가상데이터 만들기_시나리오3기준관제시스템 설계_시나리오3 기준 |   |

- 

- 

- 

- 

- 

- 
|   | GUI 업데이트 (웹, PyQt)Confluence 최신 문서를 반영해서 코드 업데이트 | GUI 업데이트 (웹, PyQt)GUI 업데이트 버전 문서 정리 |   |

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-61)

- 
|   | Jira settings | Kubernetes 기술조사 | 지각 |

- 

- 
|   |   | Docking server 마무리 |   |

- 

- 

- 
|   | Robot Arm 선반 적재 출고 (3층) 하드 코딩 완료 | Robot Arm 선반 적재 출고 (2층) 하드 코딩 완료하기Robot Arm 주조 공정 시뮬레이션 |   |

- 
[](https://dayelee313.atlassian.net/browse/SR-66?atlOrigin=eyJpIjoiN2I3MTU5ZDVmNTU4NDA4NzgwZjQ0OGExMmNhYzBkZWIiLCJwIjoiaiJ9)

- 

  - 

  - 
|   | Docking server 구현 | 강사님께 질문 후Tailscale-rosDocking server 마무리 |   |

- 

- 

- 

- 
|   | 지출 관리 1차 제출완료 Robot Arm 선반 적재 출고 (3층) 오류 수정 | Robot Arm 주조 공정 시뮬레이션Robot Arm 선반 적재 출고 (2층) 하드 코딩 완료하기 |   |

- 

- 

- 
|   | ​그리퍼 적용 함수 조사그리퍼 적용 함수 개발(핑키에서 줍기) | 그리퍼 적용 함수 개발(핑키에서 줍기) |   |

- 

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-51)

- 
[](https://dayelee313.atlassian.net/browse/SR-35)[](https://dayelee313.atlassian.net/browse/SR-52)

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-50)
|   | 슬롯형 적재함용 샘플의 Object Detection 진행(업로드 해야함)슬롯형 적재함용 샘플 이미지 데이터셋 추가 촬영[Classification]Confusion matrix 축 labeling 설명 추가Jira 담당 파트 subtask 정리->링크1, 링크2 | 슬롯형 적재함용 샘플의 Object Detection 추가 진행Jira 담당 파트 subtask 추가 정리 |   |
|   | 슬롯형 적재함용 샘플의 Object Detection 진행(업로드 해야함)슬롯형 적재함용 샘플 이미지 데이터셋 추가 촬영[Classification]Confusion matrix 축 labeling 설명 추가Jira 담당 파트 subtask 정리->링크1, 링크2 | 슬롯형 적재함용 샘플의 Object Detection 추가 진행Jira 담당 파트 subtask 추가 정리 |   |   |

- 
| To Do | sprint3 최종 기능의 30% :  시나리오 3번째 (예외 상황 시나리오 구성) GUI → DB → |

#### Standup_20260416 (30114473)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/30114473
**최종 수정**: v4 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics - 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 9:40 - 9:50 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 

- 

- 

- 
|   | 드디어 ERD 설계 완성 용어 정리 검토 sequence diagram 검토 | [Dataset] DB 예외 상황에서 가상 데이터 구축 [Implementation] 관제 시스템[Technical Research] VLA [용어 정리] State Diagram (AMR 파트) | 수면 부족 |

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
|   | RFIDRFID 필요 물품 서칭->기수님 구매완료 | 가상데이터로 시나리오3 관제 테스트erd dbdiagram 그리기[용어 정리] State Diagram (RobotArm 파트) |   |

- 

- 

- 

- 

- 

- 

- 
|   | (TCP 통신 인터페이스 구현) | PyQt <--> AMR 통신 인터페이스 연동 테스트GUI 업데이트[용어 정리] State Diagram (manhole 파트) |   |

- 
[](https://dayelee313.atlassian.net/browse/SR-88)

- 
[](https://dayelee313.atlassian.net/browse/SR-86?atlOrigin=eyJpIjoiMTBiZDVlZTg3NTBhNDUzYWFjMWU4YThlYWY4MmNjODEiLCJwIjoiaiJ9)

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-89)

- 
[](https://dayelee313.atlassian.net/browse/SR-87)
|   | Docker 도입 가능성 검토Kubernetes(K8s) 도입 가능성 검토 | ​Docking Server 테스트(오전)Docker 구현 및 테스트K8s 구현 및 테스트 |   |

- 

- 

- 
|   | Docking server 테스트 | DB Cloud 서비스 적용 방법 및 비용 정리 |   |

- 

- 

- 

- 
|   | Robot Arm 선반 적재 출고 (3, 2층) 하드 코딩 완료Sequence Diagram 일부 수정 | Robot Arm 선반 적재 출고 (1층) 하드 코딩 완료하기Sequence Diagram 피드백 |   |

- 
[](https://dayelee313.atlassian.net/browse/SR-66?atlOrigin=eyJpIjoiZTE3ZDQ4OTM0NzU2NDYzZmI2N2ViZTUzNzhmZTA5MGMiLCJwIjoiaiJ9)

- 
[](https://dayelee313.atlassian.net/browse/SR-66?atlOrigin=eyJpIjoiZTE3ZDQ4OTM0NzU2NDYzZmI2N2ViZTUzNzhmZTA5MGMiLCJwIjoiaiJ9)

- 
|   | Docking Server 테스트 | Docking server 테스트관제PC, 각 로봇 공유기 IP 설정 |   |

- 

- 

- 
|   | Robot Arm 선반 적재 출고 (3, 2층) 하드 코딩 완료 | Robot Arm 선반 적재 출고 (1층) 하드 코딩 완료하기 |   |

- 

- 

- 

- 
|   | 컨베이어 카메라 서버 시리얼 연결​Robot arm 좌표 함수분석 | 컨베이어 관제시스템 시리얼 연결 구축[용어 정리] Class Diagram | ​14:30 조퇴 |

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-52)

- 
[](https://dayelee313.atlassian.net/browse/SR-50)

- 
[](https://dayelee313.atlassian.net/browse/SR-52)

- 

- 
|   | 03_technical_research 개인 작성항목 정리Jira Detection subtask 진행Jira Classification subtask 정리 | Jira Detection subtask 마무리슬롯형 적재함 맨홀 샘플 detection 마무리(추가 라벨링 포함)[용어 정리] Interface Specification |   |
|   | 03_technical_research 개인 작성항목 정리Jira Detection subtask 진행Jira Classification subtask 정리 | Jira Detection subtask 마무리슬롯형 적재함 맨홀 샘플 detection 마무리(추가 라벨링 포함)[용어 정리] Interface Specification |   |   |

- 
| To Do | [Everyone] 용어 정리 기반 → 작성한 문서 정리 (특히 diagram 그리신 분들 → 지라 테스크 있습니다) |

#### Standup_20260417 (34996292)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/34996292
**최종 수정**: v6 (2026-04-21 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | SmartCast Robotics - 사형 주조 공정 스마트 팩토리 구축 | 미팅시간 | 9:40 - 9:50 |
| 팀명 | 에러맛집 | 참석자 |   |
| 팀이슈 |   |

****
****
****
****
| 팀원 | 어제 한 일 | 오늘 할 일 | 비고 |
|---|---|---|---|

- 

- 

- 

- 

- 

- 
|   | ERD 수정 | [Dataset] DB 예외 상황에서 가상 데이터 구축 [Github] [Implementation] 관제 시스템[Technical Research] VLA [용어 정리 및 수정] State Diagram (AMR 파트) |   |

- 

- 

- 

- 

- 
|   | 테스트 DB 만들고 가상데이터 테이블 작성(시나리오3기준)ERD 그리기State Diagram 수정 (RobotArm 파트) | 가상데이터로 시나리오3 관제 테스트 실험 진행 |   |

- 

- 

- 

- 
|   | (배터리 모니터링 가능 SSH - Ok, ROS2- Fail) | RFID testPyQt GUI 업데이트 @이다예 |   |

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-89)

- 
[](https://dayelee313.atlassian.net/browse/SR-87)

- 
|   | Docking server 테스트 | Docker 구현 및 테스트K8s 구현 및 테스트 | 지각 |

- 

- 

- 
|   |   | DB Cloud 서비스 테스트RFID 테스트 |   |

- 

- 

- 

- 

- 

- 
|   | Robot Arm 선반 적재 출고 하드 코딩 완료  Robot Arm Pouring 테스트  Sequence Diagram 수정 | Robot Arm 선반 적재 영상 업로드Robot Arm Mold Making 테스트  Sequence Diagram 수정 |   |

- 
[](https://dayelee313.atlassian.net/browse/SR-66?atlOrigin=eyJpIjoiNTExYzNlNTI0MzkxNDk2NmFhNzg0ZGNkNDJiZDQxNjIiLCJwIjoiaiJ9)

- 

- 
[](https://dayelee313.atlassian.net/browse/SR-66?atlOrigin=eyJpIjoiNTExYzNlNTI0MzkxNDk2NmFhNzg0ZGNkNDJiZDQxNjIiLCJwIjoiaiJ9)

- 
[](https://dayelee313.atlassian.net/browse/SR-66?atlOrigin=eyJpIjoiNTExYzNlNTI0MzkxNDk2NmFhNzg0ZGNkNDJiZDQxNjIiLCJwIjoiaiJ9)
|   | Docking 구현 완료 | 공유기 받아서 고정 ip 설정undock, 여러 장소 테스트Docking server 문서 정리 | 15시 조퇴 |

- 

- 

- 
|   | Robot Arm 선반 적재 출고 하드 코딩 완료  Robot Arm Pouring 테스트 | Robot Arm Mold Making 테스트 | 14시 조퇴 |

- 
[](https://drive.google.com/file/d/1shBCUnkBgMjy4xyBRVMsIUMtFpk0VkEc/view?usp=sharing)

- 

- 

- 

- 
|   | 통신구조 재설계 및 테스트(MQTT->시리얼)Class diagram 수정 및 정리 | ​통신구조 재설계 내용정리Realsense D455 작동테스트Class diagram 수정 |   |

- 
[](https://dayelee313.atlassian.net/browse/SR-59)

- 
[](https://dayelee313.atlassian.net/browse/SR-55)

- 
[](https://dayelee313.atlassian.net/browse/SR-35)

- 
[](https://dayelee313.atlassian.net/browse/SR-55)

- 
|   | 슬롯형 보관함 맨홀 샘플 detection 데이터셋 수집슬롯형 보관함 맨홀 샘플 Detection 훈련 진행Interface Specification 용어 정리 | 슬롯형 보관함 맨홀 샘플 Detection Confluence 기술조사 마무리Detection(로봇팔), Classification(콘베이어 벨트) 현장 연동 검토 |   |
|   | 슬롯형 보관함 맨홀 샘플 detection 데이터셋 수집슬롯형 보관함 맨홀 샘플 Detection 훈련 진행Interface Specification 용어 정리 | 슬롯형 보관함 맨홀 샘플 Detection Confluence 기술조사 마무리Detection(로봇팔), Classification(콘베이어 벨트) 현장 연동 검토 |   |   |

- 

- 
| To Do | 공유기 언제 주시는지 ERD → 가상 데이터 수집 → 예외 상황 시나리오 (관제 만들고) → AMR charging |

#### 회의록_20260000 (950273)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/950273
**최종 수정**: v3 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 |   | 회의일시 | 10:00 - 13:00 |
| 팀명 | 에러 맛집 | 작성자 |   |
| 참석자 |   |
| 회의안건 |   |
| 회의내용 |   |
| 결정된 사안 |   |

#### 회의록_20260325_시나리오 설계안 발표 (1867783)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/1867783
**최종 수정**: v5 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 주조 공장 스마트 팩토리 자동화 | 회의일시 | 16:30 - 17:00 |
| 팀명 | 에러 맛집 | 작성자 |   |
| 참석자 |   |
| 회의안건 | 시나리오 설계안 발표 및 피드백 |

- 

- 

- 

  - 
****

    - 

  - 
****

    - 

    - 

  - 
****

    - 

  - 
****

    - 

  - 
****

    - 

    - 

  - 
****

    - 

  - 
****

  - 
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
| 회의내용 | <공통  사항> V-model 숙지주조 및 물류 도메인 용어 및 프로세스 사전 조사오늘 피드백 핵심 정리: 프로젝트는 다음과 같은 흐름으로 진행,도메인 조사일반화된 프로세스 및 현장에서 사용하는 용어 파악문제 정의 및 분석현재 프로세스에서 자동화가 필요한 부분 식별사람이 해야 하는 일 vs 자동화 가능한 일 구분User Requirements 정의 (V-model 시작)기능 요구사항 / 비기능 요구사항 구분시나리오 설계요구사항을 기반으로 실제 동작 흐름 구성System Requirements 정의HW / SW 구조데이터 흐름, 인터페이스, GUI 등우선순위 결정구현 범위 설정 (MVP 기준)구현피드백 및 반복 개선<2팀 피드백> 현실 반영 주조 작업은 대부분 로봇팔 + 컨베이어 작업에 의존물류 이동은 주로 AMR 발표 전략 품질 과장 금지: 실제 발표시, 품질을 너무 내세우면 안 될 것 같다. (품질을 기대할 수 없으므로 과장 x)특정 기업 프로세스 기반 구현으로 표현 사실 모든 팩토리마다 과정이 조금씩 다를 것이기 때문에, 실제 어떤 회사에 존재하는 과정을 모티브로 따와서 구현했다. 라는 정도가 좋을 것 같다. 시스템 설계 핵심 FMS (Facility Management System) 상위 계층 (FMS/관제)중간 계층 (실제 통제받는 장비들) 네트워크 장애 대응: FMS에서 고민해야할 점은, 중앙 통제시스템과 중간 계층의 네트워크가 끊겼을 경우, 로봇의 독립적인 동작이 가능해야한다. 이 경우, 로봇이 어디까지 기능할 수 있을 것인가를 생각해야하는데, 관제와 끊긴 경우, 로봇은 현재 작업 마무리 → 안전 위치로 이동 → 대기 의 작업같이 독립적으로 동작 가능해야 좋은 설계이다. 보통은 관제 layer는 모니터링만 하고, task는 장비 layer에서 진행된다. 이러한 상황들은 보통 만드는 제품에 따라 상이하다. 보통 일어나는 상황 로봇팔은 자율주행로봇과는 다르게, 모든 움직이는 과정이 빠르다. 따라서, 제어 속도가 매우 빨라야하는데, 관제 Layer에서 통제하는 것은 잘 작동하지 않을 것이다. 결론적으로, [제어는 장비단계에서, 관제에서는 모니터링을 하는 게 예외 상황 처리 시 안전하다] -> 이미 이렇게 되어 있는데 발표 아키텍처에서 잘 안보인 것 같다. 용석이 그림 수정 System Architecture:소프트웨어 제품, 웹서비스 제품에 따라 표준이 없다. 특히, 로봇쪽은 사용자 관점, ~ 관점 등 바운더리가 넓어서 아키텍쳐로 표현을 할 때 아키텍쳐가 달라진다.주로 layer를 (2팀이 한 것처럼) 상위 계층 (UI, 서비스, 관제 레벨) -> 딥러닝 서버 -> 하위 계층 (장비 의존도 증가) 만약, 이러한 layer가 많아질 경우, 테트리스로 오른쪽/왼쪽에 그림을 배치하기도 한다. 나중에 system requirements 가 고정된 경우에 고쳐야하는 상황이 오기 때문에, 작업의 종류, user requirements 어디까지 구현할지 정하면 된다. [제안] layout 을 먼저 정하는 게 도움이 될 것 같다. 물리적 공간을 설계하면, 아래 사항과 같은 것을 결정할 수 있다. 1) 작업 흐름 결정 (어디서 → 어디로 이동?) 2) 로봇 역할 결정3) 시스템 구조 결정 (데이터 흐름, 필요한 제어)layout 없이 시스템 설계하면 현실성 없는 구조가 된다. <3팀> 사업검토: 시장 조사, 프로젝트가 왜 필요한지. 개발자로서 해야할 부분: 1. 조사: 요양원에서 어떤 업무들이 있고, 사람들이 각자 어떤 업무를 분배받았으며 예를 들어, 공무원들은 1인 케어를 많이 하는데, 인력이 부족해서 이 주제가 굉장히 핫하다.2. 분석: 사람이 현재 하는 일 중에, 사람만이 해야하는 일과 사람이 없어도 로봇을 이용해 자동화할 수 있는 부분이 무엇인지를 구분한다. 로봇은 사람과 다르게, 여러 task에 대해서 잘 할 수 있는 특징이 있다. 사람은 자기가 잘 하는 것만 잘 하기 때문에. 3. 시나리오 결정: 위의 내용을 바탕으로 각 해결점에 대하여 시나리오를 작성하면 될 것이다. 위에서 분석 과정이 끝나면, 요양원에서 필요한 것이 필요한지 보인다. 보통 client 에서 필요한 것을 명시하지만, 우리는 시장 조사를 통해서 알아갈 수 밖에 없다. !!!! 어떤 성격의 “기능”을 만들지 결정! V-model User requirements: [중요] 기능/비기능으로 나누자. (Spec)System requirements: 하드웨어/소프트웨어, 주고받는 데이터 구조, GUI 등 4. 우선순위 결정: 위의 시나리오에서 결정한 것 중 구현의 우선순위를 결정해야한다. 최소로 필요한 시나리오를 먼저 완성하는 것이 중요할 것. <1팀 피드백> 팔의 작업과 AMR의 작업 분배가 밸런스가 안 맞을뿐더러 작업량이 많은 팔이 하드웨어에 비해 고난이도의 정밀도를 요구한다. 작업량이 없는 AMR은 주행은 또 거의 없다. —> 결론, [로봇들의 작업 분배를 적절히 하는 것이 좋다!] 팀이랑 미팅을 해서, 원하는 것을 채워줄 수 있는 다른 아이템으로 유도를 하고 싶다. 너무 작은 무인매장이 아니라 사이즈가 있는 마트로 가거나, 작업이 하나가 아니라, 입고됐을 때 정리 역할 및 다른 역할도 주면 좋을 것 같다. (주행역할을 높이기 위해 마트로) 대안 하나의 로봇당 2~3개의 작업을 스케줄링을 한다. Priority: 손님이 많을때, 손님이 없고 뭐할때 등으로 결정한다아래와 같은 주행로봇에 대한 시나리오를 더할 수 있다.  시나리오 대로 계속 도는 것 1개 사람을 following 하는 것, 목표는 타겟을 놓치지 않고 가는 것 1개 새로운 맛있는 거 추천해줘 하면 로봇이 사람을 leading 하는 것 1개. 사람과의 거리 인식을 하고 기다리는 것 등의 다른 기능들이 필요 <개인 질문>하나의 로봇이 여러 개의 task를 담당하고 있을 때, 스케줄링의 priority 를 주는 방식은 시스템에 따라 다른가? 그 분야에 대해서 잘 모르는 경우에 스케줄링의 priority 는 어떻게 조사할 수 있을까요? 프로세스가 다 같을 순 없지만 어느정도 일반화가 되어 있고 규칙을 찾아서 조사 과정을 찾아야한다. (조사 필수) 개발자가 처음에 하는 일 1. [조사] 일반화된 프로세스와 용어를 조사 이미 현장에서 사용되는 용어 사용 필수 우리의 경우, 그 분야의 전문가가 없기 때문에, 특정 회사를 타겟하여 그 회사의 프로세스를 구현했다고 시연하면 될 것이다. 2. [Client 의견 접수] client 의 의견이 중요하나, 우리의 프로젝트에서는 프로세스의 여러 단계에서 [분석] 사람이 작업하기 때문에 필요한 단계인지, 근본적으로 필요한 단계를 구분3. [자동화 부분 결정] 위의 분석을 토대로, 자동화 부분을 결정  3. [시나리오 구성] 사람의 작업이 필요한 경우, 어차피 비디오로 찍을 것이기 때문에, 실제로 사람이 해도 되며, 중요한 것은, 비디오에서 각 프로세스가 잘 이해되도록 하는 것이다. Cf)) iOS 는 보장해야하는 프로세스를 말하는 거지, 개발 레벨에서는 살펴만보고 크게 걸리지 않은 선에서 프로토타입 기획을 러프하게 잡으면 된다. <wrap-up>주제가 정할때 인원도 많고, 기간도 긴편이다. -> 프로젝트의 사이즈를 적절하게 조절할 것. 팀 내부에서 너무 진도를 나가지 말고, 피드백을 받고 나가는 게 좋다. 주의할게 강사마다 피드백이 다르기 때문에, 개인의 경험이나 경력 분야가 달라서 그렇다. 적절하게 잘 받으면 된다. 강하게 반대하는 경우에는 그래도 생각해볼 것. [confluence] 시나리오 기획, system requirements 앞으로 주제가 픽스돼서 플젝의 사이즈가 결정되면, system requirements 까지는 confluence에서 작업하면 된다. [jira] spinrt 할 때 [구글 클래스 룸] 오프라인 뿐 아니라 온라인으로 공유 및 피드백 제공 가능 [하드웨어 주의]: 하드웨어를 다룰때 조심히, 바퀴가 달려있으면 브레이크를 채워야해서, 거꾸로 하드웨어를 안전하게 다루는 방법을팔도 카메라 부속품도 있고 홈포지션이 있는 친구들은 그걸 지켜주고, 부담이 덜 되는 위치로 거치를 해주는 게 좋다. |

- 

- 

- 
| 결정된 사안 | V-model기반으로 프로젝트 설계 프로세스를 따른다. 주조 및 물류 도메인 사전 조사 (용어 및 프로세스)를 수행하여, 실제 현장과 유사한 수준으로 프로젝트를 구성한다. user requirements & system requirements 까지 초안을 완성한다. |

#### 회의록_20260326_공장컨택질문리스트 (3539017)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3539017
**최종 수정**: v7 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 주조 공장 스마트 팩토리 자동화 | 회의일시 | 11:20 - 12:20 |
| 팀명 | 에러 맛집 | 작성자 |   |
| 참석자 |   |
| 회의안건 | 주제 선정 관련 - 공장 컨택 리스트업 |

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

    - 

    - 

  - 

    - 

    - 

    - 

    - 

    - 
| 회의내용 | 컨택의 이유 인터넷 조사도 가능하지만, 실제 현장과의 괴리 감소를 위해 실제 현장을 최대한 시연에 반영하기 위함주조 공장 리스트업사형 공장 위주로 보되, 다른 주조 공장도 같이 리스트업 컨택 방법이메일, 전화, 공장 견학, etc  인적 네트워크 활용 확인 사항핑크랩 회사 통해서 컨택 가능한지 확인 현장 작업자들과 관리자에게 따로 컨택이 가능한지 확인 컨택 이후 질문 사항  [주조 공정 프로세스]전체 주조 공정은 어떻게 구성되어 있는가?  [안정성 측면, 위험 작업]어떤 부분에서 안전상 위험한지?  특히 주탕(Pouring) 작업에서 어떤 위험 요소가 있는가?  안전 사고는 주로 어떤 상황에서 발생하는가?  [물리적 측면]가장 무거운 작업은 무엇인가?  반복적으로 수행되는 작업은 무엇인가?  작업자의 피로도가 높은 구간은 어디인가?  [용어] 현장에서 사용하는 주요 용어가 있는가?  [물류 및 이송]주조 이후 제품은 어떻게 이동되는가? (컨베이어 / 크레인 / 수작업 / AGV 등)  어디서 시간 지연이 많이 발생하는가? (병목 구간이 존재하는가?)  이송 과정에서 발생하는 주요 문제는 무엇인가?  [자료 공유 요청]  혹시 가능하다면 “용어집”, “작업 프로토콜”, “안전 수칙” 등의 문서를 공유받을 수 있는가?  [데이터 및 시스템] 공정 데이터 (온도, 시간 등)를 기록하는가?  MES 또는 관제 시스템을 사용하는가?  [품질 및 검사]  불량은 주로 어느 공정에서 발생하는가?  검사는 어떻게 이루어지는가? (육안 / 장비 등) [자동화 관련]현재 자동화가 적용된 공정은 어디인가?  자동화가 어려운 이유는 무엇인가?  자동화를 고려했지만 적용하지 못한 사례가 있는가?  어떤 공정이 자동화되면 가장 효과가 클 것이라 생각하는가?  이 공정에서 가장 힘든 작업은 무엇인가? |

- 
| 결정된 사안 | 함종수 강사님에게 여쭤본 결과, 수요 기업에서 관심이 없기도 하고, 회사 차원에서 물어보는 거라 조심스럽기 때문에 거절하심. |

#### 회의록_20260326_주조가능성시연영상 (3539051)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/3539051
**최종 수정**: v3 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 주조 공장 스마트 팩토리 자동화 | 회의일시 | 11:20 - 12:20 |
| 팀명 | 에러 맛집 | 작성자 |   |
| 참석자 |   |
| 회의안건 | 주조가능성시연영상 |

- 

  - 

  - 

- 

  - 

    - 

  - 

    - 
| 회의내용 | 회의 이유user requirements 에서 주조 분야 자체를 선택 판단을 위해 시연을 통한 주제 확정을 위해 한 일 material (양초, 모래) 구입 후 실제 작동이 될 지 확인사람의 힘을 사용해, 사형 주조 시뮬레이션 확인로봇팔로 실제 압축 작업이 가능한지 확인로봇이 실제 눌렀을 때 사형 제작 시뮬레이션 확인 |

- 

- 

- 

- 

  - 

- 
| 결정된 사안 | 일단 80%까지 시연이 가능함을 확인 적합한 양초 온도 - 중탕기 온도 일정하게 설정 가능 얕고 넓은 패턴 필요 사형 재료 선택을 위해 다양한 재료로 실험 필요 모래,  튀김 가루, 전분 가루, 등등 비디오로 분석 |

#### 회의록_20260330 (5344370)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5344370
**최종 수정**: v5 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 자동화 | 회의일시 | 10:00 - 12:20 |
| 팀명 | 에러 맛집 | 작성자 |   |
| 참석자 |   |
| 회의안건 | SR 검토 및 이번 주 sprint 일정 |

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

    - 

    - 

  - 
| 회의내용 | 2시까지 SR 자기 부분 수정 완료 → 슬랙에 멘션 해서 보내주세요 Map layout: 용석 GUI (예진, 용석, 기수)  → DB (다예, 진성)  GUI (고객, 관리자 모니터링)UI (깃헙에 존재) → DB (다예, 진성) → Techinical Research (이번 주 목요일 완성 목표)정연, 다예 (SR, MAP) 내일까지 → 오늘밤까지! 이번주 목요일 자정까지 Technical Research (팀장에게) 보고 완료DB는 수요일까지UI깃헙 & SR 같이 보면서 → 수정 ERD 만들기(진성) table 하고 계시면(다예) 끝내고 테이블 정리 및 연결LLM, VLA (다예, 진성): 화요일 저녁 ~ 목요일 (금요일~주말)데이터셋 양식, comparative study (우리 HW 사양에 맞는 모델 및할 수 있는 테스크가 뭔지 정리fine-tuning dataset 만드는 방법우리 시스템에 적용가능하지 여부적재팀 (금요일 자정 예외) |
| 결정된 사안 |   |

#### 회의록_20260407_시연 시나리오 결정 (17793046)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/17793046
**최종 수정**: v4 (2026-04-19 sync)

| 과정명 | 심화 ROS2와 AI를 이용한 자율주행&로봇팔 개발자 부트캠프 |
|---|---|
| 프로젝트명 | 사형 주조 공정 스마트 팩토리 구축 | 회의일시 | 10:00 - 13:00 |
| 팀명 | 에러 맛집 | 작성자 |   |
| 참석자 |   |
| 회의안건 | 시연 시나리오 결정 |

1. 

  1. 

    1. 

    1. 

      1. 

      1. 

      1. 

  1. 
****

    1. 

      1. 

  1. 
****

    1. 

      1. 

  1. 
****

    1. 

      1. 

  1. 

1. 

  1. 

  1. 

  1. 

  1. 
| 회의내용 | 시연 시나리오 구상 최종 시연 목표원테이크(각 파트에 로봇을 분산시켜 시연)+파트별로(한 파트에 로봇 몰아서 시연)+예외 처리 상황우선 순위 파트별 구현 먼저예외처리 상황 시연시간 여유 있으면 원테이크 버전 구현주조+이송+검사 시나리오 전체 과정주형 제작-주탕-탈형-상차-이송-후처리-검사적재 +출고 시나리오전체 과정이송 → 적재 / 출고 → 이송예외상황 처리 시나리오 - 이송전체 과정AMR 이동 → 예외 상황 발생 → 관제 호출 → 재할당 → 문제 해결 - 시연 시나리오 구체화  맵 픽스하기파트별원테이크예외 상황 처리 - 시연 시나리오 페이지에 작성,추후에 맵페이지에 내용 업데이트 예정 |

- 

- 

- 
| 결정된 사안 | 원테이크, 파트별 시연, 예외 상황 처리 시연을 모두 진행하는 것을 목표로 시연 시나리오를 구성함우선순위는 파트별 → 예외처리 → 원테이크맵 구성 결정 |

#### 멘토링일지_20260000 (1311219)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/1311219
**최종 수정**: v9 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 사형 주조 기반 스마트 팩토리 시스템 | 팀명 | 에러 맛집 |
****
****
| 멘토링 일자 |   | 멘토 | 노미승 |
****
| 멘토링 내용 |   |
****
| 질문과 답변 |   |
****
| 멘토링 사진 |   |

#### 멘토링일지_260327 (4980960)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/4980960
**최종 수정**: v6 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 맨홀 주조 공장 자동화 | 팀명 | 에러 맛집 |
****
****
| 멘토링 일자 |   | 멘토 | 노미승 |
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

  - 

    - 

    - 

      - 

      - 

      - 

      - 

      - 

- 
``

- 
````

1. 

1. 

- 
``

  - 

- 
``

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

    - 
| 멘토링 내용 | <System Requirements 작성 요령>설명서의 “사용자 가이드”가 아닌, “기능 명세서”를 작성하는 것이다. 특정 장비나 기술 스택 (HW/SW)에 종속되지 않도록 작성한다. → ROS, 특정 카메라 모델 등 명시 금지 이후 단계에서의 HW/SW 설계에서 장비 스펙을 고르는 것이다. 장비는 스펙이 바뀔 수도 있기 때문에, 제약을 두지 않는다. SR_NAME: 팀에서 특정 기능을 통일된 기능명으로 부르기 쉽게 하기 위함이다. SR_NAME은 고유해야 (unique ID)하며, 형식 규칙 정의가 필요하다. 추적 (traceability)를 위함이다. 예) FR-01: 작업 상태 인식, FR-02: 작업자 위험 감지, NFR-01: 응답 시간초안은 큰 기능들로 분류한다.큰 기능이 작은 기능들로 분류되면 기능들의 사이즈가 맞도록 세분화 가능하다.기능이 분류 테스크이면, 분류 타입을 같이 적는다. 예) 사람의 상태를 인식한다. → 인식 상태 (만취, 토한 상태, 우는 상태 등) Description: SR_NAME만 보고 실제 어떤 기능인지 유추하기 힘들기 때문에 상세히 ‘줄글’로 설명한다. 세부항목이 있다면 bullet point로 나누어서 설명한다. “~등 (etc)”라는 모호한 표현이 있으면 안된다.“빠르게” “적절히” “충분히” 같은 표현은 금지한다. 측정 가능한 표현으로 작성한다. 예) 빠르게 처리한다 x → 2초 이내에 처리한다. 기능과 비기능을 따로 구분할 수도 있다. 기능: 시스템이 “무엇을 해야하는지” 정의 비기능: 시스템이 “어떻게 잘 동작해야하는지” 정의Performance (응답 시간): 시스템은 1초 이내에 상태 인식 결과를 반환해야 한다.Accuracy (정확도): (상태 인식 정확도) 상태 인식 정확도는 95%여야 한다. Relability (가용성): (시스템 가용성)시스템은 연간 99%이상의 가용성을 유지해야한다. Scalability (확장성): (확장성) 시스템은 작업 구역 수가 증가하더라도 성능 저하 없이 동작해야 한다.Safty (안전): (작업자 안전) 작업자와 로봇 간 최소 안전 거리(예: 1m)를 유지해야 한다.<System 설계> 설계는 UML로 한다. 로봇은 보통 state diagram + uml이 기본이다. <Map 설계 추천>현재 주조 공정 프로세스만 보면, 로봇팔을 많이 사용하고 AMR이 사용되는 부분은 많이 없어보인다. 아래는 노미승 강사님의 추천이다.하나의 구역을 여러 곳으로 나누기: 하나의 구역 (예) 주조 구역) 을 여러 곳으로 나누어서 AMR이 이동시키는 과정을 추가해서 보여주면 좋다. A → B 지점으로 이동 시 이동 경로가 여러개가 되도록 설계: 현재 가는 길에 놓인 장애물 (다른 AMR)이 있는 경우, 여러 경로를 선택할 수 있는 걸 보이기 위함.<SW 설계 요령>코드 안에 장비 정보를 하드코딩하지 말고 외부 파일 (.xml) 에 따로 저장해라.코드의 확장성을 위함 정적 분석 툴을 이용한다. <Glossary>자동화 공정 (Automation Process): 센서 (IO, Input/Output)와 기계적 장치가 사전에 정의된 규칙과 제어 로직에 따라 연동되어, 사람의 개입 없이 반복적인 작업을 수해앟는 고정. 즉, input → output 이 sequential하게 연결되어 센서/기계들이 맞물려 오차없이 돌아가는 시스템주요 특징:정해진 순서대로 동작반복 작업에 최적화센서 기반 트리거 (조건 → 동작)예시: 컨베이어 벨트를 통한 물체 이송, 센서 감지에 따른 장비 작동 로보틱스 (Robotics): 로봇을 활용하여 환경을 인식하고, 의사 결정을 수행하며, 물리적 동작 (이동, 조작 등) 을 수행하는 기술 및 시스템.즉, 상황을 보고 판단해서 움직이는 시스템주요 구성 요소:알고리즘 (경로 계획, 제어, 인식 등)구동부 (조인트, 모터 등)센서 (카메라, 라이다 등)이동/조작 기능 (주행, 물체 조작 등)특징:동적인 환경 대응 가능자율적인 의사결정 포함 |
****

- 

  - 

  - 

  - 
| 질문과 답변 | SR을 팀 단위로 효율적으로 작성 하는 방법은 무엇인가요?초안은 같이 작업을 하고 큰 틀을 동일하게 이해한 상태에서 분담하여 개별 작성을 한다. 개별 작성 시간에 과정을 검토하고 고민거리가 생기면 (예) 제품 후보군, 큰 기능안에 5개의 소기능으로 분류 등), 다시 모여 같이 검증하고 토론하는 과정을 거친다. 온라인 클래스룸 (초안_팀이름) 이나 슬랙 (특정 강사 언급 등) 으로 작업 과정에서 피드백을 받는 것이 좋다. |
****
| 멘토링 사진 |   |

#### 멘토링일지_260330 (5312178)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5312178
**최종 수정**: v7 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 사형 주조 기반 스마트 팩토리 시스템 | 팀명 | 2팀 |
****
****
| 멘토링 일자 |   | 멘토 | 노미승 |
****
****

- 

  - 

- 

  - 
****

- 

- 

- 
****

  - 
****

- 
****

  - 

    - 

    - 

  - 
****

    - 

    - 

      - 
****

- 

  - 

  - 
****

- 
****

  - 
****

  - 

- 
****

  - 
****

  - 
****

- 
****

  - 
****

- 
****

  - 
****

- 

  - 

  - 

    - 

      - 

      - 

## 

- 
****

  - 

  - 

  - 

- 
****

  - 
****

  - 

  - 

- 
****

  - 

## 

- 
****

  - 
****

  - 

  - 

## 

- 
****

  - 

- 
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
| 멘토링 내용 | <Sprint 발표 때 준비해야할 사항> 첫 페이지 과정 이름, 기수, 팀, 팀이름, 주제, 어떤 내용인지 진행 사항 공유 불안한 부분, 궁금한 부분들을 질문하면 좋음. <System Requirements 피드백> 반드시 비기능을 도출할 필요는 없다비기능 = 우리의 최소한의 구현 목표/성능(10초나 딜레이 되는건 안되니까)기능 정의가 모호함현재 표현이 두리뭉실 → 더 구체적이고 명확하게 작성 필요기능 단위 재설계 필요기능 덩어리가 너무 큼작게 쪼개서 관리 가능하게하위 기능이 많으면 추적이 어려움기능 = 구현해서 테스트할 단위너무 작아도/커도 안됨추적성(Traceability) 고려해야한다. SR ID 체계 필요 (UR–SR–Test 연결 구조) 추적 가능하게 설계해야함할일:비기능 설명이 적합하지 않은 곳 삭제 SR에서 기능들 관리 가능하게 다시 설계 (기능의 사이즈 기반)<Map 구조 피드백> 현재 맵이  단순함실제 시스템처럼 복잡도를 의도적으로 높일 필요같은 작업공간을 여러개병렬 처리/리소스 분배 고려 부족공정별 처리 시간 차이를 고려한 다중 작업자/설비 구조 필요병목 구간 해결을 위한 유연한 스케줄링 설계 필요AMR 경로 설계 개선 필요단일 경로 → 다중 경로 설계로 장애 대응 가능하게동적 자원 할당 개념 부족상황에 따라 AMR, 검사, 적재 등을 유연하게 재배치하는 구조 필요:할일 1. 각 공정 프로세스 단계에서 rough하게 걸리는 시간 측정2. 시간의 효율에 따라서 작업장 배치 필요 (병목현상) 작업 스케줄링예시)예를 들어, A 작업, B작업, C작업: 1, 2, 3 시간이 걸리면 c작업장이 2개 더 있으면 좋다.후처리는 여러 제품 (A, B, c) 을 동시에 같은 컨베이어 벨트3. 기술 구현 및 준비 상태 피드백하드웨어 이해 부족AMR(핑키 등)의 실제 주행 특성, 한계, 오류 상황에 대한 이해 필요로그 분석, 파라미터 튜닝 경험 필요ex.핑키가 코너를 잘 도는지 → nav2 파라미터 변경하드웨어 제약 대응 필요문제를 하드웨어 탓으로 두지 말고 소프트웨어로 보완 설계하드웨어 특성 → 제약 사항을 정확하게 파악해서 시나리오에 넣어야한다.소프트웨어가 해결하지 못하는 하드웨어의 특성을 알아내라기술 검증 부족실제 장비 테스트 및 성능 확인이 선행되어야 함요약: 장비 제대로 써보고 이해한 뒤 설계해라4. AI/딥러닝 관련 피드백AI 개발 착수 시점이 늦음딥러닝은 가장 오래 걸리는 요소 → 초기에 시작 필요딥러닝 → 학습데이터, 모델 선정에 오래 걸린다.돌려보고 성능 비교를 해보자장비 + 딥러닝 기술조사 해라!딥러닝 서칭해서 돌려보고 성능비교해보는것도 기술조사5. 전반적인 프로젝트 진행 피드백기술 조사 병행 필요구현 전에 충분한 조사 + 실습 필수다음 발표 개선 요구기술 조사 진행 상황 포함피드백 받고 싶은 부분에 대해서 중점적으로 발표발표자료 구성 신경써서 만들어라과정명/팀이름/타이틀..다른팀무엇을 하는 건지 명확하게 알 수 있도록(기타 등등 안됨)설계가 섞이지 않도록QR, 태그, 스티커 같이 도구 말고, 식별하는 기능이 있는 것으로 작성 → 기술 조사 때 결정되는 사항설계가 아닌 기능으로 작성시나리오의 적당히! 현실적인 논리성이 있어야 한다. → usability비기능은 테이블 따로 만들어서 관리해도 괜찮음기능/비기능 테이블 만들어서 관리하는 경우 많음BM 목표 : 핑키 튜닝해서 정밀하게 만들고 만들어서 팔수있을정도로 제작해라모든걸 구현할 필요는 없지만 제품성을 올리기 위해 설게만해도되니까 시나리오를 다양하게 작성해봐라 시나리오 설계까지만 해도됨 |
****
| 질문과 답변 |   |
****
| 멘토링 사진 |   |

#### 멘토링일지_260402 (11665784)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11665784
**최종 수정**: v5 (2026-04-19 sync)

# 2팀 피드백 

1. 
컨베이어 벨트 구성: 모터, 머리(보드), I/O가 있나요? 

1. 
HW랑 SW랑 두 장으로 따로 체크해야함. 

1. 
conveyor belt: 레이저랑 카메라가 붙어있는건지, 따로 있는건지 

1. 
머리(=보드)가 있는게 우리의 관심 대상임. 그 머리가 제어하는 센서가 뭔지 

  1. 
보통 속성은 동그라미 

  1. 
머리는 네모로 구분해서 그리자. 

1. 
USB 는 까보면 다른 통신을 할 때도 있어서 생략해도 괜찮다.

  1. 
직접 통신을 해야하면 써야함. 

  1. 
구현 대상이 아니고 꽂으면 되는 거면 생략 가능 

# 수업 

- 
오늘은 <그리는 법> → 다음주에는 실제 기능까지 검토 
SR을 먼저 했는데, 기구 설계/ 소프트웨어

## 전체적인 설명 

- 
표준은 존재하지 않습니다. 

- 
분야마다 설계해야하는 것이 다르기 때문입니다. 

- 
하지만, 가독성을 좋게 만들어야해서, 가독성에 대한 tip을 드리겠습니다. 

- 
Tips:

  - 
색깔은 회색 금지 (비활성 느낌) 

# HW

- 
장비가 껴서 표현해야하는게 많음.

- 
보통 장비를 보면 어떤 통신을 하는지 볼 수 있습니다. 

- 
화살표는 안에 박스 안으로까지 연결을 하면 됩니다. 방향도 같이 표현해준다. 

- 
HW: Arm, IoT system (if any), AMR, (합쳐진 제품이 있다면 제품을 더하면 됨) 

  - 
설계할 때, 하드코딩을 하지 않습니다. 

  - 
또한 현재 가지고 있는 장비의 개수가 아니라, xN으로 표현해줘야 합니다. 

  - 
또한 같은 팔이라도 안에 있는 소프트웨어가 다르고 용도가 다르면 따로 그려주는 게 맞다. 

    - 
용도가 다른 것의 예를 들면, 얹어주는애 빼는 애 등등 다름. 

  - 
하나의 HW component 안에 센서, 머리(보드) 등을 적어줌

    - 
AMR: 주행로봇 device (라즈베리파이x), 머리, 센서 

      - 
라즈베리 파이는 스펙이라 적어주는 것이 아닙니다.

      - 
모터 (2개로 fix 되어있음): 개수가 픽스되어있으면 x2 

      - 
lidar, camera: 읽기만 해서, 하나의 방향으로 적음. 

    - 
ARM: 6축 

      - 
LED : 방향 및 개수 

- 
서버: (HW PC로 생각함) 

  - 
이름은 용도에 맞게: 관제 server 라고 명명 

  - 
웹 서버 

  - 
딥러닝 서버 

- 
user device (mobile, PC,…), 

- 
관리자 PC 

- 
연결: 

  - 
근데 중앙 서버를 타지 않고 바로 연결하면 안됨. 

  - 
유지 보수 문제: UI가 바뀌면 주행로봇도 바뀌어야하는 문제 이런 거 있음 

  - 
보안 문제

  - 
리소스가 많이 듦  
<AI 서버> 

- 
Kubernetes

  - 
컨테이너로 만든 서비스를 자동으로 배포*운영해주는 시스템 

  - 
AI 서비스에서, 

    - 
모델 서버

    - 
데이터 처리 서비스

    - 
벡엔드 API

    - 
이런 것들을 전부 컨테이너로 만들고 KUBERNETES 가 관리해줘.

    - 
자동 확장(AUTO scaling), 롤링 배포 (서비스 안끊고 업데이트), 장애 복구, GPU 관리 

  - 
주행로봇에서 온 영상은 관제 서버에 줘야함.(중앙 관리 차원) 그냥 AI에 주면 안됨. 데이터 → 관제 → AI 센터

    - 
문제: 딜레이 (영상을 몇 개 통해서 보내야함) → 공유기를 따로 줘서 문제 안생길수도 있음. 

    - 
실제 구현시:

      - 
먼저 시도: → 일단 관제 → AI로 보냄. 

      - 
이후 개발 환경의 문제가 있으면 AI 서버로 보낼 수 있음 (위에거 먼저 시도, 네트워크 문제 있으면 이걸로 시도)  

# SW 

- 
구조 

  - 
Lower level: software에서는 embedded 에 가까운 사람이 low level 

  - 
Server:

  - 
High level:  user 쪽에 가까울 수록 (web, app) 

- 
interface는 SW Component의 이름으로 사용하지 않습니다. 다른 의미로 사용되곤 하기 때문입니다.

  - 
보통 두 시스템 간의 상호작용 방식 전체를 정의한 것이다. 단순히 연결된 부분이 아니라, 

  - 
두 시스템 간 상호작용을 정의한 명세(계약)을 나타낸다.  

- 
작명 

  - 
application: 사용자 목적을 직접 수행하는 소프트웨어 

    - 
사용자가 직접 쓰느는 것

    - 
서버에도 백엔드 API서버, AI Inference 서버 등등 service-side application존재

  - 
service: 백그라운드에서 지속적으로 기능 제공

    - 
OS가 관리. 서버쪽에서 도는 서비스 프로그램 

    - 
OS에 등록된 경우도 있고, 그냥 서버 프로세스일 수도 있다. (보통 백그라운드) 

  - 
Controller: 장비 안에 보드에서 도는 반쯤 Embedded는 controller 

- 
통신 종류 

  - 
DDS (Data Distribution Service)

    - 
: broadcasting, 누군지 모르겠지만 다 받아. 

    - 
**publish / subscribe 구조**

    - 
👉 “누가 받을지 몰라도 그냥 뿌림 (broadcast 느낌)”

    - 
subscriber가 알아서 받음

    - 
loose coupling: 송신자는 수신자를 몰라도 됨. 

    - 
handshake 없음(추상화됨)

  - 
TCP / UDP 

    - 
handshake 있음 

    - 
UDP: 속도 최우선, 신뢰성 없음

      - 
사용 예

        - 
영상 스트리밍

        - 
센서 데이터 (일부 유실 허용 가능)

      - 
포인트:

        - 
순서 꼬일 수 있음 → **sequence number 필요**

        - 
일부 프레임 날아가도 OK

    - 
TCP: 신뢰성 최우선, 대신 느림 

      - 
데이터는 무조건 TCP를 사용한다. 

      - 
사용예시 

        - 
명령(START/STOP)

        - 
금융데이터

        - 
상태 제어 

  - 
User 연결에서 ROS를 안 쓰는 이유

    - 
문제:

      - 
ROS는 전용 미들웨어

      - 
사용자 쪽에도 ROS 필요
👉 현실적으로 불가능

    - 
그래서,

      - 
TCP

      - 
HTTP (REST API)

      - 
WebSocket

    - 
이유: **사용자는 그냥 앱/브라우저만 쓰게 해야 함**

#### 멘토링일지_260406_전체정리 (15207997)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15207997
**최종 수정**: v6 (2026-04-19 sync)

# 전체 

- 
sprint 발표를 굳이 팀장이 하지 않아도 된다. → 앞으로 맡은 부분 담당자가 발표하기 

- 
SA 

  - 
박스 사이즈 == 중요도 

  - 
DB는 한 군데에서 관리하는 것이 좋음. 

  - 
web과 app server 은 보통 나뉘는 것 같음. 

  - 
TCP 이상, 제어 **qt **로 많이 사용해야 한다. → qt? 

    - 
web-was -db 연동 하지 말라고 함. 무슨 말이지? 힘을 많이 주지 말라고 

    - 
디버깅용 제품을 간단하게라도 만들어서 할 수 이쓴 사람이 취업에 유리 (경력)

    - 
http만 넣지 말고 TCP 많이 쓰자 

  - 
DB 등 main service는 그 프로젝트의 이름을 넣어준다. (Control service) 

  - 
HW에서도 이름을 잘 붙어줘야 하는 것 같음 (1팀 발표때 피드백 → 1팀 팀장에게 물어보기) 

- 
기술 조사 

  - 
개선했다. → 발표를 할 때는 특히나 수치로! 

- 
발표때

  - 
일정에 대한 것도 넣어주자 

# 3팀 ------

- 
Jira 로 세팅해놓은 것 같다. 일단 가서 어떻게 만들었는지 물어보기! 

## 1. 하드웨어 및 시스템 아키텍처

- 
**카메라 연결 방식:** 서버실 서버에 카메라를 직접 연결하는 것은 불가능하므로, **통신용 보드(Edge Device)**를 추가하여 설계를 보완할 것.

- 
**주행 보정 시스템:** * 외부 주행 시 위치 보정용 **탑뷰(Top-view) 카메라** 도입은 찬성 (데모 촬영용으로 우수).

  - 
단, 실내 주행 시 탑뷰 사용이 불가하므로 **대체 기술(예: SLAM, LiDAR, IMU 등)**을 반드시 조사할 것.

- 
카메라는 **통신 보드 + 무선 전송 구조**로 설계 필요

- 
**아키텍처 시각화:** 다이어그램 작성 시 박스 크기를 통해 **구성 요소의 중요도**를 직관적으로 표현할 것.

## 2. 데이터베이스(DB) 및 소프트웨어 전략

- 
**DB 설계 원칙:** * 불필요한 분리는 리소스 낭비이므로 지양할 것.

  - 
웹/앱 서비스의 관리 데이터가 동일하다면 **통합 관리**를 우선 고려하되, 확장성이 꼭 필요한 경우에만 분리할 것.

- 
**제어 및 GUI 개발:**

  - 
장비 제어 시 HTTP보다는 **TCP 이하 계층의 통신(바이너리 데이터 송수신)** 비중을 높일 것.

  - 
라이브러리 사용은 직접 구현 경험으로 보기 어려움

  - 
개발 효율과 성능을 고려하여 웹 대신 **Qt(큐티)** 사용을 적극 추천 (ROS와의 호환성 및 디버깅 용이성).

- 
**네이밍 규칙:** '핑키', '제코봇' 같은 애칭 대신 **용도 기반의 전문적인 명칭**을 사용할 것.

- 
YOLO 실행 : 로봇(온보드)에서  YOLO 실행 시 부하가 커 보임

## 3. 기술 검토 및 보고 체계

- 
**데이터 기반 의사결정:** 딥러닝 모델 선정 등 기술 조사 시 반드시 **수치(Benchmark, 정확도, 처리 속도 등)**를 근거로 제시할 것.

- 
**업무 보고:** 주간 보고서는 정성적인 설명보다 **정량적인 수치** 중심으로 작성할 것.

- 
**하드웨어 한계 극복:** 핑키봇의 스펙 한계를 인정하고, 타사 사례 벤치마킹 및 **좁은 통로 주행** 등 환경적 제약 극복을 위한 연습/파라미터 튜닝에 집중할 것.

## 4. 프로젝트 관리 및 배포 (SA/SR)

- 
**스프린트 회고:** '잘한 점/못한 점' 나열에 그치지 말고, 아쉬운 점에 대한 **구체적인 개선 방안**을 도출할 것.

- 
**문서화(SR):** 요구사항 정의 시 'A 및 B 기능'처럼 모호하게 묶지 말고, 하나의 명확한 서비스 명칭으로 정의할 것.

- 
**환경 분리:** 개발 환경과 실제 판매/구동될 **배포 환경(Production)**의 차이를 인지하고, 실제 배포 환경을 미리 구성해 볼 것.

- 
**진척도 관리:** 일정 계획에 스프린트 회고와 상세 진척도를 반드시 포함할 것.

## 

# 1팀 

## 1. 시스템 아키텍처 및 하드웨어 설계
가장 핵심적인 변화는 **'클라이언트의 경량화'**와 **'명확한 역할 분리'**입니다.

- 
**모니터링 UI (Qt)의 독립성:** * 클라이언트 PC에는 **ROS를 설치하지 않습니다.**

  - 
Qt는 오직 UI/UX와 모니터링에만 집중하며, 내부에서 ROS 노드를 생성하지 않는 **'순수 UI'** 역할을 수행합니다.

- 
**하드웨어 및 서버 구성:** * 카메라를 메인 서버에 직접 연결하는 구조를 지양하고, **별도 디바이스(통신 보드 등)로 분리**하여 설계합니다.

  - 
다이어그램 작성 시 PC, 모니터, 소프트웨어 컴포넌트 간의 구분을 명확히 해야 합니다.

- 
**다이어그램 표현 규정:** * 구성 요소의 중요도에 따라 박스 사이즈를 조절합니다.

  - 
통신선은 소프트웨어 컴포넌트까지 정확히 연결되어야 하며, 선이 겹치거나 합쳐져 가독성을 해치지 않도록 주의합니다.

## 2. 통신 및 데이터 관리 (Data Flow)
효율적인 데이터 처리를 위해 저수준 통신을 지향하고 계층 구조를 바로잡습니다.

- 
**통신 최적화:** * HTTP보다 로우 레벨인 **TCP 바이너리 통신**을 직접 구현하여 장비 제어 효율을 높이고 의존성을 낮춥니다.

- 
**데이터 흐름의 정석:** * 웹 서비스가 DB에 직접 접근하는 구조는 지양합니다.

  - 
**[웹 → 컨트롤 서비스(ROS) → DB]** 순서로 데이터가 흘러야 하며, 같은 서버 내에 있더라도 컴포넌트는 반드시 분리하여 표현합니다.

- 
**명확한 네이밍:** * 단순 'DB'가 아닌 프로젝트 성격에 맞는 이름을 부여하고, 메인 서비스와 컨트롤 서비스의 역할을 이름에서부터 구분합니다.

## 3. 프로젝트 관리 및 UI/UX 전략
운영 효율성과 배포 환경을 고려한 실무적인 지침입니다.

- 
**기능 및 제품 네이밍:** * '핑키'와 같은 제품명 대신 **용도 기반의 전문적 명칭**으로 통일합니다.

  - 
기능 정의 시 'A 및 B' 식으로 묶지 말고, 단일 기능 단위로 명확히 정의합니다.

- 
**웹 개발 리소스 조절:** * 웹 서비스 개발에 너무 많은 힘을 쏟기보다, 빠르게 구현 가능한 수준으로 개발하고 핵심 제어 로직에 집중합니다.

- 
**입력 방식 최적화:** * 로봇 자체에서 음성을 처리하는 비효율적인 구조 대신, 이미 존재하는 **앱이나 키오스크**를 활용하여 입력을 처리합니다.

## 4. 기술 검토 및 고도화 (R&D)
모든 기술적 선택에는 정량적인 근거가 뒷받침되어야 합니다.

- 
**데이터 기반 의사결정:** * YOLO, CNN 등 모델 선정 시 수치 기반의 비교 자료를 반드시 포함합니다.

  - 
거리 측정 등의 센싱 기능은 반드시 **캘리브레이션(Calibration)** 과정을 거쳐 수치를 검증합니다.

- 
**시나리오 기반 테스트:** * LLM(거대언어모델) 기능 테스트 시 단순 호출이 아닌, 실제 사용 환경을 고려한 **현실적인 시나리오와 다양한 요청 케이스**를 확보합니다.

- 
**회고와 개선:** * 스프린트 회고 시 아쉬운 점에 대한 구체적인 **개선 사항**을 도출하고 진척도를 관리합니다.

### [시스템 아키텍처 요약 표]

****
****
****
| 구분 | 역할 | 환경 및 통신 |
|---|---|---|
****
****
| 로봇 (Server) | 장비 제어, 데이터 생성 | ROS 실행, TCP 서버 |
****
****
| 모니터링 PC (Qt) | 상태 시각화, 제어 명령 | ROS 미설치, TCP 클라이언트 |
****
****
| 웹/앱 서비스 | 사용자 UI, 데이터 조회 | 컨트롤 서비스 경유, DB 관리 |

# 2팀 피드백

## 1. SR(기능 정의) 관련

- 
SR은 **아직 설계가 아닌 “해야 할 기능 정의 단계”**인데
→ 현재는 이미 **시스템/구조 설계가 들어간 상태 **

- 
기능 정의도 덜 된 상태에서 구조화까지 해버린 게 문제

- 
기능을 **파트/시스템 단위로 나누는 건 위험**

  - 
기능 간 **교집합 발생 가능**

  - 
어느 곳에도 속하지 않는 기능 생길 수 있음

- 
결론:
**성급한 그룹핑 금지 / 기능 중심으로 다시 정리 필요**

## 2. HW / SW 아키텍처 설계 문제

- 
**HW와 SW를 섞지 말 것 (강조됨)**

- 
“클라우드 서버” 표현 문제

  - 
실제는 DB 서버 → **명확하게 “DB 서버 (클라우드 상)”로 표현 필요 혹은 구름 모양**

- 
**화살표/데이터 흐름 누락**

  - 
예: ARM controller → control server 방향 없음

- 
점선 사용 문제

  - 
점선 = 비동기 의미인데 **불필요하게 사용됨 **👉 그냥 실선 사용 권장

## 3. 컨트롤 서버 구조 문제 (중요)

- 
현재 구조:

  - 
컴포넌트가 쪼개져 있음 (task 생성 / 전달 등)

- 
문제점:

  - 
**불필요한 단계 증가 (거쳐 거쳐 가는 구조)**

  - 
**리소스 비효율**

- 
DB:

  - 
**관제 시스템에서 매우 중요한 요소 → 반드시 코어가 직접 관리**

  - 
인터페이스: 

    - 
교체 가능해야 하므로 분리 필요
👉 정리:

- 
❌ 기능 쪼개기 중심 구조

- 
코어 중심 + 인터페이스 분리 구조

## 4. UI / 발표 자료 관련

- 
웹페이지 기반 발표 → **가독성 떨어짐**

- 
컨플  PPT 자동 변환 도구 사용 권장

- 
발표는:

  - 
**보기 좋게 + 전달력 중심으로 구성 필요**

## 5. Technical Research (기술 조사) 문제

- 
현재 상태:

  - 
“조사”가 아니라 **할 일 리스트 느낌**

- 
문제:

  - 
이미 아는 내용까지 포함됨

  - 
목적 불명확

- 
👉 개선 방향:

  - 
**“모르는 것 검증” 중심으로 정리**

  - 
실험/검증 결과 중심으로 정리

## 6. 진행 내용 발표 방식 문제

- 
스프린트 회의 내용 공유 부족

  - 
무엇을 했고 / 잘됐고 / 문제 무엇인지 부족

- 
발표는:

  - 
**주간 업무 보고처럼 해야 함**

    - 
진행도 (무엇이 남았고 무엇을 할거다)

    - 
문제점

    - 
다음 계획

#### 멘토링일지_20260406 (26247891)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26247891
**최종 수정**: v1 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 사형 주조 기반 스마트 팩토리 시스템 | 팀명 | 에러 맛집 |
****
****
| 멘토링 일자 |   | 멘토 | 노미승 |
****

## 

- 

****

- 

- 
****

  - 
****

  - 

- 

****

## 

- 
****

- 

  - 
****

- 
****

  - 

- 

  - 
****

## 

- 

  - 

- 

  - 
****

  - 
****

- 

  - 
****

  - 

    - 

- 

- 

## 

- 
****

- 

- 

  - 
****

## 

- 

  - 
****

- 

  - 

  - 

- 

  - 
****

  - 

## 

- 

  - 

- 

  - 
****

    - 

    - 

    - 
| 멘토링 내용 | 1. SR(기능 정의) 관련SR은 **아직 설계가 아닌 “해야 할 기능 정의 단계”**인데→ 현재는 이미 시스템/구조 설계가 들어간 상태 기능 정의도 덜 된 상태에서 구조화까지 해버린 게 문제기능을 파트/시스템 단위로 나누는 건 위험기능 간 교집합 발생 가능어느 곳에도 속하지 않는 기능 생길 수 있음결론:성급한 그룹핑 금지 / 기능 중심으로 다시 정리 필요2. HW / SW 아키텍처 설계 문제HW와 SW를 섞지 말 것 (강조됨)“클라우드 서버” 표현 문제실제는 DB 서버 → 명확하게 “DB 서버 (클라우드 상)”로 표현 필요 혹은 구름 모양화살표/데이터 흐름 누락예: ARM controller → control server 방향 없음점선 사용 문제점선 = 비동기 의미인데 불필요하게 사용됨 👉 그냥 실선 사용 권장3. 컨트롤 서버 구조 문제 (중요)현재 구조:컴포넌트가 쪼개져 있음 (task 생성 / 전달 등)문제점:불필요한 단계 증가 (거쳐 거쳐 가는 구조)리소스 비효율DB:관제 시스템에서 매우 중요한 요소 → 반드시 코어가 직접 관리인터페이스: 교체 가능해야 하므로 분리 필요👉 정리:❌ 기능 쪼개기 중심 구조코어 중심 + 인터페이스 분리 구조4. UI / 발표 자료 관련웹페이지 기반 발표 → 가독성 떨어짐컨플  PPT 자동 변환 도구 사용 권장발표는:보기 좋게 + 전달력 중심으로 구성 필요5. Technical Research (기술 조사) 문제현재 상태:“조사”가 아니라 할 일 리스트 느낌문제:이미 아는 내용까지 포함됨목적 불명확👉 개선 방향:“모르는 것 검증” 중심으로 정리실험/검증 결과 중심으로 정리6. 진행 내용 발표 방식 문제스프린트 회의 내용 공유 부족무엇을 했고 / 잘됐고 / 문제 무엇인지 부족발표는:주간 업무 보고처럼 해야 함진행도 (무엇이 남았고 무엇을 할거다)문제점다음 계획 |
****
| 질문과 답변 |   |
****
| 멘토링 사진 |   |

#### 멘토링일지_20260408 (20676673)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20676673
**최종 수정**: v3 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 사형 주조 기반 스마트 팩토리 시스템 | 팀명 | 에러 맛집 |
****
****
| 멘토링 일자 |   | 멘토 | 노미승 |
****

## 

### 
****

- 
****

- 
****

- 
****

1. 
****

1. 
****

  - 
````

  - 

1. 
********

### 
****

### 

- 
********

  - 

  - 

- 
********

  - 

  - 

  - 

### 

- 
****``````

- 
********

### 

- 

### 
| 멘토링 내용 | 프로젝트 형상관리 및 아키텍처 설계 가이드1. 운영 및 관리 원칙 (R&R)본 프로젝트는 오픈소스가 아닌 실제 개발 및 배포를 목적으로 하며, 각 도구의 역할을 엄격히 분리합니다.Confluence: 상세 설계(시나리오, State), 회의록, 결과 보고서 관리.(문서버전관리)Jira: 작업(Task) 단위 관리 및 일정 트래킹.GitHub: 배포, 유지보수, 릴리즈 단위를 기준으로 소스 코드 관리.(코드 버전 관리)==깃허브에는 코드만 올려라(형상관리에 해당되는거)포함 대상: 소스 코드, SQL 스키마(.sql), 도커 실행 파일(Dockerfile, docker-compose 등), 테스트 자동화 코드.제외 대상: * 학습 데이터 및 대용량 이미지 (형상관리 대상 아님).build, out 등 컴파일 결과물 (개인 배포용 레포에서만 허용).테스트 결과 리포트 (컨플루언스로 이동).DB 관리: 데이터 자체를 넣는 것이 아니라, 스키마(Schema) 중심의 변경 이력만 관리.2. 소프트웨어 컴포넌트 기반 Repo 구조 (SA 반영)가독성과 유지보수 효율을 위해 SA(Software Architecture) 기반의 공통 특성으로 그룹화하여 구조를 설계합니다.SA 기준 컴포넌트로 만 구성컴포넌트 -하위 폴더(프로세스)3. 전략적 README 작성 가이드인사팀과 실무 면접관의 시선을 고려하여 정보를 계층적으로 배치합니다.Main README (최상위): "프로젝트의 얼굴"인사팀/검토자가 1분 내로 파악할 수 있도록 핵심 요약, 아키텍처 다큐먼트, 핵심 성과 위주로 작성.이력서 검토 시 가장 비중 있게 보는 구간이므로 시각적 요소(다이아그램 등) 활용 권장.Component README (하위 폴더): "기술적 깊이"각 컴포넌트의 상세 구현 방식, 의존성, 실행 방법 기술.실무 면접 단계에서 깊이 있는 질문을 유도하는 용도로 활용.하지만 굳이 권장은 안함4. . ROS 2 특화 가이드워크스페이스 관리: 전체 프로젝트 자체가 워크스페이스가 되어야 하며, 불필요한 build, install, log 폴더는 제외합니다.패키지 디자인: 단순 나열이 아닌 기능별 패키지 디자인이 선행되어야 합니다.5.상세 설계시나리오와 상태(State) 설계의 타당성을 중점적으로 검토할 예정입니다.= 폴더구조 된거 먼저 보내고 피드백 받고 진행 (오늘중에라도) |
****
| 질문과 답변 |   |
****
| 멘토링 사진 |   |

#### 멘토링일지_20260409 (21725654)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/21725654
**최종 수정**: v4 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 사형 주조 기반 스마트 팩토리 시스템 | 팀명 | 에러 맛집 |
****
****
| 멘토링 일자 |   | 멘토 | 노미승 |
****
| 멘토링 내용 |   |
****

# 

## 

### 

### 

****
****

## 

- 

- 

- 

- 
****

## 

- 

- 

- 
****

## 

****

- 
****

- 
****

- 

- 

- 

## 

- 

- 

****

## 
****

### 

- 

- 

- 
****

### 

- 

- 

- 

- 
****

- 
****

### 
****

- 

- 

- 

## 

### 

- 

### 

- 

### 

#### 

- 

- 

- 

- 

#### 

- 

- 

- 

## 
****

- 

- 

- 

- 

# 

- 

- 

- 
****

- 

- 

  - 

  - 

- 
****
| 질문과 답변 | 시스템 설계 과정 및 UML 기반 설계1. 시스템 설계의 전체 흐름시스템 개발은 다음과 같은 단계로 진행된다.SR (System Requirement)시스템이 수행해야 할 기능을 정의하는 단계이다.SA (System Architecture)시스템의 전체 구조를 설계하는 단계로,하드웨어와 소프트웨어 구성, 그리고 구성 요소 간의 관계를 정의한다.→ 그러나 SA는 어디까지나 구성(Structure) 만 정의한 것이며,시스템이 실제로 어떻게 동작하는지는 설명하지 못한다는 한계가 있다.2. SA 이후 필요한 상세 설계 요소시스템을 “제대로 설명”하기 위해서는 다음 요소들이 반드시 추가로 설계되어야 한다.시나리오 (동작 흐름)데이터 구조 정의GUI 화면 구성소프트웨어 컴포넌트 간 통신 방식이 단계는 단순한 설계라기보다 이 시스템을 구현할 수 있을 정도의 명세(specification)를 만드는 과정이다.  또한 강의에서는 이 부분을 사실 설계라기보다 명세를 뽑는 단계라고 강조한다.3. 좋은 설계의 기준좋은 설계의 기준은 명확하다.새로운 팀원이 투입되었을 때추가 설명 없이설계 문서만 보고 바로 개발을 시작할 수 있어야 한다즉,  설계 = 시스템을 완전히 이해할 수 있는 수준의 설명4. UML 기반 설계 방법UML에는 다양한 기법이 존재하지만,모든 것을 다 사용할 필요는 없다.중요한 것은 시스템을 가장 명확하게 표현할 수 있는 최소한의 UML을 선택하는 것이다.대표 UML:시퀀스 다이어그램스테이트 다이어그램클래스 다이어그램유스케이스 다이어그램액티비티 다이어그램5. 핵심 UML 1: 시퀀스 다이어그램시퀀스 다이어그램은 시스템 시나리오를 표현하는 데 가장 적합하다.컴포넌트 간 메시지 흐름을 시간 순서대로 표현이벤트 기반 상호작용 구조를 보여줌핵심 개념: “이벤트가 발생했을 때 → 누가 → 무엇을 → 어떤 순서로 수행하는가”6. 핵심 UML 2: 스테이트 머신 (FSM)로봇 및 장비는 대부분 상태(State) 기반으로 동작한다.또한 실제 구현도 FSM 기반으로 많이 이루어진다.(1) FSM (Finite State Machine)정해진 상태 집합 내에서 동작상태 간 전이를 통해 시스템이 운영됨현재 산업에서는 대부분 미리 정의된 상태 기반 구조를 사용(2) 상태(State)의 기본 구조시작 상태 (Start)종료 상태 (End)중간 상태들특징:상태 간 이동은 반드시 이벤트(Event) 에 의해 발생모든 전이(화살표)는 반드시 이름(이벤트명) 을 가져야 함→ “이름 없는 전이는 잘못된 설계”(3) 상태의 의미상태는 단순 대기가 아니라  “특정 작업을 수행하는 구간”예:초기화 상태대기 상태작업 수행 상태7. 로봇 시스템의 초기화 동작 로봇은 전원을 켠다고 바로 동작하지 않는다.반드시 초기화 과정을 거친다.(1) 논리적 초기화프로그램 및 내부 설정 초기화(2) 물리적 초기화실제 장비의 위치 및 자세를 정렬(3) 초기화가 필요한 이유① 현재 위치를 알 수 없는 경우Absolute Encoder가 없는 경우전원을 켤 때마다 위치 정보가 사라짐→ 해결:기구의 끝(리밋)까지 이동기준 위치(0점)를 재설정(강의 핵심: “끝까지 갔다가 돌아오면서 기준 잡는다”)② 캘리브레이션 필요장시간 사용 시 오차 발생위치 및 동작 정확도 저하→ 해결:초기화 과정에서 보정 수행8. 상태 설계의 핵심 포인트상태는 고정된 것이 아니라, 시스템의 목적과 시나리오에 따라 정의된다.즉,같은 로봇(하드웨어)이라도용도(제품 목적)가 다르면 상태 구조도 완전히 달라진다예:A 제품용 상태 구조B 제품용 상태 구조→ 각각 별도로 설계해야 함*최종 핵심 정리*SA는 구조만 정의하며, 동작은 설명하지 못한다반드시 시나리오, 데이터, GUI, 통신까지 설계해야 한다이 단계는 설계가 아니라 명세 수준까지 구체화하는 과정이다UML은 필요한 것만 선택적으로 사용한다핵심 도구:시퀀스 다이어그램 → 동작 흐름스테이트 머신 → 상태 기반 동작좋은 설계란  누가 봐도 바로 개발할 수 있는 수준의 설계이다 |
****
| 멘토링 사진 |   |

#### 멘토링일지_20260413 (26248494)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26248494
**최종 수정**: v3 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 사형 주조 기반 스마트 팩토리 시스템 | 팀명 | 에러 맛집 |
****
****
| 멘토링 일자 |   | 멘토 | 민형기 강사 |
****

### ****

- 
********

- 
****

  - 
****

  - 
****

- 
****

  - 

  - 

### ****

- 
****

- 
****

- 
****

### ****

- 
********

- 
****``

- 
************
| 멘토링 내용 | 2팀: 용어의 정의와 통신 아키텍처 최적화엔드 투엔드(End-to-End) 정의: 실제 용어의 정확한 의미를 알고 있고 이번 프로젝트에서 이것을 ~의미로 차용해서 적용했다라고 언급 필요 통신 이중화 (ROS 2 & MQTT):로봇 내부/간: ROS 2를 활용하여 제어 효율성 확보.로봇 외부: MQTT를 활용하여 통신 효율성 극대화.중간 산출물 발표 전략: v-model에서의 중간 산출물 → 스프린트 중간 진행 상황 보고 발표 시: 산출물을 만들었다 식으로 발표 최종 발표 시에는 팀에서 어떤 부분을 이를 팀에서 특별히 신경썼는지 등 부분을 해당 부분만 캡쳐 및 설명 등 → 어떻게 시각적으로 '예쁘게' 표현할지(UI/UX, 시각화 자료) 고민할 것.1팀: 관제의 정의와 기술적 실체관제 범위 명확화: 관제 시스템의 핵심 3대 태스크(디바이스 태스크 할당, 경로 중첩 시 교통 정리, 대시보드 시각화)를 명확히 정의할 것.직접 구현 원칙: 유저층이 적은 외부 프레임워크(OpenRMF 등)에 의존하기보다 핵심 기능을 직접 구현하여 기술적 이해도를 증명할 것.기술 조사 보완: 구현 가능성 체크 미스를 방지하기 위해, 단순 조사를 넘어 실제 적용 가능한 범위를 다시 한번 점검할 것.3팀: 수치적 증명과 레이어별 상태 관리데이터 기반 리포트: 파라미터 튜닝 전후의 이동성 변화 등을 수치화하여 객관적인 리포트로 제시할 것. (예: 좁은 통로 통과 시간 단축 등)문제 해결 프로세스: 문제 정의 → 해결 방안 → 결과 수치화의 흐름을 지킬 것.상태 관리 계층화: 'State'를 독립적이고 유일한 상태로 정의하고, 로봇 단위 Layer와 관리 매니저 단위 Layer의 행동을 명확히 구분하여 설계할 것. |
****
| 질문과 답변 |   |
****
| 멘토링 사진 |   |

#### Sprint_20260000 (13370049)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13370049
**최종 수정**: v3 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | SmartCast Robotics - 다품종 소량 생산 사형 주조 공정 스마트 팩토리 시스템 구축 | 팀명 | 에러맛집 |
****
****
| 스프린트명 |   | 수행기간 | date1 ~ date2 |
****
| 스프린트 내용 |   |
****
| 차주 스프린트 |   |
****

### 

### 

### 

### 
| 회고 | 잘 된 점아쉬운 점개선 아이디어자유 코멘트 |

#### Sprint (4980900)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/4980900
**최종 수정**: v5 (2026-04-21 sync)

#### sprint4_meeting (36307613)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/36307613
**최종 수정**: v9 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | SmartCast Robotics - 다품종 소량 생산 사형 주조 공정 스마트 팩토리 시스템 구축 | 팀명 | 에러맛집 |
****
****
| 스프린트명 | Sprint4 | 수행기간 | ~ |
****
| 스프린트 내용 | 이번 주 검토 |
****
| 차주 스프린트 |   |
****

### 

- 

- 

- 

  - 

- 

- 

- 

- 

### 

- 

- 

- 

- 

- 

- 

- 

### 

### 

- 
****

  - 

  - 

- 

- 

- 

- 

- 

  - 
| 회고 | 잘 된 점Docking Server 테스트 잘 됨Jira 세팅 완료​YOLO의 Classification, Detection 결과물이 어느 정도 도출됨.문서작성의 기회가 균등하게 제공되어 포트폴리오 작성에 도움될 예정기획, 설계상 미흡했던 부분들이 채워지고 있다.진도가 빠름. 연동이 거의 완료됨적재 하드코딩이 잘 되었습니다.야근을 열심히 함(팀 1위)아쉬운 점Jira 사용이 미흡함-필터링 추가 필요함 → 수동으로 subtask 보게할 수 있다. ​프로젝트 중간에 변경되어 폐기되는 아이템에 대해서는 해당 담당자의 시간낭비 최소화가 추천됨. → 포트폴리오에는 사용할 수 있음. 그리고 최대한 계획을 자세히 세우겠지만, 계획만 세우다가는 완료 어림도 없음. Docking server를 너무 오래함 → 돼서 다행모델 언제 시작함….VLA 만져보고 싶어요….제발… → 문서 작업 빨리 한 후 시작합니다. 전원이 알아야할  상황들에 대해서 전체 보고가 안돼서, 사람마다 시나리오에 대한 이해나 결정된 사항에 대해 update 가 안돼서 아쉬움. → 동료끼리 일하고 결정된 모든 사안 (하루 마무리할때 보고) → 그 다음날 standup 회의에서 팀장이 전체 보고 ​병가가 많았음(아파도 학원에서) 기수님 state 다이어그램 쓰느라 힘드셨는데 필요없는 부분이었음…ㅠㅠ → 죄송….근데 학원에서 뭐할지 강의가 많이 부족함. 개선 아이디어자유 코멘트​당연히 로봇팔이나 선반의 위치를 임의로 바꿔도 자신있음 💪확인했습니다. 감사합니다!또 할수있다는 자신감 멋있습니다!다음주에는 건강관리를 철저히 합시다.​용석 시험 합격 기원x3맵 꾸미기 재밌겠다데모 맵 jetcobot 2대 AMR 3대로 진행 했으면 좋겠습니다.규정이의 arm 을 사용하면 좋겠다…… 통신 필요함 → 다음주에 얘기 (규정 필요한 부분 정리 다음 standup) |

#### sprint1_meeting (5308638)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5308638
**최종 수정**: v3 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | 주조공정 자동화 | 팀명 | 에러맛집 |
****
****
| 스프린트명 | 2026년 3월 27일 | 수행기간 |   |
****
| 스프린트 내용 | 기획 |
****
| 차주 스프린트 | 프로젝트 설계, 기술조사 |
****

### 

### 

1. 

1. 

### 

1. 

1. 

### 
| 회고 | 잘 된 점갈등 없이 성격이 너무 잘 맞는다.의견 공유를 통해 보완해나간다.아쉬운 점confluence 문서화가 체계화가 되지 않는다.업무 분담이 효율적이지 않다(같은 내용에 대해서 따로 작업하는 경우)개선 아이디어confluence 문서를 parent - child로 체계적으로 관리업무 분담을 팀 단위로 나눠서 의논하기자유 코멘트 |

#### sprint1_presentation (6979624)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6979624
**최종 수정**: v20 (2026-04-19 sync)

**<주제>**
사형 주조 자동화 공정 
(사형 주조: 모래로 만든 틀에 용융 금속을 부어 제품을 만드는 공정)
**<사형 주조 공장 자동화 필요성>**

- 
**사형 주조**는 반복적이고 표준화된 공정 →  자동화에 적합

- 
고온 작업 및 중량물 취급으로 **안전 이슈** 존재 → 자동화 필요
→ **End-to-End 자동화 시스템 설계에 적합한 사례**
<**제품: 맨홀 뚜껑>**

- 
데모 환경에서 실제 공정과 유사하게 구현 가능하며, **구조는 단순하지만 다양한 디자인**을 포함하고 있음

- 
맨홀 뚜껑은 **규격화된 대표 주조 제품**으로 시스템 설계에 적합
**<시나리오>**
“발주부터 출고까지 하나의 End-to-End 자동화 사이클을 설계했습니다.”

1. 
발주: 원격 발주 → 관리자 발주 승인 → 관리자 생산 시작 알림 → 공정 시작 

1. 
전체 공정: 원재료 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형 → 후처리 → 검사 → 적재 → 출고

  1. 
Casting Zone: 원재료 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형

  1. 
Inspection Zone: 후처리 → 검사

  1. 
Storage Zone: 적재 

  1. 
Shipping Zone: 출고 
**<Map>**

- 
개선할 점  

  - 
현재 주조 공정 프로세스만 보면, 로봇팔을 많이 사용하고 AMR이 사용되는 부분은 많이 없어보인다. 

    1. 
하나의 구역을 여러 곳으로 나누기: 하나의 구역 (예) 주조 구역) 을 여러 곳으로 나누어서 AMR이 이동시키는 과정을 추가 가능 

    1. 
A → B 지점으로 이동 시 이동 경로가 여러개가 되도록 설계: 현재 가는 길에 놓인 장애물 (다른 AMR)이 있는 경우, 여러 경로를 자율적으로 선택할 수 있는 걸 보여주도록 설계 가능 
**<System Requirements> **
 
전체 시스템을 기능 단위로 분석하여 **총 9개의 큰 기능으로 구조화**하였으며, 각 기능은 세부 하위 기능으로 나누어 System Requirements를 정의했습니다.
예시)
**<Key features>** 
“단순 자동화” → “스마트 시스템”

1. 
**통합 관제 시스템 **

- 
전체 공정을 한 곳에서 통합 관리 

- 
공정, 이송, 적재 상태를 통합적으로 모니터링

- 
공정 상태 기반 제어 및 이상 감지 가능

1. 
**자동화 주조 공정 시스템 **

- 
주조 공정 전체를 자동으로 수행 

- 
원재료 → 용융 → 주형 → 주탕 → 냉각 → 탈형 자동화

- 
상태 기반으로 공정이 자동으로 흐름

1. 
**물류 통합 관리 시스템 (적재/이송/출고)**

- 
공정 이후 물류까지 통합 관리 

- 
이송, 적재, 재배치, 출고까지 연계

- 
위치 관리 및 재고 관리 통합
**<UI 예시> **

- 
사용한 framework: **Next.js, React **

- 
[**관제 페이지**](http://192.168.0.16:3000/)**: **
→ 로봇 위치 / 공정 상태 / 적재 상태

- 
[**고객 발주 페이지**](http://192.168.0.16:3000/customer)**:**
→ 제품 선택 / 옵션 설정 / 주문
모니터링
고객 주문용

#### sprint2_meeting (13337285)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/13337285
**최종 수정**: v8 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | SmartCast Robotics - 다품종 소량 생산 사형 주조 공정 스마트 팩토리 시스템 구축 | 팀명 | 에러맛집 |
****
****
| 스프린트명 | Sprint2 | 수행기간 |   |
****
| 스프린트 내용 | 이번 주 검토 |
****
| 차주 스프린트 | 기술조사 마무리 & 구현 1차 |
****

### 

- 

- 

- 

- 

- 

- 

### 

- 

- 

- 

- 

### 

- 

- 

### 

- 
| 회고 | 잘 된 점파트 별 인원 분배가 잘 되어서 빠르게 기술 조사를 수행할 수 있었다.​맨홀 양품/불량품 샘플이 잘 나왔다.회의를 최소화해서 좋았다.SR 작성이 대략적으로 마무리되었다 .  스탠드업 미팅을 통해 의제의 명료화 및 당일 과제의 지정이 효율적으로 이루어졌다.팀 분위기가 화기애애하다.아쉬운 점문서 작업에 시간을 너무 할애해서 이후 작업을 진행하지 못했다.기술 조사 보고서 작성 시 이해하기 쉽게 목차 정리가 덜 되어 있는 경우가 있어 이해하기 어려운 문서가 존재했다.​프로젝트 진행 중 강의가 불규칙하게 할당되는 경우가 존재했다.컨베이어 벨트 시스템을 관제 시스템과 연동 결정이 어제 확정 되어 오늘부터 연동 준비해야 한다.(아두이노 → ESP32 보드 변경)개선 아이디어​기술조사 페이지 작성시, 한번에 알아볼 수 있도록 이 실험 목적 간략히 적어주시고 실험 결과는 수치 & 정성적 (비디오, 이미지) 등으로 상세히 적어주도록 팀장 ↔︎ 팀원 개별 피드백 진행standup meeting 등의 페이지를 새로 만드실 때, 꼭 template copy해서 만들어주기! 자유 코멘트스프린트 회의 시간: 3분 10.72초 |

#### sprint3_meeting (24543599)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/24543599
**최종 수정**: v3 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | SmartCast Robotics - 다품종 소량 생산 사형 주조 공정 스마트 팩토리 시스템 구축 | 팀명 | 에러맛집 |
****
****
| 스프린트명 | Sprint3 | 수행기간 | ~ |
****
| 스프린트 내용 | 이번 주 검토 |
****
| 차주 스프린트 | 코드 베이스 구성 + DB 구축 완료 + 딥러닝 학습 및 테스트 완료 |
****

### 

- 

- 

- 

- 

- 

- 

### 

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

### 

- 

### 

- 
| 회고 | 잘 된 점1차 연동 테스트기술 조사 분업이 잘됨일이 먼저 끝났을 때 다른 팀원들의 작업을 잘 도와줌피드백 → 반영 구조가 잘 지켜짐​진행 속도가 아주 빠름. 시각적인 구조물이 훌륭함개발 프로세스를 어느 정도 준수하는 편으로 추정됨아쉬운 점문서 작업을 특정 인원만 함. → 팀장이 다음 주부터 문서 작업 할당 일 → 월요일 넘어가는 자정 규정 sequence diagram (전체 프로세스)대현 class diagram 성수 Interface specification → 함종수 강사 Slack 공지 참고(양식)문서 작업만 하느라 하고 싶은 task를 못함. → 다음주부터 문서 작업 할당 문서 작업에 필요한 탬플릿을 학원에서 많이 주면 좋겠음. → 학원에서 적극 협조해줘야함.밀린 개발 과정이 있음. → 주말에도 출근한다. 다른 팀원들의 도움을 받는다.개발 프로세스에서 다른 task간 의사소통 개선이 필요. → 서로 간 필요한 게 무엇인지 정확히 요구해라  Map이 좁다. → 없음개선 아이디어문서 작업을 돌아가면서 모든 인원이 한다.자유 코멘트선반 디자인이 잘 나왔다. |

#### Sprint5_meeting (37224740)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/37224740
**최종 수정**: v2 (2026-04-19 sync)

****
| 과정명 | [심화] ROS2와 AI를 활용한 자율주행 로봇개발자 부트캠프 |
|---|---|
****
****
| 프로젝트명 | SmartCast Robotics - 다품종 소량 생산 사형 주조 공정 스마트 팩토리 시스템 구축 | 팀명 | 에러맛집 |
****
****
| 스프린트명 |   | 수행기간 | 04/20-04/24 |
****
| 스프린트 내용 |   |
****
| 차주 스프린트 |   |
****

### 

### 

### 

### 
| 회고 | 잘 된 점아쉬운 점개선 아이디어자유 코멘트 |

#### sprint2_presentation (11501952)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/11501952
**최종 수정**: v13 (2026-04-19 sync)

# **Sprint2: SA 및 기술조사 진행과정 보고**
**<사형 주조 공정 스마트 팩토리 시스템 구축 - 다품종 소량 생산> **
심화2 ROS와 AI를 활용한 자율주행&로봇팔 개발자 부트캠프 
2팀, 에러맛집 

# 에러 맛집 팀 주제 
사형 주조 공정 스마트 팩토리 시스템 구축 - 다품종 소량 생산 
(사형 주조: 모래로 만든 틀에 용융 금속을 부어 제품을 만드는 공정)

## **전체 공정 과정 개요**
“발주부터 출고까지 하나의 End-to-End 자동화 사이클을 설계했습니다.”

1. 
발주: 원격 발주 → 관리자 발주 승인 → 관리자 생산 시작 알림 → 공정 시작 

1. 
전체 공정: 원재료 투입 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형 → 후처리 → 검사 → 적재 → 출고

  1. 
Casting Zone: 원재료 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형

  1. 
Inspection Zone: 후처리 → 검사

  1. 
Storage Zone: 적재 

  1. 
Shipping Zone: 출고 

# Update! Map Layout 

- 
가정: 일단 로봇의 개수가 무한대

- 
TODO

  - 
제한된 로봇 개수 고려한 맵 제작 

  - 
여러 대의 AMR을 효율적으로 스케줄링할 수 있는 맵 제작 

  - 
다품종 생산 공장에서 일어날 수 있는 제품간의 제작 시간 차이를 고려한 맵 제작 

- 
내일   모여 전체적인 시나리오 및 맵 Layout 논의할 예정입니다. 

# Update! SR 
[https://dayelee313.atlassian.net/wiki/x/VoBf](https://dayelee313.atlassian.net/wiki/x/VoBf)  

- 
기존 SR: 총 9개의 큰 기능 

  - 
지난 피드백: 기존의 기능들은 구현단계에서 하나의 module로 다루기엔 사이즈가 큰 기능들이 묶여 있었음. 

- 
변경 SR: 총 10개의 기능 

  - 
기존의 기능을 분리하여 기능들의 사이즈들이 비슷하도록 조정 

  - 
**SR ID 체계**: 각 기능들의 label들을, **ORD, CTL, CAST, TR, INS, CONV, STO, POST, OUT, CLN **으로 지정

1. 
공정 통합 관제 (CTL)

1. 
주물 생산 자동화 공정 (CAST)

1. 
구역 간 이송 관리 (TR)

1. 
주물 품질 분류 및 제어 (INS)

1. 
컨베이어 이송 제어 (CONV)

1. 
적재 및 창고 관리 (STO)

1. 
출고 관리 (OUT)

1. 
후처리 공정 (POST)

1. 
청소 공정 (CLN)

# Update! UI 
현재  SR(System Requirements)을 기반으로관리자 UI와 고객 UI를 업데이트 하였습니다. 

- 
What’s new?

  - 
SR 기반으로 UI에 필요한 데이터 구조 정의 완료 → 이를 바탕으로 **DB Schema 설계 **예정 

  - 
현재는 **디자인 보완 작업만 남은 상태**

- 
사용한 framework: **Next.js, React**

- 
[관리자 UI](http://192.168.0.16:3000/) : 총 6개의 Tab 존재

  - 
첫 화면은 **통합 대시보드**로 구성하여 전체 공정 및 운영 상태를 한눈에 확인 가능하도록 설계 

- 
[고객 UI](http://192.168.0.16:3000/customer): 

  - 
우측 상단에 **주문 조회 기능 제공**

  - 
온라인 발주 프로세스를 5단계(제품 선택 → 사양 입력 → 견적 확인 → 주문자 정보 → 주문 완료)로 구성하여
사용자 흐름을 직관적으로 설계

# New! SA 

## Old Version of SA 

## New! HW Archtecture 

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

## New! SW Architecture 

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

# NEW! Technical Research 

- 
HW: Robot Arm, AMR, Gripper, Conveyor Belt, Sensor, Embedded Board 

- 
SW: 관제&제어 시스템 , AI, DB, Server 

****
****
****
****
****
****
****
****
****
****
| HW/SW | Device/Model | Research Area | 담당자 | 실험 리스트 | Page | Priority | Status | Start Date | End Date |
|---|---|---|---|---|---|---|---|---|---|
****
| HW |
|   | Robot_Arm | Spec test, 실제 시나리오 상 시연 가능성 테스트 |   | Payload test |   | 1 |   |   |   |
|   |   | Reachability_test |   | 1 |   |   |   |
|   |   | Repeatability_test Dots Marking test) |   | 1 |   |   |   |
|   |   | Repeatability_test (Dots 한붓 그리기 실험) |   | 1 |   |   |   |
|   |   | DoF Test & Orientation Edge Case |   |   |   |   |   |
|   |   | Mold Making - Cycle Time Test & Real Process Test |   |   | cycle time test           Quality 비교 실험 |   |   |
|   |   | Pouring - Cycle Time & Real Process Test |   |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/HwD)
|   | AMR | Mapping, Navigation test, Navigation Accuracy Validation |   | Mapping Test | https://dayelee313.atlassian.net/wiki/x/HwD | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/AQCd)
[](https://dayelee313.atlassian.net/wiki/x/tQC8)
|   |   | Navigation Test | https://dayelee313.atlassian.net/wiki/x/AQCd https://dayelee313.atlassian.net/wiki/x/tQC8 | 1 |   |   |   |
|   | Gripper | Spect Test, Types_comparison, Grasp_test, Failure_cases |   | Gripper Holding Test |   | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/UYDy)
|   | Conveyor | Spec 조사, 실제 시연 적용 가능성 조사 |   | 적용가능성 조사 | https://dayelee313.atlassian.net/wiki/x/UYDy | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/XADu)
|   |   | 비전 검사 & 상위 통신 연동 테스트 | https://dayelee313.atlassian.net/wiki/x/XADu | 2 |   |   |   |
|   | Sensor | Sensor spec, detection_test, reliability |   | 사용 센서 |   | 1 |   |   |   |
|   |   | RGB-D camera |   | 1 |   |   |   |
|   |   | 레이저 센서 |   | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/FQDO)
|   | Embedded Board | HW_type, System_type, Spec |   | 스펙 조사 | https://dayelee313.atlassian.net/wiki/x/FQDO | 2 |   |   |   |
|   | Layout | Workspace_design, Collision_Analysis |   |   |   |   |   |   |   |
****
| SW |
****
****
|   | 제어/시스템 SW |   |   |   |   |
|   | State_Machine | Design, Edge_Cases |   |   |   |   |   |   |   |
|   | Transport_System | Allocation_Strategy, Simulation_Test |   |   |   |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/12124168/?draftShareId=4e04722a-201a-4594-ae2a-52bfe921ced3)
|   | Storage_System | Slotting, Reallocation, Edge_cases |   |   | https://dayelee313.atlassian.net/wiki/spaces/753667/pages/12124168/?draftShareId=4e04722a-201a-4594-ae2a-52bfe921ced3 | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/fIDr)
|   | Control_System | Logic_Design, Exception_Handling |   |   | https://dayelee313.atlassian.net/wiki/x/fIDr | 2 |   |   |   |
****
|   | AI 모델 SW |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/IwB1)
|   | Vision | Classification, Anomaly Detection |   | Object Detection with YOLOv26 | https://dayelee313.atlassian.net/wiki/x/IwB1 | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/C4Ca)
|   |   |   |   | Pixel coordinate extraction from Image and Video with Yolov26 | https://dayelee313.atlassian.net/wiki/x/C4Ca |   |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/eADC)
|   |   |   |   | Camera Calibration를 통한 좌표 변환 | https://dayelee313.atlassian.net/wiki/x/eADC | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/9QCG)
|   |   |   |   | Anomaly Detection with PatchCore | https://dayelee313.atlassian.net/wiki/x/9QCG | 1 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/LACS)
|   |   |   |   | Binary Classifier via Transfer Learning with YOLOv26 nano model | https://dayelee313.atlassian.net/wiki/x/LACS | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/x/MwC-/)
|   |   |   |   | AD Comparative Study with PatchCore & RGDB-AD | https://dayelee313.atlassian.net/wiki/x/MwC-/ | 2 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7438588/?draftShareId=6283774c-2071-4234-aada-f8a6fc89f2be)
|   | LLM/VLM |   |   |   | https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7438588/?draftShareId=6283774c-2071-4234-aada-f8a6fc89f2be | 3 |   |   |   |
[](https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7405754/?draftShareId=36a216e9-6766-44e1-b132-d75a2e688172)
|   | VLA |   |   |   | https://dayelee313.atlassian.net/wiki/spaces/753667/pages/7405754/?draftShareId=36a216e9-6766-44e1-b132-d75a2e688172 | 3 |   |   |   |
****
| DB System |
[](https://dayelee313.atlassian.net/wiki/x/_QBy)
|   | Database_System | ERD_design, State_management, Transaction_consistency, Event_flow, Latency_test |   | ERD, SQL, Tools 자료 조사 및 공유 | https://dayelee313.atlassian.net/wiki/x/_QBy | 1 |   |   |   |
|   |   | Schema 작업 |   | 2 |   |   |   |
|   | Cache_System | Redius_usage, Task_queue, State_cache |   |   |   |   |   |   |   |
|   | Loggin_System | Sensor_logs, Time_series, Monitoring |   |   |   |   |   |   |   |
****
| Server |
|   | Kubernetes |   |   |   |   | 2 |   |   |   |
|   | AWS, GCP |   |   |   |   |   |   |   |   |

# Summary & Plan 

- 
Completed:

  - 
UR → SR → SA  

  - 
Technical Research (On-going)

- 
Sprint3 TODO:

  - 

    - 
**TODO: DB Schema (on-going) → 가상 데이터 구축 → GUI에 연결 **

  - 
 Technical Research 완료 (by   목) 

    - 
관제 파트 시작! 

  - 
연동 작업 (틀만 적어놓고 Implementation 은 sprint 4에 시작) 

    - 
시작  목 ~ 완료  월

#### sprint3_presentation (15208396)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/15208396
**최종 수정**: v12 (2026-04-19 sync)

|   |
|---|

## **전체 공정 과정 개요**
“발주부터 출고까지 하나의 End-to-End 자동화 사이클을 설계했습니다.”

1. 
**발주**: 원격 발주 → 관리자 발주 승인 → 관리자 생산 시작 알림 → 공정 시작 

1. 
**전체 공정**: 원재료 투입 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형 → 후처리 → 검사 → 적재 → 출고

  1. 
Casting Zone: 원재료 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형

  1. 
Inspection Zone: 후처리 → 검사

  1. 
Storage Zone: 적재 

  1. 
Shipping Zone: 출고 

# V-model 

## User Requirements 

****
| 주조 공정 실무자 인터뷰를 통해, 실무자의 자동화 필요성을 파악 |
|---|
|   |

****
| PinkyPro AMR 3대·로봇팔 2대를 활용해 주문 접수부터 주물 생산·검사·출하까지 스마트 팩토리 전 공정을 자동화하는 시스템 설계 및 구현 |
|---|
****
****
| UR_NAME | Subcategory |

- 
| 주문/생산 계획 | 고객 주문 및 생산 오더 생성 |

- 
| 관리 모니터링 | 관리자 생산 전체 공정 모니터링 |

- 

- 
| 원자재 처리 | 원자재 투입 관리도가니 용광로 투입 |

- 

- 

- 

- 
| 주형 및 주조 | 주형 생성용탕 주입 주물 냉각 상태 모니터링 주물 탈형 |

- 

- 
| 이송/물류 | 주물 팔래트 적재팔레트 구역 간 이송 |

- 

- 
| 후처리 | 후처리 구역 청소 후처리 구역에서 검사 구역 이동 |

- 
| 주물 품질 검사 | 주물 양품/불량품 검사 |

- 

- 
| 분류 / 출하 | 양품 / 불량품 적재 양품 팔레트 이송 및 적재 |

## System Requirements 

- 

- 
********
| UR 기반 SR에서는 총 10개 시스템으로 분류하고, SR-{시스템}-{기능번호} ID 체계를 수립하여 각 기능의  요구사항, 세부 기능, 우선순위를 명확히 정의하였습니다. 기능들의 사이즈들이 비슷하도록 분류SR ID 체계: 각 기능들의 label들을, ORD, CTL, CAST, TR, INS, CONV, STO, POST, OUT, CLN 으로 지정 |
|---|
|   |

## System Architecture 

### SW System Architecture 
 

|   |
|---|
|   |

### 
 

|   |
|---|

###  

###  

# Map Layout 

## 시나리오 PART1: 주조 + 이송 + 검사 
|   |   |

## Admin PC 

****
****
| Admin login | 로그인 후 관리자 포털  (2개 탭: 주문 관리, 품질 관리) |
|---|---|
|   |   |
****
****
| 주문 관리 | 품질 관리 |
|   |   |

## User PC 

****
****
| 주문 | 조회 |
|---|---|

| 온라인 발주 프로세스를 5단계(제품 선택 → 사양 입력 → 견적 확인 → 주문자 정보 → 주문 완료)로 구성하여사용자 흐름을 직관적으로 설계 | 이메일 기준 발주 목록 조회 및 각 오더마다 진행 상황을 볼 수 있도록 UI 설계 |
|   |   |
|   |   |

# Technical Research 

- 
HW: Robot Arm, AMR, Gripper, Conveyor Belt, Sensor, Embedded Board 

- 
SW: 관제&제어 시스템 , AI, DB, Server 

****
****
****
| 분류 | Device/모듈 | 실험 및 결과 |
|---|---|---|

- 

- 

- 

- 

- 

- 

- 
| HW | Robot Arm | payload test: 400g 동작 OK, 파지력 250g spec 확인Reachability test: 반경 280~300mm, 자유자재 작업 영역 한정적 → orientation 위주 map layout 필요 Repeatability (5 dots): 오차 0.5~1.0mm, 주조 시나리오에 충분Repeatability (한붓 그리기): 오차 0.5~1.5mm, 주조 시나리오에 충분 DoF: DoF 스펙 일치Mold making cycle time: 약 40초 소요Pouring cycle time: 1분 ~ 1분 30초 소요 |

- 

- 
|   | AMR | Mapping Test: SLAM toolbox 기반 안정적, mapping, 실제 주행용 map 완성 Navigation Test: 충돌 없이 안정적 주행 확인 |

- 

- 
|   | Conveyor | 적용가능성 조사: 이송 성공률 100%, 정렬 이탈 70% → 센터라인 표시 필요 비전 검사 & 통신 연동:  ESP32에 micro-ROS 설치 |

- 

- 

- 

- 

- 

- 
****

- 
****
| SW | Vision | Yolov26 (Detection): 기본 성능 충분, 맨홀 뚜껑 데이터 수집 후 finetuning 예정 pixel coordinate extraction: 실시간 스트리밍에서 작동 확인 camera calibration: 좌표 변환 확인. 성능 안 좋음 anomaly detection: patchcore 실시간 가능 (0.015~0.024초/장)3개 맨홀 디자인 클래스 분류 yolov26 finetuning 성공 VLA 기술 조사 (On-going)관제 시스템 조사 (On-going) |

# Implementation  

## Data flow 

##  

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
| Test-003-A |   | Interface Service | Management Service | TCP | Interface에서 Management Service로 주문 정보 전송테스트 영상테스트 영상 |   |   |   |
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

# Sprint 회의 내용 

## 잘된 점 

- 

- 

- 

- 

- 

- 
| 1차 연동 테스트기술 조사 분업이 잘 됨일이 먼저 끝났을 때 다른 팀원들의 작업을 잘 도와줌피드백 → 반영 구조가 잘 지켜짐​진행 속도가 아주 빠름. 시각적인 구조물이 훌륭함개발 프로세스를 어느 정도 준수하는 편으로 추정됨 |
|---|

## 아쉬운 점 & 개선 아이디어 

****
****
| 아쉬운 점 | 개선 아이디어 |
|---|---|
| 문서 작업을 특정 인원(팀장)만 함 | 팀장이 다음 주부터 문서 작업 팀원들에게 할당 |
| 문서 작업만 하느라 하고 싶은 task를 못함 | 다음 주부터 문서 작업 할당 |
| 밀린 개발 과정이 있음 | 주말에도 출근한다. 다른 팀원들의 도움을 받는다 |
| 개발 프로세스에서 다른 task간 의사소통 개선이 필요 | 서로 간 필요한 게 무엇인지 정확히 요구해라 |

# Summary & Plan 

- 
Completed:

  - 
UR → SR → SA

  - 
Technical research (almost completed, VLA 파트 on-going)

  - 
Detailed Design (On-going)

- 
Sprint4 TODO:

  - 
프로젝트 구현: 전체 기능의 30%

  - 
2차 연동 테스트 

  - 
산출물:

    - 
프로젝트 코드 리뷰: v0.2 

    - 
수행일지

#### sprint4_presentation (26249236)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/26249236
**최종 수정**: v3 (2026-04-19 sync)

|   |
|---|

## **전체 공정 과정 개요**
“발주부터 출고까지 하나의 End-to-End 자동화 사이클을 설계했습니다.”

1. 
**발주**: 원격 발주 → 관리자 발주 승인 → 관리자 생산 시작 알림 → 공정 시작 

1. 
**전체 공정**: 원재료 투입 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형 → 후처리 → 검사 → 적재 → 출고

  1. 
Casting Zone: 원재료 → 용융 → 주형 제작 → 주탕 → 냉각 → 탈형

  1. 
Inspection Zone: 후처리 → 검사

  1. 
Storage Zone: 적재 

  1. 
Shipping Zone: 출고 

- 
End-to-End: 딥러닝 분야에서는 input-output 이 하나의 통합 모델로 연결된 상태를 의미하나, 이번 시스템에서의 의미는 처음부터 끝까지라는 의미로 사용하였다. 

# 

## User Requirements 

****
| 주조 공정 실무자 인터뷰를 통해, 실무자의 자동화 필요성을 파악 |
|---|
|   |

****
| PinkyPro AMR 3대·로봇팔 2대를 활용해 주문 접수부터 주물 생산·검사·출하까지 스마트 팩토리 전 공정을 자동화하는 시스템 설계 및 구현 |
|---|
****
****
| UR_NAME | Subcategory |

- 
| 주문/생산 계획 | 고객 주문 및 생산 오더 생성 |

- 
| 관리 모니터링 | 관리자 생산 전체 공정 모니터링 |

- 

- 
| 원자재 처리 | 원자재 투입 관리도가니 용광로 투입 |

- 

- 

- 

- 
| 주형 및 주조 | 주형 생성용탕 주입 주물 냉각 상태 모니터링 주물 탈형 |

- 

- 
| 이송/물류 | 주물 팔래트 적재팔레트 구역 간 이송 |

- 

- 
| 후처리 | 후처리 구역 청소 후처리 구역에서 검사 구역 이동 |

- 
| 주물 품질 검사 | 주물 양품/불량품 검사 |

- 

- 
| 분류 / 출하 | 양품 / 불량품 적재 양품 팔레트 이송 및 적재 |

## System Requirements 

- 

- 
********
| UR 기반 SR에서는 총 10개 시스템으로 분류하고, SR-{시스템}-{기능번호} ID 체계를 수립하여 각 기능의  요구사항, 세부 기능, 우선순위를 명확히 정의하였습니다. 기능들의 사이즈들이 비슷하도록 분류SR ID 체계: 각 기능들의 label들을, ORD, CTL, CAST, TR, INS, CONV, STO, POST, OUT, CLN 으로 지정 |
|---|
|   |

## System Architecture 

### SW System Architecture 
 

|   |
|---|
|   |

### 
 

|   |
|---|

###  

###  

# Map Layout 

## 시나리오 PART1: 주조 + 이송 + 검사 
|   |   |

## Admin PC 

****
****
| Admin login | 로그인 후 관리자 포털  (2개 탭: 주문 관리, 품질 관리) |
|---|---|
|   |   |
****
****
| 주문 관리 | 품질 관리 |
|   |   |

## User PC 

****
****
| 주문 | 조회 |
|---|---|

| 온라인 발주 프로세스를 5단계(제품 선택 → 사양 입력 → 견적 확인 → 주문자 정보 → 주문 완료)로 구성하여사용자 흐름을 직관적으로 설계 | 이메일 기준 발주 목록 조회 및 각 오더마다 진행 상황을 볼 수 있도록 UI 설계 |
|   |   |
|   |   |

# Technical Research 

- 
HW: Robot Arm, AMR, Gripper, Conveyor Belt, Sensor, Embedded Board 

- 
SW: 관제&제어 시스템 , AI, DB, Server 

****
****
****
| 분류 | Device/모듈 | 실험 및 결과 |
|---|---|---|

- 

- 

- 

- 

- 

- 

- 
| HW | Robot Arm | payload test: 400g 동작 OK, 파지력 250g spec 확인Reachability test: 반경 280~300mm, 자유자재 작업 영역 한정적 → orientation 위주 map layout 필요 Repeatability (5 dots): 오차 0.5~1.0mm, 주조 시나리오에 충분Repeatability (한붓 그리기): 오차 0.5~1.5mm, 주조 시나리오에 충분 DoF: DoF 스펙 일치Mold making cycle time: 약 40초 소요Pouring cycle time: 1분 ~ 1분 30초 소요 |

- 

- 
|   | AMR | Mapping Test: SLAM toolbox 기반 안정적, mapping, 실제 주행용 map 완성 Navigation Test: 충돌 없이 안정적 주행 확인 |

- 

- 
|   | Conveyor | 적용가능성 조사: 이송 성공률 100%, 정렬 이탈 70% → 센터라인 표시 필요 비전 검사 & 통신 연동:  ESP32에 micro-ROS 설치 |

- 

- 

- 

- 

- 

- 
****

- 
****
| SW | Vision | Yolov26 (Detection): 기본 성능 충분, 맨홀 뚜껑 데이터 수집 후 finetuning 예정 pixel coordinate extraction: 실시간 스트리밍에서 작동 확인 camera calibration: 좌표 변환 확인. 성능 안 좋음 anomaly detection: patchcore 실시간 가능 (0.015~0.024초/장)3개 맨홀 디자인 클래스 분류 yolov26 finetuning 성공 VLA 기술 조사 (On-going)관제 시스템 조사 (On-going) |

# Implementation  

## Data flow 

##  

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
| Test-003-A |   | Interface Service | Management Service | TCP | Interface에서 Management Service로 주문 정보 전송테스트 영상테스트 영상 |   |   |   |
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
| Test-011-B |   | Transport Service | Management Service | ROS2 | Transport Service(AMR)에서 Management Service로 데이터 전송테스트 영상 |   |   |   |

# Sprint 회의 내용 

## 잘된 점 

- 

- 

- 

- 

- 

- 
| 1차 연동 테스트기술 조사 분업이 잘 됨일이 먼저 끝났을 때 다른 팀원들의 작업을 잘 도와줌피드백 → 반영 구조가 잘 지켜짐​진행 속도가 아주 빠름. 시각적인 구조물이 훌륭함개발 프로세스를 어느 정도 준수하는 편으로 추정됨 |
|---|

## 아쉬운 점 & 개선 아이디어 

****
****
| 아쉬운 점 | 개선 아이디어 |
|---|---|
| 문서 작업을 특정 인원(팀장)만 함 | 팀장이 다음 주부터 문서 작업 팀원들에게 할당 |
| 문서 작업만 하느라 하고 싶은 task를 못함 | 다음 주부터 문서 작업 할당 |
| 밀린 개발 과정이 있음 | 주말에도 출근한다. 다른 팀원들의 도움을 받는다 |
| 개발 프로세스에서 다른 task간 의사소통 개선이 필요 | 서로 간 필요한 게 무엇인지 정확히 요구해라 |

# Summary & Plan 

- 
Completed:

  - 
UR → SR → SA

  - 
Technical research (almost completed, VLA 파트 on-going)

  - 
Detailed Design (On-going)

- 
Sprint4 TODO:

  - 
프로젝트 구현: 전체 기능의 30%

  - 
2차 연동 테스트 

  - 
산출물:

    - 
프로젝트 코드 리뷰: v0.2 

    - 
수행일지

#### 모니터링 대시보드UI (5505054)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5505054
- **타입**: whiteboard (storage format 미지원, 본문 없이 레퍼런스만)

#### 고객용 주문 화면 (6914067)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/6914067
- **타입**: whiteboard (storage format 미지원, 본문 없이 레퍼런스만)

#### 전력 수요 관리 대시보드 (5311612)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5311612
- **타입**: whiteboard (storage format 미지원, 본문 없이 레퍼런스만)

#### MAP (whiteboard) (2850917)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/2850917
- **타입**: whiteboard (storage format 미지원, 본문 없이 레퍼런스만)

#### Untitled whiteboard 2026-04-08 (20152370)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/20152370
- **타입**: whiteboard (storage format 미지원, 본문 없이 레퍼런스만)

#### SmolVLA(미완성) (2162773)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/2162773
**최종 수정**: v1 (2026-04-19 sync)

### Model
[https://huggingface.co/lerobot/smolvla_base](https://huggingface.co/lerobot/smolvla_base) 

### Requirements

### Code

### Input

- 
데이터 구조

  - 
필수:

    - 
`observation.images.*`: 최소 1개 이상의 카메라(이미지)

      - 
config에 정의된 키와 하나 이상 이름이 매칭돼야 함

      - 
shape: `Tensor [B, 3, H, W]`

      - 
값 범위: `float32 [0, 1]`

    - 
`observation.state`: 로봇 현재 상태

      - 
shape이 config의 `state_dim`과 정확히 일치해야함

      - 

### Output

- 
데이터 구조
ex: `tensor([[-0.3133,  0.0967,  0.7009,  2.2490,  0.0577, -0.5445]])`

#### 테스트 (786449)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/786449
**최종 수정**: v1 (2026-04-19 sync)

#### Untitled page (5144703)

**Confluence URL**: https://dayelee313.atlassian.net/wiki/spaces/addinedute/pages/5144703
- **상태**: draft / placeholder

