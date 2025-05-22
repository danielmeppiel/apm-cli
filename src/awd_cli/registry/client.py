"""Simple MCP Registry client for server discovery."""

import os
import requests
from typing import Dict, List, Optional, Any


class SimpleRegistryClient:
    """Simple client for querying MCP registries for server discovery."""

    def __init__(self, registry_url: Optional[str] = None):
        """Initialize the registry client.

        Args:
            registry_url (str, optional): URL of the MCP registry.
                If not provided, uses the MCP_REGISTRY_URL environment variable
                or falls back to the default demo registry.
        """
        self.registry_url = registry_url or os.environ.get(
            "MCP_REGISTRY_URL", "https://demo.registry.azure-mcp.net"
        )
        self.session = requests.Session()

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all available servers in the registry.

        Returns:
            List[Dict[str, Any]]: List of server metadata dictionaries.
        
        Raises:
            requests.RequestException: If the request fails.
        """
        response = self.session.get(f"{self.registry_url}/v0/servers")
        response.raise_for_status()
        return response.json().get("servers", [])

    def search_servers(self, query: str) -> List[Dict[str, Any]]:
        """Search for servers in the registry.

        Args:
            query (str): Search query string.

        Returns:
            List[Dict[str, Any]]: List of matching server metadata dictionaries.
        
        Raises:
            requests.RequestException: If the request fails.
        """
        all_servers = self.list_servers()
        
        # Simple client-side filtering by name or description
        return [
            server for server in all_servers 
            if query.lower() in server.get("name", "").lower() 
            or query.lower() in server.get("description", "").lower()
        ]

    def get_server_info(self, server_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific server.

        Args:
            server_id (str): ID of the server.

        Returns:
            Dict[str, Any]: Server metadata dictionary.
        
        Raises:
            requests.RequestException: If the request fails.
            ValueError: If the server is not found.
        """
        response = self.session.get(f"{self.registry_url}/v0/servers/{server_id}")
        response.raise_for_status()
        server_info = response.json()
        
        if not server_info:
            raise ValueError(f"Server '{server_id}' not found in registry")
            
        return server_info