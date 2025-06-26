"""Codex runtime adapter for AWD."""

import subprocess
import shutil
from typing import Dict, Any, Optional
from .base import RuntimeAdapter


class CodexRuntime(RuntimeAdapter):
    """AWD adapter for the Codex CLI."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize Codex runtime.
        
        Args:
            model_name: Model name (not used for Codex, included for compatibility)
        """
        if not self.is_available():
            raise RuntimeError("Codex CLI not available. Install with: npm i -g @openai/codex@native")
        
        self.model_name = model_name or "default"
    
    def execute_prompt(self, prompt_content: str, **kwargs) -> str:
        """Execute a single prompt and return the response.
        
        Args:
            prompt_content: The prompt text to execute
            **kwargs: Additional arguments (not used for Codex)
            
        Returns:
            str: The response text from Codex
        """
        try:
            # Use codex exec to execute the prompt
            result = subprocess.run(
                ["codex", "exec", prompt_content],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Codex execution failed: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Codex execution timed out after 5 minutes")
        except FileNotFoundError:
            raise RuntimeError("Codex CLI not found. Install with: npm i -g @openai/codex@native")
        except Exception as e:
            raise RuntimeError(f"Failed to execute prompt with Codex: {e}")
    
    def list_available_models(self) -> Dict[str, Any]:
        """List all available models in the Codex runtime.
        
        Note: Codex manages its own models, so we return generic info.
        
        Returns:
            Dict[str, Any]: Dictionary of available models and their info
        """
        try:
            # Codex doesn't expose model listing via CLI, return generic info
            return {
                "codex-default": {
                    "id": "codex-default",
                    "provider": "codex",
                    "description": "Default Codex model (managed by Codex CLI)"
                }
            }
        except Exception as e:
            return {"error": f"Failed to list Codex models: {e}"}
    
    def get_runtime_info(self) -> Dict[str, Any]:
        """Get information about this runtime.
        
        Returns:
            Dict[str, Any]: Runtime information including name, version, capabilities
        """
        try:
            # Try to get Codex version
            version_result = subprocess.run(
                ["codex", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            version = version_result.stdout.strip() if version_result.returncode == 0 else "unknown"
            
            return {
                "name": "codex",
                "type": "codex_cli", 
                "version": version,
                "capabilities": {
                    "model_execution": True,
                    "mcp_servers": "native_support",
                    "configuration": "config.toml",
                    "sandboxing": "built_in"
                },
                "description": "OpenAI Codex CLI runtime adapter"
            }
        except Exception as e:
            return {"error": f"Failed to get Codex runtime info: {e}"}
    
    @staticmethod
    def is_available() -> bool:
        """Check if this runtime is available on the system.
        
        Returns:
            bool: True if runtime is available, False otherwise
        """
        return shutil.which("codex") is not None
    
    @staticmethod
    def get_runtime_name() -> str:
        """Get the name of this runtime.
        
        Returns:
            str: Runtime name
        """
        return "codex"
    
    def __str__(self) -> str:
        return f"CodexRuntime(model={self.model_name})"