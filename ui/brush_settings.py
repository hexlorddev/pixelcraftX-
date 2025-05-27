"""Custom brush settings widget for configuring brush properties."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSlider, QComboBox, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPen, QBrush

class BrushSettings(QGroupBox):
    """Brush settings widget with size, opacity, and style controls."""
    
    settingsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Brush Settings", parent)
        self.setup_ui()
        
        # Default values
        self.brush_size = 10
        self.brush_opacity = 100
        self.brush_hardness = 100
        self.brush_flow = 100
        self.brush_spacing = 25
        self.brush_angle = 0
        self.brush_roundness = 100
        self.brush_texture = "None"
        self.brush_blend_mode = "Normal"
        self.brush_smoothing = True
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Brush preview
        self.preview = QLabel()
        self.preview.setMinimumHeight(80)
        self.preview.setFrameStyle(1)  # Box
        self.update_preview()
        
        # Brush size
        self.slider_size = self.create_slider("Size:", 1, 500, 10, "px")
        self.slider_opacity = self.create_slider("Opacity:", 1, 100, 100, "%")
        self.slider_hardness = self.create_slider("Hardness:", 1, 100, 100, "%")
        self.slider_flow = self.create_slider("Flow:", 1, 100, 100, "%")
        self.slider_spacing = self.create_slider("Spacing:", 1, 200, 25, "%")
        
        # Brush angle and roundness
        angle_layout = QHBoxLayout()
        self.slider_angle = self.create_slider("Angle:", 0, 359, 0, "°")
        self.slider_roundness = self.create_slider("Roundness:", 1, 100, 100, "%")
        angle_layout.addLayout(self.slider_angle)
        angle_layout.addLayout(self.slider_roundness)
        
        # Brush texture
        self.combo_texture = QComboBox()
        self.combo_texture.addItems(["None", "Grain", "Noise", "Paper", "Canvas", "Custom"])
        self.combo_texture.currentTextChanged.connect(self.on_settings_changed)
        
        # Brush blend mode
        self.combo_blend_mode = QComboBox()
        self.combo_blend_mode.addItems([
            "Normal", "Multiply", "Screen", "Overlay", "Darken", 
            "Lighten", "Color Dodge", "Color Burn", "Hard Light", 
            "Soft Light", "Difference", "Exclusion"
        ])
        self.combo_blend_mode.currentTextChanged.connect(self.on_settings_changed)
        
        # Smoothing checkbox
        self.check_smoothing = QCheckBox("Smoothing")
        self.check_smoothing.setChecked(True)
        self.check_smoothing.stateChanged.connect(self.on_settings_changed)
        
        # Add to layout
        layout.addWidget(self.preview)
        layout.addLayout(self.slider_size)
        layout.addLayout(self.slider_opacity)
        layout.addLayout(self.slider_hardness)
        layout.addLayout(self.slider_flow)
        layout.addLayout(self.slider_spacing)
        layout.addLayout(angle_layout)
        layout.addWidget(QLabel("Texture:"))
        layout.addWidget(self.combo_texture)
        layout.addWidget(QLabel("Blend Mode:"))
        layout.addWidget(self.combo_blend_mode)
        layout.addWidget(self.check_smoothing)
        
        # Connect slider signals
        for slider in [
            self.slider_size, self.slider_opacity, self.slider_hardness,
            self.slider_flow, self.slider_spacing, self.slider_angle,
            self.slider_roundness
        ]:
            slider.itemAt(1).widget().valueChanged.connect(self.on_settings_changed)
    
    def create_slider(self, label, min_val, max_val, default, suffix=""):
        """Create a labeled slider with value display."""
        layout = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(80)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        
        value = QLabel(f"{default}{suffix}")
        value.setFixedWidth(50)
        
        # Store references
        slider.value_label = value
        slider.suffix = suffix
        
        slider.valueChanged.connect(
            lambda v, w=value, s=suffix: w.setText(f"{v}{s}")
        )
        
        layout.addWidget(lbl)
        layout.addWidget(slider)
        layout.addWidget(value)
        
        return layout
    
    def update_preview(self):
        """Update the brush preview."""
        size = 120
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw checkerboard background
        cell_size = 10
        for y in range(0, size, cell_size):
            for x in range(0, size, cell_size):
                if (x // cell_size + y // cell_size) % 2 == 0:
                    painter.fillRect(x, y, cell_size, cell_size, QColor(220, 220, 220))
        
        # Draw brush preview
        brush_size = min(self.brush_size, 100)  # Cap size for preview
        x, y = size // 2, size // 2
        
        # Draw brush stroke
        pen = QPen(QColor(0, 0, 0, 200), 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.drawEllipse(x - brush_size//2, y - brush_size//2, brush_size, brush_size)
        
        painter.end()
        
        self.preview.setPixmap(pixmap)
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Update properties
        self.brush_size = self.slider_size.itemAt(1).widget().value()
        self.brush_opacity = self.slider_opacity.itemAt(1).widget().value()
        self.brush_hardness = self.slider_hardness.itemAt(1).widget().value()
        self.brush_flow = self.slider_flow.itemAt(1).widget().value()
        self.brush_spacing = self.slider_spacing.itemAt(1).widget().value()
        self.brush_angle = self.slider_angle.itemAt(1).widget().value()
        self.brush_roundness = self.slider_roundness.itemAt(1).widget().value()
        self.brush_texture = self.combo_texture.currentText()
        self.brush_blend_mode = self.combo_blend_mode.currentText()
        self.brush_smoothing = self.check_smoothing.isChecked()
        
        # Update preview
        self.update_preview()
        
        # Emit changed signal
        self.settingsChanged.emit()
    
    def get_brush_settings(self):
        """Get current brush settings as a dictionary."""
        return {
            'size': self.brush_size,
            'opacity': self.brush_opacity,
            'hardness': self.brush_hardness,
            'flow': self.brush_flow,
            'spacing': self.brush_spacing,
            'angle': self.brush_angle,
            'roundness': self.brush_roundness,
            'texture': self.brush_texture,
            'blend_mode': self.brush_blend_mode,
            'smoothing': self.brush_smoothing
        }
    
    def set_brush_settings(self, settings):
        """Set brush settings from a dictionary."""
        if 'size' in settings:
            self.slider_size.itemAt(1).widget().setValue(settings['size'])
        if 'opacity' in settings:
            self.slider_opacity.itemAt(1).widget().setValue(settings['opacity'])
        if 'hardness' in settings:
            self.slider_hardness.itemAt(1).widget().setValue(settings['hardness'])
        if 'flow' in settings:
            self.slider_flow.itemAt(1).widget().setValue(settings['flow'])
        if 'spacing' in settings:
            self.slider_spacing.itemAt(1).widget().setValue(settings['spacing'])
        if 'angle' in settings:
            self.slider_angle.itemAt(1).widget().setValue(settings['angle'])
        if 'roundness' in settings:
            self.slider_roundness.itemAt(1).widget().setValue(settings['roundness'])
        if 'texture' in settings:
            self.combo_texture.setCurrentText(settings['texture'])
        if 'blend_mode' in settings:
            self.combo_blend_mode.setCurrentText(settings['blend_mode'])
        if 'smoothing' in settings:
            self.check_smoothing.setChecked(settings['smoothing'])
        
        self.update_preview()
