# APM CLI Reference

Complete command-line interface reference for Agent Primitives Manager (APM).

## Quick Start

```bash
# 1. Install APM
curl -sSL https://raw.githubusercontent.com/danielmeppiel/apm-cli/main/install.sh | sh

# 2. Setup runtime
apm runtime setup codex
export GITHUB_TOKEN=your_github_token

# 3. Create and run project  
apm init my-project && cd my-project
apm install && apm run start --param name="Developer"
```

## Installation

### Quick Install (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/danielmeppiel/apm-cli/main/install.sh | sh
```

### Manual Download
Download from [GitHub Releases](https://github.com/danielmeppiel/apm-cli/releases/latest):
```bash
# Linux x86_64
curl -L https://github.com/danielmeppiel/apm-cli/releases/latest/download/apm-linux-x86_64 -o apm && chmod +x apm

# macOS Intel
curl -L https://github.com/danielmeppiel/apm-cli/releases/latest/download/apm-darwin-x86_64 -o apm && chmod +x apm

# macOS Apple Silicon  
curl -L https://github.com/danielmeppiel/apm-cli/releases/latest/download/apm-darwin-arm64 -o apm && chmod +x apm
```

### From Source (Developers)
```bash
git clone https://github.com/danielmeppiel/apm-cli.git
cd apm-cli && pip install -e .
```

## Global Options

```bash
apm [OPTIONS] COMMAND [ARGS]...
```

### Options
- `--version` - Show version and exit
- `--help` - Show help message and exit

## Core Commands

### `apm init` - 🚀 Initialize new APM project

Initialize a new APM project with sample prompt and configuration (like `npm init`).

```bash
apm init [PROJECT_NAME] [OPTIONS]
```

**Arguments:**
- `PROJECT_NAME` - Optional name for new project directory. Use `.` to explicitly initialize in current directory

**Options:**
- `-f, --force` - Overwrite existing files without confirmation
- `-y, --yes` - Skip interactive questionnaire and use defaults

**Examples:**
```bash
# Initialize in current directory (interactive)
apm init

# Initialize in current directory explicitly  
apm init .

# Create new project directory
apm init my-hello-world

# Force overwrite existing project
apm init --force

# Use defaults without prompts
apm init my-project --yes
```

**Behavior:**
- **Interactive mode**: Prompts for project details unless `--yes` specified
- **Existing projects**: Detects existing `apm.yml` and preserves configuration unless `--force` used
- **Strictly additive**: Like npm, preserves existing fields and values where possible

**Creates:**
- `apm.yml` - Project configuration with MCP dependencies
- `hello-world.prompt.md` - Sample prompt with GitHub integration
- `README.md` - Project documentation

### `apm install` - 📦 Install dependencies

Install MCP server dependencies from `apm.yml` (like `npm install`).

```bash
apm install
```

**Examples:**
```bash
# Install all dependencies from apm.yml
apm install
```

**Requirements:** Must be run in a directory with `apm.yml` file.

### `apm run` - 🚀 Execute prompts

Execute a script defined in your apm.yml with parameters and real-time output streaming.

```bash
apm run [SCRIPT_NAME] [OPTIONS]
```

**Arguments:**
- `SCRIPT_NAME` - Name of script to run from apm.yml scripts section

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value` (can be used multiple times)

**Examples:**
```bash
# Run start script (default script)
apm run start --param name="Developer"

# Run with different scripts 
apm run start --param name="Alice"
apm run llm --param service=api
apm run debug --param service=api

# Run specific scripts with parameters
apm run llm --param service=api --param environment=prod
```

**Return Codes:**
- `0` - Success
- `1` - Execution failed or error occurred

### `apm preview` - 👀 Preview compiled scripts

Show the processed prompt content with parameters substituted, without executing.

```bash
apm preview [SCRIPT_NAME] [OPTIONS]
```

**Arguments:**
- `SCRIPT_NAME` - Name of script to preview from apm.yml scripts section

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value`

**Examples:**
```bash
# Preview start script
apm preview start --param name="Developer"

# Preview specific script with parameters
apm preview llm --param name="Alice"
```

### `apm list` - 📋 List available scripts

Display all scripts defined in apm.yml.

```bash
apm list
```

**Examples:**
```bash
# List all prompts in project
apm list
```

**Output format:**
```
Available scripts:
  start: codex hello-world.prompt.md
  llm: llm hello-world.prompt.md -m github/gpt-4o-mini  
  debug: RUST_LOG=debug codex hello-world.prompt.md
