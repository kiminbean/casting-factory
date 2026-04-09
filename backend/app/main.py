import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import DATABASE_URL, Base, SessionLocal, engine
from app.routes import alerts, logistics, orders, production, quality, schedule, websocket
from app.seed import seed_database

# SQLite 전용 초기화 경로 (PG 전환 후에는 사용되지 않음)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.path.join(_BASE_DIR, "casting_factory.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # SQLite 사용 시에만 파일을 지우고 재시드한다 (개발 편의).
    # PostgreSQL 은 스키마/데이터를 보존하고 create_all + idempotent seed 만 실행.
    if DATABASE_URL.startswith("sqlite") and os.path.exists(_DB_PATH):
        engine.dispose()
        os.remove(_DB_PATH)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown: 연결 정리는 SQLAlchemy 가 처리


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
app.include_router(production.router)
app.include_router(quality.router)
app.include_router(logistics.router)
app.include_router(alerts.router)
app.include_router(schedule.router)

# WebSocket router
app.include_router(websocket.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "casting-factory-api"}
