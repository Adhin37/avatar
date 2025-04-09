import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD
from PIL import ImageTk, Image, ImageDraw

from ui.modern_button import ModernButton
from ui.audio_dropzone import AudioDropZone
from ui.playback_controls import PlaybackControls
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
        
        # Create title
        title_frame = ttk.Frame(self.container)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        title_label = ttk.Label(title_frame, text="Avatar Lip Sync", 
                              font=("Helvetica", 24, "bold"), foreground="#cba6f7")
        title_label.pack()
        
        # Create the avatar display area with modern border
        self.avatar_frame = tk.Frame(self.container, bg="#313244", bd=2)
        self.avatar_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create a frame for the 2D image with fixed height
        self.image_frame = tk.Frame(self.avatar_frame, width=400, height=400, bg="#1e1e2e")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.image_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Create label to display the avatar
        self.avatar_label = tk.Label(self.image_frame, bg="#1e1e2e")
        self.avatar_label.pack(fill=tk.BOTH, expand=True)
        
        # Create the control panel below the avatar
        self.control_frame = ttk.Frame(self.container)
        self.control_frame.pack(fill=tk.X)
        
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
        """Set a custom icon for the application"""
        try:
            # Create a simple icon if the file doesn't exist
            icon_path = "resources/app_icon.ico"
            if not os.path.exists(icon_path):
                self.create_app_icon(icon_path)
            
            # Set the icon
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting app icon: {e}")
    
    def create_app_icon(self, icon_path):
        """Create a custom app icon that matches the application theme"""
        try:
            # Create resources directory if it doesn't exist
            os.makedirs(os.path.dirname(icon_path), exist_ok=True)
            
            # Create a high-resolution icon (will be scaled down for ICO)
            icon_size = 256
            icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # Colors from our app theme
            bg_color = "#1e1e2e"
            accent_color = "#cba6f7"
            highlight_color = "#f8f8f2"
            
            # Draw circular background
            draw.ellipse((0, 0, icon_size, icon_size), fill=bg_color)
            
            # Draw stylized avatar face (outer circle)
            margin = icon_size * 0.1
            draw.ellipse(
                (margin, margin, icon_size - margin, icon_size - margin),
                fill=accent_color
            )
            
            # Draw avatar features
            face_color = "#FFE4E1"  # Soft skin tone
            hair_color = "#8B0000"  # Dark red for hair
            
            # Face
            face_margin = icon_size * 0.15
            draw.ellipse(
                (face_margin, face_margin, icon_size - face_margin, icon_size - face_margin),
                fill=face_color
            )
            
            # Hair (stylized curves)
            hair_points = [
                (icon_size * 0.2, icon_size * 0.3),  # Start left
                (icon_size * 0.1, icon_size * 0.5),  # Left curve
                (icon_size * 0.15, icon_size * 0.7),
                (icon_size * 0.3, icon_size * 0.85),
                (icon_size * 0.7, icon_size * 0.85),
                (icon_size * 0.85, icon_size * 0.7),
                (icon_size * 0.9, icon_size * 0.5),  # Right curve
                (icon_size * 0.8, icon_size * 0.3),  # End right
            ]
            draw.polygon(hair_points, fill=hair_color)
            
            # Draw mouth
            mouth_width = icon_size * 0.4
            mouth_height = icon_size * 0.15
            mouth_x = (icon_size - mouth_width) / 2
            mouth_y = icon_size * 0.6
            
            # Lips
            lip_color = "#CD5C5C"  # Indian red
            draw.ellipse(
                (mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_height),
                fill=lip_color
            )
            
            # Sound wave lines (indicating audio/lip sync)
            wave_color = highlight_color
            wave_thickness = 3
            wave_spacing = 8
            wave_width = icon_size * 0.3
            wave_x = (icon_size - wave_width) / 2
            wave_y = icon_size * 0.8
            
            for i in range(3):
                y_offset = i * wave_spacing
                # Draw sound wave lines
                draw.line(
                    (wave_x, wave_y + y_offset,
                     wave_x + wave_width * 0.3, wave_y - wave_spacing + y_offset,
                     wave_x + wave_width * 0.7, wave_y + wave_spacing + y_offset,
                     wave_x + wave_width, wave_y + y_offset),
                    fill=wave_color,
                    width=wave_thickness
                )
            
            # Resize to standard icon sizes
            icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            icons = []
            for size in icon_sizes:
                icons.append(icon.resize(size, Image.LANCZOS))
            
            # Save as ICO with multiple sizes
            icons[0].save(
                icon_path,
                format='ICO',
                sizes=icon_sizes,
                optimize=True
            )
            
            return True
        except Exception as e:
            print(f"Error creating app icon: {e}")
            return False
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only resize if the window size has changed significantly
        if hasattr(self, 'last_width') and hasattr(self, 'last_height'):
            if abs(self.last_width - event.width) < 10 and abs(self.last_height - event.height) < 10:
                return
        
        self.last_width = event.width
        self.last_height = event.height
        
        # Resize the avatar image
        if hasattr(self, 'image_frame'):
            width = self.image_frame.winfo_width()
            height = self.image_frame.winfo_height()
            if width > 10 and height > 10:  # Ensure valid dimensions
                self.image_processor.resize_image(width, height)
                self.display_avatar()
    
    def on_window_loaded(self):
        """Called after the window is fully loaded"""
        # Force an update to ensure widgets are properly sized
        self.root.update_idletasks()
        
        # Load initial avatar and automatically remove background
        self.load_avatar_image("resources/female_avatar.png")
        
        # Setup audio processor callbacks
        self.audio_processor.set_callbacks(
            on_playback_update=self.update_playback,
            on_playback_complete=self.handle_playback_complete
        )
        
        # Force initial resize to ensure proper layout
        width = self.image_frame.winfo_width()
        height = self.image_frame.winfo_height()
        if width > 10 and height > 10:
            self.image_processor.resize_image(width, height)
            self.display_avatar()
    
    def load_avatar_image(self, image_path):
        """Load and display the avatar image"""
        if self.image_processor.load_image(image_path):
            # Automatically remove background
            self.image_processor.remove_background()
            
            # Resize the image to fit the frame
            width = self.image_frame.winfo_width()
            height = self.image_frame.winfo_height()
            if width > 10 and height > 10:  # Ensure valid dimensions
                self.image_processor.resize_image(width, height)
            
            self.display_avatar()
            self.status_bar.config(text="Avatar image loaded successfully")
        else:
            self.status_bar.config(text="Error loading avatar image")
    
    def display_avatar(self, mouth_openness=0):
        """Display the avatar with current mouth state"""
        try:
            display_img = self.image_processor.apply_mouth_frame(mouth_openness)
            if display_img:
                # Get the current frame size
                frame_width = self.image_frame.winfo_width()
                frame_height = self.image_frame.winfo_height()
                
                # Ensure we have valid dimensions
                if frame_width <= 1 or frame_height <= 1:
                    frame_width = 400
                    frame_height = 400
                
                # Create a PhotoImage from the display image
                photo = ImageTk.PhotoImage(display_img)
                
                # Update the avatar label
                self.avatar_label.config(image=photo)
                self.avatar_label.image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            print(f"Error displaying avatar: {e}")
            # Try to display the original image without mouth frame
            try:
                if self.image_processor.processed_image:
                    photo = ImageTk.PhotoImage(self.image_processor.processed_image)
                    self.avatar_label.config(image=photo)
                    self.avatar_label.image = photo
            except Exception as e2:
                print(f"Error displaying fallback image: {e2}")
    
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