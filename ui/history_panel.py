"""History panel for tracking and managing document history states."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                           QListWidgetItem, QToolButton, QLabel, QMenu,
                           QStyle, QSizePolicy, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction

class HistoryPanel(QWidget):
    """Panel for displaying and managing document history states."""
    
    # Signals
    stateSelected = pyqtSignal(int)  # Emitted when a state is selected
    stateDeleted = pyqtSignal(int)   # Emitted when a state is deleted
    cleared = pyqtSignal()           # Emitted when history is cleared
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.states = []  # List of (description, thumbnail) tuples
        self.current_state = -1
        self.max_states = 100
        self.thumbnail_size = QSize(64, 48)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(2)
        
        # Navigation buttons
        self.back_btn = self.create_tool_button("Step Backward", "SP_MediaSeekBackward")
        self.forward_btn = self.create_tool_button("Step Forward", "SP_MediaSeekForward")
        
        # State management buttons
        self.snapshot_btn = self.create_tool_button("New Snapshot", "SP_FileIcon")
        self.clear_btn = self.create_tool_button("Clear History", "SP_TrashIcon")
        
        # Add to toolbar
        toolbar.addWidget(self.back_btn)
        toolbar.addWidget(self.forward_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.snapshot_btn)
        toolbar.addWidget(self.clear_btn)
        
        # State list
        self.state_list = QListWidget()
        self.state_list.setIconSize(self.thumbnail_size)
        self.state_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.state_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.state_list.setMovement(QListWidget.Movement.Static)
        self.state_list.setSpacing(4)
        self.state_list.setWordWrap(True)
        self.state_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.state_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect signals
        self.back_btn.clicked.connect(self.step_backward)
        self.forward_btn.clicked.connect(self.step_forward)
        self.snapshot_btn.clicked.connect(self.create_snapshot)
        self.clear_btn.clicked.connect(self.clear_history)
        self.state_list.itemClicked.connect(self.on_item_clicked)
        self.state_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Add to layout
        layout.addLayout(toolbar)
        layout.addWidget(self.state_list, 1)
        
        # Update buttons
        self.update_buttons()
    
    def create_tool_button(self, tooltip, icon_name):
        """Create a tool button with the given icon and tooltip."""
        btn = QToolButton()
        btn.setToolTip(tooltip)
        btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, icon_name)
        ))
        btn.setIconSize(QSize(16, 16))
        return btn
    
    def add_state(self, description, thumbnail):
        """Add a new state to the history."""
        # Remove any states after current position
        if self.current_state < len(self.states) - 1:
            self.states = self.states[:self.current_state + 1]
        
        # Add new state
        self.states.append((description, thumbnail))
        
        # Enforce maximum states
        if len(self.states) > self.max_states:
            self.states.pop(0)
        else:
            self.current_state = len(self.states) - 1
        
        # Update UI
        self.update_state_list()
    
    def update_state_list(self):
        """Update the state list widget."""
        self.state_list.clear()
        
        for i, (desc, pixmap) in enumerate(self.states):
            item = QListWidgetItem(desc)
            
            # Scale thumbnail
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                item.setIcon(QIcon(scaled_pixmap))
            
            # Highlight current state
            if i == self.current_state:
                item.setBackground(QColor(200, 230, 255))
            
            self.state_list.addItem(item)
        
        # Scroll to current state
        if 0 <= self.current_state < self.state_list.count():
            self.state_list.scrollToItem(
                self.state_list.item(self.current_state),
                QListWidget.ScrollHint.PositionAtCenter
            )
        
        # Update buttons
        self.update_buttons()
    
    def step_backward(self):
        """Step backward in history."""
        if self.current_state > 0:
            self.current_state -= 1
            self.stateSelected.emit(self.current_state)
            self.update_state_list()
    
    def step_forward(self):
        """Step forward in history."""
        if self.current_state < len(self.states) - 1:
            self.current_state += 1
            self.stateSelected.emit(self.current_state)
            self.update_state_list()
    
    def create_snapshot(self):
        """Create a new snapshot of the current state."""
        # This should be implemented by the parent widget
        # to provide the current document state
        pass
    
    def clear_history(self):
        """Clear the history."""
        self.states = []
        self.current_state = -1
        self.state_list.clear()
        self.cleared.emit()
    
    def on_item_clicked(self, item):
        """Handle item click."""
        row = self.state_list.row(item)
        if 0 <= row < len(self.states) and row != self.current_state:
            self.current_state = row
            self.stateSelected.emit(row)
            self.update_state_list()
    
    def on_item_double_clicked(self, item):
        """Handle item double-click."""
        row = self.state_list.row(item)
        if 0 <= row < len(self.states) and row != self.current_state:
            self.current_state = row
            self.stateSelected.emit(row)
            self.update_state_list()
    
    def show_context_menu(self, pos):
        """Show context menu for history items."""
        item = self.state_list.itemAt(pos)
        if not item:
            return
            
        row = self.state_list.row(item)
        if row < 0 or row >= len(self.states):
            return
        
        menu = QMenu(self)
        
        # View action
        view_action = QAction("View", self)
        view_action.triggered.connect(lambda: self.stateSelected.emit(row))
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_state(row))
        
        # Add actions
        menu.addAction(view_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        # Show menu
        menu.exec(self.state_list.mapToGlobal(pos))
    
    def delete_state(self, index):
        """Delete a state from the history."""
        if 0 <= index < len(self.states):
            self.states.pop(index)
            
            # Adjust current state index
            if index <= self.current_state:
                self.current_state = max(0, self.current_state - 1)
            
            # Update UI
            self.update_state_list()
            self.stateDeleted.emit(index)
    
    def update_buttons(self):
        """Update button states based on current history position."""
        self.back_btn.setEnabled(self.current_state > 0)
        self.forward_btn.setEnabled(self.current_state < len(self.states) - 1)
        self.clear_btn.setEnabled(len(self.states) > 0)
    
    def get_current_state(self):
        """Get the current state index."""
        return self.current_state
    
    def set_current_state(self, index):
        """Set the current state index."""
        if 0 <= index < len(self.states) and index != self.current_state:
            self.current_state = index
            self.update_state_list()
    
    def get_max_states(self):
        """Get the maximum number of history states."""
        return self.max_states
    
    def set_max_states(self, max_states):
        """Set the maximum number of history states."""
        self.max_states = max(1, max_states)
        
        # Trim history if needed
        if len(self.states) > self.max_states:
            self.states = self.states[-self.max_states:]
            self.current_state = min(self.current_state, len(self.states) - 1)
            self.update_state_list()
    
    def get_state_count(self):
        """Get the number of states in the history."""
        return len(self.states)
    
    def get_state(self, index):
        """Get the state at the specified index."""
        if 0 <= index < len(self.states):
            return self.states[index]
        return None
