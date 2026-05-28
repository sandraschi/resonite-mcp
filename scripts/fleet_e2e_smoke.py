"""Fleet E2E smoke: inkscape UI -> resonite import (offline + live HTTP chain)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from resonite_mcp.utils.fleet_e2e_live import run_live_smoke
from resonite_mcp.utils.fleet_e2e_offline import run_offline_smoke
from resonite_mcp.utils.fleet_http import (
    DEFAULT_INKSCAPE_URL,
    DEFAULT_RESONITE_URL,
    call_http_tool,
    check_http_health,
)


async def _probe(name: str, url: str) -> dict[str, object]:
    ok = await check_http_health(url)
    return {"service": name, "url": url, "online": ok}


async def run_e2e_smoke(
    *,
    offline: bool = False,
    live: bool = False,
    offline_work_dir: Path | None = None,
    live_work_dir: Path | None = None,
) -> dict[str, object]:
    if offline:
        work = offline_work_dir or Path("D:/Temp/fleet_pipeline/resonite_e2e_offline")
        return await run_offline_smoke(work_dir=work)

    inkscape_online = await check_http_health(DEFAULT_INKSCAPE_URL)
    resonite_online = await check_http_health(DEFAULT_RESONITE_URL)

    if live or (inkscape_online and resonite_online):
        work = live_work_dir or Path("D:/Temp/fleet_pipeline/resonite_e2e_live")
        return await run_live_smoke(work_dir=work)

    steps: list[dict[str, object]] = []
    probes = await asyncio.gather(
        _probe("resonite-mcp", DEFAULT_RESONITE_URL),
        _probe("inkscape-mcp", DEFAULT_INKSCAPE_URL),
    )
    steps.append({"name": "fleet_probe", "success": True, "detail": probes})

    if resonite_online:
        mode = await call_http_tool(DEFAULT_RESONITE_URL, "resonite_fleet", {"operation": "execution_mode"})
        steps.append({"name": "resonite_execution_mode", "success": bool(mode.get("success")), "detail": mode})
        listing = await call_http_tool(DEFAULT_RESONITE_URL, "resonite_fleet", {"operation": "list_staging"})
        steps.append({"name": "resonite_list_staging", "success": bool(listing.get("success")), "detail": listing})
    else:
        steps.append({"name": "resonite_execution_mode", "success": False, "detail": {"skipped": "resonite offline"}})

    if inkscape_online:
        presets = await call_http_tool(
            DEFAULT_INKSCAPE_URL,
            "inkscape_sim_art",
            {"operation": "list_presets"},
        )
        steps.append({"name": "inkscape_sim_presets", "success": bool(presets.get("success")), "detail": presets})
    else:
        steps.append({"name": "inkscape_sim_presets", "success": False, "detail": {"skipped": "inkscape offline"}})

    success = all(bool(s.get("success")) for s in steps if s.get("name") != "fleet_probe")
    return {"success": success, "mode": "http", "steps": steps}


def main() -> None:
    parser = argparse.ArgumentParser(description="Resonite fleet E2E smoke")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--live", action="store_true", help="Force live inkscape->resonite HTTP chain")
    parser.add_argument("--offline-work-dir", default="")
    parser.add_argument("--live-work-dir", default="")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    offline_work = Path(args.offline_work_dir) if args.offline_work_dir else None
    live_work = Path(args.live_work_dir) if args.live_work_dir else None
    report = asyncio.run(
        run_e2e_smoke(
            offline=args.offline,
            live=args.live,
            offline_work_dir=offline_work,
            live_work_dir=live_work,
        ),
    )
    print(json.dumps(report, indent=2))
    if not args.json:
        mode = report.get("mode", "http")
        print(f"\nE2E smoke ({mode}) {'SUCCESS' if report['success'] else 'FAILED'}")
    if args.strict and not report.get("success"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
