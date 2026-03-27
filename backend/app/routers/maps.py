"""Map API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import MapSchema, SpawnEntry
from app.services.cache import get_map

router = APIRouter(prefix="/maps", tags=["maps"])


@router.get("/{map_id}", response_model=MapSchema)
async def read_map(map_id: str, db: AsyncSession = Depends(get_db)):
    """Get a map with its monster spawns. Data is cached locally."""
    try:
        map_obj = await get_map(db, map_id)
        return MapSchema(
            id=map_obj.id,
            name=map_obj.name,
            fetched_at=map_obj.fetched_at,
            spawns=[
                SpawnEntry(
                    monster_id=s.monster_id,
                    monster_name=s.monster.name if s.monster else f"#{s.monster_id}",
                    amount=s.amount,
                )
                for s in map_obj.spawns
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch map: {exc}") from exc
