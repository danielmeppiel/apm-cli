# Binary Performance Optimization

**Status**: Work in Progress  
**Priority**: High  
**Target**: Reduce binary startup time from ~4s to ~1-1.5s (60-75% improvement)

## Executive Summary

APM-CLI binary startup is **23-30x slower** than Python source execution:
- **Binary startup**: 3.7-4.9 seconds
- **Python source**: 0.16 seconds  
- **Performance penalty**: Unacceptable user experience

This document provides a prioritized roadmap to achieve 60-75% startup performance improvement through targeted optimizations.

## Root Cause Analysis

### Performance Breakdown (Measured)

```
Total Binary Startup: ~4.0s
├── PyInstaller extraction: ~3.5s (87%)
├── Rich library loading: ~0.35s (9%)  
├── YAML parser: ~0.11s (3%)
├── Click framework: ~0.09s (2%)
└── Other (version, etc): ~0.06s (1%)
```

### Binary Metrics
- **Binary size**: 11MB compressed
- **Bundle contents**: 18MB uncompressed
- **Bundle extraction**: Occurs on every execution
- **Import overhead**: All dependencies loaded eagerly

## Optimization Roadmap

### Phase 1: Quick Wins (4-6 hours total, 50%+ improvement)

#### 1.1 Lazy Import Rich Components (1-2 hours) 🎯 HIGH IMPACT
**Impact**: -0.35s (9% improvement)  
**Effort**: Low  
**Risk**: Low

**Current Issue**:
```python
# cli.py - All imported at module level
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
```

**Solution**:
```python
def _rich_echo(message, style="info", symbol=None, fallback_color=INFO):
    """Print message with Rich styling, fallback to colorama."""
    try:
        from rich.console import Console  # Import only when needed
        if not hasattr(_rich_echo, '_console'):
            from rich.theme import Theme
            custom_theme = Theme({
                "info": "cyan", "warning": "yellow", "error": "bold red",
                "success": "bold green", "highlight": "bold magenta"
            })
            _rich_echo._console = Console(theme=custom_theme)
        
        if symbol:
            message = f"{STATUS_SYMBOLS.get(symbol, '')} {message}"
        _rich_echo._console.print(message, style=style)
    except ImportError:
        # Existing fallback logic
        if symbol:
            message = f"{STATUS_SYMBOLS.get(symbol, '')} {message}"
        click.echo(f"{fallback_color}{message}{RESET}")

def _rich_panel(content, title=None, style="cyan"):
    """Display content in a Rich panel with fallback."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        if not hasattr(_rich_panel, '_console'):
            _rich_panel._console = Console()
        _rich_panel._console.print(Panel(content, title=title, border_style=style))
    except ImportError:
        # Existing fallback
        if title:
            click.echo(f"\n{TITLE}{title}{RESET}")
        click.echo(content)
        click.echo()

def _create_files_table(files):
    """Create a table of created files with Rich styling."""
    try:
        from rich.table import Table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Icon", style="cyan")
        table.add_column("File", style="white")
        for file in files:
            table.add_row(STATUS_SYMBOLS["file"], file)
        return table
    except ImportError:
        return "\n".join([f"  - {file}" for file in files])
```

**Action Items**:
- [ ] Move all Rich imports inside helper functions
- [ ] Add caching for Console instances to avoid re-creation
- [ ] Test fallback paths work correctly
- [ ] Update existing helper functions to use lazy imports

#### 1.2 Lazy Import YAML (30 minutes) 🎯 MEDIUM IMPACT
**Impact**: -0.11s (3% improvement)  
**Effort**: Very Low  
**Risk**: Very Low

**Current Issue**:
```python
# cli.py line 5
import yaml
```

**Solution**:
```python
# Remove module-level import, add to functions that need it
@cli.command(help="📦 Install MCP dependencies from apm.yml")
def install(ctx):
    import yaml  # Import here instead
    # ... rest of function

def _load_apm_config():
    """Load configuration from apm.yml."""
    if Path('apm.yml').exists():
        import yaml
        with open('apm.yml', 'r') as f:
            return yaml.safe_load(f)
    return None
```

