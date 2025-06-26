# AWD CLI Reference

Complete command-line interface reference for Agentic Workflow Definitions (AWD).

## Installation

```bash
# Development installation (current)
git clone https://github.com/danielmeppiel/awd-cli.git
cd awd-cli && pip install -e .

# Future PyPI installation (Phase 1)
pip install awd-cli
```

## Global Options

```bash
awd [OPTIONS] COMMAND [ARGS]...
```

### Options
- `--version` - Show version and exit
- `-c, --client TEXT` - Target MCP client (vscode, cursor, claude) - *Note: Currently used for MCP commands only*
- `--help` - Show help message and exit

## Core Commands

### `awd run` - Execute prompts and workflows

Execute a prompt or workflow with parameters and real-time output streaming.

```bash
awd run NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Name of the prompt/workflow to run

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value` (can be used multiple times)
- `--runtime TEXT` - Runtime to use (`llm`, `codex`)
- `--llm TEXT` - LLM model to use (for llm runtime)

**Examples:**
```bash
# Run with GitHub Models (free tier)
awd run document --runtime=llm --llm=github/gpt-4o-mini

# Run with parameters
awd run analyze-logs --runtime=llm --llm=github/gpt-4o-mini \
  --param service_name=api --param time_window=1h

# Run with Codex (requires OPENAI_API_KEY)
awd run code-review --runtime=codex

# Run with OpenAI GPT-4 (requires llm keys set openai)
awd run tests --runtime=llm --llm=gpt-4o
```

**Return Codes:**
- `0` - Success
- `1` - Execution failed or error occurred

### `awd preview` - Preview prompts without execution

Show the processed prompt content with parameters substituted, without executing.

```bash
awd preview NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Name of the prompt/workflow to preview

**Options:**
- `-p, --param TEXT` - Parameter in format `name=value`

**Examples:**
```bash
# Preview with parameters
awd preview document --param project_name=my-app

# Preview without parameters
awd preview code-review
```

### `awd list` - List available prompts and workflows

Display all discovered `.prompt.md` files in the current project.

```bash
awd list
```

**Examples:**
```bash
# List all prompts and workflows
awd list
```

**Output format:**
```
- document (prompt): Documentation gap analysis
- tests (prompt): Unit test gap analysis and implementation
- code-review (prompt): Security, quality & accessibility review
```

## Creation Commands

### `awd create prompt` - Create new prompt template

Create a new `.prompt.md` file with standard template.

```bash
awd create prompt NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Name of the prompt to create

**Options:**
- `-d, --description TEXT` - Description for the prompt

**Examples:**
```bash
# Create basic prompt
awd create prompt my-prompt

# Create with description
awd create prompt analyze-performance -d "Performance analysis prompt"
```

**Output:** Creates `prompts/NAME.prompt.md` with template content.

### `awd create workflow` - Create new workflow template

Create a new workflow following VSCode `.github/prompts` convention.

```bash
awd create workflow NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Name of the workflow to create

**Options:**
- `-d, --description TEXT` - Description for the workflow

**Examples:**
```bash
# Create basic workflow
awd create workflow incident-response

# Create with description  
awd create workflow deploy-app -d "Application deployment workflow"
```

**Output:** Creates `.github/prompts/NAME.prompt.md` with workflow template.

## Runtime Commands

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

## Configuration Commands

### `awd config` - Configure AWD CLI

Manage AWD CLI configuration settings.

```bash
awd config [OPTIONS]
```

**Options:**
- `--set-client TEXT` - Set default MCP client
- `--show` - Show current configuration

**Examples:**
```bash
# Show current config
awd config --show

# Set default client (for MCP commands)
awd config --set-client vscode
```

## MCP Commands (WIP - Phase 2)

> **⚠️ Note**: MCP commands are currently work-in-progress. They point to a demo registry and installation is not reliable.

### `awd mcp list` - List installed MCP servers

```bash
awd mcp list
```

### `awd mcp registry list` - List available servers in registry

```bash
awd mcp registry list
```

### `awd mcp registry search` - Search registry

```bash
awd mcp registry search QUERY
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

### Prompt Format (`.prompt.md`)
```markdown
---
description: Brief description of what this prompt does
input:
  - param1
  - param2
---

# Prompt Title

Your prompt content here with ${input:param1} substitution.
```

### Supported Locations
AWD discovers `.prompt.md` files anywhere in your project:
- `./prompts/my-prompt.prompt.md`
- `./.github/prompts/workflow.prompt.md` 
- `./docs/prompts/helper.prompt.md`
- `./my-prompt.prompt.md`

## Tips & Best Practices

1. **Use GitHub Models for free tier**: Start with `--runtime=llm --llm=github/gpt-4o-mini`
2. **Preview before running**: Use `awd preview` to check parameter substitution
3. **Organize prompts**: Use descriptive names and place in logical directories
4. **Version control**: Include `.prompt.md` files in your git repository
5. **Parameter naming**: Use clear, descriptive parameter names in prompts
6. **Error handling**: Always check return codes in scripts and CI/CD

## Integration Examples

### In CI/CD (GitHub Actions)
```yaml
- name: Run code review
  run: |
    awd run code-review --runtime=llm --llm=github/gpt-4o-mini \
      --param pr_number=${{ github.event.number }}
```

### In Development Scripts
```bash
#!/bin/bash
# Run documentation analysis
if awd run document --runtime=llm --llm=github/gpt-4o-mini --param project_name=$(basename $PWD); then
    echo "Documentation analysis completed"
else
    echo "Documentation analysis failed" 
    exit 1
fi
```
