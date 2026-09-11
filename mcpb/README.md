# resonite-mcp (MCPB Bundle)

Resonite social VR platform MCP server for natural language control of avatars, worlds, and ProtoFlux scripting

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "resonite-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "resonite_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **health_check**: health_check
- **api_v1_tool**: api_v1_tool
- **get_logs**: Query the activity log.
- **logs_stats**: Get activity log statistics (counts by level/kind).
- **logs_export**: Export the activity log as JSON or CSV.
- **clear_logs**: Clear the activity log.
- **root**: Root endpoint with server information.
- **get_osc_status**: Get status of all running OSC servers.
- **send_osc_message_route**: Send an OSC message.
- **start_osc_server_endpoint**: Start an OSC server.
- **stop_osc_server_endpoint**: Stop an OSC server.
- **get_received_messages_endpoint**: Get received OSC messages.
- **clear_osc_buffer_endpoint**: Clear the OSC message buffer for a specific port.
- **start_resonite_session**: Start a new Resonite session.
- **get_session_status**: Get current session status.
- **load_avatar**: Load an avatar.
- **get_avatar_info**: Get current avatar info.
- **set_parameter**: Set an avatar parameter.
- **reset_avatar_pose**: Reset avatar pose.
- **set_avatar_locomotion**: Set avatar locomotion mode.
- **kill_avatar_sequences**: Kill all avatar sequences.
- **execute_protoflux**: Execute a ProtoFlux script.
- **load_world**: Load a world.
- **end_session**: End the current session.
- **get_platform_info**: Get Resonite platform information.
- **list_sessions**: List public Resonite sessions.
- **get_contacts**: Get Resonite contacts list.
- **start_resonite**: Launch Resonite application.
- **get_system_status_api**: Get full system status.
- **import_worldlabs**: Import a WorldLabs splat from URL into Resonite.      Downloads the SPZ/GLB from the bridge proxy...
- **import_blender**: Import Blender object.
- **sync_unity_avatar**: Sync Unity avatar.
- **list_inventory**: List inventory items.
- **search_inventory**: Search inventory items.
- **spawn_inventory_item**: Spawn an inventory item.
- **upload_inventory_item**: Upload an item to inventory.
- **delete_inventory_item**: Delete an inventory item.
- **share_inventory_item**: Share an inventory item.
- **get_inventory_item_info**: Get detailed information about an inventory item.
- **get_resonite_gallery**: Retrieve gallery items (screenshots).
- **list_plugins**: List all loaded plugins.
- **discover_plugins**: Discover available plugins.
- **load_plugin_endpoint**: Load a plugin.
- **unload_plugin_endpoint**: Unload a plugin.
- **reload_plugin_endpoint**: Reload a plugin.
- **get_plugin_info**: Get plugin information.
- **rl_connect**: Connect to ResoniteLink WebSocket in Resonite. Prefer calling     /rl/discover first and passing ...
- **rl_disconnect**: Disconnect from ResoniteLink.
- **rl_status**: Get ResoniteLink connection status and session info.
- **rl_discover**: Discover ResoniteLink sessions on the LAN (UDP 12512, protocol 0.12.0+).
- **rl_read_field**: Read a component's data (type + members) by component ID.
- **rl_write_field**: Write one member on a component (updateComponent). Requires 'member'.
- **rl_get_node**: Get slot or component info by ref ID.
- **rl_get_children**: List direct children of a slot.
- **rl_add_slot**: Add a named child slot under a parent slot.
- **rl_add_component**: Add a component to a slot. component_type is the fully-qualified C# type name.
- **rl_update_slot**: Update a slot's name/position/rotation/scale. Only send fields you want changed.
- **rl_destroy_slot**: Destroy a slot and all its children.
- **rl_batch**: Execute multiple ResoniteLink operations atomically (dataModelOperationBatch, protocol 0.13.1).
- **rl_reflect**: Reflection API (protocol 0.13.1).     Without component_type: list all supported component types....
- **list_cloud_sessions**: list_cloud_sessions
- **get_cloud_session**: Get full metadata for a specific public session.
- **world_root**: Get the Root slot of the currently connected Resonite world.
- **world_children**: List direct children of any slot (use 'Root' for top level).
- **world_node**: Get full slot/component data by ref ID.
- **world_write_field**: Update a specific field/property in Resonite.
- **inject_file**: inject_file
- **list_asset_files**: Scan the canonical asset directory for a given category.      Categories:       avatars      → ~/...
- **list_vrm_files**: Scan ~/.avatarmcp/models/ for .vrm files.     Returns list of {name, path, size_bytes} objects.  ...
- **import_vrm**: Inject a VRM avatar into the connected world.      NOT IMPLEMENTED: ResoniteLink (protocol 0.13.1...
- **control_move**: Control avatar movement.     Sends OSC messages to Resonite (typically localhost:9000).     Requi...
- **control_view**: Toggle first/third person view.     Requires 'ThirdPerson' parameter in the avatar.
- **world_map_data**: Get spatial data for 2D map visualization.     Scans the world for active users and important slots.
- **start_worldlabs_listener**: start_worldlabs_listener
- **stop_worldlabs_listener**: stop_worldlabs_listener
- **detect_resonite_platform**: detect_resonite_platform
- **get_protoflux_graph**: get_protoflux_graph
- **list_vbot_types_route**: list_vbot_types_route
- **get_vbot_receiver_spec**: get_vbot_receiver_spec
- **test_vbot_receiver**: test_vbot_receiver
- **search_guides**: search_guides
- **ask_resonite**: ask_resonite
- **agentic_plan_execute**: agentic_plan_execute
- **main_stdio**: main(stdio)
- **main_http**: main(http)
- **main_sse**: main(sse)
- **osc_monitor_start**: osc_monitor_start
- **osc_batch_send**: osc_batch_send
- **osc_record_session**: osc_record_session
- **osc_analyze_traffic**: osc_analyze_traffic
- **protoflux_analyze_script**: protoflux_analyze_script
- **protoflux_generate_template**: protoflux_generate_template
- **protoflux_debug_session**: protoflux_debug_session
- **protoflux_optimize_script**: protoflux_optimize_script
- **protoflux_document_script**: protoflux_document_script
- **resonite_avatar_load**: resonite_avatar_load
- **resonite_parameter_set**: resonite_parameter_set
- **resonite_protoflux_execute**: resonite_protoflux_execute
- **resonite_fleet**: resonite_fleet
- **pull_inkscape_fab**: pull_inkscape_fab
- **import_worldlabs_batch**: import_worldlabs_batch
- **pull_inkscape_ui**: pull_inkscape_ui
- **import_staged_assets**: import_staged_assets
- **import_blender_asset**: import_blender_asset
- **import_gimp_texture**: import_gimp_texture
- **pull_blender_vrm**: pull_blender_vrm
- **import_vrm_batch**: import_vrm_batch
- **run_marble_pipeline**: run_marble_pipeline
- **inventory_status**: inventory_status
- **voice_parse_command**: voice_parse_command
- **resonite_inventory_list**: resonite_inventory_list
- **resonite_inventory_search**: resonite_inventory_search
- **resonite_inventory_spawn**: resonite_inventory_spawn
- **resonite_inventory_upload**: resonite_inventory_upload
- **resonite_inventory_delete**: resonite_inventory_delete
- **resonite_inventory_share**: resonite_inventory_share
- **resonite_inventory_info**: resonite_inventory_info
- **send_osc**: send_osc
- **start_osc_server**: start_osc_server
- **stop_osc_server**: stop_osc_server
- **get_received_messages**: get_received_messages
- **get_latest_message**: get_latest_message
- **get_osc_server_stats**: get_osc_server_stats
- **clear_osc_message_buffer**: clear_osc_message_buffer
- **test_osc_echo**: test_osc_echo
- **plugin_list**: plugin_list
- **plugin_load**: plugin_load
- **plugin_unload**: plugin_unload
- **plugin_reload**: plugin_reload
- **plugin_discover**: plugin_discover
- **plugin_info**: plugin_info
- **resonite_dashboard_card**: resonite_dashboard_card
- **resonite_inventory_card**: resonite_inventory_card
- **resonite_link_discover**: resonite_link_discover
- **resonite_link_connect**: resonite_link_connect
- **resonite_link_get_slot**: resonite_link_get_slot
- **resonite_link_get_node**: resonite_link_get_node
- **resonite_link_get_children**: resonite_link_get_children
- **resonite_link_add_slot**: resonite_link_add_slot
- **resonite_link_destroy_slot**: resonite_link_destroy_slot
- **resonite_link_add_component**: resonite_link_add_component
- **resonite_link_read_field**: resonite_link_read_field
- **resonite_link_write_field**: resonite_link_write_field
- **resonite_link_call_method**: resonite_link_call_method
- **resonite_link_reflect**: resonite_link_reflect
- **resonite_link_batch**: resonite_link_batch
- **resonite_link_import_mesh_json**: resonite_link_import_mesh_json
- **resonite_link_import_texture**: resonite_link_import_texture
- **resonite_link_spawn_mesh**: resonite_link_spawn_mesh
- **resonite_link_spawn**: resonite_link_spawn
- **resonite_link_set**: resonite_link_set
- **resonite_link_get**: resonite_link_get
- **resonite_rest_login**: resonite_rest_login
- **resonite_rest_get_sessions**: resonite_rest_get_sessions
- **resonite_rest_get_user**: resonite_rest_get_user
- **resonite_rest_get_records**: resonite_rest_get_records
- **resonite_rest_send_message**: resonite_rest_send_message
- **resonite_rest_get_platform**: resonite_rest_get_platform
- **resonite_cloud_var_list**: resonite_cloud_var_list
- **resonite_cloud_var_get**: resonite_cloud_var_get
- **resonite_cloud_var_set**: resonite_cloud_var_set
- **resonite_cloud_var_delete**: resonite_cloud_var_delete
- **resonite_friends_list**: resonite_friends_list
- **resonite_friend_requests**: resonite_friend_requests
- **resonite_friend_presence**: resonite_friend_presence
- **resonite_session_start**: resonite_session_start
- **resonite_session_status**: resonite_session_status
- **resonite_world_load**: resonite_world_load
- **resonite_session_end**: resonite_session_end
- **help**: help
- **status**: status
- **resonite_vbot_list_types**: resonite_vbot_list_types
- **resonite_vbot_spawn**: resonite_vbot_spawn
- **resonite_vbot_move**: resonite_vbot_move
- **resonite_vbot_head**: resonite_vbot_head
- **resonite_vbot_stop**: resonite_vbot_stop
- **resonite_voice**: resonite_voice
- **_api_metrics**: _api_metrics
- **_metrics_endpoint**: _metrics_endpoint

## Requirements

- Python 3.12+
- uv