**Action Items**:
- [ ] Remove `import yaml` from module level
- [ ] Add `import yaml` to `install()`, `_load_apm_config()`, `run()`, `preview()`, `list()` functions
- [ ] Test all YAML-dependent commands work correctly

#### 1.3 Streamline Version Detection (30 minutes) 🎯 LOW IMPACT
**Impact**: -0.06s (1% improvement)  
**Effort**: Very Low  
**Risk**: Very Low

**Current Issue**:
```python
# version.py - Complex TOML parsing with multiple fallbacks
def get_version() -> str:
    try:
        # Multiple TOML library attempts + file system access
        if getattr(sys, 'frozen', False):
            pyproject_path = Path(sys._MEIPASS) / 'pyproject.toml'
        else:
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            data = _load_toml(pyproject_path)
            # ... complex parsing
```

**Solution Option A (Simple)**:
```python
# version.py - Build-time constant
__version__ = "0.0.7"  # Updated by CI/CD build process

def get_version() -> str:
    return __version__
```

**Solution Option B (Embedded)**:
```python
# Embed version in PyInstaller bundle as simple text file
def get_version() -> str:
    try:
        if getattr(sys, 'frozen', False):
            version_file = Path(sys._MEIPASS) / 'VERSION'
            if version_file.exists():
                return version_file.read_text().strip()
        return "0.0.7"  # Fallback
    except Exception:
        return "unknown"
```

**Action Items**:
- [ ] Choose approach (recommend Option A for simplicity)
- [ ] Update build process to inject version
- [ ] Remove TOML parsing dependencies
- [ ] Test version display works in both dev and binary

#### 1.4 PyInstaller Configuration Optimization (2 hours) 🎯 HIGHEST IMPACT
**Impact**: -1.5-2.0s (25-50% improvement)  
**Effort**: Medium  
**Risk**: Medium (requires thorough testing)

**Current Issues**:
- Using `--onefile` (slow extraction)
- No optimization flags
- Including unnecessary modules
- Suboptimal UPX compression

**Solution**:
```python
# build/apm.spec - Optimize configuration
exe = EXE(
    pyz,
    a.scripts,
    # Optimization flags
    exclude_binaries=True,  # Use --onedir for faster startup
    name='apm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols
    upx=True,  # Enable UPX compression
    upx_exclude=[],
    console=True,
    # Performance optimizations
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Additional excludes for smaller bundle
excludes = [
    'tkinter', 'matplotlib', 'scipy', 'numpy', 'pandas',
    'jupyter', 'IPython', 'notebook', 'PIL', 'PyQt5', 'PyQt6',
    'PySide2', 'PySide6', 'setuptools', 'pip', 'wheel',
    'distutils', 'email', 'urllib3', 'certifi', 'charset_normalizer',
    'unittest', 'pydoc', 'doctest', 'xml', 'xmlrpc',
]
```

**Build Script Optimization**:
```bash
# scripts/build-binary.sh
pyinstaller build/apm.spec \
    --clean \
    --noconfirm \
    --optimize=2 \
    --strip \
    --exclude-module tkinter \
    --exclude-module matplotlib
```

**Action Items**:
- [ ] Modify PyInstaller spec for `--onedir` mode
- [ ] Add comprehensive excludes list
- [ ] Test binary functionality across all commands
- [ ] Update CI/CD to handle directory distribution
- [ ] Measure startup improvement
- [ ] Consider bundling as compressed archive if needed

### Phase 2: Advanced Optimizations (6-10 hours, additional 10-20% improvement)

#### 2.1 Module Structure Optimization (4 hours)
**Impact**: -0.2s (5% improvement)  
**Effort**: High  
**Risk**: Medium

