import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import numpy as np
import pygame
import librosa
import wave
import pyaudio
import sounddevice as sd
import soundfile as sf
import time
from PIL import Image, ImageTk
import math
import random

# For 3D mesh handling
import trimesh
import moderngl
from pyrr import Matrix44
import glfw
import numpy as np

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
        self.avatar_model = None
        self.mesh_vertices = None
        self.mesh_indices = None
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
        
        # Create a placeholder for the 3D rendering window
        self.render_frame = tk.Frame(self.avatar_frame, width=1000, height=600, bg="#11111b")
        self.render_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the control panel below the 3D model (initially hidden)
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
        
        # Initialize OpenGL context
        self.ctx = None
        self.prog = None
        self.vao = None
        self.init_gl()
        
        # Load the 3D model directly from the resources folder
        self.load_model_from_path("resources/female_head.obj")
        
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
        
    def init_gl(self):
        """Initialize OpenGL for 3D rendering"""
        # Initialize GLFW
        if not glfw.init():
            print("Failed to initialize GLFW")
            return
            
        # Create a hidden window for OpenGL context
        glfw.window_hint(glfw.VISIBLE, False)
        self.gl_window = glfw.create_window(800, 600, "Hidden Window", None, None)
        if not self.gl_window:
            glfw.terminate()
            print("Failed to create GLFW window")
            return
            
        glfw.make_context_current(self.gl_window)
        
        # Create ModernGL context
        self.ctx = moderngl.create_context()
        
        # Basic shaders for 3D model rendering
        vertex_shader = '''
            #version 330
            uniform mat4 mvp;
            in vec3 in_position;
            in vec3 in_normal;
            out vec3 v_normal;
            
            void main() {
                gl_Position = mvp * vec4(in_position, 1.0);
                v_normal = in_normal;
            }
        '''
        
        fragment_shader = '''
            #version 330
            in vec3 v_normal;
            out vec4 f_color;
            
            void main() {
                vec3 light = vec3(0.0, 0.0, 1.0);
                float lum = max(dot(normalize(v_normal), normalize(light)), 0.0);
                vec3 color = vec3(0.8, 0.2, 0.2); // Reddish color for red hair
                f_color = vec4(color * (0.25 + 0.75 * lum), 1.0);
            }
        '''
        
        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )
        
        # Setup an offscreen framebuffer for rendering to texture
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((800, 600), 4)]
        )
        
    def load_model_from_path(self, model_path):
        """Load a 3D model file from a specific path"""
        if not os.path.exists(model_path):
            self.status_bar.config(text=f"Error: Model file not found at {model_path}")
            return
        
        try:
            # Load the model using trimesh
            mesh = trimesh.load(model_path)
            self.status_bar.config(text="3D model loaded successfully")
            
            # Extract vertices and faces
            vertices = np.array(mesh.vertices, dtype='f4')
            indices = np.array(mesh.faces, dtype='i4')
            
            # Calculate vertex normals if not available
            if not hasattr(mesh, 'vertex_normals') or mesh.vertex_normals is None:
                mesh.vertex_normals = np.zeros_like(mesh.vertices)
                for face in mesh.faces:
                    normal = np.cross(
                        mesh.vertices[face[1]] - mesh.vertices[face[0]],
                        mesh.vertices[face[2]] - mesh.vertices[face[0]]
                    )
                    normal = normal / np.linalg.norm(normal)
                    mesh.vertex_normals[face[0]] += normal
                    mesh.vertex_normals[face[1]] += normal
                    mesh.vertex_normals[face[2]] += normal
                
                for i in range(len(mesh.vertex_normals)):
                    if np.any(mesh.vertex_normals[i]):
                        mesh.vertex_normals[i] = mesh.vertex_normals[i] / np.linalg.norm(mesh.vertex_normals[i])
            
            normals = np.array(mesh.vertex_normals, dtype='f4')
            
            # Store for later use
            self.mesh_vertices = vertices
            self.mesh_indices = indices
            self.mesh_normals = normals
            
            # Find mouth vertices (this is a simplification - in a real app, you'd need to know the vertex indices of the mouth)
            # For demonstration, we'll assume the mouth vertices are located in a specific Y range
            # You'd need to modify this based on your actual model
            y_min = np.percentile(vertices[:, 1], 45)  # Approximate position of mouth
            y_max = np.percentile(vertices[:, 1], 50)
            z_min = np.percentile(vertices[:, 2], 75)  # Front of face
            
            self.mouth_vertices_indices = np.where(
                (vertices[:, 1] >= y_min) & 
                (vertices[:, 1] <= y_max) & 
                (vertices[:, 2] >= z_min)
            )[0]
            
            print(f"Found {len(self.mouth_vertices_indices)} potential mouth vertices")
            
            # Create VBO and VAO
            vbo = self.ctx.buffer(np.hstack([vertices, normals]).flatten().astype('f4').tobytes())
            ibo = self.ctx.buffer(indices.flatten().astype('i4').tobytes())
            
            self.vao = self.ctx.vertex_array(
                self.prog,
                [
                    (vbo, '3f 3f', 'in_position', 'in_normal')
                ],
                ibo
            )
            
            # Store original vertices for animation
            self.original_vertices = vertices.copy()
            
            # Initial render
            self.render_model()
            
        except Exception as e:
            self.status_bar.config(text=f"Error loading model: {e}")
            print(f"Error loading model: {e}")
            
    def render_model(self):
        """Render the 3D model to texture"""
        if self.vao is None:
            return
            
        # Setup viewport
        self.ctx.viewport = (0, 0, 800, 600)
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        # Clear the framebuffer
        self.fbo.use()
        self.ctx.clear(0.1, 0.1, 0.1, 1.0)
        
        # Create model-view-projection matrix
        proj = Matrix44.perspective_projection(45.0, 800/600, 0.1, 100.0)
        view = Matrix44.look_at(
            (0, 0, 2),  # Eye position
            (0, 0, 0),  # Target
            (0, 1, 0),  # Up vector
        )
        model = Matrix44.from_eulers([0, time.time() * 0.2, 0])
        mvp = proj * view * model
        
        # Update uniform and render
        self.prog['mvp'].write(mvp.astype('f4').tobytes())
        self.vao.render()
        
        # Read pixels from the framebuffer
        data = self.fbo.read(components=4)
        image = Image.frombytes('RGBA', (800, 600), data).transpose(Image.FLIP_TOP_BOTTOM)
        
        # Convert to PhotoImage and display in Tkinter
        photo = ImageTk.PhotoImage(image)
        
        # If a label exists, update it, otherwise create one
        if hasattr(self, 'render_label'):
            self.render_label.config(image=photo)
            self.render_label.image = photo
        else:
            self.render_label = tk.Label(self.render_frame, image=photo, bg="#11111b")
            self.render_label.image = photo
            self.render_label.pack(fill=tk.BOTH, expand=True)
        
        # Continue animation if we're playing
        if hasattr(self, 'is_playing') and self.is_playing:
            self.root.after(30, self.render_model)
        else:
            self.root.after(100, self.render_model)
        
    def update_model_animation(self, mouth_openness):
        """Update the 3D model based on lip sync data"""
        if self.mesh_vertices is None or not hasattr(self, 'mouth_vertices_indices'):
            return
            
        # In a real implementation, you would modify the vertices around the mouth
        # based on the phoneme data
        modified_vertices = self.original_vertices.copy()
        
        # Move the mouth vertices based on openness
        if len(self.mouth_vertices_indices) > 0:
            # Scale the movement based on openness (0-30)
            scale = mouth_openness / 30.0
            
            # Move vertices down to open mouth
            for idx in self.mouth_vertices_indices:
                modified_vertices[idx, 1] -= scale * 0.05  # Move in Y direction
        
        # Update the vertex buffer
        # Note: In a real app, you'd need to update the vertex buffer properly
        # This simplified version just re-renders with the original vertices
        
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
            # For this demo, we'll simulate phoneme detection using amplitude
            
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
            frame_duration = 0.512  # seconds (based on hop_length/sr)
            
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
                self.root.after(0, lambda o=mouth_openness: self.update_model_animation(o))
                
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
                self.root.after(0, lambda: self.update_model_animation(0))
                self.root.after(0, self.update_waveform_display)
                
            # Stop audio
            sd.stop()
                
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Error during playback: {e}"))
            self.is_playing = False
            self.root.after(0, self.stop_playback)
    
    def on_closing(self):
        """Clean up resources before closing"""
        if hasattr(self, 'gl_window') and self.gl_window:
            glfw.destroy_window(self.gl_window)
        glfw.terminate()
        self.root.destroy()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = AvatarLipSyncApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()