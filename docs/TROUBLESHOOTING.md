# Resonite MCP Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Resonite MCP server.

## Quick Diagnosis

### Check Server Status

```bash
# Test if the MCP server starts
python -m resonite_mcp --help

# Test HTTP API
resonite-mcp --host 127.0.0.1 --port 8000
# In another terminal:
curl http://127.0.0.1:8000/health
```

### Check Resonite Connection

```bash
# Test OSC connection to Resonite
curl -X POST http://127.0.0.1:8000/osc/send \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1", "port": 9000, "address": "/test", "values": ["ping"]}'
```

### Check Claude/Cursor Integration

Try these commands in Claude Desktop or Cursor:

- `@resonite What tools are available?`
- `@resonite Start a session`
- `@resonite Load avatar`

## Common Issues and Solutions

### ❌ "resonite_mcp module not found"

**Symptoms:**
- ImportError when running the server
- Tools not available in Claude/Cursor

**Solutions:**

1. **Check installation:**
   ```bash
   pip list | grep resonite
   # Should show: resonite-mcp 0.1.0
   ```

2. **Reinstall:**
   ```bash
   pip uninstall resonite-mcp
   pip install -e .
   ```

3. **Check Python path:**
   ```bash
   python -c "import sys; print('\\n'.join(sys.path))"
   # Should include the project directory
   ```

### ❌ "OSC connection failed"

**Symptoms:**
- Tools return "Failed to send OSC message"
- No response from Resonite commands

**Solutions:**

1. **Verify Resonite is running:**
   - Check Steam for Resonite process
   - Look for Resonite icon in system tray

2. **Check Resonite OSC settings:**
   - Open Resonite Settings (Menu → Settings)
   - Go to "Network" tab
   - Ensure "OSC" is enabled
   - Verify port is set to `9000`

3. **Test network connectivity:**
   ```bash
   # Check if port 9000 is open
   netstat -ano | findstr :9000

   # Test UDP connectivity
   nmap -sU -p 9000 127.0.0.1
   ```

4. **Firewall issues:**
   - Windows: Allow Python through Windows Firewall
   - Temporarily disable firewall for testing

### ❌ "Port already in use"

**Symptoms:**
- Server fails to start with "Address already in use"
- HTTP API returns connection refused

**Solutions:**

1. **Find conflicting process:**
   ```powershell
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

   # Linux/macOS
   lsof -i :8000
   kill -9 <PID>
   ```

2. **Change port:**
   ```bash
   # Use different port for HTTP API
   resonite-mcp --host 127.0.0.1 --port 8001
   ```

### ❌ "Permission denied" (Linux/macOS)

**Symptoms:**
- Server fails to start
- OSC communication fails

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la /path/to/resonite-mcp/
   chmod +x /path/to/resonite-mcp/
   ```

2. **OSC ports (< 1024 require root):**
   - Use ports 9000+ instead of 900
   - Don't run as root for security

### ❌ "Tools not appearing in Claude/Cursor"

**Symptoms:**
- Server starts but tools don't appear in IDE
- `@resonite` commands don't work

**Solutions:**

1. **Check configuration:**
   - Claude: Verify `claude_desktop_config.json`
   - Cursor: Check settings.json MCP section

2. **Restart IDE:**
   - Fully quit and restart Claude Desktop/Cursor
   - Wait 30 seconds after restart

3. **Check logs:**
   ```bash
   # Enable debug logging
   LOG_LEVEL=DEBUG resonite-mcp --stdio
   ```

4. **Validate JSON syntax:**
   ```bash
   python -c "import json; json.load(open('claude_desktop_config.json'))"
   ```

### ❌ "Plugin loading failed"

**Symptoms:**
- Server starts but plugins don't load
- `plugin_list()` returns empty

**Solutions:**

1. **Check plugin files:**
   ```bash
   ls -la src/resonite_mcp/plugins/
   ```

2. **Test plugin import:**
   ```python
   from resonite_mcp.plugins.osc_extensions import OSCExtensionsPlugin
   plugin = OSCExtensionsPlugin()
   print(plugin.name)
   ```

3. **Check plugin logs:**
   ```bash
   LOG_LEVEL=DEBUG resonite-mcp --stdio
   ```

## Advanced Diagnostics

### OSC Traffic Monitoring

```bash
# Start OSC monitor
curl -X POST http://127.0.0.1:8000/osc/server/start \
  -H "Content-Type: application/json" \
  -d '{"port": 9001}'

