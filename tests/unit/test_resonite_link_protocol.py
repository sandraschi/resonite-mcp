"""Wire-format regression tests for the ResoniteLink client (protocol 0.13.1).

These tests lock the REAL protocol shapes verified against upstream
Yellow-Dog-Man/ResoniteLink (Message.cs / Response.cs / websocket docs),
so future edits can't silently drift back to the pre-2026-07 fictional
format. No network involved: a fake WebSocket captures outbound JSON and
the tests resolve the pending futures with synthetic responses.
"""

import asyncio
import json

import pytest

from resonite_mcp.resonite_link import (
    DISCOVERY_PORT,
    PROTOCOL_TARGET,
    ResoniteLinkClient,
    ResoniteLinkError,
    _DiscoveryProtocol,
    rl_auto,
    rl_list,
    rl_ref,
    rl_value,
)


class FakeWS:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, raw: str):
        self.sent.append(json.loads(raw))

    async def close(self):
        pass


@pytest.fixture
def client():
    c = ResoniteLinkClient()
    c.ws = FakeWS()
    c.running = True
    return c


async def roundtrip(client, coro, **response_extra):
    """Drive one request: let it send, then resolve with a success response.

    Returns (result, sent_payload).
    """
    task = asyncio.ensure_future(coro)
    for _ in range(50):
        await asyncio.sleep(0)
        if client.ws.sent and client.ws.sent[-1]["messageId"] in client._pending:
            break
    sent = client.ws.sent[-1]
    fut = client._pending[sent["messageId"]]
    fut.set_result(
        {
            "$type": "response",
            "sourceMessageId": sent["messageId"],
            "success": True,
            "errorInfo": None,
            **response_extra,
        }
    )
    result = await task
    return result, sent


# ── Envelope ────────────────────────────────────────────────────────────────────


async def test_send_uses_dollar_type_and_message_id(client):
    _, sent = await roundtrip(client, client.request_session_data())
    assert sent["$type"] == "requestSessionData"
    assert isinstance(sent["messageId"], str) and sent["messageId"]
    assert "type" not in sent  # fictional pre-0.13 key must not reappear
    assert "id" not in sent


async def test_send_rejects_legacy_fictional_format(client):
    with pytest.raises(ResoniteLinkError, match=r"\$type"):
        await client._send({"type": "ReadField", "refId": "X"})


async def test_error_response_raises_with_error_info(client):
    task = asyncio.ensure_future(client.get_slot("Nope"))
    for _ in range(50):
        await asyncio.sleep(0)
        if client.ws.sent:
            break
    sent = client.ws.sent[-1]
    client._pending[sent["messageId"]].set_result(
        {
            "$type": "response",
            "sourceMessageId": sent["messageId"],
            "success": False,
            "errorInfo": "No such slot",
        }
    )
    with pytest.raises(ResoniteLinkError, match="No such slot"):
        await task


# ── Slots ───────────────────────────────────────────────────────────────────────


async def test_get_slot_shape(client):
    _, sent = await roundtrip(client, client.get_slot("Root", include_component_data=True, depth=-1))
    assert sent["$type"] == "getSlot"
    assert sent["slotId"] == "Root"
    assert sent["includeComponentData"] is True
    assert sent["depth"] == -1


async def test_add_slot_wraps_typed_values_and_returns_entity_id(client):
    result, sent = await roundtrip(
        client,
        client.add_slot(name="Hello", parent_id="Root", position={"x": 0, "y": 1.5, "z": 10}),
        **{"$type": "newEntityId", "entityId": "Reso_42"},
    )
    assert sent["$type"] == "addSlot"
    data = sent["data"]
    assert data["name"] == {"$type": "string", "value": "Hello"}
    assert data["parent"] == {"$type": "reference", "targetId": "Root"}
    assert data["position"] == {"$type": "float3", "value": {"x": 0, "y": 1.5, "z": 10}}
    assert result == "Reso_42"


async def test_add_slot_client_supplied_id_wins(client):
    result, sent = await roundtrip(
        client,
        client.add_slot(name="X", slot_id="MySDK_0"),
        **{"$type": "newEntityId", "entityId": "MySDK_0"},
    )
    assert sent["data"]["id"] == "MySDK_0"
    assert result == "MySDK_0"


