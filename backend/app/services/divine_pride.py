"""Async HTTP client wrapper for the Divine-Pride API.

Maps the raw JSON responses to flat dicts consumable by the cache/ORM layer.

Divine-Pride endpoints used:
  GET /api/database/Monster/{id}?apiKey={key}
  GET /api/database/Map/{id}?apiKey={key}
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# ── Element & Race lookup tables ─────────────────────────────────────────────
# Divine-Pride encodes element as an int (element_level * 10 + element_id).
ELEMENTS: dict[int, str] = {
    0: "Neutral",
    1: "Water",
    2: "Earth",
    3: "Fire",
    4: "Wind",
    5: "Poison",
    6: "Holy",
    7: "Shadow",
    8: "Ghost",
    9: "Undead",
}

RACES: dict[int, str] = {
    0: "Formless",
    1: "Undead",
    2: "Brute",
    3: "Plant",
    4: "Insect",
    5: "Fish",
    6: "Demon",
    7: "Demi-Human",
    8: "Angel",
    9: "Dragon",
}

SIZES: dict[int, str] = {
    0: "Small",
    1: "Medium",
    2: "Large",
}


def _parse_element(raw: int) -> str:
    """Convert Divine-Pride element int to a readable string like 'Fire2'."""
    if raw == 0:
        return "Neutral1"
    element_id = raw % 10
    element_level = raw // 20  # DP formula quirk
    name = ELEMENTS.get(element_id, f"Unknown({element_id})")
    return f"{name}{element_level}"


class DivinePrideClient:
    """Thin async wrapper around the Divine-Pride REST API."""

    def __init__(self) -> None:
        self._base = settings.divine_pride_base_url.rstrip("/")
        self._key = settings.divine_pride_api_key
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    # ── Raw fetchers ─────────────────────────────────────────────────────

    async def _get(self, path: str) -> dict[str, Any]:
        url = f"{self._base}{path}"
        params = {"apiKey": self._key}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    # ── Public API ───────────────────────────────────────────────────────

    async def fetch_monster(self, monster_id: int) -> dict[str, Any]:
        """Fetch a single monster and return a normalized dict."""
        raw = await self._get(f"/Monster/{monster_id}")
        stats = raw.get("stats", {})
        return {
            "id": raw["id"],
            "name": raw.get("name", f"Monster#{raw['id']}"),
            "level": stats.get("level", 0),
            "hp": stats.get("health", 0),
            "base_exp": stats.get("baseExperience", 0),
            "job_exp": stats.get("jobExperience", 0),
            "atk_min": stats.get("atk", {}).get("minimum", 0) if isinstance(stats.get("atk"), dict) else stats.get("attack", 0),
            "atk_max": stats.get("atk", {}).get("maximum", 0) if isinstance(stats.get("atk"), dict) else stats.get("attack", 0),
            "defense": stats.get("defense", 0),
            "magic_defense": stats.get("magicDefense", 0),
            "element": _parse_element(stats.get("element", 0)),
            "race": RACES.get(stats.get("race", 0), "Formless"),
            "size": SIZES.get(stats.get("scale", 1), "Medium"),
        }

    async def fetch_map(self, map_id: str) -> dict[str, Any]:
        """Fetch a single map and return a normalized dict with spawns."""
        raw = await self._get(f"/Map/{map_id}")
        spawns = []
        for entry in raw.get("spawn", []):
            monster_id = entry.get("mobId") or entry.get("id")
            amount = entry.get("amount", 0)
            if monster_id and amount > 0:
                spawns.append({"monster_id": monster_id, "amount": amount})
        return {
            "id": raw.get("mapname", map_id),
            "name": raw.get("name", map_id),
            "spawns": spawns,
        }


# Module-level singleton
divine_pride = DivinePrideClient()
