# AWD Primitives Guide

AWD primitives are the foundational building blocks for AI-powered development workflows. They include chatmodes, instructions, and context files that define how AI assistants should behave and what information they should have access to.

## Overview

The AWD CLI supports three types of primitives:

- **Chatmodes** (`.chatmode.md`) - Define AI assistant personalities and behaviors
- **Instructions** (`.instructions.md`) - Provide coding standards and guidelines for specific file types
- **Context** (`.context.md`, `.memory.md`) - Supply background information and project context

## File Structure

### Supported Locations

AWD discovers primitives in these locations:

```
# AWD-native structure
.awd/
├── chatmodes/           # AI assistant definitions
│   └── *.chatmode.md
├── instructions/        # Coding standards and guidelines  
│   └── *.instructions.md
├── context/            # Project context files
│   └── *.context.md
└── memory/             # Team info, contacts, etc.
    └── *.memory.md

# VSCode-compatible structure  
.github/
├── chatmodes/          # VSCode Copilot chatmodes
│   └── *.chatmode.md
└── instructions/       # VSCode Copilot instructions
    └── *.instructions.md

# Generic files (anywhere in project)
*.chatmode.md
*.instructions.md
*.context.md
*.memory.md
```

## Primitive Types

### Chatmodes

Chatmodes define AI assistant personalities and specialized behaviors for different development tasks.

**Format:** `.chatmode.md`

**Frontmatter:**
- `description` (required) - Clear explanation of the chatmode purpose
- `applyTo` (optional) - Glob pattern for file targeting (e.g., `"**/*.{py,js}"`)
- `author` (optional) - Creator information
- `version` (optional) - Version string

**Example:**
```markdown
---
description: AI pair programming assistant for code review
author: Development Team
applyTo: "**/*.{py,js,ts}"
version: "1.0.0"
---

# Code Review Assistant

You are an expert software engineer specializing in code review.

## Your Role
- Analyze code for bugs, security issues, and performance problems
- Suggest improvements following best practices
- Ensure code follows team conventions

## Communication Style
- Be constructive and specific in feedback
- Explain reasoning behind suggestions
- Prioritize critical issues over style preferences
```

### Instructions

Instructions provide coding standards, conventions, and guidelines that apply to specific file types or patterns.

**Format:** `.instructions.md`

**Frontmatter:**
- `description` (required) - Clear explanation of the standards
- `applyTo` (required) - Glob pattern for file targeting (e.g., `"**/*.py"`)
- `author` (optional) - Creator information
- `version` (optional) - Version string

**Example:**
```markdown
---
description: Python coding standards and documentation requirements
applyTo: "**/*.py"
author: Development Team
version: "2.0.0"
---

# Python Coding Standards

## Style Guide
- Follow PEP 8 for formatting
- Maximum line length of 88 characters (Black formatting)
- Use type hints for all function parameters and returns

## Documentation Requirements
- All public functions must have docstrings
- Include Args, Returns, and Raises sections
- Provide usage examples for complex functions

## Example Format
```python
def calculate_metrics(data: List[Dict], threshold: float = 0.5) -> Dict[str, float]:
    """Calculate performance metrics from data.
    
    Args:
        data: List of data dictionaries containing metrics
        threshold: Minimum threshold for filtering
    
    Returns:
        Dictionary containing calculated metrics
    
    Raises:
        ValueError: If data is empty or invalid
    """
```

### Context Files

Context files provide background information, project details, and other relevant context that AI assistants should be aware of.

**Format:** `.context.md` or `.memory.md` files

**Frontmatter:**
- `description` (optional) - Brief description of the context
- `author` (optional) - Creator information
- `version` (optional) - Version string

**Examples:**

Project context (`.awd/context/project-info.context.md`):
```markdown
---
description: Project overview and architecture
---

# AWD CLI Project

## Overview
Command-line tool for AI-powered development workflows.

## Key Technologies
- Python 3.9+ with Click framework
- YAML frontmatter for configuration
- Rich library for terminal output

## Architecture
- Modular runtime system
- Plugin-based workflow engine
- Extensible primitive system
```

Team information (`.awd/memory/team-contacts.memory.md`):
```markdown
# Team Contacts

## Development Team
- Lead Developer: Alice Johnson (alice@company.com)
- Backend Engineer: Bob Smith (bob@company.com)

## Emergency Contacts
- On-call: +1-555-0123
- Incidents: incidents@company.com

## Meeting Schedule
- Daily standup: 9:00 AM PST
- Sprint planning: Mondays 2:00 PM PST
```

## Discovery and Parsing

The AWD CLI automatically discovers and parses all primitive files in your project:

```python
from awd_cli.primitives import discover_primitives

# Discover all primitives in current directory
collection = discover_primitives()

print(f"Found {collection.count()} primitives:")
print(f"  Chatmodes: {len(collection.chatmodes)}")
print(f"  Instructions: {len(collection.instructions)}")  
print(f"  Contexts: {len(collection.contexts)}")

# Access individual primitives
for chatmode in collection.chatmodes:
    print(f"Chatmode: {chatmode.name}")
    print(f"  Description: {chatmode.description}")
    if chatmode.apply_to:
        print(f"  Applies to: {chatmode.apply_to}")
```

## Validation

All primitives are automatically validated during discovery:

- **Chatmodes**: Must have description and content
- **Instructions**: Must have description, applyTo pattern, and content
- **Context**: Must have content (description optional)

Invalid files are skipped with warning messages, allowing valid primitives to continue loading.

## Best Practices

### 1. Clear Naming
Use descriptive names that indicate purpose:
- `code-review-assistant.chatmode.md`
- `python-documentation.instructions.md`
- `team-contacts.md`

### 2. Targeted Application
Use specific `applyTo` patterns for instructions:
- `"**/*.py"` for Python files
- `"**/*.{ts,tsx}"` for TypeScript React files
- `"**/test_*.py"` for Python test files

### 3. Version Control
Keep primitives in version control alongside your code. Use semantic versioning for breaking changes.

### 4. Organized Structure
Use the structured `.awd/` directories for better organization:
```
.awd/
├── chatmodes/
│   ├── code-reviewer.chatmode.md
│   └── documentation-writer.chatmode.md
├── instructions/
│   ├── python-style.instructions.md
│   └── typescript-conventions.instructions.md
└── context/
    ├── project-info.context.md
    └── architecture-overview.context.md
```

### 5. Team Collaboration
- Include author information in frontmatter
- Document the purpose and scope of each primitive
- Regular review and updates as standards evolve

## Integration with VSCode

For VSCode Copilot compatibility, place files in `.github/` directories:
```
.github/
├── chatmodes/
│   └── assistant.chatmode.md
└── instructions/
    └── coding-standards.instructions.md
```

These files follow the same format and will be discovered alongside AWD-specific primitives.

## Error Handling

The primitive system handles errors gracefully:

- **Malformed YAML**: Files with invalid frontmatter are skipped with warnings
- **Missing required fields**: Validation errors are reported clearly
- **File access issues**: Permission and encoding problems are handled safely
- **Invalid patterns**: Glob pattern errors are caught and reported

This ensures that a single problematic file doesn't prevent other primitives from loading.