"""Simple MCP Registry client for package discovery."""

import os
import requests
from typing import Dict, List, Optional, Any


class SimpleRegistryClient:
    """Simple client for querying MCP registries for package discovery."""

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

    def list_packages(self) -> List[Dict[str, Any]]:
        """List all available packages in the registry.

        Returns:
            List[Dict[str, Any]]: List of package metadata dictionaries.
        
        Raises:
            requests.RequestException: If the request fails.
        """
        response = self.session.get(f"{self.registry_url}/v1/packages")
        response.raise_for_status()
        return response.json().get("packages", [])

    def search_packages(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages in the registry.

        Args:
            query (str): Search query string.

        Returns:
            List[Dict[str, Any]]: List of matching package metadata dictionaries.
        
        Raises:
            requests.RequestException: If the request fails.
        """
        all_packages = self.list_packages()
        
        # Simple client-side filtering by name or description
        return [
            pkg for pkg in all_packages 
            if query.lower() in pkg.get("name", "").lower() 
            or query.lower() in pkg.get("description", "").lower()
        ]

    def get_package_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a specific package.

        Args:
            name (str): Name of the package.

        Returns:
            Dict[str, Any]: Package metadata dictionary.
        
        Raises:
            requests.RequestException: If the request fails.
            ValueError: If the package is not found.
        """
        response = self.session.get(f"{self.registry_url}/v1/packages/{name}")
        response.raise_for_status()
        package_info = response.json()
        
        if not package_info:
            raise ValueError(f"Package '{name}' not found in registry")
            
        return package_info