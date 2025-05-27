import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PluginConfig:
    def __init__(self, config_dir: str = "config/plugins"):
        self.config_dir = config_dir
        self.configs: Dict[str, Dict] = {}
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def load_config(self, plugin_name: str) -> Optional[Dict]:
        """Load configuration for a specific plugin."""
        config_path = os.path.join(self.config_dir, f"{plugin_name}.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.configs[plugin_name] = config
                    return config
            except Exception as e:
                logger.error(f"Error loading config for {plugin_name}: {e}")
        return None
    
    def save_config(self, plugin_name: str, config: Dict) -> bool:
        """Save configuration for a specific plugin."""
        try:
            config_path = os.path.join(self.config_dir, f"{plugin_name}.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            self.configs[plugin_name] = config
            return True
        except Exception as e:
            logger.error(f"Error saving config for {plugin_name}: {e}")
            return False
    
    def get_config(self, plugin_name: str) -> Optional[Dict]:
        """Get configuration for a specific plugin."""
        if plugin_name not in self.configs:
            return self.load_config(plugin_name)
        return self.configs.get(plugin_name)
    
    def update_config(self, plugin_name: str, updates: Dict) -> bool:
        """Update configuration for a specific plugin."""
        current_config = self.get_config(plugin_name) or {}
        updated_config = {**current_config, **updates}
        return self.save_config(plugin_name, updated_config)
    
    def delete_config(self, plugin_name: str) -> bool:
        """Delete configuration for a specific plugin."""
        try:
            config_path = os.path.join(self.config_dir, f"{plugin_name}.json")
            if os.path.exists(config_path):
                os.remove(config_path)
            self.configs.pop(plugin_name, None)
            return True
        except Exception as e:
            logger.error(f"Error deleting config for {plugin_name}: {e}")
            return False 