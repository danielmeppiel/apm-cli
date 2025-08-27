# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Changelog

## [0.1.6] - 2025-08-27

### Fixed
- **CRITICAL: Fixed missing Agent Primitives in CI-built binaries**
  - Added `include-hidden-files: true` to GitHub Actions upload-artifact@v4
  - GitHub Actions v4.4+ excludes hidden files by default, causing `.apm` directories to be lost
  - This was causing "Template file not found" errors in released binaries
  - Added verification steps to CI to catch similar issues in the future
- **Enhanced E2E tests to verify template bundling**
  - Added dedicated test for `apm init` command and `.apm` directory creation
  - E2E tests now catch template bundling failures during CI

### Technical Details
- Root cause: `upload-artifact@v4` behavior change excluding hidden files
- Impact: All released binaries from v0.1.0 to v0.1.5 missing Agent Primitives
- Solution: Explicit `include-hidden-files: true` configuration

## [0.1.5] - 2025-08-27

### Fixed
- **Critical CI/CD artifact merge issue** - Fixed GitHub Actions workflow where `merge-multiple: true` was causing artifact conflicts and dropping hidden `.apm` directories

## [0.1.4] - 2025-08-27

### Fixed
- **Critical PyInstaller template bundling fix** - Fixed PyInstaller spec file to properly bundle hidden `.apm` directories containing Agent Primitives (chatmodes, instructions, context, specs)

## [0.1.3] - 2025-08-27

### Fixed
- **Critical PyInstaller template bundling fix** - Fixed PyInstaller spec file to properly bundle hidden `.apm` directories containing Agent Primitives (chatmodes, instructions, context, specs)

## [0.1.2] - 2025-08-27

### Fixed
- **CI/CD Build Environment**: Standardized CI/CD build process to use uv like local development
  - Ensures consistent dependency resolution between local and CI builds
  - Activates virtual environment during binary build process
  - Fixes potential environment-related build discrepancies

### Technical Details
- Updated GitHub Actions workflow to use uv for dependency management in build job
- Added virtual environment activation step in CI/CD binary build process
- This ensures CI/CD builds match local development environment exactly

## [0.1.1] - 2025-08-27

### Fixed
- **Critical binary installation fix** - Fixed PyInstaller `--onedir` mode binary distribution where only the main executable was being installed, leaving behind the essential `_internal/` directory containing the Python runtime
- **Template bundling fix** - Fixed PyInstaller spec to properly bundle template files including hidden `.apm` directories that were being ignored during packaging
- **Compilation module fix** - Added missing `apm_cli.compilation` modules to PyInstaller's `hiddenimports` to resolve "attempted relative import with no known parent package" errors

### Improved
- **Enhanced install script** - Updated install script to properly handle PyInstaller `--onedir` mode by copying the entire bundle directory to `/usr/local/lib/apm/` and creating a symlink in `/usr/local/bin/apm`

## [0.1.0] - 2025-08-27

### Changed
- **Complete rebranding from AWD to APM** - Changed from "Agentic Workflow Definitions (AWD)" to "Agent Primitives Manager (APM)"
- **New positioning** - APM is now positioned as "the package manager for AI-Native Development"
- **Updated CLI commands** - All `awd` commands changed to `apm`
- **Configuration files** - `awd.yml` renamed to `apm.yml`, `.awd/` directory renamed to `.apm/`
- **Repository rename** - Repository changed from `awd-cli` to `apm-cli`
- **Package naming** - PyPI package changed from `awd-cli` to `apm-cli`

## [0.0.14] - 2025-01-19

### Changed
- **Python Version Standardization** - Standardized build environment to Python 3.12 for better Ubuntu 24.04 LTS compatibility
- **Build System Optimization** - Updated CI/CD pipeline to use Python 3.12 for binary builds, resolving shared library issues on Ubuntu systems

### Technical
- Updated GitHub Actions workflow to use Python 3.12 consistently
- Updated development tools (black, mypy) to target Python 3.12
- Improved binary compatibility with Ubuntu 24.04 LTS default Python version