async def test_update_slot_requires_id(client):
    with pytest.raises(ResoniteLinkError, match="mandatory"):
        await client.update_slot({"scale": rl_value("float3", {"x": 2, "y": 2, "z": 2})})


async def test_remove_slot_shape(client):
    _, sent = await roundtrip(client, client.remove_slot("MySDK_0"))
    assert sent == {"$type": "removeSlot", "slotId": "MySDK_0", "messageId": sent["messageId"]}


# ── Components ─────────────────────────────────────────────────────────────────


async def test_add_component_shape(client):
    result, sent = await roundtrip(
        client,
        client.add_component("MySDK_0", "[FrooxEngine]FrooxEngine.Grabbable", members={"Scalable": True}),
        **{"$type": "newEntityId", "entityId": "Reso_C1"},
    )
    assert sent["$type"] == "addComponent"
    assert sent["containerSlotId"] == "MySDK_0"
    assert sent["data"]["componentType"] == "[FrooxEngine]FrooxEngine.Grabbable"
    assert sent["data"]["members"]["Scalable"] == {"$type": "bool", "value": True}
    assert result == "Reso_C1"


async def test_update_component_auto_encodes_members(client):
    _, sent = await roundtrip(client, client.update_component("Reso_C1", {"Scalable": False}))
    assert sent["$type"] == "updateComponent"
    assert sent["data"]["id"] == "Reso_C1"
    assert sent["data"]["members"]["Scalable"] == {"$type": "bool", "value": False}


async def test_set_component_value_explicit_type(client):
    _, sent = await roundtrip(
        client, client.set_component_value("C1", "TintColor", {"r": 1, "g": 0, "b": 0, "a": 1}, "colorX")
    )
    assert sent["data"]["members"]["TintColor"] == {
        "$type": "colorX",
        "value": {"r": 1, "g": 0, "b": 0, "a": 1},
    }


# ── Sync methods (0.11.0+) ─────────────────────────────────────────────────────


async def test_call_sync_method_shape(client):
    _, sent = await roundtrip(
        client,
        client.call_sync_method("Reso_C1", "Jump", {"height": 2.0}),
        **{"$type": "methodResult", "result": None},
    )
    assert sent["$type"] == "callSyncMethod"
    assert sent["targetID"] == "Reso_C1"
    assert sent["methodName"] == "Jump"
    assert sent["arguments"]["height"] == {"$type": "float", "value": 2.0}


async def test_call_static_sync_method_shape(client):
    _, sent = await roundtrip(client, client.call_static_sync_method("SomeType", "DoThing"))
    assert sent["$type"] == "callStaticSyncMethod"
    assert sent["targetType"] == "SomeType"


# ── Reflection & batch ─────────────────────────────────────────────────────────


async def test_reflect_maps_to_real_messages(client):
    _, sent = await roundtrip(client, client.reflect())
    assert sent["$type"] == "getComponentTypeList"
    _, sent = await roundtrip(client, client.reflect("FrooxEngine.Grabbable"))
    assert sent["$type"] == "getComponentDefinition"
    assert sent["componentType"] == "FrooxEngine.Grabbable"
    assert sent["flattened"] is True


async def test_batch_requires_dollar_type_per_operation(client):
    with pytest.raises(ResoniteLinkError, match=r"\$type"):
        await client.batch([{"type": "AddSlot", "refId": "Root"}])


async def test_batch_shape(client):
    ops = [{"$type": "removeSlot", "slotId": "A"}, {"$type": "removeSlot", "slotId": "B"}]
    _, sent = await roundtrip(client, client.batch(ops), **{"$type": "batchResponse"})
    assert sent["$type"] == "dataModelOperationBatch"
    assert sent["operations"] == ops


# ── Honest not-implemented paths ───────────────────────────────────────────────


async def test_write_field_raises_with_guidance(client):
    with pytest.raises(ResoniteLinkError, match="update_component"):
        await client.write_field("X", 1.0)


async def test_import_file_raises_not_implemented(client):
    with pytest.raises(ResoniteLinkError, match="importFile does not exist"):
        await client.import_file(file_path="a.vrm", target_slot_id="Root")


# ── Value encoding ─────────────────────────────────────────────────────────────


