"""Tests for the cache service — uses mocked Divine-Pride responses."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.models import Map, MapSpawn, Monster
from app.services.cache import get_monster, get_map, _is_stale


# ── Staleness check ──────────────────────────────────────────────────────────


class TestIsStaleness:
    def test_fresh_record(self):
        fetched = datetime.now(timezone.utc) - timedelta(hours=1)
        assert _is_stale(fetched) is False

    def test_stale_record(self):
        fetched = datetime.now(timezone.utc) - timedelta(hours=25)
        assert _is_stale(fetched) is True

    def test_naive_datetime_treated_as_utc(self):
        fetched = datetime.utcnow() - timedelta(hours=25)
        assert _is_stale(fetched) is True


# ── Monster cache ────────────────────────────────────────────────────────────

MOCK_MONSTER_DATA = {
    "id": 1002,
    "name": "Poring",
    "level": 1,
    "hp": 50,
    "base_exp": 2,
    "job_exp": 1,
    "atk_min": 7,
    "atk_max": 10,
    "defense": 0,
    "magic_defense": 5,
    "element": "Water1",
    "race": "Plant",
    "size": "Medium",
}


class TestGetMonster:
    @pytest.mark.asyncio
    async def test_fetches_and_caches_monster(self, db_session):
        with patch(
            "app.services.cache.divine_pride.fetch_monster",
            new_callable=AsyncMock,
            return_value=MOCK_MONSTER_DATA,
        ):
            monster = await get_monster(db_session, 1002)
            assert monster.id == 1002
            assert monster.name == "Poring"
            assert monster.hp == 50

    @pytest.mark.asyncio
    async def test_returns_cached_monster_without_api_call(self, db_session):
        # Pre-populate cache
        cached = Monster(**MOCK_MONSTER_DATA, fetched_at=datetime.now(timezone.utc))
        db_session.add(cached)
        await db_session.commit()

        with patch(
            "app.services.cache.divine_pride.fetch_monster",
            new_callable=AsyncMock,
        ) as mock_fetch:
            monster = await get_monster(db_session, 1002)
            mock_fetch.assert_not_called()
            assert monster.name == "Poring"


# ── Map cache ────────────────────────────────────────────────────────────────

MOCK_MAP_DATA = {
    "id": "prt_fild01",
    "name": "Prontera Field 01",
    "spawns": [
        {"monster_id": 1002, "amount": 50},
        {"monster_id": 1113, "amount": 30},
    ],
}

MOCK_MONSTER_1113 = {
    "id": 1113,
    "name": "Lunatic",
    "level": 3,
    "hp": 60,
    "base_exp": 6,
    "job_exp": 2,
    "atk_min": 9,
    "atk_max": 12,
    "defense": 0,
    "magic_defense": 0,
    "element": "Neutral1",
    "race": "Brute",
    "size": "Small",
}


class TestGetMap:
    @pytest.mark.asyncio
    async def test_fetches_and_caches_map_with_spawns(self, db_session):
        async def mock_fetch_monster(monster_id):
            if monster_id == 1002:
                return MOCK_MONSTER_DATA
            return MOCK_MONSTER_1113

        with (
            patch(
                "app.services.cache.divine_pride.fetch_map",
                new_callable=AsyncMock,
                return_value=MOCK_MAP_DATA,
            ),
            patch(
                "app.services.cache.divine_pride.fetch_monster",
                new_callable=AsyncMock,
                side_effect=mock_fetch_monster,
            ),
        ):
            map_obj = await get_map(db_session, "prt_fild01")
            assert map_obj.id == "prt_fild01"
            assert map_obj.name == "Prontera Field 01"
            assert len(map_obj.spawns) == 2
            amounts = {s.monster_id: s.amount for s in map_obj.spawns}
            assert amounts[1002] == 50
            assert amounts[1113] == 30
