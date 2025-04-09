import tkinter as tk
from tkinter import ttk

class ModernButton(ttk.Button):
    """A modern-looking button with hover effects"""
    
    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure(
            "Modern.TButton",
            background="#313244",
            foreground="#cdd6f4",
            padding=10,
            font=("Helvetica", 10)
        )
        
        # Apply style
        self.configure(style="Modern.TButton")
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter event"""
        self.style.configure(
            "Modern.TButton",
            background="#45475a"
        )
    
    def _on_leave(self, event):
        """Handle mouse leave event"""
        self.style.configure(
            "Modern.TButton",
            background="#313244"
        ) 