"""Unit tests for the VSCode client adapter."""

import os
import json
import tempfile
import unittest
from unittest.mock import patch
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
        
        adapter.update_config({"github.copilot.enable": True})
        
        with open(self.temp_path, "r") as f:
            updated_config = json.load(f)
        
        self.assertEqual(
            updated_config,
            {
                "editor.fontSize": 14,
                "github.copilot.enable": True
            }
        )


if __name__ == "__main__":
    unittest.main()
