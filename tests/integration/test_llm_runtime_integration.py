"""Integration test for LLM runtime with AWD workflows."""

import tempfile
import os
from unittest.mock import patch, Mock
from awd_cli.workflow.runner import run_workflow


def test_workflow_with_llm_runtime():
    """Test running a workflow with LLM runtime."""
    # Create a temporary workflow file
    workflow_content = """---
name: test-prompt
description: Test prompt for LLM runtime
input: [name]
---

# Test Prompt

Hello ${input:name}, this is a test prompt for the LLM runtime integration.

Please respond with a greeting.
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_file = os.path.join(temp_dir, "test-prompt.prompt.md")
        with open(workflow_file, "w") as f:
            f.write(workflow_content)
        
        # Mock the LLM runtime
        with patch('awd_cli.workflow.runner.LLMRuntime') as mock_runtime_class:
            mock_runtime = Mock()
            mock_runtime.execute_prompt.return_value = "Hello World! Nice to meet you."
            mock_runtime_class.return_value = mock_runtime
            
            # Run the workflow with runtime parameter
            params = {
                'name': 'World',
                '_runtime': 'gpt-4o-mini'
            }
            
            success, result = run_workflow('test-prompt', params, temp_dir)
            
            # Verify the result
            assert success is True
            assert result == "Hello World! Nice to meet you."
            
            # Verify LLM runtime was called correctly
            mock_runtime_class.assert_called_once_with('gpt-4o-mini')
            mock_runtime.execute_prompt.assert_called_once()
            
            # Check that the prompt was properly substituted
            call_args = mock_runtime.execute_prompt.call_args[0]
            assert 'Hello World' in call_args[0]  # Parameter substitution worked
            assert '${input:name}' not in call_args[0]  # No unsubstituted params


def test_workflow_without_runtime():
    """Test that workflows still work without runtime (copy mode)."""
    workflow_content = """---
name: test-copy
description: Test workflow for copy mode
input: [service]
---

# Deploy Service

Deploy the ${input:service} service to production.

1. Check current status
2. Run deployment
3. Verify health
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_file = os.path.join(temp_dir, "test-copy.prompt.md")
        with open(workflow_file, "w") as f:
            f.write(workflow_content)
        
        # Run without runtime (traditional copy mode)
        params = {'service': 'api-gateway'}
        
        success, result = run_workflow('test-copy', params, temp_dir)
        
        # Verify the result
        assert success is True
        assert 'Deploy the api-gateway service' in result
        assert '${input:service}' not in result  # Parameter substitution worked
