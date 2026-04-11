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
        # Flet
        "flet",
        "flet.controls",
        "flet.controls.core",
        "flet.controls.material",
        "flet.controls.services",
        "flet.controls.services.clipboard",
        "flet.controls.services.url_launcher",
        # FastAPI / uvicorn
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "fastapi",
        "fastapi.middleware",
        "fastapi.middleware.cors",
        # Auth
        "jose",
        "jose.jwt",
        "passlib",
        "passlib.handlers",
        "passlib.handlers.bcrypt",
        # Other
        "qrcode",
        "qrcode.image.pil",
        "jinja2",
        "multipart",
        "python_multipart",
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
    upx=False,
    console=False,
    icon="assets/icon.icns",  # macOS — use assets/icon.ico for Windows
)

app = BUNDLE(
    exe,
    name="LanHopper.app",
    icon="assets/icon.icns",
    bundle_identifier="com.michinded.lanhopper",
    info_plist={
        "CFBundleName": "LanHopper",
        "CFBundleDisplayName": "LanHopper",
        "CFBundleVersion": "0.9.0",
        "CFBundleShortVersionString": "0.9.0",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
    },
)
