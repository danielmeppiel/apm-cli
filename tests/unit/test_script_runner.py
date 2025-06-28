"""Unit tests for script runner functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from awd_cli.core.script_runner import ScriptRunner, PromptCompiler


class TestScriptRunner:
    """Test ScriptRunner functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.script_runner = ScriptRunner()
        self.compiled_content = "You are a helpful assistant. Say hello to TestUser!"
        self.compiled_path = ".awd/compiled/hello-world.txt"
    
    def test_transform_runtime_command_simple_codex(self):
        """Test simple codex command transformation."""
        original = "codex hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"codex exec '{self.compiled_content}'"
    
    def test_transform_runtime_command_codex_with_flags(self):
        """Test codex command with flags before file."""
        original = "codex --skip-git-repo-check hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"codex exec --skip-git-repo-check '{self.compiled_content}'"
    
    def test_transform_runtime_command_codex_multiple_flags(self):
        """Test codex command with multiple flags before file."""
        original = "codex --verbose --skip-git-repo-check hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"codex exec --verbose --skip-git-repo-check '{self.compiled_content}'"
    
    def test_transform_runtime_command_env_var_simple(self):
        """Test environment variable with simple codex command."""
        original = "DEBUG=true codex hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"DEBUG=true codex exec '{self.compiled_content}'"
    
    def test_transform_runtime_command_env_var_with_flags(self):
        """Test environment variable with codex flags."""
        original = "DEBUG=true codex --skip-git-repo-check hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"DEBUG=true codex exec --skip-git-repo-check '{self.compiled_content}'"
    
    def test_transform_runtime_command_llm_simple(self):
        """Test simple llm command transformation."""
        original = "llm hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"llm '{self.compiled_content}'"
    
    def test_transform_runtime_command_llm_with_options(self):
        """Test llm command with options after file."""
        original = "llm hello-world.prompt.md --model gpt-4"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"llm '{self.compiled_content}' --model gpt-4"
    
    def test_transform_runtime_command_bare_file(self):
        """Test bare prompt file defaults to codex exec."""
        original = "hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"codex exec '{self.compiled_content}'"
    
    def test_transform_runtime_command_fallback(self):
        """Test fallback behavior for unrecognized patterns."""
        original = "unknown-command hello-world.prompt.md"
        result = self.script_runner._transform_runtime_command(
            original, "hello-world.prompt.md", self.compiled_content, self.compiled_path
        )
        assert result == f"unknown-command {self.compiled_path}"
    
    @patch('awd_cli.core.script_runner.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="scripts:\n  start: 'codex hello.prompt.md'")
    def test_list_scripts(self, mock_file, mock_exists):
        """Test listing scripts from awd.yml."""
        mock_exists.return_value = True
        
        scripts = self.script_runner.list_scripts()
        
        assert 'start' in scripts
        assert scripts['start'] == 'codex hello.prompt.md'


class TestPromptCompiler:
    """Test PromptCompiler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = PromptCompiler()
    
    def test_substitute_parameters_simple(self):
        """Test simple parameter substitution."""
        content = "Hello ${input:name}!"
        params = {"name": "World"}
        
        result = self.compiler._substitute_parameters(content, params)
        
        assert result == "Hello World!"
    
    def test_substitute_parameters_multiple(self):
        """Test multiple parameter substitution."""
        content = "Service: ${input:service}, Environment: ${input:env}"
        params = {"service": "api", "env": "production"}
        
        result = self.compiler._substitute_parameters(content, params)
        
        assert result == "Service: api, Environment: production"
    
    def test_substitute_parameters_no_params(self):
        """Test content with no parameters to substitute."""
        content = "This is a simple prompt with no parameters."
        params = {}
        
        result = self.compiler._substitute_parameters(content, params)
        
        assert result == content
    
    def test_substitute_parameters_missing_param(self):
        """Test behavior when parameter is missing."""
        content = "Hello ${input:name}!"
        params = {}
        
        result = self.compiler._substitute_parameters(content, params)
        
        # Should leave placeholder unchanged when parameter is missing
        assert result == "Hello ${input:name}!"
    
    @patch('awd_cli.core.script_runner.Path.mkdir')
    @patch('awd_cli.core.script_runner.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_compile_with_frontmatter(self, mock_file, mock_exists, mock_mkdir):
        """Test compiling prompt file with frontmatter."""
        mock_exists.return_value = True
        
        # Mock file content with frontmatter
        file_content = """---
description: Test prompt
input:
  - name
---

# Test Prompt

Hello ${input:name}!"""
        
        mock_file.return_value.read.return_value = file_content
        
        result_path = self.compiler.compile("test.prompt.md", {"name": "World"})
        
        # Check that the compiled content was written correctly
        mock_file.return_value.write.assert_called_once()
        written_content = mock_file.return_value.write.call_args[0][0]
        assert "Hello World!" in written_content
        assert "---" not in written_content  # Frontmatter should be stripped
    
    @patch('awd_cli.core.script_runner.Path.mkdir')
    @patch('awd_cli.core.script_runner.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_compile_without_frontmatter(self, mock_file, mock_exists, mock_mkdir):
        """Test compiling prompt file without frontmatter."""
        mock_exists.return_value = True
        
        # Mock file content without frontmatter
        file_content = "Hello ${input:name}!"
        mock_file.return_value.read.return_value = file_content
        
        result_path = self.compiler.compile("test.prompt.md", {"name": "World"})
        
        # Check that the compiled content was written correctly
        mock_file.return_value.write.assert_called_once()
        written_content = mock_file.return_value.write.call_args[0][0]
        assert written_content == "Hello World!"
    
    @patch('awd_cli.core.script_runner.Path.exists')
    def test_compile_file_not_found(self, mock_exists):
        """Test compiling non-existent prompt file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Prompt file not found"):
            self.compiler.compile("nonexistent.prompt.md", {})
