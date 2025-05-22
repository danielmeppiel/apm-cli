"""Unit tests for the dependencies management module."""

import os
import tempfile
import unittest
from unittest.mock import patch, mock_open
import yaml
import frontmatter

from awd_cli.deps.aggregator import scan_workflows_for_dependencies, sync_workflow_dependencies
from awd_cli.deps.verifier import verify_dependencies, install_missing_dependencies, load_awd_config


class TestDependenciesAggregator(unittest.TestCase):
    """Test cases for the dependencies aggregator."""
    
    @patch('glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    @patch('frontmatter.load')
    def test_scan_workflows_for_dependencies(self, mock_frontmatter_load, mock_file, mock_glob):
        """Test scanning workflows for dependencies."""
        # Mock glob to return workflow files
        mock_glob.return_value = ['workflow1.awd.md', 'workflow2.awd.md']
        
        # Mock frontmatter.load to return content with mcp metadata
        mock_content1 = unittest.mock.MagicMock()
        mock_content1.metadata = {'mcp': ['server1', 'server2']}
        
        mock_content2 = unittest.mock.MagicMock()
        mock_content2.metadata = {'mcp': ['server2', 'server3']}
        
        mock_frontmatter_load.side_effect = [mock_content1, mock_content2]
        
        # Call the function
        result = scan_workflows_for_dependencies()
        
        # Verify the results
        self.assertIsInstance(result, set)
        self.assertEqual(result, {'server1', 'server2', 'server3'})
        self.assertEqual(mock_glob.call_count, 1)
        self.assertEqual(mock_file.call_count, 2)
        self.assertEqual(mock_frontmatter_load.call_count, 2)
    
    @patch('awd_cli.deps.aggregator.scan_workflows_for_dependencies')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_sync_workflow_dependencies(self, mock_yaml_dump, mock_file, mock_scan):
        """Test syncing workflow dependencies to awd.yml."""
        # Mock scan_workflows_for_dependencies to return a set of servers
        mock_scan.return_value = {'server1', 'server2', 'server3'}
        
        # Call the function
        success, servers = sync_workflow_dependencies('test.yml')
        
        # Verify the results
        self.assertTrue(success)
        self.assertEqual(set(servers), {'server1', 'server2', 'server3'})
        self.assertEqual(mock_scan.call_count, 1)
        mock_file.assert_called_once_with('test.yml', 'w', encoding='utf-8')
        mock_yaml_dump.assert_called_once()


class TestDependenciesVerifier(unittest.TestCase):
    """Test cases for the dependencies verifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'awd.yml')
        
        # Create a test configuration file
        config = {
            'version': '1.0',
            'servers': ['server1', 'server2', 'server3']
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_load_awd_config(self):
        """Test loading the AWD configuration file."""
        # Test with an existing file
        config = load_awd_config(self.config_path)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['version'], '1.0')
        self.assertEqual(config['servers'], ['server1', 'server2', 'server3'])
        
        # Test with a non-existent file
        config = load_awd_config('nonexistent.yml')
        self.assertIsNone(config)
    
    @patch('awd_cli.factory.PackageManagerFactory.create_package_manager')
    def test_verify_dependencies(self, mock_factory):
        """Test verifying dependencies."""
        # Mock the package manager to return a list of installed packages
        mock_package_manager = unittest.mock.MagicMock()
        mock_package_manager.list_installed.return_value = ['server1', 'server3']
        mock_factory.return_value = mock_package_manager
        
        # Call the function
        all_installed, installed, missing = verify_dependencies(self.config_path)
        
        # Verify the results
        self.assertFalse(all_installed)
        self.assertEqual(set(installed), {'server1', 'server3'})
        self.assertEqual(set(missing), {'server2'})
        
        # Test with all packages installed
        mock_package_manager.list_installed.return_value = ['server1', 'server2', 'server3']
        all_installed, installed, missing = verify_dependencies(self.config_path)
        self.assertTrue(all_installed)
        self.assertEqual(set(installed), {'server1', 'server2', 'server3'})
        self.assertEqual(missing, [])
    
    @patch('awd_cli.factory.ClientFactory.create_client')
    @patch('awd_cli.factory.PackageManagerFactory.create_package_manager')
    @patch('awd_cli.deps.verifier.verify_dependencies')
    def test_install_missing_dependencies(self, mock_verify, mock_factory, mock_client_factory):
        """Test installing missing dependencies."""
        # Mock verify_dependencies to return missing packages
        mock_verify.return_value = (False, ['server1'], ['server2', 'server3'])
        
        # Mock the package manager to install packages
        mock_package_manager = unittest.mock.MagicMock()
        mock_package_manager.install.return_value = True
        mock_factory.return_value = mock_package_manager
        
        # Mock the client adapter
        mock_client = unittest.mock.MagicMock()
        mock_client.configure_mcp_server.return_value = True
        mock_client_factory.return_value = mock_client
        
        # Call the function
        success, installed = install_missing_dependencies(self.config_path, "vscode")
        
        # Verify the results
        self.assertTrue(success)
        self.assertEqual(set(installed), {'server2', 'server3'})
        self.assertEqual(mock_verify.call_count, 1)
        self.assertEqual(mock_package_manager.install.call_count, 2)
        self.assertEqual(mock_client.configure_mcp_server.call_count, 2)
        
        # Verify client was configured properly
        mock_client.configure_mcp_server.assert_any_call('server2', server_name='server2')
        mock_client.configure_mcp_server.assert_any_call('server3', server_name='server3')


if __name__ == "__main__":
    unittest.main()