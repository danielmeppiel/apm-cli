"""Unit tests for the MCP registry client."""

import unittest
import os
from unittest import mock
from awd_cli.registry.client import SimpleRegistryClient


class TestSimpleRegistryClient(unittest.TestCase):
    """Test cases for the MCP registry client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = SimpleRegistryClient()
        
    @mock.patch('requests.Session.get')
    def test_list_packages(self, mock_get):
        """Test listing packages from the registry."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "packages": [
                {"name": "package1", "description": "Description 1"},
                {"name": "package2", "description": "Description 2"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        packages = self.client.list_packages()
        
        # Assertions
        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0]["name"], "package1")
        self.assertEqual(packages[1]["name"], "package2")
        mock_get.assert_called_once_with(f"{self.client.registry_url}/v1/packages")
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.list_packages')
    def test_search_packages(self, mock_list_packages):
        """Test searching for packages in the registry."""
        # Mock response
        mock_list_packages.return_value = [
            {"name": "test-package", "description": "Test description"},
            {"name": "package2", "description": "Another test"}
        ]
        
        # Call the method with a query that should match both packages
        results = self.client.search_packages("test")
        
        # Assertions
        self.assertEqual(len(results), 2)
        
        # Call the method with a query that should match only one package
        results = self.client.search_packages("another")
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "package2")
        
    @mock.patch('requests.Session.get')
    def test_get_package_info(self, mock_get):
        """Test getting package information from the registry."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "name": "test-package",
            "description": "Test package description",
            "versions": [
                {"version": "1.0.0"},
                {"version": "1.1.0"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        package_info = self.client.get_package_info("test-package")
        
        # Assertions
        self.assertEqual(package_info["name"], "test-package")
        self.assertEqual(len(package_info["versions"]), 2)
        mock_get.assert_called_once_with(f"{self.client.registry_url}/v1/packages/test-package")
        
    @mock.patch.dict(os.environ, {"MCP_REGISTRY_URL": "https://custom-registry.example.com"})
    def test_environment_variable_override(self):
        """Test overriding the registry URL with an environment variable."""
        client = SimpleRegistryClient()
        self.assertEqual(client.registry_url, "https://custom-registry.example.com")
        
        # Test explicit URL takes precedence over environment variable
        client = SimpleRegistryClient("https://explicit-url.example.com")
        self.assertEqual(client.registry_url, "https://explicit-url.example.com")


if __name__ == "__main__":
    unittest.main()