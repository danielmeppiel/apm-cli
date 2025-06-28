#!/bin/bash
# Setup script for Codex runtime
# Downloads Codex binary from GitHub releases and configures with GitHub Models

set -euo pipefail

# Get the directory of this script for sourcing common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup-common.sh"

# Configuration
CODEX_REPO="openai/codex"
CODEX_VERSION="${1:-latest}"  # Allow version override from command line

setup_codex() {
    log_info "Setting up Codex runtime..."
    
    # Detect platform using detect_platform from common utilities
    detect_platform
    
    # Map AWD platform format to Codex binary format
    local codex_platform
    case "$DETECTED_PLATFORM" in
        darwin-arm64)
            codex_platform="aarch64-apple-darwin"
            ;;
        darwin-x86_64)
            codex_platform="x86_64-apple-darwin"
            ;;
        linux-x86_64)
            codex_platform="x86_64-unknown-linux-gnu"
            ;;
        *)
            log_error "Unsupported platform: $DETECTED_PLATFORM"
            exit 1
            ;;
    esac
    
    # Ensure AWD runtime directory exists
    ensure_awd_runtime_dir
    
    # Set up paths
    local runtime_dir="$HOME/.awd/runtimes"
    local codex_binary="$runtime_dir/codex"
    local codex_config_dir="$HOME/.codex"
    local codex_config="$codex_config_dir/config.toml"
    local temp_dir="/tmp/awd-codex-install"
    
    # Create temp directory
    mkdir -p "$temp_dir"
    
    # Determine download URL for the tar.gz file
    local download_url
    if [[ "$CODEX_VERSION" == "latest" ]]; then
        # Use the specific release tag that contains the rust binaries
        download_url="https://github.com/$CODEX_REPO/releases/download/codex-rs-6a8a936f75ea44faf05ff4fab0c6a36fc970428d-1-rust-v0.0.2506261603/codex-$codex_platform.tar.gz"
    else
        download_url="https://github.com/$CODEX_REPO/releases/download/$CODEX_VERSION/codex-$codex_platform.tar.gz"
    fi
    
    # Download and extract Codex binary
    log_info "Downloading Codex binary for $codex_platform..."
    local tar_file="$temp_dir/codex-$codex_platform.tar.gz"
    download_file "$download_url" "$tar_file" "Codex binary archive"
    
    # Extract the binary
    log_info "Extracting Codex binary..."
    cd "$temp_dir"
    tar -xzf "$tar_file"
    
    # Find the extracted binary (should be named 'codex-{platform}' or just 'codex')
    local extracted_binary=""
    if [[ -f "$temp_dir/codex" ]]; then
        extracted_binary="$temp_dir/codex"
    elif [[ -f "$temp_dir/codex-$codex_platform" ]]; then
        extracted_binary="$temp_dir/codex-$codex_platform"
    else
        log_error "Codex binary not found in extracted archive. Contents:"
        ls -la "$temp_dir"
        exit 1
    fi
    
    # Move to final location
    mv "$extracted_binary" "$codex_binary"
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    # Verify binary
    verify_binary "$codex_binary" "Codex"
    
    # Create Codex config directory
    if [[ ! -d "$codex_config_dir" ]]; then
        log_info "Creating Codex config directory: $codex_config_dir"
        mkdir -p "$codex_config_dir"
    fi
    
    # Create Codex configuration for GitHub Models
    log_info "Creating Codex configuration for GitHub Models..."
    cat > "$codex_config" << 'EOF'
model_provider = "github-models"
model = "gpt-4o-mini"

[model_providers.github-models]
name = "GitHub Models"
base_url = "https://models.inference.ai.azure.com"
env_key = "GITHUB_TOKEN"
wire_api = "chat"
EOF
    
    log_success "Codex configuration created at $codex_config"
    
    # Update PATH
    ensure_path_updated
    
    # Test installation
    log_info "Testing Codex installation..."
    if "$codex_binary" --version >/dev/null 2>&1; then
        local version=$("$codex_binary" --version)
        log_success "Codex runtime installed successfully! Version: $version"
    else
        log_warning "Codex binary installed but version check failed. It may still work."
    fi
    
    # Show next steps
    echo ""
    log_info "Next steps:"
    echo "1. Set your GitHub token: export GITHUB_TOKEN=your_token_here"
    echo "2. Test with: codex --help"
    echo "3. Or use via AWD: awd run your-prompt"
}

# Run setup if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_codex "$@"
fi
