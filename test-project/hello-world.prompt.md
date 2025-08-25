---
description: A hello world prompt demonstrating AWD with GitHub integration
mcp:
  - ghcr.io/github/github-mcp-server
input: [name]
---

# Hello World AWD Application

Welcome to AWD, ${input:name}! This demonstrates:
- ✅ Parameter substitution with ${input:name}
- ✅ MCP server integration with GitHub
- ✅ Reusable, shareable prompt applications

## Instructions

Please:
1. Use the **get_me** tool to display my key GitHub information (username, bio, public repos count)
2. Give ${input:name} an enthusiastic welcome to AI-native development
3. Share one interesting insight about their GitHub profile
4. Suggest their next step with AWD based on their GitHub activity

## Expected Output

A personalized greeting with GitHub profile insights and tailored AWD recommendations.
