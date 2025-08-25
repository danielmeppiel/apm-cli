# {{project_name}}

An AWD (Agentic Workflow Definitions) application with comprehensive primitives compilation examples.

## Quick Start

```bash
# Install dependencies
awd install

# Compile AWD primitives into AGENTS.md
awd compile

# Run the hello world prompt
awd run start --param name="Developer"

# Run feature implementation workflow
awd run feature --param feature_name="User Authentication" --param feature_description="Implement secure user login and registration"

# Preview before execution
awd preview --param name="Developer"
```

## AWD Primitives Compilation

This project demonstrates the full AWD primitives system:

### Available Primitives
- **Chatmodes**: `default`, `backend-engineer`
- **Instructions**: TypeScript, Python, Testing guidelines
- **Context**: Project information, Architecture guidelines
- **Specs**: Feature specifications and requirements

### Compilation Commands
```bash
# Compile all primitives into AGENTS.md
awd compile

# Watch for changes and auto-recompile
awd compile --watch

# Validate primitives without compiling
awd compile --validate

# Dry run to preview output
awd compile --dry-run

# Use specific chatmode
awd compile --chatmode backend-engineer
```

### Directory Structure
```
.awd/
├── chatmodes/
│   ├── default.chatmode.md
│   └── backend-engineer.chatmode.md
├── instructions/
│   ├── typescript.instructions.md
│   ├── python.instructions.md
│   └── testing.instructions.md
├── context/
│   ├── project-info.context.md
│   └── architecture.context.md
└── specs/
    └── hello-feature.spec.md
```

## Available Workflows
- `hello-world.prompt.md` - Basic hello world demonstration
- `feature-implementation.prompt.md` - Implement features with validation gates

## About

This project was created with AWD - The NPM for AI-Native Development.

Learn more at: https://github.com/danielmeppiel/awd-cli
