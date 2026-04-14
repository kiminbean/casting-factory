# 주물공장 생산 관제 시스템 (Casting Factory MES)

> **Last updated**: 2026-04-14 (V6 아키텍처 마이그레이션 8단계 완료)

## 0. V6 아키텍처 (2026-04-14)

Interface Service(FastAPI :8000) 와 Management Service(gRPC :50051) 를 별도 프로세스로 분리. PyQt 는 Management Service 직결.

| 구간 | 프로토콜 | 채널 | 엔드포인트 |
|---|---|---|---|
| Admin/Customer 웹 → Server | HTTP | Interface Service | `localhost:8000/api/*` |
| **Factory PC PyQt → Server** | **gRPC TCP** | **Management Service** | **`localhost:50051`** |
| Server → AMR/Cobot | ROS2 DDS (Lazy) | ros2_adapter (RPi 배포 시) | `MGMT_ROS2_ENABLED=1` |
| Server → ESP32 | MQTT | mqtt_adapter | `casting/esp/{id}/cmd` |
| Image Publisher → Server | gRPC streaming | ImagePublisherService | `:50051 PublishFrames` |

**핵심 가치**: Interface Service 장애/AWS 이관 시에도 공장 가동 중단 없음 (SPOF 제거).

**Management Service RPC** (8종):
- StartProduction, ListItems, AllocateItem, PlanRoute, ExecuteCommand, WatchItems, WatchAlerts, Health

**자세한 설계**: `docs/management_service_design.md`

## 프로젝트 개요

주물(캐스팅) 스마트 공장의 실시간 생산 관제 시스템. 용해 → 주형 제작 → 주탕 → 냉각 → 탈형 → 후처리 → 검사 → 분류의 **8단계 생산 공정** 전체를 모니터링·통제하며, 주문·품질·물류·설비·우선순위 계산을 단일 플랫폼에서 관리한다.

## 사용자 및 배포 채널

| 사용자 | 채널 | 접근 방법 |
|---|---|---|
| **공장 관리자** | Next.js 웹 `/orders`, `/quality` | 데스크톱 브라우저 |
| **Factory PC 담당자** | PyQt5 데스크톱 앱 (6 페이지) | Factory PC 직접 실행 |
| **생산 담당자** | PyQt5 (대시보드·공장맵·생산모니터링·생산계획) | Factory PC |
| **품질 관리자** | PyQt5 (품질) + 웹 `/quality` | Factory PC + 웹 |
| **물류 담당자** | PyQt5 (물류) | Factory PC |
| **고객사** | Next.js `/customer` 포털 | 웹 브라우저 (4단계 발주 폼) |
| **고객 (주문 조회)** | Next.js `/customer/orders` | 웹 브라우저 (타임라인) |

### UI 분리 정책 (2026-04-08 확정)

실시간 모니터링성 페이지 5종(대시보드·공장맵·생산모니터링·생산계획·물류·품질 모니터링)은 **PyQt5 Factory PC 앱**으로 이관 완료. Next.js 웹에는 **주문 관리·품질 관리** 2페이지와 **고객 포털** 2페이지만 유지. 근거: Confluence 17956894 결정, Sidebar 주석에 명시.

## 핵심 기능

### 1. 고객 발주 포털 `/customer`

5단계 발주 폼 (주문자 정보 → 제품 선택 → 사양 입력 → 견적 확인 → 주문 완료) — 2026-04-13 재배치:
- **제품 카탈로그 30종** (2026-04-14 확장):
  - 원형 맨홀뚜껑 10종 (KS D-450 ~ D-900, 75,000~165,000원)
  - 사각 맨홀뚜껑 10종 (400x400 ~ 900x900, 68,000~168,000원)
  - 타원형 맨홀뚜껑 10종 (450x300 ~ 900x750, 72,000~168,000원)
