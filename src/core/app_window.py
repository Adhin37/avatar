import tkinter as tk
from tkinterdnd2 import TkinterDnD
import os
from .window.window_manager import WindowManager
from .media.media_manager import MediaManager
from .ui import AvatarZone, AudioDropZone, PlaybackControls
from .ui.styles.theme import Theme

class AppWindow:
    def __init__(self):
        # Initialize root window with drag and drop support
        self.root = TkinterDnD.Tk()
        
        # Initialize theme
        self.theme = Theme()
        self.theme.apply_theme(self.root)
        
        # Initialize managers
        self.window_manager = WindowManager(self.root)
        self.media_manager = MediaManager()
        
        # Create main widgets
        self._create_widgets()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Load initial avatar
        self.load_initial_avatar()
    
    def _create_widgets(self):
        """Create and setup all widgets"""
        container = self.window_manager.get_container()
        
        # Create avatar zone with reduced width
        self.avatar_zone = AvatarZone(container)
        self.avatar_zone.avatar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 15))
        
        # Create audio drop zone with adjusted padding
        self.audio_dropzone = AudioDropZone(container)
        self.audio_dropzone.frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Create playback controls (initially hidden)
        self.playback_controls = PlaybackControls(container, self.media_manager)
        # Note: Don't pack here, the widget starts hidden by default
    
    def _setup_event_handlers(self):
        """Setup event handlers for widgets"""
        # Bind media manager events
        self.media_manager.bind_event_handler("avatar_loaded", self._on_avatar_loaded)
        self.media_manager.bind_event_handler("audio_loaded", self._on_audio_loaded)
        self.media_manager.bind_event_handler("playback_update", self._on_playback_update)
        self.media_manager.bind_event_handler("playback_complete", self._on_playback_complete)
        
        # Bind UI events
        self.audio_dropzone.bind_drop_handler(self._on_audio_drop)
        self.playback_controls.bind_play_handler(self._on_play_toggle)
        self.playback_controls.bind_seek_handler(self._on_seek)
        self.window_manager.bind_close_handler(self._handle_close)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
    
    def load_initial_avatar(self):
        """Load the default avatar image"""
        try:
            # Get the absolute path to the resources directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            resources_dir = os.path.join(project_root, "resources")
            avatar_path = os.path.join(resources_dir, "female_avatar.png")
            
            # Normalize path for current platform
            avatar_path = os.path.abspath(os.path.normpath(avatar_path))
            
            print(f"Attempting to load avatar from: {avatar_path}")
            if os.path.exists(avatar_path):
                print(f"Avatar file found, loading from: {avatar_path}")
                success = self.media_manager.load_avatar_image(avatar_path)
                if not success:
                    print("Failed to load avatar image")
            else:
                print(f"Avatar file not found at: {avatar_path}")
                
        except Exception as e:
            print(f"Failed to load initial avatar: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_avatar_loaded(self):
        """Handle avatar loaded event"""
        try:
            print("Avatar loaded event received")
            avatar_image = self.media_manager.get_avatar_image()
            if avatar_image:
                print(f"Got avatar image from media manager, size: {avatar_image.size}")
                print("Displaying avatar image")
                success = self.avatar_zone.display_avatar(avatar_image)
                if success:
                    print("Successfully displayed avatar")
                else:
                    print("Failed to display avatar")
            else:
                print("No avatar image available to display")
        except Exception as e:
            print(f"Error in avatar loaded handler: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_audio_drop(self, file_path):
        """Handle audio file drop event"""
        self.media_manager.load_audio_file(file_path)
    
    def _on_audio_loaded(self, filename):
        """Handle audio loaded event"""
        info = self.media_manager.get_playback_info()
        self.playback_controls.set_duration(info['duration'])
        self.playback_controls.set_position(0)
        self.playback_controls.update_display(0)
        
        # Show playback controls when audio is loaded
        if not self.playback_controls.is_visible:
            self.playback_controls.show()
    
    def _on_play_toggle(self):
        """Handle play/pause toggle"""
        if self.media_manager.toggle_playback():
            info = self.media_manager.get_playback_info()
            self.playback_controls.set_playing(info['is_playing'])
    
    def _on_seek(self, position):
        """Handle seek event"""
        self.media_manager.seek_to(position)
    
    def _on_playback_update(self, current_time, mouth_openness):
        """Handle playback update event"""
        # Update playback time display
        self.playback_controls.update_display(current_time)
        
        # Update avatar mouth animation if we have a valid openness value
        if isinstance(mouth_openness, (float, int)):
            # Ensure value is between 0 and 1
            mouth_openness = max(0.0, min(1.0, float(mouth_openness)))
            self.avatar_zone.display_avatar(mouth_openness)
    
    def _on_playback_complete(self):
        """Handle playback complete event"""
        self.playback_controls.set_playing(False)
        self.playback_controls.set_position(0)
        self.avatar_zone.display_avatar(0)
    
    def _handle_close(self, event=None):
        """Handle window close event"""
        try:
            # Stop any ongoing playback first
            if hasattr(self.media_manager, 'audio_processor'):
                self.media_manager.audio_processor.stop_playback()
            
            # Cleanup media resources
            self.media_manager.cleanup()
            
            # Destroy all widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Force destroy the root window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force quit even if cleanup fails
            self.root.destroy() 