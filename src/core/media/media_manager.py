import os
import numpy as np
from ..processors.audio_processor import AudioProcessor
from ..processors.image_processor import ImageProcessor
from ..processors.lipsync_processor import LipSyncProcessor
from ..utils.event_manager import EventManager
from ..events import EventEmitter

class MediaManager(EventEmitter):
    """Manages all media-related operations including audio, image, and lip sync"""
    
    def __init__(self):
        super().__init__()
        self.event_manager = EventManager()
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.lipsync_processor = LipSyncProcessor()
        
        # Initialize state
        self.is_initialized = False
        self._setup_processors()
        
        self.current_audio_file = None
        self.current_avatar_file = None
    
    def _setup_processors(self):
        """Initialize and connect processors"""
        try:
            # Connect processors
            self.audio_processor.set_callbacks(
                on_playback_update=self._handle_playback_update,
                on_playback_complete=self._handle_playback_complete
            )
            
            # Mark as initialized
            self.is_initialized = True
            
        except Exception as e:
            print(f"Error initializing media manager: {e}")
            self.is_initialized = False
    
    def load_avatar_image(self, image_path):
        """Load and process avatar image"""
        try:
            if not self.is_initialized:
                raise RuntimeError("MediaManager not properly initialized")
                
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            print(f"Loading avatar from path: {image_path}")
            success = self.image_processor.load_image(image_path)
            if success:
                print("Successfully loaded avatar image")
                self.current_avatar_file = image_path
                # Verify image is loaded
                img = self.image_processor.get_image()
                if img:
                    print(f"Avatar image loaded successfully, size: {img.size}")
                else:
                    print("Warning: Image processor returned None after successful load")
                self.emit_event("avatar_loaded")
            return success
            
        except Exception as e:
            print(f"Error loading avatar image: {e}")
            self.emit_event("avatar_load_error", str(e))
            return False
    
    def load_audio_file(self, file_path):
        """Load and process audio file"""
        try:
            if not self.is_initialized:
                raise RuntimeError("MediaManager not properly initialized")
                
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found: {file_path}")
                
            if not file_path.lower().endswith(('.wav', '.mp3', '.ogg')):
                raise ValueError("Unsupported audio format")
                
            success = self.audio_processor.load_file(file_path)
            if not success:
                raise RuntimeError("Failed to load audio file")
                
            self.current_audio_file = file_path
            # Get audio data for waveform visualization
            audio_data = self.audio_processor.get_audio_data()
            # Emit loaded event with filename and audio data
            self.emit_event("audio_loaded", os.path.basename(file_path), audio_data)
            return True
            
        except Exception as e:
            print(f"Error loading audio: {e}")
            self.emit_event("audio_load_error", str(e))
            return False
    
    def get_current_frame(self, mouth_openness=0):
        """Get current avatar frame with mouth animation"""
        try:
            if not self.image_processor.has_image():
                return None
            return self.image_processor.get_current_frame(mouth_openness)
        except Exception as e:
            print(f"Error getting current frame: {e}")
            return None
    
    def get_mouth_region(self):
        """Get mouth region coordinates"""
        try:
            return self.image_processor.get_mouth_region()
        except Exception as e:
            print(f"Error getting mouth region: {e}")
            return None
    
    def toggle_playback(self):
        """Toggle audio playback"""
        try:
            if not self.is_initialized:
                return False
                
            if self.audio_processor.is_playing:
                self.audio_processor.stop_playback()
                self.emit_event("playback_stopped")
                return False
            else:
                success = self.audio_processor.start_playback(
                    self.audio_processor.current_playback_time
                )
                if success:
                    self.emit_event("playback_started")
                return success
                
        except Exception as e:
            print(f"Error toggling playback: {e}")
            self.emit_event("playback_error", str(e))
            return False
    
    def seek_to(self, position):
        """Seek to position in audio"""
        try:
            if self.audio_processor.seek_to(position):
                self.lipsync_processor.seek_to(position)
                self.emit_event("playback_seek", position)
                # Update UI immediately after seeking
                current_time = self.audio_processor.get_position()
                mouth_openness = self.audio_processor.get_mouth_openness_at(current_time)
                self.emit_event("playback_update", current_time, mouth_openness)
                return True
            return False
        except Exception as e:
            print(f"Error seeking: {e}")
            return False
    
    def _handle_playback_update(self, current_time, frame):
        """Handle playback update event"""
        try:
            mouth_openness = self.audio_processor.get_current_mouth_openness()
            self.emit_event("playback_update", current_time, mouth_openness)
        except Exception as e:
            print(f"Error handling playback update: {e}")
    
    def _handle_playback_complete(self):
        """Handle playback complete event"""
        try:
            self.emit_event("playback_complete")
        except Exception as e:
            print(f"Error handling playback complete: {e}")
    
    def get_playback_info(self):
        """Get current playback information"""
        if self.audio_processor:
            return {
                'duration': self.audio_processor.get_duration(),
                'position': self.audio_processor.get_position(),
                'is_playing': self.audio_processor.is_playing()
            }
        return None
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop any ongoing playback
            if hasattr(self, 'audio_processor'):
                if self.audio_processor.is_playing:
                    self.audio_processor.stop_playback()
                self.audio_processor.cleanup()
            
            # Clear image resources
            if hasattr(self, 'image_processor'):
                self.image_processor.clear()
            
            # Clear event handlers
            if hasattr(self, 'event_manager'):
                self.event_manager.clear()
            
            # Clear any stored data
            self.is_initialized = False
            
            self.current_audio_file = None
            self.current_avatar_file = None
            
        except Exception as e:
            print(f"Error cleaning up media resources: {e}")
    
    def bind_event_handler(self, event, handler):
        """Bind event handler"""
        self.event_manager.bind(event, handler)
    
    def get_avatar_image(self):
        """Get the current avatar image"""
        if self.image_processor:
            return self.image_processor.get_image()
        return None 