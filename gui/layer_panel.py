"""
Layer panel component for PixelCrafterX.
Handles layer management and settings.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QListWidget, QListWidgetItem, QLabel, QSlider,
                            QComboBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from core.layers.layer_manager import LayerManager

class LayerPanel(QWidget):
    # Signals
    layer_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layer_manager = LayerManager()
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create layer list
        self.create_layer_list()
        
        # Create layer controls
        self.create_layer_controls()
        
        # Connect signals
        self.connect_signals()
        
    def create_layer_list(self):
        """Create layer list widget."""
        self.layer_list = QListWidget()
        self.layer_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.layer_list.customContextMenuRequested.connect(self.show_layer_menu)
        self.layout.addWidget(self.layer_list)
        
    def create_layer_controls(self):
        """Create layer control buttons."""
        # Create button layout
        button_layout = QHBoxLayout()
        
        # New layer button
        self.new_layer_btn = QPushButton()
        self.new_layer_btn.setIcon(QIcon("icons/new_layer.png"))
        self.new_layer_btn.setToolTip("New Layer")
        button_layout.addWidget(self.new_layer_btn)
        
        # Delete layer button
        self.delete_layer_btn = QPushButton()
        self.delete_layer_btn.setIcon(QIcon("icons/delete_layer.png"))
        self.delete_layer_btn.setToolTip("Delete Layer")
        button_layout.addWidget(self.delete_layer_btn)
        
        # Duplicate layer button
        self.duplicate_layer_btn = QPushButton()
        self.duplicate_layer_btn.setIcon(QIcon("icons/duplicate_layer.png"))
        self.duplicate_layer_btn.setToolTip("Duplicate Layer")
        button_layout.addWidget(self.duplicate_layer_btn)
        
        # Merge layer button
        self.merge_layer_btn = QPushButton()
        self.merge_layer_btn.setIcon(QIcon("icons/merge_layer.png"))
        self.merge_layer_btn.setToolTip("Merge Layer")
        button_layout.addWidget(self.merge_layer_btn)
        
        self.layout.addLayout(button_layout)
        
        # Create layer settings
        settings_layout = QVBoxLayout()
        
        # Opacity setting
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacity:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        settings_layout.addLayout(opacity_layout)
        
        # Blend mode setting
        blend_layout = QHBoxLayout()
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
        
        self.layout.addLayout(settings_layout)
        
    def connect_signals(self):
        """Connect signals and slots."""
        # Connect buttons
        self.new_layer_btn.clicked.connect(self.on_new_layer)
        self.delete_layer_btn.clicked.connect(self.on_delete_layer)
        self.duplicate_layer_btn.clicked.connect(self.on_duplicate_layer)
        self.merge_layer_btn.clicked.connect(self.on_merge_layer)
        
        # Connect settings
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        self.blend_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        
        # Connect layer list
        self.layer_list.itemSelectionChanged.connect(self.on_layer_selected)
        self.layer_list.itemChanged.connect(self.on_layer_renamed)
        
    def show_layer_menu(self, pos):
        """Show layer context menu."""
        menu = QMenu(self)
        
        # Add menu actions
        new_action = QAction("New Layer", self)
        new_action.triggered.connect(self.on_new_layer)
        menu.addAction(new_action)
        
        delete_action = QAction("Delete Layer", self)
        delete_action.triggered.connect(self.on_delete_layer)
        menu.addAction(delete_action)
        
        duplicate_action = QAction("Duplicate Layer", self)
        duplicate_action.triggered.connect(self.on_duplicate_layer)
        menu.addAction(duplicate_action)
        
        merge_action = QAction("Merge Down", self)
        merge_action.triggered.connect(self.on_merge_layer)
        menu.addAction(merge_action)
        
        menu.addSeparator()
        
        # Add visibility toggle
        visibility_action = QAction("Toggle Visibility", self)
        visibility_action.triggered.connect(self.on_toggle_visibility)
        menu.addAction(visibility_action)
        
        # Add lock toggle
        lock_action = QAction("Toggle Lock", self)
        lock_action.triggered.connect(self.on_toggle_lock)
        menu.addAction(lock_action)
        
        menu.exec(self.layer_list.mapToGlobal(pos))
        
    def on_new_layer(self):
        """Create new layer."""
        layer = self.layer_manager.add_layer()
        self.add_layer_item(layer)
        self.layer_changed.emit()
        
    def on_delete_layer(self):
        """Delete selected layer."""
        current = self.layer_list.currentRow()
        if current >= 0:
            self.layer_manager.remove_layer(current)
            self.layer_list.takeItem(current)
            self.layer_changed.emit()
            
    def on_duplicate_layer(self):
        """Duplicate selected layer."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.duplicate_layer(current)
            self.add_layer_item(layer)
            self.layer_changed.emit()
            
    def on_merge_layer(self):
        """Merge selected layer with layer below."""
        current = self.layer_list.currentRow()
        if current > 0:
            self.layer_manager.merge_layers(current, current - 1)
            self.layer_list.takeItem(current)
            self.layer_changed.emit()
            
    def on_toggle_visibility(self):
        """Toggle layer visibility."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.get_layer(current)
            layer.visible = not layer.visible
            self.update_layer_item(current)
            self.layer_changed.emit()
            
    def on_toggle_lock(self):
        """Toggle layer lock."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.get_layer(current)
            layer.locked = not layer.locked
            self.update_layer_item(current)
            
    def on_layer_selected(self):
        """Handle layer selection."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.get_layer(current)
            self.opacity_slider.setValue(int(layer.opacity * 100))
            self.blend_combo.setCurrentText(layer.blend_mode.title())
            
    def on_layer_renamed(self, item):
        """Handle layer rename."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.get_layer(current)
            layer.name = item.text()
            
    def on_opacity_changed(self, value):
        """Handle opacity change."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.get_layer(current)
            layer.opacity = value / 100.0
            self.layer_changed.emit()
            
    def on_blend_mode_changed(self, mode):
        """Handle blend mode change."""
        current = self.layer_list.currentRow()
        if current >= 0:
            layer = self.layer_manager.get_layer(current)
            layer.blend_mode = mode.lower()
            self.layer_changed.emit()
            
    def add_layer_item(self, layer):
        """Add layer to list."""
        item = QListWidgetItem(layer.name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.layer_list.addItem(item)
        
    def update_layer_item(self, index):
        """Update layer item in list."""
        layer = self.layer_manager.get_layer(index)
        item = self.layer_list.item(index)
        item.setText(layer.name)
        
    def update_layers(self):
        """Update layer list."""
        self.layer_list.clear()
        for layer in self.layer_manager.layers:
            self.add_layer_item(layer) 