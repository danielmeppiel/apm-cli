"""Unit tests for primitives parser and models."""

import os
import tempfile
import unittest
from pathlib import Path

from awd_cli.primitives.models import Chatmode, Instruction, Context, PrimitiveCollection
from awd_cli.primitives.parser import parse_primitive_file, validate_primitive, _extract_primitive_name
from awd_cli.primitives.discovery import discover_primitives, find_primitive_files


class TestPrimitiveModels(unittest.TestCase):
    """Test cases for primitive data models."""

    def test_chatmode_validation(self):
        """Test chatmode validation."""
        # Valid chatmode
        chatmode = Chatmode(
            name="test-chatmode",
            file_path=Path("test.chatmode.md"),
            description="Test chatmode",
            apply_to="**/*.py",
            content="# Test content",
            author="Test Author"
        )
        self.assertEqual(chatmode.validate(), [])
        
        # Missing description
        chatmode_no_desc = Chatmode(
            name="test",
            file_path=Path("test.chatmode.md"),
            description="",
            apply_to=None,
            content="# Test content"
        )
        errors = chatmode_no_desc.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("description", errors[0])
        
        # Empty content
        chatmode_no_content = Chatmode(
            name="test",
            file_path=Path("test.chatmode.md"),
            description="Test",
            apply_to=None,
            content=""
        )
        errors = chatmode_no_content.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("content", errors[0])

    def test_instruction_validation(self):
        """Test instruction validation."""
        # Valid instruction
        instruction = Instruction(
            name="test-instruction",
            file_path=Path("test.instructions.md"),
            description="Test instruction",
            apply_to="**/*.{ts,tsx}",
            content="# Test instruction content"
        )
        self.assertEqual(instruction.validate(), [])
        
        # Missing applyTo (required for instructions)
        instruction_no_apply = Instruction(
            name="test",
            file_path=Path("test.instructions.md"),
            description="Test",
            apply_to="",
            content="# Test content"
        )
        errors = instruction_no_apply.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("applyTo", errors[0])

    def test_context_validation(self):
        """Test context validation."""
        # Valid context
        context = Context(
            name="test-context",
            file_path=Path("test.context.md"),
            content="# Test context content"
        )
        self.assertEqual(context.validate(), [])
        
        # Empty content
        context_no_content = Context(
            name="test",
            file_path=Path("test.context.md"),
            content=""
        )
        errors = context_no_content.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("content", errors[0])

    def test_primitive_collection(self):
        """Test primitive collection functionality."""
        collection = PrimitiveCollection()
        
        # Test empty collection
        self.assertEqual(collection.count(), 0)
        self.assertEqual(len(collection.all_primitives()), 0)
        
        # Add primitives
        chatmode = Chatmode("test", Path("test.chatmode.md"), "desc", None, "content")
        instruction = Instruction("test", Path("test.instructions.md"), "desc", "**/*.py", "content")
        context = Context("test", Path("test.context.md"), "content")
        
        collection.add_primitive(chatmode)
        collection.add_primitive(instruction)
        collection.add_primitive(context)
        
        # Test counts
        self.assertEqual(collection.count(), 3)
        self.assertEqual(len(collection.chatmodes), 1)
        self.assertEqual(len(collection.instructions), 1)
        self.assertEqual(len(collection.contexts), 1)
        self.assertEqual(len(collection.all_primitives()), 3)


class TestPrimitiveParser(unittest.TestCase):
    """Test cases for the primitive parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = self.temp_dir.name

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_parse_chatmode_file(self):
        """Test parsing a chatmode file."""
        chatmode_content = """---
description: Test chatmode for code review
author: Test Author
applyTo: "**/*.{py,js}"
version: "1.0.0"
---

# Code Review Assistant

You are an expert code reviewer. Analyze the provided code for:

1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Security vulnerabilities

