"""Custom color palette widget for managing color swatches."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolButton, 
                           QLabel, QColorDialog, QMenu, QSizePolicy, QFrame,
                           QGridLayout, QSpacerItem, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QSettings, QFile, QIODevice
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPixmap, QIcon, QAction
import json
import os

class ColorSwatch(QWidget):
    """A single color swatch in the palette."""
    
    clicked = pyqtSignal(QColor, str)  # color, name
    
    def __init__(self, color=Qt.GlobalColor.white, name="", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.name = name
        self.hovered = False
        self.selected = False
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{self.name} ({self.color.name()})" if self.name else self.color.name())
    
    def paintEvent(self, event):
        """Paint the color swatch."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        border_color = QColor(100, 100, 100) if self.hovered or self.selected else QColor(200, 200, 200)
        painter.setPen(QPen(border_color, 1, Qt.PenStyle.SolidLine))
        
        # Fill with color
        if self.color.alpha() < 255:
            # Draw checkerboard for transparent colors
            self.draw_checkerboard(painter, self.rect())
        
        painter.setBrush(QBrush(self.color))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 2, 2)
        
        # Draw selection highlight
        if self.selected:
            painter.setPen(QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), 3, 3)
    
    def draw_checkerboard(self, painter, rect):
        """Draw a checkerboard pattern for transparent colors."""
        size = 4
        color1 = QColor(200, 200, 200)
        color2 = QColor(255, 255, 255)
        
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        
        for y in range(rect.top(), rect.bottom() + size, size):
            for x in range(rect.left(), rect.right() + size, size):
                color = color1 if ((x + y) // size) % 2 == 0 else color2
                painter.fillRect(x, y, size, size, color)
        
        painter.restore()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self.hovered = True
        self.update()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self.hovered = False
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.color, self.name)
    
    def set_selected(self, selected):
        """Set the selected state of the swatch."""
        if self.selected != selected:
            self.selected = selected
            self.update()
    
    def set_color(self, color, name=""):
        """Set the color and optionally the name of the swatch."""
        self.color = QColor(color)
        if name:
            self.name = name
        self.setToolTip(f"{self.name} ({self.color.name()})" if self.name else self.color.name())
        self.update()


