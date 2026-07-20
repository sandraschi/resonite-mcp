# 🏛️ Resonite MCP Architecture & Overview

This document provides a detailed overview of the system architecture, component layout, and data-flow protocols governing **Resonite MCP** and its State-of-the-Art frontend dashboard (`resonite-mcp-sota`).

---

## 🗺️ High-Level System Architecture

The platform operates as a three-tier system linking LLM interfaces (MCP clients), web dashboards, and the live Resonite game engine:

```
  ┌────────────────────────────────┐
  │         Client Tier            │
  │  - IDE/Chat AI (MCP Stdio)     │
  │  - React Dashboard (HTTP/REST) │
  └────────────────────────────────┘
                 │
                 ▼ [MCP Tools / REST Commands]
  ┌────────────────────────────────┐
  │         Backend Tier           │
  │  - Python FastMCP Server       │
  │  - OSC Engine (Port 9000/9001) │
  │  - REST Server (Port 10979)    │
  └────────────────────────────────┘
                 │
                 ▼ [WebSockets (Port 4242) / OSC UDP]
  ┌────────────────────────────────┐
  │        In-Game Tier            │
  │  - Resonite Engine            │
  │  - ResoniteLink Helper Mod     │
  └────────────────────────────────┘
```

---

## 🧱 The Three Core Tiers

### 1. The Client Tier (Interfaces)
* **MCP Stdio Client**: The Python backend communicates via standard I/O (Stdio) with LLM environments (such as Cursor, Claude Desktop, or custom IDEs). This allows LLMs to discover and invoke the 65+ Python tools.
* **React Dashboard (`resonite-mcp-sota`)**: A modern Vite + Tailwind CSS dashboard that communicates with the Python backend via local HTTP REST endpoints. It provides UI controls for session tracking, friends status, inventory lists, and avatar tuning.

### 2. The Backend Tier (Python MCP Server)
Built using **FastMCP**, the backend serves as the central hub:
* **Tool Orchestration**: Implements modules for fleet management, inventory synchronization, cloud variables, and session handling.
* **OSC Server/Client**: Runs a UDP OSC socket client to send biometrics/locomotion triggers to the game on port `9000`, and an OSC receiver on port `9001` to capture game status callbacks.
* **REST HTTP Server**: Hosts the backend API on port `10979` to feed real-time JSON responses to the frontend React dashboard.

### 3. The In-Game Tier (Resonite Engine & ResoniteLink)
* **Resonite Engine**: The primary VR simulation client. It natively consumes OSC streams on port `9000` to drive avatar blendshapes and parameters.
* **ResoniteLink**: A WebSocket server running inside the game on port `4242`. It acts as a bridge, accepting commands from the Python backend to inspect scene hierarchies, locate entities, and spawn items or avatars from inventory.

---

## 📡 Communication Protocols & Port Mappings

| Protocol | Source | Destination | Default Port | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Stdio** | MCP Client | Python Backend | N/A | Tool registration, query, and tool execution requests. |
| **HTTP (REST)** | React Webapp | Python Backend | `10979` | Telemetry, contacts query, configuration, and API actions. |
| **WebSocket** | Python Backend | ResoniteLink (In-game) | `4242` | In-world spawning, entity searches, and world details querying. |
| **OSC (UDP)** | Python Backend | Resonite Client | `9000` | Real-time biometrics feed (face, voice, eyes, locomotion). |
| **OSC (UDP)** | Resonite Client | Python Backend | `9001` | Event notifications and callback status confirmations. |

---

## 📁 Workspace Directory Structure

* **`src/resonite_mcp/`**: Core Python backend.
  - **`tools/`**: Exposes MCP tool wrappers (OSC, avatar, inventory, sessions, fleet).
  - **`utils/`**: Helper scripts for staging files, formatting network payloads, and REST queries.
  - **`server.py` & `http_server.py`**: Entry points for standard MCP stdio and REST API servers.
* **`web_sota/`**: React + Vite dashboard frontend source code.
  - **`src/pages/`**: Navigation views (Dashboard, Sessions, Avatar, Contacts, Help).
  - **`src/components/layout/`**: Layout structure (collapsible sidebar, navigation headers).
* **`tests/`**: Unit test suites checking fleet configurations, tool payloads, and API routing.
* **`~/.avatarmcp/`**: Local caching directory containing VRM files, textures, and staged assets shared across multi-agent nodes.
