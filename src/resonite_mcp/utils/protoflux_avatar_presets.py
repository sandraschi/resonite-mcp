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
    "vrm_visemes_full": {
        "label": "VRM vowel visemes (A/I/U/E/O)",
        "description": "VRM 0.x standard lip-sync vowel preset maps (WISE blend shapes).",
        "parameters": {
            "Viseme/A": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Viseme/I": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Viseme/U": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Viseme/E": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Viseme/O": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm_mood": {
        "label": "VRM mood expressions",
        "description": "VRM 0.x standard emotion preset maps (Joy/Angry/Sorrow/Fun/Surprised).",
        "parameters": {
            "Expression/Joy": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/Angry": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/Sorrow": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/Fun": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/Surprised": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm_look": {
        "label": "VRM gaze directions",
        "description": "VRM 0.x standard look preset maps (LookUp/LookDown/LookLeft/LookRight).",
        "parameters": {
            "Look/Up": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/Down": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/Left": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/Right": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm_blink_sides": {
        "label": "VRM asymmetric blink (L/R)",
        "description": "VRM 0.x Blink_L/Blink_R side presets for winks and asymmetric blinks.",
        "parameters": {
            "Expression/BlinkLeft": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/BlinkRight": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "Pulse",
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm_neutral_reset": {
        "label": "VRM neutral rest face",
        "description": "VRM 0.x Neutral preset: zero-weight rest pose to clear stuck expressions.",
        "parameters": {
            "Expression/Neutral": {"type": "float", "range": [0.0, 1.0], "default": 1.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm1_vowels": {
        "label": "VRM 1.0 vowel expressions (aa/ih/ou/ee/oh)",
        "description": "VRM 1.0 VRMC_vrm expression preset names for lip-sync vowels.",
        "parameters": {
            "Expression/aa": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/ih": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/ou": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/ee": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/oh": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm1_emotion": {
        "label": "VRM 1.0 emotions",
        "description": "VRM 1.0 VRMC_vrm expression preset names (happy/angry/sad/relaxed/surprised).",
        "parameters": {
            "Expression/happy": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/angry": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/sad": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/relaxed": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/surprised": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
        },
        "protoflux_nodes": [
            "ValueField<float>",
            "AvatarExpressionDriver",
        ],
    },
    "vrm1_gaze": {
        "label": "VRM 1.0 gaze and blink",
        "description": "VRM 1.0 VRMC_vrm look/blink expression preset names.",
        "parameters": {
            "Look/lookUp": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/lookDown": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/lookLeft": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Look/lookRight": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/blink": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/blinkLeft": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
            "Expression/blinkRight": {"type": "float", "range": [0.0, 1.0], "default": 0.0},
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
