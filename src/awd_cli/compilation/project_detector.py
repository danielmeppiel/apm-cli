"""Project setup detection for generating automatic setup sections."""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


class ProjectType(Enum):
    """Supported project types for setup detection."""
    NODEJS = "nodejs"
    PYTHON = "python"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    PHP = "php"
    UNKNOWN = "unknown"


@dataclass
class SetupCommand:
    """A setup command with description and optional conditions."""
    command: str
    description: str
    condition: Optional[str] = None  # Optional condition when this command applies
    priority: int = 0  # Lower number = higher priority


def detect_project_type(base_dir: str = ".") -> ProjectType:
    """Detect project type based on configuration files.
    
    Args:
        base_dir (str): Base directory to scan. Defaults to current directory.
    
    Returns:
        ProjectType: The detected project type or UNKNOWN if none found.
    """
    base_path = Path(base_dir)
    
    # Check for project files in order of specificity
    project_indicators = [
        # Python projects
        (ProjectType.PYTHON, ['pyproject.toml', 'requirements.txt', 'setup.py', 'poetry.lock', 'Pipfile']),
        
        # Node.js projects
        (ProjectType.NODEJS, ['package.json', 'yarn.lock', 'package-lock.json', 'pnpm-lock.yaml']),
        
        # Rust projects
        (ProjectType.RUST, ['Cargo.toml', 'Cargo.lock']),
        
        # Go projects
        (ProjectType.GO, ['go.mod', 'go.sum']),
        
        # Java projects
        (ProjectType.JAVA, ['pom.xml', 'build.gradle', 'build.gradle.kts', 'gradlew']),
        
        # PHP projects
        (ProjectType.PHP, ['composer.json', 'composer.lock']),
    ]
    
    for project_type, indicators in project_indicators:
        for indicator in indicators:
            if (base_path / indicator).exists():
                return project_type
    
    return ProjectType.UNKNOWN


def auto_detect_setup_commands(base_dir: str = ".") -> List[SetupCommand]:
    """Auto-detect project setup commands based on project files.
    
    Args:
        base_dir (str): Base directory to scan. Defaults to current directory.
    
    Returns:
        List[SetupCommand]: List of detected setup commands.
    """
    project_type = detect_project_type(base_dir)
    base_path = Path(base_dir)
    commands = []
    
    if project_type == ProjectType.PYTHON:
        commands.extend(_detect_python_setup_commands(base_path))
    elif project_type == ProjectType.NODEJS:
        commands.extend(_detect_nodejs_setup_commands(base_path))
    elif project_type == ProjectType.RUST:
        commands.extend(_detect_rust_setup_commands(base_path))
    elif project_type == ProjectType.GO:
        commands.extend(_detect_go_setup_commands(base_path))
    elif project_type == ProjectType.JAVA:
        commands.extend(_detect_java_setup_commands(base_path))
    elif project_type == ProjectType.PHP:
        commands.extend(_detect_php_setup_commands(base_path))
    
    # Sort by priority (lower number = higher priority)
    commands.sort(key=lambda x: x.priority)
    
    return commands


def _detect_python_setup_commands(base_path: Path) -> List[SetupCommand]:
    """Detect Python project setup commands."""
    commands = []
    
    # Check for uv (modern Python package manager)
    if (base_path / 'pyproject.toml').exists():
        # Check if uv.lock exists (uv project)
        if (base_path / 'uv.lock').exists():
            commands.append(SetupCommand(
                command="uv sync",
                description="Install dependencies with uv",
                priority=1
            ))
        else:
            # Generic pyproject.toml - could be Poetry, PDM, or pip
            commands.append(SetupCommand(
                command="uv venv && source .venv/bin/activate",
                description="Create and activate virtual environment",
                priority=2
            ))
            commands.append(SetupCommand(
                command="uv pip install -e .",
                description="Install project in development mode",
                priority=3
            ))
    
    # Check for Poetry
    if (base_path / 'poetry.lock').exists() or _has_poetry_config(base_path):
        commands.append(SetupCommand(
            command="poetry install",
            description="Install dependencies with Poetry",
            priority=1
        ))
    
    # Check for Pipenv
    if (base_path / 'Pipfile').exists():
        commands.append(SetupCommand(
            command="pipenv install --dev",
            description="Install dependencies with Pipenv",
            priority=1
        ))
    
    # Check for requirements.txt
    if (base_path / 'requirements.txt').exists():
        commands.append(SetupCommand(
            command="pip install -r requirements.txt",
            description="Install dependencies from requirements.txt",
            priority=4
        ))
    
    # Check for setup.py
    if (base_path / 'setup.py').exists():
        commands.append(SetupCommand(
            command="pip install -e .",
            description="Install package in development mode",
            priority=5
        ))
    
    return commands


