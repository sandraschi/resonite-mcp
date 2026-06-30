# -*- mode: python ; coding: utf-8 -*-
# Tauri sidecar — HTTP backend on port 10979 (Agent Lab + presence gate).
from PyInstaller.utils.hooks import copy_metadata

datas = [("src/resonite_mcp", "resonite_mcp")]
for pkg in ("fastmcp", "fastapi", "uvicorn", "pydantic", "starlette", "httpx", "websockets"):
    datas += copy_metadata(pkg)

a = Analysis(
    ["run_server.py"],
    pathex=["src"],
    binaries=[],
    
    datas=datas,
    hiddenimports=[
        "charset_normalizer",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "resonite_mcp.http_server",
        "resonite_mcp.tools.fleet_tools",
        "resonite_mcp.tools.voice_tools",
        "resonite_mcp.utils.telemetry",
    "_strptime",
],
hookspath=[],
    
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "lancedb",
        "sentence_transformers",
        "torch",
        "transformers",
    ],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    
    name="resonite-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)








