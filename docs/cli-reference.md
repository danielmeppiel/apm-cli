# AWD CLI Reference

Complete command-line interface reference for Agentic Workflow Definitions (AWD).

## Quick Start

```bash
# 1. Install AWD
curl -sSL https://raw.githubusercontent.com/danielmeppiel/awd-cli/main/install.sh | sh

# 2. Setup runtime
awd runtime setup codex
export GITHUB_TOKEN=your_github_token

# 3. Create and run project  
awd init my-project && cd my-project
awd install && awd run start --param name="Developer"
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

### `awd init` - 🚀 Initialize new AWD project

Initialize a new AWD project with sample prompt and configuration (like `npm init`).

```bash
awd init [PROJECT_NAME] [OPTIONS]
```

**Arguments:**
- `PROJECT_NAME` - Optional name for new project directory. Use `.` to explicitly initialize in current directory

**Options:**
- `-f, --force` - Overwrite existing files without confirmation
- `-y, --yes` - Skip interactive questionnaire and use defaults

**Examples:**
```bash
# Initialize in current directory (interactive)
awd init

# Initialize in current directory explicitly  
awd init .

# Create new project directory
awd init my-hello-world

# Force overwrite existing project
awd init --force

# Use defaults without prompts
awd init my-project --yes
```

**Behavior:**
- **Interactive mode**: Prompts for project details unless `--yes` specified
- **Existing projects**: Detects existing `awd.yml` and preserves configuration unless `--force` used
- **Strictly additive**: Like npm, preserves existing fields and values where possible

**Creates:**
- `awd.yml` - Project configuration with MCP dependencies
- `hello-world.prompt.md` - Sample prompt with GitHub integration
- `README.md` - Project documentation

### `awd install` - 📦 Install dependencies

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

### `awd run` - 🚀 Execute prompts

Execute a script defined in your awd.yml with parameters and real-time output streaming.

```bash
awd run [SCRIPT_NAME] [OPTIONS]
```

**Arguments:**
- `SCRIPT_NAME` - Name of script to run from awd.yml scripts section

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value` (can be used multiple times)

**Examples:**
```bash
# Run start script (default script)
awd run start --param name="Developer"

# Run with different scripts 
awd run start --param name="Alice"
awd run llm --param service=api
awd run debug --param service=api

# Run specific scripts with parameters
awd run llm --param service=api --param environment=prod
```

**Return Codes:**
- `0` - Success
- `1` - Execution failed or error occurred

### `awd preview` - 👀 Preview compiled scripts

Show the processed prompt content with parameters substituted, without executing.

```bash
awd preview [SCRIPT_NAME] [OPTIONS]
```

**Arguments:**
- `SCRIPT_NAME` - Name of script to preview from awd.yml scripts section

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value`

**Examples:**
```bash
# Preview start script
awd preview start --param name="Developer"

# Preview specific script with parameters
awd preview llm --param name="Alice"
```

### `awd list` - 📋 List available scripts

Display all scripts defined in awd.yml.

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
Available scripts:
  start: codex hello-world.prompt.md
  llm: llm hello-world.prompt.md -m github/gpt-4o-mini  
  debug: DEBUG=true codex hello-world.prompt.md
```

### `awd config` - ⚙️ Configure AWD CLI

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

### `awd runtime` - 🤖 Manage AI runtimes

AWD manages AI runtime installation and configuration automatically.

```bash
awd runtime COMMAND [OPTIONS]
```

#### `awd runtime setup` - ⚙️ Install AI runtime

Download and configure an AI runtime from official sources.

```bash
awd runtime setup RUNTIME_NAME [OPTIONS]
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to install: `codex` or `llm`

**Options:**
- `--vanilla` - Install runtime without AWD configuration (uses runtime's native defaults)

**Examples:**
```bash
# Install Codex with AWD defaults (GitHub Models, free)
awd runtime setup codex

# Install LLM with AWD defaults  
awd runtime setup llm

# Install Codex without AWD configuration (vanilla)
awd runtime setup codex --vanilla

# Install LLM without AWD configuration (vanilla)
awd runtime setup llm --vanilla
```

**Default Behavior:**
- Installs runtime binary from official sources
- Configures with GitHub Models (free) as AWD default
- Creates configuration file at `~/.codex/config.toml` or similar
- Provides clear logging about what's being configured

**Vanilla Behavior (`--vanilla` flag):**
- Installs runtime binary only
- No AWD-specific configuration applied
- Uses runtime's native defaults (e.g., OpenAI for Codex)
- No configuration files created by AWD

#### `awd runtime list` - 📋 Show installed runtimes

List all available runtimes and their installation status.

```bash
awd runtime list
```

**Output includes:**
- Runtime name and description
- Installation status (✅ Installed / ❌ Not installed)
- Installation path and version
- Configuration details

#### `awd runtime remove` - 🗑️ Uninstall runtime

Remove an installed runtime and its configuration.

```bash
awd runtime remove RUNTIME_NAME
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to remove: `codex` or `llm`

#### `awd runtime status` - 📊 Show runtime status

Display which runtime AWD will use for execution and runtime preference order.

```bash
awd runtime status
```

**Output includes:**
- Runtime preference order (codex → llm)
- Currently active runtime
- Next steps if no runtime is available

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
scripts:
  start: "codex hello-world.prompt.md"
  llm: "llm hello-world.prompt.md -m github/gpt-4o-mini"
  debug: "DEBUG=true codex hello-world.prompt.md"

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
awd run start --param name="Developer"

# 5. Preview before execution
awd preview start --param name="Developer"

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
    awd run code-review \
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
if awd run document --param project_name=$(basename $PWD); then
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
├── hello-world.prompt.md             # Main prompt file
├── prompts/
│   ├── code-review.prompt.md         # Code review prompt
│   └── documentation.prompt.md       # Documentation prompt
└── .github/
    └── workflows/
        └── awd-ci.yml                # CI using AWD prompts
```
