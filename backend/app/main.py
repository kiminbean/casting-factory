import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routes import alerts, dashboard, logistics, orders, production, quality, schedule, websocket
from app.seed import seed_database
from app.services import fms_is_enabled, run_fms_sequencer

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # smartcast schema (Confluence 32342045 v59) 정착.
    # DDL 은 backend/scripts/create_tables_v2.sql 로 사전 적용됨 — create_all 은 보조.
    # search_path=smartcast,public 옵션이 DATABASE_URL 에 포함되어 있어 ORM 이 자동 사용.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # FMS_AUTOPLAY=1 환경에서만 자동 진행 시퀀서 실행 (실기 연동 시 OFF)
    sequencer_task: asyncio.Task | None = None
    if fms_is_enabled():
        # uvicorn logger 가 app.* 로거를 노출하지 않을 수 있어 print 도 함께 사용
        print("[FMS] FMS_AUTOPLAY=1 — sequencer 백그라운드 시작", flush=True)
        logger.info("FMS_AUTOPLAY=1 — sequencer 백그라운드 시작")
        sequencer_task = asyncio.create_task(run_fms_sequencer())
    else:
        print("[FMS] FMS_AUTOPLAY 비활성 — sequencer 미가동", flush=True)
        logger.info("FMS_AUTOPLAY 비활성 — sequencer 미가동 (실기 연동 모드)")

    yield

    # Shutdown
    if sequencer_task is not None:
        sequencer_task.cancel()
        try:
            await sequencer_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="주물공장 관제 API",
    description="Casting factory dashboard REST API and WebSocket service",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins for development with the Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routers
app.include_router(orders.router)
app.include_router(orders.products_router)
app.include_router(orders.load_classes_router)
app.include_router(production.router)
app.include_router(quality.router)
app.include_router(logistics.router)
app.include_router(alerts.router)
app.include_router(schedule.router)
app.include_router(dashboard.router)

# WebSocket router
app.include_router(websocket.router)

# Dev-only debug router (SPEC-AMR-001 FR-AMR-01-07)
# APP_ENV=development 이 아니면 등록하지 않음 → production 에서 404 반환
if os.environ.get("APP_ENV", "development").lower() == "development":
    from app.routes import debug  # noqa: E402  지연 import: dev 환경에서만 로드

    app.include_router(debug.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "casting-factory-api"}
