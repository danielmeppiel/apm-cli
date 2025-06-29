#!/bin/bash
# Setup script for LLM runtime
# Installs Simon Willison's llm library via pip in a managed environment

set -euo pipefail

# Get the directory of this script for sourcing common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup-common.sh"

# Configuration
VANILLA_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --vanilla)
            VANILLA_MODE=true
            shift
            ;;
        *)
            # For LLM, we don't currently support version selection
            shift
            ;;
    esac
done

setup_llm() {
    log_info "Setting up LLM runtime..."
    
    # Ensure AWD runtime directory exists
    ensure_awd_runtime_dir
    
    local runtime_dir="$HOME/.awd/runtimes"
    local llm_venv="$runtime_dir/llm-venv"
    local llm_wrapper="$runtime_dir/llm"
    
    # Check if Python is available
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3 is required but not found. Please install Python 3."
        exit 1
    fi
    
    # Create virtual environment for LLM
    log_info "Creating Python virtual environment for LLM..."
    python3 -m venv "$llm_venv"
    
    # Install LLM in virtual environment
    log_info "Installing LLM library..."
    "$llm_venv/bin/pip" install --upgrade pip
    "$llm_venv/bin/pip" install llm
    
    # Install GitHub Models plugin in non-vanilla mode
    if [[ "$VANILLA_MODE" == "false" ]]; then
        log_info "Installing GitHub Models plugin for AWD defaults..."
        "$llm_venv/bin/pip" install llm-github-models
        log_success "GitHub Models plugin installed"
    else
        log_info "Vanilla mode: Skipping GitHub Models plugin installation"
    fi
    
    # Create wrapper script
    log_info "Creating LLM wrapper script..."
    cat > "$llm_wrapper" << EOF
#!/bin/bash
# LLM wrapper script created by AWD
exec "$llm_venv/bin/llm" "\$@"
EOF
    
    chmod +x "$llm_wrapper"
    
    # Verify installation
    verify_binary "$llm_wrapper" "LLM"
    
    # Update PATH
    ensure_path_updated
    
    # Test installation
    log_info "Testing LLM installation..."
    if "$llm_wrapper" --version >/dev/null 2>&1; then
        local version=$("$llm_wrapper" --version)
        log_success "LLM runtime installed successfully! Version: $version"
    else
        log_warning "LLM installed but version check failed. It may still work."
    fi
    
    # Show next steps
    echo ""
    log_info "Next steps:"
    if [[ "$VANILLA_MODE" == "false" ]]; then
        echo "1. Set your GitHub token: export GITHUB_TOKEN=your_token_here"
        echo "2. Then run with AWD: awd run start --runtime=llm"
        echo ""
        log_info "GitHub Models provides free access to OpenAI models with your GitHub token"
    else
        echo "1. Configure LLM providers: llm keys set <provider>"
        echo "2. For OpenAI: llm keys set openai"
        echo "3. For Anthropic: llm keys set anthropic"
        echo "4. Then run with AWD: awd run start --runtime=llm"
    fi
}

# Run setup if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_llm "$@"
fi
