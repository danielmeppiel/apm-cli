"""Tests for helper utility functions."""

import unittest
import sys
from awd_cli.utils.helpers import is_tool_available, detect_platform, get_available_package_managers


class TestHelpers(unittest.TestCase):
    """Test cases for helper utility functions."""
    
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
        # At least one package manager should be available in the test environment
        if sys.platform != 'win32':  # On non-Windows, Python's pip should be available
            self.assertIn('pip', managers)


if __name__ == '__main__':
    unittest.main()