import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD
from PIL import ImageTk, Image, ImageDraw
import pygame
import atexit

from ui.modern_button import ModernButton
from ui.audio_dropzone import AudioDropZone
from ui.playback_controls import PlaybackControls
from ui.avatar_zone import AvatarZone
from image.image_processor import ImageProcessor
from audio.audio_processor import AudioProcessor
from lipsync.lipsync_processor import LipSyncProcessor

class AvatarLipSyncApp:
    def __init__(self, root):
        self.root = root
        self.is_closing = False  # Add flag to track closing state
        
        self.root.title("Avatar Lip Sync App")
        self.root.geometry("700x800")
        self.root.configure(bg="#1e1e2e")
        
        # Set application icon
        self.set_app_icon()
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#f8f8f2", font=("Helvetica", 10))
        
        # Initialize processors
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.lipsync_processor = LipSyncProcessor()
        
        # Create main container with padding
        self.container = ttk.Frame(self.root, padding="20")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create avatar zone with reduced dimensions
        self.avatar_zone = AvatarZone(self.container, width=350, height=450)  # Adjusted for portrait orientation
        
        # Create the control panel below the avatar
        self.control_frame = ttk.Frame(self.container)
        self.control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create audio drop zone
        self.audio_dropzone = AudioDropZone(
            self.control_frame,
            on_drop=self.handle_audio_drop,
            on_click=self.load_audio
        )
        
        # Create playback controls
        self.playback_controls = PlaybackControls(
            self.control_frame,
            on_play_pause=self.toggle_playback,
            on_seek=self.seek_audio
        )
        
        # Status bar with modern style
        self.status_frame = tk.Frame(self.root, bg="#313244", height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar = ttk.Label(self.status_frame, text="Ready", background="#313244")
        self.status_bar.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Bind events
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.after(100, self.on_window_loaded)  # Wait for window to be fully loaded
        
        # Register cleanup function
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup_resources)
    
    def set_app_icon(self):
        """Set a custom icon for the application that works across platforms"""
        try:
            # Get absolute path to the icon file
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(current_dir, "resources", "app_icon.ico")
            
            # Create icon if it doesn't exist
            if not os.path.exists(icon_path):
                if not self.create_app_icon(icon_path):
                    print(f"Failed to create icon at {icon_path}")
                    return
            
            # Verify the file exists and is readable
            if not os.path.isfile(icon_path):
                print(f"Icon file not found at {icon_path}")
                return
                
            if not os.access(icon_path, os.R_OK):
                print(f"Icon file not readable at {icon_path}")
                return
            
            try:
                # Load and convert the icon
                with Image.open(icon_path) as ico:
                    # Convert to RGBA if needed
                    if ico.mode != 'RGBA':
                        ico = ico.convert('RGBA')
                    
                    # Get the size of the icon
                    size = ico.size[0]  # Icons are square, so width = height
                    
                    # If the icon is too small, resize it up to 32x32
                    if size < 32:
                        ico = ico.resize((32, 32), Image.Resampling.LANCZOS)
                    # If the icon is too large, resize it down to 64x64
                    elif size > 64:
                        ico = ico.resize((64, 64), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage and set
                    photo = ImageTk.PhotoImage(ico)
                    self.root.tk.call('wm', 'iconphoto', self.root._w, photo)
            except Exception as e:
                print(f"Error converting icon: {e}")
                # Fallback to creating a simple icon
                self.create_and_set_simple_icon()
            
        except Exception as e:
            print(f"Error setting app icon: {e}")
            print(f"Attempted icon path: {icon_path}")
            # Fallback to creating a simple icon
            self.create_and_set_simple_icon()
    
    def create_and_set_simple_icon(self):
        """Create and set a simple icon as fallback"""
        try:
            # Create a simple colored square as icon
            icon_size = 32
            icon = Image.new('RGBA', (icon_size, icon_size), "#1e1e2e")
            draw = ImageDraw.Draw(icon)
            
            # Draw a simple avatar-like circle
            margin = 2
            draw.ellipse(
                [margin, margin, icon_size - margin, icon_size - margin],
                fill="#cba6f7"
            )
            
            # Convert to PhotoImage and set
            photo = ImageTk.PhotoImage(icon)
            self.root.tk.call('wm', 'iconphoto', self.root._w, photo)
            
        except Exception as e:
            print(f"Error creating fallback icon: {e}")
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only resize if the window size has changed significantly
        if hasattr(self, 'last_width') and hasattr(self, 'last_height'):
            if abs(self.last_width - event.width) < 10 and abs(self.last_height - event.height) < 10:
                return
        
        self.last_width = event.width
        self.last_height = event.height
        
        # Calculate new avatar dimensions based on window size
        new_width = min(event.width - 40, 450)  # Max width of 450, with 20px padding on each side
        new_height = min(event.height - 200, 350)  # Leave space for controls and status bar
        
        # Update avatar zone size
        self.avatar_zone.resize(new_width, new_height)
        
        # Update the avatar display
        if self.image_processor.has_image():
            self.display_avatar()
    
    def on_window_loaded(self):
        """Called after the window is fully loaded"""
        # Force an update to ensure widgets are properly sized
        self.root.update_idletasks()
        
        # Load initial avatar
        self.load_avatar_image("resources/female_avatar.png")
        
        # Setup audio processor callbacks
        self.audio_processor.set_callbacks(
            on_playback_update=self.update_playback,
            on_playback_complete=self.handle_playback_complete
        )
    
    def load_avatar_image(self, image_path):
        """Load the avatar image"""
        try:
            # Process the image
            if self.image_processor.load_image(image_path):
                self.display_avatar()
                return True
            return False
        except Exception as e:
            print(f"Error loading avatar image: {e}")
            return False
    
    def display_avatar(self, mouth_openness=0):
        """Display the avatar with optional mouth animation"""
        if not self.image_processor.has_image():
            return
        
        # Get the processed image with mouth animation
        processed_image = self.image_processor.get_current_frame(mouth_openness)
        if processed_image:
            # Display the image in the avatar zone
            if self.avatar_zone.display_avatar(processed_image):
                # Update mouth region after successful display
                # This ensures the region is properly scaled to the displayed image size
                canvas_width = self.avatar_zone.canvas.winfo_width()
                canvas_height = self.avatar_zone.canvas.winfo_height()
                
                if canvas_width > 0 and canvas_height > 0:
                    # Get the displayed image position and size
                    image_id = self.avatar_zone.canvas.find_withtag("avatar")
                    if image_id:
                        bbox = self.avatar_zone.canvas.bbox(image_id[0])
                        if bbox:
                            img_x, img_y, img_x2, img_y2 = bbox
                            img_width = img_x2 - img_x
                            img_height = img_y2 - img_y
                            
                            # Calculate mouth region relative to displayed image
                            mouth_region = self.image_processor.get_mouth_region()
                            if mouth_region:
                                orig_x1, orig_y1, orig_x2, orig_y2 = mouth_region
                                
                                # Scale mouth region to match displayed image size
                                scale_x = img_width / processed_image.width
                                scale_y = img_height / processed_image.height
                                
                                x1 = img_x + orig_x1 * scale_x
                                y1 = img_y + orig_y1 * scale_y
                                x2 = img_x + orig_x2 * scale_x
                                y2 = img_y + orig_y2 * scale_y
                                
                                # Update mouth region in avatar zone
                                self.avatar_zone.set_mouth_region(x1, y1, x2, y2)
    
    def handle_audio_drop(self, file_path):
        """Handle dropped audio file"""
        # Remove curly braces if present (Windows drag and drop)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        # Check if it's a valid audio file
        if os.path.isfile(file_path) and file_path.lower().endswith(('.wav', '.mp3', '.ogg')):
            self.load_audio_file(file_path)
        else:
            self.status_bar.config(text="Please drop a valid audio file (.wav, .mp3, .ogg)")
    
    def load_audio(self):
        """Load audio file through file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=(("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*"))
        )
        
        if file_path:
            self.load_audio_file(file_path)
    
    def load_audio_file(self, file_path):
        """Load and process an audio file"""
        try:
            # Update UI to show loading state
            self.status_bar.config(text="Loading audio file...")
            self.audio_dropzone.update_status("Loading audio file...", color="#89b4fa")
            self.root.update()  # Force UI update
            
            # Load the audio file
            if not self.audio_processor.load_audio(file_path):
                raise Exception("Failed to load audio file")
            
            # Update UI with success state
            filename = os.path.basename(file_path)
            self.status_bar.config(text=f"Loaded: {filename}")
            
            # Hide dropzone and show success message briefly before hiding
            self.audio_dropzone.update_status(f"Loaded: {filename}", color="#a6e3a1")  # Green success color
            self.root.after(1000, self.audio_dropzone.hide)  # Hide after 1 second
            
            # Show playback controls
            self.playback_controls.show()
            
            # Update waveform display
            self.playback_controls.update_waveform(
                self.audio_processor.audio_data,
                0,
                self.audio_processor.audio_duration
            )
            
            # Update time display
            self.playback_controls.update_time(0, self.audio_processor.audio_duration)
            
            return True
            
        except Exception as e:
            # Update UI with error state
            error_msg = f"Error loading audio: {str(e)}"
            self.status_bar.config(text=error_msg)
            self.audio_dropzone.update_status("Failed to load audio file", color="#f38ba8")  # Red error color
            print(error_msg)
            return False
    
    def toggle_playback(self):
        """Toggle between play and pause"""
        if self.audio_processor.is_playing:
            self.audio_processor.stop_playback()
            self.playback_controls.set_playing(False)
        else:
            # Start playback from current position
            if self.audio_processor.start_playback(self.audio_processor.current_playback_time):
                self.playback_controls.set_playing(True)
            else:
                self.status_bar.config(text="Error starting playback")
                self.playback_controls.set_playing(False)
    
    def seek_audio(self, position):
        """Seek to a position in the audio"""
        if self.audio_processor.seek_to(position):
            self.lipsync_processor.seek_to(position)
            self.playback_controls.update_time(
                self.audio_processor.current_playback_time,
                self.audio_processor.audio_duration
            )
    
    def update_playback(self, current_time, frame):
        """Update UI during playback"""
        # Update time display
        self.playback_controls.update_time(current_time, self.audio_processor.audio_duration)
        
        # Update waveform
        self.playback_controls.update_waveform(
            self.audio_processor.audio_data,
            current_time,
            self.audio_processor.audio_duration
        )
        
        # Update avatar mouth
        mouth_openness = self.audio_processor.get_current_mouth_openness()
        self.display_avatar(mouth_openness)
    
    def handle_playback_complete(self):
        """Handle playback completion"""
        self.playback_controls.set_playing(False)
        self.playback_controls.update_time(0, self.audio_processor.audio_duration)
        self.display_avatar(0)
    
    def update_lipsync(self, current_time, mouth_openness):
        """Update avatar mouth shape based on lip sync data"""
        # Update avatar mouth
        self.display_avatar(mouth_openness)
        
        # Update playback controls
        self.playback_controls.update_time(current_time, self.audio_processor.audio_duration)
        self.playback_controls.update_waveform(
            self.audio_processor.audio_data,
            current_time,
            self.audio_processor.audio_duration
        )
    
    def on_closing(self):
        """Handle window closing event"""
        if self.is_closing:  # Prevent multiple cleanup attempts
            return
            
        self.is_closing = True
        
        try:
            # Stop audio playback first
            if hasattr(self, 'audio_processor'):
                try:
                    self.audio_processor.stop_playback()
                except Exception as e:
                    print(f"Error stopping audio playback: {e}")
            
            # Clean up Pygame
            try:
                pygame.mixer.quit()
                pygame.quit()
            except Exception as e:
                print(f"Error cleaning up Pygame: {e}")
            
            # Clean up Tkinter last
            try:
                self.root.quit()
            except Exception as e:
                print(f"Error during Tkinter cleanup: {e}")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            try:
                self.root.destroy()
            except Exception as e:
                print(f"Error destroying window: {e}")
    
    def cleanup_resources(self):
        """Cleanup callback for atexit"""
        if not self.is_closing:  # Only cleanup if not already closing
            self.on_closing()

def main():
    root = TkinterDnD.Tk()
    app = AvatarLipSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 