"""
Color panel component for PixelCrafterX.
Handles color selection and management.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QSpinBox, QColorDialog, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush

class ColorPanel(QWidget):
    # Signals
    color_changed = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create color picker
        self.create_color_picker()
        
        # Create color values
        self.create_color_values()
        
        # Create color swatches
        self.create_color_swatches()
        
        # Initialize colors
        self.foreground_color = QColor(0, 0, 0)
        self.background_color = QColor(255, 255, 255)
        
        # Connect signals
        self.connect_signals()
        
    def create_color_picker(self):
        """Create color picker buttons."""
        # Create color picker group
        picker_group = QGroupBox("Color Picker")
        picker_layout = QHBoxLayout(picker_group)
        
        # Foreground color button
        self.fg_color_btn = QPushButton()
        self.fg_color_btn.setFixedSize(32, 32)
        self.fg_color_btn.setToolTip("Foreground Color")
        picker_layout.addWidget(self.fg_color_btn)
        
        # Background color button
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(32, 32)
        self.bg_color_btn.setToolTip("Background Color")
        picker_layout.addWidget(self.bg_color_btn)
        
        # Swap colors button
        self.swap_colors_btn = QPushButton()
        self.swap_colors_btn.setIcon(QIcon("icons/swap_colors.png"))
        self.swap_colors_btn.setToolTip("Swap Colors")
        picker_layout.addWidget(self.swap_colors_btn)
        
        # Reset colors button
        self.reset_colors_btn = QPushButton()
        self.reset_colors_btn.setIcon(QIcon("icons/reset_colors.png"))
        self.reset_colors_btn.setToolTip("Reset Colors")
        picker_layout.addWidget(self.reset_colors_btn)
        
        self.layout.addWidget(picker_group)
        
    def create_color_values(self):
        """Create color value inputs."""
        # Create color values group
        values_group = QGroupBox("Color Values")
        values_layout = QVBoxLayout(values_group)
        
        # RGB values
        rgb_layout = QHBoxLayout()
        
        # Red
        red_layout = QVBoxLayout()
        red_label = QLabel("R:")
        self.red_spin = QSpinBox()
        self.red_spin.setRange(0, 255)
        red_layout.addWidget(red_label)
        red_layout.addWidget(self.red_spin)
        rgb_layout.addLayout(red_layout)
        
        # Green
        green_layout = QVBoxLayout()
        green_label = QLabel("G:")
        self.green_spin = QSpinBox()
        self.green_spin.setRange(0, 255)
        green_layout.addWidget(green_label)
        green_layout.addWidget(self.green_spin)
        rgb_layout.addLayout(green_layout)
        
        # Blue
        blue_layout = QVBoxLayout()
        blue_label = QLabel("B:")
        self.blue_spin = QSpinBox()
        self.blue_spin.setRange(0, 255)
        blue_layout.addWidget(blue_label)
        blue_layout.addWidget(self.blue_spin)
        rgb_layout.addLayout(blue_layout)
        
        values_layout.addLayout(rgb_layout)
        
        # HSV values
        hsv_layout = QHBoxLayout()
        
        # Hue
        hue_layout = QVBoxLayout()
        hue_label = QLabel("H:")
        self.hue_spin = QSpinBox()
        self.hue_spin.setRange(0, 359)
        hue_layout.addWidget(hue_label)
        hue_layout.addWidget(self.hue_spin)
        hsv_layout.addLayout(hue_layout)
        
        # Saturation
        sat_layout = QVBoxLayout()
        sat_label = QLabel("S:")
        self.sat_spin = QSpinBox()
        self.sat_spin.setRange(0, 100)
        sat_layout.addWidget(sat_label)
        sat_layout.addWidget(self.sat_spin)
        hsv_layout.addLayout(sat_layout)
        
        # Value
        val_layout = QVBoxLayout()
        val_label = QLabel("V:")
        self.val_spin = QSpinBox()
        self.val_spin.setRange(0, 100)
        val_layout.addWidget(val_label)
        val_layout.addWidget(self.val_spin)
        hsv_layout.addLayout(val_layout)
        
        values_layout.addLayout(hsv_layout)
        
        # Alpha value
        alpha_layout = QHBoxLayout()
        alpha_label = QLabel("A:")
        self.alpha_spin = QSpinBox()
        self.alpha_spin.setRange(0, 255)
        alpha_layout.addWidget(alpha_label)
        alpha_layout.addWidget(self.alpha_spin)
        values_layout.addLayout(alpha_layout)
        
        self.layout.addWidget(values_group)
        
    def create_color_swatches(self):
        """Create color swatches."""
        # Create swatches group
        swatches_group = QGroupBox("Color Swatches")
        swatches_layout = QVBoxLayout(swatches_group)
        
        # Create swatch buttons
        self.swatch_buttons = []
        for i in range(8):
            button = QPushButton()
            button.setFixedSize(32, 32)
            button.setToolTip(f"Swatch {i+1}")
            self.swatch_buttons.append(button)
            swatches_layout.addWidget(button)
            
        self.layout.addWidget(swatches_group)
        
    def connect_signals(self):
        """Connect signals and slots."""
        # Connect color picker buttons
        self.fg_color_btn.clicked.connect(self.on_fg_color_clicked)
        self.bg_color_btn.clicked.connect(self.on_bg_color_clicked)
        self.swap_colors_btn.clicked.connect(self.on_swap_colors)
        self.reset_colors_btn.clicked.connect(self.on_reset_colors)
        
        # Connect color value inputs
        self.red_spin.valueChanged.connect(self.on_rgb_changed)
        self.green_spin.valueChanged.connect(self.on_rgb_changed)
        self.blue_spin.valueChanged.connect(self.on_rgb_changed)
        self.hue_spin.valueChanged.connect(self.on_hsv_changed)
        self.sat_spin.valueChanged.connect(self.on_hsv_changed)
        self.val_spin.valueChanged.connect(self.on_hsv_changed)
        self.alpha_spin.valueChanged.connect(self.on_alpha_changed)
        
        # Connect swatch buttons
        for button in self.swatch_buttons:
            button.clicked.connect(self.on_swatch_clicked)
            
    def on_fg_color_clicked(self):
        """Handle foreground color button click."""
        color = QColorDialog.getColor(self.foreground_color, self)
        if color.isValid():
            self.set_foreground_color(color)
            
    def on_bg_color_clicked(self):
        """Handle background color button click."""
        color = QColorDialog.getColor(self.background_color, self)
        if color.isValid():
            self.set_background_color(color)
            
    def on_swap_colors(self):
        """Swap foreground and background colors."""
        self.foreground_color, self.background_color = self.background_color, self.foreground_color
        self.update_color_buttons()
        self.update_color_values()
        self.color_changed.emit(self.foreground_color)
        
    def on_reset_colors(self):
        """Reset colors to default."""
        self.set_foreground_color(QColor(0, 0, 0))
        self.set_background_color(QColor(255, 255, 255))
        
    def on_rgb_changed(self):
        """Handle RGB value changes."""
        color = QColor(
            self.red_spin.value(),
            self.green_spin.value(),
            self.blue_spin.value(),
            self.alpha_spin.value()
        )
        self.set_foreground_color(color)
        
    def on_hsv_changed(self):
        """Handle HSV value changes."""
        color = QColor()
        color.setHsv(
            self.hue_spin.value(),
            int(self.sat_spin.value() * 2.55),
            int(self.val_spin.value() * 2.55),
            self.alpha_spin.value()
        )
        self.set_foreground_color(color)
        
    def on_alpha_changed(self):
        """Handle alpha value change."""
        self.foreground_color.setAlpha(self.alpha_spin.value())
        self.update_color_buttons()
        self.color_changed.emit(self.foreground_color)
        
    def on_swatch_clicked(self):
        """Handle swatch button click."""
        button = self.sender()
        if button.palette().button().color() != Qt.GlobalColor.transparent:
            self.set_foreground_color(button.palette().button().color())
            
    def set_foreground_color(self, color: QColor):
        """Set foreground color."""
        self.foreground_color = color
        self.update_color_buttons()
        self.update_color_values()
        self.color_changed.emit(color)
        
    def set_background_color(self, color: QColor):
        """Set background color."""
        self.background_color = color
        self.update_color_buttons()
        
    def update_color_buttons(self):
        """Update color button appearances."""
        # Update foreground color button
        palette = self.fg_color_btn.palette()
        palette.setColor(QPalette.ColorRole.Button, self.foreground_color)
        self.fg_color_btn.setPalette(palette)
        
        # Update background color button
        palette = self.bg_color_btn.palette()
        palette.setColor(QPalette.ColorRole.Button, self.background_color)
        self.bg_color_btn.setPalette(palette)
        
    def update_color_values(self):
        """Update color value inputs."""
        # Update RGB values
        self.red_spin.setValue(self.foreground_color.red())
        self.green_spin.setValue(self.foreground_color.green())
        self.blue_spin.setValue(self.foreground_color.blue())
        
        # Update HSV values
        h, s, v, _ = self.foreground_color.getHsv()
        self.hue_spin.setValue(h)
        self.sat_spin.setValue(int(s / 2.55))
        self.val_spin.setValue(int(v / 2.55))
        
        # Update alpha value
        self.alpha_spin.setValue(self.foreground_color.alpha()) 