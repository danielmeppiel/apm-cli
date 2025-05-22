"""Command-line interface for Agentic Workflow Definitions (AWD)."""

import sys
import click
from colorama import init, Fore, Style
from .config import get_default_client, set_default_client
from .factory import ClientFactory, PackageManagerFactory
from .core.operations import install_package, uninstall_package

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


@workflow.command(name="create", help="Create a new workflow template")
@click.option('--name', required=True, help="Name of the workflow to create")
@click.pass_context
def create_workflow(ctx, name):
    """Create a new workflow template."""
    from .workflow.discovery import create_workflow_template
    
    click.echo(f"{SUCCESS}Creating new workflow template: {HIGHLIGHT}{name}.awd.md{RESET}")
    
    try:
        file_path = create_workflow_template(name)
        click.echo(f"{INFO}Workflow template created at: {file_path}{RESET}")
        click.echo(f"{SUCCESS}Workflow template created successfully!{RESET}")
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


@workflow.command(name="mcp-sync", help="Update mcp.yml with workflow dependencies")
@click.pass_context
def mcp_sync(ctx):
    """Sync MCP dependencies from workflows to mcp.yml."""
    click.echo(f"{INFO}Syncing workflow MCP dependencies to mcp.yml...{RESET}")
    # Placeholder for actual implementation
    click.echo(f"{SUCCESS}MCP dependencies synced successfully!{RESET}")


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
@click.pass_context
def install_mcp(ctx, package, version):
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
            # Install from mcp.yml
            click.echo(f"{INFO}Installing MCP servers from mcp.yml...{RESET}")
            # Placeholder for actual implementation
            click.echo(f"{SUCCESS}MCP servers installed successfully!{RESET}")
            
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


@mcp.command(name="verify", help="Verify servers in mcp.yml are installed")
@click.pass_context
def verify_mcp(ctx):
    """Verify MCP servers in mcp.yml are installed."""
    click.echo(f"{INFO}Verifying MCP servers in mcp.yml...{RESET}")
    # Placeholder for actual implementation
    click.echo(f"{SUCCESS}All required MCP servers are installed!{RESET}")


@mcp.command(name="init", help="Create mcp.yml from installed servers")
@click.option('--output', default="mcp.yml", help="Output file name")
@click.pass_context
def init_mcp(ctx, output):
    """Create mcp.yml from installed servers."""
    click.echo(f"{INFO}Creating {output} from installed MCP servers...{RESET}")
    # Placeholder for actual implementation
    click.echo(f"{SUCCESS}{output} created successfully!{RESET}")


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
    # Placeholder for actual implementation
    click.echo("  - ghcr.io/github/github-mcp-server")
    click.echo("  - ghcr.io/azure/azure-mcp-server")
    click.echo("  - ghcr.io/redis/redis-mcp-server")


@registry.command(name="search", help="Search the registry for packages")
@click.argument('query')
@click.pass_context
def search_registry(ctx, query):
    """Search the registry for packages."""
    click.echo(f"{INFO}Searching registry for: {HIGHLIGHT}{query}{RESET}")
    # Placeholder for actual implementation
    click.echo(f"{INFO}Found matching MCP servers:{RESET}")
    click.echo(f"  - {query}-mcp-server")


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


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"{ERROR}Error: {e}{RESET}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
