#!/bin/bash
# Unified E2E testing script for both CI and local environments
# - CI mode: Uses pre-built artifacts from build job, sets up runtimes, runs E2E tests
# - Local mode: Builds binary, sets up runtimes, runs E2E tests
# This ensures consistent testing workflow between CI/CD and local development

set -euo pipefail

# Global variables
USE_EXISTING_BINARY=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites 
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        log_error "GITHUB_TOKEN environment variable is required"
        echo "Please set your GitHub token: export GITHUB_TOKEN=your_token_here"
        echo "Get a token at: https://github.com/settings/personal-access-tokens/new"
        exit 1
    fi
    
    log_success "GITHUB_TOKEN is set"
}

# Detect platform (like CI matrix does)
detect_platform() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    case "$os" in
        linux*)
            case "$arch" in
                x86_64|amd64)
                    BINARY_NAME="awd-linux-x86_64"
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
                    BINARY_NAME="awd-darwin-x86_64"
                    ;;
                arm64)
                    BINARY_NAME="awd-darwin-arm64"
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
    
    log_info "Detected platform: $BINARY_NAME"
}

# Detect environment and check if we should build or use existing binary
detect_environment() {
    log_info "Detecting environment..."
    
    # Check if we're in CI with pre-built artifacts (binary exists in ./dist/)
    # The binary is located at ./dist/$BINARY_NAME/awd (directory structure)
    if [[ -d "./dist/$BINARY_NAME" ]] && [[ -f "./dist/$BINARY_NAME/awd" ]]; then
        USE_EXISTING_BINARY=true
        log_info "Found existing binary: ./dist/$BINARY_NAME/awd (CI mode)"
    else
        USE_EXISTING_BINARY=false
        log_info "No existing binary found, will build locally"
    fi
}
# Build binary (like CI build job does) - only if needed
build_binary() {
    if [[ "$USE_EXISTING_BINARY" == "true" ]]; then
        log_info "=== Skipping binary build (using existing CI artifact) ==="
        return 0
    fi
    
    log_info "=== Building AWD binary (local mode) ==="
    
    # Install Python dependencies (like CI does)
    log_info "Installing Python dependencies..."
    python -m pip install --upgrade pip
    pip install -e .
    pip install pyinstaller
    
    # Build binary (like CI does)
    log_info "Building binary with build-binary.sh..."
    chmod +x scripts/build-binary.sh
    ./scripts/build-binary.sh
    
    # Verify binary was created
    # The build script creates ./dist/$BINARY_NAME/awd (directory structure)
    if [[ ! -f "./dist/$BINARY_NAME/awd" ]]; then
        log_error "Binary not found: ./dist/$BINARY_NAME/awd"
        exit 1
    fi
    
    log_success "Binary built: ./dist/$BINARY_NAME/awd"
}

# Set up binary for testing (exactly like CI does)
setup_binary_for_testing() {
    log_info "=== Setting up binary for testing (mirroring CI process) ==="
    
    # The binary is located at ./dist/$BINARY_NAME/awd (directory structure)
    BINARY_PATH="./dist/$BINARY_NAME/awd"
    
    # Make binary executable (like CI does)
    chmod +x "$BINARY_PATH"
    
    # Create AWD symlink for testing (exactly like CI does)
    ln -sf "$(pwd)/dist/$BINARY_NAME/awd" "$(pwd)/awd"
    
    # Add current directory to PATH (like CI does)
    export PATH="$(pwd):$PATH"
    
    # Verify setup
    if ! command -v awd >/dev/null 2>&1; then
        log_error "AWD not found in PATH after setup"
        exit 1
    fi
    
    local version=$(awd --version)
    log_success "AWD binary ready for testing: $version"
}

