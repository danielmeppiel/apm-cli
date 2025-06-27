# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.0.1]: https://github.com/danielmeppiel/awd-cli/releases/tag/v0.0.1
