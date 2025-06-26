"""LLM runtime adapter for AWD."""

import llm
from typing import Dict, Any, Optional
from .base import RuntimeAdapter


class LLMRuntime(RuntimeAdapter):
    """AWD adapter for the llm library."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize LLM runtime with specified model.
        
        Args:
            model_name: Name of the LLM model to use
        """
        try:
            self.model = llm.get_model(model_name)
            self.model_name = model_name
        except Exception as e:
            # Fallback to default model if specified model fails
            try:
                self.model = llm.get_model("gpt-4o-mini")
                self.model_name = "gpt-4o-mini"
                print(f"Warning: {model_name} not available, using gpt-4o-mini")
            except Exception:
                raise RuntimeError(f"Failed to initialize LLM runtime: {e}")
    
    def execute_prompt(self, prompt_content: str, **kwargs) -> str:
        """Execute a single prompt and return the response.
        
        Args:
            prompt_content: The prompt text to execute
            **kwargs: Additional arguments passed to the model
            
        Returns:
            str: The response text from the model
        """
        try:
            response = self.model.prompt(prompt_content, **kwargs)
            return response.text()
        except Exception as e:
            raise RuntimeError(f"Failed to execute prompt: {e}")
    
    def list_available_models(self) -> Dict[str, Any]:
        """List all available models in the LLM runtime.
        
        Returns:
            Dict[str, Any]: Dictionary of available models and their info
        """
        try:
            models = {}
            for model in llm.get_models():
                models[model.model_id] = {
                    "id": model.model_id,
                    "provider": getattr(model, 'provider', 'unknown')
                }
            return models
        except Exception as e:
            return {"error": f"Failed to list models: {e}"}
    
    @staticmethod
    def get_default_model() -> str:
        """Get the default model name."""
        return "gpt-4o-mini"
    
    def get_runtime_info(self) -> Dict[str, Any]:
        """Get information about this runtime.
        
        Returns:
            Dict[str, Any]: Runtime information including name, version, capabilities
        """
        try:
            return {
                "name": "llm",
                "type": "llm_library",
                "current_model": self.model_name,
                "capabilities": {
                    "model_execution": True,
                    "mcp_servers": "runtime_dependent",
                    "configuration": "llm_commands",
                    "sandboxing": "runtime_dependent"
                },
                "description": "LLM library runtime adapter"
            }
        except Exception as e:
            return {"error": f"Failed to get runtime info: {e}"}
    
    @staticmethod
    def is_available() -> bool:
        """Check if this runtime is available on the system.
        
        Returns:
            bool: True if runtime is available, False otherwise
        """
        try:
            import llm
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_runtime_name() -> str:
        """Get the name of this runtime.
        
        Returns:
            str: Runtime name
        """
        return "llm"
    
    def __str__(self) -> str:
        return f"LLMRuntime(model={self.model_name})"
