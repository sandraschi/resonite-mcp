"""Copy canonical resonite_mcp package into mcp-server/src for MCPB layout."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _ignore(_path: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name == "__pycache__" or name.endswith(".egg-info"):
            ignored.add(name)
        elif name.endswith((".pyc", ".pyo")):
            ignored.add(name)
    return ignored


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    src_pkg = repo / "src" / "resonite_mcp"
    dst_root = repo / "mcp-server" / "src"
    dst_pkg = dst_root / "resonite_mcp"

    if not src_pkg.is_dir():
        print(f"Missing canonical package: {src_pkg}", file=sys.stderr)
        return 1

    if dst_root.exists():
        shutil.rmtree(dst_root)
    dst_root.mkdir(parents=True)
    shutil.copytree(src_pkg, dst_pkg, ignore=_ignore)
    print(f"Synced {src_pkg} -> {dst_pkg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
