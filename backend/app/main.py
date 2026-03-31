from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routes import alerts, logistics, orders, production, quality, websocket
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all tables and run seed data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown: nothing to clean up for SQLite


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
app.include_router(production.router)
app.include_router(quality.router)
app.include_router(logistics.router)
app.include_router(alerts.router)

# WebSocket router
app.include_router(websocket.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "casting-factory-api"}