# Set up runtimes (codex/llm) - THE MISSING PIECE!
setup_runtimes() {
    log_info "=== Setting up runtimes for E2E tests ==="
    
    # Set up codex runtime
    log_info "Setting up Codex runtime..."
    if ! ./awd runtime setup codex; then
        log_error "Failed to set up Codex runtime"
        exit 1
    fi
    
    # Set up LLM runtime  
    log_info "Setting up LLM runtime..."
    if ! ./awd runtime setup llm; then
        log_error "Failed to set up LLM runtime"
        exit 1
    fi
    
    # Add runtime paths to current session PATH
    log_info "Adding runtime paths to current session..."
    RUNTIME_PATH="$HOME/.awd/runtimes"
    export PATH="$RUNTIME_PATH:$PATH"
    
    # Verify runtimes are available
    log_info "Verifying runtime installations..."
    
    # Check codex
    if command -v codex >/dev/null 2>&1; then
        local codex_version=$(codex --version 2>&1 || echo "unknown")
        log_success "Codex runtime ready: $codex_version"
    else
        log_error "Codex not found in PATH after setup"
        echo "PATH: $PATH"
        echo "Looking for codex in: $RUNTIME_PATH"
        ls -la "$RUNTIME_PATH" || echo "Runtime directory not found"
        exit 1
    fi
    
    # Check LLM wrapper
    local llm_path="$HOME/.awd/runtimes/llm"
    if [[ -x "$llm_path" ]]; then
        log_success "LLM runtime ready at: $llm_path"
    else
        log_error "LLM runtime not found at: $llm_path"
        exit 1
    fi
    
    log_success "All runtimes configured successfully"
}

# Install test dependencies (like CI does)
install_test_dependencies() {
    log_info "=== Installing test dependencies ==="
    
    # Check if uv is available, otherwise use pip
    if command -v uv >/dev/null 2>&1; then
        log_info "Using uv for dependency installation..."
        uv venv --python 3.13 || uv venv  # Try 3.13 first, fallback to default
        source .venv/bin/activate
        uv pip install -e ".[dev]"
    else
        log_info "Using pip for dependency installation..."
        pip install -e ".[dev]"
    fi
    
    log_success "Test dependencies installed"
}

# Run E2E tests (exactly like CI does)
run_e2e_tests() {
    log_info "=== Running E2E golden scenario tests (mirroring CI) ==="
    
    # Set environment variables (like CI does)
    export AWD_E2E_TESTS="1"
    export GITHUB_TOKEN="$GITHUB_TOKEN"
    
    log_info "Environment:"
    echo "  AWD_E2E_TESTS: $AWD_E2E_TESTS"
    echo "  GITHUB_TOKEN: ${GITHUB_TOKEN:0:10}..."
    echo "  PATH contains: $(dirname "$(which awd)")"
    echo "  AWD binary: $(which awd)"
    
    # Activate virtual environment if it exists
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    fi
    
    # Run the exact same pytest command as CI
    log_info "Running pytest command (same as CI)..."
    echo "Command: pytest tests/integration/test_golden_scenario_e2e.py -v -s --tb=short"
    
    if pytest tests/integration/test_golden_scenario_e2e.py -v -s --tb=short; then
        log_success "E2E tests passed!"
    else
        log_error "E2E tests failed!"
        exit 1
    fi
}

# Main execution
main() {
    echo "AWD CLI E2E Testing - Unified CI/Local Script"
    echo "============================================="
    echo ""
    echo "This script adapts to CI (using artifacts) or local (building) environments"
    echo ""
    
    check_prerequisites
    detect_platform
    detect_environment
    build_binary
    setup_binary_for_testing
    setup_runtimes  # THE MISSING PIECE!
    install_test_dependencies
    run_e2e_tests
    
    log_success "All E2E tests completed successfully!"
    echo ""
    if [[ "$USE_EXISTING_BINARY" == "true" ]]; then
        echo "✅ CI mode: Used pre-built artifacts and validated E2E workflow"
    else
        echo "✅ Local mode: Built binary and validated full CI/CD process"
    fi
    echo ""
    echo "E2E validation complete:"
    echo "  1. Binary setup ✅"
    echo "  2. Runtime installation (codex/llm) ✅"
    echo "  3. E2E tests with real API calls ✅"
    echo ""
    log_success "Ready for production deployment!"
}

# Cleanup on exit
cleanup() {
    if [[ -f "awd" ]]; then
        rm -f awd
    fi
}
trap cleanup EXIT

# Run main function
main "$@"
