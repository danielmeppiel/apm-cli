"""Lightweight clipboard utility using native OS commands."""

import subprocess
import sys
from typing import Optional


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard using native OS commands.
    
    Args:
        text: The text to copy to clipboard
        
    Returns:
        True if successful, False if clipboard unavailable or failed
    """
    if not text:
        return False
        
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(
                ["pbcopy"], 
                input=text, 
                text=True, 
                check=True,
                capture_output=True
            )
        elif sys.platform == "win32":  # Windows
            subprocess.run(
                ["clip"], 
                input=text,
                text=True,
                check=True,
                capture_output=True
            )
        else:  # Linux and other Unix-like systems
            # Try xclip first, fall back to xsel
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"], 
                    input=text,
                    text=True,
                    check=True,
                    capture_output=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to xsel
                subprocess.run(
                    ["xsel", "--clipboard", "--input"], 
                    input=text,
                    text=True,
                    check=True,
                    capture_output=True
                )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def get_clipboard_status() -> str:
    """
    Get the current clipboard status for the platform.
    
    Returns:
        String indicating clipboard availability
    """
    try:
        if sys.platform == "darwin":
            subprocess.run(["which", "pbcopy"], check=True, capture_output=True)
            return "pbcopy available"
        elif sys.platform == "win32":
            subprocess.run(["where", "clip"], check=True, capture_output=True)
            return "clip available"
        else:
            try:
                subprocess.run(["which", "xclip"], check=True, capture_output=True)
                return "xclip available"
            except (subprocess.CalledProcessError, FileNotFoundError):
                subprocess.run(["which", "xsel"], check=True, capture_output=True)
                return "xsel available"
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "clipboard unavailable"
