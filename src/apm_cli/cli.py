"""Command-line interface for Agent Primitives Manager (APM)."""

import sys
import os
import click
from pathlib import Path
from colorama import init, Fore, Style

# Standard imports
import sys
import os
import click
from pathlib import Path
from colorama import init, Fore, Style

# APM imports - use absolute imports everywhere for consistency
from apm_cli.version import get_version
from apm_cli.compilation import AgentsCompiler, CompilationConfig
from apm_cli.primitives.discovery import discover_primitives

# Initialize colorama for fallback
init(autoreset=True)

# Modern status symbols
STATUS_SYMBOLS = {
    "success": "✨",
    "installed": "🎯", 
    "running": "🚀",
    "building": "⚡",
    "warning": "⚠️ ",
    "error": "❌",
    "info": "💡",
    "default": "📍",
    "file": "📄",
    "folder": "📁",
    "rocket": "🚀",
    "sparkles": "✨",
    "gear": "⚙️ ",
    "check": "✅",
    "cross": "❌"
}

# Legacy colorama constants for compatibility
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


# Lazy loading for Rich components to improve startup performance
_console = None

def _get_console():
    """Get Rich console instance with lazy loading."""
    global _console
    if _console is None:
        try:
            from rich.console import Console
            from rich.theme import Theme
            
            custom_theme = Theme({
                "info": "cyan",
                "warning": "yellow", 
                "error": "bold red",
                "success": "bold green",
                "highlight": "bold magenta",
                "muted": "dim white",
                "accent": "bold blue",
                "title": "bold cyan"
            })
            
            _console = Console(theme=custom_theme)
        except ImportError:
            _console = None
    return _console


def _rich_blank_line():
    """Print a blank line with Rich if available, otherwise use click."""
    console = _get_console()
    if console:
        console.print()
    else:
        click.echo()


def _lazy_yaml():
    """Lazy import for yaml module to improve startup performance."""
    try:
        import yaml
        return yaml
    except ImportError:
        raise ImportError("PyYAML is required but not installed")


def _lazy_prompt():
    """Lazy import for Rich Prompt to improve startup performance."""
    try:
        from rich.prompt import Prompt
        return Prompt
    except ImportError:
        return None


def _lazy_confirm():
    """Lazy import for Rich Confirm to improve startup performance."""
    try:
        from rich.prompt import Confirm
        return Confirm
    except ImportError:
        return None


def _rich_echo(message, style="info", symbol=None, fallback_color=INFO):
    """Print message with Rich styling, fallback to colorama."""
    console = _get_console()
    if console:
        try:
            if symbol:
                message = f"{STATUS_SYMBOLS.get(symbol, '')} {message}"
            console.print(message, style=style)
            return
        except Exception:
            pass
    
    # Fallback to colorama
    if symbol:
        message = f"{STATUS_SYMBOLS.get(symbol, '')} {message}"
    click.echo(f"{fallback_color}{message}{RESET}")


def _rich_success(message, symbol="success"):
    """Print success message with Rich styling."""
    _rich_echo(message, style="success", symbol=symbol, fallback_color=SUCCESS)


def _rich_error(message, symbol="error"):
    """Print error message with Rich styling."""
    _rich_echo(message, style="error", symbol=symbol, fallback_color=ERROR)


def _rich_info(message, symbol="info"):
    """Print info message with Rich styling."""
    _rich_echo(message, style="info", symbol=symbol, fallback_color=INFO)


def _rich_warning(message, symbol="warning"):
    """Print warning message with Rich styling."""
    _rich_echo(message, style="warning", symbol=symbol, fallback_color=WARNING)


def _rich_panel(content, title=None, style="cyan"):
    """Display content in a Rich panel with fallback."""
    console = _get_console()
    if console:
        try:
            from rich.panel import Panel
            if title:
                console.print(Panel(content, title=title, border_style=style))
            else:
                console.print(Panel(content, border_style=style))
            return
        except Exception:
            pass
    
    # Fallback to simple output
    if title:
        click.echo(f"\n{TITLE}{title}{RESET}")
    click.echo(content)
    click.echo()


def _create_files_table(files):
    """Create a table of created files with Rich styling."""
    console = _get_console()
    if console:
        try:
            from rich.table import Table
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Icon", style="cyan")
            table.add_column("File", style="white")
            
            for file in files:
                table.add_row(STATUS_SYMBOLS["file"], file)
            
            return table
        except Exception:
            pass
    
    # Fallback to simple list
    return "\n".join([f"  - {file}" for file in files])


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
    
    console = _get_console()
    if console:
        try:
            from rich.text import Text
            from rich.panel import Panel
            version_text = Text()
            version_text.append("Agent Primitives Manager (APM) CLI", style="bold cyan")
            version_text.append(f" version {get_version()}", style="white")
            console.print(Panel(
                version_text,
                border_style="cyan",
                padding=(0, 1)
            ))
        except Exception:
            click.echo(f"{TITLE}Agent Primitives Manager (APM) CLI{RESET} version {get_version()}")
    else:
        # Fallback to colorama if Rich is not available
        click.echo(f"{TITLE}Agent Primitives Manager (APM) CLI{RESET} version {get_version()}")
    
    ctx.exit()

@click.group(help="✨ Agent Primitives Manager (APM): The package manager for AI-Native Development")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version and exit.")
@click.pass_context
def cli(ctx):
    """Main entry point for the APM CLI."""
    ctx.ensure_object(dict)


