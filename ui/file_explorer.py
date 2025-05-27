"""File explorer panel for browsing and opening project files."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
                           QFileSystemModel, QLineEdit, QPushButton, QToolButton,
                           QMenu, QFileIconProvider, QApplication, QStyle, QLabel)
from PyQt6.QtCore import Qt, QDir, QFileInfo, QSize
from PyQt6.QtGui import QIcon, QAction
import os

class FileExplorer(QWidget):
    """File explorer panel for browsing and opening files."""
    
    # Signals
    fileSelected = pyqtSignal(str)  # Emitted when a file is selected
    fileOpened = pyqtSignal(str)    # Emitted when a file is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = QDir.homePath()
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Navigation bar
        nav_layout = QHBoxLayout()
        
        # Back button
        self.back_btn = QToolButton()
        self.back_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowBack
        ))
        self.back_btn.setToolTip("Go back")
        self.back_btn.clicked.connect(self.navigate_back)
        
        # Forward button
        self.forward_btn = QToolButton()
        self.forward_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowForward
        ))
        self.forward_btn.setToolTip("Go forward")
        
        # Up button
        self.up_btn = QToolButton()
        self.up_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowUp
        ))
        self.up_btn.setToolTip("Go up")
        self.up_btn.clicked.connect(self.navigate_up)
        
        # Home button
        self.home_btn = QToolButton()
        self.home_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DirHomeIcon
        ))
        self.home_btn.setToolTip("Home directory")
        self.home_btn.clicked.connect(self.go_home)
        
        # Refresh button
        self.refresh_btn = QToolButton()
        self.refresh_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_BrowserReload
        ))
        self.refresh_btn.setToolTip("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        # Path bar
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Path...")
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        
        # Add to nav layout
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.up_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addWidget(self.path_edit)
        
        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)
        
        # File extensions to show
        image_extensions = [
            '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp',
            '.psd', '.xcf', '.kra', '.ora', '.clip', '.csp', '.sai'
        ]
        
        # Set name filters
        self.model.setNameFilters([f"*{ext}" for ext in image_extensions] + ["*"])
        self.model.setNameFilterDisables(False)
        
        # Tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
        # Hide unnecessary columns
        self.tree.setHeaderHidden(False)
        self.tree.hideColumn(1)  # Size
        self.tree.hideColumn(2)  # Type
        self.tree.hideColumn(3)  # Modified
        
        # Connect signals
        self.tree.clicked.connect(self.on_item_clicked)
        self.tree.doubleClicked.connect(self.on_item_double_clicked)
        
        # Status bar
        self.status_bar = QLabel()
        self.status_bar.setStyleSheet("color: #888; padding: 2px 5px;")
        
        # Add to main layout
        layout.addLayout(nav_layout)
        layout.addWidget(self.tree, 1)
        layout.addWidget(self.status_bar)
        
        # Initial update
        self.update_path(self.current_path)
        
        # Set initial directory
        self.go_home()
    
    def update_path(self, path):
        """Update the current path and UI elements."""
        self.current_path = path
        self.path_edit.setText(path)
        
        # Update status bar
        info = QFileInfo(path)
        if info.isDir():
            dir_info = QDir(path)
            count = len(dir_info.entryList(
                QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries
            ))
            self.status_bar.setText(f"{count} items")
        else:
            self.status_bar.setText(f"{info.size() / 1024:.1f} KB")
    
    def navigate_to_path(self, path=None):
        """Navigate to the specified path."""
        if path is None:
            path = self.path_edit.text()
            
        if not os.path.exists(path):
            return
            
        info = QFileInfo(path)
        if info.isDir():
            self.current_path = path
            self.tree.setRootIndex(self.model.index(path))
            self.update_path(path)
        else:
            self.fileOpened.emit(path)
    
    def navigate_back(self):
        """Navigate to the previous directory."""
        current_index = self.tree.rootIndex()
        parent_index = current_index.parent()
        if parent_index.isValid():
            self.tree.setRootIndex(parent_index)
            self.update_path(self.model.filePath(parent_index))
    
    def navigate_forward(self):
        """Navigate forward in history."""
        # TODO: Implement forward navigation with history
        pass
    
    def navigate_up(self):
        """Navigate up one directory level."""
        current_path = self.model.filePath(self.tree.rootIndex())
        parent_path = os.path.dirname(current_path)
        if parent_path and os.path.exists(parent_path):
            self.navigate_to_path(parent_path)
    
    def go_home(self):
        """Navigate to the user's home directory."""
        home_path = QDir.homePath()
        self.navigate_to_path(home_path)
    
    def refresh(self):
        """Refresh the current directory."""
        current_path = self.model.filePath(self.tree.rootIndex())
        self.model.setRootPath("")
        self.tree.setRootIndex(self.model.index(current_path))
    
    def on_item_clicked(self, index):
        """Handle item click."""
        path = self.model.filePath(index)
        self.fileSelected.emit(path)
    
    def on_item_double_clicked(self, index):
        """Handle item double-click."""
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.fileOpened.emit(path)
        else:
            self.navigate_to_path(path)
    
    def set_current_directory(self, path):
        """Set the current directory."""
        if os.path.isdir(path):
            self.navigate_to_path(path)
    
    def get_current_directory(self):
        """Get the current directory path."""
        return self.current_path
    
    def set_filters(self, filters):
        """Set file name filters."""
        self.model.setNameFilters(filters)
        self.model.setNameFilterDisables(False)
    
    def set_show_hidden(self, show):
        """Set whether to show hidden files."""
        self.model.setFilter(
            QDir.Filter.AllDirs | 
            QDir.Filter.NoDotAndDotDot | 
            QDir.Filter.AllEntries | 
            (QDir.Filter.Hidden if show else QDir.Filter.NoFilter)
        )


class FileIconProvider(QFileIconProvider):
    """Custom icon provider for file system model."""
    def __init__(self):
        super().__init__()
        self.icon_cache = {}
    
    def icon(self, info):
        """Return icon for the given file info."""
        if info.isDir():
            return super().icon(QFileIconProvider.IconType.Folder)
            
        ext = info.suffix().lower()
        if ext in self.icon_cache:
            return self.icon_cache[ext]
            
        # Try to get system icon for the file type
        icon = super().icon(QFileIconProvider.IconType.File)
        self.icon_cache[ext] = icon
        return icon