# Send test message
curl -X POST http://127.0.0.1:8000/osc/send \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1", "port": 9001, "address": "/test", "values": ["monitor"]}'
```

### Session Debugging

```bash
# Start debug session
curl -X POST http://127.0.0.1:8000/resonite/session/start \
  -H "Content-Type: application/json" \
  -d '{"session_name": "debug_session"}'

# Check session status
curl http://127.0.0.1:8000/resonite/session/status
```

### Performance Issues

**Symptoms:**
- Slow response times
- High CPU/memory usage

**Solutions:**

1. **Check system resources:**
   ```bash
   # Windows
   Get-Process python | Select-Object CPU, Memory

   # Linux
   ps aux | grep python
   ```

2. **Reduce logging:**
   ```bash
   LOG_LEVEL=WARNING resonite-mcp --stdio
   ```

3. **Profile performance:**
   ```python
   import cProfile
   cProfile.run('import resonite_mcp.server')
   ```

## Resonite-Specific Issues

### Avatar Loading Problems

```bash
# Test avatar loading
curl -X POST http://127.0.0.1:8000/resonite/avatar/load \
  -H "Content-Type: application/json" \
  -d '{"avatar_path": "resonite://DefaultAvatar", "slot": 0}'
```

**Common causes:**
- Invalid avatar path format
- Avatar not in inventory
- Slot already occupied

### ProtoFlux Execution Issues

```bash
# Test ProtoFlux execution
curl -X POST http://127.0.0.1:8000/resonite/protoflux/execute \
  -H "Content-Type: application/json" \
  -d '{"script_name": "TestScript"}'
```

**Common causes:**
- Script name doesn't exist
- Invalid script parameters
- ProtoFlux engine not ready

### World Loading Problems

```bash
# Test world loading
curl -X POST http://127.0.0.1:8000/resonite/world/load \
  -H "Content-Type: application/json" \
  -d '{"world_path": "resonite://TutorialWorld"}'
```

**Common causes:**
- Invalid world path
- World not accessible
- Network connectivity issues

## Log Analysis

### Enable Comprehensive Logging

```bash
# Set maximum verbosity
export LOG_LEVEL=DEBUG
export PYTHONUNBUFFERED=1

# Run with logging
resonite-mcp --stdio 2>&1 | tee resonite_mcp.log
```

### Common Log Patterns

**Successful operation:**
```
INFO - Sent OSC to 127.0.0.1:9000 - /avatar/load: ['resonite://DefaultAvatar', 0]
INFO - Avatar loaded: resonite://DefaultAvatar in slot 0
```

**Connection failure:**
```
ERROR - Failed to send OSC message: [Errno 111] Connection refused
ERROR - OSC connection failed - check Resonite OSC settings
```

**Plugin loading issues:**
```
WARNING - Plugin system not available
ERROR - Failed to load plugin osc_extensions: ImportError
```

## Getting Help

### Information to Include

When reporting issues, please include:

1. **System information:**
   ```bash
   python --version
   pip list | grep -E "(fastmcp|resonite|python-osc)"
   ```

2. **Configuration:**
   - Contents of `claude_desktop_config.json` or Cursor settings
   - Environment variables

3. **Logs:**
   ```bash
   # Capture logs during issue reproduction
   resonite-mcp --stdio 2>&1 | head -100
   ```

4. **Resonite status:**
   - Version number
   - OSC settings
   - Whether Resonite is running

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **Resonite Forums**: Discuss with other users
- **Discord**: Real-time community support

### Professional Support

For enterprise deployments or critical issues:

- Contact: sandra@example.com
- Priority response for commercial users
- On-site troubleshooting available

---

**Last updated**: December 22, 2025
**Tested on**: Windows 10/11, macOS 12+, Ubuntu 20.04+
