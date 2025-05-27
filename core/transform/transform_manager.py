"""
Transformation management system for PixelCrafterX.
Handles image transformations, scaling, rotation, and perspective.
"""

from typing import List, Optional, Tuple, Union
import numpy as np
from PyQt6.QtCore import QPoint, QRect, QTransform
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QBrush

class Transform:
    def __init__(self):
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.rotation = 0.0
        self.skew_x = 0.0
        self.skew_y = 0.0
        self.translate_x = 0.0
        self.translate_y = 0.0
        
    def get_matrix(self) -> QTransform:
        """Get transformation matrix."""
        matrix = QTransform()
        matrix.translate(self.translate_x, self.translate_y)
        matrix.rotate(self.rotation)
        matrix.scale(self.scale_x, self.scale_y)
        matrix.shear(self.skew_x, self.skew_y)
        return matrix
        
    def reset(self):
        """Reset transformation."""
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.rotation = 0.0
        self.skew_x = 0.0
        self.skew_y = 0.0
        self.translate_x = 0.0
        self.translate_y = 0.0

class TransformManager:
    def __init__(self):
        self.transform = Transform()
        self.pivot = QPoint(0, 0)
        self.mode = "free"  # free, constrained
        
    def set_transform_mode(self, mode: str):
        """Set transformation mode."""
        if mode in ["free", "constrained"]:
            self.mode = mode
            
    def set_pivot(self, x: float, y: float):
        """Set transformation pivot point."""
        self.pivot = QPoint(int(x), int(y))
        
    def scale(self, sx: float, sy: float):
        """Scale transformation."""
        if self.mode == "constrained":
            scale = min(sx, sy)
            self.transform.scale_x *= scale
            self.transform.scale_y *= scale
        else:
            self.transform.scale_x *= sx
            self.transform.scale_y *= sy
            
    def rotate(self, angle: float):
        """Rotate transformation."""
        self.transform.rotation += angle
        
    def skew(self, sx: float, sy: float):
        """Skew transformation."""
        self.transform.skew_x += sx
        self.transform.skew_y += sy
        
    def translate(self, dx: float, dy: float):
        """Translate transformation."""
        self.transform.translate_x += dx
        self.transform.translate_y += dy
        
    def reset_transform(self):
        """Reset transformation."""
        self.transform.reset()
        
    def apply_transform(self, image: QImage) -> QImage:
        """Apply transformation to image."""
        if image.isNull():
            return image
            
        # Create transformed image
        matrix = self.transform.get_matrix()
        transformed = QImage(image.size(), QImage.Format.Format_ARGB32)
        transformed.fill(Qt.GlobalColor.transparent)
        
        # Apply transformation
        painter = QPainter(transformed)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Move to pivot point
        painter.translate(self.pivot)
        painter.setTransform(matrix)
        painter.translate(-self.pivot)
        
        # Draw image
        painter.drawImage(0, 0, image)
        painter.end()
        
        return transformed
        
    def get_bounds(self, rect: QRect) -> QRect:
        """Get transformed bounds."""
        matrix = self.transform.get_matrix()
        return matrix.mapRect(rect)
        
    def is_identity(self) -> bool:
        """Check if transformation is identity."""
        return (self.transform.scale_x == 1.0 and
                self.transform.scale_y == 1.0 and
                self.transform.rotation == 0.0 and
                self.transform.skew_x == 0.0 and
                self.transform.skew_y == 0.0 and
                self.transform.translate_x == 0.0 and
                self.transform.translate_y == 0.0)
                
    def get_scale(self) -> Tuple[float, float]:
        """Get scale factors."""
        return self.transform.scale_x, self.transform.scale_y
        
    def get_rotation(self) -> float:
        """Get rotation angle."""
        return self.transform.rotation
        
    def get_skew(self) -> Tuple[float, float]:
        """Get skew factors."""
        return self.transform.skew_x, self.transform.skew_y
        
    def get_translation(self) -> Tuple[float, float]:
        """Get translation offsets."""
        return self.transform.translate_x, self.transform.translate_y 