```

### `apm compile` - 📝 Compile APM primitives into AGENTS.md

Compile APM primitives (chatmodes, instructions, contexts) into a single intelligent AGENTS.md file with conditional sections, markdown link resolution, and project setup auto-detection.

```bash
apm compile [OPTIONS]
```

**Options:**
- `-o, --output TEXT` - Output file path (default: AGENTS.md)
- `--chatmode TEXT` - Chatmode to prepend to the AGENTS.md file
- `--dry-run` - Generate content without writing file
- `--no-links` - Skip markdown link resolution
- `--watch` - Auto-regenerate on changes (file system monitoring)
- `--validate` - Validate primitives without compiling

**Examples:**
```bash
# Basic compilation with auto-detected primitives
apm compile

# Generate with specific chatmode
apm compile --chatmode architect

# Preview without writing file
apm compile --dry-run

# Custom output file
apm compile --output docs/AI-CONTEXT.md

# Validate primitives without generating output
apm compile --validate

# Watch for changes and auto-recompile (development mode)
apm compile --watch

# Watch mode with dry-run for testing
apm compile --watch --dry-run
```

**Watch Mode:**
- Monitors `.apm/`, `.github/instructions/`, `.github/chatmodes/` directories
- Auto-recompiles when `.md` or `apm.yml` files change
- Includes 1-second debounce to prevent rapid recompilation
- Press Ctrl+C to stop watching
- Requires `watchdog` library (automatically installed)

**Validation Mode:**
- Checks primitive structure and frontmatter completeness
- Displays actionable suggestions for fixing validation errors
- Exits with error code 1 if validation fails
- No output file generation in validation-only mode

**Configuration Integration:**
The compile command supports configuration via `apm.yml`:

```yaml
compilation:
  output: "AGENTS.md"           # Default output file
  chatmode: "backend-engineer"  # Default chatmode to use
  resolve_links: true           # Enable markdown link resolution
