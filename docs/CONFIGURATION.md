# resonite-mcp — Configuration

Moved out of README.md 2026-07-18 per fleet README_STRUCTURE standard.

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `RESONITE_OSC_HOST` | `127.0.0.1` | OSC target host (parameter streaming) |
| `RESONITE_OSC_PORT` | `9000` | OSC target port |
| `RESONITE_INVENTORY_MODE` | `auto` | Inventory adapter: `mock` / `live` / `auto` |
| `LOG_LEVEL` | `INFO` | Logging level |

## Resonite Setup — ResoniteLink (primary path)

ResoniteLink is official and built into Resonite (no mod). Only the **session
host** can enable it.

- Graphical client: Dashboard → Session → Settings → **Enable ResoniteLink**
  (a port is displayed — but see below).
- Headless config: `"enableResoniteLink": true`, optional `"forceResoniteLinkPort"`.
- Headless console: `enableResoniteLink <port>` (`0` = random).

**Port truth**: use `resonite_link_discover()` (UDP 12512 announcements) rather
than the dashboard readout — in live testing 2026-07-18 the displayed port did
not match the actual `linkPort`.

## Resonite Setup — OSC (secondary, parameter streaming)

1. Resonite Settings → Network → enable OSC (port 9000), optionally
   "Receive OSC" for bidirectional.
2. Allow the connection when Resonite prompts for host access consent; check
   firewall for UDP if messages don't arrive.

## Asset directories (World Inspector inject panel)

| Category | Path |
|---|---|
| Avatars (VRM) | `~/.avatarmcp/models/` |
| Props | `~/Documents/ResoniteAssets/props/` |
| Furniture | `~/Documents/ResoniteAssets/furniture/` |
| Architecture | `~/Documents/ResoniteAssets/architecture/` |
| Misc | `~/Documents/ResoniteAssets/misc/` |

Drop `.vrm`, `.fbx`, `.obj`, `.glb`, `.gltf`, `.blend`, `.dae` files there for
the inject picker. Note the protocol truth: files do not travel as-is —
geometry goes in via mesh-JSON/raw-mesh conversion (see RESONITELINK_GUIDE).
