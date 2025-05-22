"""Unit tests for the MCP registry integration."""

import unittest
from unittest import mock
from awd_cli.registry.integration import RegistryIntegration


class TestRegistryIntegration(unittest.TestCase):
    """Test cases for the MCP registry integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = RegistryIntegration()
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.list_packages')
    def test_list_available_packages(self, mock_list_packages):
        """Test listing available packages."""
        # Mock response
        mock_list_packages.return_value = [
            {"name": "package1", "description": "Description 1"},
            {"name": "package2", "description": "Description 2"}
        ]
        
        # Call the method
        packages = self.integration.list_available_packages()
        
        # Assertions
        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0]["name"], "package1")
        self.assertEqual(packages[1]["name"], "package2")
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.search_packages')
    def test_search_packages(self, mock_search_packages):
        """Test searching for packages."""
        # Mock response
        mock_search_packages.return_value = [
            {"name": "test-package", "description": "Test description"}
        ]
        
        # Call the method
        results = self.integration.search_packages("test")
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test-package")
        mock_search_packages.assert_called_once_with("test")
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.get_package_info')
    def test_get_package_info(self, mock_get_package_info):
        """Test getting package information."""
        # Mock response
        mock_get_package_info.return_value = {
            "name": "test-package",
            "description": "Test package description",
            "versions": [
                {"version": "1.0.0"},
                {"version": "1.1.0"}
            ]
        }
        
        # Call the method
        package_info = self.integration.get_package_info("test-package")
        
        # Assertions
        self.assertEqual(package_info["name"], "test-package")
        self.assertEqual(len(package_info["versions"]), 2)
        mock_get_package_info.assert_called_once_with("test-package")
        
    @mock.patch('awd_cli.registry.integration.RegistryIntegration.get_package_info')
    def test_get_latest_version(self, mock_get_package_info):
        """Test getting the latest version of a package."""
        # Mock response
        mock_get_package_info.return_value = {
            "name": "test-package",
            "versions": [
                {"version": "1.0.0"},
                {"version": "1.1.0"}
            ]
        }
        
        # Call the method
        version = self.integration.get_latest_version("test-package")
        
        # Assertions
        self.assertEqual(version, "1.1.0")
        mock_get_package_info.assert_called_once_with("test-package")
        
        # Test with empty versions
        mock_get_package_info.return_value = {
            "name": "test-package",
            "versions": []
        }
        
        # Call the method and assert it raises a ValueError
        with self.assertRaises(ValueError):
            self.integration.get_latest_version("test-package")


if __name__ == "__main__":
    unittest.main()