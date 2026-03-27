"""Pydantic schemas for API request/response serialization."""

from datetime import datetime

from pydantic import BaseModel


# ── Monster ──────────────────────────────────────────────────────────────────


class MonsterSchema(BaseModel):
    id: int
    name: str
    level: int
    hp: int
    base_exp: int
    job_exp: int
    atk_min: int
    atk_max: int
    defense: int
    magic_defense: int
    element: str
    race: str
    size: str
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ── Map ──────────────────────────────────────────────────────────────────────


class SpawnEntry(BaseModel):
    monster_id: int
    monster_name: str
    amount: int

    model_config = {"from_attributes": True}


class MapSchema(BaseModel):
    id: str
    name: str
    fetched_at: datetime
    spawns: list[SpawnEntry] = []

    model_config = {"from_attributes": True}


# ── Health ───────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
