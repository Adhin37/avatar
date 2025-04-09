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

class AudioDropZone:
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
    
    def __init__(self, parent):
        self.parent = parent
        self.accepted_formats = ('.mp3', '.wav', '.ogg')
        
        # CRITICAL: Main frame for hide/show functionality
        # DO NOT modify this frame's pack management without updating hide() and show()
        self.frame = ttk.Frame(parent)
        
        # Create outer frame with border
        self.border_frame = tk.Frame(
            self.frame,
            bg="#45475a",  # Border color
            padx=1,        # Border width
            pady=1
        )
        self.border_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Create container frame for better layout
        self.container = tk.Frame(
            self.border_frame,
            bg="#313244",  # Dark background
        )
        self.container.pack(fill=tk.X, expand=True)
        
        # Create icon label
        self.icon_label = tk.Label(
            self.container,
            text="♪",  # Musical note symbol (more widely supported)
            font=("Arial", 18, "bold"),  # Larger, bolder font
            fg="#cba6f7",
            bg="#313244",
            padx=10,
            pady=6
        )
        self.icon_label.pack(side=tk.LEFT)
        
        # Create drop zone with adjusted height and styling
        self.drop_label = tk.Label(
            self.container,
            text="Drop audio file here or click to browse",
            font=("Helvetica", 10),
            fg="#cdd6f4",
            bg="#313244",
            cursor="hand2",
            justify=tk.LEFT,
            padx=5,
            pady=8
        )
        self.drop_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create status label
        self.status_label = tk.Label(
            self.container,
            text="",
            font=("Helvetica", 9),
            fg="#6c7086",
            bg="#313244",
            padx=10,
            pady=8
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Track widget visibility state
        self._is_visible = False
        
        # Configure drop zone styling and bindings
        for widget in (self.icon_label, self.drop_label, self.status_label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Button-1>", self._on_click_visual, add="+")
        
        # Initialize handlers
        self.on_drop = None
        self.is_dragging = False
        
        # Setup drag and drop
        self._setup_drag_and_drop()
    
    def hide(self):
        """
        Hide the drop zone.
        CRITICAL: This method manages the main frame's pack state.
        """
        if self._is_visible:
            self.frame.pack_forget()
            self._is_visible = False
    
    def show(self):
        """
        Show the drop zone.
        CRITICAL: This method manages the main frame's pack state.
        """
        if not self._is_visible:
            self.frame.pack(fill=tk.X, pady=10)
            self._is_visible = True
    
    @property
    def is_visible(self):
        """Read-only property indicating if the widget is currently visible."""
        return self._is_visible
    
    def _on_click_visual(self, event):
        """Handle click visual feedback"""
        # Flash effect
        orig_bg = self.container["bg"]
        self.container.configure(bg="#454759")
        self.container.after(100, lambda: self.container.configure(bg=orig_bg))
    
    def _on_enter(self, event):
        """Handle mouse enter event"""
        if not self.is_dragging:
            self.border_frame.configure(bg="#89b4fa")  # Highlight border
            for widget in (self.icon_label, self.drop_label, self.status_label):
                widget.configure(bg="#454759")  # Lighter background
    
    def _on_leave(self, event):
        """Handle mouse leave event"""
        if not self.is_dragging:
            self.border_frame.configure(bg="#45475a")  # Normal border
            for widget in (self.icon_label, self.drop_label, self.status_label):
                widget.configure(bg="#313244")  # Normal background
    
    def _setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        try:
            # Register drop target for all widgets
            for widget in (self.container, self.drop_label, self.icon_label, self.status_label):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', self._on_drop)
                widget.dnd_bind('<<DragEnter>>', self._on_drag_enter)
                widget.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            
        except Exception as e:
            print(f"Warning: Could not initialize drag and drop: {e}")
            self.drop_label.configure(text="Click to browse audio file")
    
    def _on_drag_enter(self, event):
        """Handle drag enter event"""
        self.is_dragging = True
        self.border_frame.configure(bg="#cba6f7")  # Purple highlight
        for widget in (self.icon_label, self.drop_label, self.status_label):
            widget.configure(bg="#454759")  # Lighter background
        self.drop_label.configure(fg="#cba6f7")  # Purple text
        self.icon_label.configure(fg="#cba6f7")  # Purple icon
    
    def _on_drag_leave(self, event):
        """Handle drag leave event"""
        self.is_dragging = False
        self._on_leave(event)  # Reset to normal state
        self.drop_label.configure(fg="#cdd6f4")  # Normal text
        self.icon_label.configure(fg="#cba6f7")  # Normal icon color
    
    def _on_click(self, event):
        """Handle click event"""
        try:
            # Open file dialog
            file_path = tk.filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=[
                    ("Audio Files", " ".join(f"*{fmt}" for fmt in self.accepted_formats)),
                    ("All Files", "*.*")
                ],
                parent=self.parent
            )
            
            if file_path:
                self._handle_file(file_path)
                
        except Exception as e:
            print(f"Error opening file dialog: {e}")
            self.update_status("Error selecting file", "error")
    
    def _on_drop(self, event):
        """Handle file drop event"""
        try:
            # Get the dropped file path and clean it
            file_path = event.data
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]
            
            self._handle_file(file_path)
                
        except Exception as e:
            print(f"Error handling dropped file: {e}")
            self.update_status("Error processing file", "error")
    
    def _handle_file(self, file_path):
        """Process the received audio file"""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                self.update_status("File not found", "error")
                return
                
            # Validate file size (max 100MB)
            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                self.update_status("File too large (max 100MB)", "error")
                return
            
            # Validate file format
            if not file_path.lower().endswith(self.accepted_formats):
                self.update_status(f"Unsupported format (use {', '.join(self.accepted_formats)})", "error")
                return
            
            # File is valid, process it
            if self.on_drop:
                self.on_drop(file_path)
                filename = os.path.basename(file_path)
                self.update_status(f"Loaded: {filename}", "success")
            
        except Exception as e:
            print(f"Error processing file: {e}")
            self.update_status("Error processing file", "error")
    
    def bind_drop_handler(self, handler):
        """Bind drop event handler"""
        self.on_drop = handler
    
    def update_status(self, text, status="info"):
        """Update the dropzone text and color"""
        # Status colors
        colors = {
            "error": "#ff5555",
            "success": "#a6e3a1",
            "info": "#cdd6f4",
            "warning": "#f9e2af"
        }
        
        # Update main label
        if status == "error":
            self.drop_label.configure(
                text="Drop audio file here or click to browse",
                foreground=colors["info"]
            )
        
        # Update status label
        self.status_label.configure(
            text=text,
            foreground=colors.get(status, colors["info"])
        )