import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

class BasicFilters:
    @staticmethod
    def apply_gaussian_blur(image: Image.Image, radius: float = 2.0) -> Image.Image:
        """Apply Gaussian blur to the image."""
        return image.filter(ImageFilter.GaussianBlur(radius))
    
    @staticmethod
    def apply_sharpen(image: Image.Image, factor: float = 2.0) -> Image.Image:
        """Sharpen the image."""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_brightness(image: Image.Image, factor: float = 1.0) -> Image.Image:
        """Adjust image brightness."""
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_contrast(image: Image.Image, factor: float = 1.0) -> Image.Image:
        """Adjust image contrast."""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_saturation(image: Image.Image, factor: float = 1.0) -> Image.Image:
        """Adjust image saturation."""
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def apply_emboss(image: Image.Image) -> Image.Image:
        """Apply emboss effect to the image."""
        return image.filter(ImageFilter.EMBOSS)
    
    @staticmethod
    def apply_edge_enhance(image: Image.Image, factor: float = 2.0) -> Image.Image:
        """Enhance edges in the image."""
        return image.filter(ImageFilter.EDGE_ENHANCE_MORE) 