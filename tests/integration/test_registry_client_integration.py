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
    
    def test_list_servers(self):
        """Test listing servers from the demo registry."""
        try:
            servers, next_cursor = self.client.list_servers()
            self.assertIsInstance(servers, list)
            # We don't know exactly what servers will be in the demo registry,
            # but we can check that the structure is correct
            if servers:
                self.assertIn("name", servers[0])
                self.assertIn("id", servers[0])
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not list servers from demo registry: {e}")
    
    def test_search_servers(self):
        """Test searching for servers in the demo registry."""
        try:
            # First, get all servers to find something to search for
            all_servers, _ = self.client.list_servers()
            if not all_servers:
                self.skipTest("No servers found in demo registry to search for")
                
            # Search for the first server by name
            search_term = all_servers[0]["name"][:4]  # Use the first few letters
            results = self.client.search_servers(search_term)
            
            # We should find at least the server we searched for
            self.assertGreaterEqual(len(results), 1)
            self.assertTrue(any(s["name"] == all_servers[0]["name"] for s in results))
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not search servers in demo registry: {e}")
    
    def test_get_server_info(self):
        """Test getting server information from the demo registry."""
        try:
            # First, get all servers to find one to get info about
            all_servers, _ = self.client.list_servers()
            if not all_servers:
                self.skipTest("No servers found in demo registry to get info about")
                
            # Get info about the first server
            server_id = all_servers[0]["id"]
            server_info = self.client.get_server_info(server_id)
            
            # Check that we got the expected server info
            self.assertIn("name", server_info)
            self.assertEqual(server_info["id"], server_id)
            self.assertIn("description", server_info)
            
            # Check for version_detail
            self.assertIn("version_detail", server_info)
            if "version_detail" in server_info:
                self.assertIn("version", server_info["version_detail"])
                
            # Check for packages if available
            if "packages" in server_info and server_info["packages"]:
                pkg = server_info["packages"][0]
                self.assertIn("name", pkg)
                self.assertIn("version", pkg)
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not get server info from demo registry: {e}")
    
    def test_get_server_by_name(self):
        """Test finding a server by name."""
        try:
            # First, get all servers to find one to look up
            all_servers, _ = self.client.list_servers()
            if not all_servers:
                self.skipTest("No servers found in demo registry to look up")
                
            # Try to find the first server by name
            server_name = all_servers[0]["name"]
            found_server = self.client.get_server_by_name(server_name)
            
            # Check that we found the expected server
            self.assertIsNotNone(found_server, "Server should be found by name")
            self.assertEqual(found_server["name"], server_name)
            
            # Try with a non-existent name
            non_existent = self.client.get_server_by_name("non-existent-server-name-12345")
            self.assertIsNone(non_existent, "Non-existent server should return None")
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not find server by name in demo registry: {e}")


if __name__ == "__main__":
    unittest.main()