"""Unit tests for the MCP registry integration."""

import unittest
from unittest import mock
import requests
from apm_cli.registry.integration import RegistryIntegration


class TestRegistryIntegration(unittest.TestCase):
    """Test cases for the MCP registry integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = RegistryIntegration()
        
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.list_servers')
    def test_list_available_packages(self, mock_list_servers):
        """Test listing available packages."""
        # Mock response
        mock_list_servers.return_value = (
            [
                {
                    "id": "123",
                    "name": "server1",
                    "description": "Description 1",
                    "repository": {"url": "https://github.com/test/server1"}
                },
                {
                    "id": "456",
                    "name": "server2",
                    "description": "Description 2",
                    "repository": {"url": "https://github.com/test/server2"}
                }
            ],
            None
        )
        
        # Call the method
        packages = self.integration.list_available_packages()
        
        # Assertions
        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0]["name"], "server1")
        self.assertEqual(packages[0]["id"], "123")
        self.assertEqual(packages[0]["repository"]["url"], "https://github.com/test/server1")
        self.assertEqual(packages[1]["name"], "server2")
        
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.search_servers')
    def test_search_packages(self, mock_search_servers):
        """Test searching for packages."""
        # Mock response
        mock_search_servers.return_value = [
            {
                "id": "123",
                "name": "test-server",
                "description": "Test description"
            }
        ]
        
        # Call the method
        results = self.integration.search_packages("test")
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test-server")
        mock_search_servers.assert_called_once_with("test")
        
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.get_server_info')
    def test_get_package_info(self, mock_get_server_info):
        """Test getting package information by ID."""
        # Mock response
        mock_get_server_info.return_value = {
            "id": "123",
            "name": "test-server",
            "description": "Test server description",
            "repository": {
                "url": "https://github.com/test/test-server",
                "source": "github"
            },
            "version_detail": {
                "version": "1.0.0",
                "release_date": "2025-05-16T19:13:21Z",
                "is_latest": True
            },
            "packages": [
                {
                    "registry_name": "npm",
                    "name": "test-package",
                    "version": "1.0.0"
                }
            ]
        }
        
        # Call the method
        package_info = self.integration.get_package_info("123")
        
        # Assertions
        self.assertEqual(package_info["name"], "test-server")
        self.assertEqual(package_info["description"], "Test server description")
        self.assertEqual(package_info["repository"]["url"], "https://github.com/test/test-server")
        self.assertEqual(package_info["version_detail"]["version"], "1.0.0")
        self.assertEqual(package_info["packages"][0]["name"], "test-package")
        self.assertEqual(len(package_info["versions"]), 1)
        self.assertEqual(package_info["versions"][0]["version"], "1.0.0")
        mock_get_server_info.assert_called_once_with("123")
        
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.get_server_info')
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.get_server_by_name')
    def test_get_package_info_by_name(self, mock_get_server_by_name, mock_get_server_info):
        """Test getting package information by name when ID fails."""
        # Mock get_server_info to fail
        mock_get_server_info.side_effect = ValueError("Server not found")
        
        # Mock get_server_by_name
        mock_get_server_by_name.return_value = {
            "id": "123",
            "name": "test-server",
            "description": "Test description",
            "version_detail": {"version": "1.0.0"}
        }
        
        # Call the method
        result = self.integration.get_package_info("test-server")
        
        # Assertions
        self.assertEqual(result["name"], "test-server")
        mock_get_server_by_name.assert_called_once_with("test-server")
        
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.get_server_info')
    @mock.patch('apm_cli.registry.client.SimpleRegistryClient.get_server_by_name')
    def test_get_package_info_not_found(self, mock_get_server_by_name, mock_get_server_info):
        """Test error handling when package is not found."""
        # Mock both methods to fail
        mock_get_server_info.side_effect = ValueError("Server not found")
        mock_get_server_by_name.return_value = None
        
        # Call the method and assert it raises a ValueError
        with self.assertRaises(ValueError):
            self.integration.get_package_info("non-existent")
            
    @mock.patch('apm_cli.registry.integration.RegistryIntegration.get_package_info')
    def test_get_latest_version(self, mock_get_package_info):
        """Test getting the latest version of a package."""
        # Test with version_detail
        mock_get_package_info.return_value = {
            "version_detail": {
                "version": "2.0.0",
                "is_latest": True
            }
        }
        
        version = self.integration.get_latest_version("test-package")
        self.assertEqual(version, "2.0.0")
        
        # Test with packages list
        mock_get_package_info.return_value = {
            "packages": [
                {"name": "test", "version": "1.5.0"}
            ]
        }
        
        version = self.integration.get_latest_version("test-package")
        self.assertEqual(version, "1.5.0")
        
        # Test with versions list (backward compatibility)
        mock_get_package_info.return_value = {
            "versions": [
                {"version": "1.0.0"},
                {"version": "1.1.0"}
            ]
        }
        
        version = self.integration.get_latest_version("test-package")
        self.assertEqual(version, "1.1.0")
        
        # Test with no versions
        mock_get_package_info.return_value = {}
        with self.assertRaises(ValueError):
            self.integration.get_latest_version("test-package")


if __name__ == "__main__":
    unittest.main()