"""Layer properties panel for managing layer attributes."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSlider, QCheckBox, QComboBox, QPushButton,
                           QLineEdit, QToolButton, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter, QIcon

class LayerProperties(QWidget):
    """Panel for displaying and editing layer properties."""
    
    # Signals
    visibilityToggled = pyqtSignal(bool)
    opacityChanged = pyqtSignal(int)
    blendModeChanged = pyqtSignal(str)
    layerRenamed = pyqtSignal(str)
    layerLocked = pyqtSignal(bool)
    layerMoved = pyqtSignal(int)
    layerDuplicated = pyqtSignal()
    layerDeleted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layer_name = "Layer 1"
        self.layer_visible = True
        self.layer_opacity = 100
        self.layer_blend_mode = "Normal"
        self.layer_locked = False
        self.layer_index = 0
        self.total_layers = 1
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Layer name and visibility
        name_layout = QHBoxLayout()
        
        self.visibility_btn = QToolButton()
        self.visibility_btn.setCheckable(True)
        self.visibility_btn.setChecked(True)
        self.visibility_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_DialogYesButton")
        ))
        self.visibility_btn.setToolTip("Toggle Visibility")
        self.visibility_btn.clicked.connect(self.toggle_visibility)
        
        self.name_edit = QLineEdit(self.layer_name)
        self.name_edit.setPlaceholderText("Layer Name")
        self.name_edit.editingFinished.connect(self.rename_layer)
        
        name_layout.addWidget(self.visibility_btn)
        name_layout.addWidget(self.name_edit)
        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.layer_opacity)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        
        self.opacity_label = QLabel(f"{self.layer_opacity}%")
        self.opacity_label.setFixedWidth(40)
        
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        # Blend mode
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("Blend Mode:"))
        
        self.blend_combo = QComboBox()
        self.blend_combo.addItems([
            "Normal", "Multiply", "Screen", "Overlay", "Darken", 
            "Lighten", "Color Dodge", "Color Burn", "Hard Light", 
            "Soft Light", "Difference", "Exclusion"
        ])
        self.blend_combo.setCurrentText(self.layer_blend_mode)
        self.blend_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        
        blend_layout.addWidget(self.blend_combo)
        
        # Layer actions
        actions_layout = QHBoxLayout()
        
        self.lock_btn = QToolButton()
        self.lock_btn.setCheckable(True)
        self.lock_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_DialogNoButton")
        ))
        self.lock_btn.setToolTip("Lock/Unlock Layer")
        self.lock_btn.clicked.connect(self.toggle_lock)
        
        self.duplicate_btn = QToolButton()
        self.duplicate_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_FileDialogNewFolder")
        ))
        self.duplicate_btn.setToolTip("Duplicate Layer")
        self.duplicate_btn.clicked.connect(self.duplicate_layer)
        
        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_TrashIcon")
        ))
        self.delete_btn.setToolTip("Delete Layer")
        self.delete_btn.clicked.connect(self.delete_layer)
        
        # Navigation buttons
        self.move_up_btn = QToolButton()
        self.move_up_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_ArrowUp")
        ))
        self.move_up_btn.setToolTip("Move Layer Up")
        self.move_up_btn.clicked.connect(lambda: self.move_layer(-1))
        
        self.move_down_btn = QToolButton()
        self.move_down_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_ArrowDown")
        ))
        self.move_down_btn.setToolTip("Move Layer Down")
        self.move_down_btn.clicked.connect(lambda: self.move_layer(1))
        
        # Add buttons to layout
        actions_layout.addWidget(self.lock_btn)
        actions_layout.addWidget(self.duplicate_btn)
        actions_layout.addWidget(self.delete_btn)
        actions_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        actions_layout.addWidget(self.move_up_btn)
        actions_layout.addWidget(self.move_down_btn)
        
        # Add all to main layout
        layout.addLayout(name_layout)
        layout.addLayout(opacity_layout)
        layout.addLayout(blend_layout)
        layout.addLayout(actions_layout)
        
        # Update button states
        self.update_button_states()
    
    def update_button_states(self):
        """Update the enabled/disabled state of navigation buttons."""
        self.move_up_btn.setEnabled(self.layer_index > 0)
        self.move_down_btn.setEnabled(self.layer_index < self.total_layers - 1)
        self.delete_btn.setEnabled(self.total_layers > 1)
    
    def toggle_visibility(self, checked):
        """Toggle layer visibility."""
        self.layer_visible = checked
        self.visibility_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 
                   "SP_DialogYesButton" if checked else "SP_DialogNoButton")
        ))
        self.visibilityToggled.emit(checked)
    
    def on_opacity_changed(self, value):
        """Handle opacity slider change."""
        self.layer_opacity = value
        self.opacity_label.setText(f"{value}%")
        self.opacityChanged.emit(value)
    
    def on_blend_mode_changed(self, mode):
        """Handle blend mode change."""
        self.layer_blend_mode = mode
        self.blendModeChanged.emit(mode)
    
    def rename_layer(self):
        """Handle layer renaming."""
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.layer_name:
            self.layer_name = new_name
            self.layerRenamed.emit(new_name)
    
    def toggle_lock(self, locked):
        """Toggle layer lock state."""
        self.layer_locked = locked
        self.lock_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 
                   "SP_DialogYesButton" if locked else "SP_DialogNoButton")
        ))
        self.layerLocked.emit(locked)
    
    def move_layer(self, direction):
        """Move layer up or down."""
        new_index = self.layer_index + direction
        if 0 <= new_index < self.total_layers:
            self.layerMoved.emit(direction)
    
    def duplicate_layer(self):
        """Duplicate the current layer."""
        self.layerDuplicated.emit()
    
    def delete_layer(self):
        """Delete the current layer."""
        self.layerDeleted.emit()
    
    def set_layer_info(self, name, visible, opacity, blend_mode, locked, index, total):
        """Set all layer properties at once."""
        self.layer_name = name
        self.layer_visible = visible
        self.layer_opacity = opacity
        self.layer_blend_mode = blend_mode
        self.layer_locked = locked
        self.layer_index = index
        self.total_layers = total
        
        # Update UI
        self.name_edit.setText(name)
        self.visibility_btn.setChecked(visible)
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f"{opacity}%")
        self.blend_combo.setCurrentText(blend_mode)
        self.lock_btn.setChecked(locked)
        
        # Update button states
        self.update_button_states()
        
        # Update lock button icon
        self.lock_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 
                   "SP_DialogYesButton" if locked else "SP_DialogNoButton")
        ))
        
        # Update visibility button icon
        self.visibility_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 
                   "SP_DialogYesButton" if visible else "SP_DialogNoButton")
        ))
