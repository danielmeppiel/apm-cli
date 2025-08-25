"""Unit tests for the compilation module."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import re
from urllib.parse import urlparse

from awd_cli.compilation.project_detector import (
    detect_project_type,
    auto_detect_setup_commands,
    generate_setup_section,
    ProjectType,
    SetupCommand
)
from awd_cli.compilation.template_builder import (
    build_conditional_sections,
    build_chatmode_sections,
    build_workflow_listing,
    _pattern_to_description
)
from awd_cli.compilation.link_resolver import (
    resolve_markdown_links,
    validate_link_targets,
    _remove_frontmatter
)
from awd_cli.compilation.agents_compiler import (
    AgentsCompiler,
    CompilationConfig,
    compile_agents_md
)
from awd_cli.primitives.models import Instruction, Chatmode, Context, PrimitiveCollection


class TestProjectDetector(unittest.TestCase):
    """Test project detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_python_project(self):
        """Test Python project detection."""
        # Create pyproject.toml
        (self.temp_path / 'pyproject.toml').write_text('[build-system]\nrequires = ["setuptools"]')
        
        project_type = detect_project_type(str(self.temp_path))
        self.assertEqual(project_type, ProjectType.PYTHON)

    def test_detect_nodejs_project(self):
        """Test Node.js project detection."""
        # Create package.json
        (self.temp_path / 'package.json').write_text('{"name": "test"}')
        
        project_type = detect_project_type(str(self.temp_path))
        self.assertEqual(project_type, ProjectType.NODEJS)

    def test_detect_unknown_project(self):
        """Test unknown project type."""
        project_type = detect_project_type(str(self.temp_path))
        self.assertEqual(project_type, ProjectType.UNKNOWN)

    def test_auto_detect_python_setup_commands(self):
        """Test Python setup command detection."""
        # Create pyproject.toml
        (self.temp_path / 'pyproject.toml').write_text('[build-system]\nrequires = ["setuptools"]')
        
        commands = auto_detect_setup_commands(str(self.temp_path))
        self.assertGreater(len(commands), 0)
        self.assertTrue(any('uv' in cmd.command for cmd in commands))

    def test_generate_setup_section(self):
        """Test setup section generation."""
        commands = [
            SetupCommand("npm install", "Install dependencies", priority=1),
            SetupCommand("npm test", "Run tests", priority=2)
        ]
        
        section = generate_setup_section(commands)
        self.assertIn("Project Setup", section)
        self.assertIn("npm install", section)
        self.assertIn("npm test", section)


class TestTemplateBuilder(unittest.TestCase):
    """Test template building functionality."""

    def test_pattern_to_description(self):
        """Test pattern to description conversion."""
        test_cases = [
            ('**/*.py', 'Python files'),  # Corrected back
            ('**/*.{ts,tsx}', 'TypeScript files'),  # Correct implementation match
            ('**/*test*', 'test files'),
            ('src/awd_cli/cli.py', 'CLI implementation files')
        ]
        
        for pattern, expected in test_cases:
            with self.subTest(pattern=pattern):
                result = _pattern_to_description(pattern)
                self.assertEqual(result, expected)

    def test_build_conditional_sections(self):
        """Test conditional sections building."""
        instructions = [
            Instruction(
                name="python-rules",
                file_path=Path("test.instructions.md"),
                description="Python guidelines",
                apply_to="**/*.py",
                content="Use Python best practices"
            ),
            Instruction(
                name="test-rules", 
                file_path=Path("test2.instructions.md"),
                description="Test guidelines",
                apply_to="**/*test*",
                content="Write comprehensive tests"
            )
        ]
        
        result = build_conditional_sections(instructions)
        self.assertIn("Development Guidelines", result)
        self.assertIn("When working on Python files", result)
        self.assertIn("When working on test files", result)
        self.assertIn("Use Python best practices", result)
        self.assertIn("Write comprehensive tests", result)

    def test_build_chatmode_sections(self):
        """Test chatmode sections building."""
        chatmodes = [
            Chatmode(
                name="architect",
                file_path=Path("architect.chatmode.md"),
                description="Software architect assistant",
                apply_to=None,
                content="You are a software architect"
            )
        ]
        
        result = build_chatmode_sections(chatmodes)
        self.assertIn("Development Approach", result)
        self.assertIn("Software architect assistant", result)
        self.assertIn("You are a software architect", result)

    def test_build_workflow_listing(self):
        """Test workflow listing building."""
        prompt_files = [
            Path("test1.prompt.md"),
            Path("test2.prompt.md")
        ]
        
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.return_value = "---\ndescription: Test workflow\n---\n# Test"
            
            result = build_workflow_listing(prompt_files)
            self.assertIn("Available Workflows", result)
            self.assertIn("test1.prompt.md", result)
            self.assertIn("test2.prompt.md", result)


