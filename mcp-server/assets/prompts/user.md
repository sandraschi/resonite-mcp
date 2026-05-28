# Resonite MCP — user prompt patterns

Use these patterns when the user asks for Resonite, social VR, avatars, worlds, or fleet imports.

## Discovery

- "What can you do in Resonite?" → `health_check`, `resonite_fleet(list_presets)`, summarize OSC + fleet + voice.
- "Is Resonite running?" → `resonite_fleet(execution_mode)`.

## Staging and UI

- "Import my inkscape UI icons" → `pull_inkscape_ui` with `input_dir` / `staging_dir`.
- "What's staged?" → `list_staging`.
- "Import everything in staging" → `import_staged_assets`.

## Avatars and VRM

- "Import VRM avatars from staging" → `list_vrm_staging` then `import_vrm_batch`.
- "Pull VRM from blender Cube" → `pull_blender_vrm(object_name="Cube")`.
- "Get avatar from avatar-mcp" → `pull_avatar_vrm`.

## Worlds and Marble

- "Import marble splats" → `list_marble_staging` then `import_worldlabs_batch`.
- "Run full marble pipeline" → `run_marble_pipeline`.
- "Load world X" → `resonite_world_load(world_path="resonite://...")` only if Resonite is running.

## Voice and macros

- "Wave hello" → `resonite_voice(parse_command)` then `send_macro` if user confirms in-world action.
- "List voice commands" → `resonite_voice(list_macros)`.

## Full pipelines

- "Run fleet pipeline skipping blender" → `run_fleet_pipeline(skip_blender=True, ...)`.
- "Strict E2E test" → `run_strict_fleet_pipeline` with explicit paths.

## Inventory

- "Show my inventory" → `inventory_status`; explain mock vs live mode if needed.

Always confirm destructive or in-world actions before `send_macro` or live imports when execution_mode is hands_off.
