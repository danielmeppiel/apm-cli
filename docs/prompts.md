# Prompts Guide

Prompts are the building blocks of AWD - focused, reusable AI instructions that accomplish specific tasks. Think of them as functions in traditional programming: they take inputs, perform a specific operation, and produce outputs.

## What are Prompts?

A prompt is a single-purpose AI instruction stored in a `.prompt.md` file. Prompts are:
- **Focused**: Each prompt does one thing well
- **Reusable**: Can be used across multiple workflows
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

Reference workflow inputs using the `${input:name}` syntax:

```markdown
## Analysis Target
- Service: ${input:service_name}
- Environment: ${input:environment}
- Start time: ${input:start_time}
```

## MCP Tool Integration

Prompts can use MCP servers for external capabilities:

```yaml
---
mcp:
  - kubernetes-mcp    # For cluster access
  - github-mcp         # For repository operations
  - slack-mcp # For team communication
---
```

AWD will resolve and install any missing MCP Server dependencies on your target MCP Client (your runtime). The MCP Client where you run the prompt will have access to these tools when executing the prompt.

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

Prompts can be executed independently for testing:

```bash
# Run a prompt directly
awd prompt run analyze-logs --service_name=api-gateway --time_window="1h"

# Test with mock data
awd prompt test analyze-logs --mock-inputs

# Validate prompt syntax
awd prompt validate ./prompts/analyze-logs.prompt.md
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
Keep prompts in version control alongside workflows. Use semantic versioning for breaking changes.

## Next Steps

- Learn about [Workflows](workflows.md) to orchestrate multiple prompts
