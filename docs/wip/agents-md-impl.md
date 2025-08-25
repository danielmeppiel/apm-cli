# **AGENTS.md Compilation Implementation Strategy**

Please ### **Phase 2 Implementation:**
- Generate optimal hierarchical `AGENTS.md` structure based on project analysis
- Root AGENTS.md: Global chatmode + shared context + universal instructions
- Nested AGENTS.md: Specialized context that overrides root for specific directories
- Intelligent placement: Only create nested files when they add meaningful specializationetch and read (agents-md-integration.md first)[../agents-md-integration.md].

## **Overview**

This document outlines the technical implementation strategy for compiling AWD primitives into `AGENTS.md` files, enabling seamless integration with the agents.md ecosystem while maintaining the modularity and intelligence of AWD's approach.

## **Strategic Context**

### **Problem Statement**
- **agents.md** provides universal context injection for 20+ coding agent CLIs with hierarchical override
- **AWD primitives** offer modular, reusable, and intelligent context management beyond what static files can provide
- **Integration gap**: Need to compile AWD primitives into optimized `AGENTS.md` hierarchies

### **Solution Approach**
AWD CLI becomes the **intelligent compiler** that transforms structured `.awd/` primitives into optimized `AGENTS.md` hierarchies, providing:
- **Primitive Reusability**: Share chatmodes and instructions across projects
- **Dynamic Compilation**: Generate context based on actual project structure and file presence
- **Intelligent Hierarchies**: Create optimal nested AGENTS.md structure automatically
- **Cross-Agent Compatibility**: Universal support while leveraging agent-specific features

---

## **Agent Primitive Compilation Strategy**

### **1. Chatmode.md Files**
**Purpose**: Define AI assistant behavior and approach for specific domains  
**Compilation Strategy**: 
- **Domain-Specific Behavior**: Different chatmodes for different parts of the project
- **applyTo Logic**: Like instructions, chatmodes can target specific file patterns
- **Phase 1**: Conditional sections based on `applyTo` patterns
- **Phase 2**: Directory-specific chatmode inclusion based on file presence
- **Runtime Selection**: `awd run prompt.md --mode=backend-engineer` for explicit override

**Chatmode Structure:**
```markdown
---
applyTo: "src/backend/**/*.{py,js}"
description: "Backend development specialist"
---
You are a backend development specialist focused on secure API development, 
database design, and server-side architecture. You prioritize security-first 
design patterns and comprehensive testing strategies.
```

**Phase 1 Implementation:**
```markdown
## Development Approach

### For Backend Development (when working on src/backend/**, **/*.py)
{content from backend-engineer.chatmode.md}

### For Frontend Development (when working on src/frontend/**, **/*.tsx)
{content from frontend-engineer.chatmode.md}

### For Architecture & Planning (when working on docs/**, specs/**)
{content from architect.chatmode.md}
```

**Phase 2 Implementation:**
- Generate directory-specific `AGENTS.md` files with appropriate chatmode
- Backend directories get backend chatmode, frontend directories get frontend chatmode
- Hierarchical behavior: specific chatmodes override general ones

### **2. Instructions.md Files**
**Purpose**: Conditional development guidelines based on file types  
**Compilation Strategy**:
- **Phase 1**: Conditional sections using `applyTo` patterns
- **Phase 2**: Directory-specific inclusion based on actual file presence
- **Format**: "When working on [file types]..." sections

**Implementation:**
```markdown
## Development Guidelines

### When working on TypeScript files (*.ts, *.tsx)
{content from instructions with applyTo: "**/*.{ts,tsx}"}

### When working on Python files (*.py)  
{content from instructions with applyTo: "**/*.py"}
```

### **3. Context.md / Memory.md Files**
**Purpose**: Reusable knowledge blocks referenced via markdown hyperlinks  
**Compilation Strategy**:
- **NOT directly included** in `AGENTS.md`
- **Reference Resolution**: When `chatmode.md` or `instructions.md` contain `[link](../context/architecture.md)`, resolve and inline the content
- **Smart Linking**: Follow markdown links and include referenced content

**Implementation:**
```python
def resolve_markdown_links(content):
    """Resolve [text](path.md) links and inline referenced content."""
    # Parse markdown links
    # Read referenced files  
    # Replace links with actual content
    # Return enhanced content
```

