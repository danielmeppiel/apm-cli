"""Test LLM runtime integration."""

import pytest
from unittest.mock import Mock, patch
from awd_cli.runtime.llm_runtime import LLMRuntime


class TestLLMRuntime:
    """Test LLM runtime adapter."""
    
    @patch('awd_cli.runtime.llm_runtime.llm')
    def test_init_success(self, mock_llm):
        """Test successful initialization."""
        mock_model = Mock()
        mock_llm.get_model.return_value = mock_model
        
        runtime = LLMRuntime("gpt-4o-mini")
        
        assert runtime.model == mock_model
        assert runtime.model_name == "gpt-4o-mini"
        mock_llm.get_model.assert_called_once_with("gpt-4o-mini")
    
    @patch('awd_cli.runtime.llm_runtime.llm')
    def test_init_fallback(self, mock_llm):
        """Test fallback to default model."""
        mock_model = Mock()
        mock_llm.get_model.side_effect = [Exception("Model not found"), mock_model]
        
        runtime = LLMRuntime("invalid-model")
        
        assert runtime.model == mock_model
        assert runtime.model_name == "gpt-4o-mini"
        assert mock_llm.get_model.call_count == 2
    
    @patch('awd_cli.runtime.llm_runtime.llm')
    def test_execute_prompt_success(self, mock_llm):
        """Test successful prompt execution."""
        mock_response = Mock()
        mock_response.text.return_value = "Test response"
        mock_model = Mock()
        mock_model.prompt.return_value = mock_response
        mock_llm.get_model.return_value = mock_model
        
        runtime = LLMRuntime()
        result = runtime.execute_prompt("Test prompt")
        
        assert result == "Test response"
        mock_model.prompt.assert_called_once_with("Test prompt")
    
    @patch('awd_cli.runtime.llm_runtime.llm')
    def test_execute_prompt_failure(self, mock_llm):
        """Test prompt execution failure."""
        mock_model = Mock()
        mock_model.prompt.side_effect = Exception("API error")
        mock_llm.get_model.return_value = mock_model
        
        runtime = LLMRuntime()
        
        with pytest.raises(RuntimeError, match="Failed to execute prompt"):
            runtime.execute_prompt("Test prompt")
    
    def test_get_default_model(self):
        """Test default model getter."""
        assert LLMRuntime.get_default_model() == "gpt-4o-mini"
    
    @patch('awd_cli.runtime.llm_runtime.llm')
    def test_str_representation(self, mock_llm):
        """Test string representation."""
        mock_llm.get_model.return_value = Mock()
        
        runtime = LLMRuntime("claude-3-sonnet")
        
        assert str(runtime) == "LLMRuntime(model=claude-3-sonnet)"
