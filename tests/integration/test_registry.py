"""Integration tests for MCP registry client."""

import os
import json
import pytest
import tempfile
from awd_cli.registry.client import SimpleRegistryClient
from awd_cli.adapters.client.vscode import VSCodeClientAdapter


class TestMCPRegistry:
    """Test the MCP registry client with the demo registry."""
    
    def setup_method(self):
        """Set up test environment."""
        self.registry_client = SimpleRegistryClient("https://demo.registry.azure-mcp.net")
        
        # Create a temporary directory for tests
        self.test_dir = tempfile.TemporaryDirectory()
        os.chdir(self.test_dir.name)
        
        # Create .vscode directory
        os.makedirs(os.path.join(self.test_dir.name, ".vscode"), exist_ok=True)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.test_dir.cleanup()
    
    def test_list_servers(self):
        """Test listing servers from the registry."""
        servers, _ = self.registry_client.list_servers()
        assert isinstance(servers, list), "Server list should be a list"
        assert len(servers) > 0, "Demo registry should have some servers"
    
    def test_get_server_info(self):
        """Test getting server details for a specific server."""
        # Get the first server from the list
        servers, _ = self.registry_client.list_servers()
        if not servers:
            pytest.skip("No servers available in the demo registry")
        
        server_id = servers[0]["id"]
        server_info = self.registry_client.get_server_info(server_id)
        
        assert server_info is not None, f"Server info for {server_id} should be retrievable"
        assert "name" in server_info, "Server info should include name"
        assert "id" in server_info, "Server info should include id"
    
    def test_vscode_adapter_with_registry(self):
        """Test VSCode adapter with registry integration."""
        # Create a VSCode adapter
        adapter = VSCodeClientAdapter("https://demo.registry.azure-mcp.net")
        
        # Get a list of servers
        servers, _ = self.registry_client.list_servers()
        if not servers:
            pytest.skip("No servers available in the demo registry")
        
        # Configure the first server
        server_id = servers[0]["id"]
        result = adapter.configure_mcp_server(server_id)
        
        assert result is True, f"Should be able to configure server {server_id}"
        
        # Check the generated configuration file
        config_path = os.path.join(self.test_dir.name, ".vscode", "mcp.json")
        assert os.path.exists(config_path), "Configuration file should be created"
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        assert "servers" in config, "Config should have servers section"
        
        # The server name in the config will be the server_id unless a name was specified
        assert server_id in config["servers"], f"Config should include {server_id}"
        assert "type" in config["servers"][server_id], "Server config should have type"