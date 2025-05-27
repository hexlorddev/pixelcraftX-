"""
Configuration management system for PixelCrafterX.
Handles application settings, user preferences, and configuration files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class AppConfig:
    # General settings
    language: str = "en"
    theme: str = "dark"
    auto_save: bool = True
    auto_save_interval: int = 300  # seconds
    
    # Canvas settings
    default_canvas_width: int = 1920
    default_canvas_height: int = 1080
    default_canvas_dpi: int = 300
    default_background_color: str = "#808080"
    
    # Tool settings
    default_brush_size: int = 10
    default_brush_hardness: float = 0.8
    default_brush_opacity: float = 1.0
    
    # Performance settings
    use_gpu: bool = True
    max_undo_steps: int = 50
    cache_size: int = 1024  # MB
    
    # AI settings
    ai_model_path: str = "models"
    use_cuda: bool = True
    batch_size: int = 4
    
    # Export settings
    default_export_format: str = "png"
    default_export_quality: int = 95
    preserve_metadata: bool = True

class ConfigManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.settings_file = self.config_dir / "settings.json"
        self.shortcuts_file = self.config_dir / "shortcuts.json"
        self.themes_file = self.config_dir / "themes.json"
        self.ai_models_file = self.config_dir / "ai_models.json"
        
        self.config = AppConfig()
        self.shortcuts: Dict[str, str] = {}
        self.themes: Dict[str, Dict[str, str]] = {}
        self.ai_models: Dict[str, Dict[str, Any]] = {}
        
        self._ensure_config_dir()
        self._load_all_configs()
        
    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_all_configs(self):
        """Load all configuration files."""
        self._load_settings()
        self._load_shortcuts()
        self._load_themes()
        self._load_ai_models()
        
    def _load_settings(self):
        """Load application settings."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
            except Exception as e:
                print(f"Error loading settings: {e}")
                
    def _load_shortcuts(self):
        """Load keyboard shortcuts."""
        if self.shortcuts_file.exists():
            try:
                with open(self.shortcuts_file, 'r') as f:
                    self.shortcuts = json.load(f)
            except Exception as e:
                print(f"Error loading shortcuts: {e}")
                
    def _load_themes(self):
        """Load UI themes."""
        if self.themes_file.exists():
            try:
                with open(self.themes_file, 'r') as f:
                    self.themes = json.load(f)
            except Exception as e:
                print(f"Error loading themes: {e}")
                
    def _load_ai_models(self):
        """Load AI model configurations."""
        if self.ai_models_file.exists():
            try:
                with open(self.ai_models_file, 'r') as f:
                    self.ai_models = json.load(f)
            except Exception as e:
                print(f"Error loading AI models: {e}")
                
    def save_settings(self):
        """Save application settings."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def save_shortcuts(self):
        """Save keyboard shortcuts."""
        try:
            with open(self.shortcuts_file, 'w') as f:
                json.dump(self.shortcuts, f, indent=4)
        except Exception as e:
            print(f"Error saving shortcuts: {e}")
            
    def save_themes(self):
        """Save UI themes."""
        try:
            with open(self.themes_file, 'w') as f:
                json.dump(self.themes, f, indent=4)
        except Exception as e:
            print(f"Error saving themes: {e}")
            
    def save_ai_models(self):
        """Save AI model configurations."""
        try:
            with open(self.ai_models_file, 'w') as f:
                json.dump(self.ai_models, f, indent=4)
        except Exception as e:
            print(f"Error saving AI models: {e}")
            
    def get_setting(self, key: str) -> Any:
        """Get a setting value."""
        return getattr(self.config, key, None)
        
    def set_setting(self, key: str, value: Any):
        """Set a setting value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_settings()
            
    def get_shortcut(self, action: str) -> Optional[str]:
        """Get keyboard shortcut for an action."""
        return self.shortcuts.get(action)
        
    def set_shortcut(self, action: str, shortcut: str):
        """Set keyboard shortcut for an action."""
        self.shortcuts[action] = shortcut
        self.save_shortcuts()
        
    def get_theme(self, name: str) -> Optional[Dict[str, str]]:
        """Get UI theme by name."""
        return self.themes.get(name)
        
    def set_theme(self, name: str, theme: Dict[str, str]):
        """Set UI theme."""
        self.themes[name] = theme
        self.save_themes()
        
    def get_ai_model(self, name: str) -> Optional[Dict[str, Any]]:
        """Get AI model configuration by name."""
        return self.ai_models.get(name)
        
    def set_ai_model(self, name: str, config: Dict[str, Any]):
        """Set AI model configuration."""
        self.ai_models[name] = config
        self.save_ai_models() 