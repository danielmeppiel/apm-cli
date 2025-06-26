# Development Status

Current state of AWD CLI features, testing coverage, and development roadmap.

## Feature Status Matrix

### ✅ Fully Working (Phase 1 - Complete)
| Feature | Status | Test Coverage | Documentation |
|---------|--------|---------------|---------------|
| **CLI Foundation** | ✅ Complete | ✅ Unit Tests | ✅ CLI Reference |
| **LLM Runtime Integration** | ✅ Complete | ✅ Integration Tests | ✅ Runtime Guide |
| **Codex Runtime Integration** | ✅ Complete | ✅ Integration Tests | ✅ Runtime Guide |
| **Prompt Discovery** | ✅ Complete | ✅ Unit Tests | ✅ CLI Reference |
| **Parameter Substitution** | ✅ Complete | ✅ Unit Tests | ✅ Prompt Guide |
| **Preview Functionality** | ✅ Complete | ✅ Unit Tests | ✅ CLI Reference |
| **Real-time Output Streaming** | ✅ Complete | ✅ Manual Tests | ✅ Runtime Guide |
| **Enhanced CLI Logging** | ✅ Complete | ✅ Manual Tests | ✅ CLI Reference |
| **Prompt Creation Templates** | ✅ Complete | ✅ Unit Tests | ✅ CLI Reference |

### 🚧 Work in Progress (Phase 2 - Planned)
| Feature | Status | ETA | Notes |
|---------|--------|-----|-------|
| **MCP Server Installation** | 🚧 Stub Implementation | Week 6-8 | Points to demo registry |
| **MCP Runtime Execution** | 🚧 Declared Only | Week 8-10 | Can declare deps, can't execute |
| **PyPI Package Distribution** | 🚧 Not Started | Week 2-3 | Setup CI/CD pipeline |
| **GitHub Action** | 🚧 Not Started | Week 3-4 | Marketplace publication |

### 🔮 Future (Phase 3 - Roadmap)
| Feature | Status | ETA | Notes |
|---------|--------|-----|-------|
| **Workflow Composition** | 🔮 Planned | Week 12-14 | Chaining prompts together |
| **GitHub Package Management** | 🔮 Planned | Week 14-16 | Install from GitHub repos |
| **Community Registry** | 🔮 Planned | Week 16-18 | Public prompt sharing |
| **Advanced Orchestration** | 🔮 Planned | Week 18-20 | Complex workflow coordination |

## Testing Coverage

### ✅ Well Tested
- **CLI Commands**: All core commands (`run`, `preview`, `list`, `create`)
- **Runtime Adapters**: LLM and Codex runtime integration
- **Prompt Parsing**: YAML frontmatter and content parsing
- **Parameter Substitution**: All variable replacement scenarios
- **Error Handling**: Common error cases and edge conditions

### 🧪 Manual Testing Only
- **Real-time Output Streaming**: Verified manually, needs automated tests
- **CLI User Experience**: Visual formatting and color output
- **End-to-end Workflows**: Full prompt execution scenarios

### ❌ Not Tested (WIP Features)
- **MCP Server Installation**: Stub implementation, not reliable
- **MCP Registry Integration**: Points to demo registry
- **Package Distribution**: No CI/CD pipeline yet
- **Workflow Composition**: Parsing works, execution not implemented

## Known Limitations

### Current Limitations (Phase 1)
1. **MCP Integration**: 
   - ❌ Can declare MCP dependencies in prompts but cannot execute them
   - ❌ MCP registry points to demo endpoint (not production-ready)
   - ❌ Installation commands exist but are unreliable

2. **Distribution**:
   - ❌ Not published to PyPI (development install only)
   - ❌ No GitHub Action available yet
   - ❌ Manual installation required

3. **Workflow Features**:
   - ❌ Workflow composition syntax parses but doesn't execute
   - ❌ No support for chaining prompts together
   - ❌ No conditional logic or approval gates

### Workarounds
1. **For MCP functionality**: Use natural language instructions instead of tool calls
2. **For distribution**: Use `git clone` and `pip install -e .` for now
3. **For workflows**: Run individual prompts separately until Phase 3