class TestLinkResolver(unittest.TestCase):
    """Test link resolution functionality."""

    def test_remove_frontmatter(self):
        """Test frontmatter removal."""
        content_with_frontmatter = """---
title: Test
description: A test file
---

# Content

This is the actual content."""
        
        result = _remove_frontmatter(content_with_frontmatter)
        self.assertNotIn("---", result)
        self.assertIn("# Content", result)
        self.assertIn("This is the actual content.", result)

    def test_validate_link_targets_with_valid_links(self):
        """Test link validation with valid links."""
        content = "[External link](https://example.com) and [Anchor](#section)"
        
        errors = validate_link_targets(content, Path("."))
        # External URLs and anchors should not generate errors
        def is_example_com_error(e):
            # Find all URLs in the error message
            urls = re.findall(r'https?://[^\s)]+', e)
            for url in urls:
                host = urlparse(url).hostname
                if host == "example.com":
                    return True
            return False
        self.assertEqual(len([e for e in errors if is_example_com_error(e) or '#section' in e]), 0)

    def test_validate_link_targets_with_missing_files(self):
        """Test link validation with missing files."""
        content = "[Missing file](nonexistent.md)"
        
        errors = validate_link_targets(content, Path("."))
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('nonexistent.md' in error for error in errors))


class TestAgentsCompiler(unittest.TestCase):
    """Test the main agents compiler."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.compiler = AgentsCompiler(str(self.temp_path))

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compilation_config(self):
        """Test compilation configuration."""
        config = CompilationConfig(
            output_path="test.md",
            chatmode="test-mode",
            dry_run=True
        )
        
        self.assertEqual(config.output_path, "test.md")
        self.assertEqual(config.chatmode, "test-mode")
        self.assertTrue(config.dry_run)

    def test_validate_primitives(self):
        """Test primitive validation."""
        # Create a valid primitive
        valid_instruction = Instruction(
            name="valid",
            file_path=Path("valid.instructions.md"),
            description="Valid instruction",
            apply_to="**/*.py",
            content="Valid content"
        )
        
        # Create an invalid primitive (missing description)
        invalid_instruction = Instruction(
            name="invalid",
            file_path=Path("invalid.instructions.md"),
            description="",  # Missing description
            apply_to="**/*.py",
            content="Content"
        )
        
        collection = PrimitiveCollection()
        collection.add_primitive(valid_instruction)
        collection.add_primitive(invalid_instruction)
        
        # Validation should report warnings for invalid primitives
        errors = self.compiler.validate_primitives(collection)
        self.assertEqual(len(errors), 0)  # No hard errors
        self.assertGreater(len(self.compiler.warnings), 0)  # But warnings should be present

    @patch('awd_cli.compilation.agents_compiler.discover_primitives')
    def test_compile_with_mock_primitives(self, mock_discover):
        """Test compilation with mocked primitives."""
        # Create mock primitives
        mock_collection = PrimitiveCollection()
        mock_collection.add_primitive(Chatmode(
            name="test",
            file_path=Path("test.chatmode.md"),
            description="Test chatmode",
            apply_to=None,
            content="You are a test assistant"
        ))
        
        mock_discover.return_value = mock_collection
        
        config = CompilationConfig(dry_run=True)
        result = self.compiler.compile(config)
        
        self.assertTrue(result.success)
        self.assertIn("Development Approach", result.content)
        self.assertIn("You are a test assistant", result.content)

    def test_compile_agents_md_function(self):
        """Test the standalone compile_agents_md function.""" 
        # Create a minimal primitive collection
        collection = PrimitiveCollection()
        collection.add_primitive(Chatmode(
            name="test",
            file_path=Path("test.chatmode.md"),
            description="Test",
            apply_to=None,
            content="Test content"
        ))
        
        result = compile_agents_md(
            primitives=collection,
            dry_run=True,
            base_dir=str(self.temp_path)
        )
        
        self.assertIn("AGENTS.md", result)
        self.assertIn("Test content", result)


if __name__ == '__main__':
    unittest.main()