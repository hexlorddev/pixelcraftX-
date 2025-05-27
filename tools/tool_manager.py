"""
Tool management system for PixelCrafterX.
Handles tool registration, activation, and state management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Type
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor

class Tool(ABC):
    def __init__(self):
        self.active = False
        self.cursor = Qt.CursorShape.ArrowCursor
        
    @abstractmethod
    def activate(self):
        """Activate the tool."""
        pass
        
    @abstractmethod
    def deactivate(self):
        """Deactivate the tool."""
        pass
        
    @abstractmethod
    def mouse_press(self, event):
        """Handle mouse press events."""
        pass
        
    @abstractmethod
    def mouse_move(self, event):
        """Handle mouse move events."""
        pass
        
    @abstractmethod
    def mouse_release(self, event):
        """Handle mouse release events."""
        pass
        
    @abstractmethod
    def draw_preview(self, painter: QPainter):
        """Draw tool preview."""
        pass

class BrushTool(Tool):
    def __init__(self):
        super().__init__()
        self.cursor = Qt.CursorShape.CrossCursor
        self.size = 10
        self.color = QColor(0, 0, 0, 255)
        self.hardness = 0.8
        self.pressure = 1.0
        
    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False
        
    def mouse_press(self, event):
        if self.active:
            # Start drawing
            pass
            
    def mouse_move(self, event):
        if self.active:
            # Continue drawing
            pass
            
    def mouse_release(self, event):
        if self.active:
            # End drawing
            pass
            
    def draw_preview(self, painter: QPainter):
        if self.active:
            # Draw brush preview
            pass

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.active_tool: Optional[Tool] = None
        
    def register_tool(self, name: str, tool_class: Type[Tool]) -> bool:
        """Register a new tool."""
        if name not in self.tools:
            self.tools[name] = tool_class()
            return True
        return False
        
    def activate_tool(self, name: str) -> bool:
        """Activate a tool by name."""
        if name in self.tools:
            if self.active_tool:
                self.active_tool.deactivate()
            self.active_tool = self.tools[name]
            self.active_tool.activate()
            return True
        return False
        
    def deactivate_current_tool(self):
        """Deactivate the current tool."""
        if self.active_tool:
            self.active_tool.deactivate()
            self.active_tool = None
            
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
        
    def get_active_tool(self) -> Optional[Tool]:
        """Get the currently active tool."""
        return self.active_tool
        
    def handle_mouse_press(self, event):
        """Handle mouse press events."""
        if self.active_tool:
            self.active_tool.mouse_press(event)
            
    def handle_mouse_move(self, event):
        """Handle mouse move events."""
        if self.active_tool:
            self.active_tool.mouse_move(event)
            
    def handle_mouse_release(self, event):
        """Handle mouse release events."""
        if self.active_tool:
            self.active_tool.mouse_release(event)
            
    def draw_tool_preview(self, painter: QPainter):
        """Draw the active tool's preview."""
        if self.active_tool:
            self.active_tool.draw_preview(painter) 