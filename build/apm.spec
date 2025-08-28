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

# Data files to include - recursively include all template files
datas = [
    (str(repo_root / 'scripts' / 'runtime'), 'scripts/runtime'),  # Bundle runtime setup scripts
    (str(repo_root / 'pyproject.toml'), '.'),  # Bundle pyproject.toml for version reading
]

# Recursively add all files from templates directory, including hidden directories
def collect_template_files(templates_root):
    """Recursively collect all template files, including those in hidden directories."""
    template_files = []
    
    for root, dirs, files in os.walk(templates_root):
        for file in files:
            source_path = os.path.join(root, file)
            # Calculate the relative path from the templates root
            rel_path = os.path.relpath(source_path, templates_root)
            # Destination should maintain the same structure under templates/
            dest_dir = os.path.dirname(f'templates/{rel_path}')
            if dest_dir == 'templates':
                dest_dir = 'templates'
            template_files.append((source_path, dest_dir))
    
    return template_files

# Add all template files to datas
template_files = collect_template_files(str(repo_root / 'templates'))
datas.extend(template_files)

# Hidden imports for APM modules that might not be auto-detected
hiddenimports = [
    'apm_cli',
    'apm_cli.cli',
    'apm_cli.config',
    'apm_cli.factory',
    'apm_cli.version',  # Add version module
    'apm_cli.adapters',
    'apm_cli.adapters.client',
    'apm_cli.adapters.client.base',
    'apm_cli.adapters.client.vscode',
    'apm_cli.adapters.package_manager',
    'apm_cli.compilation',  # Add compilation module
    'apm_cli.compilation.agents_compiler',
    'apm_cli.compilation.template_builder',
    'apm_cli.compilation.link_resolver',
    'apm_cli.primitives',  # Add primitives module
    'apm_cli.primitives.models',
    'apm_cli.primitives.discovery',
    'apm_cli.primitives.parser',
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
    # Rich modules (lazily imported, must be explicitly included)
    'rich',
    'rich.console',
    'rich.theme',
    'rich.panel',
    'rich.table',
    'rich.text',
    'rich.prompt',
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