### **4. Spec.md Files**
**Purpose**: Implementation specifications for features/components  
**Compilation Strategy**:
- **NOT included in `AGENTS.md`** by default
- **On-demand Usage**: User explicitly references specs when needed
- **User Workflow**: `codex "implement auth based on spec file .awd/specs/auth.md"`
- **Reference Support**: If `instructions.md` contains `${spec:auth}`, resolve and inline

**Implementation:**
- Specs remain as separate files
- AWD CLI can resolve `${spec:name}` references in prompts
- Agent CLIs read specs when explicitly provided by user

### **5. .prompt.md Files**
**Purpose**: Executable workflows that combine primitives  
**Compilation Strategy**:
- **NOT included in `AGENTS.md`** - these are executable, not context
- **Remain Executable**: Continue to work via `awd run workflow.prompt.md`
- **Optional Listing**: Could include "Available Workflows" section for discovery

**Implementation:**
```markdown
## Available Workflows
- `awd run feature-implementation.prompt.md` - Implement features with validation gates
- `awd run code-review.prompt.md` - Comprehensive code review process
```

---

## **Two-Phase Implementation Strategy**

### **Phase 1: Single Smart AGENTS.md (MVP - 2 weeks)**

#### **Goal**: Generate one intelligent root `AGENTS.md` file

#### **Compilation Algorithm:**
```python
def compile_single_agents_md():
    """Generate single AGENTS.md with conditional sections."""
    
    # 1. Load all chatmodes with applyTo patterns
    chatmodes = load_all_chatmodes()
    
    # 2. Load all instructions with applyTo patterns
    instructions = load_all_instructions()
    
    # 3. Resolve markdown links in chatmodes and instructions
    chatmodes = [(resolve_markdown_links(content), pattern) for content, pattern in chatmodes]
    instructions = [(resolve_markdown_links(content), pattern) for content, pattern in instructions]
    
    # 4. Auto-detect project setup commands
    setup_commands = auto_detect_setup_commands()
    
    # 5. Generate structured AGENTS.md with conditional chatmodes and instructions
    agents_md = build_agents_md_template(
        chatmodes=chatmodes,
        instructions=instructions,
        setup_commands=setup_commands
    )
    
    # 6. Write to root directory
    write_file("AGENTS.md", agents_md)
```

#### **Generated Structure:**
```markdown
# AGENTS.md
<!-- Generated by AWD CLI from .awd/ primitives -->

## Development Approach
{content from default chatmode.md with resolved links}

## Project Setup
{auto-detected setup commands from package.json, requirements.txt, etc.}

## Development Guidelines

### When working on TypeScript files (*.ts, *.tsx)
{content from typescript.instructions.md with resolved context links}

### When working on Python files (*.py)
{content from python.instructions.md with resolved context links}

### When working on test files (*test*, *spec*)
{content from testing.instructions.md with resolved context links}

## Available Workflows
- `awd run feature-implementation.prompt.md` - Spec-first feature development
- `awd run code-review.prompt.md` - Systematic code review
```

#### **Commands:**
```bash
awd compile                          # Generate AGENTS.md with default chatmode
awd compile --mode=backend-engineer  # Generate with specific chatmode
awd compile --watch                  # Auto-regenerate on primitive changes
```

### **Phase 2: Multi-File Directory-Based (4 weeks)**

#### **Goal**: Generate multiple `AGENTS.md` files based on directory structure and file presence

#### **Compilation Algorithm:**
```python
def compile_multi_file_agents_md():
    """Generate multiple AGENTS.md files based on directory analysis."""
    
    # 1. Scan all directories with files
    directories = get_directories_with_files()
    
    # 2. For each directory, determine applicable instructions
    for directory in directories:
        applicable_instructions = []
        directory_files = get_files_in_directory(directory)
        
        # Check which instructions apply to files in this directory
        for instruction in get_all_instructions():
            apply_to_pattern = get_apply_to_pattern(instruction)
            if any_file_matches_pattern(directory_files, apply_to_pattern):
                applicable_instructions.append(instruction)
        
        # 3. Generate AGENTS.md if instructions apply or if root directory
        if applicable_instructions or directory == project_root:
            # Inherit from parent + add specific instructions
            parent_context = get_parent_context(directory)
            resolved_instructions = [resolve_markdown_links(inst) for inst in applicable_instructions]
            
            agents_md = build_directory_agents_md(
                parent_context=parent_context,
                specific_instructions=resolved_instructions,
                directory=directory
            )
            
            write_file(f"{directory}/AGENTS.md", agents_md)
```

