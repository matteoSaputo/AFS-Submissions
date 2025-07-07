# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs

a = Analysis(
    ['src/main.py'],
    pathex=['.', 'src'],
    binaries=collect_dynamic_libs('numpy'),
    datas=[
        ('data/uploads/*', 'data/uploads'),
        ('data/fonts/*', 'data/fonts'),
        ('data/data/*', 'data/data'),
        ('assets/*', 'assets'),
        ('assets/cats/*', 'assets/cats'),
        ('info/*', 'info')
    ],    
    hiddenimports=collect_submodules('numpy'),
    hookspath=['venv/Lib/site-packages/pyinstaller_hooks_contrib/hooks'],
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
    name='AFS-Submissions-Tool',
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
)
