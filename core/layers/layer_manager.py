"""
Layer management system for PixelCrafterX.
Handles layer operations and organization.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from PyQt6.QtGui import QImage

@dataclass
class Layer:
    name: str
    image: QImage
    visible: bool = True
    opacity: float = 1.0
    blend_mode: str = "normal"
    locked: bool = False

class LayerManager:
    def __init__(self):
        self.layers: List[Layer] = []
        self.active_layer_index: Optional[int] = None
        
    def add_layer(self, width: int, height: int, name: str = "New Layer") -> Layer:
        """Add a new layer to the stack."""
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(0)  # Transparent
        layer = Layer(name=name, image=image)
        self.layers.append(layer)
        self.active_layer_index = len(self.layers) - 1
        return layer
        
    def remove_layer(self, index: int) -> bool:
        """Remove a layer from the stack."""
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            if self.active_layer_index == index:
                self.active_layer_index = max(0, len(self.layers) - 1)
            return True
        return False
        
    def move_layer(self, from_index: int, to_index: int) -> bool:
        """Move a layer to a new position in the stack."""
        if 0 <= from_index < len(self.layers) and 0 <= to_index < len(self.layers):
            layer = self.layers.pop(from_index)
            self.layers.insert(to_index, layer)
            if self.active_layer_index == from_index:
                self.active_layer_index = to_index
            return True
        return False
        
    def duplicate_layer(self, index: int) -> Optional[Layer]:
        """Create a copy of a layer."""
        if 0 <= index < len(self.layers):
            original = self.layers[index]
            new_image = QImage(original.image)
            new_layer = Layer(
                name=f"{original.name} (copy)",
                image=new_image,
                visible=original.visible,
                opacity=original.opacity,
                blend_mode=original.blend_mode,
                locked=original.locked
            )
            self.layers.insert(index + 1, new_layer)
            self.active_layer_index = index + 1
            return new_layer
        return None
        
    def merge_layers(self, indices: List[int]) -> Optional[Layer]:
        """Merge multiple layers into one."""
        if not indices or not all(0 <= i < len(self.layers) for i in indices):
            return None
            
        # Get the first layer as base
        base = self.layers[indices[0]]
        result = QImage(base.image)
        
        # Merge other layers
        for i in indices[1:]:
            layer = self.layers[i]
            if layer.visible:
                # Convert to numpy arrays for efficient blending
                base_array = np.array(result.bits()).reshape(result.height(), result.width(), 4)
                layer_array = np.array(layer.image.bits()).reshape(layer.image.height(), layer.image.width(), 4)
                
                # Apply blend mode and opacity
                if layer.blend_mode == "normal":
                    alpha = layer.opacity
                    base_array = base_array * (1 - alpha) + layer_array * alpha
                
                # Convert back to QImage
                result = QImage(base_array.tobytes(), result.width(), result.height(), QImage.Format.Format_ARGB32)
        
        # Create new merged layer
        merged = Layer(
            name="Merged Layer",
            image=result,
            visible=True,
            opacity=1.0
        )
        
        # Remove old layers and add merged layer
        for i in sorted(indices, reverse=True):
            self.layers.pop(i)
        self.layers.append(merged)
        self.active_layer_index = len(self.layers) - 1
        
        return merged
        
    @property
    def active_layer(self) -> Optional[Layer]:
        """Get the currently active layer."""
        if self.active_layer_index is not None and 0 <= self.active_layer_index < len(self.layers):
            return self.layers[self.active_layer_index]
        return None 