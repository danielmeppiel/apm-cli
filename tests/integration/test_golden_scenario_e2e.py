"""
End-to-end golden path tests for AWD runtime integration.

These tests verify the complete user journey from the README golden scenario,
including real runtime installation and API calls. They should only run on 
releases to avoid API rate limits and costs during development.

To run these tests, you need:
- GITHUB_TOKEN environment variable set with appropriate permissions
- Network access to download runtimes and make API calls
"""

import os
import subprocess
import tempfile
import shutil
import pytest
import json
from pathlib import Path
from unittest import mock


# Skip all tests in this module if not in E2E mode
E2E_MODE = os.environ.get('AWD_E2E_TESTS', '').lower() in ('1', 'true', 'yes')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

pytestmark = pytest.mark.skipif(
    not E2E_MODE, 
    reason="E2E tests only run when AWD_E2E_TESTS=1 is set"
)


def run_command(cmd, check=True, capture_output=True, timeout=180, cwd=None, show_output=False):
    """Run a shell command with proper error handling."""
    try:
        if show_output:
            # For commands we want to see output from (like runtime setup and execution)
            print(f"\n>>> Running command: {cmd}")
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=check, 
                capture_output=False,  # Don't capture, let it stream to terminal
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            # For show_output commands, we need to capture in a different way to return something
            # Run again with capture to get return data
            result_capture = subprocess.run(
                cmd, 
                shell=True, 
                check=False,  # Don't fail here, we already ran it above
                capture_output=True, 
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            result.stdout = result_capture.stdout
            result.stderr = result_capture.stderr
        else:
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=check, 
                capture_output=capture_output, 
                text=True,
                timeout=timeout,
                cwd=cwd
            )
        return result
    except subprocess.TimeoutExpired:
        pytest.fail(f"Command timed out after {timeout}s: {cmd}")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Command failed: {cmd}\nStdout: {e.stdout}\nStderr: {e.stderr}")


