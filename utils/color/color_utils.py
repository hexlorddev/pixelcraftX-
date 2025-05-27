"""
Color utility functions for PixelCrafterX.
Handles color conversions, manipulations, and analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Union
from dataclasses import dataclass
from PyQt6.QtGui import QColor

@dataclass
class Color:
    r: int
    g: int
    b: int
    a: int = 255
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create a Color from hex string."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            hex_color += 'ff'
        return cls(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
            int(hex_color[6:8], 16)
        )
        
    @classmethod
    def from_qcolor(cls, qcolor: QColor) -> 'Color':
        """Create a Color from QColor."""
        return cls(
            qcolor.red(),
            qcolor.green(),
            qcolor.blue(),
            qcolor.alpha()
        )
        
    def to_hex(self) -> str:
        """Convert to hex string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"
        
    def to_qcolor(self) -> QColor:
        """Convert to QColor."""
        return QColor(self.r, self.g, self.b, self.a)
        
    def to_hsv(self) -> Tuple[float, float, float]:
        """Convert to HSV."""
        r, g, b = self.r / 255.0, self.g / 255.0, self.b / 255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val
        
        h = 0.0
        s = 0.0 if max_val == 0 else delta / max_val
        v = max_val
        
        if delta != 0:
            if max_val == r:
                h = (g - b) / delta
            elif max_val == g:
                h = 2 + (b - r) / delta
            else:
                h = 4 + (r - g) / delta
                
            h *= 60
            if h < 0:
                h += 360
                
        return h, s, v
        
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, a: int = 255) -> 'Color':
        """Create a Color from HSV."""
        h = h % 360
        s = max(0, min(1, s))
        v = max(0, min(1, v))
        
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return cls(
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255),
            a
        )

class ColorUtils:
    @staticmethod
    def blend_colors(color1: Color, color2: Color, factor: float = 0.5) -> Color:
        """Blend two colors."""
        factor = max(0, min(1, factor))
        return Color(
            int(color1.r * (1 - factor) + color2.r * factor),
            int(color1.g * (1 - factor) + color2.g * factor),
            int(color1.b * (1 - factor) + color2.b * factor),
            int(color1.a * (1 - factor) + color2.a * factor)
        )
        
    @staticmethod
    def adjust_brightness(color: Color, factor: float) -> Color:
        """Adjust color brightness."""
        factor = max(-1, min(1, factor))
        if factor > 0:
            return Color(
                int(color.r + (255 - color.r) * factor),
                int(color.g + (255 - color.g) * factor),
                int(color.b + (255 - color.b) * factor),
                color.a
            )
        else:
            return Color(
                int(color.r * (1 + factor)),
                int(color.g * (1 + factor)),
                int(color.b * (1 + factor)),
                color.a
            )
            
    @staticmethod
    def adjust_saturation(color: Color, factor: float) -> Color:
        """Adjust color saturation."""
        h, s, v = color.to_hsv()
        s = max(0, min(1, s * (1 + factor)))
        return Color.from_hsv(h, s, v, color.a)
        
    @staticmethod
    def get_complementary(color: Color) -> Color:
        """Get complementary color."""
        h, s, v = color.to_hsv()
        return Color.from_hsv((h + 180) % 360, s, v, color.a)
        
    @staticmethod
    def get_analogous(color: Color, angle: float = 30) -> Tuple[Color, Color]:
        """Get analogous colors."""
        h, s, v = color.to_hsv()
        return (
            Color.from_hsv((h + angle) % 360, s, v, color.a),
            Color.from_hsv((h - angle) % 360, s, v, color.a)
        )
        
    @staticmethod
    def get_triadic(color: Color) -> Tuple[Color, Color]:
        """Get triadic colors."""
        h, s, v = color.to_hsv()
        return (
            Color.from_hsv((h + 120) % 360, s, v, color.a),
            Color.from_hsv((h + 240) % 360, s, v, color.a)
        )
        
    @staticmethod
    def get_tetradic(color: Color) -> Tuple[Color, Color, Color]:
        """Get tetradic colors."""
        h, s, v = color.to_hsv()
        return (
            Color.from_hsv((h + 90) % 360, s, v, color.a),
            Color.from_hsv((h + 180) % 360, s, v, color.a),
            Color.from_hsv((h + 270) % 360, s, v, color.a)
        )
        
    @staticmethod
    def get_monochromatic(color: Color, count: int = 5) -> List[Color]:
        """Get monochromatic colors."""
        h, s, v = color.to_hsv()
        return [
            Color.from_hsv(h, s, v * (1 - i / (count - 1)), color.a)
            for i in range(count)
        ]
        
    @staticmethod
    def get_color_scheme(color: Color, scheme_type: str = 'complementary') -> List[Color]:
        """Get a color scheme."""
        if scheme_type == 'complementary':
            return [color, ColorUtils.get_complementary(color)]
        elif scheme_type == 'analogous':
            return [color] + list(ColorUtils.get_analogous(color))
        elif scheme_type == 'triadic':
            return [color] + list(ColorUtils.get_triadic(color))
        elif scheme_type == 'tetradic':
            return [color] + list(ColorUtils.get_tetradic(color))
        elif scheme_type == 'monochromatic':
            return [color] + ColorUtils.get_monochromatic(color)[1:]
        else:
            return [color] 