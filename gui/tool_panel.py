"""
Tool panel component for PixelCrafterX.
Handles tool selection and settings.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolButton, QLabel,
                            QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from core.tools.tool_manager import ToolManager

class ToolPanel(QWidget):
    # Signals
    tool_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tool_manager = ToolManager()
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create tool buttons
        self.create_tool_buttons()
        
        # Create tool settings
        self.create_tool_settings()
        
        # Connect signals
        self.connect_signals()
        
    def create_tool_buttons(self):
        """Create tool selection buttons."""
        # Create tool button group
        tool_group = QGroupBox("Tools")
        tool_layout = QVBoxLayout(tool_group)
        
        # Create tool buttons
        tools = [
            ("brush", "Brush", "icons/brush.png"),
            ("eraser", "Eraser", "icons/eraser.png"),
            ("fill", "Fill", "icons/fill.png"),
            ("select", "Select", "icons/select.png"),
            ("move", "Move", "icons/move.png"),
            ("crop", "Crop", "icons/crop.png"),
            ("text", "Text", "icons/text.png"),
            ("shape", "Shape", "icons/shape.png"),
            ("gradient", "Gradient", "icons/gradient.png"),
            ("eyedropper", "Eyedropper", "icons/eyedropper.png")
        ]
        
        self.tool_buttons = {}
        for tool_id, name, icon in tools:
            button = QToolButton()
            button.setIcon(QIcon(icon))
            button.setIconSize(Qt.QSize(32, 32))
            button.setToolTip(name)
            button.setCheckable(True)
            button.setProperty("tool_id", tool_id)
            tool_layout.addWidget(button)
            self.tool_buttons[tool_id] = button
            
        self.layout.addWidget(tool_group)
        
    def create_tool_settings(self):
        """Create tool settings widgets."""
        # Create settings group
        settings_group = QGroupBox("Tool Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Size setting
        size_layout = QVBoxLayout()
        size_label = QLabel("Size:")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(10)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        settings_layout.addLayout(size_layout)
        
        # Opacity setting
        opacity_layout = QVBoxLayout()
        opacity_label = QLabel("Opacity:")
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.1)
        self.opacity_spin.setValue(1.0)
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_spin)
        settings_layout.addLayout(opacity_layout)
        
        # Hardness setting
        hardness_layout = QVBoxLayout()
        hardness_label = QLabel("Hardness:")
        self.hardness_spin = QDoubleSpinBox()
        self.hardness_spin.setRange(0.0, 1.0)
        self.hardness_spin.setSingleStep(0.1)
        self.hardness_spin.setValue(0.8)
        hardness_layout.addWidget(hardness_label)
        hardness_layout.addWidget(self.hardness_spin)
        settings_layout.addLayout(hardness_layout)
        
        # Blend mode setting
        blend_layout = QVBoxLayout()
        blend_label = QLabel("Blend Mode:")
        self.blend_combo = QComboBox()
        self.blend_combo.addItems([
            "Normal", "Multiply", "Screen", "Overlay",
            "Darken", "Lighten", "Color Dodge", "Color Burn",
            "Hard Light", "Soft Light", "Difference", "Exclusion"
        ])
        blend_layout.addWidget(blend_label)
        blend_layout.addWidget(self.blend_combo)
        settings_layout.addLayout(blend_layout)
        
        self.layout.addWidget(settings_group)
        
    def connect_signals(self):
        """Connect signals and slots."""
        # Connect tool buttons
        for button in self.tool_buttons.values():
            button.clicked.connect(self.on_tool_button_clicked)
            
        # Connect settings widgets
        self.size_spin.valueChanged.connect(self.on_size_changed)
        self.opacity_spin.valueChanged.connect(self.on_opacity_changed)
        self.hardness_spin.valueChanged.connect(self.on_hardness_changed)
        self.blend_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        
    def on_tool_button_clicked(self):
        """Handle tool button click."""
        button = self.sender()
        if button.isChecked():
            # Uncheck other buttons
            for other in self.tool_buttons.values():
                if other != button:
                    other.setChecked(False)
                    
            # Emit tool changed signal
            tool_id = button.property("tool_id")
            self.tool_changed.emit(tool_id)
            
    def on_size_changed(self, value: int):
        """Handle size change."""
        if self.tool_manager.active_tool:
            self.tool_manager.active_tool.set_size(value)
            
    def on_opacity_changed(self, value: float):
        """Handle opacity change."""
        if self.tool_manager.active_tool:
            self.tool_manager.active_tool.set_opacity(value)
            
    def on_hardness_changed(self, value: float):
        """Handle hardness change."""
        if self.tool_manager.active_tool:
            self.tool_manager.active_tool.set_hardness(value)
            
    def on_blend_mode_changed(self, mode: str):
        """Handle blend mode change."""
        if self.tool_manager.active_tool:
            self.tool_manager.active_tool.set_blend_mode(mode.lower())
            
    def set_active_tool(self, tool_id: str):
        """Set active tool."""
        if tool_id in self.tool_buttons:
            # Uncheck all buttons
            for button in self.tool_buttons.values():
                button.setChecked(False)
                
            # Check selected button
            self.tool_buttons[tool_id].setChecked(True)
            
            # Update tool settings
            if self.tool_manager.active_tool:
                self.size_spin.setValue(self.tool_manager.active_tool.size)
                self.opacity_spin.setValue(self.tool_manager.active_tool.opacity)
                self.hardness_spin.setValue(self.tool_manager.active_tool.hardness)
                self.blend_combo.setCurrentText(self.tool_manager.active_tool.blend_mode.title()) 