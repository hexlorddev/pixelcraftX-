#!/usr/bin/env python3
"""
PixelCrafterX - Professional Image Editing Suite
Main application entry point
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the application environment."""
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Create necessary directories if they don't exist
    for dir_path in [
        'config/settings',
        'config/shortcuts',
        'config/themes',
        'config/ai_models',
        'assets/icons',
        'assets/brushes',
        'assets/palettes',
        'assets/textures',
        'assets/sounds'
    ]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def main():
    """Main application entry point."""
    try:
        # Setup environment
        setup_environment()
        logger.info("Environment setup complete")
        
        # Import core components
        from core.plugin_manager import PluginManager
        from ui.main_window.window import MainWindow
        
        # Initialize plugin system
        plugin_manager = PluginManager()
        if not plugin_manager.initialize():
            logger.error("Failed to initialize plugin system")
            return 1
        
        # Create and show main window
        app = MainWindow(plugin_manager)
        app.run()
        
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
