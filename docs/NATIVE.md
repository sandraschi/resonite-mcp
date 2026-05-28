# Native desktop app (Tauri 2.0)

Windows installer bundling **Agent Lab** (`web_sota`) + HTTP backend (`:10979`) + presence gate.

## Prerequisites

- Rust (rustup) + MSVC build tools
- Node.js 20+
- uv + Python 3.12+
- WebView2 (Windows 11 OK; Windows 10 may need [WebView2 runtime](https://developer.microsoft.com/microsoft-edge/webview2/))

## Build

```powershell
cd D:\Dev\repos\resonite-mcp
just build-all
```

Pipeline (`native/build.ps1`):

1. `web_sota` Vite production build
2. Generate Tauri icons
3. PyInstaller sidecar → `native/binaries/resonite-mcp-backend-x86_64-pc-windows-msvc.exe`
4. Tauri NSIS installer

Output: `native/target/release/bundle/nsis/Resonite MCP_*_x64-setup.exe`

## Dev

Terminal A — backend:

```powershell
just start-be
```

Terminal B — Tauri + Vite:

```powershell
just tauri-dev
```

Or build sidecar once, then `just build-native-debug` for a local `.exe` shell.

## Production API URLs

Tauri serves static `web_sota/dist`. All API calls use `http://127.0.0.1:10979` via `web_sota/src/lib/api-base.ts` (`apiUrl()`).

## Release artifacts (tag `v*`)

| Asset | Audience |
|-------|----------|
| `dist/resonite-mcp-v*.mcpb` | Claude Desktop / MCP hosts |
| `Resonite MCP_*_x64-setup.exe` | Human operators (Agent Lab UI) |

## Notes

- **Resonite** is not bundled; Steam/standalone install still required.
- PyInstaller excludes `lancedb` / `sentence_transformers` to shrink sidecar; RAG search may be limited in the installer build.
- CI: `.github/workflows/native-release.yml` (Windows, tag-triggered).

## Reference

- Fleet standard: `mcp-central-docs/standards/rules/tauri_godot_sota.md`
- email-mcp / freecad-mcp / qcad-mcp `native/` layouts