#### **Example Multi-File Output:**
```
project/
├── AGENTS.md                    # Global: Default chatmode + shared context + universal patterns
├── src/
│   ├── frontend/
│   │   ├── AGENTS.md           # Frontend specialist mode + React/TypeScript focus
│   │   └── components/
│   │       └── Button.tsx      # Uses frontend/AGENTS.md (no additional override needed)
│   └── backend/
│       ├── AGENTS.md           # Backend specialist mode + API/security focus
│       └── api/
│           ├── auth/
│           │   ├── AGENTS.md   # Security specialist mode + auth-specific context
│           │   └── auth.py
│           └── user.py         # Uses backend/AGENTS.md
```

**Key Insight**: AWD creates **meaningful specialization hierarchies**, not duplicate content.

#### **Commands:**
```bash
awd compile --multi-file             # Generate hierarchical AGENTS.md files
awd compile --multi-file --dry-run   # Preview what would be generated
awd compile --directory=src/frontend # Generate for specific directory only
```

---

## **Technical Implementation Details**

### **Markdown Link Resolution**
```python
def resolve_markdown_links(content):
    """Resolve markdown links to context/memory files."""
    import re
    
    link_pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
    
    def replace_link(match):
        link_text = match.group(1)
        file_path = match.group(2)
        
        # Resolve relative path from .awd/ directory
        full_path = resolve_path_from_awd_dir(file_path)
        
        if Path(full_path).exists():
            content = Path(full_path).read_text()
            return f"\n### {link_text}\n{content}\n"
        else:
            return match.group(0)  # Keep original link if file not found
    
    return re.sub(link_pattern, replace_link, content)
```

### **Pattern Matching**
```python
def any_file_matches_pattern(files, pattern):
    """Check if any files match the applyTo pattern."""
    import fnmatch
    
    for file_path in files:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False
```

### **Auto-Detection of Setup Commands**
```python
def auto_detect_setup_commands():
    """Auto-detect common setup commands from project files."""
    commands = []
    
    if Path("package.json").exists():
        commands.extend([
            "npm install",
            "npm run dev",
            "npm test"
        ])
    
    if Path("requirements.txt").exists():
        commands.extend([
            "pip install -r requirements.txt",
            "python -m pytest"
        ])
    
    if Path("Cargo.toml").exists():
        commands.extend([
            "cargo build",
            "cargo test"
        ])
    
    return commands
```

---

## **Integration Points**

### **Migration from Existing agents.md**
```bash
awd init --from-agents-md    # Convert existing AGENTS.md to AWD primitives
```

### **Runtime Chatmode Selection**
```bash
awd run feature-impl.prompt.md --mode=backend-engineer
awd run code-review.prompt.md --mode=senior-architect
```

### **Watch Mode for Development**
```bash
awd compile --watch    # Auto-regenerate AGENTS.md when primitives change
```

---

## **Success Metrics**

### **Phase 1 Success Criteria:**
- ✅ Generate valid `AGENTS.md` that works with all agent CLIs
- ✅ Conditional instructions based on file types
- ✅ Markdown link resolution for context files
- ✅ Auto-detection of project setup commands
- ✅ Chatmode selection and compilation

### **Phase 2 Success Criteria:**
- ✅ Multi-file generation based on directory analysis
- ✅ Hierarchical context inheritance
- ✅ Precise instruction targeting per directory
- ✅ Performance optimization for large projects
- ✅ Backward compatibility with Phase 1

### **Overall Success:**
- **Universal Compatibility**: Generated `AGENTS.md` hierarchies work optimally with all agent CLIs
- **Zero Configuration**: Intelligent hierarchy generation with sensible specialization
- **Enhanced Intelligence**: Context is more relevant and specialized than manual hierarchies
- **Primitive Reusability**: Share and compose battle-tested chatmodes across projects
- **Developer Adoption**: Easy migration path with immediate value from modular primitives

---

## **Next Steps**

1. **Week 1-2**: Implement Phase 1 single-file compilation
2. **Week 3**: Add markdown link resolution and chatmode selection
3. **Week 4**: Implement migration from existing agents.md files
4. **Week 5-8**: Develop Phase 2 multi-file generation
5. **Week 9-10**: Testing, documentation, and community feedback

This implementation strategy positions AWD CLI as the **intelligent compiler for the agents.md ecosystem**, providing immediate value while building toward sophisticated multi-file capabilities.