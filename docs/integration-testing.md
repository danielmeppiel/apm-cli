# Integration Testing

This document describes AWD's integration testing strategy to ensure runtime setup scripts work correctly and the golden scenario from the README functions as expected.

## Testing Strategy

AWD uses a tiered approach to integration testing:

### 1. **Smoke Tests** (Every CI run)
- **Location**: `tests/integration/test_runtime_smoke.py`
- **Purpose**: Fast verification that runtime setup scripts work
- **Scope**: 
  - Runtime installation (codex, llm)
  - Binary functionality (`--version`, `--help`)
  - AWD runtime detection
  - Workflow compilation without execution
- **Duration**: ~2-3 minutes per platform
- **Trigger**: Every push/PR

### 2. **End-to-End Golden Scenario Tests** (Releases only)
- **Location**: `tests/integration/test_golden_scenario_e2e.py`
- **Purpose**: Complete verification of the README golden scenario
- **Scope**:
  - Full runtime setup and configuration
  - Project initialization (`awd init`)
  - Dependency installation (`awd install`)
  - Real API calls to GitHub Models
  - Both Codex and LLM runtime execution
- **Duration**: ~10-15 minutes per platform  
- **Trigger**: Only on version tags (releases)

## Running Tests Locally

### Smoke Tests
```bash
# Run all smoke tests
pytest tests/integration/test_runtime_smoke.py -v

# Run specific test
pytest tests/integration/test_runtime_smoke.py::TestRuntimeSmoke::test_codex_runtime_setup -v
```

### E2E Tests

#### Option 1: Complete CI Process Simulation (Recommended)
```bash
# Set up environment
export GITHUB_TOKEN=your_github_token_here

# Run the complete CI/CD simulation script
./scripts/test-e2e-ci-local.sh
```

This script (`scripts/test-e2e-ci-local.sh`) mirrors the exact CI/CD process:
1. **Builds binary** with PyInstaller (like CI build job)
2. **Sets up symlink and PATH** (like CI artifacts download)
3. **Installs test dependencies** (like CI test setup)
4. **Runs E2E tests** with the built binary (like CI e2e-tests job)

#### Option 2: Direct pytest execution
```bash
# Set up environment
export AWD_E2E_TESTS=1
export GITHUB_TOKEN=your_github_token_here
export GITHUB_MODELS_KEY=your_github_token_here  # LLM runtime expects this specific env var

# Run E2E tests
pytest tests/integration/test_golden_scenario_e2e.py -v -s

# Run specific E2E test
pytest tests/integration/test_golden_scenario_e2e.py::TestGoldenScenarioE2E::test_complete_golden_scenario_codex -v -s
```

**Note**: Both `GITHUB_TOKEN` and `GITHUB_MODELS_KEY` should contain the same GitHub token value, but different runtimes expect different environment variable names.

## CI/CD Integration

### GitHub Actions Workflow

**On every push/PR:**
1. Unit tests
2. **Smoke tests** (runtime installation verification)

**On version tag releases:**
1. Unit tests  
2. Smoke tests
3. Build binaries
4. **E2E golden scenario tests** (using built binaries)
5. Publish to PyPI (only if E2E tests pass)

### GitHub Actions Authentication

E2E tests require proper GitHub Models API access:

**Required Permissions:**
- `contents: read` - for repository access
- `models: read` - **Required for GitHub Models API access**

**Environment Variables:**
- `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` - for Codex runtime
- `GITHUB_MODELS_KEY: ${{ secrets.GITHUB_TOKEN }}` - for LLM runtime (expects different env var name)

Both runtimes authenticate against GitHub Models but expect different environment variable names.

### Test Matrix

All integration tests run on:
- **Linux**: ubuntu-22.04 (x86_64)
- **macOS Intel**: macos-13 (x86_64) 
- **macOS Apple Silicon**: macos-14 (arm64)

## What the Tests Verify

### Smoke Tests Verify:
- ✅ Runtime setup scripts execute successfully
- ✅ Binaries are downloaded and installed correctly
- ✅ Binaries respond to basic commands
- ✅ AWD can detect installed runtimes
- ✅ Configuration files are created properly
- ✅ Workflow compilation works (without execution)

### E2E Tests Verify:
- ✅ Complete golden scenario from README works
- ✅ `awd runtime setup codex` installs and configures Codex
- ✅ `awd runtime setup llm` installs and configures LLM
- ✅ `awd init my-hello-world` creates project correctly
- ✅ `awd install` handles dependencies
- ✅ `awd run start --param name="Tester"` executes successfully
- ✅ Real API calls to GitHub Models work
- ✅ Parameter substitution works correctly
- ✅ MCP integration functions (GitHub tools)

## Benefits

### **Speed vs Confidence Balance**
- **Smoke tests**: Fast feedback (2-3 min) on every change
- **E2E tests**: High confidence (15 min) only when shipping

### **Cost Efficiency**
- Smoke tests use no API credits
- E2E tests only run on releases (minimizing API usage)

### **Platform Coverage**
- Tests run on all supported platforms
- Catches platform-specific runtime issues

### **Release Confidence**
- E2E tests must pass before PyPI publish
- Guarantees shipped releases work end-to-end
- Users can trust the README golden scenario

## Debugging Test Failures

### Smoke Test Failures
- Check runtime setup script output
- Verify platform compatibility
- Check network connectivity for downloads

### E2E Test Failures  
- **Use the CI simulation script first**: Run `./scripts/test-e2e-ci-local.sh` to reproduce the exact CI environment
- Verify `GITHUB_TOKEN` has required permissions (`models:read`)
- Ensure both `GITHUB_TOKEN` and `GITHUB_MODELS_KEY` environment variables are set
- Check GitHub Models API availability
- Review actual vs expected output
- Test locally with same environment
- For hanging issues: Check command transformation in script runner (codex expects prompt content, not file paths)

## Adding New Tests

### For New Runtime Support:
1. Add smoke test for runtime setup
2. Add E2E test for golden scenario with new runtime
3. Update CI matrix if new platform support

### For New Features:
1. Add smoke test for compilation/validation
2. Add E2E test if feature requires API calls
3. Keep tests focused and fast

---

This testing strategy ensures we ship with confidence while maintaining fast development cycles.
