# AWD Decision Log

Internal tracking of major decisions and changes.

## v0.0.1 - June 2025 - NPM-like CLI

**Date**: June 27, 2025  
**Breaking**: Yes - Complete CLI redesign

### Changes Made

**Added:**
- `awd init [name]` - Creates project with awd.yml + hello-world.prompt.md
- `awd install` - Installs MCP deps from awd.yml (hides MCP complexity)
- `awd run [prompt]` - Runs entrypoint if no prompt specified
- Project-based workflow with awd.yml (like package.json)
- Enhanced .prompt.md frontmatter with `mcp:` field
- Entrypoint system for default prompt execution

**Removed:**
- All `awd mcp *` commands (kept internal functions for `awd install`)
- `awd create prompt/workflow` commands
- `awd workflow *` command group
- `--client` global option

### Command Mapping

| Old | New | Notes |
|-----|-----|-------|
| `awd create prompt` | `awd init` | Now creates full project |
| `awd mcp install` | `awd install` | Automatic from awd.yml |
| `awd workflow run` | `awd run` | Uses entrypoint by default |

### Key Decisions

1. **npm-like workflow**: `init` → `install` → `run` for developer familiarity
2. **Hide MCP complexity**: Users work with AWD apps, not MCP servers directly  
3. **Project-based**: Everything starts with `awd init` (no standalone prompts)
4. **Breaking changes**: Clean slate, no backward compatibility
5. **Real integration**: Hello world uses actual GitHub MCP with `get_me` tool
6. **Binary distribution**: Eliminate Python installation barrier with self-contained executables

### Implementation Status

**COMPLETED ✅** - All features implemented and tested:
- Template-based project initialization with variable substitution
- NPM-like developer workflow (init → install → run)  
- Project-based configuration with awd.yml
- Automatic MCP dependency management
- Complete documentation updates
- Full CLI redesign with 6 simple commands
- End-to-end validation of complete workflow
- **Binary distribution system with PyInstaller**
- **Zero-dependency installation via curl script**
- **Cross-platform binaries (Linux x86_64, macOS x86_64/ARM64)**
- **11MB self-contained executables with UPX compression**

### Files Updated

- **CLI**: Complete rewrite of `src/awd_cli/cli.py`
- **Docs**: `README.md`, `docs/cli-reference.md` 
- **Version**: Updated to 0.0.1 throughout

### Testing

✅ Full workflow: `awd init` → `awd install` → `awd list` → `awd run`  
✅ Hello world creates working GitHub MCP integration  
✅ Error handling for missing awd.yml
