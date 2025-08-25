"""Template building system for AGENTS.md compilation."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from ..primitives.models import Instruction, Chatmode


@dataclass
class TemplateData:
    """Data structure for template generation."""
    chatmode_content: str
    setup_content: str
    instructions_content: str
    workflows_content: str
    timestamp: str
    version: str
    

def build_conditional_sections(instructions: List[Instruction]) -> str:
    """Build 'When working on...' sections grouped by applyTo patterns.
    
    Args:
        instructions (List[Instruction]): List of instruction primitives.
    
    Returns:
        str: Formatted conditional sections content.
    """
    if not instructions:
        return ""
    
    # Group instructions by pattern and create descriptive names
    pattern_groups = _group_instructions_by_pattern(instructions)
    
    sections = []
    sections.append("## Development Guidelines")
    sections.append("")
    
    for pattern_desc, pattern_instructions in pattern_groups.items():
        sections.append(f"### When working on {pattern_desc}")
        sections.append("")
        
        # Combine content from all instructions for this pattern
        combined_content = []
        for instruction in pattern_instructions:
            content = instruction.content.strip()
            if content:
                combined_content.append(content)
        
        if combined_content:
            sections.append("\n\n".join(combined_content))
            sections.append("")
    
    return "\n".join(sections)


def build_chatmode_sections(chatmodes: List[Chatmode], selected_mode: Optional[str] = None) -> str:
    """Build chatmode sections or single selected mode.
    
    Args:
        chatmodes (List[Chatmode]): List of chatmode primitives.
        selected_mode (Optional[str]): Specific chatmode to use, or None for default.
    
    Returns:
        str: Formatted chatmode content.
    """
    if not chatmodes:
        return _generate_default_approach()
    
    # If specific mode requested, use that
    if selected_mode:
        for chatmode in chatmodes:
            if chatmode.name == selected_mode:
                return _format_chatmode_content(chatmode)
        # If requested mode not found, fall back to default logic
    
    # Find default chatmode (one without applyTo pattern, or first one)
    default_chatmode = None
    for chatmode in chatmodes:
        if not chatmode.apply_to:
            default_chatmode = chatmode
            break
    
    if not default_chatmode and chatmodes:
        default_chatmode = chatmodes[0]
    
    if default_chatmode:
        return _format_chatmode_content(default_chatmode)
    
    return _generate_default_approach()


def build_workflow_listing(prompt_files: List[Path]) -> str:
    """Build available workflows section from .prompt.md files.
    
    Args:
        prompt_files (List[Path]): List of .prompt.md files found in the project.
    
    Returns:
        str: Formatted workflows section content.
    """
    if not prompt_files:
        return ""
    
    sections = []
    sections.append("## Available Workflows")
    sections.append("")
    
    for prompt_file in prompt_files:
        # Extract name and description
        name = prompt_file.stem
        if name.endswith('.prompt'):
            name = name[:-7]  # Remove .prompt suffix
        
        description = _extract_workflow_description(prompt_file)
        
        sections.append(f"- `awd run {prompt_file.name}` - {description}")
    
    sections.append("")
    return "\n".join(sections)


def _group_instructions_by_pattern(instructions: List[Instruction]) -> Dict[str, List[Instruction]]:
    """Group instructions by applyTo patterns with descriptive names.
    
    Args:
        instructions (List[Instruction]): List of instructions to group.
    
    Returns:
        Dict[str, List[Instruction]]: Grouped instructions with descriptive keys.
    """
    pattern_groups: Dict[str, List[Instruction]] = {}
    
    for instruction in instructions:
        if not instruction.apply_to:
            continue
        
        pattern_desc = _pattern_to_description(instruction.apply_to)
        
        if pattern_desc not in pattern_groups:
            pattern_groups[pattern_desc] = []
        
        pattern_groups[pattern_desc].append(instruction)
    
    return pattern_groups


def _pattern_to_description(pattern: str) -> str:
    """Convert a glob pattern to a human-readable description.
    
    Args:
        pattern (str): Glob pattern to convert.
    
    Returns:
        str: Human-readable description.
    """
    # Common pattern mappings
    pattern_mappings = {
        # TypeScript/JavaScript
        '**/*.ts': 'TypeScript files',
        '**/*.tsx': 'TypeScript React files',
        '**/*.js': 'JavaScript files',
        '**/*.jsx': 'JavaScript React files',
        '**/*.{ts,tsx}': 'TypeScript files',
        '**/*.{js,jsx}': 'JavaScript files',
        
        # Python
        '**/*.py': 'Python files',
        
        # Test files
        '**/*test*': 'test files',
        '**/*spec*': 'test files',
        '**/*.test.*': 'test files',
        '**/*.spec.*': 'test files',
        '**/test_*.py': 'Python test files',
        '**/tests/**': 'test files',
        
        # Configuration
        '**/*.json': 'JSON configuration files',
        '**/*.yaml': 'YAML configuration files',
        '**/*.yml': 'YAML configuration files',
        '**/*.toml': 'TOML configuration files',
        
        # Documentation
        '**/*.md': 'Markdown documentation files',
        '**/*.rst': 'reStructuredText documentation files',
        
        # Rust
        '**/*.rs': 'Rust files',
        
        # Go
        '**/*.go': 'Go files',
        
        # Java
        '**/*.java': 'Java files',
        
        # C/C++
        '**/*.c': 'C files',
        '**/*.cpp': 'C++ files',
        '**/*.h': 'header files',
        '**/*.hpp': 'C++ header files',
        
        # CSS/Styling
        '**/*.css': 'CSS files',
        '**/*.scss': 'SASS files',
        '**/*.less': 'LESS files',
        
        # CLI files
        'src/awd_cli/cli.py': 'CLI implementation files',
    }
    
    # Check for exact matches first
    if pattern in pattern_mappings:
        return pattern_mappings[pattern]
    
    # Try to infer from pattern structure
    pattern_lower = pattern.lower()
    
    # Check for file extension patterns
    ext_match = re.search(r'\*\.(\w+)$', pattern)
    if ext_match:
        ext = ext_match.group(1)
        return f"{ext.upper()} files"
    
    # Check for multiple extensions
    multi_ext_match = re.search(r'\{([^}]+)\}', pattern)
    if multi_ext_match:
        extensions = multi_ext_match.group(1).split(',')
        ext_list = [ext.strip() for ext in extensions]
        if len(ext_list) == 2:
            return f"{ext_list[0]} and {ext_list[1]} files"
        elif len(ext_list) > 2:
            return f"{', '.join(ext_list[:-1])}, and {ext_list[-1]} files"
    
    # Check for directory patterns
    if 'test' in pattern_lower:
        return 'test files'
    if 'spec' in pattern_lower:
        return 'specification files'
    if 'doc' in pattern_lower:
        return 'documentation files'
    if 'config' in pattern_lower:
        return 'configuration files'
    
    # Fall back to the raw pattern
    return f"files matching `{pattern}`"


def _format_chatmode_content(chatmode: Chatmode) -> str:
    """Format a chatmode into the development approach section.
    
    Args:
        chatmode (Chatmode): Chatmode to format.
    
    Returns:
        str: Formatted chatmode content.
    """
    sections = []
    sections.append("## Development Approach")
    sections.append("")
    
    # Add description if available
    if chatmode.description:
        sections.append(f"*{chatmode.description}*")
        sections.append("")
    
    # Add main content
    sections.append(chatmode.content.strip())
    sections.append("")
    
    return "\n".join(sections)


def _generate_default_approach() -> str:
    """Generate a default development approach when no chatmodes are found.
    
    Returns:
        str: Default development approach content.
    """
    return """## Development Approach

