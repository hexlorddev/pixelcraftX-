"""Custom color picker dialog with advanced color selection options."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QSlider, QColorDialog, QWidget, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPixmap, QLinearGradient

class ColorPickerDialog(QDialog):
    """Advanced color picker dialog with RGB/HSV sliders and palette."""
    colorSelected = pyqtSignal(QColor)
    
    def __init__(self, initial_color=Qt.GlobalColor.black, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Color")
        self.setMinimumSize(400, 500)
        
        self.color = QColor(initial_color)
        self.setup_ui()
        self.update_color_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(80)
        self.color_preview.setFrameStyle(QFrame.Shape.Box | QFrame.Shape.Plain)
        
        # Color sliders
        self.slider_r = self.create_slider("Red", 0, 255)
        self.slider_g = self.create_slider("Green", 0, 255)
        self.slider_b = self.create_slider("Blue", 0, 255)
        self.slider_a = self.create_slider("Alpha", 0, 255, 255)
        
        # Color wheel (placeholder)
        self.color_wheel = QLabel("Color Wheel")
        self.color_wheel.setMinimumHeight(200)
        self.color_wheel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        buttons = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_pick = QPushButton("Pick from Screen")
        
        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_pick)
        
        # Add to layout
        layout.addWidget(self.color_preview)
        layout.addWidget(QLabel("RGB:"))
        layout.addLayout(self.slider_r)
        layout.addLayout(self.slider_g)
        layout.addLayout(self.slider_b)
        layout.addLayout(self.slider_a)
        layout.addWidget(self.color_wheel)
        layout.addLayout(buttons)
        
        # Connect signals
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_pick.clicked.connect(self.pick_from_screen)
    
    def create_slider(self, label, min_val, max_val, default=None):
        """Create a labeled slider component."""
        layout = QHBoxLayout()
        lbl = QLabel(f"{label}:")
        lbl.setFixedWidth(60)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default or min_val)
        slider.valueChanged.connect(self.update_color_from_sliders)
        
        value = QLabel(str(default or min_val))
        value.setFixedWidth(30)
        
        # Store references
        slider.value_label = value
        slider.property_name = label.lower()
        
        layout.addWidget(lbl)
        layout.addWidget(slider)
        layout.addWidget(value)
        
        return layout
    
    def update_color_ui(self):
        """Update UI to reflect current color."""
        # Update preview
        pixmap = QPixmap(100, 80)
        pixmap.fill(self.color)
        self.color_preview.setPixmap(pixmap)
        
        # Update sliders without triggering events
        for slider in [self.slider_r, self.slider_g, self.slider_b, self.slider_a]:
            slider.itemAt(1).widget().blockSignals(True)
        
        self.slider_r.itemAt(1).widget().setValue(self.color.red())
        self.slider_g.itemAt(1).widget().setValue(self.color.green())
        self.slider_b.itemAt(1).widget().setValue(self.color.blue())
        self.slider_a.itemAt(1).widget().setValue(self.color.alpha())
        
        for slider in [self.slider_r, self.slider_g, self.slider_b, self.slider_a]:
            slider.itemAt(1).widget().blockSignals(False)
    
    def update_color_from_sliders(self):
        """Update color based on slider values."""
        r = self.slider_r.itemAt(1).widget().value()
        g = self.slider_g.itemAt(1).widget().value()
        b = self.slider_b.itemAt(1).widget().value()
        a = self.slider_a.itemAt(1).widget().value()
        
        self.color = QColor(r, g, b, a)
        self.update_color_ui()
    
    def pick_from_screen(self):
        """Open system color picker to select color from screen."""
        color = QColorDialog.getColor(self.color, self, "Pick Color from Screen")
        if color.isValid():
            self.color = color
            self.update_color_ui()
    
    def accept(self):
        """Handle dialog accept."""
        self.colorSelected.emit(self.color)
        super().accept()

    def get_color(self):
        """Get the selected color."""
        return self.color

    @staticmethod
    def get_color_dialog(initial_color=Qt.GlobalColor.black, parent=None):
        """Static method to show dialog and return selected color."""
        dialog = ColorPickerDialog(initial_color, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_color()
        return None
