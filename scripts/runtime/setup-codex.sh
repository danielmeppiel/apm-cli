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
    
    # Detect platform
    detect_platform
    
    # Ensure AWD runtime directory exists
    ensure_awd_runtime_dir
    
    # Set up paths
    local runtime_dir="$HOME/.awd/runtimes"
    local codex_binary="$runtime_dir/codex"
    local codex_config_dir="$HOME/.codex"
    local codex_config="$codex_config_dir/config.toml"
    
    # Determine download URL
    local download_url
    if [[ "$CODEX_VERSION" == "latest" ]]; then
        download_url="https://github.com/$CODEX_REPO/releases/latest/download/codex-$DETECTED_PLATFORM"
    else
        download_url="https://github.com/$CODEX_REPO/releases/download/$CODEX_VERSION/codex-$DETECTED_PLATFORM"
    fi
    
    # Download Codex binary
    log_info "Downloading Codex binary for $DETECTED_PLATFORM..."
    download_file "$download_url" "$codex_binary" "Codex binary"
    
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
model = "openai/gpt-4.1"

[model_providers.github-models]
name = "GitHub Models"
base_url = "https://models.github.ai/inference"
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
