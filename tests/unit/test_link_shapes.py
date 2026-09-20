"""Unit tests for ResoniteLink response shapes and dashboard helpers.

Covers the envelope-unwrapping layer (protocol 0.13.1, live-researched
2026-09-18/19): slot fields arrive as {"value": ..., "id": ...} and must
never be treated as plain values. Uses stub clients, no network.
"""

import asyncio

import pytest

from resonite_mcp.resonite_link import (
    build_map_nodes,
    find_worn_avatars,
    parse_username,
    rl_unwrap,
    summarize_node,
    summarize_slot,
)


def env(value):
    return {"value": value, "id": "Reso_X"}


def test_rl_unwrap_envelope():
    assert rl_unwrap({"value": "World", "id": "Reso_1"}) == "World"
    assert rl_unwrap({"value": None, "id": "Reso_1"}, "dflt") == "dflt"
    assert rl_unwrap(None, "dflt") == "dflt"
    assert rl_unwrap("plain") == "plain"
    # Reference members (no value key) pass through untouched.
    ref = {"$type": "reference", "targetId": "Reso_9"}
    assert rl_unwrap(ref) is ref


def test_summarize_slot_unwraps():
    slot = {
        "id": "Reso_45",
        "name": env("World"),
        "isActive": env(True),
        "position": {"value": {"x": 1.0, "y": 2.0, "z": 3.0}, "id": "Reso_P"},
        "rotation": {"value": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}, "id": "Reso_R"},
        "scale": {"value": {"x": 1.0, "y": 1.0, "z": 1.0}, "id": "Reso_S"},
    }
    s = summarize_slot(slot)
    assert s == {
        "refId": "Reso_45",
        "name": "World",
        "active": True,
        "position": {"x": 1.0, "y": 2.0, "z": 3.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
        "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
    }


def test_summarize_slot_degrades_gracefully():
    s = summarize_slot(None)
    assert s["name"] == "Unknown"
    assert s["position"] == {"x": 0.0, "y": 0.0, "z": 0.0}
    assert build_map_nodes(None) == []
    assert build_map_nodes("nope") == []


def test_build_map_nodes_expands_users():
    children = [
        {"id": "W", "name": env("World"), "position": env({"x": 0, "y": 0, "z": 0})},
        {
            "id": "U",
            "name": env("Users"),
            "position": env({"x": 0, "y": 0, "z": 0}),
            "children": [
                {
                    "id": "U1",
                    "name": env("User <noparse=8>sanschip (ID2E00)"),
                    "position": env({"x": 1.0, "y": 2.0, "z": 3.0}),
                },
                {
                    "id": "U2",
                    "name": env("Mirror"),
                    "position": env({"x": 2.0, "y": 1.0, "z": 0.0}),
                },
            ],
        },
        {"id": "M", "name": env("UserManual"), "position": env({"x": 0, "y": 0, "z": 0})},
    ]
    nodes = build_map_nodes(children)
    assert len(nodes) == 4
    by_id = {n["id"]: n for n in nodes}
    assert by_id["W"]["type"] == "object"
    # Real user slot: clean display name, avatar type.
    assert by_id["U1"]["type"] == "avatar"
    assert by_id["U1"]["name"] == "sanschip"
    assert by_id["U1"]["position"] == {"x": 1.0, "y": 2.0, "z": 3.0}
    # Parked non-user slot under Users: object, raw name kept.
    assert by_id["U2"]["type"] == "object"
    assert by_id["U2"]["name"] == "Mirror"
    # Substring "User" alone is not a user slot.
    assert by_id["M"]["type"] == "object"


def test_summarize_node_flattens_components():
    resp = {
        "data": {
            "id": "Reso_6D",
            "name": env("User X"),
            "isActive": env(True),
            "position": env({"x": 0, "y": 0, "z": 0}),
            "components": [
                {"id": "C1", "componentType": "[FrooxEngine]FrooxEngine.UserRoot"},
                "junk",
            ],
        }
    }
    node = summarize_node(resp)
    assert node["refId"] == "Reso_6D"
    assert node["components"] == [{"refId": "C1", "componentType": "[FrooxEngine]FrooxEngine.UserRoot"}]


def test_parse_username():
    assert parse_username("User <noparse=8>sanschip (ID2E00)") == "sanschip"
    assert parse_username("User Alice") == "Alice"
    assert parse_username("Bob") == "Bob"
    assert parse_username(None) is None


class StubClient:
    def __init__(self, root_children, slots):
        self._root = root_children
        self._slots = slots

    async def get_children(self, slot_id):
        assert slot_id == "Root"
        return self._root

    async def get_slot(self, slot_id, include_component_data=False, depth=0):
        return {"data": self._slots[slot_id]}


def _slot(sid, name, components=()):
    return {
        "id": sid,
        "name": env(name),
        "components": [{"id": f"{sid}-c{i}", "componentType": ct} for i, ct in enumerate(components)],
    }


def _user_tree(with_avatar_marker):
    root = [
        {"id": "W", "name": env("World"), "children": []},
        {
            "id": "U",
            "name": env("Users"),
            "children": [{"id": "U1", "name": env("User <noparse=8>sanschip (ID2E00)")}],
        },
        {"id": "A", "name": env("CoolAvatar"), "children": []},
    ]
    avatar_comps = (
        ["[FrooxEngine]FrooxEngine.BipedRig"] if with_avatar_marker else ["[FrooxEngine]FrooxEngine.StaticMesh"]
    )
    slots = {
        "W": _slot("W", "World"),
        "U": _slot("U", "Users"),
        "A": _slot("A", "CoolAvatar", avatar_comps),
        "U1": {
            "id": "U1",
            "name": env("User <noparse=8>sanschip (ID2E00)"),
            "components": [
                {
                    "id": "U1-am",
                    "componentType": "[FrooxEngine]FrooxEngine.CommonAvatar.AvatarManager",
                    "members": {"NameTagText": {"$type": "string", "value": "<b>sanschip</b>"}},
                }
            ],
        },
    }
    return root, slots


def test_find_worn_avatars_resolves():
    root, slots = _user_tree(with_avatar_marker=True)
    res = asyncio.run(find_worn_avatars(StubClient(root, slots)))
    assert len(res) == 1
    assert res[0]["username"] == "sanschip"
    assert res[0]["avatar"] == {"refId": "A", "name": "CoolAvatar"}


def test_find_worn_avatars_honest_unknown():
    root, slots = _user_tree(with_avatar_marker=False)
    res = asyncio.run(find_worn_avatars(StubClient(root, slots)))
    assert len(res) == 1
    assert res[0]["username"] == "sanschip"
    assert res[0]["avatar"] is None


def test_find_worn_avatars_no_users_container():
    root, slots = _user_tree(with_avatar_marker=True)
    res = asyncio.run(find_worn_avatars(StubClient([root[0]], slots)))
    assert res == []


def test_list_protoflux_presets_shape():
    from resonite_mcp.utils.protoflux_avatar_presets import (
        get_protoflux_preset,
        list_protoflux_presets,
    )

    catalog = list_protoflux_presets()
    assert catalog["count"] == len(catalog["presets"]) >= 11
    for entry in catalog["presets"]:
        assert {"id", "label", "description", "parameter_count"} <= set(entry)
        assert get_protoflux_preset(entry["id"])["label"] == entry["label"]


def test_stats_counts_distinct_worlds(monkeypatch):
    import resonite_mcp.http_functions as http_functions

    async def fake_sessions():
        return {
            "status": "ok",
            "sessions": [
                {"correspondingWorldId": {"recordId": "R1"}},
                {"correspondingWorldId": {"recordId": "R1"}},
                {"correspondingWorldId": {"recordId": "R2"}},
                {"correspondingWorldId": None},
            ],
        }

    monkeypatch.setattr(http_functions.rest_api, "resonite_rest_get_sessions", fake_sessions)
    http_functions._STATS_CACHE["data"] = None
    stats = asyncio.run(http_functions.resonite_stats_http())
    assert stats["sessions"] == 4
    assert stats["worlds"] == 2
    assert set(stats) == {"worlds", "avatars", "sessions", "scripts"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
