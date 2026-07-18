# resonite-mcp 1.1.0 — 2026-07-11 — Real ResoniteLink Protocol (0.13.1)

## Live verification (2026-07-18, docs-only update)
- First live E2E against a running session: Resonite 2026.7.14.913, protocol
  0.13.1.0 — discovery, connect, read (Root + components), write (slot with
  position, readback-verified). Zero client fixes. The 07-11 rewrite against
  upstream 0.13.1 was exactly right.
- Field lesson: the in-game dashboard's displayed port did not match the real
  linkPort; UDP discovery (12512) is authoritative.
- Next: wrap asset imports (importMeshJSON / importTexture2DFile / audio) as
  first-class client methods + live-test with blender-mcp-exported geometry.

## BREAKING / Fixed
- Complete ResoniteLink client rewrite: the old client spoke a fictional wire format that never existed upstream. Now implements the verified real protocol (0.13.1): `$type` discriminators, `messageId`/`sourceMessageId` correlation, typed value wrappers, camelCase messages.
- Legacy method names kept as compatibility mappings onto real messages.
- Per-field-ref writes and generic model import (VRM/GLB) do not exist in the protocol — those paths now fail honestly (501/not_implemented) instead of fake-success.

## Added
- LAN session discovery (UDP 12512, protocol 0.12.0) — tool `resonite_link_discover`, `GET /rl/discover`
- Sync method calls (protocol 0.11.0) — `resonite_link_call_method`
- Reflection: component type list / component / type / enum definitions
- Value helpers `rl_value` / `rl_ref` / `rl_auto`; session metadata on connect
- 22 wire-format regression tests locking the protocol shapes

## Changed
- `POST /rl/field` requires `member`; `GET /rl/field/{id}` returns full component data
- `resonite_link_spawn` creates named slots; template-URL spawning returns not_implemented