- 카테고리 필터: 전체 / 원형 / 사각 / 타원형 (4개 버튼)
- 카테고리별 대표 이미지 (`public/products/round|square|oval.jpg`)
- 사양: 직경, 두께, 재질(FC200/FC250/GCD450/GCD500), 하중 등급(B125~F900), 후처리 4종(연마/방청/아연도금/로고)
- 고객 정보 + 배송지 + 요청 납기
- 견적 확인 → 주문 제출 시 `/api/orders` + `/api/orders/{id}/details` 순차 POST

### 2. 고객 주문 조회 `/customer/orders`

- 주문번호·연락처·회사명으로 검색
- 6단계 상태 파이프라인 타임라인 (pending → reviewing → approved → in_production → shipping_ready → completed)
- 주문 상세 (품목·금액·납기·상태 변경 알림)

### 3. 관리자 주문 관리 `/orders`

- 주문 접수/검토/승인/생산/출하/완료 상태 탭
- 주문 상세 (고객사·납기·품목·금액 편집)
- **생산 승인** 버튼으로 7요소 가중 우선순위 계산 후 ProductionJob 생성
- 상태 스테퍼 (2026-04-09 추가)

### 4. 관리자 품질 관리 `/quality`

- 검사 기록 / 품질 통계 / 기준 관리 / 분류기 로그 4탭
- 합격률·불량률·불량 유형 분포 차트

### 5. PyQt5 대시보드 (`monitoring/app/pages/dashboard.py`)

- 생산 KPI 카드, 공장 맵, 알림 피드, 주간 차트

### 6. PyQt5 공장 맵 (`monitoring/app/pages/map.py`)

- 2D/3D 공장 레이아웃, 설비 위치·상태 시각화
- 컨베이어·AMR·로봇 암 상태 표시

### 7. PyQt5 생산 모니터링 (`monitoring/app/pages/production.py`)

- 8단계 공정 상태 실시간 (용해 → 분류)
- 공정별 온도·압력·출력·진행률

### 8. PyQt5 생산 계획 (`monitoring/app/pages/schedule.py`)

- 7요소 가중 우선순위 엔진 (납기 긴급도 25 + 착수 가능 20 + 체류 15 + 지연 위험 15 + 고객 중요도 10 + 수량 효율 10 + 세팅 5 = 100점)
- 대기 주문 랭킹, 수동 우선순위 조정, 변경 이력

### 9. PyQt5 품질 관리 (`monitoring/app/pages/quality.py`)

- 비전 검사 결과, 불량 유형 분류, 소터 로그

### 10. PyQt5 물류 관리 (`monitoring/app/pages/logistics.py`)

- AMR 이송 태스크, 창고 랙 상태(24칸), 출고 지시서(FIFO/LIFO)

### 11. ESP32 컨베이어 펌웨어 (`firmware/conveyor_controller/`)

- L298N + TOF250×2 + JGB37-555 모터
- 상태머신: IDLE → RUNNING → STOPPED → POST_RUN → CLEARING
- WiFi + MQTT (`vision/1/result` 구독)

## 제품 카탈로그

| id | 이름 | 카테고리 | 기준가 | 하중 범위 |
|---|---|---|---|---|
| D450 | 맨홀 뚜껑 KS D-450 | 맨홀 뚜껑 | 50,000 - 70,000원 | B125 ~ D400 |
| D600 | 맨홀 뚜껑 KS D-600 | 맨홀 뚜껑 | 75,000 - 100,000원 | B125 ~ F900 |
| D800 | 맨홀 뚜껑 KS D-800 | 맨홀 뚜껑 | 110,000 - 140,000원 | C250 ~ F900 |
| GRATING | 배수구 그레이팅 500x300 | 그레이팅 | 30,000 - 45,000원 | B125 ~ C250 |

**Source of truth**: `src/app/customer/page.tsx` 의 `PRODUCTS` 하드코딩 배열.
**DB 반영**: `products` 테이블 (2026-04-09, 프론트와 1:1 매칭). `PRD-001~005` 레거시 ID 는 모두 정리 완료.

## EN 124 하중 등급 마스터 (신규, 2026-04-09)

