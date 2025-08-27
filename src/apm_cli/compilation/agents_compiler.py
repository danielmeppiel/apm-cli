"""Main compilation orchestration for AGENTS.md generation."""

import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..primitives.models import PrimitiveCollection
from ..primitives.discovery import discover_primitives
from ..version import get_version
from .template_builder import (
    build_conditional_sections,
    generate_agents_md_template,
    TemplateData,
    find_chatmode_by_name
)
from .link_resolver import resolve_markdown_links, validate_link_targets


@dataclass
class CompilationConfig:
    """Configuration for AGENTS.md compilation."""
    output_path: str = "AGENTS.md"
    chatmode: Optional[str] = None
    resolve_links: bool = True
    dry_run: bool = False
    
    @classmethod
    def from_apm_yml(cls, **overrides) -> 'CompilationConfig':
        """Create configuration from apm.yml with command-line overrides.
        
        Args:
            **overrides: Command-line arguments that override config file values.
            
        Returns:
            CompilationConfig: Configuration with apm.yml values and overrides applied.
        """
        config = cls()
        
        # Try to load from apm.yml
        try:
            from pathlib import Path
            import yaml
            
            if Path('apm.yml').exists():
                with open('apm.yml', 'r') as f:
                    apm_config = yaml.safe_load(f) or {}
                
                # Look for compilation section
                compilation_config = apm_config.get('compilation', {})
                
                # Apply config file values
                if 'output' in compilation_config:
                    config.output_path = compilation_config['output']
                if 'chatmode' in compilation_config:
                    config.chatmode = compilation_config['chatmode']
                if 'resolve_links' in compilation_config:
                    config.resolve_links = compilation_config['resolve_links']
                
        except Exception:
            # If config loading fails, use defaults
            pass
        
        # Apply command-line overrides (highest priority)
        for key, value in overrides.items():
            if value is not None:  # Only override if explicitly provided
                setattr(config, key, value)
        
        return config


@dataclass
class CompilationResult:
    """Result of AGENTS.md compilation."""
    success: bool
    output_path: str
    content: str
    warnings: List[str]
    errors: List[str]
    stats: Dict[str, Any]


