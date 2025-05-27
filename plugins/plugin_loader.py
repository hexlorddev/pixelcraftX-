import os
import importlib.util
import sys
import logging
from typing import Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLUGIN_DIR = "plugins"
PLUGIN_METADATA_FILE = "plugin_metadata.json"

class PluginMetadata:
    def __init__(self, name: str, version: str, description: str = "", 
                 dependencies: list = None, author: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies or []
        self.author = author

def validate_plugin(module: Any) -> bool:
    """Validate if a plugin has the required attributes and methods."""
    required_attrs = ['PLUGIN_NAME', 'PLUGIN_VERSION']
    required_methods = ['initialize', 'cleanup']
    
    for attr in required_attrs:
        if not hasattr(module, attr):
            logger.error(f"Plugin missing required attribute: {attr}")
            return False
    
    for method in required_methods:
        if not hasattr(module, method) or not callable(getattr(module, method)):
            logger.error(f"Plugin missing required method: {method}")
            return False
    
    return True

def load_plugin_metadata(plugin_name: str) -> Optional[PluginMetadata]:
    """Load plugin metadata from JSON file if it exists."""
    metadata_path = os.path.join(PLUGIN_DIR, plugin_name, PLUGIN_METADATA_FILE)
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                return PluginMetadata(**data)
        except Exception as e:
            logger.error(f"Error loading metadata for {plugin_name}: {e}")
    return None

def check_dependencies(plugin: Any, loaded_plugins: Dict[str, Any]) -> bool:
    """Check if all plugin dependencies are satisfied."""
    if not hasattr(plugin, 'PLUGIN_DEPENDENCIES'):
        return True
    
    for dep in plugin.PLUGIN_DEPENDENCIES:
        if dep not in loaded_plugins:
            logger.error(f"Missing dependency {dep} for plugin {plugin.PLUGIN_NAME}")
            return False
    return True

def load_plugins() -> Dict[str, Any]:
    """Load and initialize all valid plugins."""
    plugins = {}
    if not os.path.exists(PLUGIN_DIR):
        logger.warning(f"Plugin directory {PLUGIN_DIR} does not exist")
        return plugins
    
    # First pass: Load all plugins
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                module_name = filename[:-3]
                file_path = os.path.join(PLUGIN_DIR, filename)
                
                # Load metadata
                metadata = load_plugin_metadata(module_name)
                
                # Load module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Validate plugin
                if validate_plugin(module):
                    plugins[module_name] = {
                        'module': module,
                        'metadata': metadata
                    }
                    logger.info(f"Successfully loaded plugin: {module_name}")
                else:
                    logger.error(f"Failed to validate plugin: {module_name}")
                    
            except Exception as e:
                logger.error(f"Error loading plugin {filename}: {e}")
    
    # Second pass: Initialize plugins and check dependencies
    initialized_plugins = {}
    for name, plugin_data in plugins.items():
        try:
            if check_dependencies(plugin_data['module'], initialized_plugins):
                plugin_data['module'].initialize()
                initialized_plugins[name] = plugin_data
                logger.info(f"Successfully initialized plugin: {name}")
        except Exception as e:
            logger.error(f"Error initializing plugin {name}: {e}")
    
    return initialized_plugins

def cleanup_plugins(plugins: Dict[str, Any]) -> None:
    """Cleanup all loaded plugins."""
    for name, plugin_data in plugins.items():
        try:
            plugin_data['module'].cleanup()
            logger.info(f"Successfully cleaned up plugin: {name}")
        except Exception as e:
            logger.error(f"Error cleaning up plugin {name}: {e}") 