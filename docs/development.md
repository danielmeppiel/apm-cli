# Development Guide

## Setup

```bash
# Clone repository
git clone https://github.com/danielmeppiel/awd-cli.git
cd awd-cli

# Install with development dependencies
pip install -e ".[dev,build]"
```

## Development Workflow

```bash
# Run tests
pytest

# Code formatting and linting
black src/ tests/
isort src/ tests/
mypy src/

# Test CLI locally
awd --version
awd init test-project
```

## Building Binaries

```bash
# Build binary for current platform
./scripts/build-binary.sh

# Test binary
./dist/awd-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m) --version
```

## Release Process

See [Binary Release Guide](binary-release.md) for complete release process.

## Stack

- **Python 3.11+** - Runtime (3.11 for binary compatibility)
- **Click** - CLI framework
- **PyYAML** - Configuration parsing
- **Colorama** - Terminal colors
- **PyInstaller** - Binary packaging
- **pytest** - Testing
- **GitHub Actions** - CI/CD and binary builds
