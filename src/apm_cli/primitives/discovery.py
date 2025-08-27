"""Discovery functionality for primitive files."""

import os
import glob
from pathlib import Path
from typing import List

from .models import PrimitiveCollection
from .parser import parse_primitive_file


def discover_primitives(base_dir: str = ".") -> PrimitiveCollection:
    """Find all APM primitive files in the project.
    
    Searches for .chatmode.md, .instructions.md, .context.md, and .memory.md files
    in both .apm/ and .github/ directory structures.
    
    Args:
        base_dir (str): Base directory to search in. Defaults to current directory.
    
    Returns:
        PrimitiveCollection: Collection of discovered and parsed primitives.
    """
    collection = PrimitiveCollection()
    
    # Define patterns for different primitive types
    primitive_patterns = {
        'chatmode': [
            "**/.apm/chatmodes/*.chatmode.md",
            "**/.github/chatmodes/*.chatmode.md",
            "**/*.chatmode.md"  # Generic .chatmode.md files
        ],
        'instruction': [
            "**/.apm/instructions/*.instructions.md",
            "**/.github/instructions/*.instructions.md",
            "**/*.instructions.md"  # Generic .instructions.md files
        ],
        'context': [
            "**/.apm/context/*.context.md",
            "**/.apm/memory/*.memory.md",  # APM memory convention
            "**/.github/context/*.context.md",
            "**/.github/memory/*.memory.md",  # VSCode compatibility
            "**/*.context.md",  # Generic .context.md files
            "**/*.memory.md"  # Generic .memory.md files
        ]
    }
    
    # Find and parse files for each primitive type
    for primitive_type, patterns in primitive_patterns.items():
        files = find_primitive_files(base_dir, patterns)
        
        for file_path in files:
            try:
                primitive = parse_primitive_file(file_path)
                collection.add_primitive(primitive)
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")
    
    return collection


def find_primitive_files(base_dir: str, patterns: List[str]) -> List[Path]:
    """Find primitive files matching the given patterns.
    
    Args:
        base_dir (str): Base directory to search in.
        patterns (List[str]): List of glob patterns to match.
    
    Returns:
        List[Path]: List of unique file paths found.
    """
    if not os.path.isdir(base_dir):
        return []
    
    all_files = []
    
    for pattern in patterns:
        # Use glob to find files matching the pattern
        matching_files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
        all_files.extend(matching_files)
    
    # Remove duplicates while preserving order and convert to Path objects
    seen = set()
    unique_files = []
    
    for file_path in all_files:
        abs_path = os.path.abspath(file_path)
        if abs_path not in seen:
            seen.add(abs_path)
            unique_files.append(Path(abs_path))
    
    # Filter out directories and ensure files are readable
    valid_files = []
    for file_path in unique_files:
        if file_path.is_file() and _is_readable(file_path):
            valid_files.append(file_path)
    
    return valid_files


def _is_readable(file_path: Path) -> bool:
    """Check if a file is readable.
    
    Args:
        file_path (Path): Path to check.
    
    Returns:
        bool: True if file is readable, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to read first few bytes to verify it's readable
            f.read(1)
        return True
    except (PermissionError, UnicodeDecodeError, OSError):
        return False


def _should_skip_directory(dir_path: str) -> bool:
    """Check if a directory should be skipped during scanning.
    
    Args:
        dir_path (str): Directory path to check.
    
    Returns:
        bool: True if directory should be skipped, False otherwise.
    """
    skip_patterns = {
        '.git',
        'node_modules',
        '__pycache__',
        '.pytest_cache',
        '.venv',
        'venv',
        '.tox',
        'build',
        'dist',
        '.mypy_cache'
    }
    
    dir_name = os.path.basename(dir_path)
    return dir_name in skip_patterns