**Strategy**: Split CLI into command-specific modules with lazy loading
```python
# cli.py - Minimal core
@click.group()
def cli():
    pass

@cli.command()
def init(*args, **kwargs):
    from .commands.init import init_command
    return init_command(*args, **kwargs)

@cli.command()  
def install(*args, **kwargs):
    from .commands.install import install_command
    return install_command(*args, **kwargs)
```

#### 2.2 Alternative UI Framework (8 hours)
**Impact**: -0.3s (7% improvement)  
**Effort**: Very High  
**Risk**: High

**Strategy**: Create lightweight Rich alternative for simple operations
- Use Rich only for complex tables/panels
- Implement simple colorama-based theming for basic operations
- Maintain Rich as optional dependency

### Phase 3: Long-term Optimizations

#### 3.1 Binary Distribution Strategy
- Consider distributing as AppImage/DMG with pre-extracted runtime
- Implement smart caching of extracted bundles
- Explore alternative packaging (e.g., Rust-based launcher)

#### 3.2 Startup Cache
- Cache parsed configurations
- Pre-compile prompt templates
- Implement smart dependency detection

## Implementation Plan

### Week 1: Quick Wins Implementation
**Days 1-2**: Lazy import Rich and YAML (Items 1.1, 1.2)
**Days 3-4**: Streamline version detection (Item 1.3)  
**Days 4-5**: PyInstaller optimization (Item 1.4)

**Expected Result**: 50-60% startup improvement (4s → 1.6-2s)

### Week 2: Testing and Refinement
**Days 1-3**: Comprehensive testing across platforms
**Days 4-5**: Performance measurement and tuning

### Week 3: Advanced Optimizations (if needed)
**Implementation of Phase 2 items if additional performance needed**

## Success Metrics

### Primary Targets
- **Startup time**: < 1.5 seconds (from 4s)
- **Binary size**: < 8MB (from 11MB)
- **User experience**: Feels responsive

### Measurement Commands
```bash
# Startup time measurement
time ./dist/apm-darwin-arm64 --version

# Import time measurement  
python3 -c "
import time
start = time.time()
from apm_cli.cli import cli
print(f'CLI import: {time.time()-start:.3f}s')
"

# Binary size
ls -lh dist/apm-*
```

## Risk Mitigation

### Testing Strategy
1. **Functional testing**: All commands work correctly
2. **Fallback testing**: Rich/YAML import failures handled gracefully
3. **Platform testing**: macOS, Linux binaries perform similarly
4. **E2E testing**: Golden scenarios still pass

### Rollback Plan
- Keep current build configuration as backup
- Implement performance improvements incrementally
- Each change should be independently revertible

## Technical Notes

### Import Analysis Results
```python
# Measured import times (development environment)
Rich components: 0.347s (9% of total startup)
YAML parser: 0.114s (3% of total startup)  
Click framework: 0.091s (2% of total startup)
Version detection: 0.063s (1% of total startup)
Full CLI import: 0.069s (source execution)
```

### PyInstaller Bundle Analysis
- **Bundle size**: 18MB uncompressed, 11MB compressed
- **Extraction time**: ~3.5s (87% of startup time)
- **Key insight**: Bundle extraction dominates performance

### Dependencies for Optimization
- PyInstaller 6.0+ for latest optimizations
- UPX for compression (already available)
- Rich library fallback compatibility
- YAML parser import error handling

## Questions for Engineering Team

1. **Distribution preference**: `--onedir` vs `--onefile` for user experience?
2. **Rich dependency**: Keep as hard dependency or make optional?
3. **Version strategy**: Build-time injection vs runtime parsing?
4. **Testing scope**: Which platforms need performance validation?

## Related Documentation

- [CLI Reference](../cli-reference.md) - Command documentation
- [Development Status](../development-status.md) - Current feature status
- [Build Release Workflow](../../.github/workflows/build-release.yml) - CI/CD pipeline

---

**Next Action**: Engineering team to review and assign Phase 1 items for immediate implementation.
