"""Unit tests for the simplified compilation module."""

import os
import tempfile
import unittest
import yaml
from pathlib import Path
from unittest.mock import patch

from apm_cli.compilation.template_builder import (
    build_conditional_sections,
)
from apm_cli.compilation.link_resolver import (
    validate_link_targets,
)
from apm_cli.compilation.agents_compiler import (
    AgentsCompiler,
    CompilationConfig,
    compile_agents_md
)
from apm_cli.primitives.models import Instruction, Chatmode, PrimitiveCollection


class TestTemplateBuilder(unittest.TestCase):
    """Test template building functionality."""

    def test_build_conditional_sections(self):
        """Test building conditional sections from instructions."""
        # Create test instructions
        instructions = [
            Instruction(
                name="python_test",
                file_path=Path("test.md"),
                description="Python instructions",
                apply_to="**/*.py",
                content="Use type hints and follow PEP 8.",
                author="test",
                version="1.0"
            ),
            Instruction(
                name="js_test",
                file_path=Path("test2.md"),
                description="JavaScript instructions",
                apply_to="**/*.js",
                content="Use ES6+ features and proper formatting.",
                author="test",
                version="1.0"
            ),
            Instruction(
                name="python_test2",
                file_path=Path("test3.md"),
                description="More Python instructions",
                apply_to="**/*.py",
                content="Write comprehensive docstrings.",
                author="test",
                version="1.0"
            )
        ]
        
        result = build_conditional_sections(instructions)
        
        # Should group by pattern
        self.assertIn("## Files matching `**/*.py`", result)
        self.assertIn("## Files matching `**/*.js`", result)
        self.assertIn("Use type hints and follow PEP 8.", result)
        self.assertIn("Write comprehensive docstrings.", result)
        self.assertIn("Use ES6+ features and proper formatting.", result)

    def test_build_conditional_sections_empty(self):
        """Test building conditional sections with no instructions."""
        result = build_conditional_sections([])
        self.assertEqual(result, "")


class TestLinkResolver(unittest.TestCase):
    """Test link resolution functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_link_targets_with_valid_links(self):
        """Test link validation with valid file targets."""
        # Create test files
        (self.temp_path / "README.md").write_text("# Test README")
        (self.temp_path / "CONTRIBUTING.md").write_text("# Contributing")
        
        content = """
        See [README](README.md) and [Contributing](CONTRIBUTING.md).
        """
        
        errors = validate_link_targets(content, self.temp_path)
        self.assertEqual(len(errors), 0)

    def test_validate_link_targets_with_missing_files(self):
        """Test link validation with missing file targets."""
        content = """
        See [Missing](missing.md) file.
        """
        
        errors = validate_link_targets(content, self.temp_path)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing.md", errors[0])


class TestAgentsCompiler(unittest.TestCase):
    """Test main compilation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compilation_config(self):
        """Test compilation configuration."""
        config = CompilationConfig(
            output_path="test.md",
            dry_run=True,
            resolve_links=False
        )
        
        self.assertEqual(config.output_path, "test.md")
        self.assertTrue(config.dry_run)
        self.assertFalse(config.resolve_links)

    def test_validate_primitives(self):
        """Test primitive validation."""
        compiler = AgentsCompiler(str(self.temp_path))
        
        # Create test primitives
        primitives = PrimitiveCollection()
        
        # Valid instruction
        valid_instruction = Instruction(
            name="test",
            file_path=self.temp_path / "test.md",
            description="Test instruction",
            apply_to="**/*.py",
            content="Test content",
            author="test"
        )
        primitives.add_primitive(valid_instruction)
        
        # Test validation (should return empty error list since we use warnings)
        errors = compiler.validate_primitives(primitives)
        self.assertEqual(len(errors), 0)

    @patch('apm_cli.primitives.discovery.discover_primitives')
    def test_compile_with_mock_primitives(self, mock_discover):
        """Test compilation with mocked primitives."""
        # Create mock primitives
        primitives = PrimitiveCollection()
        
        instruction = Instruction(
            name="test",
            file_path=Path("test.md"),
            description="Test instruction",
            apply_to="**/*.py",
            content="Use type hints.",
            author="test"
        )
        primitives.add_primitive(instruction)
        
        mock_discover.return_value = primitives
        
        compiler = AgentsCompiler(str(self.temp_path))
        config = CompilationConfig(dry_run=True, resolve_links=False)
        
        # Pass primitives directly to avoid discovery
        result = compiler.compile(config, primitives)
        
        self.assertTrue(result.success)
        self.assertIn("# AGENTS.md", result.content)
        self.assertIn("Files matching `**/*.py`", result.content)
        self.assertIn("Use type hints.", result.content)

    def test_compile_agents_md_function(self):
        """Test the standalone compile function."""
        # Create test primitives
        primitives = PrimitiveCollection()
        
        instruction = Instruction(
            name="test",
            file_path=Path("test.md"),
            description="Test instruction",
            apply_to="**/*.py",
            content="Test content.",
            author="test"
        )
        primitives.add_primitive(instruction)
        
        # Test the standalone function
        content = compile_agents_md(
            primitives=primitives,
            dry_run=True,
            base_dir=str(self.temp_path)
        )
        
        self.assertIn("# AGENTS.md", content)
        self.assertIn("Files matching `**/*.py`", content)
        self.assertIn("Test content.", content)

    def test_compile_with_chatmode(self):
        """Test compilation with chatmode."""
        # Create test primitives with chatmode
        primitives = PrimitiveCollection()
        
        chatmode = Chatmode(
            name="test-chatmode",
            file_path=Path("test.chatmode.md"),
            description="Test chatmode",
            apply_to=None,
            content="You are a test assistant.",
            author="test"
        )
        primitives.add_primitive(chatmode)
        
        instruction = Instruction(
            name="test",
            file_path=Path("test.md"),
            description="Test instruction",
            apply_to="**/*.py",
            content="Use type hints.",
            author="test"
        )
        primitives.add_primitive(instruction)

        compiler = AgentsCompiler(str(self.temp_path))
        config = CompilationConfig(chatmode="test-chatmode", dry_run=True, resolve_links=False)

        result = compiler.compile(config, primitives)

        self.assertTrue(result.success)
        self.assertIn("You are a test assistant.", result.content)
        self.assertIn("Files matching `**/*.py`", result.content)
        # Chatmode should come before instructions
        chatmode_pos = result.content.find("You are a test assistant.")
        instructions_pos = result.content.find("Files matching `**/*.py`")
        self.assertTrue(chatmode_pos < instructions_pos)

    def test_compile_with_nonexistent_chatmode(self):
        """Test compilation with non-existent chatmode."""
        primitives = PrimitiveCollection()
        
        instruction = Instruction(
            name="test",
            file_path=Path("test.md"),
            description="Test instruction",
            apply_to="**/*.py",
            content="Use type hints.",
            author="test"
        )
        primitives.add_primitive(instruction)

        compiler = AgentsCompiler(str(self.temp_path))
        config = CompilationConfig(chatmode="nonexistent", dry_run=True, resolve_links=False)

        result = compiler.compile(config, primitives)

        self.assertTrue(result.success)
        self.assertIn("Chatmode 'nonexistent' not found", result.warnings)
        # Should not contain chatmode content since it wasn't found
        self.assertNotIn("You are a test assistant.", result.content)