Provide constructive feedback and suggestions for improvement.
"""
        
        # Create test file
        file_path = os.path.join(self.temp_dir_path, "code-review.chatmode.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(chatmode_content)
        
        # Parse file
        primitive = parse_primitive_file(file_path)
        
        # Verify it's a Chatmode
        self.assertIsInstance(primitive, Chatmode)
        self.assertEqual(primitive.name, "code-review")
        self.assertEqual(primitive.description, "Test chatmode for code review")
        self.assertEqual(primitive.author, "Test Author")
        self.assertEqual(primitive.apply_to, "**/*.{py,js}")
        self.assertEqual(primitive.version, "1.0.0")
        self.assertIn("Code Review Assistant", primitive.content)
        
        # Test validation
        errors = primitive.validate()
        self.assertEqual(len(errors), 0)

    def test_parse_instruction_file(self):
        """Test parsing an instruction file."""
        instruction_content = """---
description: Python coding standards and conventions
applyTo: "**/*.py"
author: Development Team
---

# Python Coding Standards

Follow these coding standards when writing Python code:

## Style Guide
- Use PEP 8 for formatting
- Maximum line length of 88 characters
- Use type hints for function parameters and returns

## Best Practices
- Write docstrings for all public functions
- Use meaningful variable names
- Follow SOLID principles
"""
        
        # Create test file  
        file_path = os.path.join(self.temp_dir_path, "python-standards.instructions.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(instruction_content)
        
        # Parse file
        primitive = parse_primitive_file(file_path)
        
        # Verify it's an Instruction
        self.assertIsInstance(primitive, Instruction)
        self.assertEqual(primitive.name, "python-standards")
        self.assertEqual(primitive.description, "Python coding standards and conventions")
        self.assertEqual(primitive.apply_to, "**/*.py")
        self.assertEqual(primitive.author, "Development Team")
        self.assertIn("Python Coding Standards", primitive.content)
        
        # Test validation
        errors = primitive.validate()
        self.assertEqual(len(errors), 0)

    def test_parse_context_file(self):
        """Test parsing a context file."""
        context_content = """---
description: Project context and background
---

# Project Context

This project is a command-line tool for managing AI workflows.

## Architecture
- Built with Python and Click
- Uses frontmatter for file parsing
- Supports multiple runtime environments

## Key Components
- CLI interface
- Workflow engine
- Runtime management
"""
        
        # Create test file
        file_path = os.path.join(self.temp_dir_path, "project-info.context.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(context_content)
        
        # Parse file
        primitive = parse_primitive_file(file_path)
        
        # Verify it's a Context
        self.assertIsInstance(primitive, Context)
        self.assertEqual(primitive.name, "project-info")
        self.assertEqual(primitive.description, "Project context and background")
        self.assertIn("Project Context", primitive.content)
        
        # Test validation
        errors = primitive.validate()
        self.assertEqual(len(errors), 0)

    def test_extract_primitive_name(self):
        """Test primitive name extraction from various path formats."""
        # Test structured .awd/ paths
        self.assertEqual(
            _extract_primitive_name(Path(".awd/chatmodes/code-review.chatmode.md")),
            "code-review"
        )
        self.assertEqual(
            _extract_primitive_name(Path(".awd/instructions/python-style.instructions.md")),
            "python-style"
        )
        self.assertEqual(
            _extract_primitive_name(Path(".awd/context/project-info.context.md")),
            "project-info"
        )
        
        # Test .github/ paths (VSCode compatibility)
        self.assertEqual(
            _extract_primitive_name(Path(".github/chatmodes/assistant.chatmode.md")),
            "assistant"
        )
        
        # Test memory files
        self.assertEqual(
            _extract_primitive_name(Path(".awd/memory/team-info.memory.md")),
            "team-info"
        )
        
        # Test generic files
        self.assertEqual(
            _extract_primitive_name(Path("my-chatmode.chatmode.md")),
            "my-chatmode"
        )

    def test_malformed_files(self):
        """Test handling of malformed files."""
        # File with invalid YAML frontmatter
        malformed_content = """---
