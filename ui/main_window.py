"""
Main window for PixelCrafter X - Core UI components.
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QFileDialog, QMessageBox, QStatusBar, QToolBar,
    QVBoxLayout, QWidget, QLabel, QMenuBar, QMenu, QSizePolicy, QToolButton,
    QColorDialog, QSlider, QComboBox, QHBoxLayout, QSplitter, QTabWidget,
    QPushButton, QGraphicsView, QGraphicsScene
)
from PyQt6.QtCore import Qt, QSize, QSettings, QTimer, QPoint, QRectF
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QColor, QFont, QPainter, QPen, QBrush

from core.canvas import Canvas
from utils.config import load_config, save_config

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or load_config()
        self.current_file = None
        self.unsaved_changes = False
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        self.setup_docks()
        self.setup_central_widget()
        self.load_settings()
        
        # Set window properties
        self.setWindowTitle("PixelCrafter X")
        self.resize(1280, 800)
        self.setMinimumSize(800, 600)
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Apply stylesheet
        self.apply_styles()
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
    
    def apply_styles(self):
        """Apply application styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
            }
            QToolBar {
                background-color: #333337;
                border: none;
                spacing: 2px;
                padding: 2px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px;
            }
            QToolButton:hover {
                background-color: #3F3F46;
            }
            QToolButton:checked {
                background-color: #007ACC;
            }
            QDockWidget {
                titlebar-close-icon: url(none.png);
                titlebar-normal-icon: url(none.png);
            }
            QDockWidget::title {
                text-align: left;
                padding: 5px;
                background: #333337;
            }
            QStatusBar {
                background: #333337;
                color: #FFFFFF;
            }
        """)
    
    def setup_menus(self):
        """Set up the menu bar and menus."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # New File
        new_action = QAction("&New...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Open File
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)
        
        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_toolbars(self):
        """Set up the toolbars."""
        # Main Toolbar
        self.main_toolbar = QToolBar("Main Toolbar", self)
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.main_toolbar)
        
        # Add actions to toolbar
        self.main_toolbar.addAction(self.findChild(QAction, "new_action"))
        self.main_toolbar.addAction(self.findChild(QAction, "open_action"))
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addSeparator()
        
        # Tools Toolbar
        self.tools_toolbar = QToolBar("Tools", self)
        self.tools_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.tools_toolbar)
        
        # Add tool buttons
        self.setup_tool_buttons()
    
    def setup_tool_buttons(self):
        """Set up tool buttons in the tools toolbar."""
        # Selection Tool
        select_tool = QAction(QIcon("assets/icons/select.png"), "Select", self)
        select_tool.setCheckable(True)
        select_tool.setChecked(True)
        select_tool.triggered.connect(lambda: self.set_tool("select"))
        self.tools_toolbar.addAction(select_tool)
        
        # Brush Tool
        brush_tool = QAction(QIcon("assets/icons/brush.png"), "Brush", self)
        brush_tool.setCheckable(True)
        brush_tool.triggered.connect(lambda: self.set_tool("brush"))
        self.tools_toolbar.addAction(brush_tool)
        
        # Eraser Tool
        eraser_tool = QAction(QIcon("assets/icons/eraser.png"), "Eraser", self)
        eraser_tool.setCheckable(True)
        eraser_tool.triggered.connect(lambda: self.set_tool("eraser"))
        self.tools_toolbar.addAction(eraser_tool)
        
        # Color Picker
        self.color_btn = QToolButton()
        self.color_btn.setFixedSize(32, 32)
        self.color_btn.setStyleSheet("""
            QToolButton {
                background-color: #000000;
                border: 2px solid #3F3F46;
                border-radius: 4px;
            }
            QToolButton:hover {
                border: 2px solid #007ACC;
            }
        """)
        self.color_btn.clicked.connect(self.choose_color)
        self.tools_toolbar.addWidget(self.color_btn)
    
    def setup_statusbar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Position indicator
        self.pos_label = QLabel("X: 0, Y: 0")
        self.status_bar.addPermanentWidget(self.pos_label)
        
        # Zoom level
        self.zoom_label = QLabel("100%")
        self.status_bar.addPermanentWidget(self.zoom_label)
        
        # Default status message
        self.status_bar.showMessage("Ready")
    
    def setup_docks(self):
        """Set up dockable panels."""
        # Layers Panel
        self.layers_dock = QDockWidget("Layers", self)
        self.layers_widget = QWidget()
        self.layers_layout = QVBoxLayout(self.layers_widget)
        self.layers_dock.setWidget(self.layers_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layers_dock)
        
        # Properties Panel
        self.props_dock = QDockWidget("Properties", self)
        self.props_widget = QWidget()
        self.props_layout = QVBoxLayout(self.props_widget)
        self.props_dock.setWidget(self.props_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.props_dock)
        
        # Tool Options Panel
        self.tool_options_dock = QDockWidget("Tool Options", self)
        self.tool_options_widget = QWidget()
        self.tool_options_layout = QVBoxLayout(self.tool_options_widget)
        self.tool_options_dock.setWidget(self.tool_options_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tool_options_dock)
    
    def setup_central_widget(self):
        """Set up the central widget with canvas."""
        # Create canvas
        self.canvas = Canvas()
        self.main_layout.addWidget(self.canvas)
        
        # Connect canvas signals
        self.canvas.mouseMoved.connect(self.update_position_indicator)
        self.canvas.zoomChanged.connect(self.update_zoom_indicator)
    
    def load_settings(self):
        """Load window state and settings."""
        settings = QSettings("PixelCrafter", "PixelCrafterX")
        self.restoreGeometry(settings.value("geometry", self.saveGeometry()))
        self.restoreState(settings.value("windowState", self.saveState()))
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.maybe_save():
            settings = QSettings("PixelCrafter", "PixelCrafterX")
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("windowState", self.saveState())
            event.accept()
        else:
            event.ignore()
    
    # Tool methods
    def set_tool(self, tool_name):
        """Set the current tool."""
        self.current_tool = tool_name
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.set_tool(tool_name)
    
    def choose_color(self):
        """Open color dialog and set the selected color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color.name()};
                    border: 2px solid #3F3F46;
                    border-radius: 4px;
                }}
                QToolButton:hover {{
                    border: 2px solid #007ACC;
                }}
            """)
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.set_brush_color(color)
    
    # File operations
    def new_file(self):
        """Create a new file."""
        if self.maybe_save():
            # Reset canvas
            self.canvas.clear()
            self.current_file = None
            self.unsaved_changes = False
            self.update_window_title()
    
    def open_file(self):
        """Open an existing file."""
        if not self.maybe_save():
            return
            
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            
        if file_name:
            if self.canvas.load_image(file_name):
                self.current_file = file_name
                self.unsaved_changes = False
                self.update_window_title()
    
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            if self.canvas.save_image(self.current_file):
                self.unsaved_changes = False
                self.update_window_title()
                return True
        else:
            return self.save_file_as()
        return False
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)")
            
        if file_name:
            if self.canvas.save_image(file_name):
                self.current_file = file_name
                self.unsaved_changes = False
                self.update_window_title()
                return True
        return False
    
    def maybe_save(self):
        """Prompt to save if there are unsaved changes."""
        if not self.unsaved_changes:
            return True
            
        ret = QMessageBox.warning(
            self, "Unsaved Changes",
            "The document has been modified.\nDo you want to save your changes?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        
        if ret == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif ret == QMessageBox.StandardButton.Cancel:
            return False
        return True
    
    def update_window_title(self):
        """Update the window title with the current file name and modified status."""
        title = "PixelCrafter X"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.unsaved_changes:
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def update_position_indicator(self, pos):
        """Update the position indicator in the status bar."""
        self.pos_label.setText(f"X: {pos.x()}, Y: {pos.y()}")
    
    def update_zoom_indicator(self, zoom_level):
        """Update the zoom level indicator in the status bar."""
        self.zoom_label.setText(f"{int(zoom_level * 100)}%")

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
