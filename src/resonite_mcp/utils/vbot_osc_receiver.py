"""Resonite-side OSC receiver spec for fleet vBots (vBoomy, vMechazilla, …)."""

from __future__ import annotations

from typing import Any

# Canonical OSC contract — keep in sync with teleoperator-mcp/docs/resonite/VBOOMY_OSC.md
DEFAULT_OSC_PORT = 9000

VBOOMY_SPAWN_ADDRESS = "/resonite/vbot/spawn"
VBOOMY_ESTOP_ADDRESS = "/fleet/emergency_stop"


def robot_address(robot_id: str, channel: str) -> str:
    """Build per-robot OSC address for move/stop/head/reset."""
    return f"/robot/{robot_id}/{channel}"


VBOT_ROBOT_TYPES: dict[str, dict[str, Any]] = {
    "yahboom": {
        "label": "vBoomy (Yahboom wheeled twin)",
        "drive": "holonomic_2d",
        "default_robot_id": "vbot_yahboom_01",
        "default_scale": 1.0,
        "notes": "Training twin for physical Boomy / Raspbot.",
    },
    "mechazilla": {
        "label": "vMechazilla (creative vBot)",
        "drive": "holonomic_2d",
        "default_robot_id": "vbot_mechazilla_01",
        "default_scale": 2.5,
        "notes": "Fun scale — same OSC contract; swap mesh in Resonite. IRL Mechazilla optional.",
    },
    "bumi": {
        "label": "vBumi (biped twin, planned rig)",
        "drive": "walk_yaw_pitch",
        "default_robot_id": "vbot_bumi_01",
        "default_scale": 1.0,
        "notes": "Future humanoid; head + walk channels same addresses, different ProtoFlux rig.",
    },
    "custom": {
        "label": "Custom vBot",
        "drive": "holonomic_2d",
        "default_robot_id": "vbot_custom_01",
        "default_scale": 1.0,
        "notes": "Any mesh — wire the same receiver graph.",
    },
    "godzilla": {
        "label": "Kaiju / tokusatsu scale",
        "drive": "holonomic_2d",
        "default_robot_id": "vbot_godzilla_01",
        "default_scale": 50.0,
        "notes": "Resonite handles city-block scale; prefer kinematic locomotion for stability.",
    },
}


def list_vbot_types() -> dict[str, Any]:
    return {
        "types": [
            {
                "id": type_id,
                "label": body.get("label", type_id),
                "default_robot_id": body.get("default_robot_id"),
                "default_scale": body.get("default_scale", 1.0),
                "drive": body.get("drive"),
            }
            for type_id, body in VBOT_ROBOT_TYPES.items()
        ],
        "count": len(VBOT_ROBOT_TYPES),
    }


