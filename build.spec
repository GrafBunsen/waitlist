# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-Spec-Datei für die Wartelisten-Kontaktverwaltung.

Build-Befehl:
    pyinstaller build.spec

Erzeugt eine einzelne .exe-Datei (Windows) ohne Konsolenfenster.
Der Python-Code ist plattformunabhängig – für macOS/Linux kann
das Build-Ziel später angepasst werden.
"""

import os
import sys

block_cipher = None

# Projektverzeichnis – SPECPATH zeigt auf das Verzeichnis der .spec-Datei
PROJECT_DIR = os.path.abspath(SPECPATH if os.path.isdir(SPECPATH) else os.path.dirname(SPECPATH))

a = Analysis(
    [os.path.join(PROJECT_DIR, 'main.py')],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_DIR, 'templates'), 'templates'),
        (os.path.join(PROJECT_DIR, 'static'), 'static'),
        (os.path.join(PROJECT_DIR, 'icon.ico'), '.'),
        (os.path.join(PROJECT_DIR, 'src'), 'src'),
    ],
    hiddenimports=['src.app', 'src.db', 'src.tray', 'src.validators'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Warteliste',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_DIR, 'icon.ico'),
)
