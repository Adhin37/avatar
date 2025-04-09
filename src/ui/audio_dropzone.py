import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageDraw, ImageTk

class AudioDropZone:
    def __init__(self, parent, on_drop=None, on_click=None):
        self.parent = parent
        self.on_drop = on_drop
        self.on_click = on_click
        
        # Create drop zone frame
        self.dropzone_frame = ttk.Frame(parent, height=100)
        self.dropzone_frame.pack(fill=tk.X, pady=10)
        
        # Create drop area
        self.drop_area = tk.Frame(self.dropzone_frame, bg="#2e2e3e", bd=2, relief=tk.GROOVE)
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Create container frame with Windows Explorer-like layout
        self.container = tk.Frame(self.drop_area, bg="#2e2e3e")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Explorer interface frame
        self.explorer_frame = tk.Frame(self.container, bg="#2e2e3e")
        self.explorer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title bar with folder icon
        self.title_bar = tk.Frame(self.explorer_frame, bg="#3e3e4e", height=30)
        self.title_bar.pack(fill=tk.X)
        
        # Create and set folder icon
        folder_icon = self._create_folder_icon()
        self.folder_icon = tk.Label(self.title_bar, image=folder_icon, bg="#3e3e4e")
        self.folder_icon.image = folder_icon  # Keep a reference
        self.folder_icon.pack(side=tk.LEFT, padx=5)
        
        self.title_label = tk.Label(self.title_bar, text="Select Audio File", 
                                   font=("Helvetica", 10, "bold"), 
                                   bg="#3e3e4e", fg="#f8f8f2")
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Main content area with file icon
        self.content_area = tk.Frame(self.explorer_frame, bg="#2e2e3e")
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Create and set music note icon
        music_icon = self._create_music_icon()
        self.file_icon = tk.Label(self.content_area, image=music_icon, bg="#2e2e3e")
        self.file_icon.image = music_icon  # Keep a reference
        self.file_icon.pack(pady=(10, 5))
        
        # Instruction label
        self.instructions = tk.Label(self.content_area, 
                                   text="Drag and drop audio file here\nor click to browse", 
                                   font=("Helvetica", 10),
                                   bg="#2e2e3e", fg="#f8f8f2")
        self.instructions.pack(pady=2)
        
        # Setup hover effects
        self._setup_hover_effects()
        
        # Setup drag and drop
        self._setup_drag_drop()
    
    def _create_folder_icon(self):
        """Create a folder icon"""
        size = 16
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Folder colors
        folder_color = "#89b4fa"
        
        # Draw folder base
        draw.rectangle([0, size//4, size-1, size-1], fill=folder_color)
        # Draw folder top
        draw.rectangle([0, size//4, size//3, size//2], fill=folder_color)
        # Draw folder tab
        points = [(size//3, size//4), (size//2, 0), (size-1, 0), (size-1, size//4)]
        draw.polygon(points, fill=folder_color)
        
        return ImageTk.PhotoImage(icon)
    
    def _create_music_icon(self):
        """Create a music note icon"""
        size = 48
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Music note color
        note_color = "#89b4fa"
        
        # Draw note head (ellipse)
        head_width = size // 4
        head_height = size // 3
        head_x = size // 2
        head_y = size * 2 // 3
        draw.ellipse([head_x, head_y, head_x + head_width, head_y + head_height], fill=note_color)
        
        # Draw note stem
        stem_width = size // 16
        draw.rectangle([head_x + head_width - stem_width, size//4, 
                       head_x + head_width, head_y + head_height//2], fill=note_color)
        
        # Draw flag
        flag_points = [
            (head_x + head_width, size//4),
            (head_x + head_width + size//4, size//3),
            (head_x + head_width, size//2)
        ]
        draw.polygon(flag_points, fill=note_color)
        
        return ImageTk.PhotoImage(icon)
    
    def _setup_hover_effects(self):
        # Hover effects for content area
        def content_on_enter(e):
            self.content_area.config(bg="#3e3e4e")
            self.file_icon.config(bg="#3e3e4e")
            self.instructions.config(bg="#3e3e4e")
        
        def content_on_leave(e):
            self.content_area.config(bg="#2e2e3e")
            self.file_icon.config(bg="#2e2e3e")
            self.instructions.config(bg="#2e2e3e")
        
        # Bind hover events for content area
        for widget in [self.content_area, self.file_icon, self.instructions]:
            widget.bind("<Enter>", content_on_enter)
            widget.bind("<Leave>", content_on_leave)
            if self.on_click:
                widget.bind("<Button-1>", lambda e: self._handle_click())
    
    def _setup_drag_drop(self):
        # Enable file drop support for all relevant widgets
        for widget in [self.drop_area, self.container, self.explorer_frame, 
                     self.content_area, self.file_icon, self.instructions]:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self._handle_drop)
    
    def _handle_drop(self, event):
        if self.on_drop:
            self.on_drop(event.data)
        return "break"
    
    def _handle_click(self):
        if self.on_click:
            self.on_click()
    
    def show(self):
        self.dropzone_frame.pack(fill=tk.X, pady=20)
    
    def hide(self):
        self.dropzone_frame.pack_forget()
    
    def update_status(self, text, color="#f8f8f2"):
        self.instructions.config(text=text, fg=color)