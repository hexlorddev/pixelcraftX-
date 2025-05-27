"""
AI model management system for PixelCrafterX.
Handles AI models, their loading, and inference.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type, Any
import torch
import numpy as np
from PyQt6.QtGui import QImage

class AIModel(ABC):
    def __init__(self):
        self.name = "Base Model"
        self.category = "General"
        self.description = "Base AI model class"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        
    @abstractmethod
    def load(self):
        """Load the model."""
        pass
        
    @abstractmethod
    def unload(self):
        """Unload the model."""
        pass
        
    @abstractmethod
    def process(self, image: QImage, **kwargs) -> QImage:
        """Process an image using the model."""
        pass
        
    def get_parameters(self) -> Dict:
        """Get model parameters."""
        return {}
        
    def set_parameters(self, **kwargs):
        """Set model parameters."""
        pass

class StyleTransferModel(AIModel):
    def __init__(self):
        super().__init__()
        self.name = "Style Transfer"
        self.category = "Artistic"
        self.description = "Transfer artistic style to images"
        self.style_strength = 0.5
        
    def load(self):
        """Load the style transfer model."""
        try:
            # Load model from torch hub or local path
            self.model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
            self.model.to(self.device)
            self.model.eval()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
            
    def unload(self):
        """Unload the model."""
        if self.model is not None:
            self.model.cpu()
            torch.cuda.empty_cache()
            self.model = None
            
    def process(self, image: QImage, **kwargs) -> QImage:
        """Process an image using style transfer."""
        if self.model is None:
            return image
            
        # Convert QImage to tensor
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        tensor = torch.from_numpy(arr).float().div(255.0)
        tensor = tensor.permute(2, 0, 1).unsqueeze(0)
        tensor = tensor.to(self.device)
        
        # Apply style transfer
        with torch.no_grad():
            output = self.model(tensor)
            
        # Convert back to QImage
        output = output.squeeze(0).permute(1, 2, 0)
        output = output.cpu().numpy()
        output = (output * 255).astype(np.uint8)
        result = QImage(output.tobytes(), width, height, QImage.Format.Format_ARGB32)
        return result
        
    def get_parameters(self) -> Dict:
        return {'style_strength': self.style_strength}
        
    def set_parameters(self, **kwargs):
        if 'style_strength' in kwargs:
            self.style_strength = float(kwargs['style_strength'])

class AIModelManager:
    def __init__(self):
        self.models: Dict[str, AIModel] = {}
        self.categories: Dict[str, List[str]] = {}
        
    def register_model(self, model_class: Type[AIModel]) -> bool:
        """Register a new AI model."""
        model_instance = model_class()
        name = model_instance.name
        
        if name not in self.models:
            self.models[name] = model_instance
            category = model_instance.category
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)
            return True
        return False
        
    def load_model(self, name: str) -> bool:
        """Load a model by name."""
        model = self.get_model(name)
        if model:
            return model.load()
        return False
        
    def unload_model(self, name: str):
        """Unload a model by name."""
        model = self.get_model(name)
        if model:
            model.unload()
            
    def get_model(self, name: str) -> Optional[AIModel]:
        """Get a model by name."""
        return self.models.get(name)
        
    def get_models_by_category(self, category: str) -> List[AIModel]:
        """Get all models in a category."""
        if category in self.categories:
            return [self.models[name] for name in self.categories[category]]
        return []
        
    def get_categories(self) -> List[str]:
        """Get all model categories."""
        return list(self.categories.keys())
        
    def process_image(self, name: str, image: QImage, **kwargs) -> Optional[QImage]:
        """Process an image using a model."""
        model = self.get_model(name)
        if model:
            return model.process(image, **kwargs)
        return None
        
    def get_model_parameters(self, name: str) -> Dict:
        """Get parameters for a model."""
        model = self.get_model(name)
        if model:
            return model.get_parameters()
        return {}
        
    def set_model_parameters(self, name: str, **kwargs):
        """Set parameters for a model."""
        model = self.get_model(name)
        if model:
            model.set_parameters(**kwargs) 