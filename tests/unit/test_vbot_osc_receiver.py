"""Tests for vBot OSC receiver spec."""

from __future__ import annotations

from resonite_mcp.utils.vbot_osc_receiver import (
    get_vbot_receiver_spec,
    list_vbot_types,
    robot_address,
)


def test_list_vbot_types_includes_mechazilla() -> None:
    catalog = list_vbot_types()
    ids = {t["id"] for t in catalog["types"]}
    assert "yahboom" in ids
    assert "mechazilla" in ids
    assert "godzilla" in ids


def test_receiver_spec_addresses() -> None:
    spec = get_vbot_receiver_spec(robot_id="vbot_yahboom_01", robot_type="yahboom")
    assert spec["addresses"]["move"]["address"] == "/robot/vbot_yahboom_01/move"
    assert len(spec["test_sequence"]) >= 4


def test_robot_address_helper() -> None:
    assert robot_address("vbot_mechazilla_01", "head") == "/robot/vbot_mechazilla_01/head"
