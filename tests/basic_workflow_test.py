"""Basic tests for workflow functionality."""

import os
import sys
import tempfile
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from awd_cli.workflow.parser import WorkflowDefinition, parse_workflow_file
from awd_cli.workflow.runner import substitute_parameters
from awd_cli.workflow.discovery import create_workflow_template


class TestWorkflow(unittest.TestCase):
    """Basic test cases for workflow functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_workflow_definition(self):
        """Test the WorkflowDefinition class."""
        workflow = WorkflowDefinition(
            "test",
            "test.awd.md",
            {
                "description": "Test workflow",
                "author": "Test Author",
                "mcp": ["test-package"],
                "input": ["param1", "param2"]
            },
            "Test content"
        )
        
        self.assertEqual(workflow.name, "test")
        self.assertEqual(workflow.description, "Test workflow")
        self.assertEqual(workflow.author, "Test Author")
        self.assertEqual(workflow.mcp_dependencies, ["test-package"])
        self.assertEqual(workflow.input_parameters, ["param1", "param2"])
        self.assertEqual(workflow.content, "Test content")
    
    def test_parameter_substitution(self):
        """Test parameter substitution."""
        content = "This is ${input:param1} and ${input:param2}"
        params = {"param1": "value1", "param2": "value2"}
        
        result = substitute_parameters(content, params)
        self.assertEqual(result, "This is value1 and value2")
    
    def test_create_workflow_template(self):
        """Test creating a workflow template."""
        template_path = create_workflow_template("test-workflow", self.temp_dir.name)
        
        self.assertTrue(os.path.exists(template_path))
        self.assertEqual(os.path.basename(template_path), "test-workflow.awd.md")


if __name__ == "__main__":
    unittest.main()