You are an AI assistant helping with software development. Please:

- Follow the project's existing code style and patterns
- Write clear, well-documented code
- Include appropriate tests for new functionality
- Consider security and performance implications
- Ask for clarification when requirements are unclear

"""


def _extract_workflow_description(prompt_file: Path) -> str:
    """Extract description from a workflow prompt file.
    
    Args:
        prompt_file (Path): Path to the prompt file.
    
    Returns:
        str: Description of the workflow or default text.
    """
    try:
        content = prompt_file.read_text(encoding='utf-8')
        
        # Try to extract from frontmatter
        if content.startswith('---\n'):
            lines = content.split('\n')
            in_frontmatter = True
            
            for line in lines[1:]:
                if line.strip() == '---':
                    break
                if line.startswith('description:'):
                    desc = line[12:].strip()
                    # Remove quotes if present
                    if desc.startswith('"') and desc.endswith('"'):
                        desc = desc[1:-1]
                    elif desc.startswith("'") and desc.endswith("'"):
                        desc = desc[1:-1]
                    return desc
        
        # Try to extract from first H1 heading
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fall back to generic description
        return "Workflow automation"
        
    except (OSError, UnicodeDecodeError):
        return "Workflow automation"


def generate_agents_md_template(template_data: TemplateData) -> str:
    """Generate the complete AGENTS.md file content.
    
    Args:
        template_data (TemplateData): Data for template generation.
    
    Returns:
        str: Complete AGENTS.md file content.
    """
    sections = []
    
    # Header
    sections.append("# AGENTS.md")
    sections.append(f"<!-- Generated by AWD CLI from .awd/ primitives -->")
    sections.append(f"<!-- Generated on: {template_data.timestamp} -->")
    sections.append(f"<!-- AWD Version: {template_data.version} -->")
    sections.append("")
    
    # Development Approach (from chatmode)
    if template_data.chatmode_content:
        sections.append(template_data.chatmode_content)
    
    # Project Setup
    if template_data.setup_content:
        sections.append(template_data.setup_content)
    
    # Development Guidelines (from instructions)
    if template_data.instructions_content:
        sections.append(template_data.instructions_content)
    
    # Available Workflows
    if template_data.workflows_content:
        sections.append(template_data.workflows_content)
    
    # Footer
    sections.append("---")
    sections.append("*This file was generated by AWD CLI. Do not edit manually.*")
    sections.append("*To regenerate: `awd compile`*")
    sections.append("")
    
    return "\n".join(sections)