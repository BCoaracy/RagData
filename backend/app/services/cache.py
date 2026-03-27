"""Cache layer — checks SQLite for fresh data, fetches from Divine-Pride if stale."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Map, MapSpawn, Monster
from app.services.divine_pride import divine_pride

logger = logging.getLogger(__name__)


def _is_stale(fetched_at: datetime) -> bool:
    """Return True if the record is older than the configured TTL."""
    now = datetime.now(timezone.utc)
    ttl = timedelta(hours=settings.cache_ttl_hours)
    # Handle naive datetimes from SQLite
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    return (now - fetched_at) > ttl


# ── Monster cache ────────────────────────────────────────────────────────────


async def get_monster(db: AsyncSession, monster_id: int) -> Monster:
    """Return a cached Monster, refreshing from Divine-Pride if stale/missing."""
    monster = await db.get(Monster, monster_id)
    if monster and not _is_stale(monster.fetched_at):
        return monster

    logger.info("Fetching monster %d from Divine-Pride API", monster_id)
    data = await divine_pride.fetch_monster(monster_id)

    if monster:
        # Update existing record
        for key, value in data.items():
            setattr(monster, key, value)
        monster.fetched_at = datetime.now(timezone.utc)
    else:
        monster = Monster(**data, fetched_at=datetime.now(timezone.utc))
        db.add(monster)

    await db.commit()
    await db.refresh(monster)
    return monster


# ── Map cache ────────────────────────────────────────────────────────────────


async def get_map(db: AsyncSession, map_id: str) -> Map:
    """Return a cached Map with spawns, refreshing from Divine-Pride if stale/missing."""
    stmt = select(Map).where(Map.id == map_id)
    result = await db.execute(stmt)
    map_obj = result.scalar_one_or_none()

    if map_obj and not _is_stale(map_obj.fetched_at):
        # Eagerly load spawns
        await db.refresh(map_obj, ["spawns"])
        return map_obj

    logger.info("Fetching map '%s' from Divine-Pride API", map_id)
    data = await divine_pride.fetch_map(map_id)

    if map_obj:
        map_obj.name = data["name"]
        map_obj.fetched_at = datetime.now(timezone.utc)
        # Replace spawns
        await db.refresh(map_obj, ["spawns"])
        for spawn in list(map_obj.spawns):
            await db.delete(spawn)
    else:
        map_obj = Map(id=data["id"], name=data["name"], fetched_at=datetime.now(timezone.utc))
        db.add(map_obj)

    # Ensure monsters are cached before creating spawn records
    for spawn_data in data["spawns"]:
        await get_monster(db, spawn_data["monster_id"])
        map_spawn = MapSpawn(
            map_id=data["id"],
            monster_id=spawn_data["monster_id"],
            amount=spawn_data["amount"],
        )
        db.add(map_spawn)

    await db.commit()
    await db.refresh(map_obj, ["spawns"])
    return map_obj
