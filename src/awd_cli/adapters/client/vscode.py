"""VSCode implementation of MCP client adapter.

This adapter implements the VSCode-specific handling of MCP server configuration,
following the official documentation at:
https://code.visualstudio.com/docs/copilot/chat/mcp-servers
"""

import json
import os
import platform
import sys
from pathlib import Path
from .base import MCPClientAdapter


class VSCodeClientAdapter(MCPClientAdapter):
    """VSCode implementation of MCP client adapter.
    
    This adapter handles VSCode-specific configuration for MCP servers,
    properly handling OS-specific paths to settings.json.
    """
    
    def get_config_path(self):
        """Get the path to the VSCode settings file.
        
        Returns:
            str: Path to the VSCode settings file.
            
        Raises:
            NotImplementedError: If the platform is not supported.
        """
        # Get user home directory
        home = Path.home()
        
        # Platform-specific path to VSCode settings
        if sys.platform == "darwin":  # macOS
            settings_path = home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        elif sys.platform == "linux":  # Linux
            # Try the XDG config path first
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                settings_path = Path(xdg_config) / "Code" / "User" / "settings.json"
            else:
                settings_path = home / ".config" / "Code" / "User" / "settings.json"
                
            # Check for Flatpak installation
            flatpak_path = home / ".var" / "app" / "com.visualstudio.code" / "config" / "Code" / "User" / "settings.json"
            if flatpak_path.exists():
                settings_path = flatpak_path
                
            # Check for Snap installation
            snap_path = home / "snap" / "code" / "current" / ".config" / "Code" / "User" / "settings.json"
            if snap_path.exists():
                settings_path = snap_path
        elif sys.platform == "win32":  # Windows
            appdata = os.environ.get("APPDATA")
            if not appdata:
                raise ValueError("APPDATA environment variable not found")
                
            settings_path = Path(appdata) / "Code" / "User" / "settings.json"
            
            # Check for Windows Store installation
            store_path = home / "AppData" / "Local" / "Packages" / "Microsoft.VisualStudioCode_8wekyb3d8bbwe" / "LocalState" / "settings.json"
            if store_path.exists():
                settings_path = store_path
        else:
            raise NotImplementedError(f"Unsupported platform: {sys.platform}")
            
        # Create the directory if it doesn't exist
        os.makedirs(settings_path.parent, exist_ok=True)
            
        return str(settings_path)
    
    def update_config(self, config_updates):
        """Update the VSCode settings with new values.
        
        Args:
            config_updates (dict): Dictionary of settings to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        config_path = self.get_config_path()
        
        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
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
            print(f"Error updating VSCode configuration: {e}")
            return False
    
    def get_current_config(self):
        """Get the current VSCode settings.
        
        Returns:
            dict: Current VSCode settings.
        """
        config_path = self.get_config_path()
        
        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
        except Exception as e:
            print(f"Error reading VSCode configuration: {e}")
            return {}
    
    def configure_mcp_server(self, server_url, server_name=None, enabled=True):
        """Configure an MCP server in VSCode settings according to official documentation.
        
        This method follows the VSCode documentation for MCP server configuration
        at https://code.visualstudio.com/docs/copilot/chat/mcp-servers
        
        Args:
            server_url (str): URL of the MCP server.
            server_name (str, optional): Name of the server. Defaults to None.
            enabled (bool, optional): Whether to enable the server. Defaults to True.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not server_url:
            print("Error: server_url cannot be empty")
            return False
            
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
            return self.update_config({"mcp.servers": config.get("mcp.servers", [])})
            
        except Exception as e:
            print(f"Error configuring MCP server: {e}")
            return False
