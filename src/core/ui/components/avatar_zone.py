import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class AvatarZone:
    def __init__(self, parent, width=None, height=None):
        self.parent = parent
        
        # Get theme instance from root window
        self.theme = parent.winfo_toplevel().theme
        
        # Calculate dimensions based on screen if not provided
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        self.width = width or int(screen_width * 0.3)  # 30% of screen width
        self.height = height or int(screen_height * 0.4)  # 40% of screen height
        
        # Create main frame for avatar
        self.avatar_frame = ttk.Frame(parent)
        self.avatar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title at the top
        self.title = ttk.Label(
            self.avatar_frame,
            text="Avatar Lip Sync",
            font=self.theme.get_font('title'),
            style='Title.TLabel'
        )
        self.title.pack(pady=(0, 10))
        
        # Create canvas for avatar display
        self.canvas = tk.Canvas(
            self.avatar_frame,
            width=self.width,
            height=self.height,
            bg=self.theme.get_color('background'),
            highlightthickness=1,
            highlightbackground=self.theme.get_color('surface')
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Store the avatar image reference
        self.avatar_image = None
        self.photo_image = None
        
        # Initialize mouth region
        self.mouth_region = None
        self.mouth_rect = None
        
        # Bind resize event
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
        # Force update to ensure canvas has proper dimensions
        self.avatar_frame.update_idletasks()
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize event"""
        if self.avatar_image:
            # Update canvas size
            self.width = event.width
            self.height = event.height
            # Redisplay avatar with new dimensions
            self.display_avatar(self.avatar_image)
    
    def display_avatar(self, image_or_openness):
        """Display the avatar image or update mouth animation"""
        try:
            # If we received a mouth openness value (float/int)
            if isinstance(image_or_openness, (float, int)):
                # TODO: Update mouth animation
                return True
                
            # Handle both file paths and PIL Image objects
            if isinstance(image_or_openness, str):
                # Load image from file path
                self.avatar_image = Image.open(image_or_openness)
            else:
                # Use the provided PIL Image object
                self.avatar_image = image_or_openness
            
            # Get current canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 0 or canvas_height <= 0:
                # Use default dimensions if canvas size is not yet determined
                canvas_width = self.width
                canvas_height = self.height
            
            # Calculate scaling factor while maintaining aspect ratio
            width_ratio = canvas_width / self.avatar_image.width
            height_ratio = canvas_height / self.avatar_image.height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = int(self.avatar_image.width * scale_factor)
            new_height = int(self.avatar_image.height * scale_factor)
            
            # Resize image
            resized_image = self.avatar_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # Convert to PhotoImage and store reference
            self.photo_image = ImageTk.PhotoImage(resized_image)
            
            # Calculate center position
            x = canvas_width // 2
            y = canvas_height // 2
            
            # Clear previous image and display new one
            self.canvas.delete("all")
            self.canvas.create_image(
                x, y,
                anchor=tk.CENTER,
                image=self.photo_image,
                tags="avatar"
            )
            
            return True
            
        except Exception as e:
            print(f"Error displaying avatar: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_mouth_region(self, x1, y1, x2, y2):
        """Set the mouth region for lip sync"""
        if self.mouth_rect:
            self.canvas.delete(self.mouth_rect)
        
        # Store the mouth region coordinates
        self.mouth_region = (x1, y1, x2, y2)
        
        # Draw rectangle around mouth region
        self.mouth_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=self.theme.get_color('foreground'),
            width=2
        )
    
    def get_mouth_region(self):
        """Get the current mouth region coordinates"""
        return self.mouth_region
    
    def clear(self):
        """Clear the avatar display"""
        self.canvas.delete("all")
        self.avatar_image = None
        self.photo_image = None
        self.mouth_region = None
        self.mouth_rect = None
    
    def show(self):
        """Show the avatar zone"""
        self.avatar_frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide the avatar zone"""
        self.avatar_frame.pack_forget()
    
    def update_title(self, text):
        """Update the title text"""
        self.title.config(text=text)
    
    def resize(self, width, height):
        """Resize the avatar zone"""
        self.width = width
        self.height = height
        self.canvas.configure(width=width, height=height)
        if self.avatar_image:
            self.display_avatar(self.avatar_image) 