@cli.command(help="🚀 Initialize a new APM project")
@click.argument('project_name', required=False)
@click.option('--force', '-f', is_flag=True, help="Overwrite existing files without confirmation")
@click.option('--yes', '-y', is_flag=True, help="Skip interactive questionnaire and use defaults")
@click.pass_context
def init(ctx, project_name, force, yes):
    """Initialize a new APM project (like npm init)."""
    try:
        # Handle explicit current directory
        if project_name == '.':
            project_name = None
            
        # Determine project directory and name
        if project_name:
            project_dir = Path(project_name)
            project_dir.mkdir(exist_ok=True)
            os.chdir(project_dir)
            _rich_info(f"Created project directory: {project_name}", symbol="folder")
            final_project_name = project_name
        else:
            project_dir = Path.cwd()
            final_project_name = project_dir.name
            
        # Check for existing APM project
        apm_yml_exists = Path('apm.yml').exists()
        existing_files = []
        if apm_yml_exists:
            existing_files.append('apm.yml')
        if Path('hello-world.prompt.md').exists():
            existing_files.append('hello-world.prompt.md')
        if Path('README.md').exists():
            existing_files.append('README.md')
            
        # Handle existing project
        if existing_files and not force:
            _rich_warning("Existing APM project detected:")
            for file in existing_files:
                _rich_echo(f"  - {file}", style="muted")
            _rich_blank_line()
            
            if not yes:
                Confirm = _lazy_confirm()
                if Confirm:
                    try:
                        confirm = Confirm.ask("Continue and overwrite existing files?")
                    except Exception:
                        confirm = click.confirm("Continue and overwrite existing files?")
                else:
                    confirm = click.confirm("Continue and overwrite existing files?")
                
                if not confirm:
                    _rich_info("Initialization cancelled.")
                    return
            else:
                _rich_info("--yes specified, continuing with overwrite...")
        
        # Get project configuration (interactive mode or defaults)
        if not yes and not apm_yml_exists:
            config = _interactive_project_setup(final_project_name)
        else:
            # Use defaults or preserve existing config
            if apm_yml_exists and not force:
                config = _merge_existing_config(final_project_name)
            else:
                config = _get_default_config(final_project_name)
        
        _rich_success(f"Initializing APM project: {config['name']}", symbol="rocket")
        
        # Create files from config
        _create_project_files(config)
        
        _rich_success("APM project initialized successfully!", symbol="sparkles")
        
        # Next steps with better formatting
        next_steps = [
            f"1. {STATUS_SYMBOLS['sparkles']} apm compile - Generate AGENTS.md from your primitives",
            f"2. {STATUS_SYMBOLS['gear']} apm install - Install dependencies", 
            f"3. {STATUS_SYMBOLS['running']} apm run start --param name=\"Your Name\" - Run the start script"
        ]
        
        try:
            _rich_panel("\n".join(next_steps), title="Next Steps", style="green")
        except (ImportError, NameError):
            _rich_info("Next steps:")
            for step in next_steps:
                click.echo(f"  {step}")
        
    except Exception as e:
        _rich_error(f"Error initializing project: {e}")
        sys.exit(1)


@cli.command(help="📦 Install MCP dependencies from apm.yml")
@click.pass_context
def install(ctx):
    """Install MCP dependencies from apm.yml (like npm install)."""
    try:
        # Check if apm.yml exists
        if not Path('apm.yml').exists():
            _rich_error("No apm.yml found. Run 'apm init' first.")
            sys.exit(1)
            
        _rich_info("Installing dependencies from apm.yml...", symbol="gear")
        
        # Read apm.yml
        with open('apm.yml', 'r') as f:
            yaml = _lazy_yaml()
            config = yaml.safe_load(f)
            
        # Get MCP dependencies
        mcp_deps = config.get('dependencies', {}).get('mcp', [])
        
        if not mcp_deps:
            _rich_warning("No MCP dependencies found in apm.yml")
            return
            
        _rich_info(f"Found {len(mcp_deps)} MCP dependencies:")
        
        # Show dependencies in a nice list
        console = _get_console()
        if console:
            try:
                from rich.table import Table
                dep_table = Table(show_header=False, box=None, padding=(0, 1))
                dep_table.add_column("Icon", style="cyan")
                dep_table.add_column("Dependency", style="white")
                
                for dep in mcp_deps:
                    dep_table.add_row(STATUS_SYMBOLS["gear"], dep)
                
                console.print(dep_table)
            except Exception:
                for dep in mcp_deps:
                    click.echo(f"  - {dep}")
        else:
            for dep in mcp_deps:
                click.echo(f"  - {dep}")
            
        # Import and use existing MCP installation functionality
        try:
            try:
                from .factory import PackageManagerFactory
                from .core.operations import install_package
            except ImportError:
                from apm_cli.factory import PackageManagerFactory
                from apm_cli.core.operations import install_package
            
            package_manager = PackageManagerFactory.create_package_manager()
            
            for dep in mcp_deps:
                _rich_info(f"Installing {dep}...", symbol="building")
                try:
                    result = install_package('vscode', dep)  # Default to vscode client
                    if result and result.get('success'):
                        _rich_success(f"{dep} installed", symbol="check")
                    else:
                        _rich_warning(f"{dep} installation may have issues")
                except Exception as install_error:
                    _rich_warning(f"Failed to install {dep}: {install_error}")
                    
        except ImportError:
            _rich_warning("MCP installation functionality not available yet")
            dep_list = ', '.join(mcp_deps)
            _rich_info(f"Dependencies listed in apm.yml: {dep_list}")
            
        _rich_blank_line()
        _rich_success("Dependencies installation complete!", symbol="sparkles")
        
    except Exception as e:
        _rich_error(f"Error installing dependencies: {e}")
        sys.exit(1)


