# Resonite as a Robotics Simulation & HRI Testbed

**Status**: Research Note · February 2026  
**Author**: Antigravity / Sandra Schipal  
**Relevance**: OpenFang · robotics-mcp · Unitree G1 · resonite-mcp

---

## 1. What Is Resonite?

Resonite is a **social VR/desktop metaverse** (Steam: App 2519830) built by ex-VRChat developer Frooxius (Tomáš Mariančík). Unlike VRChat, it is architecture-first: everything in the world is a typed `Record`, the scripting system (ProtoFlux) is a visual dataflow graph, and it has first-class headless server support.

**Key thesis**: Resonite is not just a social VR platform — it is a **programmable, multiplayer, real-time 3D environment** with a bidirectional external control interface. This makes it a credible alternative to Gazebo for certain robotics-simulation and HRI use cases.

---

## 2. Core Concepts You Need to Know

### 2.1 Sessions (Worlds)
A "session" is a live instance of a world — the equivalent of a simulation scene. Sessions can be:
- **Public**: discoverable via `GET /sessions` — anyone can join
- **Private**: restricted to contacts or whitelist
- **Headless**: running on a dedicated server with no graphics (perfect for robotics simulation)

A session URL looks like: `res-session:///S-xxxxxxxx`

### 2.2 Records (Possessions / Inventory)
Everything persisted in Resonite is a **Record** with a `resrec://` URI:
- 3D objects you've imported or created
- Saved world templates (spawn from inventory → creates a new session)
- Avatars (your body)
- ProtoFlux script objects
- Folders / nested directories

Your personal inventory is a tree of records: `resrec://U-{userId}/Inventory/...`

### 2.3 Contacts (Friends)
Your social graph. Key fields:
- `contactUsername` — their display name
- `userStatus.onlineStatus` — Online / Away / Busy / Offline
- `userStatus.currentSessionId` — which world they're in right now

### 2.4 Avatars
Your 3D body. GLB/VRM format. Bones map to human skeleton (HumanoidRig). You can:
- Import any GLB model as an avatar
- Bind ProtoFlux scripts to bone transforms (for external joint control via OSC)
- Control facial expressions via blendshapes (avatar parameters — LipSync, Eye tracking)

### 2.5 ProtoFlux (Visual Scripting)
The in-world logic engine. Think: a dataflow graph where nodes represent operations. Key capabilities for robotics:
- Read/write any object property (position, rotation, scale, material color, audio volume)
- Respond to OSC inputs → drive avatar bone transforms
- Emit OSC messages → send sensor readings back to external systems
- Timer pulses, collision events, proximity triggers, user proximity detection

---

## 3. External Control Architecture (OSC)

Resonite's control interface is **OSC (Open Sound Control)** over UDP — the same protocol used for VRChat avatar automation.

```
External System (ROS2 / Python / resonite-mcp)
        │
        ▼  UDP port 9000
  Resonite Client / Headless
        │  (OSC receiver → ProtoFlux nodes)
        │
   In-World Object / Avatar
        │
        ▼  UDP port 9001
  External System (OSC sender from Resonite)
```

### OSC addresses in use (resonite-mcp)
| Address | Direction | Purpose |
|---|---|---|
| `/inventory/list` | → Resonite | List inventory items |
| `/inventory/spawn` | → Resonite | Spawn item into world |
| `/inventory/upload` | → Resonite | Upload file to inventory |
| `/worldlabs/import` | → Resonite | Import a World Labs GLB asset |
| `/inventory/list/response` | ← Resonite | Response from list query |
| `/inventory/info/response` | ← Resonite | Response from info query |

### Robotics-specific OSC addresses you would add
| Address | Direction | Purpose |
|---|---|---|
| `/avatar/joint/{name}/rotation` | → Resonite | Drive skeleton bone rotation (quaternion) |
| `/avatar/joint/{name}/position` | → Resonite | Drive bone position delta |
| `/avatar/voice/amplitude` | → Resonite | Control voice output volume |
| `/world/sensor/proximity` | ← Resonite | Avatar-to-user distance |
| `/world/sensor/collision` | ← Resonite | Collision events |
| `/world/sensor/audio` | ← Resonite | Ambient audio level from mic |

---

## 4. Resonite vs Gazebo for Robotics

