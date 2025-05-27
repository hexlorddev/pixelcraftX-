from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton,
    QHBoxLayout, QLabel, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal

class LayersPanel(QWidget):
    layer_selected = pyqtSignal(int)  # Signal emitted when a layer is selected
    layer_visibility_changed = pyqtSignal(int, bool)  # Signal for layer visibility toggle
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the layers panel UI."""
        layout = QVBoxLayout(self)
        
        # Layers list
        self.layers_list = QListWidget()
        self.layers_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.layers_list.itemSelectionChanged.connect(self.on_layer_selected)
        layout.addWidget(self.layers_list)
        
        # Layer controls
        controls_layout = QHBoxLayout()
        
        # New layer button
        self.new_layer_btn = QPushButton("New Layer")
        self.new_layer_btn.clicked.connect(self.create_new_layer)
        controls_layout.addWidget(self.new_layer_btn)
        
        # Delete layer button
        self.delete_layer_btn = QPushButton("Delete")
        self.delete_layer_btn.clicked.connect(self.delete_selected_layer)
        controls_layout.addWidget(self.delete_layer_btn)
        
        layout.addLayout(controls_layout)
        
        # Layer opacity control
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        layout.addLayout(opacity_layout)
        
    def create_new_layer(self):
        """Create a new layer."""
        layer_name = f"Layer {self.layers_list.count() + 1}"
        self.layers_list.addItem(layer_name)
        
    def delete_selected_layer(self):
        """Delete the selected layer."""
        current_row = self.layers_list.currentRow()
        if current_row >= 0:
            self.layers_list.takeItem(current_row)
            
    def on_layer_selected(self):
        """Handle layer selection."""
        current_row = self.layers_list.currentRow()
        if current_row >= 0:
            self.layer_selected.emit(current_row)
            
    def on_opacity_changed(self, value):
        """Handle opacity changes."""
        current_row = self.layers_list.currentRow()
        if current_row >= 0:
            opacity = value / 100.0
            # Emit signal or update layer opacity 