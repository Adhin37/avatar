import tkinter as tk
from tkinter import ttk

class ModernButton(ttk.Frame):
    def __init__(self, parent, text="", command=None, width=None, height=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Calculate dimensions based on parent if not provided
        if width is None:
            width = int(parent.winfo_width() * 0.15)  # 15% of parent width
        if height is None:
            height = int(parent.winfo_height() * 0.05)  # 5% of parent height
        
        # Create the button
        self.button = ttk.Button(
            self,
            text=text,
            command=command,
            style='Modern.TButton',
            width=width
        )
        self.button.pack(fill=tk.BOTH, expand=True)
        
        # Bind hover events
        self.button.bind('<Enter>', self._on_enter)
        self.button.bind('<Leave>', self._on_leave)
        self.button.bind('<Button-1>', self._on_press)
        self.button.bind('<ButtonRelease-1>', self._on_release)
    
    def _on_enter(self, event):
        """Handle mouse enter event"""
        self.button.state(['active'])
    
    def _on_leave(self, event):
        """Handle mouse leave event"""
        self.button.state(['!active'])
    
    def _on_press(self, event):
        """Handle mouse press event"""
        self.button.state(['pressed'])
    
    def _on_release(self, event):
        """Handle mouse release event"""
        self.button.state(['!pressed'])
    
    def configure(self, **kwargs):
        """Configure button properties"""
        self.button.configure(**kwargs)
    
    def cget(self, key):
        """Get button property"""
        return self.button.cget(key)
    
    @property
    def state(self):
        """Get button state"""
        return self.button.state()
    
    @state.setter
    def state(self, value):
        """Set button state"""
        self.button.state([value]) 