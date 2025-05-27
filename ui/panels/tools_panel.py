from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QButtonGroup,
    QLabel, QSpinBox, QColorDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor

class ToolsPanel(QWidget):
    tool_changed = pyqtSignal(str)  # Signal emitted when tool is changed
    color_changed = pyqtSignal(QColor)  # Signal emitted when color is changed
    size_changed = pyqtSignal(int)  # Signal emitted when tool size is changed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tools panel UI."""
        layout = QVBoxLayout(self)
        
        # Tool buttons
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        # Selection tool
        self.select_tool = QToolButton()
        self.select_tool.setCheckable(True)
        self.select_tool.setIcon(QIcon("assets/icons/select.png"))
        self.select_tool.setToolTip("Selection Tool")
        self.tool_group.addButton(self.select_tool)
        layout.addWidget(self.select_tool)
        
        # Brush tool
        self.brush_tool = QToolButton()
        self.brush_tool.setCheckable(True)
        self.brush_tool.setIcon(QIcon("assets/icons/brush.png"))
        self.brush_tool.setToolTip("Brush Tool")
        self.tool_group.addButton(self.brush_tool)
        layout.addWidget(self.brush_tool)
        
        # Eraser tool
        self.eraser_tool = QToolButton()
        self.eraser_tool.setCheckable(True)
        self.eraser_tool.setIcon(QIcon("assets/icons/eraser.png"))
        self.eraser_tool.setToolTip("Eraser Tool")
        self.tool_group.addButton(self.eraser_tool)
        layout.addWidget(self.eraser_tool)
        
        # Color picker
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_btn = QToolButton()
        self.color_btn.setStyleSheet("background-color: black;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)
        
        # Size control
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(10)
        self.size_spin.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)
        
        # Connect tool group signals
        self.tool_group.buttonClicked.connect(self.on_tool_changed)
        
    def choose_color(self):
        """Open color dialog and update color button."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.color_changed.emit(color)
            
    def on_tool_changed(self, button):
        """Handle tool selection changes."""
        if button == self.select_tool:
            self.tool_changed.emit("select")
        elif button == self.brush_tool:
            self.tool_changed.emit("brush")
        elif button == self.eraser_tool:
            self.tool_changed.emit("eraser")
            
    def on_size_changed(self, value):
        """Handle tool size changes."""
        self.size_changed.emit(value) 