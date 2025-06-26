"""Command-line interface for Agentic Workflow Definitions (AWD)."""

import sys
import click
from colorama import init, Fore, Style
from .config import get_default_client, set_default_client
from .factory import ClientFactory, PackageManagerFactory
from .core.operations import install_package, uninstall_package
from .registry.integration import RegistryIntegration

# Initialize colorama
init(autoreset=True)

# CLI styling constants
TITLE = f"{Fore.CYAN}{Style.BRIGHT}"
SUCCESS = f"{Fore.GREEN}{Style.BRIGHT}"
ERROR = f"{Fore.RED}{Style.BRIGHT}"
INFO = f"{Fore.BLUE}"
WARNING = f"{Fore.YELLOW}"
HIGHLIGHT = f"{Fore.MAGENTA}{Style.BRIGHT}"
RESET = Style.RESET_ALL

def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"{TITLE}Agentic Workflow Definitions (AWD) CLI{RESET} version 0.1.0")
    ctx.exit()

@click.group(help=f"{TITLE}Agentic Workflow Definitions (AWD){RESET}: " 
             f"Turn complex DevOps tasks into reusable, AI-powered automation")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version and exit.")
@click.option('--client', '-c', help="Target MCP client (vscode, cursor, claude)")
@click.pass_context
def cli(ctx, client):
    """Main entry point for the AWD CLI."""
    # Store the client in the context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj['client'] = client if client else get_default_client()
    

# Workflow command group
@cli.group(help="Manage agentic workflows")
@click.pass_context
def workflow(ctx):
    """Workflow management commands."""
    pass


@workflow.command(name="list", help="List all available workflows")
@click.pass_context
def list_workflows(ctx):
    """List all available workflows."""
    from .workflow.discovery import discover_workflows
    
    click.echo(f"{INFO}Available workflows:{RESET}")
    
    try:
        workflows = discover_workflows()
        
        if not workflows:
            click.echo(f"{WARNING}No workflows found.{RESET}")
            return
            
        for wf in workflows:
            click.echo(f"  - {HIGHLIGHT}{wf.name}{RESET}: {wf.description}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing workflows: {e}{RESET}", err=True)
        sys.exit(1)


@workflow.command(name="create", help="Create a new workflow template (DEPRECATED: use 'awd create workflow' instead)")
@click.option('--name', required=True, help="Name of the workflow to create")
@click.pass_context
def create_workflow(ctx, name):
    """Create a new workflow template. (DEPRECATED)"""
    click.echo(f"{WARNING}DEPRECATED: Use 'awd create workflow {name}' instead{RESET}")
    
    from .workflow.discovery import create_workflow_template
    
    file_format = "VSCode .github/prompts format"
    click.echo(f"{SUCCESS}Creating new workflow template: {HIGHLIGHT}{name}{RESET} ({file_format})")
    
    try:
        file_path = create_workflow_template(name, use_vscode_convention=True)
        click.echo(f"{INFO}Workflow template created at: {file_path}{RESET}")
        click.echo(f"{SUCCESS}Workflow template created successfully!{RESET}")
        click.echo(f"{INFO}💡 Tip: This follows VSCode's .github/prompts convention for better integration.{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error creating workflow template: {e}{RESET}", err=True)
        sys.exit(1)


@workflow.command(name="run", help="Run a workflow with parameters")
@click.argument('workflow_name')
@click.option('--param', '-p', multiple=True, help="Parameter in the format name=value")
@click.pass_context
def run_workflow(ctx, workflow_name, param):
    """Run a workflow."""
    from .workflow.runner import run_workflow as execute_workflow
    
    click.echo(f"{INFO}Running workflow: {HIGHLIGHT}{workflow_name}{RESET}")
    
    # Parse parameters
    params = {}
    for p in param:
        if '=' in p:
            name, value = p.split('=', 1)
            params[name] = value
            click.echo(f"  - {name}: {value}")
    
    try:
        success, result = execute_workflow(workflow_name, params)
        
        if not success:
            click.echo(f"{ERROR}{result}{RESET}", err=True)
            sys.exit(1)
            
        click.echo(f"\n{INFO}Workflow output:{RESET}")
        click.echo(result)
        click.echo(f"\n{SUCCESS}Workflow executed successfully!{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error executing workflow: {e}{RESET}", err=True)
        sys.exit(1)


