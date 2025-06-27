#!/bin/bash
# Common utilities for runtime setup scripts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Platform detection matching build-release.yml
detect_platform() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    case "$os" in
        linux*)
            case "$arch" in
                x86_64|amd64)
                    DETECTED_PLATFORM="linux-x86_64"
                    ;;
                *)
                    log_error "Unsupported Linux architecture: $arch"
                    exit 1
                    ;;
            esac
            ;;
        darwin*)
            case "$arch" in
                x86_64)
                    DETECTED_PLATFORM="darwin-x86_64"
                    ;;
                arm64)
                    DETECTED_PLATFORM="darwin-arm64"
                    ;;
                *)
                    log_error "Unsupported macOS architecture: $arch"
                    exit 1
                    ;;
            esac
            ;;
        *)
            log_error "Unsupported operating system: $os"
            exit 1
            ;;
    esac
    
    log_info "Detected platform: $DETECTED_PLATFORM"
}

# Create AWD runtime directory
ensure_awd_runtime_dir() {
    local runtime_dir="$HOME/.awd/runtimes"
    if [[ ! -d "$runtime_dir" ]]; then
        log_info "Creating AWD runtime directory: $runtime_dir"
        mkdir -p "$runtime_dir"
    fi
}

# Add AWD runtimes to PATH if not already present
ensure_path_updated() {
    local runtime_dir="$HOME/.awd/runtimes"
    local shell_rc=""
    
    # Detect shell and appropriate RC file
    case "$SHELL" in
        */zsh)
            shell_rc="$HOME/.zshrc"
            ;;
        */bash)
            shell_rc="$HOME/.bashrc"
            if [[ ! -f "$shell_rc" && -f "$HOME/.bash_profile" ]]; then
                shell_rc="$HOME/.bash_profile"
            fi
            ;;
        *)
            log_warning "Unknown shell: $SHELL. You may need to manually add $runtime_dir to your PATH"
            return
            ;;
    esac
    
    # Check if PATH already contains the runtime directory
    if [[ ":$PATH:" != *":$runtime_dir:"* ]]; then
        log_info "Adding $runtime_dir to PATH in $shell_rc"
        echo "" >> "$shell_rc"
        echo "# Added by AWD runtime setup" >> "$shell_rc"
        echo "export PATH=\"\$HOME/.awd/runtimes:\$PATH\"" >> "$shell_rc"
        log_success "PATH updated. Please restart your shell or run: source $shell_rc"
    else
        log_info "PATH already contains AWD runtime directory"
    fi
}

# Download file with progress
download_file() {
    local url="$1"
    local output="$2"
    local description="${3:-file}"
    
    log_info "Downloading $description from $url"
    
    if command -v curl >/dev/null 2>&1; then
        curl -L --progress-bar "$url" -o "$output"
    elif command -v wget >/dev/null 2>&1; then
        wget --progress=bar "$url" -O "$output"
    else
        log_error "Neither curl nor wget is available. Please install one of them."
        exit 1
    fi
}

# Verify file was downloaded and is executable
verify_binary() {
    local binary_path="$1"
    local binary_name="$2"
    
    if [[ ! -f "$binary_path" ]]; then
        log_error "$binary_name binary not found at $binary_path"
        exit 1
    fi
    
    chmod +x "$binary_path"
    
    if [[ ! -x "$binary_path" ]]; then
        log_error "$binary_name binary is not executable"
        exit 1
    fi
    
    log_success "$binary_name binary installed and verified"
}
