"""
History panel component for PixelCrafterX.
Handles undo/redo history display and management.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QListWidget, QListWidgetItem, QLabel, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from core.history.history_manager import HistoryManager

class HistoryPanel(QWidget):
    # Signals
    undo_triggered = pyqtSignal()
    redo_triggered = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = HistoryManager()
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create history list
        self.create_history_list()
        
        # Create history controls
        self.create_history_controls()
        
        # Connect signals
        self.connect_signals()
        
    def create_history_list(self):
        """Create history list widget."""
        # Create history list group
        history_group = QGroupBox("History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        self.layout.addWidget(history_group)
        
    def create_history_controls(self):
        """Create history control buttons."""
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Undo button
        self.undo_btn = QPushButton()
        self.undo_btn.setIcon(QIcon("icons/undo.png"))
        self.undo_btn.setToolTip("Undo")
        button_layout.addWidget(self.undo_btn)
        
        # Redo button
        self.redo_btn = QPushButton()
        self.redo_btn.setIcon(QIcon("icons/redo.png"))
        self.redo_btn.setToolTip("Redo")
        button_layout.addWidget(self.redo_btn)
        
        # Clear history button
        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(QIcon("icons/clear_history.png"))
        self.clear_btn.setToolTip("Clear History")
        button_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(button_layout)
        
    def connect_signals(self):
        """Connect signals and slots."""
        # Connect buttons
        self.undo_btn.clicked.connect(self.on_undo)
        self.redo_btn.clicked.connect(self.on_redo)
        self.clear_btn.clicked.connect(self.on_clear)
        
        # Connect history list
        self.history_list.itemSelectionChanged.connect(self.on_history_selected)
        
    def on_undo(self):
        """Handle undo button click."""
        if self.history_manager.undo():
            self.undo_triggered.emit()
            self.update_history_list()
            
    def on_redo(self):
        """Handle redo button click."""
        if self.history_manager.redo():
            self.redo_triggered.emit()
            self.update_history_list()
            
    def on_clear(self):
        """Handle clear button click."""
        self.history_manager.clear()
        self.update_history_list()
        
    def on_history_selected(self):
        """Handle history item selection."""
        current = self.history_list.currentRow()
        if current >= 0:
            # Get state count
            state_count = self.history_manager.get_state_count()
            
            # Calculate steps to undo/redo
            steps = state_count - current - 1
            
            # Perform undo/redo
            if steps > 0:
                for _ in range(steps):
                    self.history_manager.undo()
                self.undo_triggered.emit()
            elif steps < 0:
                for _ in range(-steps):
                    self.history_manager.redo()
                self.redo_triggered.emit()
                
            self.update_history_list()
            
    def add_history_item(self, description: str):
        """Add item to history list."""
        item = QListWidgetItem(description)
        self.history_list.addItem(item)
        self.history_list.setCurrentItem(item)
        
    def update_history_list(self):
        """Update history list."""
        self.history_list.clear()
        
        # Add undo stack items
        for i in range(self.history_manager.get_state_count()):
            description = self.history_manager.get_undo_description()
            if description:
                self.history_list.addItem(description)
                
        # Add redo stack items
        for i in range(len(self.history_manager.redo_stack)):
            description = self.history_manager.get_redo_description()
            if description:
                item = QListWidgetItem(description)
                item.setForeground(Qt.GlobalColor.gray)
                self.history_list.addItem(item)
                
    def update_buttons(self):
        """Update button states."""
        self.undo_btn.setEnabled(self.history_manager.can_undo())
        self.redo_btn.setEnabled(self.history_manager.can_redo())
        self.clear_btn.setEnabled(self.history_manager.get_state_count() > 0) 