def _detect_nodejs_setup_commands(base_path: Path) -> List[SetupCommand]:
    """Detect Node.js project setup commands."""
    commands = []
    
    if not (base_path / 'package.json').exists():
        return commands
    
    # Check for specific lock files to determine package manager
    if (base_path / 'pnpm-lock.yaml').exists():
        commands.append(SetupCommand(
            command="pnpm install",
            description="Install dependencies with pnpm",
            priority=1
        ))
    elif (base_path / 'yarn.lock').exists():
        commands.append(SetupCommand(
            command="yarn install",
            description="Install dependencies with Yarn",
            priority=1
        ))
    elif (base_path / 'package-lock.json').exists():
        commands.append(SetupCommand(
            command="npm install",
            description="Install dependencies with npm",
            priority=1
        ))
    else:
        # No lock file, provide options
        commands.append(SetupCommand(
            command="npm install",
            description="Install dependencies with npm",
            priority=1
        ))
    
    return commands


def _detect_rust_setup_commands(base_path: Path) -> List[SetupCommand]:
    """Detect Rust project setup commands."""
    commands = []
    
    if (base_path / 'Cargo.toml').exists():
        commands.append(SetupCommand(
            command="cargo build",
            description="Build the project",
            priority=1
        ))
        commands.append(SetupCommand(
            command="cargo test",
            description="Run tests",
            priority=2
        ))
    
    return commands


def _detect_go_setup_commands(base_path: Path) -> List[SetupCommand]:
    """Detect Go project setup commands."""
    commands = []
    
    if (base_path / 'go.mod').exists():
        commands.append(SetupCommand(
            command="go mod download",
            description="Download dependencies",
            priority=1
        ))
        commands.append(SetupCommand(
            command="go build",
            description="Build the project",
            priority=2
        ))
        commands.append(SetupCommand(
            command="go test ./...",
            description="Run tests",
            priority=3
        ))
    
    return commands


def _detect_java_setup_commands(base_path: Path) -> List[SetupCommand]:
    """Detect Java project setup commands."""
    commands = []
    
    # Check for Maven
    if (base_path / 'pom.xml').exists():
        commands.append(SetupCommand(
            command="mvn clean install",
            description="Build project with Maven",
            priority=1
        ))
        commands.append(SetupCommand(
            command="mvn test",
            description="Run tests with Maven",
            priority=2
        ))
    
    # Check for Gradle
    gradle_files = ['build.gradle', 'build.gradle.kts', 'gradlew']
    if any((base_path / f).exists() for f in gradle_files):
        # Use gradlew if available, otherwise gradle
        gradle_cmd = "./gradlew" if (base_path / 'gradlew').exists() else "gradle"
        commands.append(SetupCommand(
            command=f"{gradle_cmd} build",
            description="Build project with Gradle",
            priority=1
        ))
        commands.append(SetupCommand(
            command=f"{gradle_cmd} test",
            description="Run tests with Gradle",
            priority=2
        ))
    
    return commands


def _detect_php_setup_commands(base_path: Path) -> List[SetupCommand]:
    """Detect PHP project setup commands."""
    commands = []
    
    if (base_path / 'composer.json').exists():
        commands.append(SetupCommand(
            command="composer install",
            description="Install dependencies with Composer",
            priority=1
        ))
        
        # Check for PHPUnit
        if (base_path / 'phpunit.xml').exists() or (base_path / 'phpunit.xml.dist').exists():
            commands.append(SetupCommand(
                command="vendor/bin/phpunit",
                description="Run PHPUnit tests",
                priority=2
            ))
    
    return commands


def _has_poetry_config(base_path: Path) -> bool:
    """Check if pyproject.toml contains Poetry configuration."""
    pyproject_file = base_path / 'pyproject.toml'
    if not pyproject_file.exists():
        return False
    
    try:
        content = pyproject_file.read_text(encoding='utf-8')
        return '[tool.poetry]' in content
    except (OSError, UnicodeDecodeError):
        return False


def generate_setup_section(commands: List[SetupCommand]) -> str:
    """Generate formatted project setup section.
    
    Args:
        commands (List[SetupCommand]): List of setup commands to format.
    
    Returns:
        str: Formatted setup section content.
    """
    if not commands:
        return ""
    
    lines = ["## Project Setup", ""]
    
    for i, cmd in enumerate(commands, 1):
        lines.append(f"{i}. **{cmd.description}**")
        lines.append(f"   ```bash")
        lines.append(f"   {cmd.command}")
        lines.append(f"   ```")
        if cmd.condition:
            lines.append(f"   *{cmd.condition}*")
        lines.append("")
    
    return "\n".join(lines)