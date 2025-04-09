"""
Playback Controls Component with Waveform Visualization

This component provides audio playback controls with the following features:
- Play/Pause button
- Audio waveform visualization with seek functionality
- Time display
- Hide/Show capability for dynamic UI

IMPORTANT: This component uses pack geometry manager with specific settings.
Any modifications to the widget hierarchy must preserve the following structure:
    frame (ttk.Frame - self)
    └── container (ttk.Frame)
        ├── time_label (ttk.Label)
        ├── play_button (tk.Button)
        └── waveform_canvas (tk.Canvas)

The hide/show functionality relies on managing the main frame's pack state.
DO NOT modify the frame packing hierarchy without updating hide() and show() methods.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np

class PlaybackControls(ttk.Frame):
    """
    Audio playback controls widget that supports play/pause, seeking, and hide/show functionality.
    
    Key Methods:
        hide(): Removes the widget from view
        show(): Displays the widget
        set_playing(is_playing): Updates play/pause button state
        set_duration(duration): Sets the total duration
        set_position(position): Updates current position
        update_display(current_time): Updates time display
        bind_play_handler(handler): Sets the play/pause callback
        bind_seek_handler(handler): Sets the seek callback
    
    Important:
        - The widget uses pack geometry manager
        - hide/show functionality manages the main frame's pack state
        - Preserve the widget hierarchy when modifying the code
    """
    
    def __init__(self, parent, media_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.media_manager = media_manager
        self.theme = parent.winfo_toplevel().theme
        self.canvas_height = int(parent.winfo_screenheight() * 0.08)  # 8% of screen height
        self.waveform_data = None
        self.is_playing = False
        
        # Create widgets
        self._create_widgets()
        self._setup_bindings()
        
        # Subscribe to media manager events
        self.media_manager.on("audio_loaded", self._on_audio_loaded)
        self.media_manager.on("playback_update", self._on_playback_update)
    
    def _create_widgets(self):
        """Create and layout the playback control widgets"""
        # Main container
        self.controls_frame = ttk.Frame(self, style='Playback.TFrame')
        self.controls_frame.pack(fill=tk.BOTH, expand=True)
        
        # Waveform canvas
        self.canvas = tk.Canvas(
            self.controls_frame,
            height=self.canvas_height,
            bg=self.theme.get_color('background'),
            highlightthickness=1,
            highlightbackground=self.theme.get_color('border')
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Progress indicator
        self.progress_line = self.canvas.create_line(
            0, 0, 0, self.canvas_height,
            fill=self.theme.get_color('progress'),
            width=2,
            state=tk.HIDDEN
        )
        
        # Control bar frame
        self.control_bar = ttk.Frame(self.controls_frame, style='Playback.TFrame')
        self.control_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Play/Pause button
        self.play_button = ttk.Button(
            self.control_bar,
            text="▶",
            width=3,
            command=self._toggle_playback,
            style="PlayPause.TButton"
        )
        self.play_button.pack(side=tk.LEFT)
        
        # Time labels
        self.time_frame = ttk.Frame(self.control_bar, style='Playback.TFrame')
        self.time_frame.pack(side=tk.RIGHT)
        
        self.current_time = ttk.Label(
            self.time_frame,
            text="0:00",
            style="Time.TLabel"
        )
        self.current_time.pack(side=tk.LEFT)
        
        ttk.Label(
            self.time_frame,
            text=" / ",
            style="Time.TLabel"
        ).pack(side=tk.LEFT)
        
        self.total_time = ttk.Label(
            self.time_frame,
            text="0:00",
            style="Time.TLabel"
        )
        self.total_time.pack(side=tk.LEFT)
    
    def _setup_bindings(self):
        """Set up event bindings"""
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
    
    def _on_audio_loaded(self, filename, audio_data):
        """Handle audio loaded event"""
        self.waveform_data = audio_data
        self._draw_waveform()
        duration = self.media_manager.get_playback_info()["duration"]
        self.total_time.configure(text=self._format_time(duration))
    
    def _on_playback_update(self, position, duration):
        """Handle playback update event"""
        if self.waveform_data is not None:
            canvas_width = self.canvas.winfo_width()
            x_pos = (position / duration) * canvas_width
            self.canvas.coords(self.progress_line, x_pos, 0, x_pos, self.canvas_height)
            self.canvas.itemconfigure(self.progress_line, state=tk.NORMAL)
        
        self.current_time.configure(text=self._format_time(position))
    
    def _draw_waveform(self):
        """Draw the audio waveform on the canvas"""
        if self.waveform_data is None:
            return
        
        self.canvas.delete("waveform")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas_height
        center_y = canvas_height // 2
        
        # Scale the waveform data to fit the canvas
        num_points = min(len(self.waveform_data), canvas_width)
        if num_points < 2:
            return
        
        # Resample the waveform data
        indices = np.linspace(0, len(self.waveform_data) - 1, num_points)
        resampled_data = np.interp(indices, np.arange(len(self.waveform_data)), self.waveform_data)
        
        # Scale the amplitude to fit the canvas height
        scaled_data = resampled_data * (canvas_height * 0.4)
        
        # Draw the waveform
        for i in range(num_points - 1):
            x1 = i
            x2 = i + 1
            
            # Draw mirrored waveform
            self.canvas.create_line(
                x1, center_y + scaled_data[i],
                x2, center_y + scaled_data[i + 1],
                fill=self.theme.get_color('waveform'),
                width=1,
                tags="waveform"
            )
            self.canvas.create_line(
                x1, center_y - scaled_data[i],
                x2, center_y - scaled_data[i + 1],
                fill=self.theme.get_color('waveform'),
                width=1,
                tags="waveform"
            )
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize event"""
        self._draw_waveform()
    
    def _on_canvas_click(self, event):
        """Handle canvas click event"""
        if self.waveform_data is not None:
            canvas_width = self.canvas.winfo_width()
            click_position = event.x / canvas_width
            
            duration = self.media_manager.get_playback_info()["duration"]
            seek_position = click_position * duration
            
            self.media_manager.seek_to(seek_position)
    
    def _toggle_playback(self):
        """Toggle audio playback"""
        is_playing = self.media_manager.toggle_playback()
        self.play_button.configure(text="⏸" if is_playing else "▶")
    
    def _format_time(self, seconds):
        """Format time in seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def hide(self):
        """Hide the playback controls"""
        self.pack_forget()
    
    def show(self):
        """Show the playback controls"""
        self.pack(fill=tk.X, padx=5, pady=(0, 10))
    
    @property
    def is_visible(self):
        """Read-only property indicating if the widget is currently visible"""
        return self.winfo_ismapped()
    
    def bind_play_handler(self, handler):
        """Bind play/pause handler"""
        self.play_button.configure(command=handler)
    
    def bind_seek_handler(self, handler):
        """Bind seek handler"""
        self.canvas.bind("<Button-1>", handler)
    
    def set_duration(self, duration):
        """Set audio duration"""
        self.total_time.configure(text=self._format_time(duration))
    
    def set_playing(self, is_playing):
        """Set playing state"""
        self.is_playing = is_playing
        self.play_button.configure(text="⏸" if is_playing else "▶")
    
    def update_display(self, current_time):
        """Update time display and progress"""
        self.current_time.configure(text=self._format_time(current_time))
        self.update_position(current_time)
    
    def update_position(self, position):
        """Update the current playback position"""
        # Implementation needed
        pass
    
    def _on_play_toggle(self):
        """Handle play/pause button click"""
        # Implementation needed
        pass 