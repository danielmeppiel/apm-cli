"""Unit tests for the VSCode client adapter."""

import os
import json
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from awd_cli.adapters.client.vscode import VSCodeClientAdapter


class TestVSCodeClientAdapter(unittest.TestCase):
    """Test cases for the VSCode client adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = os.path.join(self.temp_dir.name, "settings.json")
        
        # Create a temporary settings file
        with open(self.temp_path, "w") as f:
            json.dump({"editor.fontSize": 14}, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_get_current_config(self, mock_get_path):
        """Test getting the current configuration."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        config = adapter.get_current_config()
        self.assertEqual(config, {"editor.fontSize": 14})
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_update_config(self, mock_get_path):
        """Test updating the configuration."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.update_config({"github.copilot.enable": True})
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertEqual(
            updated_config,
            {
                "editor.fontSize": 14,
                "github.copilot.enable": True
            }
        )
        self.assertTrue(result)
        
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_update_config_nonexistent_file(self, mock_get_path):
        """Test updating configuration when file doesn't exist."""
        nonexistent_path = os.path.join(self.temp_dir.name, "nonexistent.json")
        mock_get_path.return_value = nonexistent_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.update_config({"github.copilot.enable": True})
        
        with open(nonexistent_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertEqual(
            updated_config,
            {
                "github.copilot.enable": True
            }
        )
        self.assertTrue(result)
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_configure_mcp_server(self, mock_get_path):
        """Test configuring an MCP server."""
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.configure_mcp_server(
            server_url="http://example.com/api", 
            server_name="Example Server"
        )
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertTrue(result)
        self.assertEqual(len(updated_config["mcp.servers"]), 1)
        self.assertEqual(updated_config["mcp.servers"][0]["url"], "http://example.com/api")
        self.assertEqual(updated_config["mcp.servers"][0]["name"], "Example Server")
        self.assertEqual(updated_config["mcp.servers"][0]["enabled"], True)
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_configure_mcp_server_update_existing(self, mock_get_path):
        """Test updating an existing MCP server."""
        # Create a config with an existing server
        existing_config = {
            "editor.fontSize": 14,
            "mcp.servers": [
                {
                    "url": "http://example.com/api",
                    "name": "Old Name",
                    "enabled": False
                }
            ]
        }
        
        with open(self.temp_path, "w") as f:
            json.dump(existing_config, f)
            
        mock_get_path.return_value = self.temp_path
        adapter = VSCodeClientAdapter()
        
        result = adapter.configure_mcp_server(
            server_url="http://example.com/api", 
            server_name="New Name",
            enabled=True
        )
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertTrue(result)
        self.assertEqual(len(updated_config["mcp.servers"]), 1)
        self.assertEqual(updated_config["mcp.servers"][0]["url"], "http://example.com/api")
        self.assertEqual(updated_config["mcp.servers"][0]["name"], "New Name")
        self.assertEqual(updated_config["mcp.servers"][0]["enabled"], True)
    
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
    
    @patch("sys.platform", "darwin")
    @patch("pathlib.Path.home")
    def test_get_config_path_macos(self, mock_home):
        """Test getting the config path on macOS."""
        mock_home_path = MagicMock()
        mock_home.return_value = mock_home_path
        
        adapter = VSCodeClientAdapter()
        adapter.get_config_path()
        
        # Verify the path is constructed correctly for macOS
        mock_home_path.__truediv__.assert_any_call("Library")
        mock_home_path.__truediv__.return_value.__truediv__.assert_any_call("Application Support")
    
    @patch("sys.platform", "linux")
    @patch("os.environ", {})
    @patch("pathlib.Path.home")
    @patch("pathlib.Path.exists")
    def test_get_config_path_linux(self, mock_exists, mock_home):
        """Test getting the config path on Linux."""
        mock_exists.return_value = False
        mock_home_path = MagicMock()
        mock_home.return_value = mock_home_path
        
        adapter = VSCodeClientAdapter()
        adapter.get_config_path()
        
        # Verify the path is constructed correctly for Linux
        mock_home_path.__truediv__.assert_any_call(".config")
        mock_home_path.__truediv__.return_value.__truediv__.assert_any_call("Code")
    
    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "C:\\Users\\user\\AppData\\Roaming"})
    @patch("pathlib.Path.exists")
    def test_get_config_path_windows(self, mock_exists):
        """Test getting the config path on Windows."""
        mock_exists.return_value = False
        
        adapter = VSCodeClientAdapter()
        path = adapter.get_config_path()
        
        # Verify the path is constructed correctly for Windows
        self.assertIn("AppData\\Roaming\\Code\\User\\settings.json", path.replace("/", "\\"))


if __name__ == "__main__":
    unittest.main()
