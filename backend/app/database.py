"""Database engine and session factory.

PostgreSQL 16 + TimescaleDB가 운영 DB. 개발 편의를 위해 DATABASE_URL 이 설정되지 않은
경우에 한해 SQLite 파일로 폴백한다. 실제 배포 환경에서는 반드시 PostgreSQL 을 사용할 것.

환경 변수:
    DATABASE_URL - e.g. "postgresql+psycopg://user:pass@localhost:5432/casting_factory"
                   or   "sqlite:///./casting_factory.db"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# @MX:NOTE: PostgreSQL 이 기본, SQLite 는 개발 폴백 (Phase 1 부터 PG 사용)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_SQLITE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'casting_factory.db')}"


def _load_env_local() -> None:
    """backend/.env.local 파일이 있으면 단순 KEY=VALUE 를 os.environ 에 주입.

    python-dotenv 의존성 없이 stdlib 로 처리. 이미 환경변수가 설정되어 있으면 덮어쓰지 않는다.
    """
    env_path = Path(BASE_DIR) / ".env.local"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_local()
DATABASE_URL: str = os.environ.get("DATABASE_URL", _DEFAULT_SQLITE_URL)


def _build_engine(url: str) -> Engine:
    """Create SQLAlchemy engine with driver-specific options."""
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
    # PostgreSQL (or other network DB) - connection pooling
    return create_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False,
    )


engine: Engine = _build_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: provide a database session per-request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
