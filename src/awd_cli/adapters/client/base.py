"""Base adapter interface for MCP clients."""

from abc import ABC, abstractmethod


class MCPClientAdapter(ABC):
    """Base adapter for MCP clients."""

    @abstractmethod
    def get_config_path(self):
        """Get the path to the MCP configuration file."""
        pass

    @abstractmethod
    def update_config(self, config_updates):
        """Update the MCP configuration."""
        pass

    @abstractmethod
    def get_current_config(self):
        """Get the current MCP configuration."""
        pass

    @abstractmethod
    def configure_mcp_server(self, server_url, server_name=None, enabled=True):
        """Configure an MCP server in the client configuration.

        Args:
            server_url (str): URL of the MCP server.
            server_name (str, optional): Name of the server. Defaults to None.
            enabled (bool, optional): Whether to enable the server. Defaults to True.

        Returns:
            bool: True if successful, False otherwise.
        """
        pass
