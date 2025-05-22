"""Core operations for AWD-CLI."""

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
        
        # Configure the client to use the package
        # This is just a placeholder - actual implementation will depend on the package
        client.update_config({f"mcp.package.{package_name}.enabled": True})
        
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
        
        # Update the client configuration to disable the package
        current_config = client.get_current_config()
        if f"mcp.package.{package_name}.enabled" in current_config:
            client.update_config({f"mcp.package.{package_name}.enabled": False})
        
        return result
    except Exception as e:
        print(f"Error uninstalling package: {e}")
        return False
