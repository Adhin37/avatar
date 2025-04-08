import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import numpy as np
import pygame
import librosa
import pyaudio
import sounddevice as sd
import soundfile as sf
import time
from PIL import Image, ImageTk, ImageDraw
import math
import random

class AvatarLipSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Avatar Lip Sync App")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2e")
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", background="#7f849c", foreground="#f8f8f2", font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("TButton", background=[("active", "#89b4fa")])
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#f8f8f2", font=("Helvetica", 10))
        
        # Initialize variables
        self.avatar_image = None
        self.mouth_region = None  # Coordinates of mouth area (x1, y1, x2, y2)
        self.mouth_frames = []    # Different mouth positions for animation
        self.audio_file = None
        self.is_playing = False
        self.phonemes = []
        self.current_frame = 0
        self.audio_data = None
        self.audio_duration = 0
        self.current_playback_time = 0
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create the avatar display area
        self.avatar_frame = ttk.Frame(self.main_frame, width=1000, height=600)
        self.avatar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for the 2D image
        self.image_frame = tk.Frame(self.avatar_frame, width=1000, height=600, bg="#11111b")
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create label to display the avatar
        self.avatar_label = tk.Label(self.image_frame, bg="#11111b")
        self.avatar_label.pack(fill=tk.BOTH, expand=True)
        
        # Create the control panel below the avatar
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create initial audio selection area (dropzone)
        self.create_audio_dropzone()
        
        # Create the playback controls (initially hidden)
        self.create_playback_controls()
        self.hide_playback_controls()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize recording variables
        self.audio_frames = []
        self.stream = None
        self.p = pyaudio.PyAudio()
        
        # Load the avatar image
        self.load_avatar_image("resources/female_avatar.png")  # Update with your image path
        
        # Generate mouth frames for animation
        self.generate_mouth_frames()
        
    def load_avatar_image(self, image_path):
        """Load the avatar image from file"""
        try:
            # If no path provided, try to use the image from the resources
            if not os.path.exists(image_path):
                # Fallback to sample path or use default
                default_paths = ["resources/female_avatar.png", "female_avatar.png", "avatar.png"]
                for path in default_paths:
                    if os.path.exists(path):
                        image_path = path
                        break
                else:
                    self.status_bar.config(text="Error: Avatar image not found, please select one")
                    self.select_avatar_image()
                    return
            
            # Load and resize the image to fit the frame
            img = Image.open(image_path)
            
            # Resize maintaining aspect ratio
            display_width = 800
            width_percent = (display_width / float(img.size[0]))
            display_height = int((float(img.size[1]) * float(width_percent)))
            
            self.original_avatar = img.copy()
            self.avatar_image = img.resize((display_width, display_height), Image.LANCZOS)
            
            # Define mouth region (adjust these values based on your image)
            # Format: (x1, y1, x2, y2) as proportions of image width/height
            # These values need to be adjusted based on your specific avatar image
            mouth_x_center = display_width * 0.5  # Center of image horizontally
            mouth_y_position = display_height * 0.58  # Lower middle area of face
            mouth_width = display_width * 0.15
            mouth_height = display_height * 0.05
            
            self.mouth_region = (
                int(mouth_x_center - mouth_width/2),  # x1
                int(mouth_y_position - mouth_height/2),  # y1
                int(mouth_x_center + mouth_width/2),  # x2
                int(mouth_y_position + mouth_height/2)   # y2
            )
            
            # Display the image
            self.display_avatar(self.avatar_image)
            self.status_bar.config(text="Avatar image loaded successfully")
            
        except Exception as e:
            self.status_bar.config(text=f"Error loading avatar image: {e}")
            print(f"Error loading avatar image: {e}")
    
    def select_avatar_image(self):
        """Allow user to select an avatar image"""
        file_path = filedialog.askopenfilename(
            title="Select Avatar Image",
            filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*"))
        )
        
        if file_path:
            self.load_avatar_image(file_path)
    
    def display_avatar(self, img, mouth_openness=0):
        """Display the avatar image with current mouth state"""
        display_img = img.copy()
        
        # If we have mouth animation data, apply it
        if mouth_openness > 0 and hasattr(self, 'mouth_frames') and len(self.mouth_frames) > 0:
            # Select appropriate mouth frame based on openness
            frame_index = min(len(self.mouth_frames)-1, int(mouth_openness * len(self.mouth_frames) / 30))
            
            if frame_index >= 0 and frame_index < len(self.mouth_frames):
                mouth_frame = self.mouth_frames[frame_index]
                
                # Paste the mouth frame onto the avatar image
                x1, y1, x2, y2 = self.mouth_region
                display_img.paste(mouth_frame, (x1, y1, x2, y2), mouth_frame)
        
        # Convert to PhotoImage and display
        photo = ImageTk.PhotoImage(display_img)
        self.avatar_label.config(image=photo)
        self.avatar_label.image = photo  # Keep reference to prevent garbage collection
    
    def generate_mouth_frames(self):
        """Generate different mouth shapes for animation"""
        if not self.avatar_image or not self.mouth_region:
            return
            
        x1, y1, x2, y2 = self.mouth_region
        mouth_width = x2 - x1
        mouth_height = y2 - y1
        
        # Create a series of mouth shapes with different openness levels
        num_frames = 8  # Number of different mouth positions
        self.mouth_frames = []
        
        for i in range(num_frames):
            # Create a transparent image for the mouth
            mouth_img = Image.new('RGBA', (mouth_width, mouth_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(mouth_img)
            
            # Calculate openness based on frame index
            openness = i / (num_frames - 1)
            
            # Extract lip color from the original image (approximate)
            lip_color = (208, 108, 103, 255)  # Pink-ish color for lips
            
            # Draw upper lip (fixed)
            upper_lip_height = int(mouth_height * 0.4)
            draw.ellipse((0, 0, mouth_width, upper_lip_height*2), fill=lip_color)
            
            # Draw lower lip with varying openness
            lower_lip_y = int(mouth_height * (0.5 + 0.25 * openness))
            lower_lip_height = int(mouth_height * 0.4)
            draw.ellipse((0, lower_lip_y-lower_lip_height, mouth_width, lower_lip_y+lower_lip_height), fill=lip_color)
            
            # If mouth is open, draw black inside
            if openness > 0.1:
                inner_mouth_height = int(mouth_height * openness * 0.8)
                inner_mouth_y = int(mouth_height * 0.5)
                inner_mouth_width = int(mouth_width * 0.8)
                inner_mouth_x = int(mouth_width * 0.1)
                
                draw.ellipse(
                    (inner_mouth_x, inner_mouth_y-inner_mouth_height//2, 
                     inner_mouth_x+inner_mouth_width, inner_mouth_y+inner_mouth_height//2), 
                    fill=(40, 40, 40, 255)
                )
            
            self.mouth_frames.append(mouth_img)
        
        # Display initial avatar with mouth closed
        self.display_avatar(self.avatar_image)
    
    def create_audio_dropzone(self):
        """Create a dropzone for audio file selection"""
        self.dropzone_frame = ttk.Frame(self.control_frame, height=150)
        self.dropzone_frame.pack(fill=tk.X, pady=20)
        
        # Create a drop zone with border
        self.drop_area = tk.Frame(self.dropzone_frame, bg="#2e2e3e", bd=2, relief=tk.GROOVE)
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # Add label and icon to drop zone
        self.drop_icon = tk.Label(self.drop_area, text="🎵", font=("Helvetica", 24), bg="#2e2e3e", fg="#89b4fa")
        self.drop_icon.pack(pady=(15, 5))
        
        self.drop_label = tk.Label(self.drop_area, 
                                   text="Click here to select an audio file\nor drag and drop", 
                                   font=("Helvetica", 12), 
                                   bg="#2e2e3e", 
                                   fg="#f8f8f2")
        self.drop_label.pack(pady=5)
        
        # Bind click event
        self.drop_area.bind("<Button-1>", self.load_audio)
        self.drop_icon.bind("<Button-1>", self.load_audio)
        self.drop_label.bind("<Button-1>", self.load_audio)
        
    def create_playback_controls(self):
        """Create playback controls that will show after audio is loaded"""
        # Horizontal layout for controls
        self.controls_layout = ttk.Frame(self.control_frame)
        
        # Audio time display (current time)
        self.current_time_var = tk.StringVar(value="0:00")
        self.current_time = ttk.Label(self.controls_layout, textvariable=self.current_time_var)
        self.current_time.pack(side=tk.LEFT, padx=(0, 10))
        
        # Round play/pause button with distinctive colors
        self.play_frame = ttk.Frame(self.controls_layout)
        self.play_frame.pack(side=tk.LEFT, padx=10)
        
        # Create a round play button using Canvas
        self.play_canvas = tk.Canvas(self.play_frame, width=50, height=50, bg="#1e1e2e", highlightthickness=0)
        self.play_canvas.pack()
        
        # Draw circle for play button (initial state)
        self.play_bg_color = "#4CAF50"  # Green for play
        self.pause_bg_color = "#FF5722"  # Orange for pause
        self.play_circle = self.play_canvas.create_oval(5, 5, 45, 45, fill=self.play_bg_color, outline="")
        
        # Draw play triangle initially
        self.play_symbol = self.play_canvas.create_polygon(20, 15, 20, 35, 35, 25, fill="white")
        
        # Bind click event to the canvas
        self.play_canvas.bind("<Button-1>", self.toggle_playback)
        
        # Waveform canvas
        self.waveform_canvas = tk.Canvas(self.controls_layout, height=50, bg="#1e1e2e", highlightthickness=0)
        self.waveform_canvas.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.waveform_canvas.bind("<Button-1>", self.seek_audio)
        
        # Audio time display (total time)
        self.total_time_var = tk.StringVar(value="0:00")
        self.total_time = ttk.Label(self.controls_layout, textvariable=self.total_time_var)
        self.total_time.pack(side=tk.LEFT, padx=10)
        
    def show_playback_controls(self):
        """Show the playback controls"""
        # Hide dropzone
        self.dropzone_frame.pack_forget()
        
        # Show controls
        self.controls_layout.pack(fill=tk.X)
        
    def hide_playback_controls(self):
        """Hide the playback controls"""
        self.controls_layout.pack_forget()
    
    def load_audio(self, event=None):
        """Load an audio file"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=(("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*"))
        )
        
        if file_path:
            self.audio_file = file_path
            filename = os.path.basename(file_path)
            self.status_bar.config(text=f"Loading audio file: {filename}")
            
            # Show loading indicator
            self.drop_label.config(text=f"Loading {filename}...", fg="#89b4fa")
            
            # Process the audio file for lip sync in a separate thread
            threading.Thread(target=self.process_audio_for_lip_sync).start()
    
    def format_time(self, seconds):
        """Format time in minutes:seconds"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def update_waveform_display(self):
        """Draw the audio waveform on the canvas"""
        # Get canvas dimensions
        width = self.waveform_canvas.winfo_width()
        height = self.waveform_canvas.winfo_height()
        
        if width <= 1:  # Canvas not yet realized
            self.root.after(100, self.update_waveform_display)
            return
            
        # Clear current waveform
        self.waveform_canvas.delete("all")
        
        # Draw background
        self.waveform_canvas.create_rectangle(0, 0, width, height, fill="#2e2e3e", outline="")
        
        if self.audio_data is not None and len(self.audio_data) > 0:
            # Calculate waveform data points
            samples_per_pixel = max(1, len(self.audio_data) // width)
            waveform_points = []
            
            for i in range(0, width):
                start = i * samples_per_pixel
                end = min(len(self.audio_data), (i + 1) * samples_per_pixel)
                if start < len(self.audio_data):
                    # Calculate average amplitude for this segment
                    segment = self.audio_data[start:end]
                    if len(segment) > 0:
                        amplitude = np.max(np.abs(segment)) * height / 2
                        # Ensure minimum visibility
                        amplitude = max(2, amplitude)
                        center_y = height / 2
                        waveform_points.append((i, center_y - amplitude, i, center_y + amplitude))
            
            # Draw waveform bars
            for i, (x, y1, x2, y2) in enumerate(waveform_points):
                # Alternate colors for played/unplayed sections
                if self.current_playback_time > 0 and self.audio_duration > 0:
                    progress_x = (self.current_playback_time / self.audio_duration) * width
                    color = "#89b4fa" if x < progress_x else "#7f849c"  # Blue for played, gray for unplayed
                else:
                    color = "#7f849c"
                    
                self.waveform_canvas.create_line(x, y1, x, y2, fill=color, width=1)
            
            # Draw playhead
            if self.current_playback_time > 0 and self.audio_duration > 0:
                playhead_x = (self.current_playback_time / self.audio_duration) * width
                self.waveform_canvas.create_line(playhead_x, 0, playhead_x, height, fill="#ff5555", width=2)
        else:
            # Draw placeholder waveform
            center_y = height / 2
            for i in range(0, width, 3):
                # Generate a random height for the waveform line
                line_height = random.randint(1, 5)
                self.waveform_canvas.create_line(i, center_y - line_height, 
                                             i, center_y + line_height, 
                                             fill="#7f849c", width=1)
    
    def seek_audio(self, event):
        """Seek to a position in the audio when clicking on waveform"""
        if not self.audio_file or not self.phonemes:
            return
            
        # Calculate position
        width = self.waveform_canvas.winfo_width()
        click_position = event.x / width
        
        # Update current playback time
        self.current_playback_time = click_position * self.audio_duration
        
        # If playing, stop and restart from new position
        was_playing = self.is_playing
        if self.is_playing:
            self.stop_playback()
            
        # Calculate frame number
        if len(self.phonemes) > 0:
            self.current_frame = min(len(self.phonemes) - 1, 
                                     int(click_position * len(self.phonemes)))
            
        # Update UI
        self.current_time_var.set(self.format_time(self.current_playback_time))
        self.update_waveform_display()
        
        # Restart playback if it was playing
        if was_playing:
            self.start_playback()
    
    def process_audio_for_lip_sync(self):
        """Process audio to extract phoneme timing for lip sync"""
        try:
            # Load the audio file
            y, sr = librosa.load(self.audio_file)
            
            # Store raw audio data for waveform display
            self.audio_data = y
            self.audio_duration = librosa.get_duration(y=y, sr=sr)
            
            # Update UI elements
            self.root.after(0, lambda: self.total_time_var.set(self.format_time(self.audio_duration)))
            self.root.after(0, lambda: self.current_time_var.set("0:00"))
            
            # Extract audio features for lip sync
            # In a real app, you would use a phoneme detection model
            # For this demo, we'll simulate mouth movement using amplitude
            
            # Get amplitude envelope
            hop_length = 512
            amplitude_envelope = np.array([
                np.max(abs(y[i:i+hop_length])) 
                for i in range(0, len(y), hop_length)
            ])
            
            # Convert to "mouth openness" values
            mouth_values = []
            for amp in amplitude_envelope:
                # Scale amplitude to mouth openness (0-30 pixels)
                mouth_openness = min(30, int(amp * 100))
                mouth_values.append(mouth_openness)
            
            # Store phoneme data
            self.phonemes = mouth_values
            
            # Update UI on the main thread
            self.root.after(0, lambda: self.status_bar.config(text="Lip sync data generated successfully"))
            
            # Show playback controls and hide dropzone
            self.root.after(0, self.show_playback_controls)
            
            # Update waveform before auto-playing
            self.root.after(0, self.update_waveform_display)
            
            # Auto play after processing is complete
            self.root.after(500, self.start_playback)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Error generating lip sync: {e}"))
            
    def toggle_playback(self, event=None):
        """Toggle between play and pause"""
        if not self.audio_file:
            self.status_bar.config(text="Please load an audio file first")
            return
            
        if not self.is_playing:
            self.start_playback()
        else:
            self.stop_playback()
    
    def start_playback(self):
        """Start avatar animation and audio playback"""
        if not self.audio_file or not self.phonemes:
            return
            
        # Start playback
        self.is_playing = True
        
        # Update play button to show pause symbol
        self.play_canvas.delete("all")
        self.play_circle = self.play_canvas.create_oval(5, 5, 45, 45, fill=self.pause_bg_color, outline="")
        
        # Draw pause symbol (two rectangles)
        self.play_canvas.create_rectangle(17, 15, 23, 35, fill="white", outline="")
        self.play_canvas.create_rectangle(27, 15, 33, 35, fill="white", outline="")
        
        # Start animation and audio playback thread
        threading.Thread(target=self.animate_avatar).start()
    
    def stop_playback(self):
        """Stop avatar animation and audio playback"""
        # Stop playback
        self.is_playing = False
        
        # Update pause button to show play symbol
        self.play_canvas.delete("all")
        self.play_circle = self.play_canvas.create_oval(5, 5, 45, 45, fill=self.play_bg_color, outline="")
        self.play_symbol = self.play_canvas.create_polygon(20, 15, 20, 35, 35, 25, fill="white")
        
        # Stop audio
        sd.stop()
            
    def animate_avatar(self):
        """Animate the avatar based on phoneme data and play audio"""
        try:
            # Get current position in the audio file
            start_time = 0
            if self.current_playback_time > 0:
                start_time = self.current_playback_time
                
            # Load audio data
            data, fs = sf.read(self.audio_file, dtype='float32')
            
            # Calculate starting sample
            start_sample = int(start_time * fs)
            
            # Play audio from the current position
            if start_sample < len(data):
                sd.play(data[start_sample:], fs)
            
            # Frame timing and starting position
            frame_duration = 0.0512  # seconds (based on hop_length/sr)
            
            # Set starting frame based on current playback time
            if self.current_playback_time > 0 and self.audio_duration > 0:
                self.current_frame = min(len(self.phonemes) - 1, 
                                      int((self.current_playback_time / self.audio_duration) * len(self.phonemes)))
            else:
                self.current_frame = 0
                
            total_frames = len(self.phonemes)
            start_time = time.time() - start_time
            
            # Animate mouth with the audio
            while self.is_playing and self.current_frame < total_frames:
                # Calculate current playback time
                self.current_playback_time = min(self.audio_duration, time.time() - start_time)
                
                # Update UI elements
                self.root.after(0, lambda t=self.current_playback_time: 
                              self.current_time_var.set(self.format_time(t)))
                
                # Update mouth shape based on current phoneme
                mouth_openness = self.phonemes[self.current_frame]
                
                # Update on main thread
                self.root.after(0, lambda o=mouth_openness: self.display_avatar(self.avatar_image, o))
                
                # Update waveform (less frequently to avoid UI lag)
                if self.current_frame % 5 == 0:
                    self.root.after(0, self.update_waveform_display)
                
                # Wait for next frame
                time.sleep(frame_duration)
                self.current_frame += 1
                
            # Reset when done
            if self.current_frame >= total_frames:
                self.is_playing = False
                self.current_playback_time = 0
                self.root.after(0, lambda: self.current_time_var.set("0:00"))
                self.root.after(0, self.stop_playback)
                self.root.after(0, lambda: self.display_avatar(self.avatar_image, 0))
                self.root.after(0, self.update_waveform_display)
                
            # Stop audio
            sd.stop()
                
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Error during playback: {e}"))
            self.is_playing = False
            self.root.after(0, self.stop_playback)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = AvatarLipSyncApp(root)
    root.mainloop()