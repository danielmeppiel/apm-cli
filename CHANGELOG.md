# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- **Interactive project initialization** - Enhanced `awd init` with interactive mode and options for overwriting existing files
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
- **NPM-like script configuration** in `awd.yml` - Define custom execution commands for different runtimes
- **Runtime-agnostic script execution** - Configure scripts for Codex, LLM, or any runtime via `scripts:` section
- **Intelligent prompt compilation** - Automatic parameter substitution and runtime command transformation
- **Multi-runtime project support** - Single project can define scripts for different LLM backends

### Architecture
- **Separation of Concerns**: Runtime execution logic moved from CLI core to configurable scripts
- **ScriptRunner system**: Handles automatic `.prompt.md` compilation and runtime command transformation  
- **Flexible runtime targeting**: Projects define their own execution strategies via `awd.yml`

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
- Runtime management system with `awd runtime` commands (setup, list, remove, status)
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
- Initial release of AWD CLI - the NPM for AI-native development
- 6 core commands: `init`, `install`, `run`, `list`, `version`, `help`
- NPM-like developer workflow: Initialize → Install → Run
- Cross-platform binaries (no Python required)
- Multiple LLM runtime support: llm library, OpenAI Codex
- Hello world template with GitHub MCP integration
- Project-based configuration with awd.yml
- Automatic MCP dependency management
- Zero-dependency installation via curl script
- PyPI package distribution

### Installation
```bash
# Zero dependencies
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh

# Or with pip
pip install awd-cli
```

### Quick Start
```bash
awd init my-project
cd my-project
awd install
awd run --param name="Developer"
```

[0.0.10]: https://github.com/danielmeppiel/awd-cli/releases/tag/v0.0.10
