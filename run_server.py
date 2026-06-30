"""Entry point for PyInstaller-bundled resonite-mcp HTTP backend."""

import _strptime  # noqa: F401
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "src")

from resonite_mcp.cli import main

if __name__ == "__main__":
    raise SystemExit(main() or 0)
