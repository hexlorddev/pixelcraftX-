"""
Canvas module for PixelCrafter X.
Handles the main drawing area and user interactions.
"""
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QRubberBand,
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsPathItem, QGraphicsTextItem, QInputDialog
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPixmap, QColor, QPen, QBrush, QPainterPath,
    QImage, QKeyEvent, QMouseEvent, QWheelEvent,
    QTransform, QCursor, QFont, QFontMetrics
)
import numpy as np
from typing import Optional, Union, Tuple, List, Dict, Any

class Canvas(QGraphicsView):
    """
    Main canvas widget that handles drawing and image manipulation.
    """
    # Signals
    mouseMoved = pyqtSignal(QPointF)
    zoomChanged = pyqtSignal(float)
    
    def __init__(self, config=None, parent=None):
        """
        Initialize the canvas.
        
        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config or {}
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Canvas properties
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.zoom_step = 0.1
        self.background_color = QColor(50, 50, 50)
        self.grid_size = 20
        self.grid_color = QColor(60, 60, 60, 100)
        self.show_grid = True
        self.show_rulers = True
        
        # Drawing properties
        self.drawing = False
        self.last_point = QPointF()
        self.current_tool = 'select'  # 'select', 'brush', 'eraser', 'shape', 'text', 'fill', etc.
        self.brush_size = 5
        self.brush_color = QColor(Qt.GlobalColor.black)
        self.brush_opacity = 1.0
        self.eraser_size = 20
        self.eraser_opacity = 1.0
        
        # Current drawing item
        self.current_item = None
        self.temp_path = None
        
        # Selection
        self.selection_start = QPointF()
        self.selection_rect = None
        self.selected_items = []
        
        # Layers
        self.layers = []
        self.current_layer_index = 0
        
        # History for undo/redo
        self.history = []
        self.history_index = -1
        self.max_history = 50
        
        # Setup view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMouseTracking(True)
        
        # Create default layer
        self.add_layer("Layer 1")
        
        # Set default brush
        # Initialize selection
        self.selection_end = QPointF()
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
        # Current shape properties
        self.shape_type = 'rectangle'  # 'rectangle', 'ellipse', 'line', 'arrow', 'text'
        self.fill_shape = False
        self.shape_start = QPointF()
        self.shape_end = QPointF()
        
        # Text properties
        self.text_font = QFont('Arial', 12)
        self.text_color = QColor(Qt.GlobalColor.black)
        
        # Connect signals
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
    def update_brush(self):
        """Update the brush properties."""
        self.brush = QPen()
        self.brush.setColor(self.brush_color)
        self.brush.setWidthF(self.brush_size)
        self.brush.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.brush.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
    def update_eraser(self):
        """Update the eraser properties."""
        self.eraser = QPen()
        self.eraser.setColor(QColor(255, 255, 255, int(255 * self.eraser_opacity)))
        self.eraser.setWidthF(self.eraser_size)
        self.eraser.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.eraser.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    
    def set_tool(self, tool_name: str):
        """Set the current drawing tool."""
        self.current_tool = tool_name
        
        # Update cursor based on tool
        if tool_name == 'select':
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif tool_name == 'brush':
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool_name == 'eraser':
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool_name in ['rectangle', 'ellipse', 'line', 'arrow']:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool_name == 'text':
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif tool_name == 'fill':
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def set_brush_color(self, color: QColor):
        """Set the brush color."""
        self.brush_color = color
        self.update_brush()
    
    def set_brush_size(self, size: float):
        """Set the brush size."""
        self.brush_size = size
        self.update_brush()
    
    def set_brush_opacity(self, opacity: float):
        """Set the brush opacity (0.0 to 1.0)."""
        self.brush_opacity = max(0.0, min(1.0, opacity))
        self.brush_color.setAlphaF(self.brush_opacity)
        self.update_brush()
    
    def set_eraser_size(self, size: float):
        """Set the eraser size."""
        self.eraser_size = size
        self.update_eraser()
    
    def set_eraser_opacity(self, opacity: float):
        """Set the eraser opacity (0.0 to 1.0)."""
        self.eraser_opacity = max(0.0, min(1.0, opacity))
        self.update_eraser()
    
    def add_layer(self, name: str):
        """Add a new layer to the canvas."""
        layer = {
            'name': name,
            'visible': True,
            'opacity': 1.0,
            'locked': False,
            'items': []
        }
        self.layers.append(layer)
        self.current_layer_index = len(self.layers) - 1
        return layer
    
    def remove_layer(self, index: int):
        """Remove a layer from the canvas."""
        if 0 <= index < len(self.layers):
            # Remove all items in the layer
            for item in self.layers[index]['items']:
                if item.scene() == self.scene():
                    self.scene().removeItem(item)
            
            # Remove the layer
            self.layers.pop(index)
            
            # Update current layer index if needed
            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = max(0, len(self.layers) - 1)
    
    def get_current_layer(self) -> dict:
        """Get the current active layer."""
        if not self.layers:
            return self.add_layer("Layer 1")
        return self.layers[self.current_layer_index]
    
    def save_state(self):
        """Save the current canvas state to history."""
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Save current state
        state = {
            'layers': [],
            'current_layer': self.current_layer_index
        }
        
        self.history.append(state)
        self.history_index = len(self.history) - 1
    
    def undo(self):
        """Undo the last action."""
        if self.history_index > 0:
            self.history_index -= 1
            self.restore_state(self.history[self.history_index])
    
    def redo(self):
        """Redo the last undone action."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.restore_state(self.history[self.history_index])
    
    def restore_state(self, state: dict):
        """Restore canvas state from history."""
        # Clear current scene
        self.scene().clear()
        
        # Restore layers
        self.layers = state.get('layers', [])
        self.current_layer_index = state.get('current_layer', 0)
        
        # Redraw all items
        for layer in self.layers:
            for item in layer.get('items', []):
                self.scene().addItem(item)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            self.last_point = pos
            self.drawing = True
            
            if self.current_tool == 'select':
                self.selection_start = pos
                self.rubber_band.setGeometry(QRect(self.mapFromScene(pos).toPoint(), QSize()))
                self.rubber_band.show()
            
            elif self.current_tool in ['rectangle', 'ellipse', 'line', 'arrow']:
                self.shape_start = pos
                self.shape_end = pos
                self.current_item = None
            
            elif self.current_tool == 'text':
                self.add_text_item(pos)
            
            elif self.current_tool == 'fill':
                self.fill_area(pos)
            
            else:  # brush, eraser
                self.start_drawing(pos)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        pos = self.mapToScene(event.pos())
        self.mouseMoved.emit(pos)
        
        if self.drawing:
            if self.current_tool == 'select':
                self.update_rubber_band(pos)
            
            elif self.current_tool in ['rectangle', 'ellipse', 'line', 'arrow']:
                self.update_shape(pos)
            
            elif self.current_tool in ['brush', 'eraser']:
                self.continue_drawing(pos)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            
            if self.current_tool == 'select':
                self.rubber_band.hide()
                self.select_items_in_rect()
            
            elif self.current_tool in ['rectangle', 'ellipse', 'line', 'arrow']:
                self.finalize_shape()
            
            # Save state after drawing
            self.save_state()
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        # Zoom with Ctrl + Mouse Wheel
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.zoom(zoom_factor)
        else:
            super().wheelEvent(event)
    
    def zoom(self, factor: float):
        """Zoom the canvas by the given factor."""
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level * factor))
        
        # Only update if zoom level actually changed
        if self.zoom_level != old_zoom:
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            self.scale(factor, factor)
            self.zoomChanged.emit(self.zoom_level)
    
    def start_drawing(self, pos: QPointF):
        """Start drawing with the current tool."""
        layer = self.get_current_layer()
        if layer.get('locked', False):
            return
        
        if self.current_tool == 'brush':
            path = QPainterPath()
            path.moveTo(pos)
            self.temp_path = self.scene().addPath(path, self.brush)
            layer['items'].append(self.temp_path)
        
        elif self.current_tool == 'eraser':
            # For eraser, we'll draw a line to simulate erasing
            path = QPainterPath()
            path.moveTo(pos)
            self.temp_path = self.scene().addPath(path, self.eraser)
            layer['items'].append(self.temp_path)
    
    def continue_drawing(self, pos: QPointF):
        """Continue drawing with the current tool."""
        if self.temp_path is None:
            return
        
        if self.current_tool in ['brush', 'eraser']:
            path = self.temp_path.path()
            path.lineTo(pos)
            self.temp_path.setPath(path)
            self.last_point = pos
    
    def update_rubber_band(self, pos: QPointF):
        """Update the rubber band selection rectangle."""
        rect = QRectF(self.selection_start, pos).normalized()
        self.rubber_band.setGeometry(QRect(
            self.mapFromScene(rect.topLeft()).toPoint(),
            self.mapFromScene(rect.bottomRight()).toPoint()
        ))
    
    def select_items_in_rect(self):
        """Select items within the rubber band rectangle."""
        rect = QRectF(self.selection_start, self.mapToScene(self.rubber_band.geometry().bottomRight()))
        
        # Clear current selection
        for item in self.selected_items:
            item.setSelected(False)
        self.selected_items.clear()
        
        # Select items in the rectangle
        for item in self.scene().items(rect, Qt.ItemSelectionMode.ContainsItemShape):
            if isinstance(item, QGraphicsItem):
                item.setSelected(True)
                self.selected_items.append(item)
    
    def update_shape(self, pos: QPointF):
        """Update the current shape being drawn."""
        self.shape_end = pos
        
        if self.current_item is not None:
            self.scene().removeItem(self.current_item)
        
        if self.current_tool == 'rectangle':
            rect = QRectF(self.shape_start, self.shape_end).normalized()
            self.current_item = self.scene().addRect(rect, self.brush, 
                                                   QBrush(self.brush_color) if self.fill_shape else Qt.BrushStyle.NoBrush)
        
        elif self.current_tool == 'ellipse':
            rect = QRectF(self.shape_start, self.shape_end).normalized()
            self.current_item = self.scene().addEllipse(rect, self.brush,
                                                      QBrush(self.brush_color) if self.fill_shape else Qt.BrushStyle.NoBrush)
        
        elif self.current_tool in ['line', 'arrow']:
            path = QPainterPath()
            path.moveTo(self.shape_start)
            path.lineTo(self.shape_end)
            
            if self.current_tool == 'arrow':
                # Add arrowhead
                angle = self.shape_start.angleTo(self.shape_end)
                arrow_size = 10.0
                
                p1 = self.shape_end - QPointF(
                    arrow_size * 0.5 * (1.0 + math.cos(angle + math.pi / 4)),
                    arrow_size * 0.5 * (1.0 + math.sin(angle + math.pi / 4))
                )
                p2 = self.shape_end - QPointF(
                    arrow_size * 0.5 * (1.0 + math.cos(angle - math.pi / 4)),
                    arrow_size * 0.5 * (1.0 + math.sin(angle - math.pi / 4))
                )
                
                path.moveTo(self.shape_end)
                path.lineTo(p1)
                path.moveTo(self.shape_end)
                path.lineTo(p2)
            
            self.current_item = self.scene().addPath(path, self.brush)
    
    def finalize_shape(self):
        """Finalize the current shape and add it to the layer."""
        if self.current_item is not None:
            layer = self.get_current_layer()
            if not layer.get('locked', False):
                layer['items'].append(self.current_item)
                self.current_item = None
    
    def add_text_item(self, pos: QPointF):
        """Add a text item at the given position."""
        text, ok = QInputDialog.getText(self, 'Add Text', 'Enter text:')
        if ok and text:
            text_item = QGraphicsTextItem(text)
            text_item.setDefaultTextColor(self.text_color)
            text_item.setFont(self.text_font)
            text_item.setPos(pos)
            
            layer = self.get_current_layer()
            if not layer.get('locked', False):
                self.scene().addItem(text_item)
                layer['items'].append(text_item)
                self.save_state()
    
    def fill_area(self, pos: QPointF):
        """Fill an area with the current brush color."""
        # This is a simplified implementation
        # A full implementation would require flood fill algorithm
        rect = QRectF(pos.x() - 5, pos.y() - 5, 10, 10)
        item = self.scene().addRect(rect, QPen(Qt.PenStyle.NoPen), 
                                   QBrush(self.brush_color, Qt.BrushStyle.SolidPattern))
        
        layer = self.get_current_layer()
        if not layer.get('locked', False):
            layer['items'].append(item)
            self.save_state()
    
    def on_selection_changed(self):
        """Handle selection changes in the scene."""
        self.selected_items = self.scene().selectedItems()
    
    def clear_selection(self):
        """Clear the current selection."""
        for item in self.selected_items:
            item.setSelected(False)
        self.selected_items.clear()
    
    def delete_selected(self):
        """Delete selected items."""
        for item in self.selected_items:
            if item.scene() == self.scene():
                self.scene().removeItem(item)
        self.selected_items.clear()
        self.save_state()
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Draw the canvas background and grid."""
        # Fill with background color
        painter.fillRect(rect, self.background_color)
        
        # Draw grid if enabled
        if self.show_grid and self.zoom_level > 0.5:  # Only show grid when zoomed in enough
            grid_pen = QPen(self.grid_color, 0.5 / self.zoom_level)
            painter.setPen(grid_pen)
            
            # Calculate visible grid lines
            left = int(rect.left()) - (int(rect.left()) % self.grid_size)
            top = int(rect.top()) - (int(rect.top()) % self.grid_size)
            
            # Draw vertical lines
            x = left
            while x < rect.right():
                painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
                x += self.grid_size
            
            # Draw horizontal lines
            y = top
            while y < rect.bottom():
                painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
                y += self.grid_size
    
    def save_image(self, file_path: str) -> bool:
        """Save the canvas to an image file."""
        try:
            # Create a QImage with the size of the scene
            rect = self.scene().sceneRect()
            image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            
            # Render the scene onto the image
            painter = QPainter(image)
            self.scene().render(painter)
            painter.end()
            
            # Save the image
            return image.save(file_path)
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def load_image(self, file_path: str) -> bool:
        """Load an image file onto the canvas."""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Clear existing content
                self.scene().clear()
                
                # Add the image to the scene
                self.scene().addPixmap(pixmap)
                self.scene().setSceneRect(pixmap.rect())
                
                # Reset view
                self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                
                # Reset zoom level
                self.zoom_level = 1.0
                self.zoomChanged.emit(self.zoom_level)
                
                return True
            return False
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        if self.scene() is not None:
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # Setup view
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform |
            QPainter.RenderHint.TextAntialiasing
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        # Create a default blank image
        self.create_new_canvas(800, 600, QColor(255, 255, 255, 255))
        
        # Set up mouse tracking
        self.setMouseTracking(True)
    
    def create_new_canvas(self, width, height, bg_color=Qt.GlobalColor.white):
        """
        Create a new blank canvas.
        
        Args:
            width: Width of the canvas
            height: Height of the canvas
            bg_color: Background color
        """
        self.scene.clear()
        self.canvas_image = QImage(width, height, QImage.Format.Format_ARGB32)
        self.canvas_image.fill(bg_color)
        
        # Create a pixmap item to hold the image
        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setPixmap(QPixmap.fromImage(self.canvas_image))
        self.scene.addItem(self.pixmap_item)
        
        # Update scene rect to match image size
        self.scene.setSceneRect(0, 0, width, height)
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.zoom(zoom_factor, event.position())
    
    def zoom(self, factor, pos=None):
        """
        Zoom the canvas by the given factor.
        
        Args:
            factor: Zoom factor (e.g., 1.1 for zoom in, 0.9 for zoom out)
            pos: Position to zoom towards (in view coordinates)
        """
        if pos is None:
            pos = self.viewport().rect().center()
            
        # Calculate the scene position before zooming
        old_pos = self.mapToScene(pos.toPoint())
        
        # Apply zoom
        new_zoom = self.zoom_level * factor
        
        # Limit zoom levels
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
            
        self.zoom_level = new_zoom
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        
        # Scale the view
        self.setTransform(QTransform().scale(self.zoom_level, self.zoom_level))
        
        # Calculate the new position to maintain the same point under the cursor
        new_pos = self.mapToScene(pos.toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
        # Restore anchor settings
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = self.mapToScene(event.pos())
            
            if self.current_tool == 'select':
                self.selection_start = self.last_point
                self.rubber_band.setGeometry(QRect(
                    self.mapFromScene(self.selection_start).toPoint(),
                    QSize()
                ))
                self.rubber_band.show()
            
            # Add other tool handlers here
            
            self.viewport().update()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if self.drawing:
            current_point = self.mapToScene(event.pos())
            
            if self.current_tool == 'select':
                self.selection_end = current_point
                self.update_rubber_band()
            # Add other tool handlers here
            
            self.last_point = current_point
            self.viewport().update()
        
        # Update cursor position in status bar if needed
        self.parent().statusBar().showMessage(f"X: {int(event.pos().x())}, Y: {int(event.pos().y())}")
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            
            if self.current_tool == 'select':
                self.selection_end = self.mapToScene(event.pos())
                self.update_rubber_band()
            # Add other tool handlers here
            
            self.viewport().update()
        
        super().mouseReleaseEvent(event)
    
    def update_rubber_band(self):
        """Update the rubber band selection rectangle."""
        start = self.mapFromScene(self.selection_start).toPoint()
        end = self.mapFromScene(self.selection_end).toPoint()
        
        rect = QRect(start, end).normalized()
        self.rubber_band.setGeometry(rect)
    
    def drawBackground(self, painter: QPainter, rect):
        """Draw the canvas background and grid."""
        # Fill with background color
        painter.fillRect(rect, self.background_color)
        
        # Draw grid if enabled
        if self.show_grid:
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))
            
            # Calculate visible grid lines
            grid_size = self.grid_size
            left = int(rect.left()) - (int(rect.left()) % grid_size)
            top = int(rect.top()) - (int(rect.top()) % grid_size)
            
            # Draw vertical lines
            for x in range(left, int(rect.right()), grid_size):
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            
            # Draw horizontal lines
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def set_tool(self, tool_name):
        """
        Set the current drawing tool.
        
        Args:
            tool_name: Name of the tool to set ('select', 'brush', 'eraser', etc.)
        """
        self.current_tool = tool_name
        
        # Update cursor based on tool
        if tool_name == 'select':
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif tool_name == 'brush':
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool_name == 'eraser':
            self.setCursor(Qt.CursorShape.CrossCursor)
        # Add more tool-specific cursors as needed
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)