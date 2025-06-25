# Workflows Guide

Workflows orchestrate multiple prompts using natural language to create complex, multi-step AI automation. Think of workflows as programs that coordinate AI assistants to accomplish business processes.

## What are Workflows?

A workflow is a natural language script stored in a `.workflow.md` file that:
- **Orchestrates prompts**: Chains multiple AI tasks together
- **Includes business logic**: Handles conditions, approvals, and error cases
- **Manages data flow**: Passes results between steps
- **Provides human oversight**: Includes approval gates and decision points

## Natural Language Architecture

AWD workflows use **LLM-executable documentation** - they read like human instructions but are structured enough for LLM execution.

## Workflow File Structure

```markdown
---
name: incident-response
description: Complete incident response procedure
author: SRE Team
version: 1.2.0
mcp:
  - monitoring-tools
  - slack-api
  - ticket-system
input:
  - incident_severity
  - affected_service
---

# Incident Response Workflow

This workflow guides you through our complete incident response procedure.

## Step 1: Initial Assessment
First, let's understand what's happening:
- [Analyze system metrics](./prompts/analyze-metrics.prompt.md) for ${input:affected_service}
- [Check service dependencies](./prompts/check-dependencies.prompt.md)
- Wait for analysis completion before proceeding

## Step 2: Severity Triage
Based on the analysis results:
- If impact is **CRITICAL**: escalate immediately and proceed to Step 3
- If impact is **HIGH**: notify on-call team and proceed to Step 3  
- If impact is **MEDIUM** or below: skip to Step 5 for standard resolution

## Step 3: Emergency Response (Critical/High Only)
When we have a significant incident:
- **Ask for approval**: "Analysis complete. Proceed with emergency response? (yes/no)"
- If approved: [Execute emergency runbook](./prompts/emergency-runbook.prompt.md)
- If denied: [Create incident ticket](./prompts/create-ticket.prompt.md) and notify team lead

## Step 4: Parallel Investigation
While emergency response runs, also start these investigations:
- [Analyze recent deployments](./prompts/analyze-deployments.prompt.md)
- [Check infrastructure changes](./prompts/check-infrastructure.prompt.md)
- [Review error patterns](./prompts/review-errors.prompt.md)

## Step 5: Resolution and Verification
Finally, let's verify everything is working:
- [Verify system health](./prompts/verify-health.prompt.md)
- [Update status page](./prompts/update-status.prompt.md)
- [Generate incident report](./prompts/generate-report.prompt.md)

## Cleanup
After resolution:
- [Schedule post-mortem](./prompts/schedule-postmortem.prompt.md)
- [Update runbooks](./prompts/update-runbooks.prompt.md) if needed
```

## Natural Language Conventions

### Execution Markers
Use markdown links to execute prompts:
```markdown
[Prompt Name](./prompts/filename.prompt.md)
```

### Conditional Logic
Use natural language conditionals:
```markdown
Based on the analysis results:
- If error rate > 5%: proceed with rollback
- If response time > 2s: scale up infrastructure  
- Otherwise: monitor for 15 minutes
```

### Human Gates
Include approval points with clear questions:
```markdown
**Ask for approval**: "Deploy to production? This will affect 1M+ users. (yes/no)"
```

### Synchronization
Control execution flow with natural language:
```markdown
- Wait for deployment completion before proceeding
- While health checks run, also start monitoring alerts
- After verification succeeds, then notify stakeholders
```

### Data Flow
Reference previous results naturally:
```markdown
Based on the performance analysis results:
Using the deployment status from Step 2:
Store the incident ID as ${incident_id} for later reference:
```

## Workflow Patterns

### Sequential Execution
```markdown
## Deployment Process
1. [Validate configuration](./prompts/validate-config.prompt.md)
2. [Run pre-deployment tests](./prompts/pre-tests.prompt.md)
3. [Deploy to staging](./prompts/deploy-staging.prompt.md)
4. [Verify staging health](./prompts/verify-staging.prompt.md)
5. [Deploy to production](./prompts/deploy-prod.prompt.md)
```

### Conditional Branching
```markdown
## Code Review Workflow
Based on the code analysis results:
- If **security issues found**: 
  - [Create security ticket](./prompts/security-ticket.prompt.md)
  - Request security team review
  - Block merge until resolved
- If **performance concerns detected**:
  - [Run performance benchmarks](./prompts/performance-test.prompt.md)
  - **Ask for approval**: "Performance impact detected. Proceed anyway? (yes/no)"
- Otherwise: approve for merge
```

