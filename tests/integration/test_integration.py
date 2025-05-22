"""Integration tests for AWD-CLI."""

import os
import json
import tempfile
import unittest
from unittest.mock import patch
from awd_cli.factory import ClientFactory, PackageManagerFactory
from awd_cli.core.operations import install_package


class TestIntegration(unittest.TestCase):
    """Integration test cases for AWD-CLI."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = os.path.join(self.temp_dir.name, "settings.json")
        
        # Create a temporary settings file
        with open(self.temp_path, "w") as f:
            json.dump({}, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    @patch("awd_cli.adapters.client.vscode.VSCodeClientAdapter.get_config_path")
    def test_install_package_integration(self, mock_get_path):
        """Test installing a package and updating client configuration."""
        mock_get_path.return_value = self.temp_path
        
        # Install a package
        result = install_package("vscode", "test-package", "1.0.0")
        self.assertTrue(result)
        
        # Verify the client configuration was updated
        with open(self.temp_path, "r") as f:
            config = json.load(f)
        
        self.assertTrue(config.get("mcp.package.test-package.enabled", False))


if __name__ == "__main__":
    unittest.main()
