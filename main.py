#!/usr/bin/env python3
"""
PixelCrafter X - Main Application Entry Point
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QMessageBox, QGraphicsView, QGraphicsScene, QMenuBar, QMenu, QAction, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QKeySequence, QPainter

from ui.main_window import MainWindow
from utils.config import load_config, save_config

class PixelCrafterX(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelCrafter X")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create canvas (QGraphicsView)
        self.scene = QGraphicsScene()
        self.canvas = QGraphicsView(self.scene)
        self.canvas.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.canvas)
        
        # Create menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        file_menu = QMenu("File", self)
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        self.menu_bar.addMenu(file_menu)
        
        # Edit menu
        edit_menu = QMenu("Edit", self)
        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        self.menu_bar.addMenu(edit_menu)
        
        # View menu
        view_menu = QMenu("View", self)
        zoom_in_action = QAction("Zoom In", self)
        zoom_out_action = QAction("Zoom Out", self)
        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)
        self.menu_bar.addMenu(view_menu)
        
        # Help menu
        help_menu = QMenu("Help", self)
        about_action = QAction("About", self)
        help_menu.addAction(about_action)
        self.menu_bar.addMenu(help_menu)

def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = PixelCrafterX()
    window.show()
    
    # Save settings on exit
    app.aboutToQuit.connect(window.save_settings)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
