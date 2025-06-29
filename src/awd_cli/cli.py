"""Command-line interface for Agentic Workflow Definitions (AWD)."""

import sys
import os
import yaml
import click
from pathlib import Path
from colorama import init, Fore, Style

# Handle version import for both package and PyInstaller contexts
try:
    from .version import get_version
except ImportError:
    # Fallback for PyInstaller or direct execution
    try:
        from awd_cli.version import get_version
    except ImportError:
        # Last resort fallback
        def get_version():
            return "unknown"

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
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
        return Path(base_path) / 'templates'
    else:
        # Running in development
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
    click.echo(f"{TITLE}Agentic Workflow Definitions (AWD) CLI{RESET} version {get_version()}")
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
@click.option('--force', '-f', is_flag=True, help="Overwrite existing files without confirmation")
@click.option('--yes', '-y', is_flag=True, help="Skip interactive questionnaire and use defaults")
@click.pass_context
def init(ctx, project_name, force, yes):
    """Initialize a new AWD project (like npm init)."""
    try:
        # Handle explicit current directory
        if project_name == '.':
            project_name = None
            
        # Determine project directory and name
        if project_name:
            project_dir = Path(project_name)
            project_dir.mkdir(exist_ok=True)
            os.chdir(project_dir)
            click.echo(f"{INFO}Created project directory: {project_name}{RESET}")
            final_project_name = project_name
        else:
            project_dir = Path.cwd()
            final_project_name = project_dir.name
            
        # Check for existing AWD project
        awd_yml_exists = Path('awd.yml').exists()
        existing_files = []
        if awd_yml_exists:
            existing_files.append('awd.yml')
        if Path('hello-world.prompt.md').exists():
            existing_files.append('hello-world.prompt.md')
        if Path('README.md').exists():
            existing_files.append('README.md')
            
        # Handle existing project
        if existing_files and not force:
            click.echo(f"{WARNING}Existing AWD project detected:{RESET}")
            for file in existing_files:
                click.echo(f"  - {file}")
            click.echo()
            
            if not yes:
                if not click.confirm(f"Continue and overwrite existing files?"):
                    click.echo(f"{INFO}Initialization cancelled.{RESET}")
                    return
            else:
                click.echo(f"{INFO}--yes specified, continuing with overwrite...{RESET}")
        
        # Get project configuration (interactive mode or defaults)
        if not yes and not awd_yml_exists:
            config = _interactive_project_setup(final_project_name)
        else:
            # Use defaults or preserve existing config
            if awd_yml_exists and not force:
                config = _merge_existing_config(final_project_name)
            else:
                config = _get_default_config(final_project_name)
        
        click.echo(f"{SUCCESS}Initializing AWD project: {HIGHLIGHT}{config['name']}{RESET}")
        
        # Create files from config
        _create_project_files(config)
            
        click.echo(f"{INFO}Created files:{RESET}")
        click.echo(f"  - awd.yml")
        click.echo(f"  - hello-world.prompt.md")
        click.echo(f"  - README.md")
        click.echo(f"\n{SUCCESS}AWD project initialized successfully!{RESET}")
        click.echo(f"{INFO}Next steps:{RESET}")
        click.echo(f"  1. {HIGHLIGHT}awd install{RESET} - Install dependencies")
        click.echo(f"  2. {HIGHLIGHT}awd run start --param name=\"Your Name\"{RESET} - Run the start script")
        click.echo(f"  3. {HIGHLIGHT}awd list{RESET} - See all available scripts")
        
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
            try:
                from .factory import PackageManagerFactory
                from .core.operations import install_package
            except ImportError:
                from awd_cli.factory import PackageManagerFactory
                from awd_cli.core.operations import install_package
            
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


def _get_default_script():
    """Get the default script (start) from awd.yml scripts."""
    config = _load_awd_config()
    if config and 'scripts' in config and 'start' in config['scripts']:
        return 'start'
    return None


