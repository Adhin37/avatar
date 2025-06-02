"""
Local TTS Server for Avatar Application
Provides text-to-speech synthesis with phoneme timing using Coqui TTS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import json
import os
import numpy as np
import soundfile as sf
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# TTS imports
try:
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    import torch
except ImportError:
    print("Coqui TTS not installed. Install with: pip install TTS")
    exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for local development


class TTSController:
    """
    Handles text-to-speech synthesis with phoneme timing extraction.
    Uses Coqui TTS for high-quality neural speech synthesis.
    """
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        """
        Initialize the TTS controller with a specific model.
        
        Args:
            model_name (str): Name of the TTS model to use
        """
        self.model_name = model_name
        self.tts = None
        self.sample_rate = 22050
        
    def initialize(self) -> bool:
        """
        Load the TTS model and prepare for synthesis.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            print(f"Loading TTS model: {self.model_name}")
            self.tts = TTS(model_name=self.model_name, progress_bar=False)
            print("TTS model loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load TTS model: {e}")
            return False
    
    def synthesize(self, text: str, speed: float = 1.0) -> Dict:
        """
        Synthesize speech from text and extract phoneme timing.
        
        Args:
            text (str): Text to synthesize
            speed (float): Speech speed multiplier (1.0 = normal)
            
        Returns:
            dict: Contains 'audio_data' (base64 WAV) and 'phoneme_timings'
        """
        if not self.tts:
            raise RuntimeError("TTS not initialized")
        
        try:
            # Generate audio
            wav = self.tts.tts(text=text)
            
            # Convert to numpy array if needed
            if isinstance(wav, list):
                wav = np.array(wav)
            
            # Adjust speed if needed
            if speed != 1.0:
                wav = self._adjust_speed(wav, speed)
            
            # Convert to WAV format
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, wav, self.sample_rate, format='WAV')
            audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
            
            # Extract phoneme timing (simplified approach)
            phoneme_timings = self._extract_phoneme_timing(text, len(wav) / self.sample_rate)
            
            return {
                'audio_data': audio_base64,
                'phoneme_timings': phoneme_timings,
                'duration': len(wav) / self.sample_rate,
                'sample_rate': self.sample_rate
            }
            
        except Exception as e:
            raise RuntimeError(f"TTS synthesis failed: {e}")
    
    def _adjust_speed(self, wav: np.ndarray, speed: float) -> np.ndarray:
        """
        Adjust audio speed by resampling.
        
        Args:
            wav (np.ndarray): Input audio
            speed (float): Speed multiplier
            
        Returns:
            np.ndarray: Speed-adjusted audio
        """
        if speed == 1.0:
            return wav
        
        # Simple speed adjustment by changing playback rate
        # Note: This is a basic implementation. For better quality,
        # consider using librosa's time stretching
        target_length = int(len(wav) / speed)
        indices = np.linspace(0, len(wav) - 1, target_length)
        return np.interp(indices, np.arange(len(wav)), wav)
    
    def _extract_phoneme_timing(self, text: str, duration: float) -> List[Dict]:
        """
        Extract phoneme timing from text. This is a simplified implementation.
        For production use, integrate with a proper phoneme alignment tool.
        
        Args:
            text (str): Input text
            duration (float): Audio duration in seconds
            
        Returns:
            List[Dict]: Phoneme timing entries
        """
        # Simplified phoneme extraction based on text analysis
        # In a real implementation, you'd use forced alignment
        words = text.lower().split()
        phoneme_timings = []
        
        # Basic phoneme mapping for common English sounds
        phoneme_map = {
            'a': 'AH', 'e': 'EH', 'i': 'IH', 'o': 'AO', 'u': 'UH',
            'b': 'B', 'p': 'P', 'f': 'F', 'v': 'V', 'm': 'M',
            'd': 'D', 't': 'T', 'n': 'N', 'l': 'L', 'r': 'R',
            'g': 'G', 'k': 'K', 'ng': 'NG', 'h': 'HH',
            's': 'S', 'z': 'Z', 'sh': 'SH', 'zh': 'ZH',
            'ch': 'CH', 'j': 'JH', 'y': 'Y', 'w': 'W'
        }
        
        time_per_char = duration / max(len(text), 1)
        current_time = 0.0
        
        for word in words:
            for char in word:
                if char.isalpha():
                    phoneme = phoneme_map.get(char, 'SIL')
                    phoneme_timings.append({
                        'phoneme': phoneme,
                        'start_ms': int(current_time * 1000),
                        'end_ms': int((current_time + time_per_char * 3) * 1000)
                    })
                    current_time += time_per_char * 3
                else:
                    current_time += time_per_char
            
            # Add silence between words
            phoneme_timings.append({
                'phoneme': 'SIL',
                'start_ms': int(current_time * 1000),
                'end_ms': int((current_time + 0.1) * 1000)
            })
            current_time += 0.1
        
        return phoneme_timings


