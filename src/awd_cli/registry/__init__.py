"""MCP Registry module for AWD-CLI."""

from .client import SimpleRegistryClient
from .integration import RegistryIntegration

__all__ = ["SimpleRegistryClient", "RegistryIntegration"]
