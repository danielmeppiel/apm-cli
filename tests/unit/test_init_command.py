"""Tests for the awd init command."""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from awd_cli.cli import cli


class TestInitCommand:
    """Test cases for awd init command."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.original_dir = os.getcwd()
        
    def teardown_method(self):
        """Clean up after tests."""
        os.chdir(self.original_dir)
        
    def test_init_current_directory(self):
        """Test initialization in current directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            result = self.runner.invoke(cli, ['init', '--yes'])
            
            assert result.exit_code == 0
            assert "AWD project initialized successfully!" in result.output
            assert Path('awd.yml').exists()
            assert Path('hello-world.prompt.md').exists()
            assert Path('README.md').exists()
    
    def test_init_explicit_current_directory(self):
        """Test initialization with explicit '.' argument."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            result = self.runner.invoke(cli, ['init', '.', '--yes'])
            
            assert result.exit_code == 0
            assert "AWD project initialized successfully!" in result.output
            assert Path('awd.yml').exists()
    
    def test_init_new_directory(self):
        """Test initialization in new directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            result = self.runner.invoke(cli, ['init', 'my-project', '--yes'])
            
            assert result.exit_code == 0
            assert "Created project directory: my-project" in result.output
            # Use absolute path to check files
            project_path = Path(tmp_dir) / 'my-project'
            assert project_path.exists()
            assert project_path.is_dir()
            assert (project_path / 'awd.yml').exists()
            assert (project_path / 'hello-world.prompt.md').exists()
    
    def test_init_existing_project_without_force(self):
        """Test initialization over existing project without --force."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Create existing awd.yml
            Path('awd.yml').write_text('name: existing-project\nversion: 0.1.0\n')
            
            # Try to init without force (should prompt)
            result = self.runner.invoke(cli, ['init', '--yes'])
            
            assert result.exit_code == 0
            assert "Existing AWD project detected" in result.output
            assert "--yes specified, continuing with overwrite" in result.output
    
    def test_init_existing_project_with_force(self):
        """Test initialization over existing project with --force."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Create existing awd.yml
            Path('awd.yml').write_text('name: existing-project\nversion: 0.1.0\n')
            
            result = self.runner.invoke(cli, ['init', '--force', '--yes'])
            
            assert result.exit_code == 0
            assert "AWD project initialized successfully!" in result.output
            # Should overwrite the file
            with open('awd.yml') as f:
                config = yaml.safe_load(f)
                # The template should have been applied
                assert 'scripts' in config
    
    def test_init_preserves_existing_config(self):
        """Test that existing config is preserved when possible."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Create existing awd.yml with custom values
            existing_config = {
                'name': 'my-custom-project',
                'version': '2.0.0',
                'description': 'Custom description',
                'author': 'Custom Author'
            }
            with open('awd.yml', 'w') as f:
                yaml.dump(existing_config, f)
            
            result = self.runner.invoke(cli, ['init', '--yes'])
            
            assert result.exit_code == 0
            assert "Preserving existing configuration" in result.output
    
    def test_init_interactive_mode(self):
        """Test interactive mode with user input."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Simulate user input
            user_input = "my-test-project\n1.5.0\nTest description\nTest Author\ny\n"
            
            result = self.runner.invoke(cli, ['init'], input=user_input)
            
            assert result.exit_code == 0
            assert "Setting up your AWD project" in result.output
            assert "Project name" in result.output
            assert "Version" in result.output
            assert "Description" in result.output
            assert "Author" in result.output
            
            # Verify the interactive values were applied to awd.yml
            with open('awd.yml') as f:
                config = yaml.safe_load(f)
                assert config['name'] == 'my-test-project'
                assert config['version'] == '1.5.0'
                assert config['description'] == 'Test description'
                assert config['author'] == 'Test Author'
    
    def test_init_interactive_mode_abort(self):
        """Test aborting interactive mode."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Simulate user input with 'no' to confirmation
            user_input = "my-test-project\n1.5.0\nTest description\nTest Author\nn\n"
            
            result = self.runner.invoke(cli, ['init'], input=user_input)
            
            assert result.exit_code == 0
            assert "Aborted" in result.output
            assert not Path('awd.yml').exists()
    
    def test_init_existing_project_interactive_cancel(self):
        """Test cancelling when existing project detected in interactive mode."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Create existing awd.yml
            Path('awd.yml').write_text('name: existing-project\nversion: 0.1.0\n')
            
            # Simulate user saying 'no' to overwrite
            result = self.runner.invoke(cli, ['init'], input='n\n')
            
            assert result.exit_code == 0
            assert "Existing AWD project detected" in result.output
            assert "Initialization cancelled" in result.output
    
    def test_init_validates_project_structure(self):
        """Test that init creates proper project structure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            result = self.runner.invoke(cli, ['init', 'test-project', '--yes'])
            
            assert result.exit_code == 0
            
            # Use absolute path for checking files
            project_path = Path(tmp_dir) / 'test-project'
            
            # Verify awd.yml structure
            with open(project_path / 'awd.yml') as f:
                config = yaml.safe_load(f)
                assert config['name'] == 'test-project'
                assert 'version' in config
                assert 'scripts' in config
                assert 'dependencies' in config
                assert 'mcp' in config['dependencies']
            
            # Verify files exist
            assert (project_path / 'hello-world.prompt.md').exists()
            assert (project_path / 'README.md').exists()
