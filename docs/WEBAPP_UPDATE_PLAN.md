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

## Phase A progress (2026-07-19)

- [x] Fixed `dashboard.tsx`/`status.tsx`'s wrong `/api/resonite/launch` and
      `/api/start` → real `/api/resonite/start`.
- [x] Found and fixed a separate real bug while in there: Resonite's Steam
      launch URI was `steam://rungameid/251980` (missing a digit) —
      confirmed the real App ID (`2519830`) against SteamDB and the
      official store page.
- [x] Replaced fabricated "65 tools" (two places in `dashboard.tsx`) with
      an honest "not live-counted yet" state.
- [x] Removed `status.tsx`'s hardcoded mock log block (own code comment
      admitted it was fake) — now points to the real Logging page.
- [x] Resolved the duplicate `/api/sessions` route — moved the shadowed
      cloud-API proxy to `/api/resonite/cloud-sessions[/{id}]` so it's
      actually reachable.
- [x] `Logging.tsx` decision made: **ported**, not retired. New
      `src/resonite_mcp/activity_log.py` module (the same `ActivityLog`
      class, now actually importable from the real server), wired
      `/api/logs`, `/api/logs/stats`, `/api/logs/export`,
      `DELETE /api/logs` into `http_server.py`. Verified functionally
      (not just import-clean): called `get_logs()`/`logs_stats()`
      directly, confirmed the startup log entry flows through both.
- [x] Fixed stale "v0.8.x"/"port 4242 default" claims in `http_server.py`'s
      comments/docstrings and the FastAPI app's own declared version
      (was `0.8.0`, now `1.2.0`) to match the real 0.13.1 protocol.
- [x] Cleaned up a confusing double-definition of `RLWriteRequest` (same
      class name, two different shapes, one for `/rl/field` one for
      `/rl/world/write-field`) — renamed the second to
      `RLWorldWriteFieldRequest`. Worked correctly before due to Python's
      sequential class binding, but was a real fragility risk.
- [x] `resonite_link.tsx`: added a real "Discover Sessions" flow — calls
      `/rl/discover`, lists real sessions, click one to auto-fill host/port.
      Removed the meaningless hardcoded port default (`"37166"`, no basis
      at all) and replaced with an honest empty state + hint placeholder.
      Fixed the "Protocol v0.8.3" header claim to v0.13.1. Updated the
      Quick Reference table to include `/rl/discover` and clarify
      `/rl/field`'s real write requirement. Verified: `ruff`/`biome` both
      clean on every touched file, `tsc --noEmit` shows no new errors.

**Still open from Phase A**: `world.tsx`/`protoflux.tsx` could use the
same discover-first treatment (currently only `resonite_link.tsx` has
it); `integrations.tsx`'s wrong paths + missing request body;
`inventory.tsx`/`io.tsx`'s wrong list-fetch path; deciding
`web_sota/backend/server.py`'s fate (recommend deleting now that
`Logging.tsx`'s real logic has been ported out of it).

### Phase A, round 3 (2026-07-19)

