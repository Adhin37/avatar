from tkinter import ttk

class Theme:
    """Manages application-wide theming and styling"""
    
    def __init__(self):
        self.colors = {
            'background': "#1e1e2e",
            'surface': "#313244",
            'primary': "#cba6f7",
            'secondary': "#89b4fa",
            'success': "#a6e3a1",
            'error': "#f38ba8",
            'text': "#f8f8f2",
            'text_secondary': "#cdd6f4",
            'hover': "#45475a"
        }
        
        self.fonts = {
            'default': ("Helvetica", 10),
            'title': ("Helvetica", 10, "bold"),
            'small': ("Helvetica", 9)
        }
    
    def get_color(self, key):
        """Get color by key"""
        return self.colors.get(key, self.colors['background'])
    
    def get_font(self, key):
        """Get font by key"""
        return self.fonts.get(key, self.fonts['default'])
    
    def apply_theme(self, root):
        """Apply theme to root window and all widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk styles
        style.configure(
            "TFrame",
            background=self.colors['background']
        )
        
        style.configure(
            "TLabel",
            background=self.colors['background'],
            foreground=self.colors['text'],
            font=self.fonts['default']
        )
        
        style.configure(
            "TButton",
            background=self.colors['surface'],
            foreground=self.colors['text'],
            font=self.fonts['default']
        )
        
        # Configure hover styles
        style.map(
            "TButton",
            background=[("active", self.colors['hover'])]
        )
    
    def get_button_style(self, color_key='primary'):
        """Get button style configuration"""
        return {
            'bg': self.colors['surface'],
            'fg': self.colors.get(color_key, self.colors['primary']),
            'font': self.fonts['default'],
            'activebackground': self.colors['hover'],
            'activeforeground': self.colors.get(color_key, self.colors['primary'])
        }
    
    def get_label_style(self, color_key='text'):
        """Get label style configuration"""
        return {
            'bg': self.colors['background'],
            'fg': self.colors.get(color_key, self.colors['text']),
            'font': self.fonts['default']
        }
    
    def get_frame_style(self):
        """Get frame style configuration"""
        return {
            'bg': self.colors['background']
        } 