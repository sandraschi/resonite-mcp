"""Voice command hooks: local LLM hints + OSC macro portmanteau."""

from __future__ import annotations

import logging
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..server import server

logger = logging.getLogger(__name__)

VoiceOperation = Literal[
    "list_macros",
    "parse_command",
    "send_macro",
    "execution_mode",
]

_OSC_MACROS: dict[str, dict[str, Any]] = {
    "wave": {"address": "/avatar/gesture/wave", "values": [1.0]},
    "jump": {"address": "/avatar/locomotion/jump", "values": [1.0]},
    "sit": {"address": "/avatar/locomotion/sit", "values": [1.0]},
    "toggle_ui": {"address": "/resonite/ui/toggle", "values": ["agent_lab"]},
    "import_staging": {"address": "/resonite/fleet/import_staging", "values": []},
}

_KEYWORD_MAP: dict[str, str] = {
    "wave": "wave",
    "hello": "wave",
    "jump": "jump",
    "sit": "sit",
    "toggle ui": "toggle_ui",
    "import staging": "import_staging",
}


class VoiceResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str = ""


async def _llm_refine_command(text: str) -> str:
    try:
        from ..llm import detect_local_llms, get_best_substrate, synthesize_answer

        llms = await detect_local_llms()
        substrate = get_best_substrate(llms)
        if not substrate:
            return text
        prompt = (
            "Map this voice command to one macro id from "
            f"{sorted(_OSC_MACROS)}. Reply with macro id only.\nCommand: {text}"
        )
        answer = await synthesize_answer(prompt, substrate=substrate)
        cleaned = (answer or "").strip().lower().replace(" ", "_")
        return cleaned if cleaned in _OSC_MACROS else text
    except Exception as exc:
        logger.debug("LLM voice refine skipped: %s", exc)
        return text


def _keyword_macro(text: str) -> str | None:
    lowered = text.strip().lower()
    for phrase, macro_id in _KEYWORD_MAP.items():
        if phrase in lowered:
            return macro_id
    for macro_id in _OSC_MACROS:
        if macro_id.replace("_", " ") in lowered or macro_id in lowered:
            return macro_id
    return None


async def resonite_voice(
    operation: VoiceOperation,
    *,
    command_text: str = "",
    macro_id: str = "",
    host: str = "127.0.0.1",
    port: int = 9000,
) -> dict[str, Any]:
    """Local LLM-assisted voice macros over OSC."""
    try:
        if operation == "list_macros":
            return VoiceResult(
                success=True,
                operation=operation,
                message="OSC macro catalog",
                data={"macros": _OSC_MACROS, "keywords": _KEYWORD_MAP},
            ).model_dump()

        if operation == "execution_mode":
            from ..llm import detect_local_llms

            llms = await detect_local_llms()
            return VoiceResult(
                success=True,
                operation=operation,
                message="Voice execution guidance",
                data={
                    "local_llm_available": len(llms) > 0,
                    "llm_count": len(llms),
                    "fallback": "keyword_map",
                },
            ).model_dump()

        if operation == "parse_command":
            if not command_text.strip():
                return VoiceResult(
                    success=False,
                    operation=operation,
                    message="command_text required",
                    error="ValueError",
                ).model_dump()
            macro = _keyword_macro(command_text)
            source = "keyword"
            if not macro:
                refined = await _llm_refine_command(command_text)
                macro = refined if refined in _OSC_MACROS else _keyword_macro(refined)
                source = "llm" if macro else "unresolved"
            return VoiceResult(
                success=macro is not None,
                operation=operation,
                message="Command parsed" if macro else "No macro matched",
                data={"macro_id": macro, "source": source, "command_text": command_text},
                error="" if macro else "UnresolvedCommand",
            ).model_dump()

        if operation == "send_macro":
            resolved = macro_id or _keyword_macro(command_text)
            if not resolved and command_text:
                parsed = await resonite_voice("parse_command", command_text=command_text)
                resolved = (parsed.get("data") or {}).get("macro_id")
            if not resolved or resolved not in _OSC_MACROS:
                return VoiceResult(
                    success=False,
                    operation=operation,
                    message="macro_id required",
                    error="ValueError",
                ).model_dump()
            spec = _OSC_MACROS[resolved]
            from ..models import OSCMessageInput
            from .osc import send_osc

            osc = await send_osc(
                OSCMessageInput(
                    host=host,
                    port=port,
                    address=str(spec["address"]),
                    values=list(spec.get("values") or []),
                )
            )
            return VoiceResult(
                success=osc.get("status") == "success",
                operation=operation,
                message=f"Macro {resolved} sent",
                data={"macro_id": resolved, "osc": osc, "spec": spec},
                error="" if osc.get("status") == "success" else "OscError",
            ).model_dump()

        return VoiceResult(
            success=False,
            operation=operation,
            message=f"Unknown operation: {operation}",
            error="ValueError",
        ).model_dump()
    except Exception as exc:
        logger.exception("resonite_voice failed operation=%s", operation)
        return VoiceResult(
            success=False,
            operation=operation,
            message=str(exc),
            error=str(exc),
        ).model_dump()


server.tool()(resonite_voice)