## [0.0.13] - 2025-01-19

### Added
- **Automatic GitHub MCP Server Integration** - Codex runtime setup now automatically configures GitHub MCP Server when GITHUB_TOKEN and Docker are available

### Fixed
- **Manual Installation Documentation** - Fixed incorrect binary download URLs in README.md to use proper `.tar.gz` archives with extraction steps
- **Codex Debug Fix** - fixed the apm app template `debug` script to correctly setup Codex in debug mode

### Documentation
- **Enhanced Quick Start** - Updated README with clearer prerequisites and Docker requirement for full GitHub integration

## [0.0.12] - 2025-01-18

### Fixed
- **CI/CD Pipeline improvements** - Removed cumbersome test-installation job that was causing timing issues
- **Release process reliability** - Simplified release pipeline by removing installation testing dependency
- **GitHub API authentication** - Fixed Bearer token format for authenticated requests to prevent rate limiting

### Changed
- Streamlined CI/CD pipeline for faster and more reliable releases
- PyPI and Homebrew jobs now depend only on core build/test jobs instead of flaky installation tests
- Manual installation testing can still be performed when needed without blocking releases

## [0.0.11] - 2025-01-18

### Fixed
- **Critical installation script fix** - Fixed 404 error when installing from GitHub releases
- **Binary archive format** - Installation script now correctly downloads and extracts `.tar.gz` archives
- **Cross-platform installation** - Proper handling of directory structure in release archives for Linux and macOS

### Added
- **Installation validation in CI** - Added automated testing of installation script on all supported platforms
- **Release integrity checks** - CI now validates installation process before publishing to PyPI/Homebrew

### Changed
- Installation script now properly handles `.tar.gz` archives instead of raw binaries
- Enhanced CI pipeline to catch installation issues before release
- Improved error messages in installation script with better troubleshooting guidance

## [0.0.10] - 2025-06-30

### Fixed
- **Homebrew installation on macOS** - Fixed "bundle format is ambiguous" error by preserving PyInstaller signatures
- **macOS quarantine handling** - Remove quarantine attributes while maintaining existing code signatures  
- **Framework compatibility** - Avoid interfering with PyInstaller's embedded Python.framework structure

### Changed
- Enhanced Homebrew formula with minimal intervention approach that preserves security
- Updated formula template to maintain PyInstaller code signatures for future releases
- **Breaking**: All previous version tags (v0.0.1-v0.0.9) have been removed

## [0.0.9] - 2025-06-30

### Fixed
- **Critical homebrew installation fix** - Fixed missing executable permissions in homebrew binary packages
- **Enhanced workflow robustness** - Improved CI/CD pipeline to explicitly preserve executable permissions in tar.gz archives
- **Release process improvements** - Better SHA256 checksum handling from GitHub releases instead of build artifacts

### Changed
- Updated release workflow to prevent executable permission issues in future releases
- Improved binary packaging process for more reliable homebrew distributions

## [0.0.8] - 2025-06-30

### Performance
- **🚀 47x startup improvement** - Binary startup time improved from 4.0s to 0.086s through lazy imports optimization
- **Lazy imports implementation** - Rich and YAML libraries now load on-demand for massive performance boost
- **Binary optimization** - Enhanced PyInstaller configuration for better runtime performance

### Fixed
- **Runtime PATH updates** - Runtime binaries (like codex) now immediately available after setup without shell restart
- **Build system improvements** - Enhanced build scripts for directory-based deployment and proper checksum generation
- **Test robustness** - Fixed integration test directory handling and unit test stability (all 126 tests now pass consistently)

### Improved
- **UX messaging** - Clearer prompt compilation info panels with less intimidating messaging
- **Script execution** - Better error handling and compilation feedback in script runner
- **Developer experience** - No longer requires restarting shell after runtime setup

### Technical
- Enhanced PyInstaller spec configuration for onedir mode support
- Improved error handling order in script execution
- Better temp directory handling in tests

## [0.0.7] - 2025-06-29