class TestCLIIntegration(unittest.TestCase):
    """Test CLI-specific functionality for the compile command."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_mode_with_valid_primitives(self):
        """Test validation mode with valid primitives."""
        from apm_cli.cli import _display_validation_errors, _get_validation_suggestion
        
        # Test validation suggestion function
        suggestion = _get_validation_suggestion("Missing 'description' in frontmatter")
        self.assertIn("Add 'description:", suggestion)
        
        suggestion = _get_validation_suggestion("Missing 'applyTo' in frontmatter")
        self.assertIn("Add 'applyTo:", suggestion)
        
        suggestion = _get_validation_suggestion("Empty content")
        self.assertIn("Add markdown content", suggestion)
    
    def test_validation_error_display(self):
        """Test validation error display functionality."""
        from apm_cli.cli import _display_validation_errors
        
        # Test with mock errors
        errors = [
            "test.md: Missing 'description' in frontmatter",
            "other.md: Empty content"
        ]
        
        # This should not raise an exception
        try:
            _display_validation_errors(errors)
        except Exception as e:
            self.fail(f"_display_validation_errors raised an exception: {e}")
    
    def test_compilation_config_from_apm_yml(self):
        """Test CompilationConfig loading from apm.yml."""
        from apm_cli.compilation.agents_compiler import CompilationConfig
        import yaml
        
        # Create test apm.yml
        test_config = {
            'compilation': {
                'output': 'CUSTOM.md',
                'chatmode': 'test-mode',
                'resolve_links': False
            }
        }
        
        with open('apm.yml', 'w') as f:
            yaml.dump(test_config, f)
        
        # Test config loading
        config = CompilationConfig.from_apm_yml()
        self.assertEqual(config.output_path, 'CUSTOM.md')
        self.assertEqual(config.chatmode, 'test-mode')
        self.assertEqual(config.resolve_links, False)
        
        # Test with overrides
        config_with_overrides = CompilationConfig.from_apm_yml(
            output_path='OVERRIDE.md',
            chatmode='override-mode'
        )
        self.assertEqual(config_with_overrides.output_path, 'OVERRIDE.md')
        self.assertEqual(config_with_overrides.chatmode, 'override-mode')
        self.assertEqual(config_with_overrides.resolve_links, False)  # Should keep from config
        
        # Clean up
        Path('apm.yml').unlink()


if __name__ == '__main__':
    unittest.main()