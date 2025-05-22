"""MCP Registry Client for AWD-CLI.

This module provides functionality to interact with MCP registries,
fetching server definitions and other metadata.
"""

import json
import urllib.request
import urllib.error


class MCPRegistryClient:
    """Client for interacting with MCP registries."""
    
    def __init__(self, registry_url="https://demo.registry.azure-mcp.net"):
        """Initialize the registry client.
        
        Args:
            registry_url (str, optional): URL of the MCP registry. 
                Defaults to the demo registry.
        """
        self.registry_url = registry_url.rstrip('/')
    
    def get_server_details(self, server_name):
        """Get details for a specific server from the registry.
        
        Args:
            server_name (str): Name of the server to fetch details for.
            
        Returns:
            dict: Server details or None if not found or error occurred.
        """
        try:
            url = f"{self.registry_url}/servers/{server_name}"
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                return None
        except urllib.error.URLError as e:
            print(f"Error connecting to registry: {e}")
            return None
        except Exception as e:
            print(f"Error fetching server details: {e}")
            return None
    
    def list_servers(self):
        """List all available servers in the registry.
        
        Returns:
            list: List of server names or empty list if error occurred.
        """
        try:
            url = f"{self.registry_url}/servers"
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                return []
        except urllib.error.URLError as e:
            print(f"Error connecting to registry: {e}")
            return []
        except Exception as e:
            print(f"Error listing servers: {e}")
            return []
    
    def format_server_config(self, server_details):
        """Format server details into VSCode mcp.json compatible format.
        
        Args:
            server_details (dict): Server details from registry.
            
        Returns:
            dict: Formatted server configuration for mcp.json.
        """
        if not server_details or "installation" not in server_details:
            return None
        
        installation = server_details["installation"]
        install_type = installation.get("type")
        
        # Handle npm packages
        if install_type == "npm":
            return {
                "type": "stdio",
                "command": "npx",
                "args": [installation.get("package")]
            }
        
        # Handle docker packages
        elif install_type == "docker":
            return {
                "type": "stdio",
                "command": "docker",
                "args": ["run", "-i", "--rm", installation.get("image")]
            }
        
        # Handle Python packages
        elif install_type == "pip" or install_type == "uv":
            command = "uvx" if install_type == "uv" else "python3"
            module = installation.get("package", "").replace("mcp-server-", "")
            return {
                "type": "stdio",
                "command": command,
                "args": [f"mcp-server-{module}"] if install_type == "uv" else ["-m", f"mcp_server_{module}"]
            }
        
        # Handle local executables
        elif install_type == "local":
            return {
                "type": "stdio",
                "command": installation.get("path"),
                "args": installation.get("args", [])
            }
        
        # Handle SSE (Server-Sent Events) endpoints
        elif install_type == "sse":
            return {
                "type": "sse",
                "url": installation.get("url"),
                "headers": installation.get("headers", {})
            }
        
        # Default fallback
        return {
            "type": "stdio",
            "command": "uvx",
            "args": [f"mcp-server-{server_details.get('name', '')}"]
        }