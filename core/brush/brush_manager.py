"""
Brush management system for PixelCrafterX.
Handles brush types, settings, and rendering.
"""

from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush

@dataclass
class BrushSettings:
    size: int = 10
    hardness: float = 0.8
    opacity: float = 1.0
    color: QColor = QColor(0, 0, 0, 255)
    pressure: float = 1.0
    spacing: float = 0.25
    angle: float = 0.0
    roundness: float = 1.0
    texture: Optional[np.ndarray] = None
    texture_scale: float = 1.0
    texture_rotation: float = 0.0
    texture_opacity: float = 1.0

class Brush:
    def __init__(self, settings: BrushSettings):
        self.settings = settings
        self._update_brush()
        
    def _update_brush(self):
        """Update brush properties."""
        # Create brush tip
        size = int(self.settings.size)
        self.tip = np.zeros((size, size), dtype=np.float32)
        
        # Calculate center and radius
        center = size / 2
        radius = size / 2
        
        # Create circular brush tip
        y, x = np.ogrid[-center:size-center, -center:size-center]
        dist = np.sqrt(x*x + y*y)
        
        # Apply hardness
        if self.settings.hardness < 1.0:
            inner_radius = radius * self.settings.hardness
            mask = np.clip((radius - dist) / (radius - inner_radius), 0, 1)
        else:
            mask = (dist <= radius).astype(np.float32)
            
        self.tip = mask
        
        # Apply texture if available
        if self.settings.texture is not None:
            self._apply_texture()
            
    def _apply_texture(self):
        """Apply texture to brush tip."""
        if self.settings.texture is None:
            return
            
        # Resize texture to match brush size
        from scipy.ndimage import zoom
        texture = self.settings.texture
        scale = self.settings.texture_scale
        size = self.tip.shape[0]
        
        # Calculate new size
        new_size = int(size * scale)
        if new_size < 1:
            new_size = 1
            
        # Resize texture
        if texture.shape != (new_size, new_size):
            texture = zoom(texture, new_size/texture.shape[0])
            
        # Rotate texture
        if self.settings.texture_rotation != 0:
            from scipy.ndimage import rotate
            texture = rotate(texture, self.settings.texture_rotation)
            
        # Center texture
        if texture.shape != self.tip.shape:
            y_offset = (self.tip.shape[0] - texture.shape[0]) // 2
            x_offset = (self.tip.shape[1] - texture.shape[1]) // 2
            centered = np.zeros_like(self.tip)
            centered[y_offset:y_offset+texture.shape[0],
                    x_offset:x_offset+texture.shape[1]] = texture
            texture = centered
            
        # Blend texture with brush tip
        self.tip = self.tip * (1 - self.settings.texture_opacity) + \
                  texture * self.settings.texture_opacity
                  
    def get_brush_tip(self) -> np.ndarray:
        """Get brush tip array."""
        return self.tip
        
    def get_brush_mask(self, pressure: float = 1.0) -> np.ndarray:
        """Get brush mask with pressure sensitivity."""
        mask = self.tip * pressure * self.settings.opacity
        return mask
        
    def get_brush_color(self) -> QColor:
        """Get brush color."""
        color = QColor(self.settings.color)
        color.setAlphaF(self.settings.opacity)
        return color
        
    def get_brush_size(self) -> int:
        """Get brush size."""
        return self.settings.size
        
    def get_brush_spacing(self) -> float:
        """Get brush spacing."""
        return self.settings.spacing * self.settings.size
        
    def get_brush_angle(self) -> float:
        """Get brush angle."""
        return self.settings.angle
        
    def get_brush_roundness(self) -> float:
        """Get brush roundness."""
        return self.settings.roundness

class BrushManager:
    def __init__(self):
        self.brushes: Dict[str, Brush] = {}
        self.active_brush: Optional[Brush] = None
        self.default_settings = BrushSettings()
        
    def create_brush(self, name: str, settings: Optional[BrushSettings] = None) -> Brush:
        """Create a new brush."""
        if settings is None:
            settings = BrushSettings()
        brush = Brush(settings)
        self.brushes[name] = brush
        return brush
        
    def get_brush(self, name: str) -> Optional[Brush]:
        """Get brush by name."""
        return self.brushes.get(name)
        
    def set_active_brush(self, name: str) -> bool:
        """Set active brush."""
        brush = self.get_brush(name)
        if brush:
            self.active_brush = brush
            return True
        return False
        
    def get_active_brush(self) -> Optional[Brush]:
        """Get active brush."""
        return self.active_brush
        
    def update_brush_settings(self, name: str, **kwargs) -> bool:
        """Update brush settings."""
        brush = self.get_brush(name)
        if brush:
            for key, value in kwargs.items():
                if hasattr(brush.settings, key):
                    setattr(brush.settings, key, value)
            brush._update_brush()
            return True
        return False
        
    def delete_brush(self, name: str) -> bool:
        """Delete brush."""
        if name in self.brushes:
            del self.brushes[name]
            if self.active_brush == self.brushes.get(name):
                self.active_brush = None
            return True
        return False
        
    def get_brush_names(self) -> List[str]:
        """Get list of brush names."""
        return list(self.brushes.keys())
        
    def create_default_brushes(self):
        """Create default brushes."""
        # Basic round brush
        self.create_brush("Round", BrushSettings(
            size=10,
            hardness=0.8,
            opacity=1.0,
            color=QColor(0, 0, 0, 255)
        ))
        
        # Soft brush
        self.create_brush("Soft", BrushSettings(
            size=15,
            hardness=0.3,
            opacity=0.8,
            color=QColor(0, 0, 0, 255)
        ))
        
        # Hard brush
        self.create_brush("Hard", BrushSettings(
            size=8,
            hardness=1.0,
            opacity=1.0,
            color=QColor(0, 0, 0, 255)
        ))
        
        # Set default active brush
        self.set_active_brush("Round") 