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
            
            # Initialize with CD quality audio (44.1kHz, 16 bit, stereo)
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(2)  # Use stereo
            
            print("Initialized pygame audio mixer with high quality settings")
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
            # Try to play audio if we have a device
            if self.has_audio_device:
                try:
                    # Load and play the audio file
                    pygame.mixer.music.load(self.audio_file)
                    pygame.mixer.music.set_volume(1.0)  # Ensure volume is at maximum
                    pygame.mixer.music.play(0, start_time)
                    print("Started audio playback")
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
            playback_start = time.time() - start_time
            
            # Animate mouth with the audio
            while self.is_playing and self.current_frame < total_frames:
                # Calculate current playback time based on pygame music position
                if self.has_audio_device and pygame.mixer.music.get_busy():
                    try:
                        pos = pygame.mixer.music.get_pos()
                        if pos >= 0:
                            self.current_playback_time = pos / 1000.0  # Convert ms to seconds
                        else:
                            self.current_playback_time = time.time() - playback_start
                    except:
                        self.current_playback_time = time.time() - playback_start
                else:
                    self.current_playback_time = time.time() - playback_start
                
                # Ensure we don't exceed audio duration
                self.current_playback_time = min(self.current_playback_time, self.audio_duration)
                
                # Update UI if callback provided
                if self.on_playback_update:
                    self.on_playback_update(self.current_playback_time, self.current_frame)
                
                # Wait for next frame
                time.sleep(frame_duration)
                self.current_frame += 1
                
            # Reset when done
            if self.current_frame >= total_frames or self.current_playback_time >= self.audio_duration:
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
            print(f"Loading audio file: {os.path.basename(file_path)}")
            
            # Stop any existing playback
            self.stop_playback()
            
            # Load audio file with librosa for analysis
            print("Reading audio data...")
            self.audio_file = file_path
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
            print(f"Audio loaded: {self.sample_rate}Hz, {len(self.audio_data)} samples")
            
            # Calculate audio duration
            self.audio_duration = librosa.get_duration(y=self.audio_data, sr=self.sample_rate)
            print(f"Audio duration: {self.audio_duration:.2f} seconds")
            
            # Extract phonemes for lip sync
            print("Extracting phonemes for lip sync...")
            self.phonemes = self.extract_phonemes(self.audio_data, self.sample_rate)
            print(f"Generated {len(self.phonemes)} phoneme frames")
            
            # Reinitialize pygame mixer with the correct sample rate if needed
            if not self.has_audio_device or pygame.mixer.get_init()[0] != self.sample_rate:
                try:
                    print(f"Reinitializing audio device with sample rate {self.sample_rate}Hz")
                    pygame.mixer.quit()
                    pygame.mixer.pre_init(self.sample_rate, -16, 2, 2048)
                    pygame.mixer.init()
                    pygame.mixer.set_num_channels(2)
                    self.has_audio_device = True
                    print("Audio device initialized successfully")
                except Exception as e:
                    print(f"Error initializing audio device with sample rate {self.sample_rate}: {e}")
                    self.has_audio_device = False
            
            # Set volume to maximum
            pygame.mixer.music.set_volume(1.0)
            
            print("Audio loading complete")
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
        try:
            # Stop playback first
            self.stop_playback()
            
            # Clean up pygame mixer if initialized
            if self.has_audio_device:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass  # Ignore errors during stop
                    
                try:
                    pygame.mixer.quit()
                except Exception:
                    pass  # Ignore errors during quit
                
            self.has_audio_device = False
            
        except Exception as e:
            print(f"Error during audio cleanup: {e}") 