# AWD CLI Reference v0.0.1

Complete command-line interface reference for Agentic Workflow Definitions (AWD) v0.0.1.

## Installation

```bash
# Development installation (current)
git clone https://github.com/danielmeppiel/awd-cli.git
cd awd-cli && pip install -e .

# Future PyPI installation
pip install awd-cli
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
- `--runtime TEXT` - Runtime to use (`llm`, `codex`) - default: `llm`
- `--llm TEXT` - LLM model to use (for llm runtime)

**Examples:**
```bash
# Run entrypoint prompt
awd run --param name="Developer"

# Run specific prompt with GitHub Models (free tier)
awd run hello-world --runtime=llm --llm=github/gpt-4o-mini --param name="Alice"

# Run with Codex (requires OPENAI_API_KEY)
awd run my-prompt --runtime=codex --param service=api

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

1. **Start with init**: Always begin with `awd init` to create proper project structure
2. **Use GitHub Models for free tier**: Start with `--runtime=llm --llm=github/gpt-4o-mini`
3. **Preview before running**: Use `awd preview` to check parameter substitution
4. **Organize prompts**: Use descriptive names and place in logical directories
5. **Version control**: Include `.prompt.md` files and `awd.yml` in your git repository
6. **Parameter naming**: Use clear, descriptive parameter names in prompts
7. **Error handling**: Always check return codes in scripts and CI/CD
8. **MCP integration**: Declare MCP dependencies in both `awd.yml` and prompt frontmatter

## Integration Examples

### In CI/CD (GitHub Actions)
```yaml
- name: Setup AWD project
  run: |
    awd install
    
- name: Run code review
  run: |
    awd run code-review --runtime=llm --llm=github/gpt-4o-mini \
      --param pr_number=${{ github.event.number }}
```

### In Development Scripts
```bash
#!/bin/bash
# Setup and run AWD project
cd my-awd-project
awd install

# Run documentation analysis
if awd run document --runtime=llm --llm=github/gpt-4o-mini --param project_name=$(basename $PWD); then
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
