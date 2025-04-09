import tkinter as tk
from tkinter import ttk
import os

class WindowManager:
    """Manages the main application window and its properties"""
    
    def __init__(self, root):
        self.root = root
        self.is_maximized = False
        self.is_minimized = False
        self.normal_geometry = None
        
        # Initialize window
        self._initialize_window()
    
    def _initialize_window(self):
        """Initialize the main window"""
        self._configure_root()
        self._create_container()
        self._setup_styles()
        self._load_icon()
        self._bind_events()
    
    def _configure_root(self):
        """Configure the root window"""
        self.root.title("Avatar Lip Sync")
        self.root.geometry("500x700")  # Reduced width, increased height
        self.root.minsize(500, 700)    # Updated minimum size to match
        self.root.configure(bg='#2b2b2b')
    
    def _create_container(self):
        """Create the main container frame"""
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _setup_styles(self):
        """Setup custom styles for widgets"""
        style = ttk.Style()
        style.configure("TFrame", background='#2b2b2b')
        style.configure("TLabel", background='#2b2b2b', foreground='white')
        style.configure("TButton", background='#3b3b3b', foreground='white')
    
    def _load_icon(self):
        """Load the application icon"""
        try:
            # Get the absolute path to the resources directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            resources_dir = os.path.join(project_root, "resources")
            icon_path = os.path.join(resources_dir, "app_icon.ico")
            
            # Convert path to platform-specific format
            icon_path = os.path.normpath(icon_path)
            
            if os.path.exists(icon_path):
                # Use PhotoImage for cross-platform icon support
                from PIL import Image, ImageTk
                icon = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, photo)
                # Store reference to prevent garbage collection
                self.root.icon = photo
            else:
                print(f"Icon file not found at: {icon_path}")
        except Exception as e:
            print(f"Failed to load icon: {e}")
            # Try alternative icon formats if .ico fails
            try:
                # Try PNG format
                png_path = os.path.join(resources_dir, "app_icon.png")
                if os.path.exists(png_path):
                    from PIL import Image, ImageTk
                    icon = Image.open(png_path)
                    photo = ImageTk.PhotoImage(icon)
                    self.root.iconphoto(True, photo)
                    self.root.icon = photo
            except Exception as e2:
                print(f"Failed to load alternative icon: {e2}")
    
    def _bind_events(self):
        """Bind window events"""
        self.root.bind("<Configure>", self._on_window_configure)
    
    def _on_window_configure(self, event):
        """Handle window configuration changes"""
        if event.widget == self.root:
            self._update_container_size()
    
    def _update_container_size(self):
        """Update container size based on window state"""
        if self.is_maximized:
            self.container.pack_configure(padx=0, pady=0)
        else:
            self.container.pack_configure(padx=10, pady=10)
    
    def get_container(self):
        """Get the main container frame"""
        return self.container
    
    def bind_close_handler(self, handler):
        """Bind a handler for window close events"""
        self.root.protocol("WM_DELETE_WINDOW", handler)
    
    def _handle_close(self, event=None):
        """Handle window close event"""
        self.root.quit() 