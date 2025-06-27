# AWD CLI Reference v0.0.1

Complete command-line interface reference for Agentic Workflow Definitions (AWD) v0.0.1.

## Quick Start

```bash
# 1. Install AWD
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh

# 2. Setup runtime
awd runtime setup codex
export GITHUB_TOKEN=your_github_token

# 3. Create and run project  
awd init my-project && cd my-project
awd install && awd run --param name="Developer"
```

## Installation

### Quick Install (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh
```

### Manual Download
Download from [GitHub Releases](https://github.com/danielmeppiel/awd-cli/releases/latest):
```bash
# Linux x86_64
curl -L https://github.com/danielmeppiel/awd-cli/releases/latest/download/awd-linux-x86_64 -o awd && chmod +x awd

# macOS Intel
curl -L https://github.com/danielmeppiel/awd-cli/releases/latest/download/awd-darwin-x86_64 -o awd && chmod +x awd

# macOS Apple Silicon  
curl -L https://github.com/danielmeppiel/awd-cli/releases/latest/download/awd-darwin-arm64 -o awd && chmod +x awd
```

### From Source (Developers)
```bash
git clone https://github.com/danielmeppiel/awd-cli.git
cd awd-cli && pip install -e .
```

## Global Options

```bash
awd [OPTIONS] COMMAND [ARGS]...
```

### Options
- `--version` - Show version and exit
- `--help` - Show help message and exit

## Core Commands

### `awd init` - Initialize new AWD project

Initialize a new AWD project with sample prompt and configuration (like `npm init`).

```bash
awd init [PROJECT_NAME]
```

**Arguments:**
- `PROJECT_NAME` - Optional name for new project directory

**Examples:**
```bash
# Initialize in current directory
awd init

# Create new project directory
awd init my-hello-world
```

**Creates:**
- `awd.yml` - Project configuration with MCP dependencies
- `hello-world.prompt.md` - Sample prompt with GitHub integration
- `README.md` - Project documentation

### `awd install` - Install dependencies

Install MCP server dependencies from `awd.yml` (like `npm install`).

```bash
awd install
```

**Examples:**
```bash
# Install all dependencies from awd.yml
awd install
```

**Requirements:** Must be run in a directory with `awd.yml` file.

### `awd run` - Execute prompts

Execute a prompt with parameters and real-time output streaming.

```bash
awd run [PROMPT_NAME] [OPTIONS]
```

**Arguments:**
- `PROMPT_NAME` - Optional name of prompt to run (uses entrypoint if not specified)

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value` (can be used multiple times)
- `--runtime TEXT` - Runtime to use (`codex`, `llm`) - default: auto-detect installed
- `--llm TEXT` - LLM model to use (for llm runtime)

**Examples:**
```bash
# Run entrypoint prompt (uses installed runtime automatically)
awd run --param name="Developer"

# Run with Codex (recommended - pre-configured with GitHub Models)
awd run hello-world --runtime=codex --param name="Alice"

# Run with LLM and specific model
awd run my-prompt --runtime=llm --llm=github/gpt-4o-mini --param service=api

# Run with OpenAI GPT-4 (requires llm keys set openai)
awd run code-review --runtime=llm --llm=gpt-4o
```

**Return Codes:**
- `0` - Success
- `1` - Execution failed or error occurred

### `awd preview` - Preview prompts without execution

Show the processed prompt content with parameters substituted, without executing.

```bash
awd preview [PROMPT_NAME] [OPTIONS]
```

**Arguments:**
- `PROMPT_NAME` - Optional name of prompt to preview (uses entrypoint if not specified)

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value`

**Examples:**
```bash
# Preview entrypoint prompt
awd preview --param name="Developer"

# Preview specific prompt with parameters
awd preview hello-world --param name="Alice"
```

### `awd list` - List available prompts

Display all discovered `.prompt.md` files in the current project.

```bash
awd list
```

**Examples:**
```bash
# List all prompts in project
awd list
```

**Output format:**
```
📍 hello-world: A hello world prompt demonstrating AWD with GitHub integration
   code-review: Security, quality & accessibility review
   tests: Unit test gap analysis and implementation

📍 = entrypoint (default when running 'awd run')
```

### `awd models` - List available models

Display all available LLM models across different providers.

```bash
awd models
```

**Examples:**
```bash
# List all available models
awd models
```

**Output:** Shows models grouped by provider:
- GitHub Models: `github/gpt-4o-mini`, `github/gpt-4o`, etc.
- OpenAI: `gpt-4o`, `gpt-4o-mini`, `o1`, etc.
- Local models (if Ollama configured)

### `awd config` - Configure AWD CLI

Display AWD CLI configuration information.

```bash
awd config [OPTIONS]
```

**Options:**
- `--show` - Show current configuration

**Examples:**
```bash
# Show current configuration
awd config --show
```

## Runtime Management

### `awd runtime` - Manage AI runtimes

AWD manages AI runtime installation and configuration automatically.

```bash
awd runtime COMMAND [OPTIONS]
```

#### `awd runtime setup` - Install AI runtime

Download and configure an AI runtime from official sources.

```bash
awd runtime setup RUNTIME_NAME
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to install: `codex` or `llm`

