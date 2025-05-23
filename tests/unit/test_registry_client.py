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
    def test_list_servers(self, mock_get):
        """Test listing servers from the registry."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "servers": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "server1", 
                    "description": "Description 1"
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426614174000",
                    "name": "server2", 
                    "description": "Description 2"
                }
            ],
            "metadata": {
                "next_cursor": "next-page-token",
                "count": 2
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        servers, next_cursor = self.client.list_servers()
        
        # Assertions
        self.assertEqual(len(servers), 2)
        self.assertEqual(servers[0]["name"], "server1")
        self.assertEqual(servers[1]["name"], "server2")
        self.assertEqual(next_cursor, "next-page-token")
        mock_get.assert_called_once_with(f"{self.client.registry_url}/v0/servers", params={'limit': 100})
        
    @mock.patch('requests.Session.get')
    def test_list_servers_with_pagination(self, mock_get):
        """Test listing servers with pagination parameters."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.json.return_value = {"servers": [], "metadata": {}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method with pagination
        self.client.list_servers(limit=10, cursor="page-token")
        
        # Assertions
        mock_get.assert_called_once_with(
            f"{self.client.registry_url}/v0/servers", 
            params={"limit": 10, "cursor": "page-token"}
        )
        
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.list_servers')
    def test_search_servers(self, mock_list_servers):
        """Test searching for servers in the registry."""
        # Mock response
        mock_list_servers.return_value = (
            [
                {"name": "test-server", "description": "Test description"},
                {"name": "server2", "description": "Another test"}
            ],
            None
        )
        
        # Call the method with a query that should match both servers
        results = self.client.search_servers("test")
        
        # Assertions
        self.assertEqual(len(results), 2)
        
        # Call the method with a query that should match only one server
        results = self.client.search_servers("another")
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "server2")
        
    @mock.patch('requests.Session.get')
    def test_get_server_info(self, mock_get):
        """Test getting server information from the registry."""
        # Mock response
        mock_response = mock.Mock()
        server_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "test-server",
            "description": "Test server description",
            "repository": {
                "url": "https://github.com/test/test-server",
                "source": "github",
                "id": "12345"
            },
            "version_detail": {
                "version": "1.0.0",
                "release_date": "2025-05-16T19:13:21Z",
                "is_latest": True
            },
            "package_canonical": "npm",
            "packages": [
                {
                    "registry_name": "npm",
                    "name": "test-package",
                    "version": "1.0.0",
                    "runtime_hint": "npx"
                }
            ]
        }
        mock_response.json.return_value = server_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        server_info = self.client.get_server_info("123e4567-e89b-12d3-a456-426614174000")
        
        # Assertions
        self.assertEqual(server_info["name"], "test-server")
        self.assertEqual(server_info["version_detail"]["version"], "1.0.0")
        self.assertEqual(server_info["packages"][0]["name"], "test-package")
        mock_get.assert_called_once_with(
            f"{self.client.registry_url}/v0/servers/123e4567-e89b-12d3-a456-426614174000"
        )
    
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.list_servers')
    @mock.patch('awd_cli.registry.client.SimpleRegistryClient.get_server_info')
    def test_get_server_by_name(self, mock_get_server_info, mock_list_servers):
        """Test finding a server by name."""
        # Mock list_servers
        mock_list_servers.return_value = (
            [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "test-server"
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426614174000",
                    "name": "other-server"
                }
            ],
            None
        )
        
        # Mock get_server_info
        server_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "test-server",
            "description": "Test server"
        }
        mock_get_server_info.return_value = server_data
        
        # Call the method
        result = self.client.get_server_by_name("test-server")
        
        # Assertions
        self.assertEqual(result, server_data)
        mock_get_server_info.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000")
        
        # Test non-existent server
        result = self.client.get_server_by_name("non-existent")
        self.assertIsNone(result)
        
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