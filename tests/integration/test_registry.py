"""Integration tests for MCP registry client."""

import os
import json
import pytest
import tempfile
from awd_cli.registry import MCPRegistryClient
from awd_cli.adapters.client.vscode import VSCodeClientAdapter


class TestMCPRegistry:
    """Test the MCP registry client with the demo registry."""
    
    def setup_method(self):
        """Set up test environment."""
        self.registry_client = MCPRegistryClient("https://demo.registry.azure-mcp.net")
        
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
        servers = self.registry_client.list_servers()
        assert isinstance(servers, list), "Server list should be a list"
        assert len(servers) > 0, "Demo registry should have some servers"
    
    def test_get_server_details(self):
        """Test getting server details for a specific server."""
        # Get the first server from the list
        servers = self.registry_client.list_servers()
        if not servers:
            pytest.skip("No servers available in the demo registry")
        
        server_name = servers[0]
        server_details = self.registry_client.get_server_details(server_name)
        
        assert server_details is not None, f"Server details for {server_name} should be retrievable"
        assert "name" in server_details, "Server details should include name"
        assert "installation" in server_details, "Server details should include installation instructions"
    
    def test_format_server_config_npm(self):
        """Test formatting server config for an npm package."""
        server_details = {
            "name": "test-npm",
            "installation": {
                "type": "npm",
                "package": "@mcp/test-server"
            }
        }
        
        config = self.registry_client.format_server_config(server_details)
        assert config["type"] == "stdio"
        assert config["command"] == "npx"
        assert "@mcp/test-server" in config["args"]
    
    def test_format_server_config_docker(self):
        """Test formatting server config for a Docker image."""
        server_details = {
            "name": "test-docker",
            "installation": {
                "type": "docker",
                "image": "mcp/test-server"
            }
        }
        
        config = self.registry_client.format_server_config(server_details)
        assert config["type"] == "stdio"
        assert config["command"] == "docker"
        assert "run" in config["args"]
        assert "--rm" in config["args"]
        assert "mcp/test-server" in config["args"]
    
    def test_format_server_config_uv(self):
        """Test formatting server config for a uv package."""
        server_details = {
            "name": "test-uv",
            "installation": {
                "type": "uv",
                "package": "mcp-server-test"
            }
        }
        
        config = self.registry_client.format_server_config(server_details)
        assert config["type"] == "stdio"
        assert config["command"] == "uvx"
        assert "mcp-server-test" in config["args"]
    
    def test_vscode_adapter_with_registry(self):
        """Test VSCode adapter with registry integration."""
        # Create a VSCode adapter
        adapter = VSCodeClientAdapter("https://demo.registry.azure-mcp.net")
        
        # Get a list of servers
        servers = self.registry_client.list_servers()
        if not servers:
            pytest.skip("No servers available in the demo registry")
        
        # Configure the first server
        server_name = servers[0]
        result = adapter.configure_mcp_server(server_name)
        
        assert result is True, f"Should be able to configure {server_name}"
        
        # Check the generated configuration file
        config_path = os.path.join(self.test_dir.name, ".vscode", "mcp.json")
        assert os.path.exists(config_path), "Configuration file should be created"
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        assert "servers" in config, "Config should have servers section"
        assert server_name in config["servers"], f"Config should include {server_name}"
        assert "type" in config["servers"][server_name], "Server config should have type"