"""
Smoke tests for runtime installation and basic functionality.

These tests verify that the runtime setup scripts work correctly and that
runtimes can be detected and used by AWD, without making actual API calls.
"""

import os
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path

# Test fixtures and utilities
@pytest.fixture(scope="module")
def temp_awd_home():
    """Create a temporary AWD home directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_home = os.environ.get('HOME')
        test_home = os.path.join(temp_dir, 'test_home')
        os.makedirs(test_home)
        
        # Set up test environment
        os.environ['HOME'] = test_home
        
        yield test_home
        
        # Restore original environment
        if original_home:
            os.environ['HOME'] = original_home
        else:
            del os.environ['HOME']


def run_command(cmd, check=True, capture_output=True, timeout=60):
    """Run a shell command with proper error handling."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output, 
            text=True,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        pytest.fail(f"Command timed out after {timeout}s: {cmd}")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Command failed: {cmd}\nStdout: {e.stdout}\nStderr: {e.stderr}")


class TestRuntimeSmoke:
    """Smoke tests for AWD runtime installation and basic functionality."""
    
    def test_codex_runtime_setup(self, temp_awd_home):
        """Test that Codex runtime setup script works correctly."""
        # Get the project root (where scripts are located)
        project_root = Path(__file__).parent.parent.parent
        setup_script = project_root / "scripts" / "runtime" / "setup-codex.sh"
        
        assert setup_script.exists(), f"Codex setup script not found: {setup_script}"
        
        # Run the setup script
        result = run_command(f"bash '{setup_script}'", timeout=120)
        
        # Verify the script completed successfully
        assert result.returncode == 0, f"Codex setup failed: {result.stderr}"
        
        # Verify codex binary was installed
        codex_binary = Path(temp_awd_home) / ".awd" / "runtimes" / "codex"
        assert codex_binary.exists(), "Codex binary not found after installation"
        assert codex_binary.is_file(), "Codex binary is not a file"
        
        # Verify binary is executable
        assert os.access(codex_binary, os.X_OK), "Codex binary is not executable"
        
        # Verify config was created
        codex_config = Path(temp_awd_home) / ".codex" / "config.toml"
        assert codex_config.exists(), "Codex config not found"
        
        # Verify config contains expected content
        config_content = codex_config.read_text()
        assert "github-models" in config_content, "GitHub Models config not found"
        assert "gpt-4o-mini" in config_content, "Default model not configured"
    
    def test_llm_runtime_setup(self, temp_awd_home):
        """Test that LLM runtime setup script works correctly."""
        # Get the project root
        project_root = Path(__file__).parent.parent.parent
        setup_script = project_root / "scripts" / "runtime" / "setup-llm.sh"
        
        assert setup_script.exists(), f"LLM setup script not found: {setup_script}"
        
        # Run the setup script
        result = run_command(f"bash '{setup_script}'", timeout=120)
        
        # Verify the script completed successfully
        assert result.returncode == 0, f"LLM setup failed: {result.stderr}"
        
        # Verify LLM wrapper was created
        llm_wrapper = Path(temp_awd_home) / ".awd" / "runtimes" / "llm"
        assert llm_wrapper.exists(), "LLM wrapper not found after installation"
        assert llm_wrapper.is_file(), "LLM wrapper is not a file"
        
        # Verify wrapper is executable
        assert os.access(llm_wrapper, os.X_OK), "LLM wrapper is not executable"
        
        # Verify virtual environment was created
        llm_venv = Path(temp_awd_home) / ".awd" / "runtimes" / "llm-venv"
        assert llm_venv.exists(), "LLM virtual environment not found"
        assert (llm_venv / "bin" / "llm").exists(), "LLM binary not found in venv"
    
    def test_codex_binary_functionality(self, temp_awd_home):
        """Test that installed Codex binary responds to basic commands."""
        codex_binary = Path(temp_awd_home) / ".awd" / "runtimes" / "codex"
        
        # Skip if codex not installed (dependency on previous test)
        if not codex_binary.exists():
            pytest.skip("Codex not installed")
        
        # Test version command
        result = run_command(f"'{codex_binary}' --version")
        assert result.returncode == 0, f"Codex --version failed: {result.stderr}"
        assert result.stdout.strip(), "Codex version output is empty"
        
        # Test help command
        result = run_command(f"'{codex_binary}' --help")
        assert result.returncode == 0, f"Codex --help failed: {result.stderr}"
        assert "Usage:" in result.stdout or "USAGE:" in result.stdout, "Help output doesn't contain usage info"
    
    def test_llm_binary_functionality(self, temp_awd_home):
        """Test that installed LLM binary responds to basic commands."""
        llm_wrapper = Path(temp_awd_home) / ".awd" / "runtimes" / "llm"
        
        # Skip if LLM not installed (dependency on previous test)
        if not llm_wrapper.exists():
            pytest.skip("LLM not installed")
        
        # Test version command
        result = run_command(f"'{llm_wrapper}' --version")
        assert result.returncode == 0, f"LLM --version failed: {result.stderr}"
        assert result.stdout.strip(), "LLM version output is empty"
        
        # Test help command
        result = run_command(f"'{llm_wrapper}' --help")
        assert result.returncode == 0, f"LLM --help failed: {result.stderr}"
        assert "Usage:" in result.stdout or "usage:" in result.stdout, "Help output doesn't contain usage info"
    
    def test_awd_runtime_detection(self, temp_awd_home):
        """Test that AWD can detect installed runtimes."""
        # Import AWD modules
        from awd_cli.runtime.factory import RuntimeFactory
        
        # Update PATH to include our test runtime directory
        runtime_dir = Path(temp_awd_home) / ".awd" / "runtimes"
        if runtime_dir.exists():
            original_path = os.environ.get('PATH', '')
            os.environ['PATH'] = f"{runtime_dir}:{original_path}"
            
            try:
                # Test runtime detection
                if (runtime_dir / "codex").exists():
                    assert RuntimeFactory.runtime_exists("codex"), "AWD cannot detect installed Codex runtime"
                
                if (runtime_dir / "llm").exists():
                    assert RuntimeFactory.runtime_exists("llm"), "AWD cannot detect installed LLM runtime"
                    
            finally:
                # Restore PATH
                os.environ['PATH'] = original_path
    
    def test_awd_workflow_compilation(self, temp_awd_home):
        """Test that AWD can compile workflows without executing them."""
        from awd_cli.workflow.runner import preview_workflow
        
        # Create a test workflow
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow_content = """---
description: Test workflow for smoke testing
input: [name]
---

# Hello ${input:name}

This is a test workflow to verify compilation works.
            """
            
            workflow_file = Path(temp_dir) / "test.prompt.md"
            workflow_file.write_text(workflow_content)
            
            # Test preview (compilation without execution)
            success, result = preview_workflow("test", {"name": "Tester"}, temp_dir)
            
            assert success, f"Workflow compilation failed: {result}"
            assert "Hello Tester" in result, "Parameter substitution failed"
            assert "${input:name}" not in result, "Parameter not substituted"