def get_vbot_receiver_spec(
    robot_id: str = "vbot_yahboom_01",
    robot_type: str = "yahboom",
    *,
    osc_port: int = DEFAULT_OSC_PORT,
) -> dict[str, Any]:
    """Return ProtoFlux build spec + OSC map for in-world receiver."""
    type_meta = VBOT_ROBOT_TYPES.get(robot_type, VBOT_ROBOT_TYPES["custom"])
    rid = robot_id or type_meta.get("default_robot_id", "vbot_custom_01")

    addresses = {
        "spawn": {
            "address": VBOOMY_SPAWN_ADDRESS,
            "args": ["robot_id", "robot_type", "x", "y", "z", "scale"],
            "port": osc_port,
        },
        "reset": {
            "address": robot_address(rid, "reset"),
            "args": ["trigger"],
            "port": osc_port,
        },
        "move": {
            "address": robot_address(rid, "move"),
            "args": ["linear", "angular"],
            "port": osc_port,
        },
        "stop": {
            "address": robot_address(rid, "stop"),
            "args": ["trigger"],
            "port": osc_port,
        },
        "head": {
            "address": robot_address(rid, "head"),
            "args": ["yaw_deg", "pitch_deg"],
            "port": osc_port,
        },
        "emergency_stop": {
            "address": VBOOMY_ESTOP_ADDRESS,
            "args": ["trigger"],
            "port": osc_port,
        },
    }

    graph = {
        "name": f"vBot OSC Receiver ({rid})",
        "description": (
            "Listens on Resonite OSC input and drives a wheeled vBot root. "
            "Compatible with robotics-mcp → teleoperator-mcp vBoomy loop."
        ),
        "osc_port": osc_port,
        "robot_id": rid,
        "robot_type": robot_type,
        "nodes": [
            {
                "id": "osc-spawn",
                "type": "OSC_Data_Source",
                "params": {"address": VBOOMY_SPAWN_ADDRESS, "argument_index": "all"},
                "action": "On match: set root Position (x,y,z), Scale (scale), store robot_id",
            },
            {
                "id": "osc-move",
                "type": "OSC_Data_Source",
                "params": {"address": robot_address(rid, "move"), "argument_index": [0, 1]},
                "action": "Write Locomotion/LinearX ← arg0, Locomotion/AngularY ← arg1",
            },
            {
                "id": "osc-stop",
                "type": "OSC_Data_Source",
                "params": {"address": robot_address(rid, "stop")},
                "action": "Zero locomotion fields",
            },
            {
                "id": "osc-head",
                "type": "OSC_Data_Source",
                "params": {"address": robot_address(rid, "head"), "argument_index": [0, 1]},
                "action": "Head slot local rotation Y ← yaw_deg, X ← pitch_deg",
            },
            {
                "id": "osc-estop",
                "type": "OSC_Data_Source",
                "params": {"address": VBOOMY_ESTOP_ADDRESS},
                "action": "Zero all cmd fields + optional brake on Rigidbody",
            },
            {
                "id": "drive-integrator",
                "type": "Update",
                "action": (
                    "Each frame: if move age < 150ms, apply velocity "
                    "Forward * linear + Turn * angular to CharacterController or Rigidbody"
                ),
            },
        ],
    }

    setup_steps = [
        "Resonite → Settings → OSC → enable input on port {port}".format(port=osc_port),
        "Create empty root 'vBotRoot' with CharacterController or Rigidbody + collider",
        "Add child 'Head' slot with Camera (for future LiveKit capture)",
        "Attach ProtoFlux to vBotRoot → add OSC_Data_Source nodes per addresses.move/stop/head",
        f"Filter spawn: only apply when arg0 == '{rid}' (string equals)",
        "Wire move args to float fields LinearCmd and AngularCmd",
        "Update node: velocity = forward * LinearCmd + up * (AngularCmd * turnSpeed)",
        "On stop/estop: set LinearCmd=0, AngularCmd=0",
        "Head: drive local rotation on Head slot (degrees)",
        "Save as template asset; duplicate for mechazilla mesh at scale 2.5",
    ]

    test_sequence = [
        {
            "address": VBOOMY_SPAWN_ADDRESS,
            "values": [rid, robot_type, 0.0, 0.0, 0.0, type_meta.get("default_scale", 1.0)],
        },
        {"address": robot_address(rid, "move"), "values": [0.15, 0.0]},
        {"address": robot_address(rid, "head"), "values": [10.0, -5.0]},
        {"address": robot_address(rid, "stop"), "values": [1.0]},
    ]

    return {
        "robot_id": rid,
        "robot_type": robot_type,
        "type_meta": type_meta,
        "osc_port": osc_port,
        "addresses": addresses,
        "graph": graph,
        "setup_steps": setup_steps,
        "test_sequence": test_sequence,
        "register_example": {
            "method": "POST",
            "url": "http://127.0.0.1:12230/api/v1/robots",
            "body": {
                "robot_id": rid,
                "robot_type": robot_type,
                "platform": "resonite",
                "metadata": {"display_name": type_meta.get("label"), "scale": type_meta.get("default_scale", 1.0)},
            },
        },
    }
