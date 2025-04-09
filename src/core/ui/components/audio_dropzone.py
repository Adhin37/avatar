"""
Audio Drop Zone Component

This component provides a drag-and-drop interface for audio files with the following features:
- Drag and drop support for audio files
- Click to browse functionality
- Visual feedback for interactions
- Status display for operations
- Hide/Show capability for dynamic UI

IMPORTANT: This component uses pack geometry manager with specific settings.
Any modifications to the widget hierarchy must preserve the following structure:
    frame (ttk.Frame)
    └── border_frame (tk.Frame)
        └── container (tk.Frame)
            ├── icon_label (tk.Label)
            ├── drop_label (tk.Label)
            └── status_label (tk.Label)

The hide/show functionality relies on managing the main frame's pack state.
DO NOT modify the frame packing hierarchy without updating hide() and show() methods.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageDraw, ImageTk
import os

class AudioDropZone(ttk.Frame):
    """
    Audio Drop Zone widget that supports drag and drop, file browsing, and hide/show functionality.
    
    Key Methods:
        hide(): Removes the widget from view
        show(): Displays the widget
        update_status(text, status): Updates the status display
        bind_drop_handler(handler): Sets the file drop callback
    
    Important:
        - The widget uses pack geometry manager
        - hide/show functionality manages the main frame's pack state
        - Preserve the widget hierarchy when modifying the code
    """
    
    def __init__(self, parent, on_file_selected=None):
        super().__init__(parent)
        self.parent = parent
        self.on_file_selected = on_file_selected
        self.theme = parent.winfo_toplevel().theme
        
        # Create the drop zone label
        self.label = ttk.Label(
            self,
            text="Drop audio file here\nor click to browse",
            style='DropZone.TLabel'
        )
        self.label.pack(expand=True, fill='both')
        
        # Bind events
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
        self.label.bind('<Button-1>', self._on_click)
        self.drop_target = DND_FILES(self.label)
        self.drop_target.bindtarget('<Drop>', self._on_drop, 'text/uri-list')
    
    def _on_enter(self, event):
        """Handle mouse enter event"""
        self.label.configure(style='DropZoneHover.TLabel')
    
    def _on_leave(self, event):
        """Handle mouse leave event"""
        self.label.configure(style='DropZone.TLabel')
    
    def _on_drop(self, event):
        """Handle file drop event"""
        file_path = event.data.strip('{}').replace('\\', '/').strip()
        if self._is_valid_audio_file(file_path):
            if self.on_file_selected:
                self.on_file_selected(file_path)
    
    def _on_click(self, event):
        """Handle click event to open file dialog"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ('Audio Files', '*.wav *.mp3 *.ogg'),
                ('All Files', '*.*')
            ]
        )
        if file_path and self._is_valid_audio_file(file_path):
            if self.on_file_selected:
                self.on_file_selected(file_path)
    
    def _is_valid_audio_file(self, file_path):
        """Check if the file is a valid audio file"""
        return file_path.lower().endswith(('.wav', '.mp3', '.ogg'))
    
    def show(self):
        """Show the drop zone"""
        self.pack(expand=True, fill='both', padx=10, pady=10)
    
    def hide(self):
        """Hide the drop zone"""
        self.pack_forget()
    
    @property
    def visible(self):
        """Check if the drop zone is visible"""
        return self.winfo_ismapped()