def test_rl_auto_primitives():
    assert rl_auto(True) == {"$type": "bool", "value": True}
    assert rl_auto(3) == {"$type": "int", "value": 3}
    assert rl_auto(1.5) == {"$type": "float", "value": 1.5}
    assert rl_auto("hi") == {"$type": "string", "value": "hi"}
    assert rl_auto({"x": 1, "y": 2, "z": 3}) == {"$type": "float3", "value": {"x": 1, "y": 2, "z": 3}}
    assert rl_auto(rl_ref("Root")) == {"$type": "reference", "targetId": "Root"}


def test_rl_auto_rejects_unknown_shapes():
    with pytest.raises(ResoniteLinkError):
        rl_auto({"foo": 1})
    with pytest.raises(ResoniteLinkError):
        rl_auto([1, 2, 3])


# ── LAN discovery (0.12.0+) ────────────────────────────────────────────────────


def test_discovery_protocol_parses_announcements():
    assert DISCOVERY_PORT == 12512
    proto = _DiscoveryProtocol()
    announce = json.dumps({"sessionName": "My World", "sessionID": "S-1", "linkPort": 40123}).encode()
    proto.datagram_received(announce, ("192.168.1.7", 55555))
    proto.datagram_received(announce, ("192.168.1.7", 55556))  # re-announce dedupes
    proto.datagram_received(b"not json", ("192.168.1.9", 1))  # ignored
    proto.datagram_received(json.dumps({"noId": True}).encode(), ("192.168.1.9", 1))  # ignored
    assert len(proto.sessions) == 1
    session = proto.sessions["S-1"]
    assert session["sessionName"] == "My World"
    assert session["linkPort"] == 40123
    assert session["host"] == "192.168.1.7"


def test_protocol_target_constant():
    assert PROTOCOL_TARGET == "0.13.1"


# ── Asset import (wrapped 2026-07-18 from the Phase 0 spike scripts) ───────────
# See mcp-central-docs/projects/RESONITE_PHASE0_HANDOFF.md for the live session
# these shapes were verified against.


async def drive(client, coro, responses):
    """Drive a coroutine that issues several SEQUENTIAL awaited sends.

    responses: one dict of response-envelope extras per expected send, in
    order. Returns (final_result, [sent_payload, ...]).
    """
    task = asyncio.ensure_future(coro)
    sent_payloads: list[dict] = []
    for resp_extra in responses:
        for _ in range(50):
            await asyncio.sleep(0)
            if len(client.ws.sent) > len(sent_payloads):
                break
        sent = client.ws.sent[len(sent_payloads)]
        sent_payloads.append(sent)
        fut = client._pending[sent["messageId"]]
        fut.set_result(
            {
                "$type": "response",
                "sourceMessageId": sent["messageId"],
                "success": True,
                "errorInfo": None,
                **resp_extra,
            }
        )
    result = await task
    return result, sent_payloads


def test_rl_list_shape():
    assert rl_list([rl_ref("Reso_1"), rl_ref("Reso_2")]) == {
        "$type": "list",
        "elements": [
            {"$type": "reference", "targetId": "Reso_1"},
            {"$type": "reference", "targetId": "Reso_2"},
        ],
    }


async def test_import_mesh_json_shape_and_return(client):
    vertices = [{"position": {"x": 0, "y": 0, "z": 0}}]
    submeshes = [{"$type": "triangles", "triangles": [{"vertex0Index": 0, "vertex1Index": 0, "vertex2Index": 0}]}]
    result, sent = await roundtrip(
        client,
        client.import_mesh_json(vertices, submeshes),
        **{"$type": "assetData", "assetURL": "local://abc/xyz.meshx"},
    )
    assert sent["$type"] == "importMeshJSON"
    assert sent["vertices"] == vertices
    assert sent["submeshes"] == submeshes
    assert "bones" not in sent
    assert "blendshapes" not in sent
    assert result == "local://abc/xyz.meshx"


async def test_import_mesh_json_includes_optional_bones_and_blendshapes(client):
    bones = [{"name": "root"}]
    blendshapes = [{"name": "smile"}]
    _, sent = await roundtrip(
        client,
        client.import_mesh_json([], [], bones=bones, blendshapes=blendshapes),
        **{"$type": "assetData", "assetURL": "local://x.meshx"},
    )
    assert sent["bones"] == bones
    assert sent["blendshapes"] == blendshapes


