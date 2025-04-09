import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES

class AudioDropZone:
    def __init__(self, parent, on_drop=None, on_click=None):
        self.parent = parent
        self.on_drop = on_drop
        self.on_click = on_click
        
        # Create drop zone frame
        self.dropzone_frame = ttk.Frame(parent, height=150)
        self.dropzone_frame.pack(fill=tk.X, pady=20)
        
        # Create drop area
        self.drop_area = tk.Frame(self.dropzone_frame, bg="#2e2e3e", bd=2, relief=tk.GROOVE)
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # Create container frame
        self.container = tk.Frame(self.drop_area, bg="#2e2e3e")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Add icon and labels
        self.drop_icon = tk.Label(self.container, text="🎵", font=("Helvetica", 36), bg="#2e2e3e", fg="#89b4fa")
        self.drop_icon.pack(pady=(10, 5))
        
        self.drop_label = tk.Label(self.container, 
                                 text="Drag and drop audio file here\nor click to browse", 
                                 font=("Helvetica", 14), 
                                 bg="#2e2e3e", 
                                 fg="#f8f8f2")
        self.drop_label.pack(pady=5)
        
        self.formats_label = tk.Label(self.container,
                                    text="Supported formats: .mp3, .wav, .ogg",
                                    font=("Helvetica", 10),
                                    bg="#2e2e3e",
                                    fg="#7f849c")
        self.formats_label.pack(pady=5)
        
        # Setup hover effects
        self._setup_hover_effects()
        
        # Setup drag and drop
        self._setup_drag_drop()
        
    def _setup_hover_effects(self):
        def on_enter(e):
            self.drop_area.config(bg="#3e3e4e")
            self.drop_icon.config(bg="#3e3e4e")
            self.drop_label.config(bg="#3e3e4e")
            self.formats_label.config(bg="#3e3e4e")
            self.container.config(bg="#3e3e4e")
        
        def on_leave(e):
            self.drop_area.config(bg="#2e2e3e")
            self.drop_icon.config(bg="#2e2e3e")
            self.drop_label.config(bg="#2e2e3e")
            self.formats_label.config(bg="#2e2e3e")
            self.container.config(bg="#2e2e3e")
        
        # Bind hover events
        for widget in [self.drop_area, self.container, self.drop_icon, self.drop_label, self.formats_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            if self.on_click:
                widget.bind("<Button-1>", lambda e: self.on_click())
    
    def _setup_drag_drop(self):
        # Enable file drop support
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self._handle_drop)
        
        # Also enable for the icon and label
        self.drop_icon.drop_target_register(DND_FILES)
        self.drop_icon.dnd_bind('<<Drop>>', self._handle_drop)
        
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self._handle_drop)
    
    def _handle_drop(self, event):
        if self.on_drop:
            self.on_drop(event.data)
        return "break"
    
    def show(self):
        self.dropzone_frame.pack(fill=tk.X, pady=20)
    
    def hide(self):
        self.dropzone_frame.pack_forget()
    
    def update_status(self, text, color="#f8f8f2"):
        self.drop_label.config(text=text, fg=color) 