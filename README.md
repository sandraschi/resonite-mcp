# Resonite MCP Server

**FastMCP 2.13.1+ compliant server for natural language control of Resonite social VR platform.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 2.13.1+](https://img.shields.io/badge/FastMCP-2.13.1+-green.svg)](https://gofastmcp.com/)
[![Status](https://img.shields.io/badge/status-beta-blue.svg)](#)

## Overview

The Resonite MCP Server provides comprehensive integration between Claude Desktop and the Resonite social VR platform. Through natural language commands, users can control avatars, manage worlds, execute ProtoFlux scripts, and participate in social interactions within Resonite.

### Key Features

- **Avatar Control**: Load avatars, set parameters, control animations
- **World Management**: Load/save worlds, manage sessions
- **ProtoFlux Scripting**: Create and execute visual scripts in real-time
- **OSC Communication**: Bidirectional communication with Resonite via OSC protocol
- **Session Management**: Start, monitor, and end Resonite sessions
- **Inventory Management**: Browse, search, spawn, and manage user assets
- **Plugin System**: Extensible architecture with OSC and ProtoFlux plugins
- **Dual Interface**: Both MCP stdio protocol and HTTP REST API
- **Real-time Feedback**: Live parameter monitoring and event handling

### Architecture

This server follows FastMCP 2.13+ SOTA standards with:
- Portmanteau tool organization for complex operations
- Pydantic input validation for all tools
- Comprehensive error handling and logging
- Dual MCP/stdio and HTTP/FastAPI interfaces
- Plugin system for extensibility

### Implementation Status

- **✅ Core OSC Communication**: 8 tools fully implemented
- **✅ Avatar Control**: 3 tools fully implemented
- **✅ Session Management**: 4 tools (3 fully implemented, 1 mock)
- **⚠️ Inventory Management**: 7 tools (structure complete, mock responses)
- **⚠️ Plugin Management**: 5 tools (structure complete, mock responses)
- **✅ System Tools**: 3 tools fully implemented
- **✅ Health Monitoring**: 1 tool fully implemented

**Total: 31 tools (13 fully functional, 15 with mock responses, 3 documentation)**

## Installation

### Prerequisites

- Python 3.8+
- Resonite client installed and running
- OSC enabled in Resonite settings (default port 9000)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/sandraschi/resonite-mcp.git
cd resonite-mcp

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import resonite_mcp; print('✅ Installation successful')"
```

### Install from PyPI (future)

```bash
pip install resonite-mcp
```

## Quick Start

### 1. Start the MCP Server

**For Claude Desktop (stdio mode):**
```bash
resonite-mcp --stdio
```

**For HTTP API mode:**
```bash
resonite-mcp --host 127.0.0.1 --port 8000
```

### 2. Configure Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resonite": {
      "command": "python",
      "args": ["-m", "resonite_mcp"],
      "env": {}
    }
  }
}
```

### 3. Start Using Resonite

Once configured, you can use natural language commands like:

- "Load the default avatar in Resonite"
- "Start a new session and load the tutorial world"
- "Set my avatar's happiness to 80%"
- "Execute the color changer ProtoFlux script"

## Documentation

### For Beginners
- **[Beginner's Guide](./BEGINNERS_GUIDE.md)** - Complete guide for total newcomers to Resonite
- **[ProtoFlux Guide](./PROTOFLUX_GUIDE.md)** - Comprehensive guide to visual programming
- **[Platform Comparison](./RESONITE_COMPARISON.md)** - How Resonite compares to VRChat, AltspaceVR, etc.
- **[Installation Guide](./docs/INSTALLATION.md)** - Step-by-step setup instructions
- **[Troubleshooting](./docs/TROUBLESHOUTING.md)** - Common issues and solutions

### For Developers
- **[API Reference](./docs/API_REFERENCE.md)** - Complete tool documentation
- **[HTTP API](http://127.0.0.1:8000/docs)** - Interactive REST API documentation

---

## Usage Examples

### Basic Session Management

```python
# Start a new Resonite session
await resonite_session_start(session_name="MySession")

# Load a world
await resonite_world_load("resonite://TutorialWorld")

# Load an avatar
await resonite_avatar_load("resonite://DefaultAvatar", slot=0)

# Set avatar parameters
await resonite_parameter_set("Happy", 0.8)
await resonite_parameter_set("Angry", 0.2)
```

### ProtoFlux Scripting

```python
# Execute a ProtoFlux script
await resonite_protoflux_execute("ColorChanger", {
    "target_color": [1.0, 0.5, 0.0],
    "transition_time": 2.0
})
```

### OSC Communication

```python
# Send custom OSC messages
await send_osc("127.0.0.1", 9000, "/avatar/parameters/CustomParam", [0.75])

# Start OSC server for receiving messages
await start_osc_server(9001)
```

## API Reference

### Available Tools (31 total)

#### Session Management (4 tools)
- `resonite_session_start(session_name?, world_path?, avatar_slot?)` - Start new Resonite session
- `resonite_session_status()` - Get current session status
- `resonite_session_end()` - End current session
- `resonite_world_load(world_path)` - Load a world in the session

#### Avatar Control (3 tools)
- `resonite_avatar_load(avatar_path, slot?, parameters?)` - Load avatar with optional parameters
- `resonite_parameter_set(parameter_name, value, avatar_slot?)` - Set avatar parameter value
- `resonite_protoflux_execute(script_name, parameters?)` - Execute ProtoFlux script

#### Inventory Management (7 tools)
- `resonite_inventory_list(item_type?, search_query?, limit?, offset?)` - List inventory items
- `resonite_inventory_search(query, item_type?)` - Search inventory by query
- `resonite_inventory_spawn(item_data)` - Spawn item in world
- `resonite_inventory_upload(file_data)` - Upload item to inventory
- `resonite_inventory_delete(item_data)` - Delete item from inventory
- `resonite_inventory_share(item_data)` - Share item with users
- `resonite_inventory_info(item_id)` - Get detailed item information

#### OSC Communication (8 tools)
- `send_osc(host, port, address, values?)` - Send OSC message
- `start_osc_server(port, address?)` - Start OSC server for receiving
- `stop_osc_server(port)` - Stop OSC server
- `get_received_messages(port, address_pattern?, max_age_seconds?, limit?)` - Get received messages
- `get_latest_message(port, address_pattern?)` - Get most recent message
- `get_osc_server_stats(port)` - Get server statistics
- `clear_osc_message_buffer(port)` - Clear message buffer
- `test_osc_echo(port?)` - Test OSC connectivity

#### Plugin Management (5 tools)
- `plugin_list()` - List all available plugins
- `plugin_load(plugin_name)` - Load a plugin
- `plugin_unload(plugin_name)` - Unload a plugin
- `plugin_reload(plugin_name)` - Reload a plugin
- `plugin_discover()` - Discover available plugins
- `plugin_info(plugin_name?)` - Get plugin information

#### System Tools (3 tools)
- `help(level?, topic?)` - Get help documentation
- `status(level?, focus?)` - Get server status information
- `health_check()` - Health check endpoint

### HTTP API Endpoints

When running in HTTP mode (`resonite-mcp --host 127.0.0.1 --port 8000`), the following REST endpoints are available:

#### Server Management
- `GET /` - Server information and API overview
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive FastAPI documentation

#### OSC Communication
- `POST /osc/send` - Send OSC messages to Resonite
- `POST /osc/server/start` - Start OSC server for receiving messages
- `POST /osc/server/stop` - Stop OSC server

#### Session Management
- `POST /resonite/session/start` - Start new Resonite session
- `GET /resonite/session/status` - Get current session status
- `POST /resonite/session/end` - End current session
- `POST /resonite/world/load` - Load a world in the session

#### Avatar Control
- `POST /resonite/avatar/load` - Load avatar with optional parameters
- `POST /resonite/parameter/set` - Set avatar parameter value
- `POST /resonite/protoflux/execute` - Execute ProtoFlux script

#### Inventory Management
- `GET /resonite/inventory/list` - List inventory items with pagination
- `GET /resonite/inventory/search` - Search inventory by query
- `POST /resonite/inventory/spawn` - Spawn item in world
- `POST /resonite/inventory/upload` - Upload item to inventory
- `DELETE /resonite/inventory/delete` - Delete item from inventory
- `POST /resonite/inventory/share` - Share item with other users
- `GET /resonite/inventory/info/{item_id}` - Get detailed item information

#### Plugin Management
- `GET /plugins/list` - List all available plugins
- `GET /plugins/discover` - Discover new plugins
- `POST /plugins/load` - Load a specific plugin
- `POST /plugins/unload` - Unload a specific plugin
- `POST /plugins/reload` - Reload a specific plugin
- `GET /plugins/info` - Get plugin information

## Configuration

### Environment Variables

- `RESONITE_OSC_HOST` - Resonite OSC host (default: 127.0.0.1)
- `RESONITE_OSC_PORT` - Resonite OSC port (default: 9000)
- `LOG_LEVEL` - Logging level (default: INFO)

### Resonite Setup

1. **Enable OSC in Resonite:**
   - Open Resonite Settings
   - Go to "Network" tab
   - Enable "OSC" and set port to 9000
   - Optionally enable "Receive OSC" for bidirectional communication

2. **Grant Permissions:**
   - Allow Resonite to accept OSC connections
   - Configure firewall if necessary

## Development

### Project Structure

```
resonite-mcp/
├── src/resonite_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # Main MCP server with all tools
│   ├── cli.py               # Command-line interface
│   └── http_server.py      # FastAPI HTTP server
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Pytest configuration
├── docs/                    # Documentation
├── examples/                # Usage examples
├── scripts/                 # Development scripts
├── assets/prompts/          # MCP prompt templates
└── pyproject.toml          # Project configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=resonite_mcp --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Development Server

```bash
# Run with auto-reload for development
resonite-mcp --host 127.0.0.1 --port 8000

# Access API docs at http://127.0.0.1:8000/docs
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest`
5. Update documentation as needed
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public functions
- Add unit tests for all new functionality
- Update documentation for any user-facing changes

## Troubleshooting

### Common Issues

**Server won't start:**
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -e ".[dev]"`
- Verify Resonite is running and OSC is enabled

**OSC connection fails:**
- Confirm Resonite OSC settings (port 9000 by default)
- Check firewall settings allow UDP traffic
- Verify Resonite is accepting OSC connections

**Tools not available in Claude:**
- Restart Claude Desktop after configuration changes
- Check `claude_desktop_config.json` syntax
- Verify server path is correct

**HTTP API not responding:**
- Confirm server is running: `curl http://127.0.0.1:8000/health`
- Check port is not already in use
- Verify CORS settings if accessing from browser

### Debug Mode

Enable debug logging:

```bash
resonite-mcp --log-level DEBUG --stdio
```

Or set environment variable:
```bash
LOG_LEVEL=DEBUG resonite-mcp --stdio
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Resonite](https://resonite.com/) - The amazing social VR platform
- [Yellow Dog Man Studios](https://yellowdogman.com/) - Creators of Resonite
- [FastMCP](https://gofastmcp.com/) - The MCP framework powering this server
- [python-osc](https://pypi.org/project/python-osc/) - OSC protocol implementation

## Recent Updates (v0.1.0)

### ✅ **Completed in December 2025**
- Fixed MCP stdio mode startup issues
- Corrected Cursor IDE configuration (use "mcp" not "mcpServers")
- Resolved Windows binary mode interference with MCP protocol
- Added comprehensive HTTP API endpoints (25+ endpoints)
- Implemented 31 MCP tools with proper FastMCP 2.13.1+ compliance

### 🔧 **Implementation Status**
- **13 tools fully functional** (OSC communication, avatar control, session management)
- **15 tools with mock responses** (inventory, plugin management - structure complete)
- **3 documentation tools** (help, status, health check)
- **Dual interface support** (MCP stdio + HTTP REST API)

## Roadmap

### v0.2.0 (Next Release)
- [ ] Complete inventory management implementation
- [ ] Plugin system dynamic loading
- [ ] Social interaction tools
- [ ] Performance monitoring and metrics

### v0.3.0
- [ ] Web dashboard for HTTP mode
- [ ] Recording and playback of sessions
- [ ] Advanced ProtoFlux integration
- [ ] Multi-user session support

### Future
- [ ] Resonite cloud API integration
- [ ] Voice command processing
- [ ] AR/VR hardware integration
- [ ] Cross-platform mobile support

---

**Made with ❤️ for the Resonite community**