description: Test
invalid yaml: [
---

# Test content
"""
        
        file_path = os.path.join(self.temp_dir_path, "malformed.chatmode.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(malformed_content)
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            parse_primitive_file(file_path)


class TestPrimitiveDiscovery(unittest.TestCase):
    """Test cases for primitive discovery."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = self.temp_dir.name
        
        # Create directory structure
        os.makedirs(os.path.join(self.temp_dir_path, ".awd", "chatmodes"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir_path, ".awd", "instructions"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir_path, ".awd", "context"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir_path, ".github", "chatmodes"), exist_ok=True)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_discover_primitives_structured(self):
        """Test discovering primitives in structured directories."""
        # Create test files
        chatmode_content = """---
description: Test chatmode
---

# Test Chatmode Content
"""
        
        instruction_content = """---
description: Test instruction
applyTo: "**/*.py"
---

# Test Instruction Content
"""
        
        context_content = """---
description: Test context
---

# Test Context Content
"""
        
        # Write files
        with open(os.path.join(self.temp_dir_path, ".awd", "chatmodes", "assistant.chatmode.md"), "w") as f:
            f.write(chatmode_content)
        
        with open(os.path.join(self.temp_dir_path, ".awd", "instructions", "style.instructions.md"), "w") as f:
            f.write(instruction_content)
        
        with open(os.path.join(self.temp_dir_path, ".awd", "context", "project.context.md"), "w") as f:
            f.write(context_content)
        
        with open(os.path.join(self.temp_dir_path, ".github", "chatmodes", "vscode.chatmode.md"), "w") as f:
            f.write(chatmode_content)
        
        # Discover primitives
        collection = discover_primitives(self.temp_dir_path)
        
        # Verify discovery
        self.assertEqual(collection.count(), 4)
        self.assertEqual(len(collection.chatmodes), 2)
        self.assertEqual(len(collection.instructions), 1)
        self.assertEqual(len(collection.contexts), 1)
        
        # Check names
        chatmode_names = [c.name for c in collection.chatmodes]
        self.assertIn("assistant", chatmode_names)
        self.assertIn("vscode", chatmode_names)
        
        instruction_names = [i.name for i in collection.instructions]
        self.assertIn("style", instruction_names)
        
        context_names = [c.name for c in collection.contexts]
        self.assertIn("project", context_names)

    def test_find_primitive_files(self):
        """Test finding primitive files with glob patterns."""
        # Create test files
        os.makedirs(os.path.join(self.temp_dir_path, "custom"), exist_ok=True)
        
        test_files = [
            "test1.chatmode.md",
            "custom/test2.chatmode.md"
        ]
        
        for file_rel_path in test_files:
            file_path = os.path.join(self.temp_dir_path, file_rel_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write("---\ndescription: Test\n---\n\n# Test")
        
        # Test pattern matching  
        patterns = ["**/*.chatmode.md"]
        found_files = find_primitive_files(self.temp_dir_path, patterns)
        
        # Should find 2 files (glob doesn't match hidden directories by default)
        self.assertEqual(len(found_files), 2)
        
        # Verify all are Path objects
        for file_path in found_files:
            self.assertIsInstance(file_path, Path)
            self.assertTrue(file_path.name.endswith('.chatmode.md'))
    
    def test_find_primitive_files_specific_patterns(self):
        """Test finding primitive files with specific patterns."""
        # Test with .awd specific pattern
        awd_file = os.path.join(self.temp_dir_path, ".awd", "chatmodes", "test.chatmode.md")
        with open(awd_file, "w") as f:
            f.write("---\ndescription: Test\n---\n\n# Test")
        
        # Test .awd specific pattern
        patterns = ["**/.awd/chatmodes/*.chatmode.md"]
        found_files = find_primitive_files(self.temp_dir_path, patterns)
        
        # Should find the .awd file
        self.assertEqual(len(found_files), 1)
        self.assertTrue(found_files[0].name.endswith('.chatmode.md'))


if __name__ == '__main__':
    unittest.main()