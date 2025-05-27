from typing import Dict, Any, List, Optional
import logging
from plugins.plugin_loader import load_plugins, cleanup_plugins

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.enabled_plugins: List[str] = []
        self.plugin_configs: Dict[str, Dict] = {}
    
    def initialize(self) -> bool:
        """Initialize the plugin manager and load all plugins."""
        try:
            self.plugins = load_plugins()
            logger.info(f"Loaded {len(self.plugins)} plugins")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plugin manager: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get a specific plugin by name."""
        return self.plugins.get(plugin_name)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a specific plugin."""
        if plugin_name in self.plugins and plugin_name not in self.enabled_plugins:
            try:
                plugin = self.plugins[plugin_name]['module']
                plugin.initialize()
                self.enabled_plugins.append(plugin_name)
                logger.info(f"Enabled plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to enable plugin {plugin_name}: {e}")
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a specific plugin."""
        if plugin_name in self.enabled_plugins:
            try:
                plugin = self.plugins[plugin_name]['module']
                plugin.cleanup()
                self.enabled_plugins.remove(plugin_name)
                logger.info(f"Disabled plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to disable plugin {plugin_name}: {e}")
        return False
    
    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugins."""
        return self.enabled_plugins
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[Dict]:
        """Get metadata for a specific plugin."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get('metadata')
        return None
    
    def shutdown(self):
        """Cleanup and shutdown all plugins."""
        cleanup_plugins(self.plugins)
        self.plugins.clear()
        self.enabled_plugins.clear()
        logger.info("Plugin manager shutdown complete") 