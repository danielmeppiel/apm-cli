"""Command-line interface for Agentic Workflow Definitions (AWD) v0.0.1."""

import sys
import os
import yaml
import click
from pathlib import Path
from colorama import init, Fore, Style

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


def _get_template_dir():
    """Get the path to the templates directory."""
    # Get the directory where this CLI module is located
    cli_dir = Path(__file__).parent
    # Go up to the src directory, then up to the repo root, then to templates
    template_dir = cli_dir.parent.parent / 'templates'
    return template_dir


def _load_template_file(template_name, filename, **variables):
    """Load a template file and substitute variables."""
    template_dir = _get_template_dir()
    template_path = template_dir / template_name / filename
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Simple template substitution using string replace
    for var_name, var_value in variables.items():
        content = content.replace(f'{{{{{var_name}}}}}', str(var_value))
    
    return content


def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"{TITLE}Agentic Workflow Definitions (AWD) CLI{RESET} version 0.0.1")
    ctx.exit()

@click.group(help=f"{TITLE}Agentic Workflow Definitions (AWD){RESET}: " 
             f"The NPM for AI-Native Development")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version and exit.")
@click.pass_context
def cli(ctx):
    """Main entry point for the AWD CLI."""
    ctx.ensure_object(dict)


@cli.command(help="Initialize a new AWD project")
@click.argument('project_name', required=False)
@click.pass_context
def init(ctx, project_name):
    """Initialize a new AWD project (like npm init)."""
    try:
        # Determine project directory
        if project_name:
            project_dir = Path(project_name)
            project_dir.mkdir(exist_ok=True)
            os.chdir(project_dir)
            click.echo(f"{INFO}Created project directory: {project_name}{RESET}")
        else:
            project_dir = Path.cwd()
            project_name = project_dir.name
            
        click.echo(f"{SUCCESS}Initializing AWD project: {HIGHLIGHT}{project_name}{RESET}")
        
        # Load templates and create files
        try:
            # Create awd.yml from template
            awd_yml_content = _load_template_file('hello-world', 'awd.yml', 
                                                  project_name=project_name)
            with open('awd.yml', 'w') as f:
                f.write(awd_yml_content)
            
            # Create hello-world.prompt.md from template
            prompt_content = _load_template_file('hello-world', 'hello-world.prompt.md')
            with open('hello-world.prompt.md', 'w') as f:
                f.write(prompt_content)
                
            # Create README.md from template
            readme_content = _load_template_file('hello-world', 'README.md',
                                                 project_name=project_name)
            with open('README.md', 'w') as f:
                f.write(readme_content)
                
        except FileNotFoundError as e:
            click.echo(f"{ERROR}Template not found: {e}{RESET}", err=True)
            click.echo(f"{WARNING}Falling back to built-in templates{RESET}")
            
            # Fallback to hardcoded content if templates are missing
            awd_yml_content = {
                'name': project_name,
                'version': '1.0.0',
                'description': f'A {project_name} AWD application',
                'author': 'Your Name',
                'entrypoint': 'hello-world.prompt.md',
                'dependencies': {
                    'mcp': ['ghcr.io/github/github-mcp-server']
                }
            }
            
            with open('awd.yml', 'w') as f:
                yaml.dump(awd_yml_content, f, default_flow_style=False, sort_keys=False)
                
            # Use minimal fallback content for other files
            with open('hello-world.prompt.md', 'w') as f:
                f.write("""---
description: A hello world prompt demonstrating AWD
input: [name]
---

# Hello World

Welcome to AWD, ${input:name}!
""")
                
            with open('README.md', 'w') as f:
                f.write(f"""# {project_name}

An AWD application created with 'awd init'.
""")
            
        click.echo(f"{INFO}Created files:{RESET}")
        click.echo(f"  - awd.yml")
        click.echo(f"  - hello-world.prompt.md")
        click.echo(f"  - README.md")
        click.echo(f"\n{SUCCESS}AWD project initialized successfully!{RESET}")
        click.echo(f"{INFO}Next steps:{RESET}")
        click.echo(f"  1. {HIGHLIGHT}awd install{RESET} - Install dependencies")
        click.echo(f"  2. {HIGHLIGHT}awd run --param name=\"Your Name\"{RESET} - Run the hello world prompt")
        
    except Exception as e:
        click.echo(f"{ERROR}Error initializing project: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="Install MCP dependencies from awd.yml")
@click.pass_context
def install(ctx):
    """Install MCP dependencies from awd.yml (like npm install)."""
    try:
        # Check if awd.yml exists
        if not Path('awd.yml').exists():
            click.echo(f"{ERROR}No awd.yml found. Run 'awd init' first.{RESET}", err=True)
            sys.exit(1)
            
        click.echo(f"{INFO}Installing dependencies from awd.yml...{RESET}")
        
        # Read awd.yml
        with open('awd.yml', 'r') as f:
            config = yaml.safe_load(f)
            
        # Get MCP dependencies
        mcp_deps = config.get('dependencies', {}).get('mcp', [])
        
        if not mcp_deps:
            click.echo(f"{WARNING}No MCP dependencies found in awd.yml{RESET}")
            return
            
        click.echo(f"{INFO}Found {len(mcp_deps)} MCP dependencies:{RESET}")
        for dep in mcp_deps:
            click.echo(f"  - {dep}")
            
        # Import and use existing MCP installation functionality
        try:
            from .factory import PackageManagerFactory
            from .core.operations import install_package
            
            package_manager = PackageManagerFactory.create_package_manager()
            
            for dep in mcp_deps:
                click.echo(f"{INFO}Installing {dep}...{RESET}")
                try:
                    result = install_package('vscode', dep)  # Default to vscode client
                    if result and result.get('success'):
                        click.echo(f"{SUCCESS}✓ {dep} installed{RESET}")
                    else:
                        click.echo(f"{WARNING}⚠ {dep} installation may have issues{RESET}")
                except Exception as install_error:
                    click.echo(f"{WARNING}⚠ Failed to install {dep}: {install_error}{RESET}")
                    
        except ImportError:
            click.echo(f"{WARNING}MCP installation functionality not available yet{RESET}")
            click.echo(f"{INFO}Dependencies listed in awd.yml: {', '.join(mcp_deps)}{RESET}")
            
        click.echo(f"\n{SUCCESS}Dependencies installation complete!{RESET}")
        
    except Exception as e:
        click.echo(f"{ERROR}Error installing dependencies: {e}{RESET}", err=True)
        sys.exit(1)


def _load_awd_config():
    """Load configuration from awd.yml."""
    if Path('awd.yml').exists():
        with open('awd.yml', 'r') as f:
            return yaml.safe_load(f)
    return None


def _discover_prompts():
    """Discover all .prompt.md files in the current project."""
    prompts = []
    
    for prompt_file in Path('.').rglob('*.prompt.md'):
        # Read frontmatter to get description
        try:
            with open(prompt_file, 'r') as f:
                content = f.read()
                
            if content.startswith('---'):
                frontmatter_end = content.find('---', 3)
                if frontmatter_end != -1:
                    frontmatter = yaml.safe_load(content[3:frontmatter_end])
                    description = frontmatter.get('description', 'No description')
                else:
                    description = 'No description'
            else:
                description = 'No description'
                
            prompt_name = prompt_file.stem.replace('.prompt', '')
            prompts.append({
                'name': prompt_name,
                'description': description,
                'file_path': str(prompt_file)
            })
        except Exception:
            # Skip files that can't be parsed
            continue
            
    return prompts


def _get_entrypoint_prompt():
    """Get the entrypoint prompt from awd.yml."""
    config = _load_awd_config()
    if config and 'entrypoint' in config:
        return config['entrypoint'].replace('.prompt.md', '')
    return None


@cli.command(help="Run a prompt with parameters")
@click.argument('prompt_name', required=False)
@click.option('--param', '-p', multiple=True, help="Parameter in format name=value")
@click.option('--runtime', default='llm', help="Runtime to use (llm, codex)")
@click.option('--llm', help="LLM model to use (for llm runtime)")
@click.pass_context
def run(ctx, prompt_name, param, runtime, llm):
    """Run a prompt (uses entrypoint if no name specified)."""
    try:
        # If no prompt name specified, use entrypoint
        if not prompt_name:
            prompt_name = _get_entrypoint_prompt()
            if not prompt_name:
                click.echo(f"{ERROR}No prompt specified and no entrypoint defined in awd.yml{RESET}", err=True)
                click.echo(f"{INFO}Available prompts:{RESET}")
                prompts = _discover_prompts()
                for prompt in prompts:
                    click.echo(f"  - {HIGHLIGHT}{prompt['name']}{RESET}: {prompt['description']}")
                sys.exit(1)
                
        click.echo(f"{INFO}Running prompt: {HIGHLIGHT}{prompt_name}{RESET}")
        
        # Parse parameters
        params = {}
        for p in param:
            if '=' in p:
                param_name, value = p.split('=', 1)
                params[param_name] = value
                click.echo(f"  - {param_name}: {value}")
                
        # Import and use existing runtime functionality
        try:
            from .workflow.runner import run_workflow
            
            success, result = run_workflow(prompt_name, params, runtime=runtime, llm=llm)
            
            if not success:
                click.echo(f"{ERROR}{result}{RESET}", err=True)
                sys.exit(1)
                
            click.echo(f"\n{INFO}Prompt output:{RESET}")
            click.echo(result)
            click.echo(f"\n{SUCCESS}Prompt executed successfully!{RESET}")
            
        except ImportError:
            click.echo(f"{WARNING}Runtime functionality not available yet{RESET}")
            click.echo(f"{INFO}Would run: {prompt_name} with params {params}{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error running prompt: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="Preview a prompt with parameters substituted (without execution)")
@click.argument('prompt_name', required=False)
@click.option('--param', '-p', multiple=True, help="Parameter in format name=value")
@click.pass_context
def preview(ctx, prompt_name, param):
    """Preview a prompt with parameters substituted."""
    try:
        # If no prompt name specified, use entrypoint
        if not prompt_name:
            prompt_name = _get_entrypoint_prompt()
            if not prompt_name:
                click.echo(f"{ERROR}No prompt specified and no entrypoint defined in awd.yml{RESET}", err=True)
                sys.exit(1)
                
        click.echo(f"{INFO}Previewing prompt: {HIGHLIGHT}{prompt_name}{RESET}")
        
        # Parse parameters
        params = {}
        for p in param:
            if '=' in p:
                param_name, value = p.split('=', 1)
                params[param_name] = value
                click.echo(f"  - {param_name}: {value}")
                
        # Import and use existing preview functionality
        try:
            from .workflow.runner import preview_workflow
            
            success, result = preview_workflow(prompt_name, params)
            
            if not success:
                click.echo(f"{ERROR}{result}{RESET}", err=True)
                sys.exit(1)
                
            click.echo(f"\n{INFO}Processed Content:{RESET}")
            click.echo("-" * 50)
            click.echo(result)
            click.echo("-" * 50)
            click.echo(f"{SUCCESS}Preview complete! Use 'awd run {prompt_name}' to execute.{RESET}")
            
        except ImportError:
            click.echo(f"{WARNING}Preview functionality not available yet{RESET}")
            click.echo(f"{INFO}Would preview: {prompt_name} with params {params}{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error previewing prompt: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="List available prompts in the current project")
@click.pass_context
def list(ctx):
    """List all available prompts in the project."""
    try:
        click.echo(f"{INFO}Available prompts:{RESET}")
        
        prompts = _discover_prompts()
        
        if not prompts:
            click.echo(f"{WARNING}No prompts found.{RESET}")
            click.echo(f"{INFO}💡 Create your first project: awd init my-project{RESET}")
            return
            
        # Show entrypoint if defined
        entrypoint = _get_entrypoint_prompt()
        
        for prompt in prompts:
            prefix = "📍 " if prompt['name'] == entrypoint else "   "
            click.echo(f"{prefix}{HIGHLIGHT}{prompt['name']}{RESET}: {prompt['description']}")
            
        if entrypoint:
            click.echo(f"\n{INFO}📍 = entrypoint (default when running 'awd run'){RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing prompts: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="List available LLM models")
@click.pass_context
def models(ctx):
    """List available LLM runtime models."""
    try:
        click.echo(f"{TITLE}Available LLM Runtime Models:{RESET}")
        
        # Try to import and use existing functionality
        try:
            from .runtime.llm_runtime import LLMRuntime
            
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
                    
        except ImportError:
            click.echo(f"{WARNING}LLM runtime not available{RESET}")
            click.echo(f"{INFO}Install with: pip install llm{RESET}")
            click.echo(f"\n{INFO}Common models:{RESET}")
            click.echo(f"  - github/gpt-4o-mini (free with GitHub PAT)")
            click.echo(f"  - gpt-4o-mini (OpenAI)")
            click.echo(f"  - claude-3-haiku (Anthropic)")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing models: {e}{RESET}", err=True)


@cli.command(help="Configure AWD CLI")
@click.option('--show', is_flag=True, help="Show current configuration")
@click.pass_context
def config(ctx, show):
    """Configure AWD CLI settings."""
    try:
        if show:
            click.echo(f"{TITLE}Current AWD Configuration:{RESET}")
            
            # Show awd.yml if in project
            if Path('awd.yml').exists():
                config = _load_awd_config()
                click.echo(f"\n{HIGHLIGHT}Project (awd.yml):{RESET}")
                click.echo(f"  Name: {config.get('name', 'Unknown')}")
                click.echo(f"  Version: {config.get('version', 'Unknown')}")
                click.echo(f"  Entrypoint: {config.get('entrypoint', 'None')}")
                click.echo(f"  MCP Dependencies: {len(config.get('dependencies', {}).get('mcp', []))}")
            else:
                click.echo(f"{INFO}Not in an AWD project directory{RESET}")
                
            click.echo(f"\n{HIGHLIGHT}Global:{RESET}")
            click.echo(f"  AWD CLI Version: 0.0.1")
            
        else:
            click.echo(f"{INFO}Use --show to display configuration{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error showing configuration: {e}{RESET}", err=True)


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"{ERROR}Error: {e}{RESET}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