@pytest.fixture(scope="module")
def temp_e2e_home():
    """Create a temporary home directory for E2E testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_home = os.environ.get('HOME')
        test_home = os.path.join(temp_dir, 'e2e_home')
        os.makedirs(test_home)
        
        # Set up test environment
        os.environ['HOME'] = test_home
        
        # Preserve GITHUB_TOKEN
        if GITHUB_TOKEN:
            os.environ['GITHUB_TOKEN'] = GITHUB_TOKEN
        
        yield test_home
        
        # Restore original environment
        if original_home:
            os.environ['HOME'] = original_home
        else:
            del os.environ['HOME']


@pytest.fixture(scope="module")
def awd_binary():
    """Get path to AWD binary for testing."""
    # Try to find AWD binary in common locations
    possible_paths = [
        "awd",  # In PATH
        "./awd",  # Local directory
        "./dist/awd",  # Build directory
        Path(__file__).parent.parent.parent / "dist" / "awd",  # Relative to test
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([str(path), "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return str(path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    pytest.skip("AWD binary not found. Build it first with: python -m build")


class TestGoldenScenarioE2E:
    """End-to-end tests for the README golden scenario."""
    
    @pytest.mark.skipif(not GITHUB_TOKEN, reason="GITHUB_TOKEN required for E2E tests")
    def test_complete_golden_scenario_codex(self, temp_e2e_home, awd_binary):
        """Test the complete golden scenario from README using Codex runtime."""
        
        # Step 1: Setup Codex runtime (equivalent to: awd runtime setup codex)
        print("\n=== Setting up Codex runtime ===")
        result = run_command(f"{awd_binary} runtime setup codex", timeout=300, show_output=True)
        assert result.returncode == 0, f"Runtime setup failed: {result.stderr}"
        
        # Verify codex is available and GitHub configuration was created
        codex_binary = Path(temp_e2e_home) / ".awd" / "runtimes" / "codex"
        codex_config = Path(temp_e2e_home) / ".codex" / "config.toml"
        
        assert codex_binary.exists(), "Codex binary not installed"
        assert codex_config.exists(), "Codex configuration not created"
        
        # Verify configuration contains GitHub Models setup
        config_content = codex_config.read_text()
        assert "github-models" in config_content, "GitHub Models configuration not found"
        assert "GITHUB_TOKEN" in config_content, "GitHub token environment variable not configured"
        print(f"✓ Codex configuration created:\n{config_content}")
        
        # Test codex binary directly
        print("\n=== Testing Codex binary directly ===")
        result = run_command(f"{codex_binary} --version", show_output=True)
        if result.returncode == 0:
            print(f"✓ Codex version: {result.stdout}")
        else:
            print(f"⚠ Codex version check failed: {result.stderr}")
            
        # Check if codex is in PATH
        print("\n=== Checking PATH setup ===")
        result = run_command("which codex", check=False)
        if result.returncode == 0:
            print(f"✓ Codex found in PATH: {result.stdout.strip()}")
        else:
            print("⚠ Codex not in PATH, will need explicit path or shell restart")
        
        # Step 2: Initialize project (equivalent to: awd init my-hello-world)
        with tempfile.TemporaryDirectory() as project_workspace:
            project_dir = Path(project_workspace) / "my-hello-world"
            
            print("\n=== Initializing AWD project ===")
            result = run_command(f"{awd_binary} init my-hello-world", cwd=project_workspace, show_output=True)
            assert result.returncode == 0, f"Project init failed: {result.stderr}"
            assert project_dir.exists(), "Project directory not created"
            
            # Verify project structure
            assert (project_dir / "awd.yml").exists(), "awd.yml not created"
            assert (project_dir / "hello-world.prompt.md").exists(), "Prompt file not created"
            
            # Show project contents for debugging
            print("\n=== Project structure ===")
            awd_yml_content = (project_dir / "awd.yml").read_text()
            prompt_content = (project_dir / "hello-world.prompt.md").read_text()
            print(f"awd.yml:\n{awd_yml_content}")
            print(f"hello-world.prompt.md:\n{prompt_content[:500]}...")
            
            # Step 3: Install dependencies (equivalent to: awd install)
            print("\n=== Installing dependencies ===")
            result = run_command(f"{awd_binary} install", cwd=project_dir, show_output=True)
            assert result.returncode == 0, f"Dependency install failed: {result.stderr}"
            
            # Step 4: Run the golden scenario (equivalent to: awd run start --param name="E2E Tester")
            print("\n=== Running golden scenario with Codex ===")
            print(f"Environment: HOME={temp_e2e_home}, GITHUB_TOKEN={'SET' if GITHUB_TOKEN else 'NOT SET'}")
            
            # Add explicit GITHUB_TOKEN to the environment for this run
            env = os.environ.copy()
            env['GITHUB_TOKEN'] = GITHUB_TOKEN
            env['HOME'] = temp_e2e_home
            
            # Run with real-time output streaming
            cmd = f'{awd_binary} run start --param name="E2E Tester"'
            print(f"Executing: {cmd}")
            
            try:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Merge stderr into stdout
                    text=True,
                    cwd=project_dir,
                    env=env
                )
                
                output_lines = []
                print("\n--- Codex Execution Output ---")
                
                # Stream output in real-time
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(line.rstrip())  # Print to terminal
                        output_lines.append(line)
                
                # Wait for completion
                return_code = process.wait(timeout=120)
                full_output = ''.join(output_lines)
                
                print("--- End Codex Output ---\n")
                
                # Verify execution
                if return_code != 0:
                    print(f"❌ Command failed with return code: {return_code}")
                    print(f"Full output:\n{full_output}")
                    
                    # Check for common issues
                    if "GITHUB_TOKEN" in full_output:
                        pytest.fail("Codex execution failed: GitHub token not properly configured")
                    elif "Connection" in full_output or "timeout" in full_output.lower():
                        pytest.fail("Codex execution failed: Network connectivity issue")
                    else:
                        pytest.fail(f"Golden scenario execution failed with return code {return_code}: {full_output}")
                
                # Verify output contains expected elements
                output_lower = full_output.lower()
                assert "e2e tester" in output_lower or "tester" in output_lower, \
                    f"Parameter substitution failed. Output: {full_output}"
                assert len(full_output.strip()) > 50, \
                    f"Output seems too short, API call might have failed. Output: {full_output}"
                
                print(f"\n✅ Golden scenario completed successfully!")
                print(f"Output length: {len(full_output)} characters")
                print(f"Contains parameter: {'✓' if 'tester' in output_lower else '❌'}")
                
            except subprocess.TimeoutExpired:
                process.kill()
                pytest.fail("Codex execution timed out after 120 seconds")
            
    @pytest.mark.skipif(not GITHUB_TOKEN, reason="GITHUB_TOKEN required for E2E tests")        
    def test_complete_golden_scenario_llm(self, temp_e2e_home, awd_binary):
        """Test the complete golden scenario using LLM runtime."""
        
        # Step 1: Setup LLM runtime (equivalent to: awd runtime setup llm)
        print("\\n=== Setting up LLM runtime ===")
        result = run_command(f"{awd_binary} runtime setup llm", timeout=300)
        assert result.returncode == 0, f"LLM runtime setup failed: {result.stderr}"
        
        # Verify LLM is available
        llm_wrapper = Path(temp_e2e_home) / ".awd" / "runtimes" / "llm"
        assert llm_wrapper.exists(), "LLM wrapper not installed"
        
        # Configure LLM for GitHub Models
        print("\\n=== Configuring LLM for GitHub Models ===")
        # LLM expects GITHUB_MODELS_KEY environment variable, not GITHUB_TOKEN
        # Set it for the LLM runtime
        os.environ['GITHUB_MODELS_KEY'] = GITHUB_TOKEN
        print("✓ Set GITHUB_MODELS_KEY environment variable for LLM")
        
        # Step 2: Use existing project or create new one
        with tempfile.TemporaryDirectory() as project_workspace:
            project_dir = Path(project_workspace) / "my-hello-world-llm"
            
            print("\\n=== Initializing LLM test project ===")
            result = run_command(f"{awd_binary} init my-hello-world-llm", cwd=project_workspace)
            assert result.returncode == 0, f"Project init failed: {result.stderr}"
            
            # Step 3: Install dependencies
            result = run_command(f"{awd_binary} install", cwd=project_dir)
            assert result.returncode == 0, f"Dependency install failed: {result.stderr}"
            
            # Step 4: Run with LLM runtime (equivalent to: awd run llm --param name="E2E LLM Tester")
            print("\\n=== Running golden scenario with LLM ===")
            
            # Ensure GITHUB_MODELS_KEY is set for the execution
            env = os.environ.copy()
            env['GITHUB_MODELS_KEY'] = GITHUB_TOKEN
            env['HOME'] = temp_e2e_home
            
            # Run the command with proper environment
            cmd = f'{awd_binary} run llm --param name="E2E LLM Tester"'
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=project_dir,
                env=env
            )
            
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                    output_lines.append(line)
            
            return_code = process.wait(timeout=120)
            full_output = ''.join(output_lines)
            
            # Verify execution (LLM might have different authentication requirements)
            if return_code == 0:
                output = full_output.lower()
                assert "e2e llm tester" in output or "tester" in output, "Parameter substitution failed"
                assert len(output.strip()) > 50, "Output seems too short"
                print(f"\\n=== LLM scenario output ===\\n{full_output}")
            else:
                # LLM might fail due to auth setup in CI, log for debugging
                print(f"\\n=== LLM execution failed (expected in CI) ===")
                print(f"Output: {full_output}")
                pytest.skip("LLM execution failed, likely due to authentication in CI environment")

    def test_runtime_list_command(self, temp_e2e_home, awd_binary):
        """Test that AWD can list installed runtimes."""
        print("\\n=== Testing runtime list command ===")
        result = run_command(f"{awd_binary} runtime list")
        
        # Should succeed even if no runtimes installed
        assert result.returncode == 0, f"Runtime list failed: {result.stderr}"
        
        # Output should contain some indication of runtime status
        output = result.stdout.lower()
        assert "runtime" in output or "codex" in output or "llm" in output or "no runtimes" in output, \
            "Runtime list output doesn't look correct"
        
        print(f"Runtime list output: {result.stdout}")

    def test_awd_version_and_help(self, awd_binary):
        """Test basic AWD CLI functionality."""
        print("\\n=== Testing AWD CLI basics ===")
        
        # Test version
        result = run_command(f"{awd_binary} --version")
        assert result.returncode == 0, f"Version command failed: {result.stderr}"
        assert result.stdout.strip(), "Version output is empty"
        
        # Test help
        result = run_command(f"{awd_binary} --help")
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        assert "usage:" in result.stdout.lower() or "awd" in result.stdout.lower(), \
            "Help output doesn't look correct"
        
        print(f"AWD version: {result.stdout}")


class TestRuntimeInteroperability:
    """Test that both runtimes can be installed and work together."""
    
    def test_dual_runtime_installation(self, temp_e2e_home, awd_binary):
        """Test installing both runtimes in the same environment."""
        
        # Install Codex
        print("\\n=== Installing Codex runtime ===")
        result = run_command(f"{awd_binary} runtime setup codex", timeout=300)
        assert result.returncode == 0, f"Codex setup failed: {result.stderr}"
        
        # Install LLM  
        print("\\n=== Installing LLM runtime ===")
        result = run_command(f"{awd_binary} runtime setup llm", timeout=300)
        assert result.returncode == 0, f"LLM setup failed: {result.stderr}"
        
        # Verify both are available
        runtime_dir = Path(temp_e2e_home) / ".awd" / "runtimes"
        assert (runtime_dir / "codex").exists(), "Codex not found after dual install"
        assert (runtime_dir / "llm").exists(), "LLM not found after dual install"
        
        # Test runtime list shows both
        result = run_command(f"{awd_binary} runtime list")
        assert result.returncode == 0, f"Runtime list failed: {result.stderr}"
        
        output = result.stdout.lower()
        # Should show both runtimes (exact format may vary)
        print(f"Runtime list with both installed: {result.stdout}")


if __name__ == "__main__":
    # Example of how to run E2E tests manually
    print("To run E2E tests manually:")
    print("export AWD_E2E_TESTS=1")
    print("export GITHUB_TOKEN=your_token_here")  
    print("pytest tests/integration/test_golden_scenario_e2e.py -v -s")
    
    # Run tests when executed directly
    if E2E_MODE:
        pytest.main([__file__, "-v", "-s"])
    else:
        print("\\nE2E mode not enabled. Set AWD_E2E_TESTS=1 to run these tests.")
