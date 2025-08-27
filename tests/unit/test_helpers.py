"""Tests for helper utility functions."""

import unittest
import sys
from apm_cli.utils.helpers import is_tool_available, detect_platform, get_available_package_managers


class TestHelpers(unittest.TestCase):
    """Test cases for helper utility functions."""
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Force garbage collection to release file handles
        import gc
        gc.collect()
        # Small delay to allow Windows to release locks
        import time
        time.sleep(0.1)
    
    def test_is_tool_available(self):
        """Test is_tool_available function with known commands."""
        # Python should always be available in the test environment
        self.assertTrue(is_tool_available('python'))
        
        # Test a command that almost certainly doesn't exist
        self.assertFalse(is_tool_available('this_command_does_not_exist_12345'))
    
    def test_detect_platform(self):
        """Test detect_platform function."""
        platform = detect_platform()
        self.assertIn(platform, ['macos', 'linux', 'windows', 'unknown'])
    
    def test_get_available_package_managers(self):
        """Test get_available_package_managers function."""
        managers = get_available_package_managers()
        self.assertIsInstance(managers, dict)
        
        # The function should return a valid dict
        # If any managers are found, they should have valid string values
        for name, path in managers.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(path, str)
            self.assertTrue(len(name) > 0)
            self.assertTrue(len(path) > 0)
        
        # On most Unix systems, at least one package manager should be available
        # This is a reasonable expectation but not guaranteed on minimal systems
        import sys
        if sys.platform != 'win32':
            # Skip this assertion on Windows since it might not have any
            # On Unix systems, we expect at least one package manager
            self.assertGreater(len(managers), 0, 
                             "Expected at least one package manager on Unix systems")


if __name__ == '__main__':
    unittest.main()