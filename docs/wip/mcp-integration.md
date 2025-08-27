# MCP Integration (Work in Progress)

**Status**: Phase 2 - Planning and Development  
**ETA**: Week 6-10 (MCP runtime integration)  
**Current State**: Stub implementation with demo registry

## Overview

Model Context Protocol (MCP) integration will enable APM prompts to call external tools and APIs. This is a major Phase 2 feature that requires collaboration with runtime providers.

## Current Implementation (Phase 1)

### What Works
```bash
# MCP commands exist but point to demo registry
apm mcp list                    # ✅ Lists installed servers
apm mcp registry list           # ✅ Queries demo registry  
apm mcp registry search logs    # ✅ Searches demo registry
```

### What's Stubbed
```bash
# Installation commands exist but are unreliable
apm mcp install redis-server    # ❌ May not work reliably
apm mcp verify                  # ❌ Points to demo registry
```

### Prompt Declaration (Works for Parsing)
```markdown
---
description: Analyze application logs
mcp:
  - logs-analyzer
  - monitoring-tools
input: [service_name, time_window]
---

# Analyze Logs

Use the logs-analyzer tool to examine ${input:service_name} logs.
```

**Current Behavior**: 
- ✅ YAML frontmatter parses correctly
- ✅ MCP dependencies are detected and listed
- ❌ **Tools are NOT available during prompt execution**
- ❌ Prompts must rely on natural language instructions only

## Architecture Plan (Phase 2)

### Approach 1: LLM Library Integration
Collaborate with Simon Willison on native MCP support in the `llm` library.

**Advantages:**
- ✅ Consistent with APM's current LLM runtime
- ✅ Community-driven development
- ✅ Standard MCP client implementation
- ✅ Multiple model provider support

**Implementation:**
```python
# Future LLM runtime with MCP
class LLMRuntime(RuntimeAdapter):
    def execute_prompt(self, prompt_content: str, mcp_servers: List[str] = None):
        # Install/configure MCP servers in LLM runtime
        if mcp_servers:
            self._configure_mcp_servers(mcp_servers)
        
        # Execute with tool calling enabled
        return self._execute_with_tools(prompt_content)
```

**Timeline:**
- Week 6-7: Research and design collaboration
- Week 8-9: Implement MCP client in LLM library  
- Week 10: APM integration testing

### Approach 2: Codex CLI Integration  
Leverage existing MCP support in OpenAI's Codex CLI.

**Advantages:**
- ✅ Native MCP client already implemented
- ✅ Robust sandboxing and security
- ✅ No additional development needed in runtime
- ✅ Production-ready MCP handling

**Implementation:**
```python
# Codex runtime already supports MCP
class CodexRuntime(RuntimeAdapter):
    def execute_prompt(self, prompt_content: str, mcp_servers: List[str] = None):
        # Codex handles MCP configuration automatically
        cmd = ["codex", "exec"]
        if mcp_servers:
            cmd.extend(["--mcp-servers"] + mcp_servers)
        cmd.append(prompt_content)
        # Execute with native MCP support
```

**Timeline:**
- Week 6: Test current Codex MCP capabilities
- Week 7: Integrate APM MCP declarations with Codex
- Week 8: Documentation and testing

## MCP Registry Strategy

### Current State: Demo Registry
```
Registry URL: https://demo.registry.azure-mcp.net
Status: For development and testing only
Reliability: Not guaranteed for production
```

### Phase 2 Options

**Option A: Azure MCP Registry (Production)**
- Leverage production Azure MCP Registry
- Reliable server discovery and installation
- Enterprise-grade availability

**Option B: GitHub-Based Registry**
- Use GitHub repos as MCP server sources
- Version control via Git tags
- Community-driven server ecosystem
- Similar to npm/pip model

**Option C: Hybrid Approach**
- Support multiple registry sources
- Azure registry for enterprise servers
- GitHub for community servers
- Local configuration for private servers

## Implementation Timeline

### Week 6: Research & Design
- [ ] Evaluate LLM library MCP plugin architecture
- [ ] Test Codex CLI MCP capabilities
- [ ] Choose primary registry strategy
- [ ] Design APM MCP integration API

### Week 7: Runtime Integration
- [ ] Implement chosen runtime MCP support
- [ ] Create MCP server installation system
- [ ] Design reliable dependency resolution

### Week 8: APM Integration
- [ ] Connect prompt MCP declarations to runtime
- [ ] Implement automatic server installation
- [ ] Add MCP-specific error handling

### Week 9: Testing & Validation
- [ ] Test with existing MCP-enabled prompts
- [ ] Validate az-cost-optimize and document prompts
- [ ] End-to-end integration testing

### Week 10: Documentation & Polish
- [ ] Update documentation with MCP examples
- [ ] Create MCP troubleshooting guide
- [ ] Performance optimization

## Expected User Experience (Phase 2)

### Automatic MCP Server Management
```bash
# APM detects MCP dependencies and installs automatically
apm run az-cost-optimize --param subscription_id=abc123

# Output:
# Installing MCP servers: azure-cost-analyzer, github-issues
# ✓ azure-cost-analyzer v1.2.0 installed
# ✓ github-issues v2.1.0 installed  
# Running az-cost-optimize...
# [Real-time output with tool calls]
```

### Manual MCP Management
```bash
# Install specific MCP server
apm mcp install azure-cost-analyzer

# List available servers  
apm mcp registry list

# Verify prompt dependencies
apm mcp verify --prompt az-cost-optimize
```

