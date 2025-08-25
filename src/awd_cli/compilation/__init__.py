"""AWD compilation module for generating AGENTS.md files."""

from .agents_compiler import AgentsCompiler, compile_agents_md, CompilationConfig, CompilationResult
from .template_builder import (
    build_conditional_sections,
    build_chatmode_sections,
    build_workflow_listing,
    TemplateData
)
from .project_detector import (
    auto_detect_setup_commands,
    detect_project_type,
    generate_setup_section,
    ProjectType,
    SetupCommand
)
from .link_resolver import (
    resolve_markdown_links,
    resolve_spec_references,
    validate_link_targets
)

__all__ = [
    # Main compilation interface
    'AgentsCompiler',
    'compile_agents_md',
    'CompilationConfig',
    'CompilationResult',
    
    # Template building
    'build_conditional_sections',
    'build_chatmode_sections', 
    'build_workflow_listing',
    'TemplateData',
    
    # Project detection
    'auto_detect_setup_commands',
    'detect_project_type',
    'generate_setup_section',
    'ProjectType',
    'SetupCommand',
    
    # Link resolution
    'resolve_markdown_links',
    'resolve_spec_references',
    'validate_link_targets'
]