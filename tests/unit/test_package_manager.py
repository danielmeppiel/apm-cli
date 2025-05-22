"""Unit tests for the default MCP package manager."""

import unittest
from awd_cli.adapters.package_manager.default_manager import DefaultMCPPackageManager


class TestDefaultMCPPackageManager(unittest.TestCase):
    """Test cases for the default MCP package manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.package_manager = DefaultMCPPackageManager()
    
    def test_install(self):
        """Test installing a package."""
        result = self.package_manager.install("test-package")
        self.assertTrue(result)
        
        result = self.package_manager.install("test-package", "1.0.0")
        self.assertTrue(result)
    
    def test_uninstall(self):
        """Test uninstalling a package."""
        result = self.package_manager.uninstall("test-package")
        self.assertTrue(result)
    
    def test_list_installed(self):
        """Test listing installed packages."""
        packages = self.package_manager.list_installed()
        self.assertIsInstance(packages, list)
    
    def test_search(self):
        """Test searching for packages."""
        results = self.package_manager.search("test")
        self.assertIsInstance(results, list)
        self.assertTrue(all("test" in result for result in results))


if __name__ == "__main__":
    unittest.main()
