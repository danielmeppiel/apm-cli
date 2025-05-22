# Agentic Workflow Definitions (AWD)

> **Turn complex DevOps tasks into reusable, AI-powered automation** - AWD lets you define workflows once and run them with any AI agent, bridging the gap between rigid vendor tools and complex custom agents.

AWD allows you to define step-by-step procedures for AI agents to execute. These workflows are written in Markdown with YAML frontmatter (`.awd.md` files) and can be run by any target agent client.

- **Portable Agentic Workflows** - Author Agentic Workflows in plain Markdown and run them with any AI agent like GitHub Copilot, Cursor, Claude or ChatGPT
- **MCP Package Management** - Define your workflow's required MCP Servers and let AWD install them from an MCP Registry
- **Version control friendly** - Store and share workflows like code in your existing repositories

## Getting Started in 5 Minutes

```bash
# 1. Install AWD CLI
pip install awd-cli

# 2. Create your first workflow
awd workflow create --name hello-world

# 3. Run the workflow
awd workflow run hello-world
```

## Community & Contributing

AWD is an open-source project built for developers, by developers. We welcome contributions of all kinds!

- [Share your workflows](https://github.com/danielmeppiel/awd-cli/examples)
- [Read our contribution guide](CONTRIBUTING.md)

Star ⭐ this repo if you find it useful!

## Usage

### Creating and Managing Workflows

Create your first Agentic Workflow and start writing your Workflow Definition file.

```zsh
# Create a new workflow template
awd workflow create --name gh-repo-from-template               # Creates deploy-service.awd.md template
```

### Workflow Definitions

Workflows are defined in Markdown files with a `.awd.md` extension. Here's an example of `gh-repo-from-template.awd.md`:

```yaml 
---
description: Creates a new GitHub repository by picking the right Repository Template from a GitHub Org and sets up a CI workflow by also picking the right GitHub Actions template. 
author: Alice DevOps  
mcp:
  - ghcr.io/github/github-mcp-server
---

# Create a GitHub Repo from a Repo Template

1. Gather Requirements:
   - Review provided parameters (language: ${input:language}, framework: ${input:framework})
   - If any key parameters are missing, such as language or framework, ask the user for clarification

2. Find Repository Template:
   - Use get-repository-templates tool to find matching GitHub Repository templates
   - Filter by language, framework, architecture type if specified
   - Consider features (example: oauth2, material-ui) and compliance (example: soc2) if specified
   - Expand the search if you don't find matching templates at first, e.g. by removing filters - you must find a template. Do NEVER propose creating a repository without a template.
   - Review options and recommend best match to user

3. Create Repository:
   - Once user confirms template choice, proceed with repository creation using GitHub MCP Server tools
   - Once the repo is created, read the contents from the template repository and copy them to the new repository

4. Setup CI:
   - Use get-github-actions-templates tool to find in which Organizations we can look for approved GitHub Actions workflow templates
   - Once you find out where we can look for templates, ask the user to select the appropriate source Organization to look for those templates
   - Fetch the contents of the workflowsUrl of that organization - this is a folder containing all the approved CI GitHub Actions workflows
   - Recommend appropriate workflows based on project type
   - Ask the user to confirm the workflow template choice
   - Once the user confirms the template choice, create a workflow in the new repository by reading/fetching the template workflow contents and then pushing a new workflow file to the new repo created above. Use the GitHub MCP tools for this.

5. Final Steps:
   - Summarize all actions taken
   - Provide next steps (git clone command) and resources to the user
```

### Running Workflows

You can then ask AWD to "run" your workflow:

```zsh
# Run a workflow with parameters
awd workflow run deploy-service --service-name=payments-api --target-env=staging

# Run with interactive parameter input (prompted if missing)
awd workflow run incident-response
```

This will ensure all required MCP Servers are installed in the target client and then generate the final prompt output by replacing the input parameter placeholders. You will need to copy and paste this in your client - hoping for a direct integration soon!

### Workflow and MCP Integration

The AWD CLI intelligently manages the relationship between workflows and MCP servers:

1. **Automatic Dependency Management**:
   - When running a workflow, AWD checks if all required MCP servers (defined in the workflow's YAML frontmatter) are installed
   - If missing servers are detected, AWD automatically installs them before executing the workflow
   - This ensures workflows always have their required tools available

2. **mcp.yml Synchronization**:
   - AWD can update the `mcp.yml` file to include MCP servers required by workflows
   - This keeps your central dependency file in sync with actual workflow requirements

3. **Project-wide Management**:
   - The `mcp.yml` file serves as the central record of all MCP server dependencies across workflows
   - Use it for version pinning, documentation, and to ensure consistent environments across team members

This integration ensures that both individual workflows can declare their specific tool requirements while maintaining a central, manageable dependency manifest for the entire project.

### MCP Configuration Files

The `awd mcp` tool supports managing MCP servers using configuration files, similar to dependency management tools like pipenv. By default awd-cli points to [Azure Community MCP Registry](https://demo.registry.azure-mcp.net). You can set the `MCP_REGISTRY_URL` environment variable to use a different registry:

```zsh
export MCP_REGISTRY_URL=https://your-mcp-registry.example.com
awd mcp registry list
```

#### Creating a Configuration File

Create a `mcp.yml` file in your project root:

```yaml
version: "1.0"
servers:
  - "ghcr.io/github/github-mcp-server"
  - "..."
```

or create a configuration file from currently installed servers:

```bash
awd mcp init
```

#### Installing Servers from Configuration

To install all servers defined in the configuration file:

```bash
awd mcp install
```

### CLI Usage Reference

```zsh
# Workflow Management
awd workflow list                                     # List all available workflows
awd workflow create --name deploy-service             # Create a new workflow template

# Workflow Execution
awd workflow run deploy-service --service-name=auth-api --target-env=staging  # Run with parameters

# Workflow-MCP Integration
awd workflow mcp-sync                                # Update mcp.yml with workflow dependencies

# MCP Server Management
awd mcp list                                          # List all installed MCP servers
awd mcp install                                       # Install servers from mcp.yml
awd mcp install redis-mcp-server                      # Install server by name

# MCP Configuration Commands
awd mcp verify                                        # Verify servers in mcp.yml are installed
awd mcp init                                          # Create mcp.yml from installed client servers
```

## Development

```zsh
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests, lint and format
pytest
flake8 awd-cli tests
black awd-cli tests
```

## Stack
- Python 3.13+
- `click` for CLI
- `mcp` package with `FastMCP` for MCP server functionality
- `pytest`, `flake8`, `black` for development
- GitHub Actions for CI/CD
