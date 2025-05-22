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
        servers = self.client.list_servers()
        # Transform server data to package format for backward compatibility
        return [self._server_to_package(server) for server in servers]

    def search_packages(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages in the registry.

        Args:
            query (str): Search query string.

        Returns:
            List[Dict[str, Any]]: List of matching package metadata dictionaries.
        """
        servers = self.client.search_servers(query)
        # Transform server data to package format for backward compatibility
        return [self._server_to_package(server) for server in servers]

    def get_package_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a specific package.

        Args:
            name (str): Name of the package.

        Returns:
            Dict[str, Any]: Package metadata dictionary.
        """
        # Note: In a real implementation, we might need to search for the server
        # by name first to get its ID, since the API uses IDs
        server_id = self._get_server_id_by_name(name)
        server_info = self.client.get_server_info(server_id)
        return self._server_to_package_detail(server_info)

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
    
    def _get_server_id_by_name(self, name: str) -> str:
        """Get server ID by name.
        
        In a real implementation, this would search the registry for a server by name.
        For simplicity, we're assuming the name is the ID for now.
        
        Args:
            name (str): Server name.
            
        Returns:
            str: Server ID.
        """
        # Simplified implementation - in real code, we would search for the server first
        return name
    
    def _server_to_package(self, server: Dict[str, Any]) -> Dict[str, Any]:
        """Convert server data format to package format for compatibility.
        
        Args:
            server (Dict[str, Any]): Server data from registry.
            
        Returns:
            Dict[str, Any]: Package formatted data.
        """
        return {
            "name": server.get("name", "Unknown"),
            "description": server.get("description", "No description available"),
            # Add other fields as needed for compatibility
        }
    
    def _server_to_package_detail(self, server: Dict[str, Any]) -> Dict[str, Any]:
        """Convert detailed server data to package detail format.
        
        Args:
            server (Dict[str, Any]): Server data from registry.
            
        Returns:
            Dict[str, Any]: Package detail formatted data.
        """
        # Extract version information from server data
        version_info = server.get("version_detail", {})
        versions = []
        
        if version_info:
            versions.append({
                "version": version_info.get("version", "latest"),
                # Add other version fields as needed
            })
        
        return {
            "name": server.get("name", "Unknown"),
            "description": server.get("description", "No description available"),
            "versions": versions,
            # Add other fields as needed for compatibility
        }