"""Discovery functionality for workflow files."""

import os
import glob
from .parser import parse_workflow_file


def discover_workflows(base_dir=None):
    """Find all .awd.md files in the current directory and subdirectories.
    
    Args:
        base_dir (str, optional): Base directory to search in. Defaults to current directory.
    
    Returns:
        list: List of WorkflowDefinition objects.
    """
    if base_dir is None:
        base_dir = os.getcwd()
    
    workflow_files = glob.glob(os.path.join(base_dir, "**/*.awd.md"), recursive=True)
    workflows = []
    
    for file_path in workflow_files:
        try:
            workflow = parse_workflow_file(file_path)
            workflows.append(workflow)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
    
    return workflows


def create_workflow_template(name, output_dir=None):
    """Create a basic workflow template file.
    
    Args:
        name (str): Name of the workflow.
        output_dir (str, optional): Directory to create the file in. Defaults to current directory.
    
    Returns:
        str: Path to the created file.
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    title = name.replace("-", " ").title()
    
    template = f"""---
description: Description here
author: Your Name
mcp:
  - package1
  - package2
input:
  - param1
  - param2
---

# {title}

1. Step One:
   - Details for step one
   - Use parameters like this: ${{input:param1}}

2. Step Two:
   - Details for step two
"""
    
    file_path = os.path.join(output_dir, f"{name}.awd.md")
    
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(template)
    
    return file_path