# Global TTS controller instance
tts_controller = TTSController()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'tts_ready': tts_controller.tts is not None})


@app.route('/synthesize', methods=['POST'])
def synthesize():
    """
    Synthesize speech from text.
    
    Expected JSON payload:
    {
        "text": "Hello world",
        "speed": 1.0
    }
    
    Returns:
    {
        "audio_data": "base64-encoded-wav",
        "phoneme_timings": [{"phoneme": "AH", "start_ms": 0, "end_ms": 120}],
        "duration": 2.5,
        "sample_rate": 22050
    }
    """
    try:
        data = request.json
        text = data.get('text', '').strip()
        speed = data.get('speed', 1.0)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        # Synthesize speech
        result = tts_controller.synthesize(text, speed)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Synthesis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/phoneme-map', methods=['GET'])
def get_phoneme_map():
    """
    Get the phoneme to viseme mapping.
    
    Returns:
    {
        "AH": 0,
        "AA": 0,
        "B": 1,
        ...
    }
    """
    # Load phoneme map from backend assets directory
    backend_dir = Path(__file__).parent
    phoneme_map_path = backend_dir / 'assets' / 'phoneme_map.json'
    
    if phoneme_map_path.exists():
        try:
            with open(phoneme_map_path, 'r') as f:
                phoneme_map = json.load(f)
        except Exception as e:
            print(f"Error loading phoneme map from {phoneme_map_path}: {e}")
            phoneme_map = get_default_phoneme_map()
    else:
        print(f"Phoneme map not found at {phoneme_map_path}, using default")
        phoneme_map = get_default_phoneme_map()
    
    return jsonify(phoneme_map)


def get_default_phoneme_map():
    """Get default phoneme to viseme mapping."""
    return {
        # Vowels - open mouth shapes
        'AH': 0, 'AA': 0, 'AO': 1, 'AW': 1, 'AY': 0,
        'EH': 2, 'ER': 2, 'EY': 2, 'IH': 3, 'IY': 3,
        'OW': 1, 'OY': 1, 'UH': 4, 'UW': 4,
        
        # Consonants - various mouth shapes
        'B': 5, 'P': 5, 'M': 5,  # Bilabial (lips together)
        'F': 6, 'V': 6,          # Labiodental (teeth on lip)
        'TH': 7, 'DH': 7,        # Dental (tongue between teeth)
        'T': 8, 'D': 8, 'N': 8, 'L': 8, 'R': 8,  # Alveolar
        'S': 9, 'Z': 9,          # Sibilants
        'SH': 10, 'ZH': 10, 'CH': 10, 'JH': 10,  # Post-alveolar
        'K': 11, 'G': 11, 'NG': 11,  # Velar
        'HH': 12, 'Y': 12, 'W': 12,  # Glottal/approximants
        'SIL': 13  # Silence/neutral
    }


def main():
    """Initialize and run the TTS server."""
    print("Initializing TTS Server...")
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    
    # Create assets directory if it doesn't exist
    assets_dir = backend_dir / 'assets'
    assets_dir.mkdir(exist_ok=True)
    
    # Initialize TTS
    if not tts_controller.initialize():
        print("Failed to initialize TTS. Please check your installation.")
        return
    
    print("TTS Server ready!")
    print("Starting server on http://localhost:5000")
    
    # Run the Flask app
    app.run(host='localhost', port=5000, debug=False)


if __name__ == '__main__':
    main()