### Error Handling
```markdown
## Deployment with Rollback
Try to deploy the new version:
- [Deploy new version](./prompts/deploy.prompt.md)
- [Verify deployment success](./prompts/verify-deploy.prompt.md)

If deployment fails or verification shows errors:
- **Ask for approval**: "Deployment issues detected. Rollback immediately? (yes/no)"
- If approved: [Execute rollback](./prompts/rollback.prompt.md)
- [Notify team of rollback](./prompts/notify-rollback.prompt.md)
```

### Loops and Retries
```markdown
## Monitoring Loop
Repeat the following until system is healthy (max 10 iterations):
1. [Check system status](./prompts/check-status.prompt.md)
2. If status is HEALTHY: exit loop
3. If status is DEGRADED: wait 30 seconds and continue
4. If status is CRITICAL: escalate and exit loop
```

## Complex Workflow Example

```markdown
---
name: zero-downtime-deployment
description: Deploy with automatic rollback and traffic management
author: Platform Team
input:
  - service_name
  - new_version
  - traffic_shift_percentage
---

# Zero-Downtime Deployment

Deploy ${input:service_name} version ${input:new_version} with zero downtime.

## Pre-Deployment Validation
Before we start, let's make sure we're ready:
- [Validate deployment config](./prompts/validate-config.prompt.md) for ${input:service_name}
- [Check cluster capacity](./prompts/check-capacity.prompt.md)
- [Verify rollback plan](./prompts/verify-rollback.prompt.md)

Based on the validation results:
- If any critical issues found: **STOP** and fix issues first
- If warnings only: **Ask for approval**: "Warnings detected. Continue deployment? (yes/no)"
- If all clear: proceed to deployment

## Canary Deployment
Let's start with a small traffic shift:
- [Deploy canary version](./prompts/deploy-canary.prompt.md) with ${input:new_version}
- [Shift traffic](./prompts/shift-traffic.prompt.md) to ${input:traffic_shift_percentage}% canary

## Monitoring Phase
Monitor the canary for 10 minutes:
- [Monitor error rates](./prompts/monitor-errors.prompt.md)
- [Check response times](./prompts/monitor-latency.prompt.md)  
- [Analyze user feedback](./prompts/analyze-feedback.prompt.md)

If any issues detected during monitoring:
- [Immediate rollback](./prompts/emergency-rollback.prompt.md)
- [Alert team](./prompts/alert-team.prompt.md) with issue details
- **STOP** deployment and investigate

## Full Deployment
If canary looks good, proceed with full deployment:
- **Ask for approval**: "Canary successful. Deploy to 100% traffic? (yes/no)"
- If approved: [Complete deployment](./prompts/complete-deploy.prompt.md)
- [Verify full deployment](./prompts/verify-full-deploy.prompt.md)

## Post-Deployment
After successful deployment:
- [Update monitoring dashboards](./prompts/update-dashboards.prompt.md)
- [Generate deployment report](./prompts/generate-report.prompt.md)
- [Schedule cleanup tasks](./prompts/schedule-cleanup.prompt.md)
```

## Running Workflows

Execute workflows with the AWD CLI:

```bash
# Run a workflow with parameters
awd workflow run incident-response --incident_severity=HIGH --affected_service=api-gateway

# Interactive parameter input
awd workflow run zero-downtime-deployment

# Dry run to see execution plan
awd workflow plan incident-response --affected_service=billing-api

# Resume from specific step
awd workflow resume incident-response --from-step=3
```

## Best Practices

### 1. Clear Step Structure
Use numbered steps or clear headings to organize the workflow:

```markdown
## Step 1: Preparation
## Step 2: Execution  
## Step 3: Verification
## Step 4: Cleanup
```

### 2. Explicit Decision Points
Make conditionals clear and specific:

```markdown
# Good
Based on the error rate analysis:
- If error rate > 5%: execute emergency rollback
- If error rate 1-5%: reduce traffic and monitor
- If error rate < 1%: continue deployment

# Avoid
If there are problems, do something about it
```

### 3. Human Oversight
Include approval gates for critical operations:

```markdown
**Ask for approval**: "This will delete production data. Are you sure? Type 'CONFIRM' to proceed."
```

### 4. Progress Indicators
Help users understand where they are:

```markdown
## Step 2 of 5: Database Migration
We're now migrating the database schema...
```

### 5. Error Recovery
Provide clear paths for when things go wrong:

```markdown
If the migration fails:
1. [Restore database backup](./prompts/restore-backup.prompt.md)
2. [Rollback application version](./prompts/rollback-app.prompt.md)
3. [Notify engineering team](./prompts/notify-team.prompt.md)
4. **STOP** and investigate before retrying
```
