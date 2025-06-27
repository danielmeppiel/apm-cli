# Runtime Integration Guide

AWD manages LLM runtime installation and configuration automatically. This guide covers the supported runtimes and how to use them.

## Overview

AWD acts as a runtime package manager, downloading and configuring LLM runtimes from their official sources:

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

```bash
# Run with Codex (auto-selected when installed)
awd run my-prompt

# Explicit runtime selection
awd run my-prompt --runtime=codex
```

## LLM Runtime

AWD can also install the LLM library for advanced model support and manual configuration.

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

```bash
# Run with LLM runtime
awd run my-prompt --runtime=llm --llm=github/gpt-4o-mini
awd run my-prompt --runtime=llm --llm=gpt-4o
awd run my-prompt --runtime=llm --llm=claude-3.5-sonnet
```

## Examples by Use Case

### Basic Usage
```bash
# Default: Uses Codex if installed, otherwise LLM
awd run my-prompt --param key=value

# Explicit runtime selection
awd run my-prompt --runtime=codex
awd run my-prompt --runtime=llm --llm=github/gpt-4o-mini
```

### Code Analysis
```bash
# Codex excels at code understanding
awd run code-review --runtime=codex --param pull_request=123
```

### Documentation Tasks
```bash
# Use GitHub Models for free text processing
awd run document --runtime=llm --llm=github/gpt-4o-mini \
  --param project_name=my-project
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
