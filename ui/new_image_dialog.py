"""Dialog for creating a new image with custom dimensions and settings."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QSpinBox,
                           QGroupBox, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QDoubleValidator

class NewImageDialog(QDialog):
    """Dialog for creating a new image with custom settings."""
    
    # Signal emitted when settings are accepted
    # Parameters: width, height, resolution, color_mode, background
    settingsAccepted = pyqtSignal(int, int, float, str, str)
    
    # Standard sizes (width, height, label)
    STANDARD_SIZES = [
        (1920, 1080, "HD (1920x1080)"),
        (2560, 1440, "QHD (2560x1440)"),
        (3840, 2160, "4K UHD (3840x2160)"),
        (5120, 2880, "5K (5120x2880)"),
        (7680, 4320, "8K UHD (7680x4320)"),
        (1080, 1080, "Instagram Post (1080x1080)"),
        (1080, 1920, "Instagram Story (1080x1920)"),
        (150, 150, "Favicon (150x150)"),
        (1200, 630, "Facebook Post (1200x630)"),
        (1200, 1200, "Pinterest (1200x1200)"),
        (1024, 512, "Twitter Header (1024x512)"),
        (800, 600, "SVGA (800x600)"),
        (1024, 768, "XGA (1024x768)"),
        (1280, 1024, "SXGA (1280x1024)"),
        (1440, 900, "WXGA+ (1440x900)"),
        (1680, 1050, "WSXGA+ (1680x1050)"),
        (1920, 1200, "WUXGA (1920x1200)"),
        (2560, 1600, "WQXGA (2560x1600)"),
        (3200, 2048, "WQXGA+ (3200x2048)"),
        (3840, 2400, "WQUXGA (3840x2400)")
    ]
    
    # Color modes
    COLOR_MODES = [
        ("RGB", "RGB - 8 bits/channel"),
        ("RGBA", "RGB with Alpha - 8 bits/channel"),
        ("RGB_16", "RGB - 16 bits/channel"),
        ("Grayscale", "Grayscale - 8 bits"),
        ("Grayscale_16", "Grayscale - 16 bits"),
        ("CMYK", "CMYK - 8 bits/channel")
    ]
    
    # Background options
    BACKGROUND_OPTIONS = [
        ("white", "White"),
        ("black", "Black"),
        ("transparent", "Transparent"),
        ("custom", "Custom...")
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Image")
        self.setMinimumSize(400, 500)
        
        # Default values
        self.width = 1920
        self.height = 1080
        self.resolution = 72.0
        self.color_mode = "RGB"
        self.background = "white"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Size presets
        preset_group = QGroupBox("Preset Sizes")
        preset_layout = QVBoxLayout()
        
        self.preset_combo = QComboBox()
        for w, h, label in self.STANDARD_SIZES:
            self.preset_combo.addItem(label, (w, h))
        
        # Set default to HD (index 0)
        self.preset_combo.setCurrentIndex(0)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        
        preset_layout.addWidget(self.preset_combo)
        preset_group.setLayout(preset_layout)
        
        # Custom size
        size_group = QGroupBox("Custom Size")
        size_layout = QFormLayout()
        
        # Width
        self.width_edit = QSpinBox()
        self.width_edit.setRange(1, 30000)
        self.width_edit.setValue(self.width)
        self.width_edit.valueChanged.connect(self.on_size_changed)
        
        # Height
        self.height_edit = QSpinBox()
        self.height_edit.setRange(1, 30000)
        self.height_edit.setValue(self.height)
        self.height_edit.valueChanged.connect(self.on_size_changed)
        
        # Resolution
        self.resolution_edit = QLineEdit(str(self.resolution))
        self.resolution_edit.setValidator(QDoubleValidator(1.0, 1200.0, 1, self))
        self.resolution_edit.textEdited.connect(self.on_resolution_changed)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["pixels/inch", "pixels/cm"])
        self.unit_combo.currentTextChanged.connect(self.on_unit_changed)
        
        # Add to layout
        size_layout.addRow("Width:", self.width_edit)
        size_layout.addRow("Height:", self.height_edit)
        size_layout.addRow("Resolution:", self.resolution_edit)
        size_layout.addRow("Unit:", self.unit_combo)
        
        # Lock aspect ratio
        self.lock_aspect = QCheckBox("Lock Aspect Ratio")
        size_layout.addRow(self.lock_aspect)
        
        size_group.setLayout(size_layout)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout()
        
        # Color mode
        self.color_mode_combo = QComboBox()
        for mode, label in self.COLOR_MODES:
            self.color_mode_combo.addItem(label, mode)
        self.color_mode_combo.currentIndexChanged.connect(
            lambda i: setattr(self, 'color_mode', self.color_mode_combo.currentData())
        )
        
        # Background
        self.background_combo = QComboBox()
        for value, label in self.BACKGROUND_OPTIONS:
            self.background_combo.addItem(label, value)
        self.background_combo.currentIndexChanged.connect(
            lambda i: setattr(self, 'background', self.background_combo.currentData())
        )
        
        # Add to layout
        advanced_layout.addRow("Color Mode:", self.color_mode_combo)
        advanced_layout.addRow("Background:", self.background_combo)
        advanced_group.setLayout(advanced_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add all to main layout
        layout.addWidget(preset_group)
        layout.addWidget(size_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        layout.addWidget(button_box)
        
        # Update initial values
        self.on_preset_changed(0)
    
    def on_preset_changed(self, index):
        """Handle preset selection change."""
        width, height = self.preset_combo.currentData()
        self.width_edit.setValue(width)
        self.height_edit.setValue(height)
    
    def on_size_changed(self):
        """Handle size changes."""
        self.width = self.width_edit.value()
        self.height = self.height_edit.value()
        
        # Update preset combo if needed
        for i in range(self.preset_combo.count()):
            w, h = self.preset_combo.itemData(i)
            if w == self.width and h == self.height:
                self.preset_combo.setCurrentIndex(i)
                return
        
        # If no match, set to custom
        self.preset_combo.setCurrentText("Custom")
    
    def on_resolution_changed(self, text):
        """Handle resolution changes."""
        try:
            self.resolution = float(text)
        except ValueError:
            pass
    
    def on_unit_changed(self, unit):
        """Handle unit changes (pixels/inch to pixels/cm and vice versa)."""
        if unit == "pixels/cm" and "inch" in self.unit_combo.currentText():
            # Convert from inches to cm
            self.resolution *= 2.54
        elif unit == "pixels/inch" and "cm" in self.unit_combo.currentText():
            # Convert from cm to inches
            self.resolution /= 2.54
        
        self.resolution_edit.setText(f"{self.resolution:.1f}")
    
    def accept(self):
        """Handle dialog accept."""
        # Validate inputs
        try:
            self.width = max(1, min(30000, self.width_edit.value()))
            self.height = max(1, min(30000, self.height_edit.value()))
            self.resolution = max(1.0, min(1200.0, float(self.resolution_edit.text())))
            
            # Emit the signal with the settings
            self.settingsAccepted.emit(
                self.width,
                self.height,
                self.resolution,
                self.color_mode,
                self.background
            )
            
            super().accept()
            
        except ValueError:
            # Invalid input, don't close
            pass
    
    @staticmethod
    def get_settings(parent=None):
        """Static method to show dialog and return settings."""
        dialog = NewImageDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return (
                dialog.width,
                dialog.height,
                dialog.resolution,
                dialog.color_mode,
                dialog.background
            )
        return None
