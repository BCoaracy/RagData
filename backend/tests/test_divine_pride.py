"""Tests for the Divine-Pride API client — parsing logic only (no real HTTP)."""

from app.services.divine_pride import _parse_element, RACES, SIZES


class TestParseElement:
    def test_neutral(self):
        assert _parse_element(0) == "Neutral1"

    def test_fire_level_1(self):
        # Fire = element_id 3, level 1 → raw = 20*1 + 3 = 23
        result = _parse_element(23)
        assert result.startswith("Fire")

    def test_water_level_2(self):
        # Water = element_id 1, level 2 → raw = 20*2 + 1 = 41
        result = _parse_element(41)
        assert result.startswith("Water")

    def test_undead_level_4(self):
        # Undead = element_id 9, level 4 → raw = 20*4 + 9 = 89
        result = _parse_element(89)
        assert result.startswith("Undead")


class TestLookupTables:
    def test_all_races_present(self):
        assert len(RACES) == 10

    def test_all_sizes_present(self):
        assert len(SIZES) == 3
        assert SIZES[0] == "Small"
        assert SIZES[1] == "Medium"
        assert SIZES[2] == "Large"
