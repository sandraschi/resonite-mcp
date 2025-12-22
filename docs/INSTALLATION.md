# Resonite MCP Installation Guide

This guide provides step-by-step instructions for installing and configuring the Resonite MCP server for use with Claude Desktop and Cursor IDE.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Resonite**: Latest version installed and running
- **Network**: OSC port 9000 available (default Resonite OSC port)

### Resonite Setup

1. **Install Resonite** from [Steam](https://store.steampowered.com/app/2519830/Resonite/)
2. **Enable OSC** in Resonite settings:
   - Open Resonite Settings (Menu → Settings)
   - Navigate to "Network" tab
   - Enable "OSC" option
   - Set OSC Port to `9000` (default)
   - Optionally enable "Receive OSC" for bidirectional communication

## Installation Methods

### Method 1: Direct Installation (Recommended)

#### 1. Clone the Repository

```bash
git clone https://github.com/sandraschi/resonite-mcp.git
cd resonite-mcp
```

#### 2. Install Dependencies

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install minimal version for production
pip install -e .
```

#### 3. Verify Installation

```bash
python -c "import resonite_mcp; print('✅ Installation successful')"
```

### Method 2: DXT Package (Claude Desktop)

#### 1. Build the DXT Package

```powershell
# On Windows PowerShell
.\scripts\build_dxt.ps1
```

#### 2. Install in Claude Desktop

1. Locate your Claude Desktop extensions directory:
   - **Windows**: `%APPDATA%\Claude\extensions\`
   - **macOS**: `~/Library/Application Support/Claude/extensions/`
   - **Linux**: `~/.config/Claude/extensions/`

2. Copy the `dist` folder to the extensions directory:
   ```bash
   cp -r dist /path/to/claude/extensions/resonite-mcp
   ```

3. Restart Claude Desktop

4. The Resonite MCP tools should now be available

## Configuration

### Claude Desktop Configuration

Add the following to your `claude_desktop_config.json`:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "resonite": {
      "command": "python",
      "args": ["-m", "resonite_mcp"],
      "env": {
        "RESONITE_OSC_HOST": "127.0.0.1",
        "RESONITE_OSC_PORT": "9000"
      }
    }
  }
}
```

### Cursor IDE Configuration

Add to your Cursor settings JSON:

**Windows**: `%APPDATA%\Cursor\User\settings.json`
**macOS**: `~/Library/Application Support/Cursor/User/settings.json`
**Linux**: `~/.config/Cursor/User/settings.json`

```json
{
  "mcp": {
    "resonite": {
      "command": "python",
      "args": ["-m", "resonite_mcp", "--stdio"],
      "cwd": "D:\\Dev\\repos\\resonite-mcp",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Environment Variables

Optional environment variables for customization:

- `RESONITE_OSC_HOST`: OSC server hostname (default: 127.0.0.1)
- `RESONITE_OSC_PORT`: OSC server port (default: 9000)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Testing the Installation

### 1. Start the MCP Server

**MCP Mode (for Claude Desktop/Cursor):**
```bash
resonite-mcp --stdio
```

**HTTP API Mode:**
```bash
resonite-mcp --host 127.0.0.1 --port 8000
```

### 2. Test OSC Connection

```bash
# Send a test OSC message
curl -X POST http://127.0.0.1:8000/osc/send \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1", "port": 9000, "address": "/test", "values": ["hello"]}'
```

### 3. Test Resonite Session

```bash
# Start a test session
curl -X POST http://127.0.0.1:8000/resonite/session/start \
  -H "Content-Type: application/json" \
  -d '{"session_name": "test_session"}'
```

### 4. Verify in Claude/Cursor

Try these commands in Claude Desktop or Cursor:

- "Start a Resonite session"
- "Load the default avatar"
- "Set happy parameter to 0.8"
- "Execute a ProtoFlux script called test"

## Troubleshooting

### Common Issues

#### "Module 'resonite_mcp' not found"
- Ensure you're in the correct directory or PYTHONPATH is set
- Try: `pip install -e .`

#### "OSC connection failed"
- Verify Resonite is running
- Check OSC settings in Resonite (port 9000)
- Ensure firewall allows UDP traffic on port 9000

#### "Port already in use"
- Find and stop conflicting processes:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F

  # Linux/macOS
  lsof -i :8000
  kill -9 <PID>
  ```

#### "Permission denied" (Linux/macOS)
- OSC ports below 1024 require root: use port 9000+ instead
- Check file permissions on the installation directory

### Debug Mode

Enable verbose logging:

```bash
# MCP mode with debug
LOG_LEVEL=DEBUG resonite-mcp --stdio

# HTTP mode with debug
LOG_LEVEL=DEBUG resonite-mcp --host 127.0.0.1 --port 8000
```

### Checking OSC Traffic

Monitor OSC messages:

```bash
# Start OSC server to monitor traffic
curl -X POST http://127.0.0.1:8000/osc/server/start \
  -H "Content-Type: application/json" \
  -d '{"port": 9001}'

# Get recent messages
curl http://127.0.0.1:8000/osc/messages
```

## Updating

To update the Resonite MCP server:

```bash
cd resonite-mcp
git pull
pip install -e ".[dev]"
```

Restart Claude Desktop/Cursor IDE after updating.

## Uninstalling

### Remove from Claude Desktop

1. Edit `claude_desktop_config.json` and remove the "resonite" entry
2. Restart Claude Desktop

### Remove from Cursor IDE

1. Edit Cursor settings and remove the resonite MCP configuration
2. Restart Cursor IDE

### Remove Files

```bash
# Remove installation
pip uninstall resonite-mcp
rm -rf /path/to/resonite-mcp

# Remove DXT package
rm -rf /path/to/claude/extensions/resonite-mcp
```

## Support

If you encounter issues:

1. Check the [troubleshooting guide](TROUBLESHOOTING.md)
2. Review the [API documentation](API_REFERENCE.md)
3. Check Resonite's OSC settings
4. File an issue on GitHub

## Next Steps

After installation, you can:

1. **Explore the API**: Visit `http://127.0.0.1:8000/docs` for the HTTP API documentation
2. **Load plugins**: Use `plugin_discover()` and `plugin_load()` to extend functionality
3. **Create worlds**: Start building ProtoFlux scripts and custom worlds
4. **Join the community**: Connect with other Resonite MCP users

---

**Installation verified on**: Windows 10/11, macOS 12+, Ubuntu 20.04+
**Last updated**: December 22, 2025


