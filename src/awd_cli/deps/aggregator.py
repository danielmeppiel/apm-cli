"""Workflow dependency aggregator for AWD-CLI."""

import os
import glob
from pathlib import Path
import yaml
import frontmatter


def scan_workflows_for_dependencies():
    """Scan all .awd.md files for MCP dependencies.
    
    Returns:
        set: A set of unique MCP server names from all workflows.
    """
    workflows = glob.glob("**/*.awd.md", recursive=True)
    all_servers = set()
    
    for workflow_file in workflows:
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = frontmatter.load(f)
                if 'mcp' in content.metadata and isinstance(content.metadata['mcp'], list):
                    all_servers.update(content.metadata['mcp'])
        except Exception as e:
            print(f"Error processing {workflow_file}: {e}")
    
    return all_servers


def sync_workflow_dependencies(output_file="awd.yml"):
    """Extract all MCP servers from workflows into awd.yml.
    
    Args:
        output_file (str, optional): Path to the output file. Defaults to "awd.yml".
        
    Returns:
        tuple: (bool, list) - Success status and list of servers added
    """
    all_servers = scan_workflows_for_dependencies()
    
    # Prepare the configuration
    awd_config = {
        'version': '1.0',
        'servers': sorted(list(all_servers))
    }
    
    try:
        # Create the file
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(awd_config, f, default_flow_style=False)
        return True, awd_config['servers']
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        return False, []