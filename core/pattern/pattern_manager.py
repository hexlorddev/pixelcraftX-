"""
Pattern management system for PixelCrafterX.
Handles image patterns, textures, and tiling.
"""

from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QBrush

@dataclass
class Pattern:
    name: str
    image: QImage
    tile_x: bool = True
    tile_y: bool = True
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    blend_mode: str = "normal"

class PatternManager:
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.active_pattern: Optional[Pattern] = None
        
    def create_pattern(self, name: str, image: QImage) -> Pattern:
        """Create a new pattern."""
        pattern = Pattern(name, image)
        self.patterns[name] = pattern
        return pattern
        
    def get_pattern(self, name: str) -> Optional[Pattern]:
        """Get pattern by name."""
        return self.patterns.get(name)
        
    def set_active_pattern(self, name: str) -> bool:
        """Set active pattern."""
        pattern = self.get_pattern(name)
        if pattern:
            self.active_pattern = pattern
            return True
        return False
        
    def get_active_pattern(self) -> Optional[Pattern]:
        """Get active pattern."""
        return self.active_pattern
        
    def delete_pattern(self, name: str) -> bool:
        """Delete pattern."""
        if name in self.patterns:
            del self.patterns[name]
            if self.active_pattern == self.patterns.get(name):
                self.active_pattern = None
            return True
        return False
        
    def get_pattern_names(self) -> List[str]:
        """Get list of pattern names."""
        return list(self.patterns.keys())
        
    def apply_pattern(self, image: QImage, pattern: Pattern, rect: Tuple[int, int, int, int]) -> QImage:
        """Apply pattern to image."""
        if image.isNull() or pattern.image.isNull():
            return image
            
        x, y, w, h = rect
        result = QImage(image)
        painter = QPainter(result)
        
        # Set pattern properties
        if pattern.tile_x and pattern.tile_y:
            painter.setBrush(QBrush(pattern.image))
        else:
            # Create non-tiling pattern
            pattern_image = QImage(pattern.image)
            if not pattern.tile_x:
                pattern_image = pattern_image.scaled(w, pattern_image.height())
            if not pattern.tile_y:
                pattern_image = pattern_image.scaled(pattern_image.width(), h)
            painter.setBrush(QBrush(pattern_image))
            
        # Apply transformations
        painter.translate(x + w/2, y + h/2)
        painter.rotate(pattern.rotation)
        painter.scale(pattern.scale_x, pattern.scale_y)
        painter.translate(-(x + w/2), -(y + h/2))
        
        # Set opacity and blend mode
        painter.setOpacity(pattern.opacity)
        
        # Draw pattern
        painter.fillRect(x, y, w, h, painter.brush())
        painter.end()
        
        return result
        
    def create_checkerboard_pattern(self, size: int = 32, color1: QColor = QColor(255, 255, 255),
                                  color2: QColor = QColor(200, 200, 200)) -> Pattern:
        """Create checkerboard pattern."""
        image = QImage(size * 2, size * 2, QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        
        # Draw checkerboard
        painter.fillRect(0, 0, size, size, color1)
        painter.fillRect(size, 0, size, size, color2)
        painter.fillRect(0, size, size, size, color2)
        painter.fillRect(size, size, size, size, color1)
        
        painter.end()
        return self.create_pattern("Checkerboard", image)
        
    def create_dots_pattern(self, size: int = 32, color: QColor = QColor(0, 0, 0),
                          background: QColor = QColor(255, 255, 255)) -> Pattern:
        """Create dots pattern."""
        image = QImage(size, size, QImage.Format.Format_ARGB32)
        image.fill(background)
        painter = QPainter(image)
        
        # Draw dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(size/4, size/4, size/2, size/2)
        
        painter.end()
        return self.create_pattern("Dots", image)
        
    def create_lines_pattern(self, size: int = 32, color: QColor = QColor(0, 0, 0),
                           background: QColor = QColor(255, 255, 255),
                           angle: float = 45) -> Pattern:
        """Create lines pattern."""
        image = QImage(size, size, QImage.Format.Format_ARGB32)
        image.fill(background)
        painter = QPainter(image)
        
        # Draw line
        painter.setPen(QPen(color, 2))
        painter.translate(size/2, size/2)
        painter.rotate(angle)
        painter.drawLine(-size/2, 0, size/2, 0)
        
        painter.end()
        return self.create_pattern("Lines", image)
        
    def create_default_patterns(self):
        """Create default patterns."""
        # Checkerboard
        self.create_checkerboard_pattern()
        
        # Dots
        self.create_dots_pattern()
        
        # Lines
        self.create_lines_pattern()
        
        # Set default active pattern
        self.set_active_pattern("Checkerboard") 