# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets", "assets"),
        ("app/web/templates", "app/web/templates"),
        ("app/web/static", "app/web/static"),
    ],
    hiddenimports=[
        "flet",
        "uvicorn",
        "fastapi",
        "jose",
        "passlib",
        "qrcode",
        "jinja2",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LanHopper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/icon.icns",  # macOS — use assets/icon.ico for Windows
)
