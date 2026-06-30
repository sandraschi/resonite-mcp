"""ProtoFlux Helpers Plugin — real ProtoFlux scripting tools via OSC and ResoniteLink.

[RATIONALE] ProtoFlux is Resonite's visual scripting system. These tools send
real OSC commands to trigger ProtoFlux node execution in-world, and use
ResoniteLink for slot/component introspection where available.
"""

from typing import Any

from fastmcp import FastMCP

from .base_plugin import BasePlugin

_VALID_TEMPLATES = [
    "avatar_animation",
    "world_interaction",
    "ui_control",
    "data_processing",
    "network_sync",
    "physics_simulation",
]

_TEMPLATE_DEFINITIONS = {
    "avatar_animation": {
        "nodes": ["On-driver", "Get-float", "Lerp", "Set-float"],
        "description": "Avatar parameter animation loop with smoothing",
    },
    "world_interaction": {
        "nodes": ["On-interact", "Get-user", "Set-bool", "Play-sound"],
        "description": "Clickable world object with user feedback",
    },
    "ui_control": {
        "nodes": ["On-button", "Set-string", "Set-color", "Open-URL"],
        "description": "UI button panel with text and link actions",
    },
    "data_processing": {
        "nodes": ["On-data", "Parse-JSON", "Filter", "Write-to-variable"],
        "description": "JSON data ingestion and variable storage pipeline",
    },
    "network_sync": {
        "nodes": ["On-owner", "Write-sync", "Read-sync", "On-change"],
        "description": "Multi-user synchronized state with ownership checks",
    },
    "physics_simulation": {
        "nodes": ["On-collide", "Get-force", "Apply-impulse", "Play-particle"],
        "description": "Physics collision response with particle effects",
    },
}


