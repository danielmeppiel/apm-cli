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

# APM CLI entry point
entry_point = repo_root / 'src' / 'apm_cli' / 'cli.py'

# Data files to include
datas = [
    (str(repo_root / 'templates'), 'templates'),  # Bundle templates directory
    (str(repo_root / 'scripts' / 'runtime'), 'scripts/runtime'),  # Bundle runtime setup scripts
    (str(repo_root / 'pyproject.toml'), '.'),  # Bundle pyproject.toml for version reading
]

# Add all files from templates directory, including hidden .apm directories
import glob
template_files = []
for template_dir in (repo_root / 'templates').iterdir():
    if template_dir.is_dir():
        # Use glob to include all files, including those in hidden directories
        for file_pattern in ['**/*', '**/.*']:
            for file_path in template_dir.glob(file_pattern):
                if file_path.is_file():
                    # Create relative path from templates directory
                    rel_path = file_path.relative_to(repo_root / 'templates')
                    template_files.append((str(file_path), f'templates/{rel_path.parent}'))

# Add template files to datas
datas.extend(template_files)

# Hidden imports for APM modules that might not be auto-detected
hiddenimports = [
    'apm_cli',
    'apm_cli.cli',
    'apm_cli.config',
    'apm_cli.factory',
    'apm_cli.adapters',
    'apm_cli.adapters.client',
    'apm_cli.adapters.client.base',
    'apm_cli.adapters.client.vscode',
    'apm_cli.adapters.package_manager',
    'apm_cli.compilation',  # Add compilation module
    'apm_cli.compilation.agents_compiler',
    'apm_cli.compilation.template_builder',
    'apm_cli.compilation.link_resolver',
    'apm_cli.core',
    'apm_cli.core.operations',
    'apm_cli.deps',
    'apm_cli.deps.aggregator',
    'apm_cli.deps.verifier',
    'apm_cli.registry',
    'apm_cli.registry.client',
    'apm_cli.registry.integration',
    'apm_cli.runtime',
    'apm_cli.runtime.base',
    'apm_cli.runtime.codex_runtime',
    'apm_cli.runtime.factory',
    'apm_cli.runtime.llm_runtime',
    'apm_cli.runtime.manager',  # Add runtime manager
    'apm_cli.utils',
    'apm_cli.utils.helpers',
    'apm_cli.workflow',
    'apm_cli.workflow.runner',
    'apm_cli.workflow.parser', 
    'apm_cli.workflow.discovery',
    # Common dependencies
    'yaml',
    'click',
    'colorama',
    'pathlib',
    'frontmatter',
    'requests',
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
    # Additional exclusions for smaller binary
    'unittest',
    'doctest',
    'pdb',
    'bdb',
    'encodings.idna',
    'encodings.ascii',
    'encodings.latin_1',
    'test',
    'tests',
    'distutils',
    'lib2to3',
    'asyncio',
    'multiprocessing',
    'xml.etree',
    'xml.parsers',
    'html',
    'http.cookiejar',
    'http.cookies',
    'urllib.robotparser',
    'email',
    'calendar',
    'decimal',
    'fractions',
    'statistics',
    'wave',
    'audioop',
    'chunk',
    'colorsys',
    'imghdr',
    'sndhdr',
    'sunau',
    'tty',
    'pty',
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
    optimize=2,  # Python optimization level for smaller, faster binaries
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Switch to --onedir for directory-based deployment (faster startup with --onedir)
exe = EXE(
    pyz,
    a.scripts,
    [],            # Empty for --onedir mode
    exclude_binaries=True,  # Exclude binaries for --onedir mode
    name='apm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols for smaller size
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=is_upx_available(),
    upx_exclude=[],
    name='apm'
)
