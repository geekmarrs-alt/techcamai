# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for TECHCAMAI native Windows application.

Build with:
    pyinstaller techcamai.spec

Produces: dist/TECHCAMAI.exe (single file, no console window)
"""

a = Analysis(
    ["techcamai_app.py"],
    pathex=["api"],
    binaries=[],
    datas=[
        ("api/app/templates", "app/templates"),
        ("api/app/static", "app/static"),
    ],
    hiddenimports=[
        "app",
        "app.main",
        "app.discover",
        "app.shell",
        # FastAPI / Starlette internals that PyInstaller misses
        "fastapi",
        "starlette",
        "starlette.responses",
        "starlette.routing",
        "starlette.middleware",
        "starlette.middleware.cors",
        "starlette.staticfiles",
        "starlette.templating",
        # Uvicorn internals
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        # SQLModel / SQLAlchemy
        "sqlmodel",
        "sqlalchemy",
        "sqlalchemy.sql.default_comparator",
        "sqlalchemy.dialects.sqlite",
        # Pydantic
        "pydantic",
        "pydantic_settings",
        # Network
        "httpx",
        "psutil",
        # Jinja2
        "jinja2",
        "jinja2.ext",
        # Multipart form handling
        "multipart",
        "python_multipart",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TECHCAMAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="techcamai.ico",
)
