import tkinter as tk
from tkinter import ttk
import time
import numpy as np

class PlaybackControls:
    def __init__(self, parent, on_play_pause=None, on_seek=None):
        self.parent = parent
        self.on_play_pause = on_play_pause
        self.on_seek = on_seek
        self.is_playing = False
        
        # Create controls layout
        self.controls_layout = ttk.Frame(parent)
        
        # Audio time display (current time)
        self.current_time_var = tk.StringVar(value="0:00")
        self.current_time = ttk.Label(self.controls_layout, textvariable=self.current_time_var, 
                                    font=("Helvetica", 10, "bold"))
        self.current_time.pack(side=tk.LEFT, padx=(0, 10))
        
        # Play/Pause button
        self.play_frame = ttk.Frame(self.controls_layout)
        self.play_frame.pack(side=tk.LEFT, padx=10)
        
        self.play_canvas = tk.Canvas(self.play_frame, width=54, height=54, bg="#2e2e3e", highlightthickness=0)
        self.play_canvas.pack()
        
        # Button colors
        self.play_bg_color = "#4CAF50"  # Green for play
        self.pause_bg_color = "#FF5722"  # Orange for pause
        
        # Draw initial play button
        self._draw_play_button()
        
        # Waveform frame
        self.waveform_frame = tk.Frame(self.controls_layout, bg="#1e1e2e", bd=2, relief=tk.RIDGE)
        self.waveform_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.waveform_canvas = tk.Canvas(self.waveform_frame, height=50, bg="#1e1e2e", highlightthickness=0)
        self.waveform_canvas.pack(fill=tk.X, expand=True)
        if self.on_seek:
            self.waveform_canvas.bind("<Button-1>", self._handle_seek)
        
        # Progress bar
        self.progress_canvas = tk.Canvas(self.waveform_frame, height=3, bg="#1e1e2e", highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X)
        
        # Total time display
        self.total_time_var = tk.StringVar(value="0:00")
        self.total_time = ttk.Label(self.controls_layout, textvariable=self.total_time_var,
                                  font=("Helvetica", 10, "bold"))
        self.total_time.pack(side=tk.LEFT, padx=10)
        
        # Setup hover effects for play button
        self._setup_play_button_hover()
    
    def _draw_play_button(self):
        self.play_canvas.delete("all")
        
        # Shadow
        self.play_canvas.create_oval(7, 7, 47, 47, fill="#000000", outline="", stipple="gray50")
        
        # Button background
        bg_color = self.pause_bg_color if self.is_playing else self.play_bg_color
        self.play_circle = self.play_canvas.create_oval(5, 5, 45, 45, fill=bg_color, outline="")
        
        # Highlight/reflection effect
        self.play_canvas.create_arc(8, 8, 42, 42, start=45, extent=180, 
                                  fill=bg_color, outline="", stipple="gray25")
        self.play_canvas.create_arc(8, 8, 42, 42, start=225, extent=180, 
                                  fill="#ffffff", outline="", stipple="gray25")
        
        # Draw play/pause symbol
        if self.is_playing:
            self.play_canvas.create_rectangle(17, 15, 23, 35, fill="white", outline="")
            self.play_canvas.create_rectangle(27, 15, 33, 35, fill="white", outline="")
        else:
            self.play_canvas.create_polygon(20, 15, 20, 35, 35, 25, fill="white")
    
    def _setup_play_button_hover(self):
        def on_enter(e):
            self.play_canvas.itemconfig(self.play_circle, 
                                      fill="#66BB6A" if self.is_playing else "#FF7043")
            self.play_canvas.create_oval(0, 0, 54, 54, outline="#89b4fa", width=2, dash=(5, 2))
        
        def on_leave(e):
            self.play_canvas.itemconfig(self.play_circle, 
                                      fill=self.pause_bg_color if self.is_playing else self.play_bg_color)
            self.play_canvas.delete("glow")
        
        self.play_canvas.bind("<Enter>", on_enter)
        self.play_canvas.bind("<Leave>", on_leave)
        self.play_canvas.bind("<Button-1>", self._handle_play_pause)
    
    def _handle_play_pause(self, event=None):
        if self.on_play_pause:
            self.on_play_pause()
    
    def _handle_seek(self, event):
        if self.on_seek:
            width = self.waveform_canvas.winfo_width()
            click_position = event.x / width
            self.on_seek(click_position)
    
    def update_waveform(self, audio_data, current_time, total_time):
        """Update the waveform display"""
        width = self.waveform_canvas.winfo_width()
        height = self.waveform_canvas.winfo_height()
        
        if width <= 1:
            return
            
        # Clear current waveform
        self.waveform_canvas.delete("all")
        self.progress_canvas.delete("all")
        
        # Draw background
        self.waveform_canvas.create_rectangle(0, 0, width, height, fill="#2e2e3e", outline="")
        
        if audio_data is not None and len(audio_data) > 0:
            # Calculate waveform data points
            samples_per_pixel = max(1, len(audio_data) // width)
            waveform_points = []
            
            for i in range(0, width):
                start = i * samples_per_pixel
                end = min(len(audio_data), (i + 1) * samples_per_pixel)
                if start < len(audio_data):
                    segment = audio_data[start:end]
                    if len(segment) > 0:
                        amplitude = np.max(np.abs(segment)) * height / 2
                        amplitude = max(2, amplitude)
                        center_y = height / 2
                        waveform_points.append((i, center_y - amplitude, i, center_y + amplitude))
            
            # Draw waveform with gradient
            for i, (x, y1, x2, y2) in enumerate(waveform_points):
                if current_time > 0 and total_time > 0:
                    progress_x = (current_time / total_time) * width
                    
                    if x < progress_x:
                        intensity = int(200 + (x / progress_x) * 55) if progress_x > 0 else 200
                        color = f"#{intensity//2:02x}{intensity//2:02x}{intensity:02x}"
                    else:
                        intensity = int(127 + ((width-x) / (width-progress_x)) * 40) if width != progress_x else 127
                        color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                else:
                    intensity = int(127 + (i / width) * 40)
                    color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                    
                self.waveform_canvas.create_line(x, y1, x, y2, fill=color, width=1)
            
            # Draw playhead
            if current_time > 0 and total_time > 0:
                playhead_x = (current_time / total_time) * width
                
                # Playhead line with gradient
                for y in range(0, height, 2):
                    intensity = int(255 - (y / height) * 100)
                    color = f"#{intensity:02x}{intensity//3:02x}{intensity//3:02x}"
                    self.waveform_canvas.create_line(playhead_x, y, playhead_x, y+1, fill=color, width=2)
                
                # Draw progress in progress bar
                self.progress_canvas.create_rectangle(0, 0, playhead_x, 3, fill="#89b4fa", outline="")
                self.progress_canvas.create_rectangle(playhead_x, 0, width, 3, fill="#3e3e4e", outline="")
            else:
                # Empty progress bar
                self.progress_canvas.create_rectangle(0, 0, width, 3, fill="#3e3e4e", outline="")
    
    def update_time(self, current_time, total_time):
        """Update time displays"""
        self.current_time_var.set(self.format_time(current_time))
        self.total_time_var.set(self.format_time(total_time))
    
    def set_playing(self, is_playing):
        """Update play/pause button state"""
        self.is_playing = is_playing
        self._draw_play_button()
    
    def show(self):
        """Show the controls with fade effect"""
        self.controls_layout.pack(fill=tk.X, pady=10)
        
        # Add glow effect to play button
        self.play_canvas.configure(bg="#2e2e3e")
        self.play_canvas.create_oval(0, 0, 54, 54, outline="#89b4fa", width=2, dash=(5, 2))
    
    def hide(self):
        """Hide the controls"""
        self.controls_layout.pack_forget()
    
    @staticmethod
    def format_time(seconds):
        """Format time in minutes:seconds"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}" 