def _load_apm_config():
    """Load configuration from apm.yml."""
    if Path('apm.yml').exists():
        with open('apm.yml', 'r') as f:
            yaml = _lazy_yaml()
            return yaml.safe_load(f)
    return None


def _get_default_script():
    """Get the default script (start) from apm.yml scripts."""
    config = _load_apm_config()
    if config and 'scripts' in config and 'start' in config['scripts']:
        return 'start'
    return None


def _list_available_scripts():
    """List all available scripts from apm.yml."""
    config = _load_apm_config()
    if config and 'scripts' in config:
        return config['scripts']
    return {}


@cli.command(help="🚀 Run a script with parameters")
@click.argument('script_name', required=False)
@click.option('--param', '-p', multiple=True, help="Parameter in format name=value")
@click.pass_context
def run(ctx, script_name, param):
    """Run a script from apm.yml (uses 'start' script if no name specified)."""
    try:
        # If no script name specified, use 'start' script
        if not script_name:
            script_name = _get_default_script()
            if not script_name:
                _rich_error("No script specified and no 'start' script defined in apm.yml")
                _rich_info("Available scripts:")
                scripts = _list_available_scripts()
                
                console = _get_console()
                if console:
                    try:
                        from rich.table import Table
                        # Show available scripts in a table
                        table = Table(show_header=False, box=None, padding=(0, 1))
                        table.add_column("Icon", style="cyan")
                        table.add_column("Script", style="highlight")
                        table.add_column("Command", style="white")
                        
                        for name, command in scripts.items():
                            table.add_row("  ", name, command)
                        
                        console.print(table)
                    except Exception:
                        for name, command in scripts.items():
                            click.echo(f"  - {HIGHLIGHT}{name}{RESET}: {command}")
                else:
                    for name, command in scripts.items():
                        click.echo(f"  - {HIGHLIGHT}{name}{RESET}: {command}")
                sys.exit(1)
                
        _rich_info(f"Running script: {script_name}", symbol="running")
        
        # Parse parameters
        params = {}
        for p in param:
            if '=' in p:
                param_name, value = p.split('=', 1)
                params[param_name] = value
                _rich_echo(f"  - {param_name}: {value}", style="muted")
                
        # Import and use script runner
        try:
            from apm_cli.core.script_runner import ScriptRunner
            
            script_runner = ScriptRunner()
            success = script_runner.run_script(script_name, params)
            
            if not success:
                _rich_error("Script execution failed")
                sys.exit(1)
                
            _rich_blank_line()
            _rich_success("Script executed successfully!", symbol="sparkles")
            
        except ImportError as ie:
            _rich_warning("Script runner not available yet")
            _rich_info(f"Import error: {ie}")
            _rich_info(f"Would run script: {script_name} with params {params}")
        except Exception as ee:
            _rich_error(f"Script execution error: {ee}")
            sys.exit(1)
            
    except Exception as e:
        _rich_error(f"Error running script: {e}")
        sys.exit(1)


@cli.command(help="👀 Preview a script's compiled prompt files")
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
                _rich_error("No script specified and no 'start' script defined in apm.yml")
                sys.exit(1)
                
        _rich_info(f"Previewing script: {script_name}", symbol="info")
        
        # Parse parameters
        params = {}
        for p in param:
            if '=' in p:
                param_name, value = p.split('=', 1)
                params[param_name] = value
                _rich_echo(f"  - {param_name}: {value}", style="muted")
                
        # Import and use script runner for preview
        try:
            from apm_cli.core.script_runner import ScriptRunner
            
            script_runner = ScriptRunner()
            
            # Get the script command
            scripts = script_runner.list_scripts()
            if script_name not in scripts:
                _rich_error(f"Script '{script_name}' not found")
                sys.exit(1)
                
            command = scripts[script_name]
            
            try:
                # Show original and compiled commands in panels
                _rich_panel(command, title="📄 Original command", style="blue")
                
                # Auto-compile prompts to show what would be executed
                compiled_command, compiled_prompt_files = script_runner._auto_compile_prompts(command, params)
                
                if compiled_prompt_files:
                    _rich_panel(compiled_command, title="⚡ Compiled command", style="green")
                else:
                    _rich_panel(compiled_command, title="⚡ Command (no prompt compilation)", style="yellow")
                    _rich_warning(f"No .prompt.md files found in command. APM only compiles files ending with '.prompt.md'")
                
                # Show compiled files if any .prompt.md files were processed
                if compiled_prompt_files:
                    file_list = []
                    for prompt_file in compiled_prompt_files:
                        output_name = Path(prompt_file).stem.replace('.prompt', '') + '.txt'
                        compiled_path = Path('.apm/compiled') / output_name
                        file_list.append(str(compiled_path))
                    
                    files_content = "\n".join([f"📄 {file}" for file in file_list])
                    _rich_panel(files_content, title="📁 Compiled prompt files", style="cyan")
                else:
                    _rich_panel(
                        "No .prompt.md files were compiled.\n\n" +
                        "APM only compiles files ending with '.prompt.md' extension.\n" +
                        "Other files are executed as-is by the runtime.", 
                        title="ℹ️  Compilation Info", 
                        style="cyan"
                    )
                
            except (ImportError, NameError):
                # Fallback display
                _rich_info("Original command:")
                click.echo(f"  {command}")
                
                compiled_command, compiled_prompt_files = script_runner._auto_compile_prompts(command, params)
                
                if compiled_prompt_files:
                    _rich_info("Compiled command:")
                    click.echo(f"  {compiled_command}")
                    
                    _rich_info("Compiled prompt files:")
                    for prompt_file in compiled_prompt_files:
                        output_name = Path(prompt_file).stem.replace('.prompt', '') + '.txt'
                        compiled_path = Path('.apm/compiled') / output_name
                        click.echo(f"  - {compiled_path}")
                else:
                    _rich_warning("Command (no prompt compilation):")
                    click.echo(f"  {compiled_command}")
                    _rich_info("APM only compiles files ending with '.prompt.md' extension.")
                    
            _rich_blank_line()
            _rich_success(f"Preview complete! Use 'apm run {script_name}' to execute.", symbol="sparkles")
            
        except ImportError:
            _rich_warning("Script runner not available yet")
            
    except Exception as e:
        _rich_error(f"Error previewing script: {e}")
        sys.exit(1)


