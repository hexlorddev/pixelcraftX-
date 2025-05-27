"""
Canvas view component for PixelCrafterX.
Handles canvas display and user interaction.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QImage

from core.canvas.canvas import Canvas
from core.tools.tool_manager import ToolManager
from core.layers.layer_manager import LayerManager
from core.history.history_manager import HistoryManager

class CanvasView(QWidget):
    # Signals
    canvas_changed = pyqtSignal()
    tool_changed = pyqtSignal(str)
    color_changed = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Create managers
        self.canvas = Canvas()
        self.tool_manager = ToolManager()
        self.layer_manager = LayerManager()
        self.history_manager = HistoryManager()
        
        # Initialize state
        self.zoom = 1.0
        self.offset = QPoint(0, 0)
        self.is_panning = False
        self.last_pos = QPoint()
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    def paintEvent(self, event):
        """Handle paint event."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        # Apply zoom and offset
        painter.translate(self.offset)
        painter.scale(self.zoom, self.zoom)
        
        # Draw canvas
        self.canvas.draw(painter)
        
        # Draw tool preview
        if self.tool_manager.active_tool:
            self.tool_manager.active_tool.draw_preview(painter)
            
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.is_panning = True
                self.last_pos = event.pos()
            else:
                # Convert to canvas coordinates
                pos = self.canvas_to_image(event.pos())
                if self.tool_manager.active_tool:
                    self.tool_manager.active_tool.mouse_press(pos, event)
                    
    def mouseMoveEvent(self, event):
        """Handle mouse move event."""
        if self.is_panning:
            delta = event.pos() - self.last_pos
            self.offset += delta
            self.last_pos = event.pos()
            self.update()
        else:
            # Convert to canvas coordinates
            pos = self.canvas_to_image(event.pos())
            if self.tool_manager.active_tool:
                self.tool_manager.active_tool.mouse_move(pos, event)
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_panning:
                self.is_panning = False
            else:
                # Convert to canvas coordinates
                pos = self.canvas_to_image(event.pos())
                if self.tool_manager.active_tool:
                    self.tool_manager.active_tool.mouse_release(pos, event)
                    
    def wheelEvent(self, event):
        """Handle mouse wheel event."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.zoom *= factor
            self.zoom = max(0.1, min(10.0, self.zoom))
            self.update()
        else:
            # Scroll
            delta = event.angleDelta().y()
            self.offset.setY(self.offset.y() - delta)
            self.update()
            
    def canvas_to_image(self, pos: QPoint) -> QPoint:
        """Convert widget coordinates to canvas coordinates."""
        x = (pos.x() - self.offset.x()) / self.zoom
        y = (pos.y() - self.offset.y()) / self.zoom
        return QPoint(int(x), int(y))
        
    def image_to_canvas(self, pos: QPoint) -> QPoint:
        """Convert canvas coordinates to widget coordinates."""
        x = pos.x() * self.zoom + self.offset.x()
        y = pos.y() * self.zoom + self.offset.y()
        return QPoint(int(x), int(y))
        
    def set_tool(self, tool_name: str):
        """Set active tool."""
        self.tool_manager.set_active_tool(tool_name)
        self.tool_changed.emit(tool_name)
        
    def set_color(self, color: QColor):
        """Set active color."""
        if self.tool_manager.active_tool:
            self.tool_manager.active_tool.set_color(color)
            self.color_changed.emit(color)
            
    def update_layers(self):
        """Update layer display."""
        self.canvas.update_layers()
        self.update()
        
    def undo(self):
        """Undo last action."""
        if self.history_manager.undo():
            self.canvas_changed.emit()
            self.update()
            
    def redo(self):
        """Redo last undone action."""
        if self.history_manager.redo():
            self.canvas_changed.emit()
            self.update()
            
    def zoom_in(self):
        """Zoom in."""
        self.zoom *= 1.1
        self.zoom = min(10.0, self.zoom)
        self.update()
        
    def zoom_out(self):
        """Zoom out."""
        self.zoom *= 0.9
        self.zoom = max(0.1, self.zoom)
        self.update()
        
    def zoom_fit(self):
        """Fit canvas to window."""
        if self.canvas.width() > 0 and self.canvas.height() > 0:
            # Calculate zoom to fit
            zoom_x = self.width() / self.canvas.width()
            zoom_y = self.height() / self.canvas.height()
            self.zoom = min(zoom_x, zoom_y)
            
            # Center canvas
            self.offset = QPoint(
                (self.width() - self.canvas.width() * self.zoom) / 2,
                (self.height() - self.canvas.height() * self.zoom) / 2
            )
            self.update() 