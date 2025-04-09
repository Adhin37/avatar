import numpy as np
import librosa
import pygame
import threading
import time
import os

class AudioProcessor:
    def __init__(self):
        self.audio_file = None
        self.audio_data = None
        self.sample_rate = None
        self.audio_duration = 0
        self.current_playback_time = 0
        self.is_playing = False
        self.phonemes = []
        self.current_frame = 0
        self.on_playback_update = None
        self.on_playback_complete = None
        self.has_audio_device = False
        self.playback_thread = None
        
        # Initialize audio device
        self.initialize_audio_device()
    
    def initialize_audio_device(self):
        """Initialize audio using pygame mixer"""
        try:
            # Set SDL audio driver to pulseaudio before initializing pygame
            os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'
            
            pygame.mixer.init()
            print("Initialized pygame audio mixer with PulseAudio")
            self.has_audio_device = True
            return True
        except Exception as e:
            print(f"Error initializing pygame audio: {e}")
            print("Running in silent mode")
            self.has_audio_device = False
            return False
    
    def _playback_thread(self, start_time):
        """Handle audio playback in a separate thread"""
        try:
            # Load audio data
            y, sr = librosa.load(self.audio_file)
            
            # Calculate starting sample
            start_sample = int(start_time * sr)
            
            # Try to play audio if we have a device
            if self.has_audio_device:
                try:
                    # Load the audio file
                    pygame.mixer.music.load(self.audio_file)
                    
                    # Calculate position to start from
                    start_pos = max(0.0, min(1.0, start_time / self.audio_duration))
                    
                    # Play the audio from the position
                    pygame.mixer.music.play(0, start_time)
                except Exception as e:
                    print(f"Error playing audio: {e}")
                    print("Continuing in silent mode")
                    self.has_audio_device = False
            
            # Frame timing and starting position
            frame_duration = 0.0512  # seconds (based on hop_length/sr)
            
            # Set starting frame based on current playback time
            if start_time > 0 and self.audio_duration > 0:
                self.current_frame = min(len(self.phonemes) - 1, 
                                      int((start_time / self.audio_duration) * len(self.phonemes)))
            else:
                self.current_frame = 0
                
            total_frames = len(self.phonemes)
            start_time = time.time() - start_time
            
            # Animate mouth with the audio
            while self.is_playing and self.current_frame < total_frames:
                # Calculate current playback time
                self.current_playback_time = min(self.audio_duration, time.time() - start_time)
                
                # Update UI if callback provided
                if self.on_playback_update:
                    self.on_playback_update(self.current_playback_time, self.current_frame)
                
                # Wait for next frame
                time.sleep(frame_duration)
                self.current_frame += 1
                
            # Reset when done
            if self.current_frame >= total_frames:
                self.is_playing = False
                self.current_playback_time = 0
                if self.on_playback_complete:
                    self.on_playback_complete()
                
            # Stop audio if we have a device
            if self.has_audio_device:
                try:
                    pygame.mixer.music.stop()
                except Exception as e:
                    print(f"Error stopping audio: {e}")
                
        except Exception as e:
            print(f"Error during playback: {e}")
            self.is_playing = False
            self.stop_playback()
    
    def stop_playback(self):
        """Stop audio playback"""
        self.is_playing = False
        
        # Wait for playback thread to finish
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
        
        # Stop audio if we have a device
        if self.has_audio_device:
            try:
                pygame.mixer.music.stop()
            except Exception as e:
                print(f"Error stopping audio: {e}")
    
    def start_playback(self, start_time=0):
        """Start audio playback from the specified time"""
        if not self.audio_file or self.audio_data is None or len(self.audio_data) == 0:
            return False
        
        # Stop any existing playback
        self.stop_playback()
        
        # Start new playback
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self._playback_thread, args=(start_time,))
        self.playback_thread.daemon = True  # Make thread daemon so it exits when main thread exits
        self.playback_thread.start()
        
        return True
    
    def seek_to(self, position):
        """Seek to a specific position in the audio"""
        if not self.audio_file or not self.audio_data:
            return False
        
        # Ensure position is within bounds
        position = max(0, min(position, self.audio_duration))
        
        # Restart playback from new position
        return self.start_playback(position)
    
    def load_audio(self, file_path):
        """Load and process an audio file"""
        try:
            # Stop any existing playback
            self.stop_playback()
            
            # Load audio file
            self.audio_file = file_path
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
            
            # Calculate audio duration
            self.audio_duration = librosa.get_duration(y=self.audio_data, sr=self.sample_rate)
            
            # Extract phonemes for lip sync
            self.phonemes = self.extract_phonemes(self.audio_data, self.sample_rate)
            
            return True
            
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False
    
    def extract_phonemes(self, audio_data, sample_rate):
        """Extract phoneme information from audio data"""
        # This is a placeholder for actual phoneme extraction
        # In a real implementation, this would use a speech recognition model
        # For now, we'll just return a simple amplitude-based approximation
        hop_length = 512  # samples
        frame_length = 2048  # samples
        
        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Normalize RMS to 0-1 range
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
        
        # Convert to phoneme-like values (simplified)
        phonemes = []
        for energy in rms_norm:
            # Map energy to mouth openness (0-1)
            mouth_openness = min(1.0, energy * 2.0)  # Scale up for more visible movement
            phonemes.append(mouth_openness)
        
        return phonemes
    
    def get_current_mouth_openness(self):
        """Get the current mouth openness value for lip sync"""
        if not self.phonemes or self.current_frame >= len(self.phonemes):
            return 0
        
        return self.phonemes[self.current_frame]
    
    def set_callbacks(self, on_playback_update=None, on_playback_complete=None):
        """Set callbacks for playback events"""
        self.on_playback_update = on_playback_update
        self.on_playback_complete = on_playback_complete
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_playback()
        
        # Clean up Pygame
        try:
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error cleaning up Pygame mixer: {e}") 