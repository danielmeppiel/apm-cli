"""Integration test for multi-runtime architecture."""

import tempfile
import os
from unittest.mock import patch, Mock
from awd_cli.workflow.runner import run_workflow
from awd_cli.runtime.factory import RuntimeFactory


def test_runtime_backward_compatibility():
    """Test that existing model names work as runtime parameters."""
    # Create a temporary workflow file
    workflow_content = """---
name: test-backward-compat
description: Test backward compatibility
input: [message]
---

# Backward Compatibility Test

${input:message}
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_file = os.path.join(temp_dir, "test-backward-compat.prompt.md")
        with open(workflow_file, "w") as f:
            f.write(workflow_content)
        
        # Mock the RuntimeFactory for testing backward compatibility
        with patch('awd_cli.workflow.runner.RuntimeFactory') as mock_factory_class:
            mock_runtime = Mock()
            mock_runtime.execute_prompt.return_value = "Response from LLM"
            mock_factory_class.create_runtime.return_value = mock_runtime
            mock_factory_class.runtime_exists.return_value = False  # Model name, not runtime
            
            # Test with model name (backward compatibility)
            params = {
                'message': 'Test message',
                '_runtime': 'gpt-4o-mini'
            }
            
            success, result = run_workflow('test-backward-compat', params, temp_dir)
            
            # Verify the result
            assert success is True
            assert result == "Response from LLM"
            
            # Verify factory calls for backward compatibility
            mock_factory_class.runtime_exists.assert_called_once_with('gpt-4o-mini')
            mock_factory_class.create_runtime.assert_called_once_with('llm', 'gpt-4o-mini')


def test_runtime_type_selection():
    """Test explicit runtime type selection."""
    # Create a temporary workflow file
    workflow_content = """---
name: test-runtime-type
description: Test runtime type selection
input: [message]
---

# Runtime Type Test

${input:message}
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_file = os.path.join(temp_dir, "test-runtime-type.prompt.md")
        with open(workflow_file, "w") as f:
            f.write(workflow_content)
        
        # Mock the RuntimeFactory for testing runtime type selection
        with patch('awd_cli.workflow.runner.RuntimeFactory') as mock_factory_class:
            mock_runtime = Mock()
            mock_runtime.execute_prompt.return_value = "Response from runtime"
            mock_factory_class.create_runtime.return_value = mock_runtime
            mock_factory_class.runtime_exists.return_value = True  # Runtime type exists
            
            # Test with runtime type
            params = {
                'message': 'Test message',
                '_runtime': 'llm'
            }
            
            success, result = run_workflow('test-runtime-type', params, temp_dir)
            
            # Verify the result
            assert success is True
            assert result == "Response from runtime"
            
            # Verify factory calls for runtime type
            mock_factory_class.runtime_exists.assert_called_once_with('llm')
            mock_factory_class.create_runtime.assert_called_once_with('llm')


def test_runtime_factory_integration():
    """Test runtime factory integration on real system."""
    # Test getting available runtimes
    available = RuntimeFactory.get_available_runtimes()
    
    # Should have at least LLM available
    assert len(available) >= 1
    assert any(rt["name"] == "llm" for rt in available)
    
    # Test runtime existence checks
    assert RuntimeFactory.runtime_exists("llm") is True
    assert RuntimeFactory.runtime_exists("unknown") is False
    
    # Test getting best available runtime
    best_runtime = RuntimeFactory.get_best_available_runtime()
    assert best_runtime is not None
    assert best_runtime.get_runtime_name() in ["llm", "codex"]
    
    # Test creating specific runtime
    llm_runtime = RuntimeFactory.create_runtime("llm")
    assert llm_runtime.get_runtime_name() == "llm"