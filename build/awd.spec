# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import subprocess
from pathlib import Path

# Check if UPX is available
def is_upx_available():
    try:
        subprocess.run(['upx', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Get the directory where this spec file is located
spec_dir = Path(SPECPATH)
repo_root = spec_dir.parent

# AWD CLI entry point
entry_point = repo_root / 'src' / 'awd_cli' / 'cli.py'

# Data files to include
datas = [
    (str(repo_root / 'templates'), 'templates'),  # Bundle templates directory
    (str(repo_root / 'scripts' / 'runtime'), 'scripts/runtime'),  # Bundle runtime setup scripts
]

# Hidden imports for AWD modules that might not be auto-detected
hiddenimports = [
    'awd_cli',
    'awd_cli.cli',
    'awd_cli.config',
    'awd_cli.factory',
    'awd_cli.adapters',
    'awd_cli.adapters.client',
    'awd_cli.adapters.client.base',
    'awd_cli.adapters.client.vscode',
    'awd_cli.adapters.package_manager',
    'awd_cli.core',
    'awd_cli.core.operations',
    'awd_cli.deps',
    'awd_cli.deps.aggregator',
    'awd_cli.deps.verifier',
    'awd_cli.registry',
    'awd_cli.registry.client',
    'awd_cli.registry.integration',
    'awd_cli.runtime',
    'awd_cli.runtime.base',
    'awd_cli.runtime.codex_runtime',
    'awd_cli.runtime.factory',
    'awd_cli.runtime.llm_runtime',
    'awd_cli.runtime.manager',  # Add runtime manager
    'awd_cli.utils',
    'awd_cli.utils.helpers',
    'awd_cli.workflow',
    'awd_cli.workflow.runner',
    'awd_cli.workflow.parser', 
    'awd_cli.workflow.discovery',
    # Common dependencies
    'yaml',
    'click',
    'colorama',
    'pathlib',
    'frontmatter',
    'requests',
    'pkg_resources',  # For accessing embedded scripts
]

# Modules to exclude to reduce binary size
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'numpy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',
    'PIL',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
]

a = Analysis(
    [str(entry_point)],
    pathex=[str(repo_root / 'src')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='awd',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=is_upx_available(),  # Enable UPX compression only if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
