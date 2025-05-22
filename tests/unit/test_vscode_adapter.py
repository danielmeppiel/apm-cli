"""Unit tests for the VSCode client adapter."""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from awd_cli.adapters.client.vscode import VSCodeClientAdapter


class TestVSCodeClientAdapter(unittest.TestCase):
    """Test cases for the VSCode client adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vscode_dir = os.path.join(self.temp_dir.name, ".vscode")
        os.makedirs(self.vscode_dir, exist_ok=True)
        self.temp_path = os.path.join(self.vscode_dir, "mcp.json")
        
        # Create a temporary MCP configuration file
        with open(self.temp_path, "w") as f:
            json.dump({"servers": {}}, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_get_current_config(self, mock_get_path):
        """Test getting the current configuration."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        config = adapter.get_current_config()
        self.assertEqual(config, {"servers": {}})
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_update_config(self, mock_get_path):
        """Test updating the configuration."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        new_config = {
            "servers": {
                "test-server": {
                    "type": "stdio",
                    "command": "uvx",
                    "args": ["mcp-server-test"]
                }
            }
        }
        
        result = adapter.update_config(new_config)
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertEqual(updated_config, new_config)
        self.assertTrue(result)
        
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_update_config_nonexistent_file(self, mock_get_path):
        """Test updating configuration when file doesn't exist."""
        nonexistent_path = os.path.join(self.vscode_dir, "nonexistent.json")
        mock_get_path.return_value = nonexistent_path
        adapter = VSCodeClientAdapter()
        
        new_config = {
            "servers": {
                "test-server": {
                    "type": "stdio",
                    "command": "uvx",
                    "args": ["mcp-server-test"]
                }
            }
        }
        
        result = adapter.update_config(new_config)
        
        with open(nonexistent_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertEqual(updated_config, new_config)
        self.assertTrue(result)
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_configure_mcp_server(self, mock_get_path):
        """Test configuring an MCP server."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.configure_mcp_server(
            server_url="fetch", 
            server_name="fetch"
        )
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertTrue(result)
        self.assertIn("servers", updated_config)
        self.assertIn("fetch", updated_config["servers"])
        self.assertEqual(updated_config["servers"]["fetch"]["type"], "stdio")
        self.assertEqual(updated_config["servers"]["fetch"]["command"], "uvx")
        self.assertEqual(updated_config["servers"]["fetch"]["args"], ["mcp-server-fetch"])
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_configure_mcp_server_update_existing(self, mock_get_path):
        """Test updating an existing MCP server."""
        # Create a config with an existing server
        existing_config = {
            "servers": {
                "fetch": {
                    "type": "stdio",
                    "command": "docker",
                    "args": ["run", "-i", "--rm", "mcp/fetch"]
                }
            }
        }
        
        with open(self.temp_path, "w") as f:
            json.dump(existing_config, f)
            
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.configure_mcp_server(
            server_url="fetch", 
            server_name="fetch"
        )
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertTrue(result)
        self.assertIn("fetch", updated_config["servers"])
        self.assertEqual(updated_config["servers"]["fetch"]["type"], "stdio")
        self.assertEqual(updated_config["servers"]["fetch"]["command"], "uvx")
        self.assertEqual(updated_config["servers"]["fetch"]["args"], ["mcp-server-fetch"])
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_configure_mcp_server_empty_url(self, mock_get_path):
        """Test configuring an MCP server with empty URL."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.configure_mcp_server(
            server_url="", 
            server_name="Example Server"
        )
        
        self.assertFalse(result)
    
    @patch("os.getcwd")
    def test_get_config_path_repository(self, mock_getcwd):
        """Test getting the config path in the repository."""
        mock_getcwd.return_value = self.temp_dir.name
        
        adapter = VSCodeClientAdapter()
        path = adapter.get_config_path()
        
        # Verify the path is constructed correctly for repository
        self.assertEqual(path, os.path.join(self.temp_dir.name, ".vscode", "mcp.json"))


if __name__ == "__main__":
    unittest.main()
