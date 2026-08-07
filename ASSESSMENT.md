# resonite-mcp — Project Assessment

**Category**: MCP Server
**Assessment Date**: 2026-07-30 (added ProtoFlux honesty findings; previous: 2026-07-11)
**Version**: v1.1.0

---

## 2026-07-30 — ProtoFlux tooling honesty audit (for opencode / local-deepseek pickup)

Prompted by a cross-check against `overte-mcp` (same fleet, same pattern of
bug). Read this before touching `plugins/protoflux_helpers.py`.

**Finding**: `protoflux_helpers.py`'s docstring claims "real ProtoFlux
scripting tools via OSC and ResoniteLink," but two of its four tools are not
real yet:

- `protoflux_analyze_script` and `protoflux_debug_session` send OSC to
  `/protoflux/analyze` and `/protoflux/debug`. **These addresses do not exist
  in Resonite by default** — they would only respond if a ProtoFlux graph
  had already been hand-built in-world specifically to listen on those
  addresses. No such graph ships with this repo. Today these tools always
  report a plausible-looking success against nothing real.
- `protoflux_generate_template` and `protoflux_optimize_script` are pure
  static text — hardcoded node-name lists and canned optimization tips, not
  actual script inspection.

This is the same class of bug the 2026-07-11 ResoniteLink rewrite already
fixed once in this repo (see below — the old client spoke a wire format that
never existed upstream). Fix it the same way: verify against what's real,
don't assume.

### Fix plan
- [ ] Rewrite `protoflux_analyze_script` / `protoflux_document_script` to
      query real slot/component/ProtoFlux-node data via `resonite_link.py`'s
      existing reflection and sync-method-call support, instead of the
      fictional OSC addresses.
- [ ] Ship a companion ProtoFlux "MCP bridge" graph (importable
      `.resonitepackage`) that actually implements listener nodes for
      whatever OSC addresses the tools still need — mirrors the
      `overte-mcp-bridge.js` approach on the Overte side. Without this,
      OSC-side ProtoFlux control is inherently unfulfillable no matter how
      the Python side is written.
- [ ] Once fixed, update this file's tool-status language and
      `protoflux_helpers.py`'s docstring to state plainly what's verified —
      don't leave "real ProtoFlux scripting tools" standing if only two of
      four tools are real.

### Feature gaps found (not started)
- **Dynamic bone chains / physics** — no tool references `DynamicBoneChain`
  or collision/physics control anywhere in `src/resonite_mcp`. Relevant if
  [[nekomimi-chan]] wants natural avatar motion (tail, ears, hair).
- **Voice macros → ProtoFlux bindings** — already flagged below as P3
  (2026-07-11), still not done. Also relevant to nekomimi-chan's
  voice-triggered NPC reactions for Japanese practice.
- **First-party Twitch/Mastodon/Bluesky integration** — Resonite has native
  ProtoFlux support for these; no MCP tool surfaces them. Low priority
  unless a concrete use case shows up (these are usable directly in-world
  via ProtoFlux without MCP involvement).

### What's actually solid (don't re-litigate)
`resonite_link.py`'s 2026-07-11 rewrite is the real deal — verified against
upstream C# reference 0.13.1, with `$type` discriminators, typed reflection,
sync method calls, and LAN session discovery. 22 wire-format regression
tests lock the shapes. The remaining gap there is a live E2E session against
a running Resonite client (operator task) — same category of blocker as
`overte-mcp`'s "no Overte installed on Goliath yet."

---

## 2026-07-11 (evening): ResoniteLink protocol upgrade — DONE


The P1 item is resolved, and the finding was worse than "outdated": the old
client implemented a **fictional wire format** (`ReadField`/`WriteField`/
`GetNode`/`Reflect`/`Batch` with `type`/`id` keys) that never existed upstream —
it could never have talked to real Resonite. v1.1.0 replaces it with the real
protocol, verified against the upstream C# reference (0.13.1): `$type`
discriminators, `messageId` correlation, typed value wrappers, camelCase
messages. Added: LAN session discovery (UDP 12512), sync method calls,
reflection family, honest not_implemented for generic model import (which the
protocol does not offer). 22 wire-format regression tests lock the shapes;
84/84 tests green. Remaining: live E2E against a running Resonite session
(operator task), and wrapping the asset-import messages (mesh-JSON/texture/
audio) for the import pipeline.

---

## Summary

| Metric | Status |
|--------|--------|
| Agent Lab roadmap (Phases 1–6) | Complete |
| MCPB packaging | `mcp-server/` + `just mcpb-pack` |
| CI/CD | `.github/workflows/ci.yml` (lint, mypy, E2E smoke, pytest) |
| Docker / monitoring | Dockerfile, compose, Prometheus/Grafana/Loki profile |
| Test suite | 52 unit tests; fleet E2E offline + strict |
| Coverage gate | 50% on `tools/` + `utils/` (HTTP stack excluded) |
| Upstream tracking | ResoniteLink client at 0.8.3; **upstream 0.13.1** — gap documented |

**Overall**: Production-ready for fleet Agent Lab and stdio MCP. Upstream ResoniteLink has moved five minor versions ahead; a compatibility review is the top technical priority. Live Resonite validation remains operator-driven.

---

## 2026-07-11 audit findings