| Criterion | Gazebo (ROS2) | Resonite |
|---|---|---|
| **Physics accuracy** | ✅ ODE/Bullet/DART, full URDF | ⚠️ Game physics only — not dynamics-accurate |
| **LIDAR/depth sim** | ✅ ROS sensor plugins | ❌ No native LIDAR sim |
| **SLAM testing** | ✅ Standard use case | ❌ Wrong tool |
| **Human presence** | ❌ Static obstacles only | ✅ Real humans in real time |
| **Social scenario testing** | ❌ No | ✅ Core strength |
| **Visual realism** | ⚠️ Improving (Fortress/Garden) | ✅ Excellent, Gaussian Splat environments |
| **External control** | ✅ ROS topics/services | ✅ OSC + REST + ProtoFlux |
| **World authoring** | ❌ SDF/URDF XML | ✅ In-world, real-time, visual |
| **Cost per test user** | N/A | ~0 (free social VR) |
| **Setup complexity** | High | Moderate |

**Verdict**: Resonite is **not a Gazebo replacement** for kinematics, SLAM, or sensor simulation. It IS a superior environment for:
1. **Human-robot interaction (HRI) testing** with real participants at zero cost
2. **World environments** generated from real locations (World Labs → Marble → Resonite)
3. **Social navigation** (how does the robot move in a crowd?)
4. **Voice and expression** testing (does the robot's TTS feel natural to real humans?)
5. **Remote teleoperation** demonstration and evaluation

---

## 5. Resonite REST API (Added in resonite-mcp)

`api.resonite.com` — documented at `wiki.resonite.com/API` (last updated 2026-01-02)

**Note: this is explicitly marked WIP by the Resonite team. No SLA. May break.**

### Authentication
```python
POST /userSessions
Body: { username, authentication: { $type: "password", password }, secretMachineId, rememberMe }
Headers: UID: <sha256-hash>, TOTP: <6-digit if 2FA enabled>
→ returns: { userId, token }
```

Token format for subsequent requests: `Authorization: res {userId}:{token}`

### Key endpoints implemented in resonite-mcp `rest_api.py`
| Tool | Endpoint | Auth |
|---|---|---|
| `resonite_rest_login` | POST /userSessions | No |
| `resonite_rest_get_sessions` | GET /sessions | No |
| `resonite_rest_get_user` | GET /users/{id} | Optional |
| `resonite_rest_get_records` | GET /users/{id}/records | Yes |
| `resonite_rest_send_message` | POST /users/{id}/messages | Yes |
| `resonite_rest_get_platform` | GET /platform | No |

### Assets domain
Resonite record assets are at `assets.resonite.com/{hash}` — hash from `resdb:///{hash}.ext` URIs.

---

## 6. Integration with resonite-mcp

The server is at `d:/Dev/repos/resonite-mcp`.

**Transport**: Dual — stdio MCP + HTTP bridge (port TBD — needs assigning in WEBAPP_PORTS.md)  
**Webapp**: `web_sota/` — rebuilt Feb 2026 with 9 pages:
- Dashboard · Status · Sessions · Inventory · Contacts · Chat · Tools · Help · Settings

**Environment variables needed**:
```
RESONITE_USER_ID=U-youruserid
RESONITE_TOKEN=your-session-token   # obtain via resonite_rest_login
RESONITE_OSC_HOST=127.0.0.1         # host running Resonite client/headless
RESONITE_OSC_PORT=9000
```

**Workflow for robot control**:
1. Start Resonite in headless mode with OSC enabled
2. Spawn robot avatar from inventory via `resonite_inventory_spawn`
3. Send joint angles via OSC: `resonite-mcp → osc-mcp → /avatar/joint/*/rotation`
4. Receive sensor data back on port 9001 via `osc-mcp` recordings buffer

---

## 7. Further Reading

- [Resonite Wiki API](https://wiki.resonite.com/API)
- [Resonite ProtoFlux Wiki](https://wiki.resonite.com/ProtoFlux)
- [resonitepy Python client](https://github.com/brodokk/resonitepy) — unofficial Python API library
- [Marble Resonite Integration Guide](MARBLE_RESONITE_GUIDE.md) — in this repo
- [World Labs API Quickstart](https://docs.worldlabs.ai/api)
