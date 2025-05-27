"""
Configuration management for PixelCrafter X.
Handles loading, saving, and validating application settings.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
default_config = {
    "app": {
        "version": "0.1.0",
        "theme": "dark",  # 'light' or 'dark'
        "language": "en_US",
        "auto_save": True,
        "auto_save_interval": 5,  # minutes
        "recent_files": [],
        "max_recent_files": 10,
    },
    "canvas": {
        "default_width": 1920,
        "default_height": 1080,
        "default_dpi": 300,
        "default_color": "#FFFFFF",  # White background
        "grid_enabled": True,
        "grid_size": 20,
        "grid_color": "#CCCCCC",
        "ruler_visible": True,
    },
    "performance": {
        "use_gpu": True,
        "gpu_backend": "auto",  # 'auto', 'opengl', 'vulkan', 'software'
        "cache_size_mb": 1024,
        "threads": 0,  # 0 = auto
    },
    "tools": {
        "brush": {
            "default_size": 10,
            "default_hardness": 0.8,
            "default_opacity": 1.0,
            "smoothing": 0.7,
        },
        "eraser": {
            "default_size": 30,
            "default_hardness": 1.0,
            "default_opacity": 1.0,
        },
    },
    "shortcuts": {
        "new_file": "Ctrl+N",
        "open_file": "Ctrl+O",
        "save_file": "Ctrl+S",
        "save_as": "Ctrl+Shift+S",
        "undo": "Ctrl+Z",
        "redo": "Ctrl+Y",
        "copy": "Ctrl+C",
        "paste": "Ctrl+V",
        "cut": "Ctrl+X",
        "delete": "Del",
        "select_all": "Ctrl+A",
        "deselect": "Ctrl+D",
        "zoom_in": "Ctrl++",
        "zoom_out": "Ctrl+-",
        "zoom_fit": "Ctrl+0",
        "zoom_100": "Ctrl+1",
    },
}

CONFIG_FILE = "config/settings.yaml"

def get_config_dir() -> Path:
    """Get the configuration directory for PixelCrafter X."""
    if os.name == 'nt':  # Windows
        config_dir = Path.home() / 'AppData' / 'Local' / 'PixelCrafterX'
    elif os.name == 'posix':  # macOS/Linux
        config_dir = Path.home() / '.config' / 'pixelcrafterx'
    else:
        config_dir = Path.cwd() / 'config'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return get_config_dir() / 'config.json'

def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or return default configuration.
    
    Returns:
        dict: The loaded or default configuration.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return default_config

def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: The configuration to save.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)
    return True

def deep_merge(base: Dict[Any, Any], update: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Recursively merge two dictionaries.
    
    Args:
        base: The base dictionary to update.
        update: The dictionary with updates.
        
    Returns:
        dict: The merged dictionary.
    """
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def get_shortcut(action: str) -> str:
    """
    Get the keyboard shortcut for an action.
    
    Args:
        action: The action to get the shortcut for.
        
    Returns:
        str: The keyboard shortcut or an empty string if not found.
    """
    config = load_config()
    return config.get('shortcuts', {}).get(action, '')

def update_shortcut(action: str, shortcut: str) -> bool:
    """
    Update a keyboard shortcut.
    
    Args:
        action: The action to update the shortcut for.
        shortcut: The new keyboard shortcut.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    config = load_config()
    
    if 'shortcuts' not in config:
        config['shortcuts'] = {}
    
    config['shortcuts'][action] = shortcut
    return save_config(config)
