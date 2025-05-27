"""
Selection management system for PixelCrafterX.
Handles image selections, masks, and transformations.
"""

from typing import List, Optional, Tuple, Union
import numpy as np
from PyQt6.QtCore import QRect, QPoint
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QBrush

class Selection:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.mask = np.zeros((height, width), dtype=np.uint8)
        self.active = False
        self.rect = QRect()
        
    def set_rect(self, rect: QRect):
        """Set selection rectangle."""
        self.rect = rect
        self.active = True
        self._update_mask()
        
    def add_rect(self, rect: QRect):
        """Add rectangle to selection."""
        self.rect = self.rect.united(rect)
        self.active = True
        self._update_mask()
        
    def subtract_rect(self, rect: QRect):
        """Subtract rectangle from selection."""
        if self.rect.intersects(rect):
            self.rect = self.rect.subtracted(rect)
            self._update_mask()
            
    def clear(self):
        """Clear selection."""
        self.mask.fill(0)
        self.active = False
        self.rect = QRect()
        
    def _update_mask(self):
        """Update selection mask."""
        self.mask.fill(0)
        if self.active and not self.rect.isEmpty():
            x, y = self.rect.x(), self.rect.y()
            w, h = self.rect.width(), self.rect.height()
            self.mask[y:y+h, x:x+w] = 255
            
    def get_mask(self) -> np.ndarray:
        """Get selection mask."""
        return self.mask
        
    def is_point_selected(self, x: int, y: int) -> bool:
        """Check if point is selected."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.mask[y, x] > 0
        return False
        
    def get_bounds(self) -> QRect:
        """Get selection bounds."""
        return self.rect
        
    def is_active(self) -> bool:
        """Check if selection is active."""
        return self.active

class SelectionManager:
    def __init__(self):
        self.selection: Optional[Selection] = None
        self.mode = "replace"  # replace, add, subtract
        self.feather_radius = 0
        
    def create_selection(self, width: int, height: int):
        """Create new selection."""
        self.selection = Selection(width, height)
        
    def set_selection_mode(self, mode: str):
        """Set selection mode."""
        if mode in ["replace", "add", "subtract"]:
            self.mode = mode
            
    def set_feather_radius(self, radius: int):
        """Set feather radius."""
        self.feather_radius = max(0, radius)
        
    def add_rect(self, rect: QRect):
        """Add rectangle to selection."""
        if not self.selection:
            return
            
        if self.mode == "replace":
            self.selection.set_rect(rect)
        elif self.mode == "add":
            self.selection.add_rect(rect)
        elif self.mode == "subtract":
            self.selection.subtract_rect(rect)
            
    def clear_selection(self):
        """Clear selection."""
        if self.selection:
            self.selection.clear()
            
    def get_selection_mask(self) -> Optional[np.ndarray]:
        """Get selection mask."""
        if self.selection and self.selection.is_active():
            mask = self.selection.get_mask()
            if self.feather_radius > 0:
                from scipy.ndimage import gaussian_filter
                mask = gaussian_filter(mask, sigma=self.feather_radius)
            return mask
        return None
        
    def is_point_selected(self, x: int, y: int) -> bool:
        """Check if point is selected."""
        if self.selection:
            return self.selection.is_point_selected(x, y)
        return False
        
    def get_selection_bounds(self) -> Optional[QRect]:
        """Get selection bounds."""
        if self.selection:
            return self.selection.get_bounds()
        return None
        
    def is_selection_active(self) -> bool:
        """Check if selection is active."""
        if self.selection:
            return self.selection.is_active()
        return False
        
    def invert_selection(self):
        """Invert selection."""
        if self.selection and self.selection.is_active():
            self.selection.mask = 255 - self.selection.mask
            
    def grow_selection(self, pixels: int):
        """Grow selection by pixels."""
        if self.selection and self.selection.is_active():
            from scipy.ndimage import binary_dilation
            self.selection.mask = binary_dilation(self.selection.mask, iterations=pixels)
            
    def shrink_selection(self, pixels: int):
        """Shrink selection by pixels."""
        if self.selection and self.selection.is_active():
            from scipy.ndimage import binary_erosion
            self.selection.mask = binary_erosion(self.selection.mask, iterations=pixels)
            
    def smooth_selection(self):
        """Smooth selection edges."""
        if self.selection and self.selection.is_active():
            from scipy.ndimage import gaussian_filter
            self.selection.mask = gaussian_filter(self.selection.mask, sigma=1.0) 