"""Integration tests for the MCP registry client with demo registry."""

import unittest
import os
import requests
from apm_cli.registry.client import SimpleRegistryClient


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
    
    def test_specific_real_servers(self):
        """Test integration with specific real servers from the demo registry."""
        # Test specific server IDs from the MCP demo registry
        figma_server_id = "43515997-b00f-4472-bca4-6c47389e7685"  # Figma Context MCP (NPX runtime)
        box_server_id = "da0676e0-e495-46a7-a330-29e2e4bfc653"  # Box MCP server (UV runtime)
        
        # Set to collect different runtime types we encounter
        runtime_types = set()
        
        # Test the Figma MCP server (NPX runtime)
        try:
            figma_server = self.client.get_server_info(figma_server_id)
            
            # Validate basic server information
            self.assertEqual(figma_server["id"], figma_server_id)
            self.assertIn("name", figma_server)
            self.assertIn("description", figma_server)
            
            # Validate repository information
            self.assertIn("repository", figma_server)
            self.assertIn("url", figma_server["repository"])
            self.assertIn("source", figma_server["repository"])
            
            # Validate version details
            self.assertIn("version_detail", figma_server)
            self.assertIn("version", figma_server["version_detail"])
            
            # Validate it has package information
            self.assertIn("packages", figma_server)
            self.assertGreater(len(figma_server["packages"]), 0)
            
            # Validate NPX package details
            package = figma_server["packages"][0]
            self.assertIn("name", package)
            self.assertIn("version", package)
            
            if "runtime_hint" in package:
                runtime_types.add(package["runtime_hint"])
                
            # Validate arguments
            if "runtime_arguments" in package:
                self.assertGreater(len(package["runtime_arguments"]), 0)
                for arg in package["runtime_arguments"]:
                    self.assertIn("is_required", arg)
                    self.assertIn("value", arg)
            
            if "package_arguments" in package:
                self.assertGreater(len(package["package_arguments"]), 0)
                for arg in package["package_arguments"]:
                    self.assertIn("is_required", arg)
                    self.assertIn("value", arg)
                    
            # Test finding by name
            figma_name = figma_server["name"]
            found_by_name = self.client.get_server_by_name(figma_name)
            self.assertIsNotNone(found_by_name)
            self.assertEqual(found_by_name["id"], figma_server_id)
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not test Figma MCP server: {e}")
            
        # Test the Box MCP server (UV runtime)
        try:
            box_server = self.client.get_server_info(box_server_id)
            
            # Validate basic server information
            self.assertEqual(box_server["id"], box_server_id)
            self.assertIn("name", box_server)
            self.assertIn("description", box_server)
            
            # Validate repository information
            self.assertIn("repository", box_server)
            self.assertIn("url", box_server["repository"])
            
            # Validate it has package information if available
            if "packages" in box_server and box_server["packages"]:
                package = box_server["packages"][0]
                self.assertIn("name", package)
                self.assertIn("version", package)
                
                if "runtime_hint" in package:
                    runtime_types.add(package["runtime_hint"])
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not test Box MCP server: {e}")
            
        # Try to find a server with Docker runtime
        try:
            # Search for servers with different runtime types
            servers, _ = self.client.list_servers(limit=50)
            
            for server in servers:
                server_id = server["id"]
                if server_id != figma_server_id and server_id != box_server_id:
                    try:
                        server_info = self.client.get_server_info(server_id)
                        
                        if "packages" in server_info and server_info["packages"]:
                            for package in server_info["packages"]:
                                if "runtime_hint" in package and package["runtime_hint"] not in runtime_types:
                                    runtime_types.add(package["runtime_hint"])
                                    
                                    # Validate we can get basic info for this server type
                                    self.assertIn("name", server_info)
                                    self.assertIn("description", server_info)
                                    self.assertIn("id", server_info)
                                    
                                    # If we found at least 3 different runtime types, we've validated enough diversity
                                    if len(runtime_types) >= 3:
                                        break
                    except (requests.RequestException, ValueError):
                        # Skip servers that can't be accessed
                        continue
                        
                    # If we found at least 3 different runtime types, we've validated enough diversity
                    if len(runtime_types) >= 3:
                        break
                        
            # We should have found at least 2 different runtime types
            self.assertGreaterEqual(len(runtime_types), 2,
                                  f"Expected to find at least 2 different runtime types, found: {runtime_types}")
        except (requests.RequestException, ValueError) as e:
            self.skipTest(f"Could not test servers with different runtime types: {e}")


if __name__ == "__main__":
    unittest.main()