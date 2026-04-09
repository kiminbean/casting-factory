"""SQLite → PostgreSQL 데이터 마이그레이션 (일회성 스크립트).

사용:
    cd backend && source venv/bin/activate
    python scripts/migrate_sqlite_to_pg.py

동작:
    1. 기존 SQLite 파일에서 SQLAlchemy 모델 기반으로 모든 row 를 읽는다.
    2. DATABASE_URL (PG) 쪽 engine 으로 테이블을 create_all 한 후, FK 안전한 순서로 insert 한다.
    3. PG 쪽 테이블에 이미 데이터가 있으면 해당 테이블은 skip 한다 (idempotent).
    4. 시퀀스를 max(id)+1 로 재설정한다.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# .env.local 을 먼저 로드해야 database.py 가 PG URL 을 집는다.
from app.database import Base, DATABASE_URL  # noqa: E402
from sqlalchemy import create_engine, inspect, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

# 모든 모델을 import 해서 Base.metadata 에 등록
from app.models import models as _models  # noqa: E402,F401

SQLITE_URL = f"sqlite:///{BACKEND_DIR / 'casting_factory.db'}"


def main() -> int:
    if not DATABASE_URL.startswith("postgresql"):
        print(f"ERROR: DATABASE_URL is not PostgreSQL: {DATABASE_URL}")
        print("backend/.env.local 에 DATABASE_URL 설정 확인 필요")
        return 1

    print(f"Source : {SQLITE_URL}")
    print(f"Target : {DATABASE_URL.split('@')[-1]}")  # 비밀번호 숨김

    src_engine = create_engine(SQLITE_URL)
    dst_engine = create_engine(DATABASE_URL)

    print("\n[1/4] Target 쪽 테이블 create_all ...")
    Base.metadata.create_all(bind=dst_engine)

    SrcSession = sessionmaker(bind=src_engine)
    DstSession = sessionmaker(bind=dst_engine)
    src = SrcSession()
    dst = DstSession()

    # 의존성 순서 (FK parent 먼저)
    ordered_tables = Base.metadata.sorted_tables
    print(f"\n[2/4] {len(ordered_tables)} 테이블 마이그레이션 시작")

    total_copied = 0
    for table in ordered_tables:
        name = table.name
        src_count = src.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar() or 0
        dst_count = dst.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar() or 0

        if dst_count > 0:
            print(f"  [skip] {name}: PG 에 이미 {dst_count} rows 존재")
            continue
        if src_count == 0:
            print(f"  [----] {name}: source 비어있음")
            continue

        rows = src.execute(table.select()).mappings().all()
        if not rows:
            continue
        dst.execute(table.insert(), [dict(r) for r in rows])
        dst.commit()
        print(f"  [ok  ] {name}: {len(rows)} rows")
        total_copied += len(rows)

    print(f"\n[3/4] 총 {total_copied} rows 복사 완료")

    # 4. Sequence 재설정 (auto-increment PK 가 있는 테이블)
    print("\n[4/4] Sequence 재설정")
    with dst_engine.connect() as conn:
        insp = inspect(dst_engine)
        for table in ordered_tables:
            pks = [c for c in table.primary_key.columns if c.autoincrement]
            if not pks:
                continue
            pk = pks[0]
            # PG 가 자동 생성한 시퀀스 이름: {table}_{col}_seq
            seq_name = f"{table.name}_{pk.name}_seq"
            exists = conn.execute(
                text("SELECT 1 FROM pg_class WHERE relname = :n AND relkind = 'S'"),
                {"n": seq_name},
            ).scalar()
            if not exists:
                continue
            max_id = conn.execute(
                text(f'SELECT COALESCE(MAX("{pk.name}"), 0) FROM "{table.name}"')
            ).scalar() or 0
            conn.execute(text(f"SELECT setval('{seq_name}', {max_id + 1}, false)"))
            print(f"  [seq ] {seq_name} → {max_id + 1}")
        conn.commit()

    src.close()
    dst.close()
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
