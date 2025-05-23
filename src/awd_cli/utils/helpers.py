"""Helper utility functions for AWD-CLI."""

import os
import platform
import subprocess
import shutil
import sys


def is_tool_available(tool_name):
    """Check if a command-line tool is available.
    
    Args:
        tool_name (str): Name of the tool to check.
    
    Returns:
        bool: True if the tool is available, False otherwise.
    """
    # First try using shutil.which which is more reliable across platforms
    if shutil.which(tool_name):
        return True
        
    # Fall back to subprocess approach if shutil.which returns None
    try:
        # Different approaches for different platforms
        if sys.platform == 'win32':
            # On Windows, use 'where' command
            result = subprocess.run(['where', tool_name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   shell=True,
                                   check=False)
            return result.returncode == 0
        else:
            # On Unix-like systems, use 'which' command
            result = subprocess.run(['which', tool_name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   check=False)
            return result.returncode == 0
    except Exception:
        return False


def get_available_package_managers():
    """Get available package managers on the system.
    
    Returns:
        dict: Dictionary of available package managers and their paths.
    """
    package_managers = {}
    
    # Check for package managers
    if is_tool_available("uv"):
        package_managers["uv"] = "uv"
    if is_tool_available("pip"):
        package_managers["pip"] = "pip"
    if is_tool_available("npm"):
        package_managers["npm"] = "npm"
    if is_tool_available("brew"):
        package_managers["brew"] = "brew"
    
    return package_managers


def detect_platform():
    """Detect the current platform.
    
    Returns:
        str: Platform name (macos, linux, windows).
    """
    system = platform.system().lower()
    
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"
