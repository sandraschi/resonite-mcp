# resonite-mcp — Troubleshooting

Moved out of README.md 2026-07-18. (Supersedes the typo-named
`TROUBLESHOUTING.md` if both exist — merge candidate.)

## ResoniteLink connection fails
- Are you the **session host**? Only the host can enable ResoniteLink.
- Don't trust the dashboard port readout — run `resonite_link_discover()`
  (UDP 12512). Live testing showed the displayed port can be wrong.
- Discovery finds nothing: check the session is actually running, and that
  UDP 12512 isn't firewalled; re-toggle "Enable ResoniteLink".
- Protocol errors after a Resonite update: upstream Link is beta; compare the
  client's pinned protocol version (0.13.1) against the release notes and
  re-run `tests/unit/test_resonite_link_protocol.py`.

## Server won't start
- Python 3.12+ (`just bootstrap` sets up the venv)
- Dependencies: `pip install -e ".[dev]"` or `just bootstrap`

## OSC connection fails
- Resonite Settings → Network → OSC enabled (port 9000)
- Firewall allows UDP; Resonite host-access consent granted

## Tools not available in Claude
- Restart Claude Desktop after config changes
- Validate `claude_desktop_config.json` syntax and the server path

## HTTP API not responding
- `curl http://127.0.0.1:8000/health`
- Port collision? CORS if calling from a browser

## Debug mode
```bash
resonite-mcp --log-level DEBUG --stdio
# or LOG_LEVEL=DEBUG
```
