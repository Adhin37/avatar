"""Audio processor for handling audio playback and analysis"""

import os
import wave
import numpy as np
import pyaudio
import threading
from time import sleep

class AudioProcessor:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.wf = None
        self.is_playing = False
        self.current_position = 0
        self.duration = 0
        self.audio_data = None
        self.playback_thread = None
        self.chunk_size = 1024
        self.channels = None
        self.sample_width = None
        self.framerate = None
        
    def load_file(self, file_path):
        """Load an audio file and prepare it for playback and visualization"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found: {file_path}")
                
            # Close any existing resources
            self.cleanup()
            
            # Open the wave file
            self.wf = wave.open(file_path, 'rb')
            
            # Get audio file properties
            self.channels = self.wf.getnchannels()
            self.sample_width = self.wf.getsampwidth()
            self.framerate = self.wf.getframerate()
            
            # Calculate duration
            n_frames = self.wf.getnframes()
            self.duration = n_frames / float(self.framerate)
            
            # Read the entire file for waveform visualization
            raw_data = self.wf.readframes(n_frames)
            self.wf.rewind()  # Reset file pointer for playback
            
            # Convert to numpy array for processing
            dtype = None
            if self.sample_width == 1:
                dtype = np.uint8
            elif self.sample_width == 2:
                dtype = np.int16
            elif self.sample_width == 4:
                dtype = np.int32
                
            audio_array = np.frombuffer(raw_data, dtype=dtype)
            
            # If stereo, convert to mono by averaging channels
            if self.channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1)
            
            # Normalize the data for visualization
            self.audio_data = audio_array / np.iinfo(dtype).max
            
            return True
            
        except Exception as e:
            print(f"Error loading audio file: {e}")
            self.cleanup()
            return False
    
    def get_audio_data(self):
        """Get the processed audio data for visualization"""
        if self.audio_data is None:
            return None
            
        # Downsample the audio data to a reasonable size for visualization
        target_size = 1000  # Number of points to display
        if len(self.audio_data) > target_size:
            # Calculate the number of samples to average
            samples_per_point = len(self.audio_data) // target_size
            # Reshape and calculate mean of each group
            remainder = len(self.audio_data) % target_size
            if remainder:
                # Trim the array to make it evenly divisible
                data = self.audio_data[:-remainder]
            else:
                data = self.audio_data
            data = data.reshape(-1, samples_per_point).mean(axis=1)
            return data.tolist()
        return self.audio_data.tolist()
    
    def get_duration(self):
        """Get the duration of the audio file in seconds"""
        return self.duration
    
    def get_position(self):
        """Get the current playback position in seconds"""
        return self.current_position
    
    def is_playing(self):
        """Check if audio is currently playing"""
        return self.is_playing
    
    def toggle_playback(self, update_callback=None, complete_callback=None):
        """Toggle audio playback state"""
        if self.is_playing:
            self.stop_playback()
            return False
        else:
            return self.start_playback(update_callback, complete_callback)
    
    def start_playback(self, update_callback=None, complete_callback=None):
        """Start audio playback"""
        if not self.wf:
            return False
            
        try:
            self.stream = self.audio.open(
                format=self.audio.get_format_from_width(self.wf.getsampwidth()),
                channels=self.wf.getnchannels(),
                rate=self.wf.getframerate(),
                output=True,
                stream_callback=self._audio_callback
            )
            
            self.is_playing = True
            self.playback_thread = threading.Thread(
                target=self._playback_thread,
                args=(update_callback, complete_callback)
            )
            self.playback_thread.daemon = True
            self.playback_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error starting playback: {e}")
            return False
    
    def stop_playback(self):
        """Stop audio playback"""
        self.is_playing = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def seek_to(self, position):
        """Seek to a specific position in the audio file"""
        if not self.wf:
            return False
            
        try:
            # Calculate frame position
            frame_pos = int(position * self.framerate)
            self.wf.setpos(frame_pos)
            self.current_position = position
            return True
            
        except Exception as e:
            print(f"Error seeking: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_playback()
        if self.wf:
            self.wf.close()
            self.wf = None
        self.current_position = 0
        self.duration = 0
        self.audio_data = None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
    
    def _playback_thread(self, update_callback=None, complete_callback=None):
        """Thread for monitoring playback progress"""
        update_interval = 0.05  # 50ms update interval
        
        while self.is_playing and self.stream and not self.stream.is_stopped():
            if self.wf:
                self.current_position = self.wf.tell() / float(self.framerate)
                if update_callback:
                    update_callback(self.current_position, self._get_mouth_openness())
            sleep(update_interval)
        
        self.is_playing = False
        if complete_callback:
            complete_callback()
    
    def _get_mouth_openness(self):
        """Calculate mouth openness based on current audio frame"""
        # Simple amplitude-based calculation
        if not self.wf or not self.audio_data:
            return 0.0
            
        current_frame = int(self.current_position * self.framerate)
        if current_frame >= len(self.audio_data):
            return 0.0
            
        # Get a small window of samples around the current position
        window_size = 1024
        start = max(0, current_frame - window_size // 2)
        end = min(len(self.audio_data), current_frame + window_size // 2)
        window = self.audio_data[start:end]
        
        # Calculate RMS amplitude
        rms = np.sqrt(np.mean(np.square(window)))
        # Map RMS to mouth openness (0.0 to 1.0)
        return min(1.0, rms * 3.0)  # Scale factor of 3.0 can be adjusted 