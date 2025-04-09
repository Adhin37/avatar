import numpy as np
import librosa
import threading
import time
from typing import List, Tuple, Callable, Optional

class LipSyncProcessor:
    """
    Processes audio data to determine appropriate mouth shapes for lip syncing.
    Analyzes phonemes and amplitude to generate mouth openness values.
    """
    
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.duration = 0
        self.phonemes = []
        self.amplitude_envelope = []
        self.mouth_openness = []
        self.current_frame = 0
        self.is_processing = False
        self.on_update = None
        self.on_complete = None
        
        # Lip sync parameters
        self.hop_length = 512  # Samples between frames
        self.window_size = 5   # Smoothing window size
        self.max_openness = 30 # Maximum mouth openness in pixels
        
    def process_audio(self, audio_data: np.ndarray, sample_rate: int) -> bool:
        """
        Process audio data to extract phonemes and generate mouth shapes.
        
        Args:
            audio_data: Audio waveform data as numpy array
            sample_rate: Sample rate of the audio in Hz
            
        Returns:
            bool: True if processing was successful
        """
        if audio_data is None or len(audio_data) == 0:
            return False
            
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.duration = librosa.get_duration(y=audio_data, sr=sample_rate)
        
        # Extract phonemes using librosa
        self._extract_phonemes()
        
        # Generate amplitude envelope
        self._generate_amplitude_envelope()
        
        # Generate mouth openness values
        self._generate_mouth_openness()
        
        return True
        
    def _extract_phonemes(self):
        """Extract phoneme information from audio data"""
        # Use librosa's onset detection to find speech segments
        onset_env = librosa.onset.onset_strength(y=self.audio_data, sr=self.sample_rate)
        
        # Find onset frames
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env, 
            sr=self.sample_rate
        )
        
        # Convert frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
        
        # Store phoneme timing information
        self.phonemes = onset_times.tolist()
        
    def _generate_amplitude_envelope(self):
        """Generate amplitude envelope from audio data"""
        # Calculate amplitude envelope
        hop_length = self.hop_length
        amplitude_envelope = np.array([
            np.max(np.abs(self.audio_data[i:i+hop_length])) 
            for i in range(0, len(self.audio_data), hop_length)
        ])
        
        # Apply smoothing to avoid jittery mouth movements
        window_size = self.window_size
        smoothed_envelope = np.convolve(
            amplitude_envelope, 
            np.ones(window_size)/window_size, 
            mode='same'
        )
        
        self.amplitude_envelope = smoothed_envelope.tolist()
        
    def _generate_mouth_openness(self):
        """Generate mouth openness values based on amplitude and phonemes"""
        if not self.amplitude_envelope:
            return
            
        # Normalize amplitude envelope
        max_amplitude = max(self.amplitude_envelope)
        if max_amplitude > 0:
            normalized_envelope = [amp / max_amplitude for amp in self.amplitude_envelope]
        else:
            normalized_envelope = [0] * len(self.amplitude_envelope)
            
        # Convert to mouth openness values (0-30 pixels)
        self.mouth_openness = [int(amp * self.max_openness) for amp in normalized_envelope]
        
        # Enhance mouth movements at phoneme positions
        if self.phonemes:
            # Convert phoneme times to frame indices
            frame_duration = self.hop_length / self.sample_rate
            phoneme_frames = [int(time / frame_duration) for time in self.phonemes]
            
            # Enhance mouth openness at phoneme positions
            for frame in phoneme_frames:
                if 0 <= frame < len(self.mouth_openness):
                    # Increase openness at phoneme positions
                    self.mouth_openness[frame] = min(
                        self.max_openness,
                        self.mouth_openness[frame] + 5
                    )
                    
    def start_processing(self, on_update: Optional[Callable[[float, int], None]] = None, 
                         on_complete: Optional[Callable[[], None]] = None):
        """
        Start processing the audio data in a separate thread.
        
        Args:
            on_update: Callback function called with (current_time, mouth_openness)
            on_complete: Callback function called when processing is complete
        """
        if not self.mouth_openness:
            return False
            
        self.on_update = on_update
        self.on_complete = on_complete
        self.is_processing = True
        self.current_frame = 0
        
        # Start processing thread
        threading.Thread(target=self._processing_thread).start()
        return True
        
    def _processing_thread(self):
        """Thread function for processing audio data"""
        try:
            # Calculate frame duration
            frame_duration = self.hop_length / self.sample_rate
            total_frames = len(self.mouth_openness)
            
            # Process each frame
            while self.is_processing and self.current_frame < total_frames:
                # Get current time and mouth openness
                current_time = self.current_frame * frame_duration
                mouth_openness = self.mouth_openness[self.current_frame]
                
                # Call update callback if provided
                if self.on_update:
                    self.on_update(current_time, mouth_openness)
                
                # Wait for next frame
                time.sleep(frame_duration)
                self.current_frame += 1
                
            # Call complete callback if provided
            if self.on_complete:
                self.on_complete()
                
        except Exception as e:
            print(f"Error in lip sync processing: {e}")
            self.is_processing = False
            
    def stop_processing(self):
        """Stop the processing thread"""
        self.is_processing = False
        
    def seek_to(self, position: float) -> bool:
        """
        Seek to a specific position in the audio.
        
        Args:
            position: Position in seconds
            
        Returns:
            bool: True if seek was successful
        """
        if not self.mouth_openness:
            return False
            
        # Calculate frame index
        frame_duration = self.hop_length / self.sample_rate
        frame_index = int(position / frame_duration)
        
        # Ensure frame index is within bounds
        if 0 <= frame_index < len(self.mouth_openness):
            self.current_frame = frame_index
            return True
            
        return False
        
    def get_current_mouth_openness(self) -> int:
        """
        Get the current mouth openness value.
        
        Returns:
            int: Current mouth openness value (0-30)
        """
        if not self.mouth_openness or self.current_frame >= len(self.mouth_openness):
            return 0
            
        return self.mouth_openness[self.current_frame]
        
    def get_mouth_shape(self, openness: int) -> str:
        """
        Get the appropriate mouth shape based on openness value.
        
        Args:
            openness: Mouth openness value (0-30)
            
        Returns:
            str: Mouth shape identifier
        """
        if openness < 5:
            return "closed"
        elif openness < 10:
            return "slightly_open"
        elif openness < 15:
            return "open"
        elif openness < 20:
            return "wide_open"
        else:
            return "very_wide_open" 