@workflow.command(name="mcp-sync", help="Update awd.yml with workflow dependencies")
@click.option('--output', default="awd.yml", help="Output file name")
@click.pass_context
def mcp_sync(ctx, output):
    """Sync MCP dependencies from workflows to awd.yml."""
    click.echo(f"{INFO}Syncing workflow MCP dependencies to {output}...{RESET}")
    
    try:
        from .deps.aggregator import sync_workflow_dependencies
        
        success, servers = sync_workflow_dependencies(output)
        
        if success:
            if servers:
                click.echo(f"{INFO}Found {len(servers)} MCP dependencies across workflows:{RESET}")
                for server in servers:
                    click.echo(f"  - {server}")
                click.echo(f"{SUCCESS}MCP dependencies synced successfully to {output}!{RESET}")
            else:
                click.echo(f"{WARNING}No MCP dependencies found in workflows.{RESET}")
                click.echo(f"{SUCCESS}Empty {output} file created!{RESET}")
        else:
            click.echo(f"{ERROR}Failed to sync MCP dependencies.{RESET}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{ERROR}Error syncing MCP dependencies: {e}{RESET}", err=True)
        sys.exit(1)


# MCP command group
@cli.group(help="Manage MCP servers")
@click.pass_context
def mcp(ctx):
    """MCP server management commands."""
    pass


@mcp.command(name="list", help="List installed MCP servers")
@click.pass_context
def list_mcp(ctx):
    """List installed MCP servers."""
    click.echo(f"{INFO}Installed MCP servers:{RESET}")
    
    # Get the client type from context
    client_type = ctx.obj['client']
    
    try:
        package_manager = PackageManagerFactory.create_package_manager()
        packages = package_manager.list_installed()
        
        if not packages:
            click.echo(f"{WARNING}No MCP servers installed.{RESET}")
            return
            
        for pkg in packages:
            click.echo(f"  - {pkg}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing MCP servers: {e}{RESET}", err=True)
        sys.exit(1)


@mcp.command(name="install", help="Install MCP servers")
@click.argument('package', required=False)
@click.option('--version', help="Package version to install")
@click.option('--file', default="awd.yml", help="Configuration file to install from")
@click.pass_context
def install_mcp(ctx, package, version, file):
    """Install MCP servers."""
    client_type = ctx.obj['client']
    
    try:
        if package:
            # Install a specific package
            click.echo(f"{INFO}Installing MCP server: {HIGHLIGHT}{package}{RESET}")
            if version:
                click.echo(f"  Version: {version}")
                
            result = install_package(client_type, package, version)
            if result:
                click.echo(f"{SUCCESS}MCP server installed successfully!{RESET}")
            else:
                click.echo(f"{ERROR}Failed to install MCP server.{RESET}", err=True)
                sys.exit(1)
        else:
            # Install from awd.yml
            click.echo(f"{INFO}Installing MCP servers from {file}...{RESET}")
            
            from .deps.verifier import verify_dependencies, install_missing_dependencies
            
            # First verify what's missing
            all_installed, installed, missing = verify_dependencies(file)
            
            if not installed and not missing:
                click.echo(f"{WARNING}No MCP servers defined in {file} or file not found.{RESET}")
                sys.exit(0)
                
            if all_installed:
                click.echo(f"{SUCCESS}All MCP servers already installed!{RESET}")
                sys.exit(0)
                
            # Confirm installation with user
            if missing:
                click.echo(f"{INFO}The following MCP servers will be installed:{RESET}")
                for server in missing:
                    click.echo(f"  - {server}")
                    
                if not click.confirm(f"{INFO}Do you want to continue?{RESET}"):
                    click.echo(f"{INFO}Installation cancelled.{RESET}")
                    sys.exit(0)
                
                # Install missing dependencies
                success, installed = install_missing_dependencies(file, client_type)
                
                if success:
                    click.echo(f"{SUCCESS}All required MCP servers installed successfully!{RESET}")
                else:
                    click.echo(f"{WARNING}Some MCP servers could not be installed.{RESET}")
                    sys.exit(1)
            
    except Exception as e:
        click.echo(f"{ERROR}Error installing MCP server: {e}{RESET}", err=True)
        sys.exit(1)


