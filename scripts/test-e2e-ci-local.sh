#!/bin/bash
# Local simulation of CI/CD E2E testing process
# This mirrors the exact steps from build-release.yml e2e-tests job

set -euo pipefail

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

# Build binary (like CI build job does)
build_binary() {
    log_info "=== Building AWD binary (mirroring CI build process) ==="
    
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
    if [[ ! -f "./dist/$BINARY_NAME" ]]; then
        log_error "Binary not found: ./dist/$BINARY_NAME"
        exit 1
    fi
    
    log_success "Binary built: ./dist/$BINARY_NAME"
}

# Set up binary for testing (exactly like CI does)
setup_binary_for_testing() {
    log_info "=== Setting up binary for testing (mirroring CI process) ==="
    
    # Make binary executable (like CI does)
    chmod +x "./dist/$BINARY_NAME"
    
    # Create AWD symlink for testing (exactly like CI does)
    ln -sf "$(pwd)/dist/$BINARY_NAME" "$(pwd)/awd"
    
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
    echo "AWD CLI E2E Testing - CI Process Simulation"
    echo "==========================================="
    echo ""
    echo "This script mirrors the exact CI/CD process from build-release.yml"
    echo ""
    
    check_prerequisites
    detect_platform
    build_binary
    setup_binary_for_testing
    install_test_dependencies
    run_e2e_tests
    
    log_success "All E2E tests completed successfully!"
    echo ""
    echo "✅ This validates the same process that runs in CI/CD:"
    echo "  1. Build binary with PyInstaller"
    echo "  2. Set up symlink and PATH (like CI artifacts)"
    echo "  3. Install test dependencies"
    echo "  4. Run pytest E2E tests with real API calls"
    echo ""
    log_success "CI/CD E2E process validated locally!"
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