### Added
- **Interactive project initialization** - Enhanced `apm init` with interactive mode and options for overwriting existing files
- **Rich library integration** - Improved CLI user experience with beautiful terminal output and formatting
- **Enhanced documentation** - Updated development documentation and integration testing details
- **Runtime support documentation** - Improved documentation reflecting changes in runtime support and prompt execution flow

### Improved
- CLI interface now provides richer visual feedback and better user experience
- Project initialization workflow with better error handling and user prompts
- Documentation clarity and accuracy across development guides

### Fixed
- E2E tests now use `--yes` flag to prevent EOF errors in non-interactive environments

## [0.0.6] - 2025-06-29

### Added
- **NPM-like script configuration** in `apm.yml` - Define custom execution commands for different runtimes
- **Runtime-agnostic script execution** - Configure scripts for Codex, LLM, or any runtime via `scripts:` section
- **Intelligent prompt compilation** - Automatic parameter substitution and runtime command transformation
- **Multi-runtime project support** - Single project can define scripts for different LLM backends

### Architecture
- **Separation of Concerns**: Runtime execution logic moved from CLI core to configurable scripts
- **ScriptRunner system**: Handles automatic `.prompt.md` compilation and runtime command transformation  
- **Flexible runtime targeting**: Projects define their own execution strategies via `apm.yml`

### Examples
```yaml
scripts:
  start: "codex --skip-git-repo-check hello-world.prompt.md"
  llm: "llm hello-world.prompt.md -m github/gpt-4o-mini" 
  debug: "DEBUG=true codex --skip-git-repo-check hello-world.prompt.md"
```

### Improved
- Command transformation handles environment variables, flags, and parameter positioning
- Enhanced Codex runtime setup and installation reliability
- Documentation clarity across CLI reference and prompts guide

### Fixed
- Runtime compatibility issues with flag positioning and environment variables
- Template execution in any directory with `--skip-git-repo-check` flag

## [0.0.5] - 2025-06-28

### Fixed
- PyInstaller binary build issues with relative imports
- Version reading in bundled binaries (now correctly shows version)
- Import errors that prevented binary execution

## [0.0.4] - 2025-06-28

### Added
- Runtime management system with `apm runtime` commands (setup, list, remove, status)
- Automated setup scripts for Codex and LLM runtimes with GitHub Models support
- Centralized version management reading from pyproject.toml
- Cross-platform runtime installation and configuration

### Changed
- Enhanced CLI with automatic runtime detection and preference ordering
- Updated documentation and build process for runtime bundling

### Fixed
- Runtime execution and distribution issues
- Version inconsistencies across codebase

## [0.0.3] - 2025-06-27

### Fixed
- Fixed binary release issues that prevented proper installation via install.sh script
- Resolved runtime execution problems in distributed binaries

## [0.0.2] - 2025-06-27

### Fixed
- Fixed binary release issues that prevented proper installation via install.sh script
- Resolved runtime execution problems in distributed binaries

## [0.0.1] - 2025-06-27

### Added
- Initial release of APM CLI - the package manager for AI-native development
- 6 core commands: `init`, `install`, `run`, `list`, `version`, `help`
- NPM-like developer workflow: Initialize → Install → Run
- Cross-platform binaries (no Python required)
- Multiple LLM runtime support: llm library, OpenAI Codex
- Hello world template with GitHub MCP integration
- Project-based configuration with apm.yml
- Automatic MCP dependency management
- Zero-dependency installation via curl script
- PyPI package distribution

### Installation
```bash
# Zero dependencies
curl -sSL https://raw.githubusercontent.com/danielmeppiel/apm-cli/main/install.sh | sh

# Or with pip
pip install apm-cli
```

### Quick Start
```bash
apm init my-project
cd my-project
apm install
apm run --param name="Developer"
```

[0.0.11]: https://github.com/danielmeppiel/apm-cli/releases/tag/v0.0.11
[0.0.10]: https://github.com/danielmeppiel/apm-cli/releases/tag/v0.0.10
