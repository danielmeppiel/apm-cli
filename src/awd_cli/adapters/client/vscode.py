"""VSCode implementation of MCP client adapter.

This adapter implements the VSCode-specific handling of MCP server configuration,
following the official documentation at:
https://code.visualstudio.com/docs/copilot/chat/mcp-servers
"""

import json
import os
from pathlib import Path
from .base import MCPClientAdapter
from ...registry.client import SimpleRegistryClient
from ...registry.integration import RegistryIntegration


class VSCodeClientAdapter(MCPClientAdapter):
    """VSCode implementation of MCP client adapter.
    
    This adapter handles VSCode-specific configuration for MCP servers using
    a repository-level .vscode/mcp.json file, following the format specified
    in the VSCode documentation.
    """
    
    def __init__(self, registry_url=None):
        """Initialize the VSCode client adapter.
        
        Args:
            registry_url (str, optional): URL of the MCP registry.
                If not provided, uses the MCP_REGISTRY_URL environment variable
                or falls back to the default demo registry.
        """
        self.registry_client = SimpleRegistryClient(registry_url)
        self.registry_integration = RegistryIntegration(registry_url)
    
    def get_config_path(self):
        """Get the path to the VSCode MCP configuration file in the repository.
        
        Returns:
            str: Path to the .vscode/mcp.json file.
        """
        # Use the current working directory as the repository root
        repo_root = Path(os.getcwd())
        
        # Path to .vscode/mcp.json in the repository
        vscode_dir = repo_root / ".vscode"
        mcp_config_path = vscode_dir / "mcp.json"
        
        # Create the .vscode directory if it doesn't exist
        try:
            if not vscode_dir.exists():
                vscode_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create .vscode directory: {e}")
            
        return str(mcp_config_path)
    
    def update_config(self, config_updates):
        """Update the VSCode MCP configuration with new values.
        
        Args:
            config_updates (dict): Dictionary of settings to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        config_path = self.get_config_path()
        
        try:
            # Read existing config or create a new one
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
            
            # Update config with new values or remove entries set to None
            for key, value in config_updates.items():
                if value is None:
                    # Remove the entry if it exists
                    if key in config:
                        del config[key]
                else:
                    config[key] = value
                
            # Write the updated config
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error updating VSCode MCP configuration: {e}")
            return False
    
    def get_current_config(self):
        """Get the current VSCode MCP configuration.
        
        Returns:
            dict: Current VSCode MCP configuration from the local .vscode/mcp.json file.
        """
        config_path = self.get_config_path()
        
        try:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
        except Exception as e:
            print(f"Error reading VSCode MCP configuration: {e}")
            return {}
    
    def configure_mcp_server(self, server_url, server_name=None, enabled=True):
        """Configure an MCP server in VSCode configuration.
        
        This method follows the VSCode documentation for MCP server configuration format:
        https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_configuration-format
        
        Args:
            server_url (str): URL or identifier of the MCP server.
            server_name (str, optional): Name of the server. Defaults to None.
            enabled (bool, optional): Ignored parameter, kept for API compatibility.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not server_url:
            print("Error: server_url cannot be empty")
            return False
            
        if not server_name:
            server_name = server_url
            
        try:
            # Use enhanced lookup with multiple strategies
            server_info = self.registry_client.find_server_by_reference(server_url)
            
            # Fail if server is not found in registry - security requirement
            if not server_info:
                raise ValueError(f"Failed to retrieve server details for '{server_url}'. Server not found in registry.")
            
            # Format server configuration and get input variables if any
            server_config, input_vars = self._format_server_config(server_info)
            
            config = self.get_current_config()
            
            # Make sure we have the servers object
            if "servers" not in config:
                config["servers"] = {}
                
            # Add input variables if any
            if input_vars:
                if "inputs" not in config:
                    config["inputs"] = []
                # Merge with existing inputs, avoiding duplicates by id
                existing_input_ids = [input_var.get("id") for input_var in config.get("inputs", [])]
                for input_var in input_vars:
                    if input_var.get("id") not in existing_input_ids:
                        config["inputs"].append(input_var)
                
            # Add the server configuration
            config["servers"][server_name] = server_config
                
            # Update the configuration
            return self.update_config(config)
            
        except ValueError as ve:
            # Re-raise ValueError to indicate missing server details
            raise ve
        except Exception as e:
            print(f"Error configuring MCP server: {e}")
            return False
    
    def _format_server_config(self, server_info):
        """Format server details into VSCode mcp.json compatible format.
        
        Args:
            server_info (dict): Server information from registry.
            
        Returns:
            tuple: (server_config, input_vars) where:
                - server_config is the formatted server configuration for mcp.json
                - input_vars is a list of input variable definitions
        """
        # Initialize the base config structure
        server_config = {}
        input_vars = []
        
        # Check for packages information
        if "packages" in server_info and server_info["packages"]:
            package = server_info["packages"][0]
            runtime_hint = package.get("runtime_hint", "")
            
            # Handle npm packages
            if runtime_hint == "npx" or "npm" in package.get("registry_name", "").lower():
                # Get args directly from runtime_arguments
                args = []
                if "runtime_arguments" in package and package["runtime_arguments"]:
                    for arg in package["runtime_arguments"]:
                        if arg.get("is_required", False) and arg.get("value_hint"):
                            args.append(arg.get("value_hint"))
                
                # Fallback if no runtime_arguments are provided
                if not args and package.get("name"):
                    args = [package.get("name")]
                
                server_config = {
                    "type": "stdio",
                    "command": "npx",
                    "args": args
                }
            
            # Handle docker packages
            elif runtime_hint == "docker":
                # Get args directly from runtime_arguments
                args = []
                if "runtime_arguments" in package and package["runtime_arguments"]:
                    for arg in package["runtime_arguments"]:
                        if arg.get("is_required", False) and arg.get("value_hint"):
                            args.append(arg.get("value_hint"))
                
                # Fallback if no runtime_arguments are provided - use standard docker run command
                if not args:
                    args = ["run", "-i", "--rm", package.get("name")]
                
                server_config = {
                    "type": "stdio",
                    "command": "docker",
                    "args": args
                }
            
            # Handle Python packages
            elif runtime_hint in ["uvx", "pip", "python"] or "python" in runtime_hint or package.get("registry_name", "").lower() == "pypi":
                # Determine the command based on runtime_hint
                if runtime_hint == "uvx":
                    command = "uvx"
                elif "python" in runtime_hint:
                    # Use the specified Python path if it's a full path, otherwise default to python3
                    command = "python3" if runtime_hint in ["python", "pip"] else runtime_hint
                else:
                    command = "python3"
                
                # Get args directly from runtime_arguments
                args = []
                if "runtime_arguments" in package and package["runtime_arguments"]:
                    for arg in package["runtime_arguments"]:
                        if arg.get("is_required", False) and arg.get("value_hint"):
                            args.append(arg.get("value_hint"))
                
                # Fallback if no runtime_arguments are provided
                if not args:
                    if runtime_hint == "uvx":
                        module_name = package.get("name", "").replace("mcp-server-", "")
                        args = [f"mcp-server-{module_name}"]
                    else:
                        module_name = package.get("name", "").replace("mcp-server-", "").replace("-", "_")
                        args = ["-m", f"mcp_server_{module_name}"]
                
                server_config = {
                    "type": "stdio",
                    "command": command,
                    "args": args
                }
            
            # Add environment variables if present
            if "environment_variables" in package and package["environment_variables"]:
                server_config["env"] = {}
                for env_var in package["environment_variables"]:
                    if "name" in env_var:
                        # Convert variable name to lowercase and replace underscores with hyphens for VS Code convention
                        input_var_name = env_var["name"].lower().replace("_", "-")
                        
                        # Create the input variable reference
                        server_config["env"][env_var["name"]] = f"${{input:{input_var_name}}}"
                        
                        # Create the input variable definition
                        input_var_def = {
                            "type": "promptString",
                            "id": input_var_name,
                            "description": env_var.get("description", f"{env_var['name']} for MCP server"),
                            "password": True  # Default to True for security
                        }
                        input_vars.append(input_var_def)
            
        # If no server config was created from packages, check for other server types
        if not server_config:
            # Check for SSE endpoints
            if "sse_endpoint" in server_info:
                server_config = {
                    "type": "sse",
                    "url": server_info["sse_endpoint"],
                    "headers": server_info.get("sse_headers", {})
                }
            # Default fallback
            else:
                server_config = {
                    "type": "stdio",
                    "command": "uvx",
                    "args": [f"mcp-server-{server_info.get('name', '')}"]
                }
        
        return server_config, input_vars
