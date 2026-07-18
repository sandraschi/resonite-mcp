# resonite-mcp 1.2.0 — 2026-07-18/19 — Live Asset & Audio Pipeline, Webapp Audit

## Live-verified additions
- `utils/gltf_meshjson.py` + `utils/stl_meshjson.py` + `utils/decimate_meshjson.py`
  — stdlib-only mesh converters and decimation, proven against real fixtures
  (Marble colliders, Boomy's chassis STL, Nekomimi-chan's full VRM at
  45,451 triangles with no decimation needed).
- `ResoniteLinkClient.import_audio_clip_file()` / `.spawn_audio()` — full
  audio pipe (import → StaticAudioClip → AudioClipPlayer → AudioOutput,
  autoplay), live-verified with a stdlib-generated test tone.
- `uvs` wire shape corrected to a list of coordinate objects (was
  incorrectly assumed to be a bare dict) — confirmed via live server error.

## Known limitations, explicit
- UV_Coordinate's polymorphic `$type` discriminator still unknown after
  4 live attempts — blocks textured (non-solid) materials generally.
- VRM bones/blendshapes unparsed — static geometry only so far.
- `import_mesh_raw()` still unimplemented (binary payload frame needed).

## Webapp audit correction
- Self-corrected a same-session mistake: the webapp's real backend is
  `http_server.py` (76 routes, mostly real), not the never-launched
  `web_sota/backend/server.py` initially checked. Full findings and a
  phased fix plan in `docs/WEBAPP_UPDATE_PLAN.md`, including one page
  (`Logging.tsx`) that turned out to be broken in production the *other*
  way — its real code sits only in the unused file.
