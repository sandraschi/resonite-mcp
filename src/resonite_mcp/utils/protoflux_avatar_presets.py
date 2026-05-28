"""ProtoFlux avatar parameter preset manifests for Agent Lab Phase 3."""

from __future__ import annotations

from typing import Any

PROTOFLUX_AVATAR_PRESETS: dict[str, dict[str, Any]] = {
    "resonite_humanoid_basic": {
        "label": "Resonite humanoid (locomotion + look)",
        "description": "Common driver slots for humanoid avatars in social VR worlds.",
        "parameters": {
            "Locomotion/Walk": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Locomotion/Run": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Locomotion/Jump": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/Horizontal": {"type": "float", "range": [-1.0, 1.0], "default": 0.0},
            "Look/Vertical": {"type": "float", "range": [-1.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarParameterDriver",
            "LocomotionModule",
        ],
    },
    "vrm_viseme_aa": {
        "label": "VRM viseme A (jaw open)",
        "description": "Maps VRM blend shape / expression channel for vowel A.",
        "parameters": {
            "Viseme/AA": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/JawOpen": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm_blink": {
        "label": "VRM blink cycle",
        "description": "Periodic blink driver for VRM look-at / blink blend shapes.",
        "parameters": {
            "Expression/Blink": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/BlinkLeft": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/BlinkRight": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "Pulse",
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
}


def list_protoflux_presets() -> dict[str, Any]:
    """Return catalog of ProtoFlux avatar parameter maps."""
    return {
        "presets": [
            {
                "id": preset_id,
                "label": body.get("label", preset_id),
                "description": body.get("description", ""),
                "parameter_count": len(body.get("parameters") or {}),
            }
            for preset_id, body in PROTOFLUX_AVATAR_PRESETS.items()
        ],
        "count": len(PROTOFLUX_AVATAR_PRESETS),
    }


def get_protoflux_preset(preset_id: str) -> dict[str, Any] | None:
    body = PROTOFLUX_AVATAR_PRESETS.get(preset_id)
    if not body:
        return None
    return {"id": preset_id, **body}