- [x] **Found a genuinely worse bug in `world.tsx`'s Inspector than a
      wrong path**: its inline-edit fields (slot name, position, scale)
      called `/rl/world/write-field`, which — per tonight's own earlier
      finding — is *guaranteed* to always fail (`write_field()`
      deliberately raises with guidance, it isn't a real capability).
      Worse: the Inspector had **no error display at all**, so every
      edit silently did nothing with zero user feedback.
- [x] **Real fix, not a workaround**: `resonite_link.py` already has a
      working `update_slot()` method (used throughout tonight's
      Nekomimi-chan debugging to move/rotate real slots) that was never
      exposed via the webapp. Added `PATCH /rl/slot/{slot_id}` wired to
      it, rewired the Inspector to call that instead, and added real
      error display (was completely missing before). Position/Scale
      edits now use proper partial updates (merge into the existing
      vector, not full replacement). The "Active" toggle was removed
      rather than wired to a guessed field name — the correct protocol
      key for slot active-state wasn't confirmed, and after tonight's
      UV-discriminator experience, guessing at another undocumented
      field name isn't the right call; flagging as a known gap rather
      than silently keeping broken functionality.
      Verified: `ruff`/import-smoke on `http_server.py` (88 routes now),
      `biome --write` + manual `type="button"` fixes on `world.tsx`
      (6→3 remaining, all pre-existing drag-drop a11y issues
      deliberately left alone), `tsc --noEmit` shows no new errors.

### Phase A, round 4 (2026-07-19) — `integrations.tsx` + `inventory.tsx`

- [x] **`integrations.tsx`**: same class of bug as before — wrong paths
      (`/api/integrations/worldlabs/import` → real
      `/api/resonite/integrations/worldlabs`) AND missing request bodies
      the real endpoints require (`splat_url`, `object_name`,
      `avatar_path` are all mandatory fields, previously never sent).
      Added real input fields for each, wired to the correct bodies.
      Also removed a fully fabricated "Fleet Discovery Active" card
      claiming `worldlabs-mcp`/`blender-mcp`/`unity3d-mcp` are all
      "active" — there's no actual discovery mechanism behind it at all;
      replaced with an honest "not auto-detected" note.
- [x] **`inventory.tsx` — deeper than a path fix.** Traced the real
      backend (`tools/inventory.py`) and found the entire subsystem
      (list/spawn/upload/delete/share) is built on an OSC round-trip
      protocol requiring a custom in-world ProtoFlux responder that isn't
      confirmed to exist anywhere — a fundamentally different, much less
      mature mechanism than the real, working ResoniteLink capabilities
      built earlier tonight. On top of that, found and fixed a **real
      crash bug** affecting 5 of 7 inventory functions: `http_functions.py`
      called them with positional arguments, but the actual functions
      (in `tools/inventory.py`) each take a single Pydantic model —
      guaranteed `TypeError` on every call, before ever reaching the
      (also-questionable) OSC logic. Fixed all 5 call sites to construct
      the correct model. **Verified functionally, not just import-clean**:
      called `resonite_inventory_list_http()` directly — no more crash,
      returns the honest `{"status": "warning", "message": "Timed out
      waiting for Resonite..."}` response, which is the correct behavior
      when no responder exists.
      **Found something deeper while verifying**: the OSC send itself
      failed separately (`Infered arg_value type is not supported`) —
      the code passes a raw Python dict as an OSC argument value, which
      OSC's wire format doesn't support. This means `list`/`spawn`/
      `upload`/`share` (all of which pass dicts) are broken at the
      protocol-serialization layer too, independent of whether any
      responder exists. **Did not fix this** — it's real redesign work
      (e.g. JSON-encode the dict as a string arg, or split into
      primitive OSC args), correctly out of scope for a Phase A path-fix
      pass; documented here so it isn't lost.
      Rewired `inventory.tsx`'s fetch to the correct (now non-crashing)
      endpoint and response shape, and replaced the fabricated "Neural
      Storage Nexus" empty-state copy with the honest warning message
      surfaced from the backend.
      Verified: `ruff` clean on `http_functions.py`, `biome`+`tsc` clean
      on `inventory.tsx` (12 pre-existing button-type issues fixed via a
      safe bulk regex pass; 3 structural a11y issues on the record-grid's
      clickable-div pattern left alone, pre-existing, not part of this fix).

### Phase A round 5 (2026-07-19) — visual polish: hero + contrast

Sandra asked to avoid tiny/low-contrast fonts and improve the dashboard
hero specifically.

- [x] **`dashboard.tsx` hero rebuilt** — it previously had none of the
      visual treatment every other page uses (no icon box, no glow
      backdrop, no gradient title). Brought it in line: icon box, glow
      blur, `text-3xl font-black tracking-tighter` title matching
      `resonite_link.tsx`/`world.tsx`/`inventory.tsx`'s headers. Status
      badges changed from plain muted text to actual pill chips
      (background + border), which is both more legible and more
      visually prominent.
- [x] **Found and fixed a systemic contrast bug**: several places stacked
      `text-muted-foreground` *and* `opacity-50` on the same element —
      double-dimming already-muted text past comfortable reading
      contrast, on top of already-tiny sizes (8px/9px/10px). Fixed in
      `dashboard.tsx` (KPI card captions, System Status panel, LLM
      provider row, "Active" pill) and `status.tsx` (session ID hash,
      session stat row, "LIVE" badge) — sizes bumped to a 10px floor,
      opacity stacking removed, colors bumped one step brighter
      (`text-slate-400`/`text-indigo-300`/etc. instead of muted+50%).
- [x] Verified: `biome`+`tsc` clean on both files (pre-existing,
      unrelated `useExhaustiveDependencies`/`noArrayIndexKey` issues on
      `dashboard.tsx` left alone, same policy as every other file
      tonight).

**Not done — flagging as a real, separate scope**: the same
tiny-text/opacity-stacking pattern (`text-[8px]`/`text-[9px]` combined
with `opacity-50` on top of an already-muted color) almost certainly
exists across some of the other 20+ pages not touched tonight. A full
sweep is a legitimate, bounded follow-up task — a simple repo-wide grep
for `text-\[[89]px\]` and `opacity-50` co-occurring with text color
classes would find them all quickly; not attempted here since it's a
different scope than tonight's Phase A functional-bug fixes.

## Estimate

Phase A: ~0.5 day. Phase B: ~1-2 hours. Phase C: per-item, roughly
0.5-1 day each depending on which get greenlit. Phase D: no build effort,
just a decision.