```

Command-line options always override `apm.yml` settings. Priority order:
1. Command-line flags (highest priority)
2. `apm.yml` compilation section
3. Built-in defaults (lowest priority)

**Generated AGENTS.md structure:**
- **Header** - Generation metadata and APM version
- **Pattern-based Sections** - Content grouped by exact `applyTo` patterns from instruction primitives (e.g., "Files matching `**/*.py`")
- **Footer** - Regeneration instructions

The structure is entirely dictated by the instruction primitives found in `.apm/` and `.github/instructions/` directories. No predefined sections or project detection are applied.

**Primitive Discovery:**
- **Chatmodes**: `.chatmode.md` files in `.apm/chatmodes/`, `.github/chatmodes/`
- **Instructions**: `.instructions.md` files in `.apm/instructions/`, `.github/instructions/`
- **Contexts**: `.context.md`, `.memory.md` files in `.apm/context/`, `.github/context/`
- **Workflows**: `.prompt.md` files in project and `.github/prompts/`

### `apm config` - ⚙️ Configure APM CLI

Display APM CLI configuration information.

```bash
apm config [OPTIONS]
```

**Options:**
- `--show` - Show current configuration

**Examples:**
```bash
# Show current configuration
apm config --show
```

## Runtime Management

### `apm runtime` - 🤖 Manage AI runtimes

APM manages AI runtime installation and configuration automatically. Currently supports two runtimes: `codex` and `llm`.

```bash
apm runtime COMMAND [OPTIONS]
```

**Supported Runtimes:**
- **`codex`** - OpenAI Codex CLI with GitHub Models support (recommended)
- **`llm`** - Simon Willison's LLM library with multiple providers

#### `apm runtime setup` - ⚙️ Install AI runtime

Download and configure an AI runtime from official sources.

```bash
apm runtime setup RUNTIME_NAME [OPTIONS]
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to install: `codex` or `llm`

**Options:**
- `--vanilla` - Install runtime without APM configuration (uses runtime's native defaults)

**Examples:**
```bash
# Install Codex with APM defaults (GitHub Models, free)
apm runtime setup codex

# Install LLM with APM defaults  
apm runtime setup llm

# Install Codex without APM configuration (vanilla)
apm runtime setup codex --vanilla

# Install LLM without APM configuration (vanilla)
apm runtime setup llm --vanilla
```

**Default Behavior:**
- Installs runtime binary from official sources
- Configures with GitHub Models (free) as APM default
- Creates configuration file at `~/.codex/config.toml` or similar
- Provides clear logging about what's being configured

**Vanilla Behavior (`--vanilla` flag):**
- Installs runtime binary only
- No APM-specific configuration applied
- Uses runtime's native defaults (e.g., OpenAI for Codex)
- No configuration files created by APM

#### `apm runtime list` - 📋 Show installed runtimes

List all available runtimes and their installation status.

```bash
apm runtime list
```

**Output includes:**
- Runtime name and description
- Installation status (✅ Installed / ❌ Not installed)
- Installation path and version
- Configuration details

#### `apm runtime remove` - 🗑️ Uninstall runtime

Remove an installed runtime and its configuration.

```bash
apm runtime remove RUNTIME_NAME
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to remove: `codex` or `llm`

#### `apm runtime status` - 📊 Show runtime status

Display which runtime APM will use for execution and runtime preference order.

```bash
apm runtime status
```

**Output includes:**
- Runtime preference order (codex → llm)
- Currently active runtime
- Next steps if no runtime is available

#### `apm runtime status` - Show runtime status

Display detailed status for a specific runtime.

```bash
apm runtime status RUNTIME_NAME
```

**Arguments:**
- `RUNTIME_NAME` - Runtime to check: `codex` or `llm`

## File Formats

### APM Project Configuration (`apm.yml`)
```yaml
name: my-project
version: 1.0.0
description: My APM application
author: Your Name
scripts:
  start: "codex hello-world.prompt.md"
  llm: "llm hello-world.prompt.md -m github/gpt-4o-mini"
  debug: "RUST_LOG=debug codex hello-world.prompt.md"

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
APM discovers `.prompt.md` files anywhere in your project:
- `./hello-world.prompt.md`
- `./prompts/my-prompt.prompt.md`
- `./.github/prompts/workflow.prompt.md` 
- `./docs/prompts/helper.prompt.md`

## Quick Start Workflow

```bash
# 1. Initialize new project (like npm init)
apm init my-hello-world

# 2. Navigate to project
cd my-hello-world

# 3. Install dependencies (like npm install)
apm install

# 4. Run the hello world prompt
apm run start --param name="Developer"

# 5. Preview before execution
apm preview start --param name="Developer"

# 6. List available prompts
apm list
```

## Tips & Best Practices

1. **Start with runtime setup**: Run `apm runtime setup codex` for best experience
2. **Use GitHub Models for free tier**: Set `GITHUB_TOKEN` for free Codex access
3. **Preview before running**: Use `apm preview` to check parameter substitution
4. **Organize prompts**: Use descriptive names and place in logical directories
5. **Version control**: Include `.prompt.md` files and `apm.yml` in your git repository
6. **Parameter naming**: Use clear, descriptive parameter names in prompts
7. **Error handling**: Always check return codes in scripts and CI/CD
8. **MCP integration**: Declare MCP dependencies in both `apm.yml` and prompt frontmatter

## Integration Examples

### In CI/CD (GitHub Actions)
```yaml
- name: Setup APM runtime
  run: |
    apm runtime setup codex
    export GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
    
- name: Setup APM project
  run: apm install
    
- name: Run code review
  run: |
    apm run code-review \
      --param pr_number=${{ github.event.number }}
```

### In Development Scripts
```bash
#!/bin/bash
# Setup and run APM project
apm runtime setup codex
export GITHUB_TOKEN=your_token

cd my-apm-project
apm install

# Run documentation analysis
if apm run document --param project_name=$(basename $PWD); then
    echo "Documentation analysis completed"
else
    echo "Documentation analysis failed" 
    exit 1
fi
```

### Project Structure Example
```
my-apm-project/
├── apm.yml                           # Project configuration
├── README.md                         # Project documentation  
├── hello-world.prompt.md             # Main prompt file
├── prompts/
│   ├── code-review.prompt.md         # Code review prompt
│   └── documentation.prompt.md       # Documentation prompt
└── .github/
    └── workflows/
        └── apm-ci.yml                # CI using APM prompts
```
