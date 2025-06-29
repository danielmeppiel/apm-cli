# Runtime Integration Guide

AWD manages LLM runtime installation and configuration automatically. This guide covers the supported runtimes, how to use them, and how to extend AWD with additional runtimes.

## Overview

AWD acts as a runtime package manager, downloading and configuring LLM runtimes from their official sources. Currently supports two runtimes:

| Runtime | Description | Best For | Configuration |
|---------|-------------|----------|---------------|
| [**OpenAI Codex**](https://github.com/openai/codex) | OpenAI's Codex CLI | Code tasks, MCP support | Auto-configured with GitHub Models |
| [**LLM Library**](https://llm.datasette.io/en/stable/index.html) | Simon Willison's `llm` CLI | General use, many providers | Manual API key setup |

## Quick Setup

### Install AWD and Setup Runtime
```bash
# 1. Install AWD
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh

# 2. Setup AI runtime (downloads and configures automatically)
awd runtime setup codex

# 3. Set GitHub token for free models
export GITHUB_TOKEN=your_github_token
```

### Runtime Management
```bash
awd runtime list              # Show installed runtimes
awd runtime setup llm         # Install LLM library
awd runtime setup codex       # Install Codex CLI
```

## OpenAI Codex Runtime (Recommended)

AWD automatically downloads, installs, and configures the Codex CLI with GitHub Models for free usage.

### Setup

#### 1. Install via AWD
```bash
awd runtime setup codex
```

This automatically:
- Downloads the latest Codex binary for your platform
- Installs to `~/.awd/runtimes/codex`
- Creates configuration for GitHub Models (`openai/gpt-4.1`)
- Updates your PATH

#### 2. Set GitHub Token
```bash
# Get a GitHub Personal Access Token with "Models" permission
# Visit: https://github.com/settings/personal-access-tokens/new
export GITHUB_TOKEN=your_github_token
```

### Usage

AWD executes scripts defined in your `awd.yml`. When scripts reference `.prompt.md` files, AWD compiles them with parameter substitution. See [Prompts Guide](prompts.md) for details.

```bash
# Run scripts (from awd.yml) with parameters
awd run start --param service_name=api-gateway
awd run debug --param service_name=api-gateway
```

**Script Configuration (awd.yml):**
```yaml
scripts:
  start: "codex analyze-logs.prompt.md"
  debug: "DEBUG=true codex analyze-logs.prompt.md"
```

## LLM Runtime

AWD also supports the LLM library runtime with multiple model providers and manual configuration.

### Setup

#### 1. Install via AWD
```bash
awd runtime setup llm
```

This automatically:
- Creates a Python virtual environment
- Installs the `llm` library and dependencies
- Creates a wrapper script at `~/.awd/runtimes/llm`

#### 2. Configure API Keys (Manual)
```bash
# GitHub Models (free)
llm keys set github
# Paste your GitHub PAT when prompted

# Other providers
llm keys set openai     # OpenAI API key
llm keys set anthropic  # Anthropic API key
```

### Usage

AWD executes scripts defined in your `awd.yml`. See [Prompts Guide](prompts.md) for details on prompt compilation.

```bash
# Run scripts that use LLM runtime
awd run llm-script --param service_name=api-gateway
awd run analysis --param time_window="24h"
```

**Script Configuration (awd.yml):**
```yaml
scripts:
  llm-script: "llm analyze-logs.prompt.md -m github/gpt-4o-mini"
  analysis: "llm performance-analysis.prompt.md -m gpt-4o"
```

## Examples by Use Case

### Basic Usage
```bash
# Run scripts defined in awd.yml
awd run start --param service_name=api-gateway
awd run llm --param service_name=api-gateway
awd run debug --param service_name=api-gateway
```

### Code Analysis
```bash
# Scripts that use Codex for code understanding
awd run code-review --param pull_request=123
awd run analyze-code --param file_path="src/main.py"
```

### Documentation Tasks
```bash
# Scripts that use LLM for text processing
awd run document --param project_name=my-project
awd run summarize --param report_type="weekly"
```

## Troubleshooting

**"Runtime not found"**
```bash
# Install missing runtime
awd runtime setup codex
awd runtime setup llm

# Check installed runtimes
awd runtime list
```

**"No GitHub token"**
```bash
# Set GitHub token for free models
export GITHUB_TOKEN=your_github_token
```

**"Command not found: codex"**
```bash
# Ensure PATH is updated (restart terminal)
# Or reinstall runtime
awd runtime setup codex
```

## Extending AWD with New Runtimes

AWD's runtime system is designed to be extensible. To add support for a new runtime:

### Architecture

AWD's runtime system consists of three main components:

1. **Runtime Adapter** (`src/awd_cli/runtime/`) - Python interface for executing prompts
2. **Setup Script** (`scripts/runtime/`) - Shell script for installation and configuration  
3. **Runtime Manager** (`src/awd_cli/runtime/manager.py`) - Orchestrates installation and discovery

### Adding a New Runtime

1. **Create Runtime Adapter** - Extend `RuntimeAdapter` in `src/awd_cli/runtime/your_runtime.py`
2. **Create Setup Script** - Add installation script in `scripts/runtime/setup-your-runtime.sh`
3. **Register Runtime** - Add entry to `supported_runtimes` in `RuntimeManager`
4. **Update CLI** - Add runtime to command choices in `cli.py`
5. **Update Factory** - Add runtime to `RuntimeFactory`

### Best Practices

- Follow the `RuntimeAdapter` interface
- Use `setup-common.sh` utilities for platform detection and PATH management
- Handle errors gracefully with clear messages
- Test installation works after setup completes
- Support vanilla mode (no AWD-specific configuration)

### Contributing

To contribute a new runtime to AWD:

1. Fork the repository and follow the extension guide above
2. Add tests and update documentation
3. Submit a pull request

The AWD team welcomes contributions for popular LLM runtimes!
