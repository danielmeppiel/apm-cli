"""Core operations for APM-CLI."""

from ..factory import ClientFactory, PackageManagerFactory


def configure_client(client_type, config_updates):
    """Configure an MCP client.
    
    Args:
        client_type (str): Type of client to configure.
        config_updates (dict): Configuration updates to apply.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        client = ClientFactory.create_client(client_type)
        client.update_config(config_updates)
        return True
    except Exception as e:
        print(f"Error configuring client: {e}")
        return False


def install_package(client_type, package_name, version=None):
    """Install an MCP package.
    
    Args:
        client_type (str): Type of client to configure.
        package_name (str): Name of the package to install.
        version (str, optional): Version of the package to install.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        client = ClientFactory.create_client(client_type)
        package_manager = PackageManagerFactory.create_package_manager()
        
        # Install the package
        result = package_manager.install(package_name, version)
                
        # Return the result of installation
        # The configuration of the server is already handled in the package_manager.install method
        return result
    except Exception as e:
        print(f"Error installing package: {e}")
        return False


def uninstall_package(client_type, package_name):
    """Uninstall an MCP package.
    
    Args:
        client_type (str): Type of client to configure.
        package_name (str): Name of the package to uninstall.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        client = ClientFactory.create_client(client_type)
        package_manager = PackageManagerFactory.create_package_manager()
        
        # Uninstall the package
        result = package_manager.uninstall(package_name)
        
        # Remove any legacy config entries if they exist
        current_config = client.get_current_config()
        config_updates = {}
        if f"mcp.package.{package_name}.enabled" in current_config:
            config_updates = {f"mcp.package.{package_name}.enabled": None}  # Set to None to remove the entry
            client.update_config(config_updates)
        
        return result
    except Exception as e:
        print(f"Error uninstalling package: {e}")
        return False
