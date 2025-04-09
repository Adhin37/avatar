import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
import threading
import time

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
    
    def load_audio(self, file_path):
        """Load and process an audio file"""
        try:
            # Load the audio file
            y, sr = librosa.load(file_path)
            
            # Store raw audio data for waveform display
            self.audio_data = y
            self.sample_rate = sr
            self.audio_duration = librosa.get_duration(y=y, sr=sr)
            self.audio_file = file_path
            
            # Extract audio features for lip sync
            self._extract_phonemes(y, sr)
            
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False
    
    def _extract_phonemes(self, y, sr):
        """Extract phoneme timing for lip sync"""
        # Get amplitude envelope
        hop_length = 512
        amplitude_envelope = np.array([
            np.max(abs(y[i:i+hop_length])) 
            for i in range(0, len(y), hop_length)
        ])
        
        # Apply smoothing to avoid jittery mouth movements
        window_size = 5
        smoothed_envelope = np.convolve(amplitude_envelope, 
                                      np.ones(window_size)/window_size, 
                                      mode='same')
        
        # Convert to "mouth openness" values
        self.phonemes = []
        for amp in smoothed_envelope:
            # Scale amplitude to mouth openness (0-30 pixels)
            mouth_openness = min(30, int(amp * 100))
            self.phonemes.append(mouth_openness)
    
    def start_playback(self, start_time=0):
        """Start audio playback"""
        if not self.audio_file or not self.phonemes:
            return False
            
        self.is_playing = True
        self.current_playback_time = start_time
        
        # Start playback thread
        threading.Thread(target=self._playback_thread, args=(start_time,)).start()
        return True
    
    def stop_playback(self):
        """Stop audio playback"""
        self.is_playing = False
        sd.stop()
    
    def _playback_thread(self, start_time):
        """Handle audio playback in a separate thread"""
        try:
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
                
            # Stop audio
            sd.stop()
                
        except Exception as e:
            print(f"Error during playback: {e}")
            self.is_playing = False
            self.stop_playback()
    
    def seek_to(self, position):
        """Seek to a position in the audio"""
        if not self.audio_file or not self.phonemes:
            return False
            
        # Stop current playback
        was_playing = self.is_playing
        if was_playing:
            self.stop_playback()
        
        # Update position
        self.current_playback_time = position * self.audio_duration
        self.current_frame = min(len(self.phonemes) - 1, 
                               int(position * len(self.phonemes)))
        
        # Restart playback if it was playing
        if was_playing:
            self.start_playback(self.current_playback_time)
        
        return True
    
    def get_current_mouth_openness(self):
        """Get the current mouth openness value"""
        if not self.phonemes or self.current_frame >= len(self.phonemes):
            return 0
        return self.phonemes[self.current_frame]
    
    def set_callbacks(self, on_playback_update=None, on_playback_complete=None):
        """Set callbacks for playback updates and completion"""
        self.on_playback_update = on_playback_update
        self.on_playback_complete = on_playback_complete 