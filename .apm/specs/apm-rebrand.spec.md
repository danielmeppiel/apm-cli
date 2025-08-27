---
title: APM Rebranding Specification
description: Complete rebrand from AWD to APM (Agent Primitives Manager)
type: specification
priority: high
status: ready
version: 1.0.0
created: 2025-08-27
---

# APM Rebranding Specification

## Overview

**Objective**: Complete rebrand from "Agentic Workflow Definitions (AWD)" to "Agent Primitives Manager (APM)"

**Rationale**: 
- Clear distinction between the tool (APM) and the methodology (AI-Native Development)
- Leverages familiar npm mental model for faster adoption
- Eliminates AWS/AID confusion
- Professional, enterprise-ready naming

**Scope**: Complete codebase transformation with no backward compatibility (zero users)

## Naming Strategy

### New Identity
- **Tool Name**: Agent Primitives Manager (APM)
- **Value Proposition**: "The package manager for AI-Native Development"
- **Mental Model**: npm for Agent Primitives

### Clear Distinctions
- **APM** = The CLI tool (Agent Primitives Manager)
- **AI-Native Development** = The methodology/framework (unchanged)
- **Agent Primitives** = The configurable building blocks (unchanged)

## Implementation Tasks

### Phase 1: Core Infrastructure

#### Package & Build System
- [ ] `pyproject.toml`: Change package name `awd-cli` → `apm-cli`
- [ ] `pyproject.toml`: Change entry point `awd = "awd_cli.cli:main"` → `apm = "apm_cli.cli:main"`
- [ ] Rename directory: `src/awd_cli/` → `src/apm_cli/`
- [ ] Update all Python imports: `awd_cli` → `apm_cli`
- [ ] Rename file: `build/awd.spec` → `build/apm.spec`
- [ ] Update build spec: All references `awd` → `apm`

#### Configuration & Templates
- [ ] `templates/hello-world/awd.yml` → `apm.yml`
- [ ] `test-project/awd.yml` → `apm.yml`
- [ ] All code references: `awd.yml` → `apm.yml`
- [ ] All code references: `.awd/` → `.apm/`

#### Scripts & Installation
- [ ] `install.sh`: Update repo URLs `awd-cli` → `apm-cli`
- [ ] `install.sh`: Update binary names `awd` → `apm`
- [ ] `scripts/build-binary.sh`: Update output names
- [ ] All script references to commands

### Phase 2: Documentation

#### README.md Complete Rewrite
- [ ] Title: `# Agent Primitives Manager (APM)`
- [ ] Subtitle: `**The package manager for AI-Native Development**`
- [ ] All commands: `awd` → `apm`
- [ ] All files: `awd.yml` → `apm.yml`, `.awd/` → `.apm/`
- [ ] Repository URLs: `awd-cli` → `apm-cli`
- [ ] Infrastructure table: `APM Package Manager`

#### All Documentation
- [ ] `docs/cli-reference.md`: Update all commands and examples
- [ ] `docs/index.md`: Update tool description
- [ ] `docs/primitives.md`: Update references
- [ ] `docs/integration-testing.md`: Update commands
- [ ] `docs/runtime-integration.md`: Update setup
- [ ] All `docs/wip/*.md`: Update references
- [ ] `CONTRIBUTING.md`: Update repo and commands
- [ ] `SECURITY.md`: Update package references
- [ ] `CHANGELOG.md`: Add rebranding entry

### Phase 3: Test & Example Content

#### Tests & Examples
- [ ] All test files: Update command references
- [ ] `test-project/AGENTS.md`: Update generation comments
- [ ] `test-project/README.md`: Update commands
- [ ] Template documentation updates

### Phase 4: Repository & Distribution

#### GitHub & Distribution
- [ ] Rename repository: `awd-cli` → `apm-cli`
- [ ] Update repo description: "Agent Primitives Manager - The package manager for AI-Native Development"
- [ ] Binary names: `awd-*` → `apm-*`
- [ ] PyPI: Register `apm-cli` (no need to maintain old one)

## Search & Replace Patterns

### File/Directory Renames
```bash
src/awd_cli/ → src/apm_cli/
build/awd.spec → build/apm.spec
*/awd.yml → */apm.yml
```

### Global Code Changes
```bash
awd-cli → apm-cli
awd_cli → apm_cli
awd (space) → apm (space)  # CLI commands in docs/examples
awd.yml → apm.yml
.awd/ → .apm/
AWD CLI → APM CLI
"Agentic Workflow Definitions (AWD)" → "Agent Primitives Manager (APM)"
"AWD Package Manager" → "APM Package Manager"
```

## New Key Messaging

### Title Section
```markdown
# Agent Primitives Manager (APM)

**The package manager for AI-Native Development** - APM manages Agent Primitives that make AI-Native Development reliable and portable across any coding agent.

**Think npm + Node.js, but for AI-Native Development.**

| Traditional Web Dev | AI-Native Development | Role |
|---------------------|----------------------|------|
| **npm** | **APM Package Manager** | Dependency resolution, distribution |
| **TypeScript Compiler** | **APM Primitives Compiler** | Transform Agent Primitives → agents.md format |
```

### Installation Examples
```bash
# 1. Install APM CLI (zero dependencies)
curl -sSL https://raw.githubusercontent.com/danielmeppiel/apm-cli/main/install.sh | sh

# 2. Initialize AI-Native project
apm init my-ai-native-project

# 3. Compile Agent Primitives
apm compile

# 4. Execute workflows
apm run start --param name="Developer"
```

## Execution Strategy

### Timeline (4-Day Sprint)
- **Day 1**: Core infrastructure changes (package, imports, build)
- **Day 2**: Documentation rewrite (README, docs/)
- **Day 3**: Tests, examples, final cleanup
- **Day 4**: Repository rename and distribution setup

### Benefits of Clean Rebrand
- ✅ Simpler codebase (no legacy support code)
- ✅ Faster implementation (no migration complexity)  
- ✅ Cleaner documentation (no confusing transition notes)
- ✅ Better UX (single, clear way to use the tool)
- ✅ Professional launch (clean brand from day one)

## Validation Criteria

### Technical Validation
- [ ] All tests pass with new naming
- [ ] Binary builds successfully with new names
- [ ] Installation script works with new repository
- [ ] Documentation examples are executable

### Brand Validation
- [ ] Clear distinction between APM (tool) and AI-Native Development (practice)
- [ ] npm mental model is evident and helpful
- [ ] Professional, enterprise-ready positioning achieved
- [ ] No confusion with existing tools (AWS, etc.)

## Risk Mitigation

### Technical Risks
- **Import errors**: Comprehensive testing after each rename
- **Build failures**: Update all build configurations before testing
- **Documentation gaps**: Complete documentation review

### Brand Risks
- **Confusion**: Clear messaging distinguishing tool from methodology
- **Positioning**: Consistent "package manager" language throughout

## Success Metrics

- [ ] Repository successfully renamed
- [ ] All commands work with `apm` prefix
- [ ] Documentation is consistent and clear
- [ ] Build artifacts use new naming
- [ ] PyPI package is successfully registered
- [ ] No legacy AWD references remain

---

**This specification defines the complete transformation of AWD to APM, positioning it as "the package manager for AI-Native Development" with clean, professional branding.**