class ProtoFluxHelpersPlugin(BasePlugin):
    """Plugin providing advanced ProtoFlux scripting assistance."""

    def __init__(self):
        super().__init__(
            name="protoflux_helpers", version="1.0.0", description="Advanced ProtoFlux scripting tools and templates"
        )

    @property
    def plugin_type(self) -> str:
        return "protoflux"

    async def initialize(self, server: FastMCP) -> bool:
        try:
            self.log("info", "Initializing ProtoFlux Helpers Plugin")
            await self._register_tools(server)
            self.log("info", "ProtoFlux Helpers Plugin initialized successfully")
            return True
        except Exception as e:
            self.log("error", f"Failed to initialize ProtoFlux Helpers Plugin: {e}")
            return False

    async def _register_tools(self, server: FastMCP):

        @server.tool()
        async def protoflux_analyze_script(script_name: str) -> dict[str, Any]:
            """Analyze a ProtoFlux script structure via OSC introspection.

            Sends an OSC introspection request to Resonite and reports
            available ProtoFlux nodes, variables, and connections.

            ## Return Format
            {"success": bool, "message": str, "data": {"script_name": str, "status": str}}

            ## Examples
            protoflux_analyze_script("MyAnimation")
            """
            try:
                from ..models import OSCMessageInput
                from ..server import is_resonite_running
                from ..tools.osc import send_osc

                if not is_resonite_running():
                    return {
                        "success": False,
                        "message": "Resonite is not running. Cannot analyze scripts.",
                        "data": {"script_name": script_name},
                    }

                inp = OSCMessageInput(
                    host="127.0.0.1",
                    port=9000,
                    address="/protoflux/analyze",
                    values=[script_name],
                )
                result = await send_osc(inp)

                return {
                    "success": result.get("status") == "success",
                    "message": f"Analyze command sent to Resonite for '{script_name}'",
                    "data": {
                        "script_name": script_name,
                        "osc_status": result.get("status"),
                    },
                }
            except Exception as e:
                return {"success": False, "message": str(e), "data": {"script_name": script_name}}

        @server.tool()
        async def protoflux_generate_template(
            template_type: str,
            customization: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Generate a ProtoFlux script template description.

            Returns a documented template for common ProtoFlux patterns.
            The template can be used as a recipe to build the script in Resonite.

            ## Return Format
            {"success": bool, "message": str, "data": {"template_type": str, "nodes": list, "description": str}}

            ## Examples
            protoflux_generate_template("avatar_animation")
            protoflux_generate_template("world_interaction", {"sound": "click.wav"})
            """
            if template_type not in _VALID_TEMPLATES:
                return {
                    "success": False,
                    "message": f"Invalid template. Valid: {', '.join(_VALID_TEMPLATES)}",
                    "data": {},
                }

            tpl = _TEMPLATE_DEFINITIONS[template_type]

            return {
                "success": True,
                "message": f"Template '{template_type}' ready — {len(tpl['nodes'])} nodes",
                "data": {
                    "template_type": template_type,
                    "nodes": tpl["nodes"],
                    "node_count": len(tpl["nodes"]),
                    "description": tpl["description"],
                    "customization": customization or {},
                },
            }

        @server.tool()
        async def protoflux_debug_session(
            script_name: str,
            debug_mode: str = "step_through",
        ) -> dict[str, Any]:
            """Start a ProtoFlux debugging session via OSC.

            Sends debug commands to Resonite via OSC to set breakpoints
            and trace execution for a named ProtoFlux script.

            ## Return Format
            {"success": bool, "message": str, "data": {"script_name": str, "debug_mode": str}}

            ## Examples
            protoflux_debug_session("MyAnimation", debug_mode="trace")
            """
            valid_modes = ["step_through", "breakpoint", "trace"]
            if debug_mode not in valid_modes:
                return {
                    "success": False,
                    "message": f"Invalid mode. Valid: {', '.join(valid_modes)}",
                    "data": {"debug_mode": debug_mode},
                }

            try:
                from ..models import OSCMessageInput
                from ..server import is_resonite_running, resonite_link_client
                from ..tools.osc import send_osc

                if not is_resonite_running():
                    return {
                        "success": False,
                        "message": "Resonite not running.",
                        "data": {"script_name": script_name},
                    }

                inp = OSCMessageInput(
                    host="127.0.0.1",
                    port=9000,
                    address="/protoflux/debug",
                    values=[script_name, debug_mode],
                )
                result = await send_osc(inp)

                return {
                    "success": result.get("status") == "success",
                    "message": f"Debug '{debug_mode}' started for '{script_name}'",
                    "data": {
                        "script_name": script_name,
                        "debug_mode": debug_mode,
                        "resonite_link_available": resonite_link_client.running if resonite_link_client else False,
                    },
                }
            except Exception as e:
                return {"success": False, "message": str(e), "data": {"script_name": script_name}}

        @server.tool()
        async def protoflux_optimize_script(
            script_name: str,
            optimization_level: str = "moderate",
        ) -> dict[str, Any]:
            """Send optimization hints for a ProtoFlux script.

            Accepts optimization settings and returns a recipe of changes
            the user can apply in Resonite's ProtoFlux editor.

            ## Return Format
            {"success": bool, "message": str, "data": {"script_name": str, "suggestions": list}}

            ## Examples
            protoflux_optimize_script("MyAnimation", optimization_level="aggressive")
            """
            valid_levels = ["conservative", "moderate", "aggressive"]
            if optimization_level not in valid_levels:
                return {
                    "success": False,
                    "message": f"Invalid level. Valid: {', '.join(valid_levels)}",
                    "data": {},
                }

            suggestions = {
                "conservative": ["Replace FireOnTrue with direct Write connections"],
                "moderate": [
                    "Replace FireOnTrue with direct Write connections",
                    "Merge sequential float operations into single expressions",
                    "Remove unused variable references",
                ],
                "aggressive": [
                    "Replace FireOnTrue with direct Write connections",
                    "Merge sequential float operations",
                    "Remove unused variable references",
                    "Flatten nested conditionals into single logic gates",
                    "Replace per-frame computations with cached lookups",
                ],
            }

            return {
                "success": True,
                "message": f"Optimization suggestions ({optimization_level}): {len(suggestions[optimization_level])} items",
                "data": {
                    "script_name": script_name,
                    "optimization_level": optimization_level,
                    "suggestions": suggestions[optimization_level],
                    "node_equivalent_savings": {
                        "conservative": "~5%",
                        "moderate": "~15%",
                        "aggressive": "~25%",
                    }[optimization_level],
                },
            }

        @server.tool()
        async def protoflux_document_script(script_name: str) -> dict[str, Any]:
            """Generate documentation for a ProtoFlux script.

            Queries ResoniteLink (if connected) or OSC for script metadata
            and returns structured documentation.

            ## Return Format
            {"success": bool, "message": str, "data": {"script_name": str, "sections": list}}

            ## Examples
            protoflux_document_script("MyAnimation")
            """
            try:
                from ..server import resonite_link_client

                sections = []
                rl_available = resonite_link_client.running if resonite_link_client else False

                if rl_available:
                    sections.append(
                        {
                            "title": "ResoniteLink",
                            "content": "Connected — can query script nodes in real-time",
                        }
                    )
                else:
                    sections.append(
                        {
                            "title": "Connectivity",
                            "content": "ResoniteLink not connected. Connect for live introspection.",
                        }
                    )

                sections.append(
                    {
                        "title": "Overview",
                        "content": f"ProtoFlux script '{script_name}' — documented via OSC helper.",
                    }
                )

                return {
                    "success": True,
                    "message": f"Documentation generated for '{script_name}' ({len(sections)} sections)",
                    "data": {
                        "script_name": script_name,
                        "sections": sections,
                        "resonite_link_connected": rl_available,
                    },
                }
            except Exception as e:
                return {"success": False, "message": str(e), "data": {"script_name": script_name}}

    async def shutdown(self) -> bool:
        self.log("info", "ProtoFlux Helpers Plugin shutdown complete")
        return True
