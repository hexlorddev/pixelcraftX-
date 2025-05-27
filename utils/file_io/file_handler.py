"""
File handling utilities for PixelCrafterX.
Handles file operations, formats, and metadata.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ExifTags
import json
import numpy as np
from PyQt6.QtGui import QImage

class FileHandler:
    SUPPORTED_FORMATS = {
        'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'],
        'project': ['.pxc', '.json'],
        'export': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.pdf']
    }
    
    def __init__(self):
        self.recent_files: List[str] = []
        self.max_recent_files = 10
        
    def load_image(self, file_path: str) -> Tuple[Optional[QImage], Dict[str, Any]]:
        """Load an image file and its metadata."""
        try:
            # Load image using PIL for metadata
            pil_image = Image.open(file_path)
            metadata = self._extract_metadata(pil_image)
            
            # Convert to QImage
            if pil_image.mode == 'RGBA':
                qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
            else:
                qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format.Format_RGB888)
                
            # Add to recent files
            self._add_recent_file(file_path)
            
            return qimage, metadata
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None, {}
            
    def save_image(self, image: QImage, file_path: str, format: str = 'PNG', quality: int = 95) -> bool:
        """Save an image to file."""
        try:
            # Convert QImage to PIL Image
            width = image.width()
            height = image.height()
            ptr = image.bits()
            ptr.setsize(height * width * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
            pil_image = Image.fromarray(arr)
            
            # Save image
            pil_image.save(file_path, format=format, quality=quality)
            
            # Add to recent files
            self._add_recent_file(file_path)
            
            return True
        except Exception as e:
            print(f"Error saving image {file_path}: {e}")
            return False
            
    def load_project(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load a project file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Add to recent files
            self._add_recent_file(file_path)
            
            return data
        except Exception as e:
            print(f"Error loading project {file_path}: {e}")
            return None
            
    def save_project(self, data: Dict[str, Any], file_path: str) -> bool:
        """Save a project file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            # Add to recent files
            self._add_recent_file(file_path)
            
            return True
        except Exception as e:
            print(f"Error saving project {file_path}: {e}")
            return False
            
    def _extract_metadata(self, image: Image.Image) -> Dict[str, Any]:
        """Extract metadata from an image."""
        metadata = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'dpi': image.info.get('dpi', (72, 72))
        }
        
        # Extract EXIF data
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif():
            for tag_id, value in image._getexif().items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
        metadata['exif'] = exif_data
        
        return metadata
        
    def _add_recent_file(self, file_path: str):
        """Add a file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:self.max_recent_files]
        
    def get_recent_files(self) -> List[str]:
        """Get list of recent files."""
        return self.recent_files
        
    def clear_recent_files(self):
        """Clear recent files list."""
        self.recent_files = []
        
    def is_supported_format(self, file_path: str, file_type: str = 'image') -> bool:
        """Check if file format is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_FORMATS.get(file_type, [])
        
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information."""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'extension': os.path.splitext(file_path)[1].lower()
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return {} 