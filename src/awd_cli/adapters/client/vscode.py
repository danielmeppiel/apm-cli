"""VSCode implementation of MCP client adapter.

This adapter implements the VSCode-specific handling of MCP server configuration,
following the official documentation at:
https://code.visualstudio.com/docs/copilot/chat/mcp-servers
"""

import json
import os
from pathlib import Path
from .base import MCPClientAdapter


class VSCodeClientAdapter(MCPClientAdapter):
    """VSCode implementation of MCP client adapter.
    
    This adapter handles VSCode-specific configuration for MCP servers using
    a repository-level .vscode/mcp.json file, following the format specified
    in the VSCode documentation.
    """
    
    def get_config_path(self):
        """Get the path to the VSCode MCP configuration file in the repository.
        
        Returns:
            str: Path to the .vscode/mcp.json file.
        """
        # Use the current working directory as the repository root
        repo_root = os.getcwd()
        
        # Path to .vscode/mcp.json in the repository
        vscode_dir = os.path.join(repo_root, ".vscode")
        mcp_config_path = os.path.join(vscode_dir, "mcp.json")
        
        # Create the .vscode directory if it doesn't exist
        if not os.path.exists(vscode_dir):
            os.makedirs(vscode_dir, exist_ok=True)
            
        return mcp_config_path
    
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
            
            # Update config with new values
            for key, value in config_updates.items():
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
            dict: Current VSCode MCP configuration.
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
            config = self.get_current_config()
            
            # Make sure we have the servers object
            if "servers" not in config:
                config["servers"] = {}
                
            # Create the server configuration
            # Using the format from VSCode docs:
            # https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_configuration-format
            config["servers"][server_name] = {
                "type": "stdio",
                "command": "uvx",
                "args": [f"mcp-server-{server_url}"]
            }
                
            # Update the configuration
            return self.update_config(config)
            
        except Exception as e:
            print(f"Error configuring MCP server: {e}")
            return False