@cli.command(help="📋 List available scripts in the current project")
@click.pass_context
def list(ctx):
    """List all available scripts from apm.yml."""
    try:
        scripts = _list_available_scripts()
        
        if not scripts:
            _rich_warning("No scripts found.")
            
            # Show helpful example in a panel
            example_content = """scripts:
  start: "codex run main.prompt.md"
  fast: "llm prompt main.prompt.md -m github/gpt-4o-mini" """
            
            try:
                _rich_panel(example_content, title=f"{STATUS_SYMBOLS['info']} Add scripts to your apm.yml file", style="blue")
            except (ImportError, NameError):
                _rich_info("💡 Add scripts to your apm.yml file:")
                click.echo("scripts:")
                click.echo("  start: \"codex run main.prompt.md\"")
                click.echo("  fast: \"llm prompt main.prompt.md -m github/gpt-4o-mini\"")
            return
        
        # Show default script if 'start' exists
        default_script = 'start' if 'start' in scripts else None
        
        console = _get_console()
        if console:
            try:
                from rich.table import Table
                # Create a nice table for scripts
                table = Table(title="📋 Available Scripts", show_header=True, header_style="bold cyan")
                table.add_column("", style="cyan", width=3)
                table.add_column("Script", style="bold white", min_width=12)
                table.add_column("Command", style="white")
                
                for name, command in scripts.items():
                    icon = STATUS_SYMBOLS["default"] if name == default_script else "  "
                    table.add_row(icon, name, command)
                
                console.print(table)
                
                if default_script:
                    console.print(f"\n[muted]{STATUS_SYMBOLS['info']} {STATUS_SYMBOLS['default']} = default script (runs when no script name specified)[/muted]")
                    
            except Exception:
                # Fallback to simple output
                _rich_info("Available scripts:")
                for name, command in scripts.items():
                    icon = STATUS_SYMBOLS["default"] if name == default_script else "  "
                    click.echo(f"  {icon} {HIGHLIGHT}{name}{RESET}: {command}")
                if default_script:
                    click.echo(f"\n{STATUS_SYMBOLS['info']} {STATUS_SYMBOLS['default']} = default script")
        else:
            # Fallback to simple output
            _rich_info("Available scripts:")
            for name, command in scripts.items():
                icon = STATUS_SYMBOLS["default"] if name == default_script else "  "
                click.echo(f"  {icon} {HIGHLIGHT}{name}{RESET}: {command}")
            if default_script:
                click.echo(f"\n{STATUS_SYMBOLS['info']} {STATUS_SYMBOLS['default']} = default script")
            # Fallback to simple output
            _rich_info("Available scripts:")
            for name, command in scripts.items():
                prefix = "📍 " if name == default_script else "   "
                click.echo(f"{prefix}{HIGHLIGHT}{name}{RESET}: {command}")
                
            if default_script:
                _rich_info("📍 = default script (runs when no script name specified)")
            
    except Exception as e:
        _rich_error(f"Error listing scripts: {e}")
        sys.exit(1)


def _display_validation_errors(errors):
    """Display validation errors in a Rich table with actionable feedback."""
    try:
        console = _get_console()
        if console:
            from rich.table import Table
            
            error_table = Table(title="❌ Primitive Validation Errors", show_header=True, header_style="bold red")
            error_table.add_column("File", style="bold red", min_width=20)
            error_table.add_column("Error", style="white", min_width=30)
            error_table.add_column("Suggestion", style="yellow", min_width=25)
            
            for error in errors:
                file_path = str(error) if hasattr(error, '__str__') else "Unknown"
                # Extract file path from error string if it contains file info
                if ":" in file_path:
                    parts = file_path.split(":", 1)
                    file_name = parts[0] if len(parts) > 1 else "Unknown"
                    error_msg = parts[1].strip() if len(parts) > 1 else file_path
                else:
                    file_name = "Unknown"
                    error_msg = file_path
                
                # Provide actionable suggestions based on error type
                suggestion = _get_validation_suggestion(error_msg)
                error_table.add_row(file_name, error_msg, suggestion)
            
            console.print(error_table)
            return
        
    except (ImportError, NameError):
        pass
    
    # Fallback to simple text output
    _rich_error("Validation errors found:")
    for error in errors:
        click.echo(f"  ❌ {error}")


