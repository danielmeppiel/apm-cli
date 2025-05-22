"""Helper utility functions for AWD-CLI."""

import os
import platform
import subprocess


def is_tool_available(tool_name):
    """Check if a command-line tool is available.
    
    Args:
        tool_name (str): Name of the tool to check.
    
    Returns:
        bool: True if the tool is available, False otherwise.
    """
    try:
        devnull = open(os.devnull, "w")
        subprocess.Popen([tool_name], stdout=devnull, stderr=devnull).communicate()
    except OSError:
        return False
    return True


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
