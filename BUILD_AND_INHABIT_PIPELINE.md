# 🔗 VR Build-and-Inhabit Fleet Pipeline Guide

This document details the architecture, stages, and execution of the **VR Build-and-Inhabit Fleet Pipeline** within the Resonite MCP ecosystem. This pipeline automates the transition from raw asset editing in external programs (Blender, GIMP, Inkscape) to live deployment and biometric control inside the virtual world.

---

## 📐 Pipeline Architecture Overview

The pipeline operates as a federated workflow spanning three layers:

```
  [1. Design & Export]          [2. Staging & Cache]          [3. Live Inhabitance]
 ┌──────────────────────┐      ┌─────────────────────┐      ┌─────────────────────────┐
 │ Blender (3D Mesh)    │ ───> │ ~/.avatarmcp/models │ ───> │ ResoniteLink (WebSocket) │
 │ GIMP (Textures)      │      │                     │      │ Spawns & Anchors Asset   │
 │ Inkscape (Vector UI) │ ───> │ Staging Cache       │      │                         │
 └──────────────────────┘      └─────────────────────┘      └─────────────────────────┘
                                          │                             │
                                          v                             v
                                   [MCP Bridge Proxy] ─────────> [OSC Biometrics]
                                  (Multi-Node Syncing)          (Facial & Eye Tracking)
```

---

## 🔄 The Pipeline Stages

### Stage 1: Design & Asset Export
* **Blender**: 3D models (characters, worlds, props) are compiled and exported as standard `.glb` or `.vrm` files. Skeletons (rigs) must align with the standard Humanoid avatar mapping.
* **GIMP**: Image files are exported as PNG textures and loaded by GIMP's material bridge.
* **Inkscape**: User interfaces are designed as SVG vectors.

### Stage 2: Staging & Staging Cache
Once exported, assets are moved to standard staging paths:
* **Avatars Directory**: Stored under the canonical path `~/.avatarmcp/models/` (shared across `resonite-mcp`, `avatar-mcp`, and `vrchat-mcp`).
* **General Assets Staging**: Temporary caches like `~/.avatarmcp/cache/` host UI vectors and props, minimizing network overhead when syncing files between multiple fleet nodes.
* **Federated Bridging**: When multi-node mode (`RESONITE_MCP_FLEET_MODE=standard`) is active, the `MCP_BRIDGE_URLS` environment variable allows separate server nodes to pull cache assets from the master build node.

### Stage 3: Live Spawning & In-Game Injection
* **ResoniteLink Client**: The MCP server connects to the running Resonite client via a local WebSocket connection (default port `4242`).
* **Object Spawning**: The `resonite_fleet` tool executes the `run_fleet_pipeline` operation. It pulls the staged asset from the local cache, instructs the ResoniteLink client to download it, and spawns the object directly in the active world.
* **Slot Mapping**: The spawned object is registered to an avatar slot (0-7).
* **ProtoFlux Binding**: Default ProtoFlux scripts are injected to handle standard locomotion inputs (`MoveX`, `MoveY`, `ThirdPerson`) and custom value multiplexers.

### Stage 4: Biometric Inhabitance (OSC)
Once the avatar is equipped in the active slot:
* **OSC Server Bind**: The MCP server fires up an OSC receiver on port `9001` and binds output to port `9000`.
* **Biometric Sync**: It begins streaming face-tracking parameters (`LipSync`, `EyeTrack`, `VoiceIntensity`) directly into the Resonite engine, immediately synchronizing the user's real-world movements and audio output with the newly spawned virtual body.

---

## 🛠️ How to Trigger the Pipeline

You can run the pipeline automatically through the MCP tool or CLI:

### 1. Via the Resonite MCP Tool
In your chat, ask:
> *"Run the fleet build pipeline for the VRM avatar 'my_character.vrm' on slot 0"*

The assistant will call the `resonite_fleet` tool:
```json
{
  "tool": "resonite_fleet",
  "params": {
    "operation": "run_fleet_pipeline",
    "avatar_path": "my_character.vrm",
    "slot": 0
  }
}
```

### 2. Under Strict Verification Mode
If you are doing strict testing:
```json
{
  "tool": "resonite_fleet",
  "params": {
    "operation": "run_strict_fleet_pipeline",
    "avatar_path": "my_character.vrm",
    "slot": 0
  }
}
```
*This ensures all network nodes are fully healthy and caches are warmed up before attempting the spawn.*