class ColorPalette(QWidget):
    """A customizable color palette widget."""
    
    colorSelected = pyqtSignal(QColor, str)  # color, name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.swatches = []
        self.selected_swatch = None
        self.rows = 10
        self.cols = 10
        self.spacing = 2
        self.swatch_size = 24
        
        # Default color palette
        self.default_colors = [
            (Qt.GlobalColor.white, "White"),
            (Qt.GlobalColor.lightGray, "Light Gray"),
            (Qt.GlobalColor.gray, "Gray"),
            (Qt.GlobalColor.darkGray, "Dark Gray"),
            (Qt.GlobalColor.black, "Black"),
            (Qt.GlobalColor.red, "Red"),
            (Qt.GlobalColor.green, "Green"),
            (Qt.GlobalColor.blue, "Blue"),
            (Qt.GlobalColor.cyan, "Cyan"),
            (Qt.GlobalColor.magenta, "Magenta"),
            (Qt.GlobalColor.yellow, "Yellow"),
            (Qt.GlobalColor.darkRed, "Dark Red"),
            (Qt.GlobalColor.darkGreen, "Dark Green"),
            (Qt.GlobalColor.darkBlue, "Dark Blue"),
            (Qt.GlobalColor.darkCyan, "Dark Cyan"),
            (Qt.GlobalColor.darkMagenta, "Dark Magenta"),
            (Qt.GlobalColor.darkYellow, "Dark Yellow"),
            (QColor(255, 192, 203), "Pink"),
            (QColor(165, 42, 42), "Brown"),
            (QColor(255, 165, 0), "Orange")
        ]
        
        self.setup_ui()
        self.load_default_palette()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(2)
        
        # Add color button
        self.add_btn = self.create_tool_button("Add Color", "SP_DialogOpenButton")
        self.add_btn.clicked.connect(self.add_color)
        
        # Remove color button
        self.remove_btn = self.create_tool_button("Remove Color", "SP_TrashIcon")
        self.remove_btn.clicked.connect(self.remove_color)
        
        # Menu button
        self.menu_btn = self.create_tool_button("Palette Options", "SP_ComputerIcon")
        self.menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Create menu
        self.setup_menu()
        
        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Add to toolbar
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.remove_btn)
        toolbar.addItem(spacer)
        toolbar.addWidget(self.menu_btn)
        
        # Swatches container
        self.swatches_container = QWidget()
        self.swatches_layout = QGridLayout(self.swatches_container)
        self.swatches_layout.setSpacing(self.spacing)
        self.swatches_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.swatches_container)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Add to layout
        layout.addLayout(toolbar)
        layout.addWidget(scroll, 1)
        
        # Update buttons
        self.update_buttons()
    
    def create_tool_button(self, tooltip, icon_name):
        """Create a tool button with the given icon and tooltip."""
        btn = QToolButton()
        btn.setToolTip(tooltip)
        btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, icon_name)
        ))
        btn.setIconSize(QSize(16, 16))
        return btn
    
    def setup_menu(self):
        """Setup the palette menu."""
        menu = QMenu(self)
        
        # Load default palette
        load_default_action = QAction("Load Default Palette", self)
        load_default_action.triggered.connect(self.load_default_palette)
        
        # Save palette
        save_action = QAction("Save Palette...", self)
        save_action.triggered.connect(self.save_palette)
        
        # Load palette
        load_action = QAction("Load Palette...", self)
        load_action.triggered.connect(self.load_palette)
        
        menu.addAction(load_default_action)
        menu.addSeparator()
        menu.addAction(save_action)
        menu.addAction(load_action)
        
        # Set menu
        self.menu_btn.setMenu(menu)
    
    def add_color(self, color=Qt.GlobalColor.white, name=""):
        """Add a color to the palette."""
        # Create swatch
        swatch = ColorSwatch(color, name, self)
        swatch.clicked.connect(self.on_swatch_clicked)
        
        # Add to layout
        row = len(self.swatches) // self.cols
        col = len(self.swatches) % self.cols
        self.swatches_layout.addWidget(swatch, row, col)
        
        # Add to list
        self.swatches.append(swatch)
        
        # Update layout
        self.update_layout()
    
    def remove_color(self):
        """Remove the selected color from the palette."""
        if self.selected_swatch and self.selected_swatch in self.swatches:
            # Remove from layout
            self.swatches_layout.removeWidget(self.selected_swatch)
            self.selected_swatch.deleteLater()
            
            # Remove from list
            self.swatches.remove(self.selected_swatch)
            self.selected_swatch = None
            
            # Update layout
            self.update_layout()
            self.update_buttons()
    
    def on_swatch_clicked(self, color, name):
        """Handle swatch click."""
        # Deselect previous swatch
        if self.selected_swatch:
            self.selected_swatch.set_selected(False)
        
        # Select clicked swatch
        self.selected_swatch = self.sender()
        self.selected_swatch.set_selected(True)
        
        # Emit signal
        self.colorSelected.emit(color, name)
        
        # Update buttons
        self.update_buttons()
    
    def update_layout(self):
        """Update the layout of the swatches."""
        # Clear layout
        while self.swatches_layout.count() > 0:
            item = self.swatches_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add swatches to layout
        for i, swatch in enumerate(self.swatches):
            row = i // self.cols
            col = i % self.cols
            self.swatches_layout.addWidget(swatch, row, col)
    
    def update_buttons(self):
        """Update button states."""
        self.remove_btn.setEnabled(self.selected_swatch is not None)
    
    def load_default_palette(self):
        """Load the default color palette."""
        # Clear existing swatches
        for swatch in self.swatches:
            self.swatches_layout.removeWidget(swatch)
            swatch.deleteLater()
        self.swatches = []
        self.selected_swatch = None
        
        # Add default colors
        for color, name in self.default_colors:
            self.add_color(color, name)
    
    def save_palette(self):
        """Save the current palette to a file."""
        # This would be implemented to save the palette to a file
        pass
    
    def load_palette(self):
        """Load a palette from a file."""
        # This would be implemented to load a palette from a file
        pass
    
    def get_colors(self):
        """Get a list of (color, name) tuples in the palette."""
        return [(swatch.color, swatch.name) for swatch in self.swatches]
    
    def set_colors(self, colors):
        """Set the colors in the palette."""
        # Clear existing swatches
        for swatch in self.swatches:
            self.swatches_layout.removeWidget(swatch)
            swatch.deleteLater()
        self.swatches = []
        self.selected_swatch = None
        
        # Add new colors
        for color, name in colors:
            self.add_color(color, name)
        
        # Update buttons
        self.update_buttons()
