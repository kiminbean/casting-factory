@AGENTS.md

# V6 아키텍처 결정 (2026-04-14)

**프로세스 이원화**:
- `backend/app/` — Interface Service (FastAPI, :8000, HTTP). Admin/Customer PC 용.
- `backend/management/` — Management Service (gRPC, :50051). Factory Operator PC(PyQt) 직결.

**클라이언트별 채널**:
- PyQt → `monitoring/app/management_client.py` (gRPC) + 기존 api_client (WebSocket 보조)
- Next.js → FastAPI REST (HTTP)

**이유**: Interface Service 장애/AWS 이관 시에도 공장 가동 유지 (SPOF 제거).

**DB 정책 (2026-04-14)**: PostgreSQL 16 + TimescaleDB **단독**. SQLite 폴백 완전 제거.
운영/개발 모두 동일 PG (`100.107.120.14:5432 / smartcast_robotics`, role `team2`).
DATABASE_URL 미설정 시 backend 가 fail-fast.

**HW 통신 채널 (V6 어댑터 라우팅)**:
- AMR-* / ARM-* → ROS2 DDS (RPi5/RPi4 노드, `MGMT_ROS2_ENABLED=1` 시 활성)
- CONV-* / ESP-* → MQTT `casting/esp/{id}/cmd` (ESP32 HW Control Service)
- Image Publisher → gRPC streaming `ImagePublisherService/PublishFrames` (Jetson)

**설계 문서**: `docs/management_service_design.md`
**API 정의**: `backend/management/proto/management.proto`

# Confluence Facts Index

프로젝트 작업 중 Confluence 기반 사실 확인이 필요할 때, 아래 목차를 참고하여 `docs/CONFLUENCE_FACTS.md`의 **해당 섹션만** 직접 읽어 참조하세요. 전체 파일(1035줄)을 한 번에 읽지 말 것.

**원본**: `docs/CONFLUENCE_FACTS.md` (22개 Confluence 페이지 전량 수집본, 주 1회 수기 재검증 + launchd 매일 자동 동기화)

## 사용 규칙

- 특정 주제가 필요할 때만 해당 섹션을 `Read`(offset/limit) 또는 `Grep`으로 부분 로드
- 코드 ↔ Confluence 불일치 의심 시 **§ 알려진 불일치** 먼저 확인
- 빠른 수치/스택 확인은 **§ 통합 팩트 시트** 우선 참조

## 목차 (CONFLUENCE_FACTS.md)

### 상단 섹션
- **사용 원칙** — L8
- **목차 (원본)** — L25

### 1. 01_Project_Design — L59
- 1.1 System Architecture (3375131) — L63
- 1.2 Detailed Design (6651919) — L97
- 1.3 v_model (3506182) — L134
- 1.4 User_Requirements (3375120) — L144
- 1.5 System_Requirements_v3 (6258774) — L179
- 1.6 Layout (4915220) — L333
- 1.7 MVP_Prioritization (3375144) — L342
- 1.8 Scenarios (15729093) — L371

### 2. 02_Domain_Research — L380
- 2.1 intro (3211297) — L384
- 2.2 Casting (3375162) — L393
- 2.3 Logistics (3637320) — L433
- 2.4 Terminology (3407906) — L446

### 3. 03_Technical_Research — L536
- 3.1 HW_Research (8552537) — L540
- 3.2 SW_Research (8552545) — L547
- 3.3 DB_Research (8585277) — L554
- 3.4 SW_Control (15433852) — L562

### 4. 04_Implementation — L572
- 4.1 VLA (3276898) — L576
- 4.2 LLM (3703098) — L583
- 4.3 Prototypes (3407954) — L590
- 4.4 DB (5898574) — L597
- 4.5 GUI (6389916) — L675
- 4.6 SmartCast Robotics GitHub 폴더 구조 초안 (20217883) — L806

### 통합 팩트 시트 (Quick Reference) — L863
- Hardware Stack (확정) — L865
- Software Stack (확정, 2026-04) — L877
- 8단계 생산 공정 — L895
- 8개 GUI 라우트 — L905
- 27개 REST API + WebSocket — L915
- SR 카테고리 (9개) — L918
- 주요 NFR 수치 — L932
- 생산 계획 7요소 우선순위 엔진 — L947
- Factory 제품 — L959

### 부록
- **알려진 Confluence ↔ 코드 불일치** — L970
- **참조 정책** — L987
- **페이지 ID 빠른 참조** — L999

## 참조 예시

```
# 예: System Requirements v3만 필요
Read docs/CONFLUENCE_FACTS.md (offset: 179, limit: 154)

# 예: 하드웨어 스택만 필요
Read docs/CONFLUENCE_FACTS.md (offset: 865, limit: 12)

# 예: 특정 키워드 검색
Grep "TimescaleDB" docs/CONFLUENCE_FACTS.md
```

## 자동 동기화 (launchd)

> **⚠️ Confluence READ-ONLY**: `dayelee313.atlassian.net/wiki/spaces/addinedute` (homepage 753829) 하부 페이지는 **사용자 명시 허락 없이 수정/생성/삭제 금지**. 자동 동기화는 GET 요청만 수행하며, `docs/CONFLUENCE_FACTS.md` 를 로컬에서 업데이트할 뿐 Confluence 원본은 건드리지 않는다. 향후 어떤 스크립트·에이전트·MCP 호출도 PUT/POST/DELETE 는 사용자 확인 후에만 허용된다.

- 스크립트: `scripts/sync_confluence_facts.py` (stdlib only)
- 스케줄: 매일 **09:07** 로컬 시각 (`~/Library/LaunchAgents/com.casting-factory.confluence-sync.plist`)
- 인증: macOS Keychain (`service=casting-factory-atlassian`, `account=kiminbean@gmail.com`)
- 동작: 섹션 헤더의 페이지 ID(예: `### 1.1 System Architecture (3375131)`)로 Confluence v2 API 조회 → version 변화 시 body(storage)를 Markdown 으로 변환해 해당 섹션 in-place 덮어쓰기 → 변경 감지 시 자동 `git commit`
- 라인 번호: 자동 동기화 실행 후 섹션 위치가 바뀔 수 있음. 위 목차의 라인 번호가 어긋나면 `Grep "### [0-9]\.[0-9]" docs/CONFLUENCE_FACTS.md -n` 으로 재확인.

### 큐레이션 보존 마커

섹션 내 수기 작성한 블록(예: `#### 코드베이스 교차검증`)을 자동 동기화에서 보호하려면 아래 마커로 감싸세요. 스크립트는 마커 블록을 그대로 다음 본문 아래에 이어 붙입니다.

```markdown
<!-- CURATED:START -->
#### 코드베이스 교차검증
- ✅ ...
- ⚠️ ...
<!-- CURATED:END -->
```

### 수동 실행 / 디버깅

```bash
# 로그 확인
tail -f logs/confluence_sync.log

# 변경 감지만 (파일/git 변경 없음)
python3 scripts/sync_confluence_facts.py --dry-run

# launchd 상태/재적재
launchctl list | grep casting-factory
launchctl unload ~/Library/LaunchAgents/com.casting-factory.confluence-sync.plist
launchctl load   ~/Library/LaunchAgents/com.casting-factory.confluence-sync.plist
```
