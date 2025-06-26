# Runtime Integration Guide

AWD supports multiple AI runtime environments for executing prompts. This guide covers setup and usage for each supported runtime.

## Overview

AWD acts as a universal interface to different AI runtimes:

| Runtime | Description | Best For | API Keys Required |
|---------|-------------|----------|-------------------|
| [**LLM Library**](https://llm.datasette.io/en/stable/index.html) | Simon Willison's `llm` CLI | General use, many providers | Provider-specific |
| [**OpenAI Codex**](https://github.com/openai/codex) | OpenAI's Codex CLI | Code-focused tasks, MCP support | OpenAI API key |

## LLM Runtime (Recommended)

The `llm` library is included automatically with AWD installation and supports 100+ models across multiple providers, including GitHub Models.

### Setup

#### 1. No installation needed
The `llm` library is automatically installed as an AWD dependency.

#### 2. Configure API Keys

**GitHub Models (Free Tier - Recommended)**
```bash
# Get a GitHub Personal Access Token with "Models" permission
# Visit: https://github.com/settings/personal-access-tokens/new

llm keys set github
# Paste your GitHub PAT when prompted
```

**OpenAI (Paid)**
```bash
llm keys set openai
# Enter your OpenAI API key from https://platform.openai.com
```

**Anthropic (Paid)**
```bash
llm keys set anthropic  
# Enter your Anthropic API key from https://console.anthropic.com
```

**Local Models with Ollama (Free)**
```bash
# Install Ollama first: https://ollama.ai
# Pull a model
ollama pull llama3.2

# Install llm-ollama plugin
pip install llm-ollama

# No API key needed for local models
```

### Usage

#### Basic Execution
```bash
# Use GitHub Models (free)
awd run my-prompt --runtime=llm --llm=github/gpt-4o-mini

# Use OpenAI GPT-4
awd run my-prompt --runtime=llm --llm=gpt-4o

# Use Anthropic Claude
awd run my-prompt --runtime=llm --llm=claude-3.5-sonnet

# Use local Ollama model
awd run my-prompt --runtime=llm --llm=llama3.2
```

#### Available Models
```bash
# List all available models
awd models

# Common models:
# - github/gpt-4o-mini (free, fast)
# - github/gpt-4o (free, high quality) 
# - gpt-4o (paid, OpenAI)
# - claude-3.5-sonnet (paid, Anthropic)
# - ollama/llama3.2 (free, local)
```

#### Advanced Configuration
```bash
# Set default model in prompt frontmatter
---
description: My prompt
llm: github/gpt-4o-mini
---

# Or override at runtime
awd run my-prompt --runtime=llm --llm=gpt-4o
```

### Troubleshooting

**"No API key configured"**
```bash
# Check configured keys
llm keys list

# Set missing key
llm keys set <provider>
```

**"Model not found"**
```bash
# List available models
awd models

# Check if provider plugin is installed
pip list | grep llm-
```

**"Rate limit exceeded"**
- Try GitHub Models (higher rate limits)
- Switch to different provider
- Wait and retry

## OpenAI Codex Runtime

OpenAI's Codex CLI provides advanced code understanding and MCP server support.

### Setup

#### 1. Install Codex CLI
```bash
npm install -g @openai/codex@native
```

#### 2. Configure API Key
```bash
# Set OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Or add to your shell profile
echo 'export OPENAI_API_KEY=your_key' >> ~/.bashrc
```

#### 3. Verify Installation
```bash
codex --version
# Should show: codex-cli 0.0.2505291458 or similar
```

### Usage

#### Basic Execution
```bash
# Run with Codex (uses OpenAI API)
awd run my-prompt --runtime=codex

# Parameters work the same way
awd run analyze-code --runtime=codex --param file_path=src/main.py
```

## Examples by Use Case

### Documentation Analysis
```bash
# Use GitHub Models (free, good for text)
awd run document --runtime=llm --llm=github/gpt-4o-mini \
  --param project_name=my-project
```

### Code Review
```bash
# Use Codex for code understanding
awd run code-review --runtime=codex \
  --param pull_request=123

# Or use LLM with GPT-4 for high quality
awd run code-review --runtime=llm --llm=gpt-4o \
  --param pull_request=123
```

### Unit Test Generation
```bash
# Codex excels at code generation
awd run tests --runtime=codex \
  --param test_file=src/utils.py

# LLM works too with good prompts
awd run tests --runtime=llm --llm=github/gpt-4o \
  --param test_file=src/utils.py
```

### Cost Optimization Analysis
```bash
# Use GitHub Models for free analysis
awd run az-cost-optimize --runtime=llm --llm=github/gpt-4o-mini \
  --param subscription_id=your-sub-id
```

## Runtime Development

### Adding Custom Models (LLM Runtime)
```bash
# Install provider plugins
pip install llm-claude-3        # Anthropic
pip install llm-ollama          # Local models
pip install llm-gpt4all         # Local models

# List new models
awd models
```

### Getting Help
- Run commands with `--help` flag
- Check `awd models` for available models  
- Use `awd preview` to debug prompt issues
- Check the [AWD CLI Reference](cli-reference.md) for command details
