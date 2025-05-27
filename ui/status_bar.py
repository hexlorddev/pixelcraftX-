"""Custom status bar widget for PixelCrafter X."""
from PyQt6.QtWidgets import (QStatusBar, QLabel, QHBoxLayout, QWidget, 
                           QSizePolicy, QToolButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QColor, QPainter

class StatusBar(QStatusBar):
    """Custom status bar with zoom, cursor position, and tool info."""
    
    zoomChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d30;
                color: #d4d4d4;
                border-top: 1px solid #3e3e42;
                padding: 2px 8px;
            }
            QLabel {
                color: #d4d4d4;
                padding: 0 8px;
                border-right: 1px solid #3e3e42;
            }
            QToolButton {
                border: none;
                background: transparent;
                padding: 0 4px;
            }
            QToolButton:hover {
                background: #3e3e42;
            }
        """)
        
        self.zoom_level = 100.0
        self.cursor_pos = (0, 0)
        self.image_size = (0, 0)
        self.current_tool = "Select"
        self.zoom_levels = [25, 50, 75, 100, 150, 200, 300, 400, 600, 800, 1200, 1600, 2400, 3200, 4800, 6400]
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Create a container widget for our custom status bar
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Current tool indicator
        self.tool_label = QLabel("Tool: " + self.current_tool)
        self.tool_label.setFixedWidth(120)
        
        # Cursor position
        self.position_label = QLabel("X: 0, Y: 0")
        self.position_label.setFixedWidth(120)
        
        # Image size
        self.size_label = QLabel("Size: 0 x 0 px")
        self.size_label.setFixedWidth(150)
        
        # Zoom controls
        zoom_container = QWidget()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(0)
        
        # Zoom out button
        self.zoom_out_btn = QToolButton()
        self.zoom_out_btn.setText("-")
        self.zoom_out_btn.setFixedSize(24, 20)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        # Zoom percentage
        self.zoom_label = QLabel(f"{int(self.zoom_level)}%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setFixedWidth(60)
        
        # Zoom in button
        self.zoom_in_btn = QToolButton()
        self.zoom_in_btn.setText("+")
        self.zoom_in_btn.setFixedSize(24, 20)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        # Add zoom controls to layout
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        # Add all widgets to layout
        layout.addWidget(self.tool_label)
        layout.addWidget(self.position_label)
        layout.addWidget(self.size_label)
        layout.addStretch()
        layout.addWidget(zoom_container)
        
        # Add the container to the status bar
        self.addPermanentWidget(container, 1)
        
        # Update the UI
        self.update_zoom_buttons()
    
    def set_tool(self, tool_name):
        """Set the current tool name."""
        self.current_tool = tool_name
        self.tool_label.setText(f"Tool: {tool_name}")
    
    def set_cursor_position(self, x, y):
        """Update the cursor position display."""
        self.cursor_pos = (int(x), int(y))
        self.position_label.setText(f"X: {self.cursor_pos[0]}, Y: {self.cursor_pos[1]}")
    
    def set_image_size(self, width, height):
        """Update the image size display."""
        self.image_size = (int(width), int(height))
        self.size_label.setText(f"Size: {self.image_size[0]} x {self.image_size[1]} px")
    
    def set_zoom(self, zoom_level):
        """Set the zoom level."""
        self.zoom_level = max(1.0, min(3200.0, zoom_level))
        self.zoom_label.setText(f"{int(self.zoom_level)}%")
        self.update_zoom_buttons()
        self.zoomChanged.emit(self.zoom_level / 100.0)
    
    def zoom_in(self):
        """Zoom in to the next zoom level."""
        for level in sorted(self.zoom_levels):
            if level > self.zoom_level:
                self.set_zoom(level)
                break
        else:
            self.set_zoom(min(self.zoom_level * 1.5, 3200))
    
    def zoom_out(self):
        """Zoom out to the previous zoom level."""
        for level in reversed(sorted(self.zoom_levels)):
            if level < self.zoom_level:
                self.set_zoom(level)
                break
        else:
            self.set_zoom(max(self.zoom_level / 1.5, 1.0))
    
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.set_zoom(100.0)
    
    def update_zoom_buttons(self):
        """Update the enabled state of zoom buttons."""
        self.zoom_in_btn.setEnabled(self.zoom_level < 3200)
        self.zoom_out_btn.setEnabled(self.zoom_level > 1)


class StatusBarSeparator(QFrame):
    """A vertical separator for the status bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        self.setFixedHeight(16)
        self.setStyleSheet("color: #3e3e42;")
