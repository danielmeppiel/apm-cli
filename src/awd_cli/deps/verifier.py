"""Dependency verification for AWD-CLI."""

import os
import yaml
from ..factory import PackageManagerFactory


def load_awd_config(config_file="awd.yml"):
    """Load the AWD configuration file.
    
    Args:
        config_file (str, optional): Path to the configuration file. Defaults to "awd.yml".
        
    Returns:
        dict: The configuration, or None if loading failed.
    """
    try:
        if not os.path.exists(config_file):
            print(f"Configuration file {config_file} not found.")
            return None
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    except Exception as e:
        print(f"Error loading {config_file}: {e}")
        return None


def verify_dependencies(config_file="awd.yml"):
    """Check if awd.yml servers are installed.
    
    Args:
        config_file (str, optional): Path to the configuration file. Defaults to "awd.yml".
        
    Returns:
        tuple: (bool, list, list) - All installed status, list of installed, list of missing
    """
    config = load_awd_config(config_file)
    if not config or 'servers' not in config:
        return False, [], []
    
    try:
        package_manager = PackageManagerFactory.create_package_manager()
        installed = package_manager.list_installed()
        
        # Check which servers are missing
        required_servers = config['servers']
        missing = [server for server in required_servers if server not in installed]
        installed_servers = [server for server in required_servers if server in installed]
        
        all_installed = len(missing) == 0
        
        return all_installed, installed_servers, missing
    except Exception as e:
        print(f"Error verifying dependencies: {e}")
        return False, [], []


def install_missing_dependencies(config_file="awd.yml", client_type="default"):
    """Install missing dependencies from awd.yml.
    
    Args:
        config_file (str, optional): Path to the configuration file. Defaults to "awd.yml".
        client_type (str, optional): Type of client to configure. Defaults to "default".
        
    Returns:
        tuple: (bool, list) - Success status and list of installed packages
    """
    _, _, missing = verify_dependencies(config_file)
    
    if not missing:
        return True, []
    
    installed = []
    package_manager = PackageManagerFactory.create_package_manager()
    
    for package in missing:
        try:
            result = package_manager.install(package)
            if result:
                installed.append(package)
        except Exception as e:
            print(f"Error installing {package}: {e}")
    
    return len(installed) == len(missing), installed