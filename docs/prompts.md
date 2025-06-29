# Prompts Guide

Prompts are the building blocks of AWD - focused, reusable AI instructions that accomplish specific tasks. They are executed through scripts defined in your `awd.yml` configuration.

## How Prompts Work in AWD

AWD uses a script-based architecture:

1. **Scripts** are defined in `awd.yml` and specify which runtime and prompt to use
2. **Prompts** (`.prompt.md` files) contain the AI instructions with parameter placeholders
3. **Compilation** happens when scripts reference `.prompt.md` files - AWD compiles them with parameter substitution
4. **Execution** runs the compiled prompt through the specified runtime

```bash
# Script execution flow
awd run start --param key=value
  ↓
Script: "codex my-prompt.prompt.md"
  ↓
AWD compiles my-prompt.prompt.md with parameters
  ↓
Codex executes the compiled prompt
```

## What are Prompts?

A prompt is a single-purpose AI instruction stored in a `.prompt.md` file. Prompts are:
- **Focused**: Each prompt does one thing well
- **Reusable**: Can be used across multiple scripts
- **Parameterized**: Accept inputs to customize behavior
- **Testable**: Easy to run and validate independently

## Prompt File Structure

Prompts follow the VSCode `.prompt.md` convention with YAML frontmatter:

```markdown
---
description: Analyzes application logs to identify errors and patterns
author: DevOps Team
mcp:
  - logs-analyzer
input:
  - service_name
  - time_window
  - log_level
---

# Analyze Application Logs

You are a expert DevOps engineer analyzing application logs to identify issues and patterns.

## Context
- Service: ${input:service_name}
- Time window: ${input:time_window}
- Log level: ${input:log_level}

## Task
1. Retrieve logs for the specified service and time window
2. Identify any ERROR or FATAL level messages
3. Look for patterns in warnings that might indicate emerging issues
4. Summarize findings with:
   - Critical issues requiring immediate attention
   - Trends or patterns worth monitoring
   - Recommended next steps

## Output Format
Provide a structured summary with:
- **Status**: CRITICAL | WARNING | NORMAL
- **Issues Found**: List of specific problems
- **Patterns**: Recurring themes or trends
- **Recommendations**: Suggested actions
```

## Key Components

### YAML Frontmatter
- **description**: Clear explanation of what the prompt does
- **author**: Who created/maintains this prompt
- **mcp**: Required MCP servers for tool access
- **input**: Parameters the prompt expects

### Prompt Body
- **Clear instructions**: Tell the AI exactly what to do
- **Context section**: Provide relevant background information
- **Input references**: Use `${input:parameter_name}` for dynamic values
- **Output format**: Specify how results should be structured

## Input Parameters

Reference script inputs using the `${input:name}` syntax:

```markdown
## Analysis Target
- Service: ${input:service_name}
- Environment: ${input:environment}
- Start time: ${input:start_time}
```

## MCP Tool Integration (Phase 2 - Coming Soon)

> **⚠️ Note**: MCP integration is planned work. Currently, prompts work with natural language instructions only.

**Future capability** - Prompts will be able to use MCP servers for external tools:

```yaml
---
description: Future MCP-enabled prompt
mcp:
  - kubernetes-mcp    # For cluster access
  - github-mcp        # For repository operations  
  - slack-mcp         # For team communication
---
```

**Current workaround**: Use detailed natural language instructions:
```markdown
---
description: Current approach without MCP tools
---

# Kubernetes Analysis

Please analyze the Kubernetes cluster by:
1. Examining the deployment configurations I'll provide
2. Reviewing resource usage patterns
3. Suggesting optimization opportunities

[Include relevant data in the prompt or as context]
```

See [MCP Integration Status](wip/mcp-integration.md) for Phase 2 development plans.

## Writing Effective Prompts

### Be Specific
```markdown
# Good
Analyze the last 24 hours of application logs for service ${input:service_name}, 
focusing on ERROR and FATAL messages, and identify any patterns that might 
indicate performance degradation.

# Avoid
Look at some logs and tell me if there are problems.
```

### Structure Your Instructions
```markdown
## Task
1. First, do this specific thing
2. Then, analyze the results looking for X, Y, and Z
3. Finally, summarize findings in the specified format

## Success Criteria
- All ERROR messages are categorized
- Performance trends are identified
- Clear recommendations are provided
```

### Specify Output Format
```markdown
## Output Format
**Summary**: One-line status
**Critical Issues**: Numbered list of immediate concerns
**Recommendations**: Specific next steps with priority levels
```

## Example Prompts

