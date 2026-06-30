"""Smoke tests for new ResoniteLink, vBot, cloud vars, and Prefab tools."""

from __future__ import annotations


def test_resonite_link_tools_register() -> None:
    """Verify new ResoniteLink low-level tools are importable."""
    from resonite_mcp.tools.resonite_link import (
        resonite_link_add_component,
        resonite_link_add_slot,
        resonite_link_batch,
        resonite_link_destroy_slot,
        resonite_link_get_children,
        resonite_link_get_node,
        resonite_link_read_field,
        resonite_link_reflect,
        resonite_link_write_field,
    )

    assert callable(resonite_link_read_field)
    assert callable(resonite_link_write_field)
    assert callable(resonite_link_get_node)
    assert callable(resonite_link_get_children)
    assert callable(resonite_link_add_slot)
    assert callable(resonite_link_add_component)
    assert callable(resonite_link_destroy_slot)
    assert callable(resonite_link_reflect)
    assert callable(resonite_link_batch)


def test_vbot_tools_register() -> None:
    """Verify vBot tools are importable."""
    from resonite_mcp.tools.vbot import (
        resonite_vbot_head,
        resonite_vbot_list_types,
        resonite_vbot_move,
        resonite_vbot_spawn,
        resonite_vbot_stop,
    )

    assert callable(resonite_vbot_list_types)
    assert callable(resonite_vbot_spawn)
    assert callable(resonite_vbot_move)
    assert callable(resonite_vbot_head)
    assert callable(resonite_vbot_stop)


def test_prefab_cards_register() -> None:
    """Verify Prefab card tools are importable."""
    from resonite_mcp.tools.prefab_cards import (
        resonite_dashboard_card,
        resonite_inventory_card,
    )

    assert callable(resonite_dashboard_card)
    assert callable(resonite_inventory_card)


def test_cloud_var_tools_register() -> None:
    """Verify cloud variable tools are importable."""
    from resonite_mcp.tools.rest_api import (
        resonite_cloud_var_delete,
        resonite_cloud_var_get,
        resonite_cloud_var_list,
        resonite_cloud_var_set,
    )

    assert callable(resonite_cloud_var_list)
    assert callable(resonite_cloud_var_get)
    assert callable(resonite_cloud_var_set)
    assert callable(resonite_cloud_var_delete)


def test_friend_tools_register() -> None:
    """Verify friends/contacts tools are importable."""
    from resonite_mcp.tools.rest_api import (
        resonite_friend_presence,
        resonite_friend_requests,
        resonite_friends_list,
    )

    assert callable(resonite_friends_list)
    assert callable(resonite_friend_requests)
    assert callable(resonite_friend_presence)


def test_vbot_list_types() -> None:
    """Verify vBot type catalog."""

    # This is a sync function despite the async @server.tool decorator
    # The underlying data is static


def test_installation_detection() -> None:
    """Verify Resonite install detection."""
    from resonite_mcp.server import is_resonite_installed

    result = is_resonite_installed()
    assert isinstance(result, bool)
