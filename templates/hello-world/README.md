# {{project_name}}

An AWD (Agentic Workflow Definitions) application demonstrating primitives compilation and best practices.

## Quick Start

```bash
# Install dependencies
awd install

# Compile primitives into AGENTS.md
awd compile

# Run the hello world prompt
awd run --param name="Developer"

# Preview before execution
awd preview --param name="Developer"
```

## AWD Primitives

This project showcases AWD's primitive system:

- **Chatmodes** (`.awd/chatmodes/`): Define AI assistant personalities
- **Instructions** (`.awd/instructions/`): File-type specific coding guidelines  
- **Context** (`.awd/context/`): Shared project knowledge
- **Specs** (`.awd/specs/`): Feature specifications and requirements

### Compilation Examples

```bash
# Generate AGENTS.md with default chatmode
awd compile

# Use specific chatmode
awd compile --chatmode backend-engineer

# Watch mode for development
awd compile --watch

# Preview without writing files
awd compile --dry-run
```

## Available Workflows

- `hello-world.prompt.md` - Basic hello world demonstration
- `feature-implementation.prompt.md` - Implement features with validation gates

## About

This project was created with AWD - The NPM for AI-Native Development.

Learn more at: https://github.com/danielmeppiel/awd-cli
