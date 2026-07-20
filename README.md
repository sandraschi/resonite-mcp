# 🎭 Resonite MCP & Dashboard

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <img src="https://img.shields.io/badge/ResoniteLink-0.13.1_live--verified-22c55e?style=flat-square" alt="ResoniteLink live-verified">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
</p>

**Talk to your virtual world.** 

Resonite MCP is an integration bridge and state-of-the-art web dashboard that connects AI assistants to the **Resonite** social VR platform. Using natural language, you can command your world, customize your avatar, inspect your sessions, and control your telemetry directly through chat.

---

## ✨ Key Features

* 🤖 **AI Assistant Integration (MCP)**: Use natural language with your AI chat client to spawn objects, toggle locomotion, change active slots, or load worlds.
* 🧬 **Avatar & Biometric Tuning**: Adjust tracking smoothing, toggle eye tracking, and monitor lipsync parameters in real-time.
* 👥 **Socials & Contacts**: Check who is online, read chat logs, and join your friends' sessions with one click.
* 📦 **In-World Spawning**: Search, organize, and spawn assets directly from your inventory database.
* 🎨 **Visual Dashboard & Gallery**: Monitor connection health, inspect the world's node tree, and browse a visual gallery of screenshots and popular worlds.

---

## 🌐 The Build-and-Inhabit Fleet Ecosystem

This repository is not just a standalone connector, but a vital node in a wider **Multi-Agent Fleet Ecosystem**:

* **Multi-Node Federation**: Supports federated asset caching under the standard directory `~/.avatarmcp/` and uses `MCP_BRIDGE_URLS` for cross-network state synchronization between developer nodes.
* **Build-and-Inhabit Pipeline**: Integrates external design environments (such as **Blender, GIMP, and Inkscape**) directly into VR platforms (such as **Resonite, VRChat, and Vircadia**). Assets are automatically compiled, staged, spawned in-world over WebSockets, and inhabited by the agent via real-time OSC telemetry. 
* *For complete details on the architecture, setup stages, and platform behaviors, read the **[Build-and-Inhabit Pipeline Guide](BUILD_AND_INHABIT_PIPELINE.md)** and **[VR Worlds Comparison Guide](VR_WORLDS_COMPARISON.md)**.*

---

## ⛩️ The Miko's Digital Shrine

In the spirit of kami and miko — this MCP server serves as a bridge between human creators and the digital spirits of virtual worlds. The kawaii and clever miko tends the shrines of code, ensuring the kami of creation flow freely through our digital spaces.

---

## 🚀 Quick Start (Get Running in 3 Steps)

### Step 1: Launch Resonite
Make sure the Resonite game client is running on Steam. Enable the ResoniteLink connection inside the session settings (Dashboard ➔ Session ➔ Settings ➔ Enable ResoniteLink).

### Step 2: Start the Dashboard
Clone the repository and spin up the frontend webapp and Python server:
```powershell
git clone https://github.com/sandraschi/resonite-mcp
cd resonite-mcp
just bootstrap
just serve
```
*The web dashboard is now active at `http://localhost:10978`.*

### Step 3: Connect your AI Assistant
Add the server configuration to your Claude Desktop config file (`claude_desktop_config.json`):
```json
"mcpServers": {
  "resonite-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/resonite-mcp", "run", "resonite-mcp"]
  }
}
```

---

## 📚 Documentation Index

For deep architectural details, setup advice, and API references, check out our dedicated guides:

| Guide | Description |
| :--- | :--- |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | High-level system architecture, protocols, and port mappings |
| **[INSTALL.md](INSTALL.md)** | Full installation paths and environment configurations |
| **[docs/TOOLS.md](docs/TOOLS.md)** | List of the 65+ Python tools and HTTP API endpoints |
| **[docs/RESONITELINK_GUIDE.md](docs/RESONITELINK_GUIDE.md)** | Deep-dive into the ResoniteLink WebSocket protocol |
| **[VR_WORLDS_COMPARISON.md](VR_WORLDS_COMPARISON.md)** | Detailed comparison between Resonite, VRChat, and Vircadia |
| **[BUILD_AND_INHABIT_PIPELINE.md](BUILD_AND_INHABIT_PIPELINE.md)** | Automation stages from Blender/GIMP to live VR injection |
| **[COMMUNITY_RESOURCES.md](COMMUNITY_RESOURCES.md)** | Links to RML modding, video tutorials, subreddits, and Discords |
| **[BEGINNERS_GUIDE.md](BEGINNERS_GUIDE.md)** | Onboarding basics and control references for new users |

---

## 📈 Status & Roadmap
* **Current Version**: `v1.1.0` (ResoniteLink Protocol 0.13.1).
* **Compliance**: Agent Lab Phases 1–6 complete. Real-time slot CRUD, OSC synchronization, and cached asset syncing are fully live-verified.
* **License**: MIT Licensed. Made with care for the Resonite community.
