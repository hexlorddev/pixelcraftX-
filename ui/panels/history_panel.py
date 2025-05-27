from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton,
    QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

class HistoryPanel(QWidget):
    history_changed = pyqtSignal()  # Signal emitted when history changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.current_index = -1
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the history panel UI."""
        layout = QVBoxLayout(self)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.history_list.itemSelectionChanged.connect(self.on_history_selected)
        layout.addWidget(self.history_list)
        
        # History controls
        controls_layout = QHBoxLayout()
        
        # Undo button
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        controls_layout.addWidget(self.undo_btn)
        
        # Redo button
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        controls_layout.addWidget(self.redo_btn)
        
        layout.addLayout(controls_layout)
        
    def add_action(self, action_name: str, action_data: dict):
        """Add a new action to the history."""
        # Remove any actions after current index
        self.history = self.history[:self.current_index + 1]
        
        # Add new action
        self.history.append({
            'name': action_name,
            'data': action_data
        })
        self.current_index = len(self.history) - 1
        
        # Update UI
        self.history_list.addItem(action_name)
        self.history_list.setCurrentRow(self.current_index)
        self.update_buttons()
        self.history_changed.emit()
        
    def undo(self):
        """Undo the last action."""
        if self.current_index > 0:
            self.current_index -= 1
            self.history_list.setCurrentRow(self.current_index)
            self.update_buttons()
            self.history_changed.emit()
            
    def redo(self):
        """Redo the last undone action."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.history_list.setCurrentRow(self.current_index)
            self.update_buttons()
            self.history_changed.emit()
            
    def update_buttons(self):
        """Update undo/redo button states."""
        self.undo_btn.setEnabled(self.current_index > 0)
        self.redo_btn.setEnabled(self.current_index < len(self.history) - 1)
        
    def on_history_selected(self):
        """Handle history item selection."""
        current_row = self.history_list.currentRow()
        if current_row != self.current_index:
            self.current_index = current_row
            self.update_buttons()
            self.history_changed.emit() 