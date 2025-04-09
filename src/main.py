import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD
from PIL import ImageTk, Image, ImageDraw

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
        
        # Create avatar zone with specific dimensions
        self.avatar_zone = AvatarZone(self.container, width=600, height=400)
        
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
        new_width = min(event.width - 40, 600)  # Max width of 600, with 20px padding on each side
        new_height = min(event.height - 200, 400)  # Leave space for controls and status bar
        
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
        
        # Get the processed image
        processed_image = self.image_processor.get_current_frame(mouth_openness)
        if processed_image:
            # Display the image in the avatar zone
            self.avatar_zone.display_avatar(processed_image)
            
            # Update mouth region if it exists
            mouth_region = self.image_processor.get_mouth_region()
            if mouth_region:
                self.avatar_zone.set_mouth_region(*mouth_region)
    
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
        """Load and process audio file"""
        try:
            filename = os.path.basename(file_path)
            self.status_bar.config(text=f"Loading audio file: {filename}")
            
            # Show loading indicator
            self.audio_dropzone.update_status(f"Loading {filename}...", "#89b4fa")
            
            # Process the audio file
            if not self.audio_processor.load_audio(file_path):
                raise Exception("Failed to load audio file")
            
            if not self.audio_processor.sample_rate:
                raise Exception("Invalid sample rate")
            
            # Process audio for lip sync
            if not self.lipsync_processor.process_audio(self.audio_processor.audio_data, self.audio_processor.sample_rate):
                raise Exception("Failed to process audio for lip sync")
            
            # Hide drop zone and show playback controls
            self.audio_dropzone.hide()
            self.playback_controls.show()
            
            # Update waveform display
            self.playback_controls.update_waveform(
                self.audio_processor.audio_data,
                self.audio_processor.current_playback_time,
                self.audio_processor.audio_duration
            )
            
            # Update time display
            self.playback_controls.update_time(
                self.audio_processor.current_playback_time,
                self.audio_processor.audio_duration
            )
            
            # Start lip sync processing
            self.lipsync_processor.start_processing(
                on_update=self.update_lipsync,
                on_complete=self.handle_playback_complete
            )
            
            # Start playback
            self.audio_processor.start_playback()
            self.playback_controls.set_playing(True)
            
            self.status_bar.config(text="Audio loaded successfully")
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            self.status_bar.config(text=f"Error: {str(e)}")
            self.audio_dropzone.update_status("Error processing audio", "#ff5555")
    
    def toggle_playback(self):
        """Toggle between play and pause"""
        if self.audio_processor.is_playing:
            self.audio_processor.stop_playback()
            self.lipsync_processor.stop_processing()
            self.playback_controls.set_playing(False)
        else:
            self.audio_processor.start_playback(self.audio_processor.current_playback_time)
            self.lipsync_processor.start_processing(
                on_update=self.update_lipsync,
                on_complete=self.handle_playback_complete
            )
            self.playback_controls.set_playing(True)
    
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

def main():
    root = TkinterDnD.Tk()
    app = AvatarLipSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 