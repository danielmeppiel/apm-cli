"""Integration tests for the MCP registry client with demo registry."""

import unittest
import os
import requests
from awd_cli.registry.client import SimpleRegistryClient


class TestRegistryClientIntegration(unittest.TestCase):
    """Integration test cases for the MCP registry client with the demo registry."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the demo registry for integration tests
        self.client = SimpleRegistryClient("https://demo.registry.azure-mcp.net")
        
        # Skip tests if we can't reach the demo registry
        try:
            response = requests.head("https://demo.registry.azure-mcp.net")
            response.raise_for_status()
        except (requests.RequestException, ValueError):
            self.skipTest("Demo registry is not accessible")
    
    def test_list_packages(self):
        """Test listing packages from the demo registry."""
        try:
            packages = self.client.list_packages()
            self.assertIsInstance(packages, list)
            # We don't know exactly what packages will be in the demo registry,
            # but we can check that the structure is correct
            if packages:
                self.assertIn("name", packages[0])
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not list packages from demo registry: {e}")
    
    def test_search_packages(self):
        """Test searching for packages in the demo registry."""
        try:
            # First, get all packages to find something to search for
            all_packages = self.client.list_packages()
            if not all_packages:
                self.skipTest("No packages found in demo registry to search for")
                
            # Search for the first package by name
            search_term = all_packages[0]["name"][:4]  # Use the first few letters
            results = self.client.search_packages(search_term)
            
            # We should find at least the package we searched for
            self.assertGreaterEqual(len(results), 1)
            self.assertTrue(any(p["name"] == all_packages[0]["name"] for p in results))
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not search packages in demo registry: {e}")
    
    def test_get_package_info(self):
        """Test getting package information from the demo registry."""
        try:
            # First, get all packages to find one to get info about
            all_packages = self.client.list_packages()
            if not all_packages:
                self.skipTest("No packages found in demo registry to get info about")
                
            # Get info about the first package
            package_name = all_packages[0]["name"]
            package_info = self.client.get_package_info(package_name)
            
            # Check that we got the expected package info
            self.assertEqual(package_info["name"], package_name)
            self.assertIn("description", package_info)
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not get package info from demo registry: {e}")


if __name__ == "__main__":
    unittest.main()