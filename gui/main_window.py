"""
Main window for PixelCrafterX.
Handles the main application window and UI layout.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QToolBar, QStatusBar, QDockWidget, QMenuBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from gui.canvas_view import CanvasView
from gui.tool_panel import ToolPanel
from gui.layer_panel import LayerPanel
from gui.color_panel import ColorPanel
from gui.history_panel import HistoryPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelCrafterX")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create canvas view
        self.canvas_view = CanvasView()
        self.main_layout.addWidget(self.canvas_view)
        
        # Create tool panel
        self.tool_panel = ToolPanel()
        self.tool_dock = QDockWidget("Tools")
        self.tool_dock.setWidget(self.tool_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tool_dock)
        
        # Create layer panel
        self.layer_panel = LayerPanel()
        self.layer_dock = QDockWidget("Layers")
        self.layer_dock.setWidget(self.layer_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)
        
        # Create color panel
        self.color_panel = ColorPanel()
        self.color_dock = QDockWidget("Colors")
        self.color_dock.setWidget(self.color_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.color_dock)
        
        # Create history panel
        self.history_panel = HistoryPanel()
        self.history_dock = QDockWidget("History")
        self.history_dock.setWidget(self.history_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.history_dock)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tool bar
        self.create_tool_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.connect_signals()
        
    def create_menu_bar(self):
        """Create menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export", self)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("Fit to Window", self)
        zoom_fit_action.setShortcut("Ctrl+0")
        view_menu.addAction(zoom_fit_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("Help")
        
        about_action = QAction("About", self)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """Create tool bar."""
        self.tool_bar = QToolBar()
        self.tool_bar.setIconSize(QSize(32, 32))
        self.addToolBar(self.tool_bar)
        
        # Add tool actions
        self.tool_bar.addAction(QIcon("icons/brush.png"), "Brush")
        self.tool_bar.addAction(QIcon("icons/eraser.png"), "Eraser")
        self.tool_bar.addAction(QIcon("icons/fill.png"), "Fill")
        self.tool_bar.addAction(QIcon("icons/select.png"), "Select")
        
        self.tool_bar.addSeparator()
        
        self.tool_bar.addAction(QIcon("icons/zoom.png"), "Zoom")
        self.tool_bar.addAction(QIcon("icons/hand.png"), "Hand")
        
    def connect_signals(self):
        """Connect signals and slots."""
        # Connect tool panel signals
        self.tool_panel.tool_changed.connect(self.canvas_view.set_tool)
        
        # Connect layer panel signals
        self.layer_panel.layer_changed.connect(self.canvas_view.update_layers)
        
        # Connect color panel signals
        self.color_panel.color_changed.connect(self.canvas_view.set_color)
        
        # Connect history panel signals
        self.history_panel.undo_triggered.connect(self.canvas_view.undo)
        self.history_panel.redo_triggered.connect(self.canvas_view.redo) 