"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routers import maps, monsters
from app.schemas import HealthResponse
from app.services.divine_pride import divine_pride


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup, close HTTP client on shutdown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await divine_pride.close()
    await engine.dispose()


app = FastAPI(
    title="RO Leveling Optimizer",
    description="Ragnarok Online map leveling advisor powered by Divine-Pride data.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the React frontend to call the API during local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(monsters.router, prefix="/api")
app.include_router(maps.router, prefix="/api")


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
async def health():
    return HealthResponse()
