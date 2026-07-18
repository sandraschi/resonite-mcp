# Resonite MCP Webapp — Update Plan (CORRECTED)

**Written**: 2026-07-18 · **Supersedes** the first version of this file,
which was wrong. Read the correction below before anything else — it
changes what actually needs doing.

## Correction — my own mistake, stated plainly

The first version of this plan checked `web_sota/backend/server.py` and
concluded the webapp's entire backend was fictional (5 real endpoints,
everything else 404s). That conclusion was **wrong**, because I checked
the wrong file. `web_sota/start.ps1` — the actual launcher — runs
`uv run python -m resonite_mcp --port 10979`, which (via `cli.py`) starts
`resonite_mcp.http_server:app`, a **separate, 1,699-line file** I hadn't
read. `web_sota/backend/server.py` is never launched by anything; it's
orphaned dead code sitting in the repo.

`http_server.py` implements 76 real routes, and the large majority of
them are genuinely wired to the real, honest `ResoniteLinkClient` — including
its "legacy compatibility" shims (`get_node`, `get_children`, `reflect`,
`read_field`, `destroy_slot`), which correctly translate old call shapes
onto the real protocol rather than faking anything. `write_field()` is
real too — it exists specifically to raise a clear, honest error
("writeField does not exist in ResoniteLink, use update_component
instead") rather than pretend to work. That's good engineering, not a bug.

**One finding flips entirely**: `Logging.tsx`, which the first version of
this plan called "the one genuinely functional page," is actually
**broken in production** — `/api/logs*` and the `ActivityLog` class only
exist in the orphaned `server.py`, not in `http_server.py`, which is what
actually runs. Grepped both files directly to confirm this, not assumed.

## Accurate page-by-page disposition (verified against http_server.py's real routes)

| Page | Status | Detail |
|---|---|---|
| `resonite_link.tsx` | **Mostly real** | connect/status/discover/field/children/reflect all call real code. Fix needed: defaults to guessed ports (4242, or the UI's own placeholder "37166") instead of calling the real `/rl/discover` first. Header wrongly claims protocol "v0.8.3" (real target is 0.13.1). |
| `world.tsx` | **Mostly real** | root/children/node/asset-files/vrm-files all real, scanning real directories. write-field/inject-file endpoints are real but honestly always fail (protocol has no generic file import) — same correct pattern as import-vrm's 501. |
| `avatar.tsx` | **Real** | all 5 endpoints exist, call real `http_functions`. |
| `protoflux.tsx` | **Mostly real** | shares resonite_link's real endpoints. |
| `osc.tsx` | **Real** | all 6 endpoints exist and are wired. |
| `control.tsx` | **Real** | both `/api/control/move` and `/api/control/view` exist, drive real OSC avatar parameters. |
| `map.tsx` | **Real** | reads a live `Root` slot tree, heuristically tags avatars vs. objects. |
| `rest_api.tsx` | **Real** | `/api/platform`, `/api/sessions` both real. |
| `agent-tools.tsx` | **Real, best-designed page in the app** | generic `/api/v1/tool` proxy to real `resonite_fleet`/`resonite_voice`/`health_check` — one endpoint, many real capabilities, no bespoke wiring needed per feature. |
| `status.tsx` | **Mixed** | platform/sessions real; `/api/start` is a wrong path (real one is `/api/resonite/start`); the log panel at the bottom is hardcoded mock data, admitted in the file's own code comment. |
| `dashboard.tsx` | **Mixed** | `/api/status` real; `/api/llm-discovery` and `/api/stats` don't exist; `/api/resonite/launch` is wrong (real path is `/api/resonite/start`); "65 tools" badge is a hardcoded, unverified number. |
| `inventory.tsx` / `io.tsx` | **Mixed** | spawn/delete calls are real; the main list-fetch hits a wrong path (`/api/records` — real one is `/api/resonite/inventory/list` or `/search`). |
| `integrations.tsx` | **Wrong paths + wrong request shape** | real capability exists at `/api/resonite/integrations/{worldlabs,blender,unity}` requiring a real body (`splat_url`, etc.); frontend calls `/api/integrations/...` (missing `resonite/`) with no body at all. |
| `scripting.tsx` | **Wrong endpoint, wrong model entirely** | real `/api/resonite/protoflux/execute` exists (named script + parameters); frontend calls a nonexistent sibling path with freeform arbitrary script text — needs a UI redesign around the real contract, not a URL fix. |
| `Logging.tsx` | **Broken in production** (surprising reversal) | its real implementation exists only in the orphaned `server.py`. |
| `contacts.tsx` | **Missing** | `/api/contacts` not implemented anywhere. |
| `search.tsx` | **Missing, admitted mock** | own code comment: "for now we mock the search behavior." |
| `settings.tsx` | **Missing + decorative** | `/api/llm/providers` doesn't exist; most fields (Neural Host, Auth Protocol, I/O Timeout, Log Retention) have no handler at all. |
| `tools.tsx` | **Missing, but cheaply buildable** | `/api/system` doesn't exist; the FastMCP server can enumerate its own real tools — building this would also retire the fabricated "65 tools" claim repeated in `dashboard.tsx` and `help.tsx`. |
| `marketplace.tsx` | **100% fictional** | hardcoded array, zero backend call, no real Resonite marketplace API exists to back it. |
| `apps.tsx` | **Stub** | no backend call, one dead button. |
| `help.tsx` | **Actively wrong, not just incomplete** | teaches the old fictional protocol (`ReadField`/`WriteField`/`GetNode`, port "4242 default"), repeats the unverified "65 tools" claim. |
| `sessions.tsx` | Not fully re-checked this pass | likely shares the real `/api/sessions`; confirm in Phase A. |

**Other real bugs found reading closely, unrelated to any single page**:
- `/api/sessions` is defined **twice** in `http_server.py` (a real
  ResoniteLink-session listing at line 584, and a real but *unreachable*
  proxy to `api.resonite.com/sessions` at line 1089 — FastAPI matches the
  first registered route, so the second never runs). Needs a decision:
  keep one, or mount both under distinct paths if they serve genuinely
  different data.

## Revised plan (much smaller than the first version)

### Phase A — Quick, mostly path/default fixes (half a day)
- Fix wrong paths: `dashboard.tsx`/`status.tsx`'s `/api/resonite/launch`
  and `/api/start` → `/api/resonite/start`; `integrations.tsx`'s paths +
  add the required request body; `inventory.tsx`/`io.tsx`'s list-fetch
  path.
- `resonite_link.tsx`/`world.tsx`/`protoflux.tsx`: call `/rl/discover`
  first and let the person pick a real session, instead of defaulting to
  a guessed port.
- Resolve the duplicate `/api/sessions` route.
- **Decide the fate of `Logging.tsx`**: port `ActivityLog` + `/api/logs*`
  from the orphaned `server.py` into `http_server.py` for real (it's a
  genuinely good feature, just stuck in a file nothing runs), or retire
  the page. Recommend porting it — cheap, and useful.
- Delete or clearly mark `web_sota/backend/server.py` as unused, so it
  stops being mistakable for the real backend (as it fooled me tonight).

### Phase B — Content correction, high value, low effort (an hour or two)
- Rewrite `help.tsx`'s Protocols tab: the real message-type table
  (`getSlot`/`addSlot`/`updateSlot`/`removeSlot`,
  `getComponent`/`addComponent`/`updateComponent`/`removeComponent`,
  `callSyncMethod`, the reflection methods, `dataModelOperationBatch`,
  the real asset-import types) and real port-discovery guidance (UDP
  12512 broadcast, not "default port 4242"). Drop the "65 tools" claim
  until Phase C makes it real.

### Phase C — Real backend builds (moderate effort, per item)
- `tools.tsx`: wire to real FastMCP tool introspection — also fixes the
  fabricated tool-count problem everywhere it's cited.
- `search.tsx`: decide build-for-real (check whether `test_rag.py`'s
  LanceDB infra at the repo root is usable) or cut.
- `scripting.tsx`: redesign around the real protoflux/execute contract
  (pick a named script, supply parameters) or cut if not wanted.
- `contacts.tsx`, `settings.tsx`'s LLM-provider picker: build-or-cut
  decisions — contacts needs real Resonite cloud auth wiring; the LLM
  picker could tie into the fleet's existing local-llm-mcp/DS4 detection.

### Phase D — Sandra's call, no urgency
- `marketplace.tsx`: recommend cutting — no real feature backs it.
- `apps.tsx`: recommend cutting or repurposing as a real "connected fleet
  servers" status page.

## Estimate

Phase A: ~0.5 day. Phase B: ~1-2 hours. Phase C: per-item, roughly
0.5-1 day each depending on which get greenlit. Phase D: no build effort,
just a decision.
