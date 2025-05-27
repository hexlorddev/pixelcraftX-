"""
Gradient management system for PixelCrafterX.
Handles color gradients, stops, and interpolation.
"""

from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass
from PyQt6.QtGui import QColor, QLinearGradient, QRadialGradient, QConicalGradient

@dataclass
class GradientStop:
    position: float  # 0.0 to 1.0
    color: QColor
    opacity: float = 1.0

class Gradient:
    def __init__(self, name: str = "New Gradient"):
        self.name = name
        self.stops: List[GradientStop] = []
        self.type = "linear"  # linear, radial, conical
        self.angle = 0.0
        self.center_x = 0.5
        self.center_y = 0.5
        self.radius = 0.5
        self.repeat = "pad"  # pad, repeat, reflect
        
    def add_stop(self, position: float, color: QColor, opacity: float = 1.0):
        """Add a color stop."""
        stop = GradientStop(position, color, opacity)
        self.stops.append(stop)
        self.stops.sort(key=lambda x: x.position)
        
    def remove_stop(self, index: int):
        """Remove a color stop."""
        if 0 <= index < len(self.stops):
            self.stops.pop(index)
            
    def move_stop(self, index: int, position: float):
        """Move a color stop."""
        if 0 <= index < len(self.stops):
            self.stops[index].position = max(0.0, min(1.0, position))
            self.stops.sort(key=lambda x: x.position)
            
    def set_stop_color(self, index: int, color: QColor):
        """Set stop color."""
        if 0 <= index < len(self.stops):
            self.stops[index].color = color
            
    def set_stop_opacity(self, index: int, opacity: float):
        """Set stop opacity."""
        if 0 <= index < len(self.stops):
            self.stops[index].opacity = max(0.0, min(1.0, opacity))
            
    def get_qgradient(self, rect: Tuple[float, float, float, float]) -> QLinearGradient | QRadialGradient | QConicalGradient:
        """Get Qt gradient object."""
        x, y, w, h = rect
        
        if self.type == "linear":
            gradient = QLinearGradient(x, y, x + w, y + h)
            gradient.setAngle(self.angle)
        elif self.type == "radial":
            center_x = x + w * self.center_x
            center_y = y + h * self.center_y
            radius = min(w, h) * self.radius
            gradient = QRadialGradient(center_x, center_y, radius)
        else:  # conical
            center_x = x + w * self.center_x
            center_y = y + h * self.center_y
            gradient = QConicalGradient(center_x, center_y, self.angle)
            
        # Set spread method
        if self.repeat == "repeat":
            gradient.setSpread(QGradient.Spread.RepeatSpread)
        elif self.repeat == "reflect":
            gradient.setSpread(QGradient.Spread.ReflectSpread)
        else:
            gradient.setSpread(QGradient.Spread.PadSpread)
            
        # Add stops
        for stop in self.stops:
            color = QColor(stop.color)
            color.setAlphaF(stop.opacity)
            gradient.setColorAt(stop.position, color)
            
        return gradient
        
    def get_colors(self, steps: int = 256) -> np.ndarray:
        """Get interpolated colors."""
        if not self.stops:
            return np.zeros((steps, 4), dtype=np.uint8)
            
        # Create position and color arrays
        positions = np.array([stop.position for stop in self.stops])
        colors = np.array([[stop.color.red(), stop.color.green(), 
                           stop.color.blue(), int(stop.color.alpha() * stop.opacity)]
                          for stop in self.stops])
                          
        # Create output array
        output = np.zeros((steps, 4), dtype=np.uint8)
        
        # Interpolate colors
        for i in range(steps):
            pos = i / (steps - 1)
            
            # Find surrounding stops
            idx = np.searchsorted(positions, pos)
            if idx == 0:
                output[i] = colors[0]
            elif idx == len(positions):
                output[i] = colors[-1]
            else:
                # Linear interpolation
                t = (pos - positions[idx-1]) / (positions[idx] - positions[idx-1])
                output[i] = colors[idx-1] * (1-t) + colors[idx] * t
                
        return output
        
    def reverse(self):
        """Reverse gradient direction."""
        for stop in self.stops:
            stop.position = 1.0 - stop.position
        self.stops.sort(key=lambda x: x.position)
        
    def duplicate(self) -> 'Gradient':
        """Create a copy of the gradient."""
        new_gradient = Gradient(f"{self.name} (copy)")
        new_gradient.type = self.type
        new_gradient.angle = self.angle
        new_gradient.center_x = self.center_x
        new_gradient.center_y = self.center_y
        new_gradient.radius = self.radius
        new_gradient.repeat = self.repeat
        new_gradient.stops = [GradientStop(stop.position, QColor(stop.color), stop.opacity)
                            for stop in self.stops]
        return new_gradient

class GradientManager:
    def __init__(self):
        self.gradients: Dict[str, Gradient] = {}
        self.active_gradient: Optional[Gradient] = None
        
    def create_gradient(self, name: str) -> Gradient:
        """Create a new gradient."""
        gradient = Gradient(name)
        self.gradients[name] = gradient
        return gradient
        
    def get_gradient(self, name: str) -> Optional[Gradient]:
        """Get gradient by name."""
        return self.gradients.get(name)
        
    def set_active_gradient(self, name: str) -> bool:
        """Set active gradient."""
        gradient = self.get_gradient(name)
        if gradient:
            self.active_gradient = gradient
            return True
        return False
        
    def get_active_gradient(self) -> Optional[Gradient]:
        """Get active gradient."""
        return self.active_gradient
        
    def delete_gradient(self, name: str) -> bool:
        """Delete gradient."""
        if name in self.gradients:
            del self.gradients[name]
            if self.active_gradient == self.gradients.get(name):
                self.active_gradient = None
            return True
        return False
        
    def get_gradient_names(self) -> List[str]:
        """Get list of gradient names."""
        return list(self.gradients.keys())
        
    def create_default_gradients(self):
        """Create default gradients."""
        # Black to white
        bw = self.create_gradient("Black to White")
        bw.add_stop(0.0, QColor(0, 0, 0))
        bw.add_stop(1.0, QColor(255, 255, 255))
        
        # Rainbow
        rainbow = self.create_gradient("Rainbow")
        rainbow.add_stop(0.0, QColor(255, 0, 0))  # Red
        rainbow.add_stop(0.2, QColor(255, 255, 0))  # Yellow
        rainbow.add_stop(0.4, QColor(0, 255, 0))  # Green
        rainbow.add_stop(0.6, QColor(0, 255, 255))  # Cyan
        rainbow.add_stop(0.8, QColor(0, 0, 255))  # Blue
        rainbow.add_stop(1.0, QColor(255, 0, 255))  # Magenta
        
        # Sunset
        sunset = self.create_gradient("Sunset")
        sunset.add_stop(0.0, QColor(255, 165, 0))  # Orange
        sunset.add_stop(0.5, QColor(255, 0, 128))  # Pink
        sunset.add_stop(1.0, QColor(128, 0, 255))  # Purple
        
        # Set default active gradient
        self.set_active_gradient("Black to White") 