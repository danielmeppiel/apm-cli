"""VSCode implementation of MCP client adapter."""

import json
import os
from .base import MCPClientAdapter


class VSCodeClientAdapter(MCPClientAdapter):
    """VSCode implementation of MCP client adapter."""
    
    def get_config_path(self):
        """Get the path to the VSCode settings file.
        
        Returns:
            str: Path to the VSCode settings file.
        """
        # Platform-specific path to VSCode settings
        if os.name == "posix":  # macOS/Linux
            if os.path.exists(os.path.expanduser("~/Library/Application Support/Code/User/settings.json")):
                return os.path.expanduser("~/Library/Application Support/Code/User/settings.json")
            else:
                return os.path.expanduser("~/.config/Code/User/settings.json")
        elif os.name == "nt":  # Windows
            return os.path.join(os.environ["APPDATA"], "Code", "User", "settings.json")
        
        raise NotImplementedError(f"Unsupported platform: {os.name}")
    
    def update_config(self, config_updates):
        """Update the VSCode settings with new values.
        
        Args:
            config_updates (dict): Dictionary of settings to update.
        """
        config_path = self.get_config_path()
        
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}
        
        # Update config with new values
        for key, value in config_updates.items():
            config[key] = value
            
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    
    def get_current_config(self):
        """Get the current VSCode settings.
        
        Returns:
            dict: Current VSCode settings.
        """
        config_path = self.get_config_path()
        
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def configure_mcp_server(self, server_url, server_name=None, enabled=True):
        """Configure an MCP server in VSCode settings.
        
        Args:
            server_url (str): URL of the MCP server.
            server_name (str, optional): Name of the server. Defaults to None.
            enabled (bool, optional): Whether to enable the server. Defaults to True.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            config = self.get_current_config()
            
            # Create the MCP servers list if it doesn't exist
            if "mcp.servers" not in config:
                config["mcp.servers"] = []
                
            # Check if the server already exists
            server_exists = False
            for i, server in enumerate(config.get("mcp.servers", [])):
                if server.get("url") == server_url:
                    # Update existing server
                    server_exists = True
                    if server_name:
                        config["mcp.servers"][i]["name"] = server_name
                    config["mcp.servers"][i]["enabled"] = enabled
                    break
                    
            # Add new server if it doesn't exist
            if not server_exists:
                new_server = {
                    "url": server_url,
                    "enabled": enabled
                }
                if server_name:
                    new_server["name"] = server_name
                    
                config["mcp.servers"].append(new_server)
                
            # Update the configuration
            self.update_config({"mcp.servers": config.get("mcp.servers", [])})
            return True
            
        except Exception as e:
            print(f"Error configuring MCP server: {e}")
            return False
