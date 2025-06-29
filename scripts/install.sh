#!/bin/bash
set -e

echo "Installing AWD-CLI..."

# Detect package managers
has_brew=$(command -v brew >/dev/null 2>&1 && echo "yes" || echo "no")
has_uv=$(command -v uv >/dev/null 2>&1 && echo "yes" || echo "no")
has_pip=$(command -v pip >/dev/null 2>&1 && echo "yes" || echo "no")

# Try to install with the best available package manager
if [ "$has_brew" = "yes" ]; then
    echo "Installing with Homebrew..."
    brew tap danielmeppiel/awd-cli
    brew install awd-cli
elif [ "$has_uv" = "yes" ]; then
    echo "Installing with uv..."
    uv pip install awd-cli
elif [ "$has_pip" = "yes" ]; then
    echo "Installing with pip..."
    pip install awd-cli
else
    echo "Error: No supported package manager found (brew, uv, or pip)."
    echo "Please install one of the following and try again:"
    echo "  - Homebrew: https://brew.sh"
    echo "  - Python with pip: https://python.org"
    echo "  - uv: https://docs.astral.sh/uv/"
    exit 1
fi

echo "AWD-CLI installed successfully!"
