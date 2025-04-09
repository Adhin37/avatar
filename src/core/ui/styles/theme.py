"""Theme management for the application UI"""

from typing import Dict, Any
import tkinter as tk
from tkinter import ttk

class Theme:
    """Manages application-wide theming and styling"""
    
    def __init__(self):
        # Default color palette
        self.colors = {
            'background': "#1e1e2e",  # Base background
            'surface': "#313244",     # Surface elements
            'primary': "#cba6f7",     # Primary accent
            'secondary': "#89b4fa",   # Secondary accent
            'text': "#f8f8f2",        # Primary text
            'text_secondary': "#cdd6f4", # Secondary text
            'border': "#3e3e4e",      # Borders
            'hover': "#45475a",       # Hover state
            'success': "#a6e3a1",     # Success state
            'error': "#f38ba8",       # Error state
            'warning': "#f9e2af",     # Warning state
            'info': "#89b4fa",        # Info state
            'waveform': "#4CAF50",    # Audio waveform
            'progress': "#89b4fa",    # Progress indicators
            'disabled': "#6c7086",    # Disabled state
            'foreground': "#cba6f7",  # Default foreground
            'accent': "#89b4fa"       # Accent color for highlights
        }
        
        # Default fonts
        self.fonts = {
            'default': ("Helvetica", 10),
            'title': ("Helvetica", 24, "bold"),
            'text': ("Helvetica", 12),
            'button': ("Helvetica", 12, "bold"),
            'small': ("Helvetica", 9)
        }
        
        # Initialize styles
        self._setup_styles()
    
    def get_color(self, key: str) -> str:
        """Get color by key"""
        return self.colors.get(key, self.colors['background'])
    
    def get_font(self, key: str) -> tuple:
        """Get font by key"""
        return self.fonts.get(key, self.fonts['default'])
    
    def apply_theme(self, root: tk.Tk) -> None:
        """Apply theme to root window and all widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure base styles
        style.configure(
            "TFrame",
            background=self.colors['background']
        )
        
        style.configure(
            "TLabel",
            background=self.colors['background'],
            foreground=self.colors['text'],
            font=self.fonts['text']
        )
        
        style.configure(
            "TButton",
            background=self.colors['surface'],
            foreground=self.colors['text'],
            font=self.fonts['button']
        )
        
        # Configure hover styles
        style.map(
            "TButton",
            background=[("active", self.colors['hover'])]
        )
        
        # Setup component-specific styles
        self._setup_styles()
    
    def _setup_styles(self) -> None:
        """Setup ttk styles for all components"""
        style = ttk.Style()
        
        # Avatar styles
        style.configure('Avatar.TFrame',
            background=self.colors['background']
        )
        
        style.configure('AvatarTitle.TLabel',
            background=self.colors['background'],
            foreground=self.colors['primary'],
            font=self.fonts['title']
        )
        
        # Audio Drop Zone styles
        style.configure('DropZone.TLabel',
            background=self.colors['surface'],
            foreground=self.colors['text'],
            font=self.fonts['text'],
            padding=10
        )
        
        style.configure('DropZoneHover.TLabel',
            background=self.colors['hover'],
            foreground=self.colors['primary'],
            font=self.fonts['text'],
            padding=10
        )
        
        # Modern Button styles
        style.configure('Modern.TButton',
            background=self.colors['surface'],
            foreground=self.colors['primary'],
            borderwidth=0,
            relief='flat',
            padding=5,
            font=self.fonts['button']
        )
        
        style.map('Modern.TButton',
            background=[
                ('active', self.colors['hover']),
                ('pressed', self.colors['surface']),
                ('disabled', self.colors['disabled'])
            ],
            foreground=[
                ('active', self.colors['primary']),
                ('pressed', self.colors['secondary']),
                ('disabled', self.colors['disabled'])
            ]
        )
        
        # Playback Controls styles
        style.configure('Playback.TFrame',
            background=self.colors['background']
        )
        
        style.configure('PlayPause.TButton',
            background=self.colors['surface'],
            foreground=self.colors['primary'],
            padding=5,
            font=self.fonts['button']
        )
        
        style.configure('Time.TLabel',
            background=self.colors['background'],
            foreground=self.colors['text_secondary'],
            font=self.fonts['small']
        )
    
    def get_button_style(self, color_key: str = 'primary') -> Dict[str, Any]:
        """Get button style configuration"""
        return {
            'bg': self.colors['surface'],
            'fg': self.colors.get(color_key, self.colors['primary']),
            'font': self.fonts['button'],
            'activebackground': self.colors['hover'],
            'activeforeground': self.colors.get(color_key, self.colors['primary'])
        }
    
    def get_label_style(self, color_key: str = 'text') -> Dict[str, Any]:
        """Get label style configuration"""
        return {
            'bg': self.colors['background'],
            'fg': self.colors.get(color_key, self.colors['text']),
            'font': self.fonts['text']
        }
    
    def get_frame_style(self) -> Dict[str, str]:
        """Get frame style configuration"""
        return {
            'bg': self.colors['background']
        } 