def _get_validation_suggestion(error_msg):
    """Get actionable suggestions for validation errors."""
    if "Missing 'description'" in error_msg:
        return "Add 'description: Your description here' to frontmatter"
    elif "Missing 'applyTo'" in error_msg:
        return "Add 'applyTo: \"**/*.py\"' to frontmatter"
    elif "Empty content" in error_msg:
        return "Add markdown content below the frontmatter"
    else:
        return "Check primitive structure and frontmatter"


def _watch_mode(output, chatmode, no_links, dry_run):
    """Watch for changes in .apm/ directories and auto-recompile."""
    try:
        # Try to import watchdog for file system monitoring
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import time
        
        class APMFileHandler(FileSystemEventHandler):
            def __init__(self, output, chatmode, no_links, dry_run):
                self.output = output
                self.chatmode = chatmode
                self.no_links = no_links
                self.dry_run = dry_run
                self.last_compile = 0
                self.debounce_delay = 1.0  # 1 second debounce
                
            def on_modified(self, event):
                if event.is_directory:
                    return
                    
                # Check if it's a relevant file
                if (event.src_path.endswith('.md') or 
                    event.src_path.endswith('apm.yml')):
                    
                    # Debounce rapid changes
                    current_time = time.time()
                    if current_time - self.last_compile < self.debounce_delay:
                        return
                    
                    self.last_compile = current_time
                    self._recompile(event.src_path)
            
            def _recompile(self, changed_file):
                """Recompile after file change."""
                try:
                    _rich_info(f"File changed: {changed_file}", symbol="eyes")
                    _rich_info("Recompiling...", symbol="gear")
                    
                    # Create configuration from apm.yml with overrides
                    config = CompilationConfig.from_apm_yml(
                        output_path=self.output if self.output != "AGENTS.md" else None,
                        chatmode=self.chatmode,
                        resolve_links=not self.no_links if self.no_links else None,
                        dry_run=self.dry_run
                    )
                    
                    # Create compiler and compile
                    compiler = AgentsCompiler(".")
                    result = compiler.compile(config)
                    
                    if result.success:
                        if self.dry_run:
                            _rich_success("Recompilation successful (dry run)", symbol="sparkles")
                        else:
                            _rich_success(f"Recompiled to {result.output_path}", symbol="sparkles")
                    else:
                        _rich_error("Recompilation failed")
                        for error in result.errors:
                            click.echo(f"  ❌ {error}")
                    
                except Exception as e:
                    _rich_error(f"Error during recompilation: {e}")
        
        # Set up file watching
        event_handler = APMFileHandler(output, chatmode, no_links, dry_run)
        observer = Observer()
        
        # Watch patterns for APM files
        watch_paths = []
        
        # Check for .apm directory
        if Path(".apm").exists():
            observer.schedule(event_handler, ".apm", recursive=True)
            watch_paths.append(".apm/")
        
        # Check for .github/instructions and chatmodes
        if Path(".github/instructions").exists():
            observer.schedule(event_handler, ".github/instructions", recursive=True)
            watch_paths.append(".github/instructions/")
            
        if Path(".github/chatmodes").exists():
            observer.schedule(event_handler, ".github/chatmodes", recursive=True)
            watch_paths.append(".github/chatmodes/")
        
        # Watch apm.yml if it exists
        if Path("apm.yml").exists():
            observer.schedule(event_handler, ".", recursive=False)
            watch_paths.append("apm.yml")
        
        if not watch_paths:
            _rich_warning("No APM directories found to watch")
            _rich_info("Run 'apm init' to create an APM project")
            return
        
        # Start watching
        observer.start()
        _rich_info(f"👀 Watching for changes in: {', '.join(watch_paths)}", symbol="eyes")
        _rich_info("Press Ctrl+C to stop watching...", symbol="info")
        
        # Do initial compilation
        _rich_info("Performing initial compilation...", symbol="gear")
        
        config = CompilationConfig.from_apm_yml(
            output_path=output if output != "AGENTS.md" else None,
            chatmode=chatmode,
            resolve_links=not no_links if no_links else None,
            dry_run=dry_run
        )
        
        compiler = AgentsCompiler(".")
        result = compiler.compile(config)
        
        if result.success:
            if dry_run:
                _rich_success("Initial compilation successful (dry run)", symbol="sparkles")
            else:
                _rich_success(f"Initial compilation complete: {result.output_path}", symbol="sparkles")
        else:
            _rich_error("Initial compilation failed")
            for error in result.errors:
                click.echo(f"  ❌ {error}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            _rich_info("Stopped watching for changes", symbol="info")
        
        observer.join()
        
    except ImportError:
        _rich_error("Watch mode requires the 'watchdog' library")
        _rich_info("Install it with: uv pip install watchdog")
        _rich_info("Or reinstall APM CLI: uv pip install -e . (from the apm-cli directory)")
        sys.exit(1)
    except Exception as e:
        _rich_error(f"Error in watch mode: {e}")
        sys.exit(1)


@cli.command(help="📝 Compile APM primitives into AGENTS.md")
@click.option('--output', '-o', default="AGENTS.md", help="Output file path")
@click.option('--dry-run', is_flag=True, help="Generate content without writing file")
@click.option('--no-links', is_flag=True, help="Skip markdown link resolution")
@click.option('--chatmode', help="Chatmode to prepend to the AGENTS.md file")
@click.option('--watch', is_flag=True, help="Auto-regenerate on changes")
@click.option('--validate', is_flag=True, help="Validate primitives without compiling")
@click.pass_context
def compile(ctx, output, dry_run, no_links, chatmode, watch, validate):
    """Compile APM primitives into a single AGENTS.md file.
    
    Supports validation-only mode with --validate, watch mode with --watch,
    and various output customization options.
    """
    try:
        
        # Handle validation-only mode
        if validate:
            _rich_info("Validating APM primitives...", symbol="gear")
            compiler = AgentsCompiler(".")
            
            # Discover and validate primitives
            try:
                primitives = discover_primitives(".")
            except Exception as e:
                _rich_error(f"Failed to discover primitives: {e}")
                _rich_info(f"💡 Error details: {type(e).__name__}")
                sys.exit(1)
            validation_errors = compiler.validate_primitives(primitives)
            
            if validation_errors:
                _display_validation_errors(validation_errors)
                _rich_error(f"Validation failed with {len(validation_errors)} errors")
                sys.exit(1)
            else:
                _rich_success("All primitives validated successfully!", symbol="sparkles")
                _rich_info(f"Validated {primitives.count()} primitives:")
                _rich_info(f"  • {len(primitives.chatmodes)} chatmodes")
                _rich_info(f"  • {len(primitives.instructions)} instructions")
                _rich_info(f"  • {len(primitives.contexts)} contexts")
            return
        
        # Handle watch mode
        if watch:
            _watch_mode(output, chatmode, no_links, dry_run)
            return
            
        _rich_info("Starting AGENTS.md compilation...", symbol="gear")
        
        # Create configuration from apm.yml with command-line overrides
        config = CompilationConfig.from_apm_yml(
            output_path=output if output != "AGENTS.md" else None,  # Only override if not default
            chatmode=chatmode,
            resolve_links=not no_links if no_links else None,  # Only override if explicitly set
            dry_run=dry_run
        )
        
        # Create compiler and compile
        compiler = AgentsCompiler(".")
        result = compiler.compile(config)
        
        # Display results
        if result.success:
            if dry_run:
                _rich_success("Compilation completed successfully (dry run)", symbol="sparkles")
                _rich_info(f"Generated {len(result.content)} characters of content")
                
                # Show preview
                try:
                    console = _get_console()
                    if console:
                        from rich.panel import Panel
                        preview = result.content[:500] + ("..." if len(result.content) > 500 else "")
                        console.print(Panel(preview, title="📋 Generated Content Preview", border_style="cyan"))
                    else:
                        _rich_info("Generated content preview:")
                        preview = result.content[:500] + ("..." if len(result.content) > 500 else "")
                        click.echo(preview)
                except (ImportError, NameError):
                    _rich_info("Generated content preview:")
                    preview = result.content[:500] + ("..." if len(result.content) > 500 else "")
                    click.echo(preview)
            else:
                _rich_success(f"AGENTS.md compiled successfully to {result.output_path}", symbol="sparkles")
                
                # Show statistics
                stats = result.stats
                _rich_info(f"Processed {stats.get('primitives_found', 0)} primitives:")
                _rich_info(f"  • {stats.get('instructions', 0)} instructions")
                _rich_info(f"  • {stats.get('contexts', 0)} contexts")
                
                # Show next steps
                try:
                    next_steps = [
                        f"Review the generated {output} file",
                        "Make any manual adjustments if needed",
                        "Share with your AI assistant for context"
                    ]
                    
                    console = _get_console()
                    if console:
                        from rich.panel import Panel
                        steps_content = "\n".join(f"• {step}" for step in next_steps)
                        console.print(Panel(steps_content, title="💡 Next Steps", border_style="blue"))
                    else:
                        _rich_info("Next steps:")
                        for step in next_steps:
                            click.echo(f"  • {step}")
                except (ImportError, NameError):
                    _rich_info("Next steps:")
                    for step in next_steps:
                        click.echo(f"  • {step}")
        
        # Display warnings
        if result.warnings:
            _rich_warning(f"Compilation completed with {len(result.warnings)} warnings:")
            for warning in result.warnings:
                click.echo(f"  ⚠️  {warning}")
        
        # Display errors
        if result.errors:
            _rich_error(f"Compilation failed with {len(result.errors)} errors:")
            for error in result.errors:
                click.echo(f"  ❌ {error}")
            sys.exit(1)
            
    except ImportError as e:
        _rich_error(f"Compilation module not available: {e}")
        _rich_info("This might be a development environment issue.")
        sys.exit(1)
    except Exception as e:
        _rich_error(f"Error during compilation: {e}")
        sys.exit(1)


@cli.command(help="⚙️  Configure APM CLI")
@click.option('--show', is_flag=True, help="Show current configuration")
@click.pass_context
def config(ctx, show):
    """Configure APM CLI settings."""
    try:
        if show:
            try:
                # Create configuration display
                config_table = Table(title="⚙️  Current APM Configuration", show_header=True, header_style="bold cyan")
                config_table.add_column("Category", style="bold yellow", min_width=12)
                config_table.add_column("Setting", style="white", min_width=15)
                config_table.add_column("Value", style="cyan")
                
                # Show apm.yml if in project
                if Path('apm.yml').exists():
                    config = _load_apm_config()
                    config_table.add_row("Project", "Name", config.get('name', 'Unknown'))
                    config_table.add_row("", "Version", config.get('version', 'Unknown'))
                    config_table.add_row("", "Entrypoint", config.get('entrypoint', 'None'))
                    config_table.add_row("", "MCP Dependencies", str(len(config.get('dependencies', {}).get('mcp', []))))
                    
                    # Show compilation configuration
                    compilation_config = config.get('compilation', {})
                    if compilation_config:
                        config_table.add_row("Compilation", "Output", compilation_config.get('output', 'AGENTS.md'))
                        config_table.add_row("", "Chatmode", compilation_config.get('chatmode', 'auto-detect'))
                        config_table.add_row("", "Resolve Links", str(compilation_config.get('resolve_links', True)))
                    else:
                        config_table.add_row("Compilation", "Status", "Using defaults (no config)")
                else:
                    config_table.add_row("Project", "Status", "Not in an APM project directory")
                
                config_table.add_row("Global", "APM CLI Version", get_version())
                
                console.print(config_table)
                
            except (ImportError, NameError):
                # Fallback display
                _rich_info("Current APM Configuration:")
                
                if Path('apm.yml').exists():
                    config = _load_apm_config()
                    click.echo(f"\n{HIGHLIGHT}Project (apm.yml):{RESET}")
                    click.echo(f"  Name: {config.get('name', 'Unknown')}")
                    click.echo(f"  Version: {config.get('version', 'Unknown')}")
                    click.echo(f"  Entrypoint: {config.get('entrypoint', 'None')}")
                    click.echo(f"  MCP Dependencies: {len(config.get('dependencies', {}).get('mcp', []))}")
                else:
                    _rich_info("Not in an APM project directory")
                    
                click.echo(f"\n{HIGHLIGHT}Global:{RESET}")
                click.echo(f"  APM CLI Version: {get_version()}")
            
        else:
            _rich_info("Use --show to display configuration")
            
    except Exception as e:
        _rich_error(f"Error showing configuration: {e}")
        sys.exit(1)


@cli.group(help="🤖 Manage AI runtimes")
def runtime():
    """Manage AI runtime installations and configurations."""
    pass


@runtime.command(help="⚙️  Set up a runtime")
@click.argument('runtime_name', type=click.Choice(['codex', 'llm']))
@click.option('--version', help="Specific version to install")
@click.option('--vanilla', is_flag=True, help="Install runtime without APM configuration (uses runtime's native defaults)")
def setup(runtime_name, version, vanilla):
    """Set up an AI runtime with APM-managed installation."""
    try:
        _rich_info(f"Setting up {runtime_name} runtime...", symbol="gear")
        
        from apm_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        success = manager.setup_runtime(runtime_name, version, vanilla)
        
        if not success:
            sys.exit(1)
        else:
            _rich_success(f"{runtime_name} runtime setup complete!", symbol="sparkles")
            
    except Exception as e:
        _rich_error(f"Error setting up runtime: {e}")
        sys.exit(1)


@runtime.command(help="📋 List available and installed runtimes")
def list():
    """List all available runtimes and their installation status."""
    try:
        from apm_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        runtimes = manager.list_runtimes()
        
        try:
            # Create a nice table for runtimes
            table = Table(title="🤖 Available Runtimes", show_header=True, header_style="bold cyan")
            table.add_column("Status", style="green", width=8)
            table.add_column("Runtime", style="bold white", min_width=10)
            table.add_column("Description", style="white")
            table.add_column("Details", style="muted")
            
            for name, info in runtimes.items():
                status_icon = STATUS_SYMBOLS["check"] if info["installed"] else STATUS_SYMBOLS["cross"]
                status_text = "Installed" if info["installed"] else "Not installed"
                
                details = ""
                if info["installed"]:
                    details_list = [f"Path: {info['path']}"]
                    if "version" in info:
                        details_list.append(f"Version: {info['version']}")
                    details = "\n".join(details_list)
                
                table.add_row(
                    f"{status_icon} {status_text}",
                    name,
                    info['description'],
                    details
                )
            
            console.print(table)
            
        except (ImportError, NameError):
            # Fallback to simple output
            _rich_info("Available Runtimes:")
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
        _rich_error(f"Error listing runtimes: {e}")
        sys.exit(1)


@runtime.command(help="🗑️  Remove an installed runtime")
@click.argument('runtime_name', type=click.Choice(['codex', 'llm']))
@click.confirmation_option(prompt='Are you sure you want to remove this runtime?')
def remove(runtime_name):
    """Remove an installed runtime from APM management."""
    try:
        _rich_info(f"Removing {runtime_name} runtime...", symbol="gear")
        
        from apm_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        success = manager.remove_runtime(runtime_name)
        
        if not success:
            sys.exit(1)
        else:
            _rich_success(f"{runtime_name} runtime removed successfully!", symbol="sparkles")
            
    except Exception as e:
        _rich_error(f"Error removing runtime: {e}")
        sys.exit(1)


@runtime.command(help="📊 Check which runtime will be used")
def status():
    """Show which runtime APM will use for execution."""
    try:
        from apm_cli.runtime.manager import RuntimeManager
        
        manager = RuntimeManager()
        available_runtime = manager.get_available_runtime()
        preference = manager.get_runtime_preference()
        
        try:
            # Create a nice status display
            status_content = f"""Preference order: {' → '.join(preference)}

Active runtime: {available_runtime if available_runtime else 'None available'}"""
            
            if not available_runtime:
                status_content += f"\n\n{STATUS_SYMBOLS['info']} Run 'apm runtime setup codex' to install the primary runtime"
            
            _rich_panel(status_content, title="📊 Runtime Status", style="cyan")
            
        except (ImportError, NameError):
            # Fallback display
            _rich_info("Runtime Status:")
            click.echo()
            
            click.echo(f"Preference order: {' → '.join(preference)}")
            
            if available_runtime:
                _rich_success(f"Active runtime: {available_runtime}")
            else:
                _rich_error("No runtimes available")
                _rich_info("Run 'apm runtime setup codex' to install the primary runtime")
            
    except Exception as e:
        _rich_error(f"Error checking runtime status: {e}")
        sys.exit(1)


def _interactive_project_setup(default_name):
    """Interactive setup for new APM projects."""
    try:
        # Rich interactive prompts
        console.print("\n[info]Setting up your APM project...[/info]")
        console.print("[muted]Press ^C at any time to quit.[/muted]\n")
        
        name = Prompt.ask("Project name", default=default_name).strip()
        version = Prompt.ask("Version", default="1.0.0").strip()
        description = Prompt.ask("Description", default=f"A {name} APM application").strip()
        author = Prompt.ask("Author", default="Your Name").strip()
        
        # Show summary in a nice panel
        summary_content = f"""name: {name}
version: {version}
description: {description}
author: {author}"""
        
        console.print(Panel(summary_content, title="About to create", border_style="cyan"))
        
        if not Confirm.ask("\nIs this OK?", default=True):
            console.print("[info]Aborted.[/info]")
            sys.exit(0)
        
    except (ImportError, NameError):
        # Fallback to click prompts
        _rich_info("Setting up your APM project...")
        _rich_info("Press ^C at any time to quit.")
        
        name = click.prompt("Project name", default=default_name).strip()
        version = click.prompt("Version", default="1.0.0").strip()
        description = click.prompt("Description", default=f"A {name} APM application").strip()
        author = click.prompt("Author", default="Your Name").strip()
        
        click.echo(f"\n{INFO}About to create:{RESET}")
        click.echo(f"  name: {name}")
        click.echo(f"  version: {version}")
        click.echo(f"  description: {description}")
        click.echo(f"  author: {author}")
        
        if not click.confirm("\nIs this OK?", default=True):
            _rich_info("Aborted.")
            sys.exit(0)
    
    return {
        'name': name,
        'version': version,
        'description': description,
        'author': author
    }


def _merge_existing_config(default_name):
    """Merge existing apm.yml with defaults for missing fields."""
    try:
        with open('apm.yml', 'r') as f:
            yaml = _lazy_yaml()
            existing_config = yaml.safe_load(f) or {}
    except Exception:
        existing_config = {}
    
    # Preserve existing values, fill in missing ones
    config = {
        'name': existing_config.get('name', default_name),
        'version': existing_config.get('version', '1.0.0'),
        'description': existing_config.get('description', f"A {default_name} APM application"),
        'author': existing_config.get('author', 'Your Name')
    }
    
    _rich_info("Preserving existing configuration where possible")
    return config


def _get_default_config(project_name):
    """Get default configuration for new projects."""
    return {
        'name': project_name,
        'version': '1.0.0',
        'description': f"A {project_name} APM application",
        'author': 'Your Name'
    }


def _create_project_files(config):
    """Create project files from configuration."""
    # Create apm.yml
    apm_yml_content = _load_template_file('hello-world', 'apm.yml', 
                                          project_name=config['name'],
                                          version=config.get('version', '1.0.0'),
                                          description=config.get('description', f"A {config['name']} APM application"),
                                          author=config.get('author', 'Your Name'))
    with open('apm.yml', 'w') as f:
        f.write(apm_yml_content)
    
    # Create hello-world.prompt.md from template
    prompt_content = _load_template_file('hello-world', 'hello-world.prompt.md',
                                         project_name=config['name'])
    with open('hello-world.prompt.md', 'w') as f:
        f.write(prompt_content)
        
    # Create feature-implementation.prompt.md from template
    feature_content = _load_template_file('hello-world', 'feature-implementation.prompt.md',
                                         project_name=config['name'])
    with open('feature-implementation.prompt.md', 'w') as f:
        f.write(feature_content)
        
    # Create README.md from template
    readme_content = _load_template_file('hello-world', 'README.md',
                                         project_name=config['name'])
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    # Create .apm directory structure and copy all primitive files
    apm_dir = Path('.apm')
    apm_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    for subdir in ['chatmodes', 'instructions', 'context', 'specs']:
        (apm_dir / subdir).mkdir(exist_ok=True)
    
    # Copy primitive files
    primitive_files = [
        '.apm/chatmodes/default.chatmode.md',
        '.apm/chatmodes/backend-engineer.chatmode.md',
        '.apm/instructions/typescript.instructions.md',
        '.apm/instructions/python.instructions.md',
        '.apm/instructions/testing.instructions.md',
        '.apm/context/project-info.context.md',
        '.apm/context/architecture.context.md',
        '.apm/specs/hello-feature.spec.md'
    ]
    
    for primitive_file in primitive_files:
        try:
            primitive_content = _load_template_file('hello-world', primitive_file,
                                                   project_name=config['name'])
            output_path = Path(primitive_file)
            with open(output_path, 'w') as f:
                f.write(primitive_content)
        except Exception as e:
            # Don't fail if individual primitive files can't be loaded
            _rich_warning(f"Could not create {primitive_file}: {e}")
            continue


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        click.echo(f"{ERROR}Error: {e}{RESET}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
