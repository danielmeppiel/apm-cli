"""
Runtime management functionality for APM CLI.
Handles installation, configuration, and management of AI runtimes.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import click
from colorama import Fore, Style


class RuntimeManager:
    """Manages AI runtime installation and configuration via embedded scripts."""
    
    def __init__(self):
        self.runtime_dir = Path.home() / ".apm" / "runtimes"
        self.supported_runtimes = {
            "codex": {
                "script": "setup-codex.sh",
                "description": "OpenAI Codex CLI with GitHub Models support",
                "binary": "codex"
            },
            "llm": {
                "script": "setup-llm.sh", 
                "description": "Simon Willison's LLM library with multiple providers",
                "binary": "llm"
            }
        }
    
    def get_embedded_script(self, script_name: str) -> str:
        """Get embedded setup script content."""
        try:
            # Try PyInstaller bundle first
            if getattr(sys, 'frozen', False):
                # Running in PyInstaller bundle
                bundle_dir = Path(sys._MEIPASS)
                script_path = bundle_dir / "scripts" / "runtime" / script_name
                if script_path.exists():
                    return script_path.read_text()
            
            # Fall back to direct file access for development
            # Look for scripts relative to the repo structure
            current_file = Path(__file__)
            repo_root = current_file.parent.parent.parent.parent  # Go up to repo root
            script_path = repo_root / "scripts" / "runtime" / script_name
            if script_path.exists():
                return script_path.read_text()
            
            raise FileNotFoundError(f"Script not found: {script_name}")
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Failed to load embedded script {script_name}: {e}{Style.RESET_ALL}", err=True)
            raise RuntimeError(f"Could not load setup script: {script_name}")
    
    def get_common_script(self) -> str:
        """Get the common utilities script."""
        return self.get_embedded_script("setup-common.sh")
    
    def run_embedded_script(self, script_content: str, common_content: str, 
                           script_args: Optional[List[str]] = None) -> bool:
        """Execute an embedded bash script with common utilities."""
        script_args = script_args or []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write common utilities
            common_script = temp_path / "setup-common.sh"
            common_script.write_text(common_content)
            common_script.chmod(0o755)
            
            # Write main script
            main_script = temp_path / "setup-script.sh"
            main_script.write_text(script_content)
            main_script.chmod(0o755)
            
            # Execute script
            try:
                cmd = ["bash", str(main_script)] + script_args
                result = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    capture_output=False,  # Show output to user
                    text=True
                )
                return result.returncode == 0
            except Exception as e:
                click.echo(f"{Fore.RED}❌ Failed to execute setup script: {e}{Style.RESET_ALL}", err=True)
                return False
    
    def setup_runtime(self, runtime_name: str, version: Optional[str] = None, vanilla: bool = False) -> bool:
        """Set up a specific runtime."""
        if runtime_name not in self.supported_runtimes:
            click.echo(f"{Fore.RED}❌ Unsupported runtime: {runtime_name}{Style.RESET_ALL}", err=True)
            click.echo(f"{Fore.BLUE}ℹ️  Supported runtimes: {', '.join(self.supported_runtimes.keys())}{Style.RESET_ALL}")
            return False
        
        runtime_info = self.supported_runtimes[runtime_name]
        script_name = runtime_info["script"]
        description = runtime_info["description"]
        
        click.echo(f"{Fore.BLUE}🔧 Setting up {runtime_name} runtime: {description}{Style.RESET_ALL}")
        
        if vanilla:
            click.echo(f"{Fore.YELLOW}⚠️  Installing in vanilla mode - no APM configuration will be applied{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.BLUE}ℹ️  Installing with APM defaults (GitHub Models for free access){Style.RESET_ALL}")
        
        try:
            # Get scripts
            script_content = self.get_embedded_script(script_name)
            common_content = self.get_common_script()
            
            # Prepare arguments
            script_args = []
            if version:
                script_args.append(version)
            if vanilla:
                script_args.append("--vanilla")
            
            # Run setup script
            success = self.run_embedded_script(script_content, common_content, script_args)
            
            if success:
                click.echo(f"{Fore.GREEN}✅ Successfully set up {runtime_name} runtime{Style.RESET_ALL}")
                return True
            else:
                click.echo(f"{Fore.RED}❌ Failed to set up {runtime_name} runtime{Style.RESET_ALL}", err=True)
                return False
                
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Error setting up {runtime_name}: {e}{Style.RESET_ALL}", err=True)
            return False
    
    def list_runtimes(self) -> Dict[str, Dict[str, str]]:
        """List available and installed runtimes."""
        runtimes = {}
        
        for name, info in self.supported_runtimes.items():
            binary_path = self.runtime_dir / info["binary"]
            
            runtime_status = {
                "description": info["description"],
                "installed": binary_path.exists(),
                "path": str(binary_path) if binary_path.exists() else None
            }
            
            # Try to get version if installed
            if runtime_status["installed"]:
                try:
                    result = subprocess.run(
                        [str(binary_path), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        runtime_status["version"] = result.stdout.strip()
                except Exception:
                    runtime_status["version"] = "unknown"
            
            runtimes[name] = runtime_status
        
        return runtimes
    
    def is_runtime_available(self, runtime_name: str) -> bool:
        """Check if a runtime is installed and available."""
        if runtime_name not in self.supported_runtimes:
            return False
        
        binary_name = self.supported_runtimes[runtime_name]["binary"]
        
        # Check in APM runtime directory
        apm_binary = self.runtime_dir / binary_name
        if apm_binary.exists() and apm_binary.is_file():
            return True
        
        # Check in system PATH
        return shutil.which(binary_name) is not None
    
    def remove_runtime(self, runtime_name: str) -> bool:
        """Remove an installed runtime."""
        if runtime_name not in self.supported_runtimes:
            click.echo(f"{Fore.RED}❌ Unknown runtime: {runtime_name}{Style.RESET_ALL}", err=True)
            return False
        
        binary_name = self.supported_runtimes[runtime_name]["binary"]
        binary_path = self.runtime_dir / binary_name
        
        if not binary_path.exists():
            click.echo(f"{Fore.YELLOW}⚠️  Runtime {runtime_name} is not installed in APM runtime directory{Style.RESET_ALL}")
            return False
        
        try:
            if binary_path.is_file():
                binary_path.unlink()
            elif binary_path.is_dir():
                shutil.rmtree(binary_path)
            
            # Also remove virtual environment for LLM
            if runtime_name == "llm":
                venv_path = self.runtime_dir / "llm-venv"
                if venv_path.exists():
                    shutil.rmtree(venv_path)
            
            click.echo(f"{Fore.GREEN}✅ Successfully removed {runtime_name} runtime{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Failed to remove {runtime_name}: {e}{Style.RESET_ALL}", err=True)
            return False
    
    def get_runtime_preference(self) -> List[str]:
        """Get the runtime preference order."""
        return ["codex", "llm"]
    
    def get_available_runtime(self) -> Optional[str]:
        """Get the first available runtime based on preference."""
        for runtime in self.get_runtime_preference():
            if self.is_runtime_available(runtime):
                return runtime
        return None
