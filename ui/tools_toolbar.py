"""Custom toolbar for drawing tools in PixelCrafter X."""
from PyQt6.QtWidgets import (QToolBar, QToolButton, QButtonGroup, 
                           QVBoxLayout, QWidget, QSizePolicy, QLabel, 
                           QColorDialog, QFrame, QMenu, QWidgetAction)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction, QKeySequence

class ToolsToolBar(QToolBar):
    """Toolbar containing drawing tools."""
    
    toolChanged = pyqtSignal(str)  # Emitted when tool changes
    primaryColorChanged = pyqtSignal(QColor)  # Emitted when primary color changes
    secondaryColorChanged = pyqtSignal(QColor)  # Emitted when secondary color changes
    
    def __init__(self, parent=None):
        super().__init__("Tools", parent)
        self.setObjectName("ToolsToolBar")
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Tool groups
        self.tools_group = QButtonGroup(self)
        self.tools_group.setExclusive(True)
        
        # Colors
        self.primary_color = QColor(0, 0, 0, 255)  # Black by default
        self.secondary_color = QColor(255, 255, 255, 255)  # White by default
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Make toolbar vertical
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 5, 2, 5)
        layout.setSpacing(2)
        
        # Add tools
        self.add_tool("select", "Select Tool", "SP_TitleBarNormalButton")
        self.add_tool("crop", "Crop Tool", "SP_FileDialogDetailedView")
        self.add_separator()
        
        self.add_tool("move", "Move Tool", "SP_ToolBarHorizontalExtensionButton")
        self.add_tool("hand", "Hand Tool", "SP_TitleBarNormalButton")
        self.add_separator()
        
        # Drawing tools
        self.add_tool("brush", "Brush Tool", "SP_FileDialogDetailedView")
        self.add_tool("eraser", "Eraser Tool", "SP_DialogResetButton")
        self.add_tool("fill", "Fill Tool", "SP_FileDialogContentsView")
        self.add_tool("gradient", "Gradient Tool", "SP_ArrowDown")
        self.add_separator()
        
        # Shape tools
        self.add_tool("rectangle", "Rectangle Tool", "SP_DialogResetButton")
        self.add_tool("ellipse", "Ellipse Tool", "SP_DialogResetButton")
        self.add_tool("line", "Line Tool", "SP_ArrowForward")
        self.add_tool("arrow", "Arrow Tool", "SP_ArrowRight")
        self.add_tool("text", "Text Tool", "SP_FileDialogDetailedView")
        self.add_separator()
        
        # Color selection
        self.primary_color_btn = self.create_color_button("Primary Color", self.primary_color)
        self.secondary_color_btn = self.create_color_button("Secondary Color", self.secondary_color)
        
        # Swap colors button
        self.swap_colors_btn = QToolButton()
        self.swap_colors_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_BrowserReload")
        ))
        self.swap_colors_btn.setToolTip("Swap Colors")
        self.swap_colors_btn.clicked.connect(self.swap_colors)
        
        # Default colors button
        self.default_colors_btn = QToolButton()
        self.default_colors_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, "SP_DialogResetButton")
        ))
        self.default_colors_btn.setToolTip("Default Colors")
        self.default_colors_btn.clicked.connect(self.reset_colors)
        
        # Add color controls to layout
        color_layout = QVBoxLayout()
        color_layout.setSpacing(2)
        
        color_btn_layout = QHBoxLayout()
        color_btn_layout.addWidget(self.primary_color_btn)
        color_btn_layout.addWidget(self.secondary_color_btn)
        
        color_layout.addLayout(color_btn_layout)
        
        color_action_layout = QHBoxLayout()
        color_action_layout.addWidget(self.swap_colors_btn)
        color_action_layout.addWidget(self.default_colors_btn)
        
        color_layout.addLayout(color_action_layout)
        
        # Add all to main layout
        layout.addLayout(color_layout)
        layout.addStretch()
        
        # Set the widget to the toolbar
        self.addWidget(widget)
        
        # Set the first tool as active
        if self.tools_group.buttons():
            self.tools_group.buttons()[0].setChecked(True)
    
    def add_tool(self, tool_id, tool_name, icon_name):
        """Add a tool button to the toolbar."""
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setToolTip(tool_name)
        btn.setStatusTip(tool_name)
        
        # Try to use standard icon, fallback to text
        try:
            icon = self.style().standardIcon(getattr(self.style().StandardPixmap, icon_name))
            btn.setIcon(icon)
        except:
            btn.setText(tool_name[0])
        
        # Add to button group
        self.tools_group.addButton(btn)
        
        # Add to layout
        self.layout().insertWidget(self.layout().count() - 2, btn)  # Before the stretch
        
        # Connect signal
        btn.clicked.connect(lambda checked, t=tool_id: self.on_tool_clicked(t))
    
    def add_separator(self):
        """Add a separator to the toolbar."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout().insertWidget(self.layout().count() - 1, separator)
    
    def create_color_button(self, tooltip, color):
        """Create a color button with the given color."""
        btn = QToolButton()
        btn.setToolTip(tooltip)
        btn.setFixedSize(32, 24)
        btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {color.name()};
                border: 1px solid #666;
                border-radius: 2px;
            }}
            QToolButton:hover {{
                border: 1px solid #fff;
            }}
        """)
        
        # Add right-click menu for color picker
        btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda pos, b=btn, is_primary=tooltip.startswith('Primary'): 
            self.show_color_menu(b, is_primary, pos)
        )
        
        # Left click to swap with secondary color if this is primary
        if tooltip.startswith('Primary'):
            btn.clicked.connect(self.swap_colors)
        
        return btn
    
    def show_color_menu(self, button, is_primary, pos):
        """Show color context menu."""
        menu = QMenu(self)
        
        # Color picker action
        picker_action = QAction("Choose Color...", self)
        picker_action.triggered.connect(
            lambda: self.pick_color(button, is_primary)
        )
        
        # Add to menu
        menu.addAction(picker_action)
        
        # Show the menu
        menu.exec(button.mapToGlobal(pos))
    
    def pick_color(self, button, is_primary):
        """Open color picker dialog."""
        color = QColorDialog.getColor(
            self.primary_color if is_primary else self.secondary_color,
            self,
            "Select Color"
        )
        
        if color.isValid():
            self.set_color(color, is_primary)
    
    def set_color(self, color, is_primary):
        """Set the primary or secondary color."""
        if is_primary:
            self.primary_color = color
            self.primary_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #666; border-radius: 2px;"
            )
            self.primaryColorChanged.emit(color)
        else:
            self.secondary_color = color
            self.secondary_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #666; border-radius: 2px;"
            )
            self.secondaryColorChanged.emit(color)
    
    def swap_colors(self):
        """Swap primary and secondary colors."""
        temp = self.primary_color
        self.set_color(self.secondary_color, True)  # Set secondary as primary
        self.set_color(temp, False)  # Set primary as secondary
    
    def reset_colors(self):
        """Reset colors to default (black and white)."""
        self.set_color(QColor(0, 0, 0, 255), True)  # Black
        self.set_color(QColor(255, 255, 255, 255), False)  # White
    
    def on_tool_clicked(self, tool_id):
        """Handle tool button click."""
        self.toolChanged.emit(tool_id)
    
    def get_current_tool(self):
        """Get the currently selected tool ID."""
        for btn in self.tools_group.buttons():
            if btn.isChecked():
                return btn.toolTip().split()[0].lower()
        return None
    
    def set_current_tool(self, tool_id):
        """Set the current tool by ID."""
        for btn in self.tools_group.buttons():
            if btn.toolTip().lower().startswith(tool_id.lower()):
                btn.setChecked(True)
                self.toolChanged.emit(tool_id)
                break
