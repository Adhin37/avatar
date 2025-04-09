import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class AvatarZone:
    def __init__(self, parent, width=300, height=400):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Create main frame for avatar
        self.avatar_frame = ttk.Frame(parent)
        self.avatar_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure style for the frame
        style = ttk.Style()
        style.configure('Avatar.TFrame', background='#1e1e2e')
        self.avatar_frame.configure(style='Avatar.TFrame')
        
        # Add title at the top
        self.title = ttk.Label(
            self.avatar_frame,
            text="Avatar Lip Sync",
            font=("Helvetica", 24, "bold"),
            foreground="#cba6f7",
            style='Avatar.TLabel'
        )
        style.configure('Avatar.TLabel', background='#1e1e2e')
        self.title.pack(pady=(0, 10))
        
        # Create canvas for avatar display with fixed dimensions
        self.canvas = tk.Canvas(
            self.avatar_frame,
            width=width,
            height=height,
            bg="#1e1e2e",
            highlightthickness=1,
            highlightbackground="#3e3e4e"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Store the avatar image reference
        self.avatar_image = None
        self.photo_image = None
        
        # Initialize mouth region
        self.mouth_region = None
        self.mouth_rect = None
        
        # Force update to ensure canvas has proper dimensions
        self.avatar_frame.update_idletasks()
    
    def display_avatar(self, image_or_openness):
        """Display the avatar image or update mouth animation
        
        Args:
            image_or_openness: Either a PIL Image object for initial display,
                             or a float value (0-1) for mouth animation
        """
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
            
            print(f"Canvas dimensions: {canvas_width}x{canvas_height}")
            print(f"Image dimensions: {self.avatar_image.width}x{self.avatar_image.height}")
            
            if canvas_width > 0 and canvas_height > 0:
                # Calculate scaling factor to fit height while maintaining aspect ratio
                height_ratio = canvas_height / self.avatar_image.height
                new_width = int(self.avatar_image.width * height_ratio)
                new_height = canvas_height
                
                # If new width is too wide, scale down based on width
                if new_width > canvas_width:
                    width_ratio = canvas_width / self.avatar_image.width
                    new_width = canvas_width
                    new_height = int(self.avatar_image.height * width_ratio)
                
                print(f"Resizing to: {new_width}x{new_height}")
                
                # Resize image
                resized_image = self.avatar_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage and store reference
                self.photo_image = ImageTk.PhotoImage(resized_image)
                
                # Calculate position to center the image
                x = canvas_width // 2
                y = canvas_height // 2
                
                # Clear previous image and display new one
                self.canvas.delete("all")
                self.canvas.create_image(x, y, anchor=tk.CENTER, image=self.photo_image, tags="avatar")
                
                print(f"Image placed at center point: ({x}, {y})")
                
                # Reset mouth region
                self.mouth_region = None
                self.mouth_rect = None
                
                return True
            
            return False
            
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
            outline="#cba6f7",
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
        self.avatar_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
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
        
        # Update canvas size
        self.canvas.configure(width=width, height=height)
        
        # Redisplay avatar if one is loaded
        if self.avatar_image:
            self.display_avatar(self.avatar_image) 