### Enhanced Prompt Capabilities
```markdown
---
description: Azure cost optimization with automated issue creation
mcp:
  - azure-cost-analyzer    # Query Azure billing APIs
  - github-issues          # Create GitHub issues automatically
input: [subscription_id, repository]
---

# Azure Cost Optimization

1. **Analyze Azure Costs**
   Use azure-cost-analyzer to examine subscription ${input:subscription_id}:
   - Identify overprovisioned resources
   - Find unused resources  
   - Calculate potential savings

2. **Create Optimization Issues**
   For each optimization opportunity, use github-issues to:
   - Create detailed GitHub issue in ${input:repository}
   - Include cost analysis and recommended actions
   - Tag with "cost-optimization" label
```

## Technical Challenges

### 1. MCP Server Installation
**Challenge**: Reliable installation across different environments
**Solution**: 
- Use runtime-specific package managers
- Fallback to git-based installation
- Clear error messages for failed installations

### 2. Dependency Resolution
**Challenge**: Managing MCP server versions and conflicts
**Solution**:
- Lock file approach (similar to package-lock.json)
- Semantic versioning support
- Isolation between different prompts

### 3. Runtime Compatibility  
**Challenge**: Different MCP implementations across runtimes
**Solution**:
- Abstract MCP interface in APM
- Runtime-specific MCP adapters
- Feature detection and graceful degradation

### 4. Security and Sandboxing
**Challenge**: MCP servers can access external APIs and file systems
**Solution**:
- Leverage runtime sandboxing (Codex built-in, LLM plugins)
- Permission-based MCP server declarations
- User confirmation for sensitive operations

## Example Prompts for Testing

### Azure Cost Optimization
```markdown
---
description: Analyze Azure costs and create GitHub issues
mcp: [azure-cost-analyzer, github-issues]
input: [subscription_id, repository]
---
# Tests full MCP integration with external APIs
```

### Documentation Analysis  
```markdown
---
description: Analyze codebase and create documentation issues
mcp: [github-api, file-analyzer]
input: [repository, target_coverage]
---
# Tests file system access and GitHub API integration
```

### Log Analysis
```markdown
---
description: Analyze application logs for issues
mcp: [log-analyzer, slack-notifier]
input: [service_name, time_window, alert_channel]  
---
# Tests log processing and notification systems
```

## Migration Strategy

### From Phase 1 to Phase 2
1. **Existing prompts continue working** with natural language instructions
2. **MCP-enabled prompts gain tool capabilities** automatically
3. **Backward compatibility** maintained for all Phase 1 features
4. **Gradual migration** - prompts can opt-in to MCP features

### Example Migration
```markdown
# Phase 1 (Current) - Natural Language Only
---
description: Review Azure costs
input: [subscription_id]
---

Analyze Azure costs for subscription ${input:subscription_id}.
Please check for overprovisioned VMs and unused storage accounts.

# Phase 2 (Future) - With MCP Tools
---  
description: Review Azure costs
mcp: [azure-cost-analyzer]
input: [subscription_id]
---

Use azure-cost-analyzer to examine subscription ${input:subscription_id}.
Focus on overprovisioned VMs and unused storage accounts.
```

## Success Metrics

### Technical Metrics
- [ ] MCP server installation success rate >95%
- [ ] Tool calling latency <2s additional overhead
- [ ] Zero breaking changes to Phase 1 prompts
- [ ] Support for 10+ common MCP servers

### User Experience Metrics
- [ ] Automatic dependency resolution works seamlessly
- [ ] Clear error messages for MCP failures
- [ ] Documentation covers all MCP integration scenarios
- [ ] 25+ prompt installations via GitHub Action (as per next-steps.md)

## Community Collaboration

### LLM Library Collaboration
- **Contact**: Simon Willison (@simonw)
- **Goal**: Native MCP plugin for LLM library
- **Timeline**: Reach out Week 6, collaborate Week 7-8
- **Benefit**: Standard MCP client for entire LLM ecosystem

### Codex CLI Integration
- **Contact**: OpenAI Codex team
- **Goal**: Validate and document MCP integration
- **Timeline**: Week 6-7 testing and documentation
- **Benefit**: Production-ready MCP support immediately

### MCP Community
- **Goal**: Contribute to MCP ecosystem standards
- **Timeline**: Ongoing throughout Phase 2
- **Benefit**: Ensure APM works with broader MCP ecosystem

## Risk Mitigation

### Risk 1: MCP Spec Changes
**Mitigation**: 
- Track MCP specification closely
- Build adapters to isolate APM from spec changes
- Maintain compatibility with multiple MCP versions

### Risk 2: Runtime Integration Delays
**Mitigation**:
- Parallel development on both LLM and Codex approaches
- Codex as fallback if LLM integration delays
- Graceful degradation to Phase 1 functionality

### Risk 3: Registry Availability
**Mitigation**:
- Support multiple registry sources
- Local/git-based fallback installation
- Clear documentation for self-hosted registries

## Getting Involved

### For Contributors
- **Research**: Help evaluate MCP libraries and tools
- **Testing**: Test MCP server installation and integration
- **Documentation**: Improve MCP-related documentation
- **Examples**: Create example MCP-enabled prompts

### For Early Adopters
- **Feedback**: Test demo registry integration
- **Requirements**: Share MCP server needs and use cases
- **Beta Testing**: Try MCP integration when available (Week 9-10)

---

**Note**: This is a living document updated throughout Phase 2 development. Check back for latest status and implementation details.
