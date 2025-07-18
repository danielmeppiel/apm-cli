#!/bin/bash
# Setup script for Codex runtime
# Downloads Codex binary from GitHub releases and configures with GitHub Models
# Automatically sets up GitHub MCP Server integration when GITHUB_TOKEN is available

set -euo pipefail

# Get the directory of this script for sourcing common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup-common.sh"

# Check if Docker is available for MCP server integration
check_docker_available() {
    if command -v docker >/dev/null 2>&1; then
        if docker info >/dev/null 2>&1; then
            return 0
        else
            log_warning "Docker is installed but not running"
            return 1
        fi
    else
        log_warning "Docker is not installed"
        return 1
    fi
}

# Configuration
CODEX_REPO="openai/codex"
CODEX_VERSION="latest"  # Default version
VANILLA_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --vanilla)
            VANILLA_MODE=true
            shift
            ;;
        *)
            # If it's not --vanilla and not empty, treat it as version
            if [[ -n "$1" && "$1" != "--vanilla" ]]; then
                CODEX_VERSION="$1"
            fi
            shift
            ;;
    esac
done

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
        # Fetch the latest release tag from GitHub API
        log_info "Fetching latest Codex release information..."
        local latest_release_url="https://api.github.com/repos/$CODEX_REPO/releases/latest"
        local latest_tag
        
        # Try to get the latest release tag using curl
        if command -v curl >/dev/null 2>&1; then
            # Use authenticated request if GITHUB_TOKEN is available
            if [[ -n "${GITHUB_TOKEN:-}" ]]; then
                log_info "Using authenticated GitHub API request"
                local auth_header="Authorization: Bearer ${GITHUB_TOKEN}"
                latest_tag=$(curl -s -H "$auth_header" "$latest_release_url" | grep '"tag_name":' | sed -E 's/.*"tag_name":[[:space:]]*"([^"]+)".*/\1/')
            else
                log_info "Using unauthenticated GitHub API request (60 requests/hour limit)"
                latest_tag=$(curl -s "$latest_release_url" | grep '"tag_name":' | sed -E 's/.*"tag_name":[[:space:]]*"([^"]+)".*/\1/')
            fi
        else
            log_error "curl is required to fetch latest release information"
            exit 1
        fi
        
        # Verify we got a valid tag
        if [[ -z "$latest_tag" || "$latest_tag" == "null" ]]; then
            log_error "Failed to fetch latest release tag from GitHub API"
            log_error "No fallback available. Please check your internet connection or specify a specific version."
            exit 1
        fi
        
        log_info "Using Codex release: $latest_tag"
        download_url="https://github.com/$CODEX_REPO/releases/download/$latest_tag/codex-$codex_platform.tar.gz"
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
    
    # Create configuration if not in vanilla mode
    if [[ "$VANILLA_MODE" == "false" ]]; then
        # Create Codex config directory
        if [[ ! -d "$codex_config_dir" ]]; then
            log_info "Creating Codex config directory: $codex_config_dir"
            mkdir -p "$codex_config_dir"
        fi
        
        # Create Codex configuration for GitHub Models with MCP integration
        log_info "Creating Codex configuration for GitHub Models with MCP (AWD default)..."
        
        # Check if GitHub token is available for MCP server setup
        if [[ -n "${GITHUB_TOKEN:-}" ]]; then
            log_info "GITHUB_TOKEN found - checking Docker availability for MCP integration..."
            
            if check_docker_available; then
                log_info "Docker is available - configuring GitHub MCP server integration..."
                cat > "$codex_config" << EOF
model_provider = "github-models"
model = "gpt-4o-mini"

[model_providers.github-models]
name = "GitHub Models"
base_url = "https://models.inference.ai.azure.com"
env_key = "GITHUB_TOKEN"
wire_api = "chat"

# MCP Server Configuration
[mcp_servers.github]
command = "docker"
args = [
  "run",
  "-i", 
  "--rm",
  "-e",
  "GITHUB_PERSONAL_ACCESS_TOKEN",
  "-e",
  "GITHUB_TOOLSETS=context",
  "ghcr.io/github/github-mcp-server"
]
env = { "GITHUB_PERSONAL_ACCESS_TOKEN" = "${GITHUB_TOKEN}" }
EOF
            else
                log_warning "Docker not available - creating basic configuration without MCP integration"
                cat > "$codex_config" << 'EOF'
model_provider = "github-models"
model = "gpt-4o-mini"

[model_providers.github-models]
name = "GitHub Models"
base_url = "https://models.inference.ai.azure.com"
env_key = "GITHUB_TOKEN"
wire_api = "chat"
EOF
            fi
        else
            log_warning "GITHUB_TOKEN not found - creating basic configuration without MCP integration"
            cat > "$codex_config" << 'EOF'
model_provider = "github-models"
model = "gpt-4o-mini"

[model_providers.github-models]
name = "GitHub Models"
base_url = "https://models.inference.ai.azure.com"
env_key = "GITHUB_TOKEN"
wire_api = "chat"
EOF
        fi
        
        log_success "Codex configuration created at $codex_config"
        log_info "AWD configured Codex with GitHub Models as default provider"
    else
        log_info "Vanilla mode: Skipping AWD configuration - Codex will use its native defaults"
    fi
    
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
    if [[ "$VANILLA_MODE" == "false" ]]; then
        # Show MCP integration status and appropriate next steps
        local docker_available=false
        if check_docker_available; then
            docker_available=true
        fi
        
        if [[ -n "${GITHUB_TOKEN:-}" ]] && [[ "$docker_available" == "true" ]]; then
            echo "🚀 Ready to use AWD with GitHub integration!"
            echo "   - Run: awd run start --param name=YourName"
            echo ""
            log_success "✨ GitHub MCP Server integration configured!"
            echo "   - Your AWD scripts can now use GitHub tools like 'get_me', 'list_repos', etc."
            echo "   - Docker is available and MCP server will work automatically"
            echo "   - GitHub Models provides free access to OpenAI models with your GitHub token"
        elif [[ -n "${GITHUB_TOKEN:-}" ]] && ! check_docker_available; then
            echo "1. Install and start Docker to enable GitHub tools in AWD scripts"
            echo "2. Re-run this script to enable MCP integration"
            echo "3. Then run: awd run start --param name=YourName"
            echo ""
            log_warning "⚠️  GitHub MCP Server integration requires Docker"
            echo "   - GITHUB_TOKEN is configured but Docker is not available"
            echo "   - GitHub Models provides free access to OpenAI models with your GitHub token"
        else
            echo "1. Set your GitHub token: export GITHUB_TOKEN=your_token_here"
            echo "2. Re-run this script to enable GitHub MCP integration"
            echo "3. Then run: awd run start --param name=YourName"
            echo ""
            log_warning "⚠️  GitHub MCP Server integration not configured"
            echo "   - Set GITHUB_TOKEN environment variable and ensure Docker is running"
            echo "   - GitHub Models provides free access to OpenAI models with your GitHub token"
        fi
    else
        echo "1. Configure Codex with your preferred provider (see: codex --help)"
        echo "2. Then run with AWD: awd run start"
    fi
}

# Run setup if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_codex "$@"
fi