@mcp.command(name="uninstall", help="Uninstall an MCP server")
@click.argument('package')
@click.pass_context
def uninstall_mcp(ctx, package):
    """Uninstall an MCP server."""
    client_type = ctx.obj['client']
    
    try:
        click.echo(f"{INFO}Uninstalling MCP server: {HIGHLIGHT}{package}{RESET}")
        result = uninstall_package(client_type, package)
        
        if result:
            click.echo(f"{SUCCESS}MCP server uninstalled successfully!{RESET}")
        else:
            click.echo(f"{ERROR}Failed to uninstall MCP server.{RESET}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{ERROR}Error uninstalling MCP server: {e}{RESET}", err=True)
        sys.exit(1)


@mcp.command(name="search", help="Search for MCP servers")
@click.argument('query')
@click.pass_context
def search_mcp(ctx, query):
    """Search for MCP servers."""
    try:
        click.echo(f"{INFO}Searching for MCP servers: {HIGHLIGHT}{query}{RESET}")
        
        package_manager = PackageManagerFactory.create_package_manager()
        results = package_manager.search(query)
        
        if not results:
            click.echo(f"{WARNING}No matching MCP servers found.{RESET}")
            return
            
        click.echo(f"{INFO}Found {len(results)} matching MCP servers:{RESET}")
        for result in results:
            click.echo(f"  - {result}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error searching for MCP servers: {e}{RESET}", err=True)
        sys.exit(1)


@mcp.command(name="verify", help="Verify servers in awd.yml are installed")
@click.option('--file', default="awd.yml", help="Configuration file to verify")
@click.pass_context
def verify_mcp(ctx, file):
    """Verify MCP servers in awd.yml are installed."""
    click.echo(f"{INFO}Verifying MCP servers in {file}...{RESET}")
    
    try:
        from .deps.verifier import verify_dependencies
        
        all_installed, installed, missing = verify_dependencies(file)
        
        if not installed and not missing:
            click.echo(f"{WARNING}No MCP servers defined in {file} or file not found.{RESET}")
            sys.exit(0)
            
        if installed:
            click.echo(f"{INFO}Installed MCP servers ({len(installed)}):{RESET}")
            for server in installed:
                click.echo(f"  - {server}")
                
        if missing:
            click.echo(f"{WARNING}Missing MCP servers ({len(missing)}):{RESET}")
            for server in missing:
                click.echo(f"  - {server}")
            click.echo(f"{INFO}Run 'awd mcp install' to install missing servers.{RESET}")
            sys.exit(1)
        else:
            click.echo(f"{SUCCESS}All required MCP servers are installed!{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error verifying MCP servers: {e}{RESET}", err=True)
        sys.exit(1)


