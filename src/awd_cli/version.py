"""Version management for AWD CLI."""

import sys
from pathlib import Path
import re

# Try different TOML libraries based on availability
try:
    import tomllib  # Python 3.11+
    def _load_toml(path):
        with open(path, 'rb') as f:
            return tomllib.load(f)
except ImportError:
    try:
        import tomli
        def _load_toml(path):
            with open(path, 'rb') as f:
                return tomli.load(f)
    except ImportError:
        try:
            import toml
            def _load_toml(path):
                with open(path, 'r') as f:
                    return toml.load(f)
        except ImportError:
            def _load_toml(path):
                raise ImportError("No TOML library available")


def get_version() -> str:
    """
    Get the current version from pyproject.toml.
    
    Returns:
        str: Version string
    """
    try:
        # Handle PyInstaller bundle vs development
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            pyproject_path = Path(sys._MEIPASS) / 'pyproject.toml'
        else:
            # Running in development
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            
        if pyproject_path.exists():
            data = _load_toml(pyproject_path)
            version = data.get('project', {}).get('version', 'unknown')
            # Validate version format (basic semver)
            if re.match(r'^\d+\.\d+\.\d+(-.*)?$', version):
                return version
    except Exception:
        pass
    
    return "unknown"


# For backward compatibility
__version__ = get_version()