### Code Review Prompt
```markdown
---
description: Reviews code changes for best practices and potential issues
author: Engineering Team
input:
  - pull_request_url
  - focus_areas
---

# Code Review Assistant

Review the code changes in pull request ${input:pull_request_url} with focus on ${input:focus_areas}.

## Review Criteria
1. **Security**: Check for potential vulnerabilities
2. **Performance**: Identify optimization opportunities  
3. **Maintainability**: Assess code clarity and structure
4. **Testing**: Evaluate test coverage and quality

## Output
Provide feedback in standard PR review format with:
- Specific line comments for issues
- Overall assessment score (1-10)
- Required changes vs suggestions
```

### Deployment Health Check
```markdown
---
description: Verifies deployment success and system health
author: Platform Team
mcp:
  - kubernetes-tools
  - monitoring-api
input:
  - service_name
  - deployment_version
---

# Deployment Health Check

Verify the successful deployment of ${input:service_name} version ${input:deployment_version}.

## Health Check Steps
1. Confirm pods are running and ready
2. Check service endpoints are responding
3. Verify metrics show normal operation
4. Test critical user flows

## Success Criteria
- All pods STATUS = Running
- Health endpoint returns 200
- Error rate < 1%
- Response time < 500ms
```

## Running Prompts

Prompts are executed through scripts defined in your `awd.yml`. When a script references a `.prompt.md` file, AWD compiles it with parameter substitution before execution:

```bash
# Run scripts that reference .prompt.md files
awd run start --param service_name=api-gateway --param time_window="1h"
awd run llm --param service_name=api-gateway --param time_window="1h"
awd run debug --param service_name=api-gateway --param time_window="1h"

# Preview compiled prompts before execution
awd preview start --param service_name=api-gateway --param time_window="1h"
```

**Script Configuration (awd.yml):**
```yaml
scripts:
  start: "codex analyze-logs.prompt.md"
  llm: "llm analyze-logs.prompt.md -m github/gpt-4o-mini"
  debug: "DEBUG=true codex analyze-logs.prompt.md"
```

### Example Project Structure

```
my-devops-project/
├── awd.yml                              # Project configuration
├── README.md                            # Project documentation
├── analyze-logs.prompt.md               # Main log analysis prompt
├── prompts/
│   ├── code-review.prompt.md           # Code review prompt
│   └── health-check.prompt.md          # Deployment health check
└── .github/
    └── workflows/
        └── awd-ci.yml                  # CI using AWD scripts
```

### Corresponding awd.yml

```yaml
name: my-devops-project
version: 1.0.0
description: DevOps automation prompts for log analysis and system monitoring
author: Platform Team

scripts:
  # Default script using Codex runtime
  start: "codex analyze-logs.prompt.md"
  
  # LLM script with GitHub Models
  llm: "llm analyze-logs.prompt.md -m github/gpt-4o-mini"
  
  # Debug script with environment variables
  debug: "DEBUG=true VERBOSE=true codex analyze-logs.prompt.md"
  
  # Code review script
  review: "codex prompts/code-review.prompt.md"
  
  # Health check script
  health: "llm prompts/health-check.prompt.md -m github/gpt-4o"

dependencies:
  mcp:
    - ghcr.io/github/github-mcp-server
    - ghcr.io/kubernetes/k8s-mcp-server
```

This structure allows you to run any prompt via scripts:
```bash
awd run start --param service_name=api-gateway --param time_window="1h"
awd run review --param pull_request_url=https://github.com/org/repo/pull/123
awd run health --param service_name=frontend --param deployment_version=v2.1.0
```

## Best Practices

### 1. Single Responsibility
Each prompt should do one thing well. Break complex operations into multiple prompts.

### 2. Clear Naming
Use descriptive names that indicate the prompt's purpose:
- `analyze-performance-metrics.prompt.md`
- `create-incident-ticket.prompt.md`
- `validate-deployment-config.prompt.md`

### 3. Document Inputs
Always specify what inputs are required and their expected format:

```yaml
input:
  - service_name     # String: name of the service to analyze
  - time_window      # String: time range (e.g., "1h", "24h", "7d")
  - severity_level   # String: minimum log level ("ERROR", "WARN", "INFO")
```

### 4. Version Control
Keep prompts in version control alongside scripts. Use semantic versioning for breaking changes.

## Next Steps

- Learn about [Runtime Integration](runtime-integration.md) to setup and use different AI runtimes
- See [CLI Reference](cli-reference.md) for complete script execution commands
- Check [Development Guide](development.md) for local development setup