| 코드 | 톤수 | 용도 |
|---|---|---|
| A15 | 1.5 | 보행자 전용 |
| B125 | 12.5 | 자전거·보행자 도로, 주차장 |
| C250 | 25 | 길가·갓길 |
| D400 | 40 | 일반 차도 |
| E600 | 60 | 항만·산업 구역 |
| F900 | 90 | 공항·특수 중하중 |

DB 테이블 `load_classes` + API `/api/load-classes`. `products.load_class_range` 문자열을 실제 톤수로 JOIN 가능.

## 비즈니스 도메인

- **산업**: 주물(캐스팅) 제조업
- **공장 제품**: EN 124 맨홀 뚜껑·그레이팅·빗물받이 (지자체 납품 중심)
- **시스템 유형**: MES + SCADA + 고객 포털 하이브리드
- **공정 특화**: 용해로 온도 제어, 주형 압력, 냉각 프로세스, 비전 검사, AMR 이송

## 주요 외부 연동 및 참조

- **Confluence `addinedute` space** (homepage 753829): 프로젝트 설계 원본 (22개 페이지). 매일 09:07 launchd 로 `docs/CONFLUENCE_FACTS.md` 자동 동기화. **쓰기 금지 (READ-ONLY)**.
- **GitHub Issues / Pull Requests** (kiminbean/casting-factory).
- **MQTT broker** (192.168.0.16:1883 추정): ESP32 ↔ 백엔드 ↔ PyQt5 vision/AMR 이벤트.
- **Atlassian Cloud** (id.atlassian.com): API token 기반 Confluence 동기화.

## 현재 상태 (2026-04-09)

| 영역 | 상태 |
|---|---|
| **DB** | PostgreSQL 16 전환 완료 (Homebrew, 127.0.0.1:5432 + LAN 192.168.0.16:5432) |
| **DB 데이터** | 15 테이블 · 163 rows (orders 12, order_details 12, products 4, load_classes 6 등) |
| **백엔드** | FastAPI + SQLAlchemy 2.0 + psycopg 3.2, 31 REST + 1 WS 엔드포인트 |
| **프론트 웹** | Next.js 16.2.1 + React 19.2.4, 주문 관리·품질 관리·고객 포털 구현 |
| **프론트 API 연동** | `api.ts` 20+ fetch 함수 활성화 완료. 단 `fetchProducts` / `fetchLoadClasses` 는 미구현 (DB 조회 전용) |
| **고객 포털 하드코딩** | `PRODUCTS`, `LOAD_CLASSES` 여전히 하드코딩 (의도적 유지, DB 서버 이관 후 연동 예정) |
| **PyQt5 모니터링** | 6 페이지 + 10 위젯 + WS/MQTT 워커 구현, Factory PC 배포 |
| **펌웨어** | conveyor_controller v4.0.0 (MQTT 연동 완료) |
| **운영 자동화** | Confluence 동기화 launchd (매일 09:07), DB LAN 공유 (scram-sha-256, 192.168.0.0/24) |
| **테스트** | 미작성 (0개 파일) |
| **인증/권한** | 미구현 (개발 단계) |

## 로드맵 (다음 단계)

### 단기 (2026-04-16 전후)
- **DB 서버 재지정**: 개인 Mac → 전용 DB 서버 (pg_dump/pg_restore 이관, 연결 문자열 한 줄만 수정하면 됨)
- **프론트 API 연동**: `fetchProducts`, `fetchLoadClasses` 추가 + `types.ts` Product 인터페이스 확장 + `customer/page.tsx` 하드코딩 제거

### 중기
- 인증 시스템 (Auth0 또는 Clerk)
- 테스트 스위트 도입 (Vitest / pytest)
- FMS 구현 (Confluence V4 레이어 07~12, 현재 설계 문서만)
- Open-RMF vs 자체 스케줄러 결정

### 장기
- TimescaleDB 하이퍼테이블 적용 (production_metrics, inspection_records 등 시계열)
- AMR 실기 연동 (현재는 별도 `casting_factory_fleet` 레포에서 개발)
- Vision 시스템 실기 연동 (YOLOv8 추정)