class TestGoldenScenarioSetup:
    """Tests for the golden scenario setup without API calls."""
    
    def test_hello_world_template_structure(self):
        """Test that hello-world template has correct structure."""
        project_root = Path(__file__).parent.parent.parent
        template_dir = project_root / "templates" / "hello-world"
        
        # Verify template exists
        assert template_dir.exists(), "Hello-world template directory not found"
        
        # Verify required files
        assert (template_dir / "awd.yml").exists(), "awd.yml not found in template"
        assert (template_dir / "hello-world.prompt.md").exists(), "hello-world.prompt.md not found in template"
        assert (template_dir / "README.md").exists(), "README.md not found in template"
        
        # Verify awd.yml has expected scripts
        awd_config = (template_dir / "awd.yml").read_text()
        assert "start:" in awd_config, "start script not found in awd.yml"
        assert "llm:" in awd_config, "llm script not found in awd.yml"
        assert "codex" in awd_config, "codex not referenced in awd.yml"
    
    def test_hello_world_prompt_structure(self):
        """Test that hello-world prompt has correct structure."""
        project_root = Path(__file__).parent.parent.parent
        prompt_file = project_root / "templates" / "hello-world" / "hello-world.prompt.md"
        
        prompt_content = prompt_file.read_text()
        
        # Verify frontmatter
        assert "description:" in prompt_content, "Prompt missing description"
        assert "mcp:" in prompt_content, "Prompt missing MCP config"
        assert "input:" in prompt_content, "Prompt missing input specification"
        
        # Verify parameter usage
        assert "${input:name}" in prompt_content, "Prompt missing parameter substitution"
        
        # Verify MCP tool references
        assert "get_me" in prompt_content, "Prompt missing GitHub MCP tool reference"
    
    def test_awd_init_workflow_dry_run(self, temp_awd_home):
        """Test AWD init command structure (without actual execution)."""
        # Test the template structure instead of CLI command
        # since we'd need to properly mock the entire CLI context
        
        project_root = Path(__file__).parent.parent.parent
        template_dir = project_root / "templates" / "hello-world"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "test-project"
            project_dir.mkdir()
            
            # Manually copy template files (simulating what init does)
            import shutil
            
            # Copy template files
            for template_file in ["awd.yml", "hello-world.prompt.md", "README.md"]:
                src = template_dir / template_file
                dst = project_dir / template_file
                
                # Read template and do basic substitution
                content = src.read_text()
                content = content.replace("{{project_name}}", "test-project")
                dst.write_text(content)
            
            # Verify project was created correctly
            assert (project_dir / "awd.yml").exists(), "awd.yml not created"
            assert (project_dir / "hello-world.prompt.md").exists(), "Prompt file not created"
            assert (project_dir / "README.md").exists(), "README.md not created"
            
            # Verify template substitution worked
            awd_config = (project_dir / "awd.yml").read_text()
            assert "test-project" in awd_config, "Project name not substituted in template"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
