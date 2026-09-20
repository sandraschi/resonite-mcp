"""Unit tests for world_builder (pure layout functions, no live session)."""

import pytest

from resonite_mcp.world_builder import FURNITURE, SIZES, STYLES, layout, presets_payload


def test_presets_payload_shape():
    payload = presets_payload()
    assert {s["id"] for s in payload["styles"]} == set(STYLES)
    assert {s["id"] for s in payload["sizes"]} == set(SIZES)
    assert {f["id"] for f in payload["furniture"]} == set(FURNITURE)
    defaults = payload["defaults"]
    assert defaults["style"] in STYLES
    assert defaults["size"] in SIZES
    assert set(defaults["furniture"]) <= set(FURNITURE)
    for style in payload["styles"]:
        assert len(style["swatches"]) == 6
        assert all(s.startswith("rgb(") for s in style["swatches"])


def test_palettes_are_valid_rgba():
    for sid, style in STYLES.items():
        for key in ("floor", "wall", "trim", "fabric", "accent", "glow", "wood"):
            color = style[key]
            assert set(color) == {"r", "g", "b", "a"}, (sid, key)
            assert all(isinstance(v, float) and 0.0 <= v <= 1.0 for v in color.values()), (sid, key)


def test_shell_piece_counts():
    cosy, warnings = layout("loft", "cosy", [])
    assert len(cosy) == 10  # floor, ceiling, 5 wall segs, 3 door trims
    assert warnings == []
    hall, _ = layout("loft", "hall", [])
    assert len(hall) == 14  # shell + 4 pillars
    names = [p.name for p in cosy]
    assert names[0] == "Floor"
    assert "DoorTrimTop" in names


def test_furniture_adds_pieces():
    base, _ = layout("tea", "hall", [])
    dining, _ = layout("tea", "hall", ["dining"])
    assert len(dining) == len(base) + 25  # table 5 + 3 chairs x6 + pendant 2
    lounge, _ = layout("tea", "hall", ["lounge"])
    assert len(lounge) == len(base) + 13  # rug + sofa 4 + table 5 + lamp 3


def test_unknown_inputs():
    with pytest.raises(ValueError):
        layout("nope", "hall", [])
    with pytest.raises(ValueError):
        layout("loft", "nope", [])
    pieces, warnings = layout("loft", "hall", ["dining", "bogus"])
    assert any("bogus" in w for w in warnings)
    assert len(pieces) > 0


def test_pieces_have_sane_geometry():
    pieces, _ = layout("tavern", "grand", ["dining", "lounge", "sleep", "work"])
    assert len(pieces) > 40
    for piece in pieces:
        assert all(v > 0 for v in piece.size), piece.name
        assert piece.color in STYLES["tavern"]
