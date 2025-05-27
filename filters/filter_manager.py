"""
Filter management system for PixelCrafterX.
Handles image filters and effects.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
import numpy as np
from PyQt6.QtGui import QImage

class Filter(ABC):
    def __init__(self):
        self.name = "Base Filter"
        self.category = "General"
        self.description = "Base filter class"
        
    @abstractmethod
    def apply(self, image: QImage, **kwargs) -> QImage:
        """Apply the filter to an image."""
        pass
        
    def get_parameters(self) -> Dict:
        """Get filter parameters."""
        return {}
        
    def set_parameters(self, **kwargs):
        """Set filter parameters."""
        pass

class GaussianBlurFilter(Filter):
    def __init__(self):
        super().__init__()
        self.name = "Gaussian Blur"
        self.category = "Blur"
        self.description = "Apply Gaussian blur to an image"
        self.radius = 5.0
        
    def apply(self, image: QImage, **kwargs) -> QImage:
        """Apply Gaussian blur to the image."""
        # Convert QImage to numpy array
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        # Apply Gaussian blur
        from scipy.ndimage import gaussian_filter
        radius = kwargs.get('radius', self.radius)
        blurred = gaussian_filter(arr, sigma=radius)
        
        # Convert back to QImage
        result = QImage(blurred.tobytes(), width, height, QImage.Format.Format_ARGB32)
        return result
        
    def get_parameters(self) -> Dict:
        return {'radius': self.radius}
        
    def set_parameters(self, **kwargs):
        if 'radius' in kwargs:
            self.radius = float(kwargs['radius'])

class FilterManager:
    def __init__(self):
        self.filters: Dict[str, Filter] = {}
        self.categories: Dict[str, List[str]] = {}
        
    def register_filter(self, filter_class: Type[Filter]) -> bool:
        """Register a new filter."""
        filter_instance = filter_class()
        name = filter_instance.name
        
        if name not in self.filters:
            self.filters[name] = filter_instance
            category = filter_instance.category
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)
            return True
        return False
        
    def get_filter(self, name: str) -> Optional[Filter]:
        """Get a filter by name."""
        return self.filters.get(name)
        
    def get_filters_by_category(self, category: str) -> List[Filter]:
        """Get all filters in a category."""
        if category in self.categories:
            return [self.filters[name] for name in self.categories[category]]
        return []
        
    def get_categories(self) -> List[str]:
        """Get all filter categories."""
        return list(self.categories.keys())
        
    def apply_filter(self, name: str, image: QImage, **kwargs) -> Optional[QImage]:
        """Apply a filter to an image."""
        filter_instance = self.get_filter(name)
        if filter_instance:
            return filter_instance.apply(image, **kwargs)
        return None
        
    def get_filter_parameters(self, name: str) -> Dict:
        """Get parameters for a filter."""
        filter_instance = self.get_filter(name)
        if filter_instance:
            return filter_instance.get_parameters()
        return {}
        
    def set_filter_parameters(self, name: str, **kwargs):
        """Set parameters for a filter."""
        filter_instance = self.get_filter(name)
        if filter_instance:
            filter_instance.set_parameters(**kwargs) 