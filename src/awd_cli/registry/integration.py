"""Integration module for connecting registry client with package manager."""

from typing import Dict, List, Any, Optional
from .client import SimpleRegistryClient


class RegistryIntegration:
    """Integration class for connecting registry discovery to package manager."""

    def __init__(self, registry_url: Optional[str] = None):
        """Initialize the registry integration.

        Args:
            registry_url (str, optional): URL of the MCP registry.
                If not provided, uses the MCP_REGISTRY_URL environment variable
                or falls back to the default demo registry.
        """
        self.client = SimpleRegistryClient(registry_url)

    def list_available_packages(self) -> List[Dict[str, Any]]:
        """List all available packages in the registry.

        Returns:
            List[Dict[str, Any]]: List of package metadata dictionaries.
        """
        return self.client.list_packages()

    def search_packages(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages in the registry.

        Args:
            query (str): Search query string.

        Returns:
            List[Dict[str, Any]]: List of matching package metadata dictionaries.
        """
        return self.client.search_packages(query)

    def get_package_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a specific package.

        Args:
            name (str): Name of the package.

        Returns:
            Dict[str, Any]: Package metadata dictionary.
        """
        return self.client.get_package_info(name)

    def get_latest_version(self, name: str) -> str:
        """Get the latest version of a package.

        Args:
            name (str): Name of the package.

        Returns:
            str: Latest version string.

        Raises:
            ValueError: If the package has no versions.
        """
        package_info = self.get_package_info(name)
        versions = package_info.get("versions", [])
        
        if not versions:
            raise ValueError(f"Package '{name}' has no versions")
            
        # Return the latest version (assuming versions are sorted)
        return versions[-1].get("version", "latest")