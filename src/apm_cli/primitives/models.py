"""Data models for APM primitives."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Union


@dataclass
class Chatmode:
    """Represents a chatmode primitive."""
    name: str
    file_path: Path
    description: str
    apply_to: Optional[str]  # Glob pattern for file targeting (optional for chatmodes)
    content: str
    author: Optional[str] = None
    version: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate chatmode structure.
        
        Returns:
            List[str]: List of validation errors.
        """
        errors = []
        if not self.description:
            errors.append("Missing 'description' in frontmatter")
        if not self.content.strip():
            errors.append("Empty content")
        return errors


@dataclass
class Instruction:
    """Represents an instruction primitive."""
    name: str
    file_path: Path
    description: str
    apply_to: str  # Glob pattern for file targeting (required for instructions)
    content: str
    author: Optional[str] = None
    version: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate instruction structure.
        
        Returns:
            List[str]: List of validation errors.
        """
        errors = []
        if not self.description:
            errors.append("Missing 'description' in frontmatter")
        if not self.apply_to:
            errors.append("Missing 'applyTo' in frontmatter (required for instructions)")
        if not self.content.strip():
            errors.append("Empty content")
        return errors


@dataclass
class Context:
    """Represents a context primitive."""
    name: str
    file_path: Path
    content: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate context structure.
        
        Returns:
            List[str]: List of validation errors.
        """
        errors = []
        if not self.content.strip():
            errors.append("Empty content")
        return errors


# Union type for all primitive types
Primitive = Union[Chatmode, Instruction, Context]


@dataclass
class PrimitiveCollection:
    """Collection of discovered primitives."""
    chatmodes: List[Chatmode]
    instructions: List[Instruction]
    contexts: List[Context]
    
    def __init__(self):
        self.chatmodes = []
        self.instructions = []
        self.contexts = []
    
    def add_primitive(self, primitive: Primitive) -> None:
        """Add a primitive to the appropriate collection."""
        if isinstance(primitive, Chatmode):
            self.chatmodes.append(primitive)
        elif isinstance(primitive, Instruction):
            self.instructions.append(primitive)
        elif isinstance(primitive, Context):
            self.contexts.append(primitive)
        else:
            raise ValueError(f"Unknown primitive type: {type(primitive)}")
    
    def all_primitives(self) -> List[Primitive]:
        """Get all primitives as a single list."""
        return self.chatmodes + self.instructions + self.contexts
    
    def count(self) -> int:
        """Get total count of all primitives."""
        return len(self.chatmodes) + len(self.instructions) + len(self.contexts)