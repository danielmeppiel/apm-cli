"""Unit tests for the MCP registry integration."""

import unittest
from unittest import mock
from awd_cli.registry.integration import RegistryIntegration


class TestRegistryIntegration(unittest.TestCase):
    """Test cases for the MCP registry integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = RegistryIntegration()
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.list_servers')
    def test_list_available_packages(self, mock_list_servers):
        """Test listing available packages."""
        # Mock response
        mock_list_servers.return_value = [
            {"name": "server1", "description": "Description 1"},
            {"name": "server2", "description": "Description 2"}
        ]
        
        # Call the method
        packages = self.integration.list_available_packages()
        
        # Assertions
        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0]["name"], "server1")
        self.assertEqual(packages[1]["name"], "server2")
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.search_servers')
    def test_search_packages(self, mock_search_servers):
        """Test searching for packages."""
        # Mock response
        mock_search_servers.return_value = [
            {"name": "test-server", "description": "Test description"}
        ]
        
        # Call the method
        results = self.integration.search_packages("test")
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test-server")
        mock_search_servers.assert_called_once_with("test")
        
    @mock.patch('awd_cli.registry.integration.RegistryIntegration._get_server_id_by_name')
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.get_server_info')
    def test_get_package_info(self, mock_get_server_info, mock_get_server_id):
        """Test getting package information."""
        # Mock responses
        mock_get_server_id.return_value = "test-server-id"
        mock_get_server_info.return_value = {
            "name": "test-server",
            "description": "Test server description",
            "version_detail": {
                "version": "1.0.0",
                "release_date": "2025-05-16T19:13:21Z",
                "is_latest": True
            }
        }
        
        # Call the method
        package_info = self.integration.get_package_info("test-server")
        
        # Assertions
        self.assertEqual(package_info["name"], "test-server")
        self.assertEqual(len(package_info["versions"]), 1)
        self.assertEqual(package_info["versions"][0]["version"], "1.0.0")
        mock_get_server_info.assert_called_once_with("test-server-id")
        
    @mock.patch('awd_cli.registry.integration.RegistryIntegration.get_package_info')
    def test_get_latest_version(self, mock_get_package_info):
        """Test getting the latest version of a package."""
        # Mock response
        mock_get_package_info.return_value = {
            "name": "test-server",
            "versions": [
                {"version": "1.0.0"},
                {"version": "1.1.0"}
            ]
        }
        
        # Call the method
        version = self.integration.get_latest_version("test-server")
        
        # Assertions
        self.assertEqual(version, "1.1.0")
        mock_get_package_info.assert_called_once_with("test-server")
        
        # Test with empty versions
        mock_get_package_info.return_value = {
            "name": "test-server",
            "versions": []
        }
        
        # Call the method and assert it raises a ValueError
        with self.assertRaises(ValueError):
            self.integration.get_latest_version("test-server")


if __name__ == "__main__":
    unittest.main()