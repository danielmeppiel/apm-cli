"""Script runner for APM NPM-like script execution."""

import os
import re
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Optional


class ScriptRunner:
    """Executes APM scripts with auto-compilation of .prompt.md files."""
    
    def __init__(self, compiler=None):
        """Initialize script runner with optional compiler."""
        self.compiler = compiler or PromptCompiler()
    
    def run_script(self, script_name: str, params: Dict[str, str]) -> bool:
        """Run a script from apm.yml with parameter substitution.
        
        Args:
            script_name: Name of the script to run
            params: Parameters for compilation and script execution
            
        Returns:
            bool: True if script executed successfully
        """
        # Load apm.yml configuration
        config = self._load_config()
        if not config:
            raise RuntimeError("No apm.yml found in current directory")
        
        scripts = config.get('scripts', {})
        if script_name not in scripts:
            available = ', '.join(scripts.keys()) if scripts else 'none'
            raise RuntimeError(f"Script '{script_name}' not found. Available scripts: {available}")
        
        # Get the script command
        command = scripts[script_name]
        
        # Auto-compile any .prompt.md files in the command
        compiled_command, compiled_prompt_files = self._auto_compile_prompts(command, params)
        
        # Execute the final command
        print(f"Executing: {compiled_command}")
        try:
            result = subprocess.run(compiled_command, shell=True, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Script execution failed with exit code {e.returncode}")
    
    def list_scripts(self) -> Dict[str, str]:
        """List all available scripts from apm.yml.
        
        Returns:
            Dict mapping script names to their commands
        """
        config = self._load_config()
        return config.get('scripts', {}) if config else {}
    
    def _load_config(self) -> Optional[Dict]:
        """Load apm.yml from current directory."""
        config_path = Path('apm.yml')
        if not config_path.exists():
            return None
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _auto_compile_prompts(self, command: str, params: Dict[str, str]) -> tuple[str, list[str]]:
        """Auto-compile .prompt.md files and transform runtime commands.
        
        Args:
            command: Original script command
            params: Parameters for compilation
            
        Returns:
            Tuple of (compiled_command, list_of_compiled_prompt_files)
        """
        # Find all .prompt.md files in the command using regex
        prompt_files = re.findall(r'(\S+\.prompt\.md)', command)
        compiled_prompt_files = []
        
        compiled_command = command
        for prompt_file in prompt_files:
            # Compile the prompt file with current params
            compiled_path = self.compiler.compile(prompt_file, params)
            compiled_prompt_files.append(prompt_file)
            
            # Read the compiled content
            with open(compiled_path, 'r') as f:
                compiled_content = f.read().strip()
            
            # Transform command based on runtime pattern
            compiled_command = self._transform_runtime_command(
                compiled_command, prompt_file, compiled_content, compiled_path
            )
        
        return compiled_command, compiled_prompt_files
    
    def _transform_runtime_command(self, command: str, prompt_file: str, 
                                 compiled_content: str, compiled_path: str) -> str:
        """Transform runtime commands to their proper execution format.
        
        Args:
            command: Original command
            prompt_file: Original .prompt.md file path
            compiled_content: Compiled prompt content as string
            compiled_path: Path to compiled .txt file
            
        Returns:
            Transformed command for proper runtime execution
        """
        # Handle environment variables prefix (e.g., "ENV1=val1 ENV2=val2 codex [args] file.prompt.md")
        # More robust approach: split by ' codex ' to separate env vars from command
        if ' codex ' in command and re.search(re.escape(prompt_file), command):
            parts = command.split(' codex ', 1)
            potential_env_part = parts[0]
            codex_part = 'codex ' + parts[1]
            
            # Check if the first part looks like environment variables (has = signs)
            if '=' in potential_env_part and not potential_env_part.startswith('codex'):
                env_vars = potential_env_part
                
                # Extract arguments before and after the prompt file from codex part
                codex_match = re.search(r'codex\s+(.*?)(' + re.escape(prompt_file) + r')(.*?)$', codex_part)
                if codex_match:
                    args_before_file = codex_match.group(1).strip()
                    args_after_file = codex_match.group(3).strip()
                    
                    # Build the exec command
                    if args_before_file:
                        result = f"{env_vars} codex exec {args_before_file} '{compiled_content}'"
                    else:
                        result = f"{env_vars} codex exec '{compiled_content}'"
                    
                    if args_after_file:
                        result += f" {args_after_file}"
                    return result
        
        # Handle "codex [args] file.prompt.md [more_args]" -> "codex exec [args] 'compiled_content' [more_args]"  
        elif re.search(r'codex\s+.*' + re.escape(prompt_file), command):
            # Extract arguments before and after the prompt file
            match = re.search(r'codex\s+(.*?)(' + re.escape(prompt_file) + r')(.*?)$', command)
            if match:
                args_before_file = match.group(1).strip()
                args_after_file = match.group(3).strip()
                
                # Build the exec command with arguments
                if args_before_file:
                    result = f"codex exec {args_before_file} '{compiled_content}'"
                else:
                    result = f"codex exec '{compiled_content}'"
                
                if args_after_file:
                    result += f" {args_after_file}"
                return result
        
        # Handle "llm file.prompt.md [options]" -> "llm 'compiled_content' [options]"
        elif re.search(r'llm\s+.*' + re.escape(prompt_file), command):
            # Extract any additional options after the file
            match = re.search(r'llm\s+(.*?)(' + re.escape(prompt_file) + r')(.*?)$', command)
            if match:
                args_before_file = match.group(1).strip()
                args_after_file = match.group(3).strip()
                
                # For llm, we don't add exec, just replace the file with content
                result = f"llm"
                if args_before_file:
                    result += f" {args_before_file}"
                result += f" '{compiled_content}'"
                if args_after_file:
                    result += f" {args_after_file}"
                return result
        
        # Handle bare "file.prompt.md" -> "codex exec 'compiled_content'" (default to codex)
        elif command.strip() == prompt_file:
            return f"codex exec '{compiled_content}'"
        
        # Fallback: just replace file path with compiled path
        # This handles any other patterns we might have missed
        return command.replace(prompt_file, compiled_path)


class PromptCompiler:
    """Compiles .prompt.md files with parameter substitution."""
    
    def __init__(self):
        """Initialize compiler."""
        self.compiled_dir = Path('.apm/compiled')
    
    def compile(self, prompt_file: str, params: Dict[str, str]) -> str:
        """Compile a .prompt.md file with parameter substitution.
        
        Args:
            prompt_file: Path to the .prompt.md file
            params: Parameters to substitute
            
        Returns:
            Path to the compiled file
        """
        # Read the prompt file first (this will fail fast if file doesn't exist)
        prompt_path = Path(prompt_file)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        # Now ensure compiled directory exists
        self.compiled_dir.mkdir(parents=True, exist_ok=True)
        
        with open(prompt_path, 'r') as f:
            content = f.read()
        
        # Parse frontmatter and content
        if content.startswith('---'):
            # Split frontmatter and content
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                main_content = parts[2].strip()
            else:
                main_content = content
        else:
            main_content = content
        
        # Substitute parameters in content
        compiled_content = self._substitute_parameters(main_content, params)
        
        # Generate output file path
        output_name = prompt_path.stem.replace('.prompt', '') + '.txt'
        output_path = self.compiled_dir / output_name
        
        # Write compiled content
        with open(output_path, 'w') as f:
            f.write(compiled_content)
        
        return str(output_path)
    
    def _substitute_parameters(self, content: str, params: Dict[str, str]) -> str:
        """Substitute parameters in content.
        
        Args:
            content: Content to process
            params: Parameters to substitute
            
        Returns:
            Content with parameters substituted
        """
        result = content
        for key, value in params.items():
            # Replace ${input:key} placeholders
            placeholder = f"${{input:{key}}}"
            result = result.replace(placeholder, str(value))
        return result