@mcp.command(name="init", help="Create awd.yml from installed servers")
@click.option('--output', default="awd.yml", help="Output file name")
@click.pass_context
def init_mcp(ctx, output):
    """Create awd.yml from installed servers."""
    click.echo(f"{INFO}Creating {output} from installed MCP servers...{RESET}")
    
    try:
        package_manager = PackageManagerFactory.create_package_manager()
        installed = package_manager.list_installed()
        
        if not installed:
            click.echo(f"{WARNING}No MCP servers installed.{RESET}")
            return
        
        # Create the configuration
        config = {
            'version': '1.0',
            'servers': installed
        }
        
        # Write to file
        with open(output, 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
            
        click.echo(f"{SUCCESS}{output} created successfully!{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error creating {output}: {e}{RESET}", err=True)
        sys.exit(1)


# MCP Registry command group
@mcp.group(help="Manage MCP registry operations")
@click.pass_context
def registry(ctx):
    """MCP registry management commands."""
    pass


@registry.command(name="list", help="List available packages in the registry")
@click.pass_context
def list_registry(ctx):
    """List available packages in the registry."""
    click.echo(f"{INFO}Available MCP servers in registry:{RESET}")
    
    try:
        registry_integration = RegistryIntegration()
        packages = registry_integration.list_available_packages()
        
        if not packages:
            click.echo(f"{WARNING}No packages found in registry.{RESET}")
            return
            
        for pkg in packages:
            name = pkg.get("name", "Unknown")
            description = pkg.get("description", "No description available")
            server_id = pkg.get("id", "")
            click.echo(f"  - {HIGHLIGHT}{name}{RESET} (ID: {server_id})")
            click.echo(f"    {description}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing registry packages: {e}{RESET}", err=True)
        sys.exit(1)


@registry.command(name="search", help="Search the registry for packages")
@click.argument('query')
@click.pass_context
def search_registry(ctx, query):
    """Search the registry for packages."""
    click.echo(f"{INFO}Searching registry for: {HIGHLIGHT}{query}{RESET}")
    
    try:
        registry_integration = RegistryIntegration()
        results = registry_integration.search_packages(query)
        
        if not results:
            click.echo(f"{WARNING}No matching packages found in registry.{RESET}")
            return
            
        click.echo(f"{INFO}Found {len(results)} matching packages:{RESET}")
        for pkg in results:
            name = pkg.get("name", "Unknown")
            description = pkg.get("description", "No description available")
            server_id = pkg.get("id", "")
            click.echo(f"  - {HIGHLIGHT}{name}{RESET} (ID: {server_id})")
            click.echo(f"    {description}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error searching registry: {e}{RESET}", err=True)
        sys.exit(1)


@registry.command(name="info", help="Get details about a specific package")
@click.argument('package')
@click.pass_context
def package_info(ctx, package):
    """Get detailed information about a specific package."""
    click.echo(f"{INFO}Package details for: {HIGHLIGHT}{package}{RESET}")
    
    try:
        registry_integration = RegistryIntegration()
        pkg_info = registry_integration.get_package_info(package)
        
        # Display basic package information
        click.echo(f"  Name: {HIGHLIGHT}{pkg_info.get('name')}{RESET}")
        click.echo(f"  Description: {pkg_info.get('description', 'No description available')}")
        
        # Display repository information if available
        if "repository" in pkg_info:
            repo = pkg_info["repository"]
            click.echo(f"  Repository: {repo.get('url', 'Unknown')}")
            if "source" in repo:
                click.echo(f"  Source: {repo.get('source')}")
        
        # Display version information
        if "version_detail" in pkg_info:
            version_detail = pkg_info["version_detail"]
            click.echo(f"  Version: {version_detail.get('version', 'Unknown')}")
            if "release_date" in version_detail:
                click.echo(f"  Release Date: {version_detail.get('release_date')}")
            if "is_latest" in version_detail:
                is_latest = "Yes" if version_detail.get("is_latest") else "No"
                click.echo(f"  Latest: {is_latest}")
        
        # Display available packages
        if "packages" in pkg_info:
            packages = pkg_info["packages"]
            if packages:
                click.echo(f"  Available packages:")
                for package in packages:
                    registry = package.get("registry_name", "Unknown")
                    name = package.get("name", "Unknown")
                    version = package.get("version", "Unknown")
                    runtime = package.get("runtime_hint", "")
                    
                    pkg_display = f"    - {name} (v{version}, {registry}"
                    if runtime:
                        pkg_display += f", runtime: {runtime}"
                    pkg_display += ")"
                    
                    click.echo(pkg_display)
                    
                    # Display runtime arguments if available
                    if "runtime_arguments" in package and package["runtime_arguments"]:
                        click.echo(f"      Runtime arguments:")
                        for arg in package["runtime_arguments"]:
                            required = "[Required]" if arg.get("is_required", False) else "[Optional]"
                            arg_name = arg.get("value", "")
                            arg_desc = f"({arg.get('type', '')})"
                            click.echo(f"        {required} {arg_name} {arg_desc}")
                    
                    # Display package arguments if available
                    if "package_arguments" in package and package["package_arguments"]:
                        click.echo(f"      Package arguments:")
                        for arg in package["package_arguments"]:
                            required = "[Required]" if arg.get("is_required", False) else "[Optional]"
                            arg_name = arg.get("value", "")
                            arg_desc = f"({arg.get('description', '')})"
                            click.echo(f"        {required} {arg_name} {arg_desc}")
        else:
            # Fall back to displaying versions (backward compatibility)
            versions = pkg_info.get("versions", [])
            if versions:
                click.echo(f"  Available versions:")
                for version in versions:
                    version_str = version.get("version", "Unknown")
                    click.echo(f"    - {version_str}")
            else:
                click.echo(f"  {WARNING}No versions available{RESET}")
            
    except ValueError as e:
        click.echo(f"{WARNING}{e}{RESET}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{ERROR}Error getting package info: {e}{RESET}", err=True)
        sys.exit(1)


# Config command
@cli.command(help="Configure AWD CLI")
@click.option('--set-client', help="Set the default MCP client")
@click.option('--show', is_flag=True, help="Show current configuration")
@click.pass_context
def config(ctx, set_client, show):
    """Configure AWD CLI."""
    if set_client:
        set_default_client(set_client)
        click.echo(f"{SUCCESS}Default client set to {HIGHLIGHT}{set_client}{RESET}")
    elif show:
        current_client = get_default_client()
        click.echo(f"{INFO}Current configuration:{RESET}")
        click.echo(f"  Default client: {HIGHLIGHT}{current_client}{RESET}")
    else:
        # Show help if no options provided
        click.echo(ctx.get_help())


# Create command group
@cli.group(help="Create new prompts or workflows")
@click.pass_context
def create(ctx):
    """Create management commands."""
    pass


@create.command(name="prompt", help="Create a new prompt template")
@click.argument('name')
@click.option('--description', '-d', help="Description for the prompt")
@click.pass_context
def create_prompt(ctx, name, description):
    """Create a new prompt template."""
    # TODO: Import prompt creation functionality when implemented
    # For now, provide a placeholder implementation
    click.echo(f"{SUCCESS}Creating new prompt: {HIGHLIGHT}{name}{RESET}")
    
    try:
        # Create a basic .prompt.md template
        import os
        from pathlib import Path
        
        # Ensure prompts directory exists
        prompts_dir = Path("prompts")
        prompts_dir.mkdir(exist_ok=True)
        
        filename = f"{name}.prompt.md"
        filepath = prompts_dir / filename
        
        # Basic prompt template
        template_content = f"""---
description: {description or f"AI prompt for {name}"}
mcp: []
input: []
---

# {name.replace('-', ' ').title()}

[Add your prompt instructions here]

## Instructions

1. [Step 1]
2. [Step 2] 
3. [Step 3]

## Expected Output

[Describe the expected output format]
"""
        
        with open(filepath, 'w') as f:
            f.write(template_content)
            
        click.echo(f"{INFO}Prompt template created at: {filepath}{RESET}")
        click.echo(f"{SUCCESS}Prompt template created successfully!{RESET}")
        click.echo(f"{INFO}💡 Tip: Edit the file to add your specific prompt instructions.{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error creating prompt template: {e}{RESET}", err=True)
        sys.exit(1)


@create.command(name="workflow", help="Create a new workflow template")
@click.argument('name')
@click.option('--description', '-d', help="Description for the workflow")
@click.pass_context
def create_workflow_new(ctx, name, description):
    """Create a new workflow template."""
    from .workflow.discovery import create_workflow_template
    
    file_format = "VSCode .github/prompts format"
    click.echo(f"{SUCCESS}Creating new workflow: {HIGHLIGHT}{name}{RESET} ({file_format})")
    
    try:
        file_path = create_workflow_template(name, description=description, use_vscode_convention=True)
        click.echo(f"{INFO}Workflow template created at: {file_path}{RESET}")
        click.echo(f"{SUCCESS}Workflow template created successfully!{RESET}")
        click.echo(f"{INFO}💡 Tip: This follows VSCode's .github/prompts convention for better integration.{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error creating workflow template: {e}{RESET}", err=True)
        sys.exit(1)


# Universal commands that work with both prompts and workflows
@cli.command(help="List all available prompts and workflows")
@click.pass_context
def list(ctx):
    """List all available prompts and workflows."""
    from .workflow.discovery import discover_workflows
    
    click.echo(f"{INFO}Available prompts and workflows:{RESET}")
    
    try:
        workflows = discover_workflows()
        
        if not workflows:
            click.echo(f"{WARNING}No prompts or workflows found.{RESET}")
            click.echo(f"{INFO}💡 Create your first prompt: awd create prompt my-prompt{RESET}")
            click.echo(f"{INFO}💡 Create your first workflow: awd create workflow my-workflow{RESET}")
            return
            
        for wf in workflows:
            # Determine type based on file extension or content
            file_type = "prompt" if ".prompt.md" in getattr(wf, 'file_path', '') else "workflow"
            click.echo(f"  - {HIGHLIGHT}{wf.name}{RESET} ({file_type}): {wf.description}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing prompts and workflows: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="Run a prompt or workflow with parameters")
@click.argument('name')
@click.option('--param', '-p', multiple=True, help="Parameter in the format name=value")
@click.option('--runtime', help="Runtime to use (llm, codex)")
@click.option('--llm', help="LLM model to use (fallback if not specified in frontmatter)")
@click.pass_context
def run(ctx, name, param, runtime, llm):
    """Run a prompt or workflow."""
    from .workflow.runner import run_workflow as execute_workflow
    
    click.echo(f"{INFO}Running {HIGHLIGHT}{name}{RESET}")
    
    # Parse parameters
    params = {}
    for p in param:
        if '=' in p:
            param_name, value = p.split('=', 1)
            params[param_name] = value
            click.echo(f"  - {param_name}: {value}")
    
    # Add runtime and llm to params if specified
    if runtime:
        params['_runtime'] = runtime
    if llm:
        params['_llm'] = llm
    
    try:
        success, result = execute_workflow(name, params)
        
        if not success:
            click.echo(f"{ERROR}{result}{RESET}", err=True)
            sys.exit(1)
            
        click.echo(f"\n{SUCCESS}Executed successfully!{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error executing {name}: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="Preview a prompt or workflow with parameters substituted (without execution)")
@click.argument('name')
@click.option('--param', '-p', multiple=True, help="Parameter in the format name=value")
@click.pass_context
def preview(ctx, name, param):
    """Preview a prompt or workflow with parameters substituted."""
    from .workflow.runner import preview_workflow
    
    click.echo(f"{INFO}Previewing {HIGHLIGHT}{name}{RESET}")
    
    # Parse parameters
    params = {}
    for p in param:
        if '=' in p:
            param_name, value = p.split('=', 1)
            params[param_name] = value
            click.echo(f"  - {param_name}: {value}")
    
    try:
        # Get the processed content without runtime execution
        success, result = preview_workflow(name, params)
        
        if not success:
            click.echo(f"{ERROR}{result}{RESET}", err=True)
            sys.exit(1)
        
        click.echo(f"\n{INFO}Processed Content:{RESET}")
        click.echo("-" * 50)
        click.echo(result)
        click.echo("-" * 50)
        click.echo(f"{SUCCESS}Preview complete! Use 'awd run {name}' to execute.{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error previewing {name}: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="List available LLM runtime models")
@click.pass_context
def models(ctx):
    """List available LLM runtime models."""
    try:
        from .runtime.llm_runtime import LLMRuntime
        
        click.echo(f"{TITLE}Available LLM Runtime Models:{RESET}")
        
        # Try to get a runtime instance to list models
        try:
            runtime = LLMRuntime()
            models = runtime.list_available_models()
            
            if "error" in models:
                click.echo(f"{ERROR}{models['error']}{RESET}")
                return
                
            if not models:
                click.echo(f"{WARNING}No models available. Install llm plugins first.{RESET}")
                click.echo(f"{INFO}Example: pip install llm-ollama{RESET}")
                return
                
            # Group by provider if possible
            providers = {}
            for model_id, info in models.items():
                provider = info.get('provider', 'unknown')
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(model_id)
            
            for provider, model_list in providers.items():
                click.echo(f"\n{HIGHLIGHT}{provider.title()}:{RESET}")
                for model in sorted(model_list):
                    click.echo(f"  - {model}")
                    
        except Exception as e:
            click.echo(f"{ERROR}Error listing models: {e}{RESET}")
            click.echo(f"{INFO}Tip: Install LLM and configure API keys first{RESET}")
            click.echo(f"{INFO}Example: pip install llm && llm keys set openai{RESET}")
            
    except ImportError:
        click.echo(f"{ERROR}LLM runtime not available. Install with: pip install llm{RESET}")


# Runtime management group
@cli.group(help="Manage LLM runtimes")
@click.pass_context
def runtime(ctx):
    """Runtime management commands."""
    pass


@runtime.command(help="List available runtimes on the system")
@click.pass_context  
def list(ctx):
    """List all available runtimes."""
    try:
        from .runtime.factory import RuntimeFactory
        
        click.echo(f"{TITLE}Available Runtimes:{RESET}")
        
        available_runtimes = RuntimeFactory.get_available_runtimes()
        
        if not available_runtimes:
            click.echo(f"{WARNING}No runtimes available.{RESET}")
            click.echo(f"{INFO}Install at least one of:{RESET}")
            click.echo(f"  - Codex CLI: npm i -g @openai/codex@native")
            click.echo(f"  - LLM library: pip install llm")
            return
        
        for runtime_info in available_runtimes:
            name = runtime_info.get("name", "unknown")
            runtime_type = runtime_info.get("type", "unknown")
            version = runtime_info.get("version", "unknown")
            
            click.echo(f"\n{HIGHLIGHT}{name}:{RESET}")
            click.echo(f"  Type: {runtime_type}")
            if version != "unknown":
                click.echo(f"  Version: {version}")
            
            capabilities = runtime_info.get("capabilities", {})
            if capabilities:
                click.echo(f"  Capabilities:")
                for cap, value in capabilities.items():
                    click.echo(f"    - {cap}: {value}")
            
            if "error" in runtime_info:
                click.echo(f"  {WARNING}Warning: {runtime_info['error']}{RESET}")
                
    except Exception as e:
        click.echo(f"{ERROR}Error listing runtimes: {e}{RESET}")


@runtime.command(help="Show detailed information about a specific runtime")
@click.argument('name')
@click.pass_context
def info(ctx, name):
    """Show detailed information about a runtime."""
    try:
        from .runtime.factory import RuntimeFactory
        
        click.echo(f"{TITLE}Runtime Information: {HIGHLIGHT}{name}{RESET}")
        
        try:
            runtime = RuntimeFactory.get_runtime_by_name(name)
            runtime_info = runtime.get_runtime_info()
            
            # Display basic info
            click.echo(f"\n{HIGHLIGHT}Basic Information:{RESET}")
            for key, value in runtime_info.items():
                if key != "capabilities":
                    click.echo(f"  {key}: {value}")
            
            # Display capabilities
            capabilities = runtime_info.get("capabilities", {})
            if capabilities:
                click.echo(f"\n{HIGHLIGHT}Capabilities:{RESET}")
                for cap, value in capabilities.items():
                    click.echo(f"  {cap}: {value}")
            
            # Try to list models if available
            try:
                models = runtime.list_available_models()
                if models and "error" not in models:
                    click.echo(f"\n{HIGHLIGHT}Available Models:{RESET}")
                    for model_id, model_info in models.items():
                        click.echo(f"  - {model_id}")
                        if isinstance(model_info, dict) and "provider" in model_info:
                            click.echo(f"    Provider: {model_info['provider']}")
                            
            except Exception:
                # Don't fail the whole command if model listing fails
                pass
                
        except ValueError as e:
            click.echo(f"{ERROR}{str(e)}{RESET}")
            click.echo(f"\n{INFO}Available runtimes:{RESET}")
            available_runtimes = RuntimeFactory.get_available_runtimes()
            for runtime_info in available_runtimes:
                click.echo(f"  - {runtime_info.get('name', 'unknown')}")
                
    except Exception as e:
        click.echo(f"{ERROR}Error getting runtime info: {e}{RESET}")


@cli.command(help="List available LLM runtime models")
@click.pass_context
def models(ctx):
    """List available LLM runtime models."""
    try:
        from .runtime.llm_runtime import LLMRuntime
        
        click.echo(f"{TITLE}Available LLM Runtime Models:{RESET}")
        
        # Try to get a runtime instance to list models
        try:
            runtime = LLMRuntime()
            models = runtime.list_available_models()
            
            if "error" in models:
                click.echo(f"{ERROR}{models['error']}{RESET}")
                return
                
            if not models:
                click.echo(f"{WARNING}No models available. Install llm plugins first.{RESET}")
                click.echo(f"{INFO}Example: pip install llm-ollama{RESET}")
                return
                
            # Group by provider if possible
            providers = {}
            for model_id, info in models.items():
                provider = info.get('provider', 'unknown')
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(model_id)
            
            for provider, model_list in providers.items():
                click.echo(f"\n{HIGHLIGHT}{provider.title()}:{RESET}")
                for model in sorted(model_list):
                    click.echo(f"  - {model}")
                    
        except Exception as e:
            click.echo(f"{ERROR}Error listing models: {e}{RESET}")
            click.echo(f"{INFO}Tip: Install LLM and configure API keys first{RESET}")
            click.echo(f"{INFO}Example: pip install llm && llm keys set openai{RESET}")
            
    except ImportError:
        click.echo(f"{ERROR}LLM runtime not available. Install with: pip install llm{RESET}")


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"{ERROR}Error: {e}{RESET}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