### Fixed in this pass (v1.0.1)
- **Version mismatch**: `__init__.py` was 0.8.0 vs pyproject/manifest 1.0.0 → all 1.0.1.
- **CHANGELOG scrambled**: duplicate 0.2.0, non-chronological order, unreleased blocks mid-file → rebuilt.
- **Em dash in `web_sota/start.ps1`** (Unicode Safety standard) → fixed.
- **`glama.json`** claimed "FastMCP 2.13+" → 3.4+.
- **`.gitignore`** missing `htmlcov/`, `.coverage`, `.lancedb/`, `*.bak`, `*.py.backup`, `test_output.txt` → added.
- **RESONITELINK_GUIDE.md factual error**: claimed ResoniteLink requires ResoniteModLoader — it is official/built-in since Dec 2025 → corrected; upstream gap table added.
- **CHANGELOG_LATEST.md** created (fleet release convention).

### Upstream: Resonite / ResoniteLink (they release frequently)
- **ResoniteLink 0.8.3 → 0.13.1** since Feb 2026. Still labeled beta; breaking changes possible.
  - **Compatibility risk**: 0.9.0 changed member definition types to type references (affects `Reflect`); 0.9.2 removed redundant type fields. Our client may parse current-Resonite `Reflect` responses incorrectly. Needs a live wire-format test.
  - **High-value adds**: 0.12.0 LAN session discovery (kills the hardcoded port-4242 assumption), 0.11.0 sync method calls, 0.10.0 dictionaries.
  - Steam notes also mention fixes to `RemoveSlot` batch ordering and bone bindings for raw-data mesh imports — both relevant to our import pipeline.
- **Cloud API** (`api.resonite.com`): wiki-documented `/sessions` endpoints (incl. `includeEmptyHeadless`) still match our proxy usage — no action needed.
- **No local REST API** has materialized; the `USE_REST_API` scaffold in `resonite_link.py` stays dormant.
- **Headless**: now on .NET 10; still Patreon-gated Steam beta. No changes affecting us.

### Standards compliance (June/July 2026 bar)

| Area | Status | Notes |
|------|--------|-------|
| FastMCP 3.2+ | ✅ | `fastmcp>=3.4.2,<4`, prefab-ui>=0.14.0, portmanteau tools |
| MCPB packaging | ✅ | `mcp-server/manifest.json`, sync/pack scripts |
| uv + justfile + llms.txt/llms-full.txt | ✅ | present |
| Implementation honesty | ✅ | mocks confined to E2E harnesses + labeled inventory adapter modes |
| Unicode safety | ✅ (after fix) | em dash removed from start.ps1 |
| **DXT deprecation** | ✅ (2026-07-19) | `dxt/` folder removed; `docs/INSTALLATION.md` and `docs/API_REFERENCE.md` updated to point at MCPB/Tauri instead |
| **Webapp Directory Standard** (2026-07-11, v1.34) | ❌ | frontend is `web_sota/`, must be `webapp/` |
| **Bun Adoption Standard** | ❌ | justfile + scripts use npm/npx; `package-lock.json` committed, no `bun.lock` |
| **Biome replaces ESLint** | ⚠️ | Both configured; ESLint config + deps still present |
| **Release Tiers** | ❌ | no `RELEASE_TIER.md` (this repo is T3 — has NSIS) |
| Repo hygiene | ⚠️ | `htmlcov/`, `.lancedb/`, `.coverage`, `*.py.backup`, `test_output.txt`, `src/lib.rs`+root `Cargo.toml` (Zed ext) clutter root; egg-info in tree |
| glama.json health metadata | ⚠️ | no fleet-grading health block |

---

## Improvement plan (priority order)

| Priority | Item | Effort (AI-assisted) |
|----------|------|----------------------|
| ~~P1~~ ✅ | ~~ResoniteLink 0.9–0.13 compatibility pass~~ — **done in v1.1.0** (full rewrite to the real wire format + discovery + sync methods; live wire test against a running session still pending) | done 2026-07-11 |
| ~~P1~~ ✅ | ~~Remove `dxt/` (DXT retired fleet-wide)~~ — **done 2026-07-19** | done |
| **P2** | Fix `protoflux_helpers.py` honesty gap: `analyze_script`/`debug_session` assume fictional `/protoflux/analyze` OSC listener; `generate_template`/`optimize_script` are static text, not real inspection (see 2026-07-30 section above) | half day |
| **P2** | `web_sota/` → `webapp/` rename (new fleet standard v1.34; touches justfile, start.ps1, gitignore, tauri/native scripts, docs) | half day, mechanical |
| **P2** | Bun migration: `bun install`/`bunx` in justfile + scripts, commit `bun.lock`, delete `package-lock.json`; drop ESLint config/deps (Biome only) | half day |
| **P2** | `RELEASE_TIER.md` (T3) + glama.json health metadata | minutes |
| **P3** | Purge committed artifacts (`htmlcov/`, `.lancedb/`, `.coverage`, `*.py.backup`, `test_output.txt`) from git index — gitignore now covers them | minutes |
| **P3** | Live E2E with Resonite (`--live --strict`); real inventory OSC responses (adapter live mode) | operator session |
| **P3** | Voice macros mapped to in-world ProtoFlux bindings | 1 day |
| **P4** | Raise coverage on `integrations.py`, `osc.py` toward 70%+ | 1 day |

---

## References

- [ROADMAP.md](docs/ROADMAP.md)
- [RESONITELINK_GUIDE.md](docs/RESONITELINK_GUIDE.md) — upstream gap table
- [MCPB.md](docs/MCPB.md)
- [MCP Central — MCPB standards](file:///D:/Dev/repos/mcp-central-docs/standards/MCPB_PACKAGING_STANDARDS.md)
- [Webapp Directory Standard](file:///D:/Dev/repos/mcp-central-docs/standards/WEBAPP_DIRECTORY_STANDARD.md)
- [Release Tiers](file:///D:/Dev/repos/mcp-central-docs/standards/RELEASE_TIERS.md)
