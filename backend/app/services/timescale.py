"""TimescaleDB 런타임 검출 + 시계열 집계 helper.

DB 서버에 timescaledb extension 이 있으면 hypertable 기반 time_bucket() 쿼리,
없으면 기본 GROUP BY date_trunc 로 폴백 (집계 동작은 동일, 성능만 차이).

검출 결과는 1회 캐시되어 매 요청마다 pg_extension 조회를 반복하지 않는다.
설치/제거 시 backend 재시작 필요.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.orm import Session


@lru_cache(maxsize=1)
def has_timescaledb() -> bool:
    """pg_extension 에 timescaledb 가 있는지 1회 검사 후 캐시."""
    from app.database import engine

    try:
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT extname FROM pg_extension WHERE extname = 'timescaledb' LIMIT 1"
            )).first()
            return row is not None
    except Exception:
        return False


def hourly_item_production(db: Session, hours: int = 24) -> list[dict]:
    """최근 N 시간 시간대별 item 생산 카운트.

    TimescaleDB 가 있으면 hypertable continuous aggregate (`item_hourly`) 사용,
    없으면 기본 date_trunc 쿼리.
    """
    since = datetime.now() - timedelta(hours=hours)
    if has_timescaledb():
        # continuous aggregate 가 미생성 상태일 수도 있어 try → 폴백
        try:
            rows = db.execute(text("""
                SELECT bucket, produced
                FROM smartcast.item_hourly
                WHERE bucket >= :since
                ORDER BY bucket
            """), {"since": since}).all()
            return [{"bucket": r.bucket.isoformat(), "produced": r.produced} for r in rows]
        except Exception:
            pass

    # 기본 폴백 — group by date_trunc('hour', updated_at)
    rows = db.execute(text("""
        SELECT date_trunc('hour', updated_at) AS bucket, COUNT(*) AS produced
        FROM smartcast.item
        WHERE updated_at >= :since
        GROUP BY bucket
        ORDER BY bucket
    """), {"since": since}).all()
    return [{"bucket": r.bucket.isoformat(), "produced": r.produced} for r in rows]


def weekly_item_production(db: Session, weeks: int = 8) -> list[dict]:
    """최근 N 주 주간 item 생산 카운트."""
    since = datetime.now() - timedelta(weeks=weeks)
    rows = db.execute(text("""
        SELECT date_trunc('week', updated_at) AS bucket, COUNT(*) AS produced
        FROM smartcast.item
        WHERE updated_at >= :since
        GROUP BY bucket
        ORDER BY bucket
    """), {"since": since}).all()
    return [{"bucket": r.bucket.date().isoformat(), "produced": r.produced} for r in rows]


def err_log_trend(db: Session, hours: int = 24) -> list[dict]:
    """equip + trans err_log 시간대별 발생 카운트."""
    since = datetime.now() - timedelta(hours=hours)
    rows = db.execute(text("""
        SELECT bucket, source, count
        FROM (
            SELECT date_trunc('hour', occured_at) AS bucket,
                   'equip'::text AS source,
                   COUNT(*) AS count
            FROM smartcast.equip_err_log
            WHERE occured_at >= :since
            GROUP BY bucket
            UNION ALL
            SELECT date_trunc('hour', occured_at) AS bucket,
                   'trans'::text AS source,
                   COUNT(*) AS count
            FROM smartcast.trans_err_log
            WHERE occured_at >= :since
            GROUP BY bucket
        ) sub
        ORDER BY bucket, source
    """), {"since": since}).all()
    return [{"bucket": r.bucket.isoformat(), "source": r.source, "count": r.count} for r in rows]