def _list_available_scripts():
    """List all available scripts from awd.yml."""
    config = _load_awd_config()
    if config and 'scripts' in config:
        return config['scripts']
    return {}


@cli.command(help="Run a script with parameters")
@click.argument('script_name', required=False)
@click.option('--param', '-p', multiple=True, help="Parameter in format name=value")
@click.pass_context
def run(ctx, script_name, param):
    """Run a script from awd.yml (uses 'start' script if no name specified)."""
    try:
        # If no script name specified, use 'start' script
        if not script_name:
            script_name = _get_default_script()
            if not script_name:
                click.echo(f"{ERROR}No script specified and no 'start' script defined in awd.yml{RESET}", err=True)
                click.echo(f"{INFO}Available scripts:{RESET}")
                scripts = _list_available_scripts()
                for name, command in scripts.items():
                    click.echo(f"  - {HIGHLIGHT}{name}{RESET}: {command}")
                sys.exit(1)
                
        click.echo(f"{INFO}Running script: {HIGHLIGHT}{script_name}{RESET}")
        
        # Parse parameters
        params = {}
        for p in param:
            if '=' in p:
                param_name, value = p.split('=', 1)
                params[param_name] = value
                click.echo(f"  - {param_name}: {value}")
                
        # Import and use script runner
        try:
            from awd_cli.core.script_runner import ScriptRunner
            
            script_runner = ScriptRunner()
            success = script_runner.run_script(script_name, params)
            
            if not success:
                click.echo(f"{ERROR}Script execution failed{RESET}", err=True)
                sys.exit(1)
                
            click.echo(f"\n{SUCCESS}Script executed successfully!{RESET}")
            
        except ImportError as ie:
            click.echo(f"{WARNING}Script runner not available yet{RESET}")
            click.echo(f"{INFO}Import error: {ie}{RESET}")
            click.echo(f"{INFO}Would run script: {script_name} with params {params}{RESET}")
        except Exception as ee:
            click.echo(f"{ERROR}Script execution error: {ee}{RESET}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{ERROR}Error running script: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="Preview a script's compiled prompt files")
@click.argument('script_name', required=False)
@click.option('--param', '-p', multiple=True, help="Parameter in format name=value")
@click.pass_context
def preview(ctx, script_name, param):
    """Preview compiled prompt files for a script."""
    try:
        # If no script name specified, use 'start' script
        if not script_name:
            script_name = _get_default_script()
            if not script_name:
                click.echo(f"{ERROR}No script specified and no 'start' script defined in awd.yml{RESET}", err=True)
                sys.exit(1)
                
        click.echo(f"{INFO}Previewing script: {HIGHLIGHT}{script_name}{RESET}")
        
        # Parse parameters
        params = {}
        for p in param:
            if '=' in p:
                param_name, value = p.split('=', 1)
                params[param_name] = value
                click.echo(f"  - {param_name}: {value}")
                
        # Import and use script runner for preview
        try:
            from awd_cli.core.script_runner import ScriptRunner
            
            script_runner = ScriptRunner()
            
            # Get the script command
            scripts = script_runner.list_scripts()
            if script_name not in scripts:
                click.echo(f"{ERROR}Script '{script_name}' not found{RESET}", err=True)
                sys.exit(1)
                
            command = scripts[script_name]
            click.echo(f"\n{INFO}Original command:{RESET}")
            click.echo(f"  {command}")
            
            # Auto-compile prompts to show what would be executed
            compiled_command = script_runner._auto_compile_prompts(command, params)
            click.echo(f"\n{INFO}Compiled command:{RESET}")
            click.echo(f"  {compiled_command}")
            
            # Show compiled files if any .prompt.md files were processed
            import re
            prompt_files = re.findall(r'(\S+\.prompt\.md)', command)
            if prompt_files:
                click.echo(f"\n{INFO}Compiled prompt files:{RESET}")
                for prompt_file in prompt_files:
                    output_name = Path(prompt_file).stem.replace('.prompt', '') + '.txt'
                    compiled_path = Path('.awd/compiled') / output_name
                    click.echo(f"  - {compiled_path}")
                    
            click.echo(f"\n{SUCCESS}Preview complete! Use 'awd run {script_name}' to execute.{RESET}")
            
        except ImportError:
            click.echo(f"{WARNING}Script runner not available yet{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error previewing script: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="List available scripts in the current project")
@click.pass_context
def list(ctx):
    """List all available scripts from awd.yml."""
    try:
        click.echo(f"{INFO}Available scripts:{RESET}")
        
        scripts = _list_available_scripts()
        
        if not scripts:
            click.echo(f"{WARNING}No scripts found.{RESET}")
            click.echo(f"{INFO}💡 Add scripts to your awd.yml file:{RESET}")
            click.echo(f"scripts:")
            click.echo(f"  start: \"codex run main.prompt.md\"")
            click.echo(f"  fast: \"llm prompt main.prompt.md -m github/gpt-4o-mini\"")
            return
            
        # Show default script if 'start' exists
        default_script = 'start' if 'start' in scripts else None
        
        for name, command in scripts.items():
            prefix = "📍 " if name == default_script else "   "
            click.echo(f"{prefix}{HIGHLIGHT}{name}{RESET}: {command}")
            
        if default_script:
            click.echo(f"\n{INFO}📍 = default script (runs when no script name specified){RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing scripts: {e}{RESET}", err=True)
        sys.exit(1)


@cli.command(help="List available LLM models")
@click.pass_context
def models(ctx):
    """List available LLM runtime models."""
    try:
        click.echo(f"{TITLE}Available LLM Runtime Models:{RESET}")
        
        # Try to import and use existing functionality
        try:
            from awd_cli.runtime.llm_runtime import LLMRuntime
            
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
            click.echo(f"  AWD CLI Version: {get_version()}")
            
        else:
            click.echo(f"{INFO}Use --show to display configuration{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error showing configuration: {e}{RESET}", err=True)


@cli.group(help="Manage AI runtimes")
def runtime():
    """Manage AI runtime installations and configurations."""
    pass


@runtime.command(help="Set up a runtime")
@click.argument('runtime_name', type=click.Choice(['codex', 'llm']))
@click.option('--version', help="Specific version to install")
@click.option('--vanilla', is_flag=True, help="Install runtime without AWD configuration (uses runtime's native defaults)")
def setup(runtime_name, version, vanilla):
    """Set up an AI runtime with AWD-managed installation."""
    try:
        from awd_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        success = manager.setup_runtime(runtime_name, version, vanilla)
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{ERROR}Error setting up runtime: {e}{RESET}", err=True)
        sys.exit(1)


@runtime.command(help="List available and installed runtimes")
def list():
    """List all available runtimes and their installation status."""
    try:
        from awd_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        runtimes = manager.list_runtimes()
        
        click.echo(f"{TITLE}Available Runtimes:{RESET}")
        click.echo()
        
        for name, info in runtimes.items():
            status_icon = "✅" if info["installed"] else "❌"
            status_text = "Installed" if info["installed"] else "Not installed"
            
            click.echo(f"{status_icon} {HIGHLIGHT}{name}{RESET}")
            click.echo(f"   Description: {info['description']}")
            click.echo(f"   Status: {status_text}")
            
            if info["installed"]:
                click.echo(f"   Path: {info['path']}")
                if "version" in info:
                    click.echo(f"   Version: {info['version']}")
            
            click.echo()
            
    except Exception as e:
        click.echo(f"{ERROR}Error listing runtimes: {e}{RESET}", err=True)
        sys.exit(1)


@runtime.command(help="Remove an installed runtime")
@click.argument('runtime_name', type=click.Choice(['codex', 'llm']))
@click.confirmation_option(prompt='Are you sure you want to remove this runtime?')
def remove(runtime_name):
    """Remove an installed runtime from AWD management."""
    try:
        from awd_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        success = manager.remove_runtime(runtime_name)
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{ERROR}Error removing runtime: {e}{RESET}", err=True)
        sys.exit(1)


@runtime.command(help="Check which runtime will be used")
def status():
    """Show which runtime AWD will use for execution."""
    try:
        from awd_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        available_runtime = manager.get_available_runtime()
        preference = manager.get_runtime_preference()
        
        click.echo(f"{TITLE}Runtime Status:{RESET}")
        click.echo()
        
        click.echo(f"Preference order: {' → '.join(preference)}")
        
        if available_runtime:
            click.echo(f"{SUCCESS}Active runtime: {available_runtime}{RESET}")
        else:
            click.echo(f"{ERROR}No runtimes available{RESET}")
            click.echo(f"{INFO}Run 'awd runtime setup codex' to install the primary runtime{RESET}")
            
    except Exception as e:
        click.echo(f"{ERROR}Error checking runtime status: {e}{RESET}", err=True)
        sys.exit(1)


def _interactive_project_setup(default_name):
    """Interactive setup for new AWD projects."""
    click.echo(f"\n{INFO}Setting up your AWD project...{RESET}")
    click.echo(f"{INFO}Press ^C at any time to quit.{RESET}")
    
    # Project name
    name = click.prompt(f"Project name", default=default_name).strip()
    
    # Project version  
    version = click.prompt(f"Version", default="1.0.0").strip()
    
    # Project description
    description = click.prompt(f"Description", default=f"A {name} AWD application").strip()
    
    # Author
    author = click.prompt(f"Author", default="Your Name").strip()
    
    # Confirm
    click.echo(f"\n{INFO}About to create:{RESET}")
    click.echo(f"  name: {name}")
    click.echo(f"  version: {version}")
    click.echo(f"  description: {description}")
    click.echo(f"  author: {author}")
    
    if not click.confirm(f"\nIs this OK?", default=True):
        click.echo(f"{INFO}Aborted.{RESET}")
        sys.exit(0)
    
    return {
        'name': name,
        'version': version,
        'description': description,
        'author': author
    }


def _merge_existing_config(default_name):
    """Merge existing awd.yml with defaults for missing fields."""
    try:
        with open('awd.yml', 'r') as f:
            existing_config = yaml.safe_load(f) or {}
    except Exception:
        existing_config = {}
    
    # Preserve existing values, fill in missing ones
    config = {
        'name': existing_config.get('name', default_name),
        'version': existing_config.get('version', '1.0.0'),
        'description': existing_config.get('description', f"A {default_name} AWD application"),
        'author': existing_config.get('author', 'Your Name')
    }
    
    click.echo(f"{INFO}Preserving existing configuration where possible{RESET}")
    return config


def _get_default_config(project_name):
    """Get default configuration for new projects."""
    return {
        'name': project_name,
        'version': '1.0.0',
        'description': f"A {project_name} AWD application",
        'author': 'Your Name'
    }


def _create_project_files(config):
    """Create project files from configuration."""
    # Create awd.yml
    awd_yml_content = _load_template_file('hello-world', 'awd.yml', 
                                          project_name=config['name'],
                                          version=config.get('version', '1.0.0'),
                                          description=config.get('description', f"A {config['name']} AWD application"),
                                          author=config.get('author', 'Your Name'))
    with open('awd.yml', 'w') as f:
        f.write(awd_yml_content)
    
    # Create hello-world.prompt.md from template
    prompt_content = _load_template_file('hello-world', 'hello-world.prompt.md',
                                         project_name=config['name'])
    with open('hello-world.prompt.md', 'w') as f:
        f.write(prompt_content)
        
    # Create README.md from template
    readme_content = _load_template_file('hello-world', 'README.md',
                                         project_name=config['name'])
    with open('README.md', 'w') as f:
        f.write(readme_content)


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"{ERROR}Error: {e}{RESET}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
