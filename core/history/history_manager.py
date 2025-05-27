"""
History management system for PixelCrafterX.
Handles undo/redo operations and command history.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass
from PyQt6.QtGui import QImage

@dataclass
class HistoryState:
    """Represents a state in the history."""
    description: str
    data: Any
    timestamp: float

class Command(ABC):
    """Base class for all commands."""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command."""
        pass
        
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command."""
        pass
        
    @abstractmethod
    def redo(self) -> bool:
        """Redo the command."""
        pass

class LayerCommand(Command):
    """Command for layer operations."""
    
    def __init__(self, layer_index: int, old_state: QImage, new_state: QImage, description: str):
        self.layer_index = layer_index
        self.old_state = old_state
        self.new_state = new_state
        self.description = description
        
    def execute(self) -> bool:
        """Execute the layer command."""
        return True
        
    def undo(self) -> bool:
        """Undo the layer command."""
        return True
        
    def redo(self) -> bool:
        """Redo the layer command."""
        return True

class HistoryManager:
    def __init__(self, max_states: int = 50):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_states = max_states
        
    def add_command(self, command: Command) -> bool:
        """Add a new command to the history."""
        if len(self.undo_stack) >= self.max_states:
            self.undo_stack.pop(0)
            
        self.undo_stack.append(command)
        self.redo_stack.clear()
        return True
        
    def undo(self) -> bool:
        """Undo the last command."""
        if not self.undo_stack:
            return False
            
        command = self.undo_stack.pop()
        if command.undo():
            self.redo_stack.append(command)
            return True
        return False
        
    def redo(self) -> bool:
        """Redo the last undone command."""
        if not self.redo_stack:
            return False
            
        command = self.redo_stack.pop()
        if command.redo():
            self.undo_stack.append(command)
            return True
        return False
        
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0
        
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
        
    def get_undo_description(self) -> Optional[str]:
        """Get description of the last command that can be undone."""
        if self.undo_stack:
            return self.undo_stack[-1].description
        return None
        
    def get_redo_description(self) -> Optional[str]:
        """Get description of the last command that can be redone."""
        if self.redo_stack:
            return self.redo_stack[-1].description
        return None
        
    def clear(self):
        """Clear the history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        
    def get_state_count(self) -> int:
        """Get the number of states in the history."""
        return len(self.undo_stack)
        
    def set_max_states(self, max_states: int):
        """Set the maximum number of states to keep."""
        self.max_states = max_states
        while len(self.undo_stack) > max_states:
            self.undo_stack.pop(0) 