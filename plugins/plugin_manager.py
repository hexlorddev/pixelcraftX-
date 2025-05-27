"""
Plugin management system for PixelCrafterX.
Handles plugin loading, unloading, and lifecycle management.
"""

import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from abc import ABC, abstractmethod

class Plugin(ABC):
    def __init__(self):
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.description = "Base plugin class"
        self.enabled = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin."""
        pass
        
    @abstractmethod
    def shutdown(self):
        """Shutdown the plugin."""
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description
        }

class PluginManager:
    def __init__(self):
        self.plugins_dir = Path("plugins")
        self.plugin_config_file = self.plugins_dir / "plugin_config.json"
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        self._ensure_plugin_dirs()
        self._load_plugin_configs()
        
    def _ensure_plugin_dirs(self):
        """Ensure plugin directories exist."""
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        (self.plugins_dir / "official").mkdir(exist_ok=True)
        (self.plugins_dir / "community").mkdir(exist_ok=True)
        (self.plugins_dir / "experimental").mkdir(exist_ok=True)
        
    def _load_plugin_configs(self):
        """Load plugin configurations."""
        if self.plugin_config_file.exists():
            try:
                with open(self.plugin_config_file, 'r') as f:
                    self.plugin_configs = json.load(f)
            except Exception as e:
                print(f"Error loading plugin configs: {e}")
                
    def _save_plugin_configs(self):
        """Save plugin configurations."""
        try:
            with open(self.plugin_config_file, 'w') as f:
                json.dump(self.plugin_configs, f, indent=4)
        except Exception as e:
            print(f"Error saving plugin configs: {e}")
            
    def discover_plugins(self) -> List[str]:
        """Discover available plugins."""
        plugin_files = []
        for root, _, files in os.walk(self.plugins_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    plugin_files.append(os.path.join(root, file))
        return plugin_files
        
    def load_plugin(self, plugin_path: str) -> Optional[Plugin]:
        """Load a plugin from a file."""
        try:
            # Convert path to module path
            rel_path = os.path.relpath(plugin_path, str(self.plugins_dir))
            module_path = rel_path.replace(os.sep, '.').replace('.py', '')
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find plugin class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin = obj()
                    if plugin.initialize():
                        self.plugins[plugin.name] = plugin
                        return plugin
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
        return None
        
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]
            return True
        return False
        
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)
        
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_info()
        return None
        
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = True
            if plugin_name in self.plugin_configs:
                self.plugin_configs[plugin_name]['enabled'] = True
                self._save_plugin_configs()
            return True
        return False
        
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = False
            if plugin_name in self.plugin_configs:
                self.plugin_configs[plugin_name]['enabled'] = False
                self._save_plugin_configs()
            return True
        return False
        
    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugins."""
        return [name for name, plugin in self.plugins.items() if plugin.enabled]
        
    def get_disabled_plugins(self) -> List[str]:
        """Get list of disabled plugins."""
        return [name for name, plugin in self.plugins.items() if not plugin.enabled]
        
    def get_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin configuration."""
        return self.plugin_configs.get(plugin_name)
        
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """Set plugin configuration."""
        self.plugin_configs[plugin_name] = config
        self._save_plugin_configs() 