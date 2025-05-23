"""Parser for workflow definition files."""

import os
import frontmatter


class WorkflowDefinition:
    """Simple container for workflow data."""
    
    def __init__(self, name, file_path, metadata, content):
        """Initialize a workflow definition.
        
        Args:
            name (str): Name of the workflow.
            file_path (str): Path to the workflow file.
            metadata (dict): Metadata from the frontmatter.
            content (str): Content of the workflow file.
        """
        self.name = name
        self.file_path = file_path
        self.description = metadata.get('description', '')
        self.author = metadata.get('author', '')
        self.mcp_dependencies = metadata.get('mcp', [])
        self.input_parameters = metadata.get('input', [])
        self.content = content
    
    def validate(self):
        """Basic validation of required fields.
        
        Returns:
            list: List of validation errors.
        """
        errors = []
        if not self.description:
            errors.append("Missing 'description' in frontmatter")
        if not self.input_parameters:
            errors.append("Missing 'input' parameters in frontmatter")
        return errors


def parse_workflow_file(file_path):
    """Parse a workflow file.
    
    Args:
        file_path (str): Path to the workflow file.
    
    Returns:
        WorkflowDefinition: Parsed workflow definition.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        name = os.path.basename(file_path).replace('.awd.md', '')
        metadata = post.metadata
        content = post.content
        
        return WorkflowDefinition(name, file_path, metadata, content)
    except Exception as e:
        raise ValueError(f"Failed to parse workflow file: {e}")