**Examples:**
```bash
# Install Codex CLI with GitHub Models (recommended)
awd runtime setup codex

# Install LLM library in managed environment
awd runtime setup llm
```

#### `awd runtime list` - Show installed runtimes

List all available runtimes and their installation status.

```bash
awd runtime list
```

**Output includes:**
- Runtime name and description
- Installation status (✅ Installed / ❌ Not installed)
- Installation path and version
- Configuration details

#### `awd runtime remove` - Uninstall runtime

Remove an installed runtime and its configuration.

```bash
awd runtime remove RUNTIME_NAME
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to remove: `codex` or `llm`

#### `awd runtime status` - Show runtime status

Display detailed status for a specific runtime.

```bash
awd runtime status RUNTIME_NAME
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to check: `codex` or `llm`

## Prerequisites by Runtime

### LLM Runtime
The `llm` library is included as a dependency. You only need to configure API keys:

```bash
# GitHub Models (free tier, recommended)
llm keys set github
# Enter your GitHub Personal Access Token

# OpenAI (paid)
llm keys set openai
# Enter your OpenAI API key

# Anthropic (paid)
llm keys set anthropic
# Enter your Anthropic API key
```

### Codex Runtime
```bash
# Install Codex CLI
npm install -g @openai/codex@native

# Set API key
export OPENAI_API_KEY=your_openai_api_key
```

## File Formats

### AWD Project Configuration (`awd.yml`)
```yaml
name: my-project
version: 1.0.0
description: My AWD application
author: Your Name
entrypoint: hello-world.prompt.md

dependencies:
  mcp:
    - ghcr.io/github/github-mcp-server
```

### Prompt Format (`.prompt.md`)
```markdown
---
description: Brief description of what this prompt does
mcp:
  - ghcr.io/github/github-mcp-server
input:
  - param1
  - param2
---

# Prompt Title

Your prompt content here with ${input:param1} substitution.
```

### Supported Prompt Locations
AWD discovers `.prompt.md` files anywhere in your project:
- `./hello-world.prompt.md`
- `./prompts/my-prompt.prompt.md`
- `./.github/prompts/workflow.prompt.md` 
- `./docs/prompts/helper.prompt.md`

## Quick Start Workflow

```bash
# 1. Initialize new project (like npm init)
awd init my-hello-world

# 2. Navigate to project
cd my-hello-world

# 3. Install dependencies (like npm install)
awd install

# 4. Run the hello world prompt
awd run --param name="Developer"

# 5. Preview before execution
awd preview --param name="Developer"

# 6. List available prompts
awd list
```

## Tips & Best Practices

1. **Start with runtime setup**: Run `awd runtime setup codex` for best experience
2. **Use GitHub Models for free tier**: Set `GITHUB_TOKEN` for free Codex access
3. **Preview before running**: Use `awd preview` to check parameter substitution
4. **Organize prompts**: Use descriptive names and place in logical directories
5. **Version control**: Include `.prompt.md` files and `awd.yml` in your git repository
6. **Parameter naming**: Use clear, descriptive parameter names in prompts
7. **Error handling**: Always check return codes in scripts and CI/CD
8. **MCP integration**: Declare MCP dependencies in both `awd.yml` and prompt frontmatter

## Integration Examples

### In CI/CD (GitHub Actions)
```yaml
- name: Setup AWD runtime
  run: |
    awd runtime setup codex
    export GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
    
- name: Setup AWD project
  run: awd install
    
- name: Run code review
  run: |
    awd run code-review --runtime=codex \
      --param pr_number=${{ github.event.number }}
```

### In Development Scripts
```bash
#!/bin/bash
# Setup and run AWD project
awd runtime setup codex
export GITHUB_TOKEN=your_token

cd my-awd-project
awd install

# Run documentation analysis
if awd run document --runtime=codex --param project_name=$(basename $PWD); then
    echo "Documentation analysis completed"
else
    echo "Documentation analysis failed" 
    exit 1
fi
```

### Project Structure Example
```
my-awd-project/
├── awd.yml                           # Project configuration
├── README.md                         # Project documentation  
├── hello-world.prompt.md             # Entrypoint prompt
├── prompts/
│   ├── code-review.prompt.md         # Code review prompt
│   └── documentation.prompt.md       # Documentation prompt
└── .github/
    └── workflows/
        └── awd-ci.yml                # CI using AWD prompts
```
