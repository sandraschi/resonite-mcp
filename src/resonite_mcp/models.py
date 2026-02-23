from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OSCMessageInput(BaseModel):
    """Input model for OSC message sending."""

    host: str = Field(..., description="Target hostname or IP address")
    port: int = Field(gt=0, le=65535, description="Target UDP port (1-65535)")
    address: str = Field(
        ..., pattern=r"^/.*", description="OSC address pattern starting with /"
    )
    values: List[Any] = Field(
        default_factory=list, description="List of values to send"
    )


class OSCServerInput(BaseModel):
    """Input model for starting OSC server."""

    port: int = Field(gt=0, le=65535, description="UDP port to listen on (1-65535)")
    address: str = Field(default="0.0.0.0", description="Network interface to bind to")


class OSCServerStopInput(BaseModel):
    """Input model for stopping OSC server."""

    port: int = Field(
        gt=0, le=65535, description="Port of the server to stop (1-65535)"
    )


class ResoniteSessionInput(BaseModel):
    """Input for Resonite session management."""

    session_name: Optional[str] = Field(
        None, description="Optional custom session name"
    )
    world_path: Optional[str] = Field(
        None, description="Initial world to load (resonite:// format)"
    )
    avatar_slot: Optional[int] = Field(
        None, ge=0, le=7, description="Avatar slot to use (0-7)"
    )


class AvatarControlInput(BaseModel):
    """Input for avatar control operations."""

    avatar_id: str = Field(..., description="Avatar identifier or path")
    slot: Optional[int] = Field(
        None,
        ge=0,
        le=7,
        description="Avatar slot (0-7), auto-assigned if not specified",
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Initial parameter values to set"
    )


class ProtoFluxScriptInput(BaseModel):
    """Input for ProtoFlux script operations."""

    script_name: str = Field(..., description="Name of the ProtoFlux script")
    script_data: Optional[Dict[str, Any]] = Field(
        None, description="Script definition and parameters"
    )
    execute: bool = Field(True, description="Whether to execute the script immediately")


class InventoryListInput(BaseModel):
    """Input for inventory listing operations."""

    item_type: Optional[str] = Field(
        None, description="Filter by item type: avatar, world, item, tool, script"
    )
    search_query: Optional[str] = Field(
        None, description="Search query to filter items by name or description"
    )
    limit: int = Field(
        50, ge=1, le=200, description="Maximum number of items to return"
    )
    offset: int = Field(0, ge=0, description="Number of items to skip (for pagination)")


class InventorySpawnInput(BaseModel):
    """Input for spawning items from inventory."""

    item_id: str = Field(..., description="Unique identifier of the inventory item")
    position: Optional[List[float]] = Field(
        None, description="Position to spawn at [x, y, z]"
    )
    rotation: Optional[List[float]] = Field(
        None, description="Rotation to spawn with [x, y, z, w] quaternion"
    )
    scale: Optional[List[float]] = Field(
        None, description="Scale to spawn with [x, y, z]"
    )


class InventoryUploadInput(BaseModel):
    """Input for uploading items to inventory."""

    item_path: str = Field(..., description="Local file path to upload")
    item_name: str = Field(..., description="Name for the uploaded item")
    item_type: str = Field(
        ..., description="Type of item: avatar, world, item, tool, script"
    )
    description: Optional[str] = Field(
        None, description="Optional description for the item"
    )
    is_public: bool = Field(
        False, description="Whether the item should be publicly accessible"
    )


class InventoryDeleteInput(BaseModel):
    """Input for deleting items from inventory."""

    item_id: str = Field(..., description="Unique identifier of the inventory item")
    confirm_deletion: bool = Field(True, description="Must be true to confirm deletion")


class InventoryShareInput(BaseModel):
    """Input for sharing inventory items."""

    item_id: str = Field(..., description="Unique identifier of the inventory item")
    share_with: str = Field(..., description="Username to share with")
    permission_level: str = Field(
        "read", description="Permission level: read, write, admin"
    )


class ResoniteLinkConnectInput(BaseModel):
    """Input for connecting to ResoniteLink."""

    host: str = Field(default="localhost", description="ResoniteLink host")
    port: int = Field(default=4242, description="ResoniteLink port")


class ResoniteLinkSpawnInput(BaseModel):
    """Input for spawning objects via ResoniteLink."""

    template_url: str = Field(..., description="URL of the template to spawn")
    position: Dict[str, float] = Field(
        default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0},
        description="Position to spawn at",
    )


class ResoniteLinkSetInput(BaseModel):
    """Input for setting component values via ResoniteLink."""

    component_id: str = Field(..., description="Target component ID")
    field: str = Field(..., description="Field to set")
    value: Any = Field(..., description="Value to set")


class ResoniteLinkGetInput(BaseModel):
    """Input for getting component values via ResoniteLink."""

    component_id: str = Field(..., description="Target component ID")
    field: str = Field(..., description="Field to get")