class AgentsCompiler:
    """Main compiler for generating AGENTS.md files."""
    
    def __init__(self, base_dir: str = "."):
        """Initialize the compiler.
        
        Args:
            base_dir (str): Base directory for compilation. Defaults to current directory.
        """
        self.base_dir = Path(base_dir)
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def compile(self, config: CompilationConfig, primitives: Optional[PrimitiveCollection] = None) -> CompilationResult:
        """Compile AGENTS.md with the given configuration.
        
        Args:
            config (CompilationConfig): Compilation configuration.
            primitives (Optional[PrimitiveCollection]): Primitives to use, or None to discover.
        
        Returns:
            CompilationResult: Result of the compilation.
        """
        self.warnings.clear()
        self.errors.clear()
        
        try:
            # Use provided primitives or discover them
            if primitives is None:
                primitives = discover_primitives(str(self.base_dir))
            
            # Validate primitives
            validation_errors = self.validate_primitives(primitives)
            if validation_errors:
                self.errors.extend(validation_errors)
            
            # Generate template data
            template_data = self._generate_template_data(primitives, config)
            
            # Generate final output
            content = self.generate_output(template_data, config)
            
            # Write output file (unless dry run)
            output_path = str(self.base_dir / config.output_path)
            if not config.dry_run:
                self._write_output_file(output_path, content)
            
            # Compile statistics
            stats = self._compile_stats(primitives, template_data)
            
            return CompilationResult(
                success=len(self.errors) == 0,
                output_path=output_path,
                content=content,
                warnings=self.warnings.copy(),
                errors=self.errors.copy(),
                stats=stats
            )
            
        except Exception as e:
            self.errors.append(f"Compilation failed: {str(e)}")
            return CompilationResult(
                success=False,
                output_path="",
                content="",
                warnings=self.warnings.copy(),
                errors=self.errors.copy(),
                stats={}
            )
    
    def validate_primitives(self, primitives: PrimitiveCollection) -> List[str]:
        """Validate primitives for compilation.
        
        Args:
            primitives (PrimitiveCollection): Collection of primitives to validate.
        
        Returns:
            List[str]: List of validation errors.
        """
        errors = []
        
        # Validate each primitive
        for primitive in primitives.all_primitives():
            primitive_errors = primitive.validate()
            if primitive_errors:
                try:
                    # Try to get relative path, but fall back to absolute if it fails
                    file_path = str(primitive.file_path.relative_to(self.base_dir))
                except ValueError:
                    # File is outside base_dir, use absolute path
                    file_path = str(primitive.file_path)
                
                for error in primitive_errors:
                    # Treat validation errors as warnings instead of hard errors
                    # This allows compilation to continue with incomplete primitives
                    self.warnings.append(f"{file_path}: {error}")
            
            # Validate markdown links in each primitive's content using its own directory as base
            if hasattr(primitive, 'content') and primitive.content:
                primitive_dir = primitive.file_path.parent
                link_errors = validate_link_targets(primitive.content, primitive_dir)
                if link_errors:
                    try:
                        file_path = str(primitive.file_path.relative_to(self.base_dir))
                    except ValueError:
                        file_path = str(primitive.file_path)
                    
                    for link_error in link_errors:
                        self.warnings.append(f"{file_path}: {link_error}")
        
        return errors
    
    def generate_output(self, template_data: TemplateData, config: CompilationConfig) -> str:
        """Generate the final AGENTS.md output.
        
        Args:
            template_data (TemplateData): Data for template generation.
            config (CompilationConfig): Compilation configuration.
        
        Returns:
            str: Generated AGENTS.md content.
        """
        content = generate_agents_md_template(template_data)
        
        # Resolve markdown links if enabled
        if config.resolve_links:
            content = resolve_markdown_links(content, self.base_dir)
        
        return content
    
    def _generate_template_data(self, primitives: PrimitiveCollection, config: CompilationConfig) -> TemplateData:
        """Generate template data from primitives and configuration.
        
        Args:
            primitives (PrimitiveCollection): Discovered primitives.
            config (CompilationConfig): Compilation configuration.
        
        Returns:
            TemplateData: Template data for generation.
        """
        # Build instructions content
        instructions_content = build_conditional_sections(primitives.instructions)
        
        # Generate metadata
        timestamp = datetime.datetime.now().isoformat()
        version = get_version()
        
        # Handle chatmode content
        chatmode_content = None
        if config.chatmode:
            chatmode = find_chatmode_by_name(primitives.chatmodes, config.chatmode)
            if chatmode:
                chatmode_content = chatmode.content
            else:
                self.warnings.append(f"Chatmode '{config.chatmode}' not found")
        
        return TemplateData(
            instructions_content=instructions_content,
            timestamp=timestamp,
            version=version,
            chatmode_content=chatmode_content
        )
    
    def _write_output_file(self, output_path: str, content: str) -> None:
        """Write the generated content to the output file.
        
        Args:
            output_path (str): Path to write the output.
            content (str): Content to write.
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except OSError as e:
            self.errors.append(f"Failed to write output file {output_path}: {str(e)}")
    
    def _compile_stats(self, primitives: PrimitiveCollection, template_data: TemplateData) -> Dict[str, Any]:
        """Compile statistics about the compilation.
        
        Args:
            primitives (PrimitiveCollection): Discovered primitives.
            template_data (TemplateData): Generated template data.
        
        Returns:
            Dict[str, Any]: Compilation statistics.
        """
        return {
            "primitives_found": primitives.count(),
            "chatmodes": len(primitives.chatmodes),
            "instructions": len(primitives.instructions),
            "contexts": len(primitives.contexts),
            "content_length": len(template_data.instructions_content),
            "timestamp": template_data.timestamp,
            "version": template_data.version
        }


def compile_agents_md(
    primitives: Optional[PrimitiveCollection] = None,
    output_path: str = "AGENTS.md",
    chatmode: Optional[str] = None,
    dry_run: bool = False,
    base_dir: str = "."
) -> str:
    """Generate AGENTS.md with conditional sections.
    
    Args:
        primitives (Optional[PrimitiveCollection]): Primitives to use, or None to discover.
        output_path (str): Output file path. Defaults to "AGENTS.md".
        chatmode (str): Specific chatmode to use, or None for default.
        dry_run (bool): If True, don't write output file. Defaults to False.
        base_dir (str): Base directory for compilation. Defaults to current directory.
    
    Returns:
        str: Generated AGENTS.md content.
    """
    # Create configuration
    config = CompilationConfig(
        output_path=output_path,
        chatmode=chatmode,
        dry_run=dry_run
    )
    
    # Create compiler and compile
    compiler = AgentsCompiler(base_dir)
    result = compiler.compile(config, primitives)
    
    if not result.success:
        raise RuntimeError(f"Compilation failed: {'; '.join(result.errors)}")
    
    return result.content