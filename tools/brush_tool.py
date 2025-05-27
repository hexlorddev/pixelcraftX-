from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainter
import numpy as np

class BrushTool:
    def __init__(self):
        self.size = 10
        self.hardness = 0.8
        self.opacity = 1.0
        self.color = QColor(0, 0, 0)
        self.smoothing = 0.7
        self.pressure_sensitive = True
        
    def create_brush_mask(self):
        """Create a circular brush mask with hardness control."""
        size = int(self.size * 2)
        mask = np.zeros((size, size), dtype=np.float32)
        center = size // 2
        
        for y in range(size):
            for x in range(size):
                distance = np.sqrt((x - center) ** 2 + (y - center) ** 2)
                if distance <= self.size:
                    # Apply hardness
                    if distance <= self.size * self.hardness:
                        mask[y, x] = 1.0
                    else:
                        # Smooth falloff
                        falloff = (distance - self.size * self.hardness) / (self.size * (1 - self.hardness))
                        mask[y, x] = 1.0 - falloff
        
        return mask
    
    def apply_brush(self, painter: QPainter, start_point: QPointF, end_point: QPointF):
        """Apply brush stroke between two points."""
        pen = QPen(self.color)
        pen.setWidth(self.size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setOpacity(self.opacity)
        
        # Draw the line
        painter.drawLine(start_point, end_point)
        
        # Add pressure sensitivity if enabled
        if self.pressure_sensitive:
            # Simulate pressure variation
            pressure = 0.5 + 0.5 * np.sin(np.linspace(0, np.pi, 10))
            for p in pressure:
                pen.setWidth(int(self.size * p))
                painter.setPen(pen)
                painter.drawPoint(end_point) 