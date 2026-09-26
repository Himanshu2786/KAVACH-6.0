# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

project_root = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = [
    (os.path.join(project_root, 'frontend', 'dist'), os.path.join('frontend', 'dist')),
    (os.path.join(project_root, 'demo', 'training_samples'), os.path.join('demo', 'training_samples')),
    (os.path.join(project_root, 'INFO'), 'INFO'),
]

if os.path.exists(os.path.join(project_root, 'kavach.db')):
    datas.append((os.path.join(project_root, 'kavach.db'), '.'))

hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespans',
    'uvicorn.lifespans.on',
    'fastapi',
    'fastapi.staticfiles',
    'pydantic',
    'pydantic_settings',
    'sqlalchemy',
    'sqlalchemy.sql.default_comparator',
    'psutil',
    'winreg',
    'backend.app.main',
    'backend.app.api.api',
    'backend.app.scanners',
    'backend.app.scanners.permissions_manager',
    'backend.app.scanners.file_scanner',
    'backend.app.scanners.process_scanner',
    'backend.app.scanners.software_scanner',
    'backend.app.scanners.startup_scanner',
    'backend.app.scanners.network_scanner',
    'backend.app.scanners.system_security_scanner',
]

a = Analysis(
    [os.path.join(project_root, 'portable', 'kavach_portable.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KAVACH',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
