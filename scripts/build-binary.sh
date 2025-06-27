#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Platform detection
OS=$(uname -s)
ARCH=$(uname -m)

# Normalize architecture names
case $ARCH in
    x86_64)
        ARCH="x86_64"
        ;;
    arm64|aarch64)
        ARCH="arm64"
        ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

# Normalize OS names and set binary name
case $OS in
    Darwin)
        PLATFORM="darwin"
        BINARY_NAME="awd-darwin-$ARCH"
        ;;
    Linux)
        PLATFORM="linux"
        BINARY_NAME="awd-linux-$ARCH"
        ;;
    *)
        echo -e "${RED}Unsupported operating system: $OS${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}Building AWD binary for $PLATFORM-$ARCH${NC}"
echo -e "${BLUE}Output binary: $BINARY_NAME${NC}"

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build/build/ dist/

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}PyInstaller not found. Installing...${NC}"
    pip install pyinstaller
fi

# Check if UPX is available (optional, for compression)
if command -v upx &> /dev/null; then
    echo -e "${GREEN}UPX found - binary will be compressed${NC}"
else
    echo -e "${YELLOW}UPX not found - binary will not be compressed (install with: brew install upx)${NC}"
fi

# Build binary
echo -e "${YELLOW}Building binary with PyInstaller...${NC}"
pyinstaller build/awd.spec

# Check if build was successful
if [ ! -f "dist/awd" ]; then
    echo -e "${RED}Build failed - binary not found${NC}"
    exit 1
fi

# Rename binary to platform-specific name
mv dist/awd "dist/$BINARY_NAME"

# Make binary executable
chmod +x "dist/$BINARY_NAME"

# Test the binary
echo -e "${YELLOW}Testing binary...${NC}"
if "./dist/$BINARY_NAME" --version; then
    echo -e "${GREEN}✓ Binary test successful${NC}"
else
    echo -e "${RED}✗ Binary test failed${NC}"
    exit 1
fi

# Show binary info
echo -e "${GREEN}✓ Build complete!${NC}"
echo -e "${BLUE}Binary: ./dist/$BINARY_NAME${NC}"
echo -e "${BLUE}Size: $(du -h "dist/$BINARY_NAME" | cut -f1)${NC}"

# Optional: Create checksum
if command -v sha256sum &> /dev/null; then
    sha256sum "dist/$BINARY_NAME" > "dist/$BINARY_NAME.sha256"
    echo -e "${BLUE}Checksum: ./dist/$BINARY_NAME.sha256${NC}"
elif command -v shasum &> /dev/null; then
    shasum -a 256 "dist/$BINARY_NAME" > "dist/$BINARY_NAME.sha256"
    echo -e "${BLUE}Checksum: ./dist/$BINARY_NAME.sha256${NC}"
fi

echo -e "${GREEN}Ready for release!${NC}"
