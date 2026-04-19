# SPEC-RC522-001 배너 패치 — PR #2 머지 후 적용

PR #2 (`feat/SPEC-RC522-001-rc522-regression-suite`) 가 main 으로 머지된 후
`.moai/specs/SPEC-RC522-001/spec.md` 의 제목 다음 줄에 다른 SPEC 들과 동일
형식의 schema migration 배너를 추가한다.

## 사전 조건

```bash
# main 에 PR #2 가 머지됐는지 확인
git fetch origin main
git log origin/main --oneline | grep -i "RC522-001" | head -3
ls .moai/specs/SPEC-RC522-001/spec.md  # 파일 존재 확인
```

## 적용 순서

### 옵션 A — 신규 브랜치에서 패치 (권장)

```bash
git fetch origin main
git checkout -b chore/spec-rc522-001-migration-banner origin/main

# 배너 삽입
python3 - <<'PY'
from pathlib import Path
p = Path(".moai/specs/SPEC-RC522-001/spec.md")
src = p.read_text(encoding="utf-8")
banner = """
> **📌 Schema Migration Note (2026-04-19)**: 본 SPEC 는 RFID 펌웨어 (`firmware/conveyor_v5_serial/conveyor_v5_serial.ino` v1.5.1) 회귀 테스트만 다루며 DB schema 와 직접 결합되지 않는다. 다만 향후 본 회귀 스위트가 smartcast schema 의 `item.is_defective`, `insp_task_txn` 과 연동될 가능성이 있어 명시:
>
> - 현재 의존 (PR #2): `firmware/conveyor_v5_serial/`, `scripts/test_rc522_regression.py` (PostgreSQL 미사용)
> - 향후 통합 (별도 SPEC): RFID UID → `item.item_id` 매핑 시 `smartcast.item` 사용 가능
>
> 자세한 신규 schema 는 [SPEC-DB-V2-MIGRATION](../SPEC-DB-V2-MIGRATION/spec.md) 참조.
"""
# 첫 "## Overview" 직전에 배너 삽입 (다른 SPEC 패턴과 동일)
needle = "## Overview"
if banner.strip() in src:
    print("이미 배너 존재 — 스킵")
elif needle in src:
    src = src.replace(needle, banner.strip() + "\n\n" + needle, 1)
    p.write_text(src, encoding="utf-8")
    print(f"배너 삽입 완료 ({p})")
else:
    print(f"WARN: '## Overview' 마커 없음 — 수동 삽입 필요")
PY

git add .moai/specs/SPEC-RC522-001/spec.md
git commit -m "docs(spec): SPEC-RC522-001 에 schema migration 배너 추가

PR #2 머지 후속 — 다른 SPEC 들과 동일 형식의 배너로 RFID 회귀 스위트가
DB 와 직접 결합되지 않음을 명시 + 향후 smartcast item 연동 가능성 포인터 추가.
참조: SPEC-DB-V2-MIGRATION."
git push -u origin chore/spec-rc522-001-migration-banner
gh pr create --base main --head chore/spec-rc522-001-migration-banner \
  --title "docs(spec): SPEC-RC522-001 schema migration 배너" \
  --body "PR #2 머지 후속. SPEC-DB-V2-MIGRATION 매핑 가이드 포인터 추가."
```

### 옵션 B — 즉시 main 에서 sed (소규모, 직접 push 시)

```bash
# main 에 PR #2 가 머지된 직후
git checkout main && git pull --ff-only origin main

# 검증: 배너가 아직 없는지
grep -c "Schema Migration Note" .moai/specs/SPEC-RC522-001/spec.md  # 0 이어야 함

# sed in-place (macOS BSD sed 기준)
sed -i '' '/^## Overview/i\
> **📌 Schema Migration Note (2026-04-19)**: 본 SPEC 는 RFID 펌웨어 회귀 테스트만 다루며 DB schema 와 직접 결합되지 않는다. 다만 향후 RFID UID → `smartcast.item.item_id` 매핑 시 신규 schema 사용 가능. 매핑 표는 [SPEC-DB-V2-MIGRATION](../SPEC-DB-V2-MIGRATION/spec.md) 참조.\
\
' .moai/specs/SPEC-RC522-001/spec.md

git add -p .moai/specs/SPEC-RC522-001/spec.md  # diff 확인 후 stage
git commit -m "docs(spec): SPEC-RC522-001 schema migration 배너"
```

## 검증

```bash
head -10 .moai/specs/SPEC-RC522-001/spec.md
# "Schema Migration Note" 가 첫 페이지 헤더 직후에 보이면 성공
```

## 왜 배너 본문이 다른 SPEC 과 다른가

다른 SPEC (API/CTL/ORD/CASTING) 은 모두 schema 의 테이블을 직접 다뤘기 때문에
"orders → ord+ord_detail" 같은 테이블 매핑이 필요했다. 반면 SPEC-RC522-001 은
ESP32 펌웨어 + Python serial 회귀 테스트로 PostgreSQL 을 사용하지 않는다.

따라서 배너 내용은:
- 현재: "DB 와 직접 결합 없음" 명시
- 향후: smartcast.item 연동 가능성 포인터

이게 정직한 기록이며 미래 독자를 잘못된 매핑으로 호도하지 않는다.