async def test_import_mesh_json_raises_without_asset_url(client):
    task = asyncio.ensure_future(client.import_mesh_json([], []))
    for _ in range(50):
        await asyncio.sleep(0)
        if client.ws.sent:
            break
    sent = client.ws.sent[-1]
    client._pending[sent["messageId"]].set_result(
        {"$type": "response", "sourceMessageId": sent["messageId"], "success": True, "errorInfo": None}
    )
    with pytest.raises(ResoniteLinkError, match="no assetURL"):
        await task


async def test_import_mesh_raw_not_implemented(client):
    with pytest.raises(ResoniteLinkError, match="binary"):
        await client.import_mesh_raw()


async def test_import_texture_file_shape(client):
    result, sent = await roundtrip(
        client,
        client.import_texture_file("C:/textures/wood.png"),
        **{"$type": "assetData", "assetURL": "local://tex/wood.png"},
    )
    assert sent == {
        "$type": "importTexture2DFile",
        "filePath": "C:/textures/wood.png",
        "messageId": sent["messageId"],
    }
    assert result == "local://tex/wood.png"


async def test_spawn_mesh_without_color_wires_static_mesh_and_renderer(client):
    vertices = [{"position": {"x": 0, "y": 0, "z": 0}}]
    submeshes = [{"$type": "triangles", "triangles": []}]
    result, sent = await drive(
        client,
        client.spawn_mesh(vertices, submeshes, position={"x": 0, "y": 1.5, "z": 2}, name="phase0-cube"),
        [
            {"$type": "assetData", "assetURL": "local://cube/asset.meshx"},  # importMeshJSON
            {"$type": "newEntityId", "entityId": "Reso_SLOT"},  # addSlot
            {"$type": "newEntityId", "entityId": "Reso_SM"},  # addComponent StaticMesh
            {"$type": "newEntityId", "entityId": "Reso_MR"},  # addComponent MeshRenderer
        ],
    )
    assert sent[0]["$type"] == "importMeshJSON"
    assert sent[1]["$type"] == "addSlot"
    assert sent[1]["data"]["name"] == {"$type": "string", "value": "phase0-cube"}
    assert sent[2]["$type"] == "addComponent"
    assert sent[2]["data"]["componentType"] == "[FrooxEngine]FrooxEngine.StaticMesh"
    assert sent[2]["data"]["members"]["URL"] == {"$type": "Uri", "value": "local://cube/asset.meshx"}
    assert sent[3]["$type"] == "addComponent"
    assert sent[3]["data"]["componentType"] == "[FrooxEngine]FrooxEngine.MeshRenderer"
    assert sent[3]["data"]["members"]["Mesh"] == {"$type": "reference", "targetId": "Reso_SM"}
    assert result == {
        "slot_id": "Reso_SLOT",
        "asset_url": "local://cube/asset.meshx",
        "static_mesh_id": "Reso_SM",
        "renderer_id": "Reso_MR",
    }


async def test_spawn_mesh_with_color_wires_material(client):
    orange = {"r": 1.0, "g": 0.45, "b": 0.05, "a": 1.0}
    result, sent = await drive(
        client,
        client.spawn_mesh([], [], color=orange),
        [
            {"$type": "assetData", "assetURL": "local://c.meshx"},  # importMeshJSON
            {"$type": "newEntityId", "entityId": "Reso_SLOT"},  # addSlot
            {"$type": "newEntityId", "entityId": "Reso_SM"},  # addComponent StaticMesh
            {"$type": "newEntityId", "entityId": "Reso_MR"},  # addComponent MeshRenderer
            {"$type": "newEntityId", "entityId": "Reso_MAT"},  # addComponent PBS_Metallic
            {},  # updateComponent Materials
        ],
    )
    assert sent[4]["data"]["componentType"] == "[FrooxEngine]FrooxEngine.PBS_Metallic"
    assert sent[4]["data"]["members"]["AlbedoColor"] == {"$type": "colorX", "value": orange}
    assert sent[5]["$type"] == "updateComponent"
    assert sent[5]["data"]["id"] == "Reso_MR"
    assert sent[5]["data"]["members"]["Materials"] == {
        "$type": "list",
        "elements": [{"$type": "reference", "targetId": "Reso_MAT"}],
    }
    assert result["material_id"] == "Reso_MAT"
