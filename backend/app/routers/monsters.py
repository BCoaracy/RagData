"""Monster API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import MonsterSchema
from app.services.cache import get_monster

router = APIRouter(prefix="/monsters", tags=["monsters"])


@router.get("/{monster_id}", response_model=MonsterSchema)
async def read_monster(monster_id: int, db: AsyncSession = Depends(get_db)):
    """Get a monster by its Divine-Pride ID. Data is cached locally."""
    try:
        monster = await get_monster(db, monster_id)
        return monster
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch monster: {exc}") from exc
