"""
Core canvas module for PixelCrafterX.
Handles the main canvas operations and rendering.
"""

import numpy as np
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QImage
from PyQt6.QtWidgets import QWidget

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.active_layer = None
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.setMouseTracking(True)
        
    def add_layer(self, width, height, name="New Layer"):
        """Add a new layer to the canvas."""
        layer = {
            'name': name,
            'image': QImage(width, height, QImage.Format.Format_ARGB32),
            'visible': True,
            'opacity': 1.0
        }
        layer['image'].fill(Qt.GlobalColor.transparent)
        self.layers.append(layer)
        self.active_layer = layer
        self.update()
        
    def remove_layer(self, index):
        """Remove a layer from the canvas."""
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            if self.active_layer in self.layers:
                self.active_layer = self.layers[-1]
            self.update()
            
    def paintEvent(self, event):
        """Handle canvas painting."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        # Draw layers
        for layer in self.layers:
            if layer['visible']:
                painter.setOpacity(layer['opacity'])
                painter.drawImage(0, 0, layer['image'])
                
    def resizeEvent(self, event):
        """Handle canvas resizing."""
        super().resizeEvent(event)
        self.update()
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.zoom = max(0.1, min(10.0, self.zoom))
        self.update()
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle mouse movement for panning."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.pos() - self.last_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_pos = event.pos()
            self.update() 