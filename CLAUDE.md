# Local Talking Avatar - Project Memory

## Project Overview

This is a **fully local, self-contained talking avatar application** that displays a realistic, animated female avatar capable of speaking any text with synchronized lip movements. All processing happens locally without any cloud dependencies or internet connectivity requirements.

### Core Technologies
- **Backend**: Python Flask server with Coqui TTS for neural text-to-speech
- **Frontend**: HTML5/JavaScript with Three.js for 3D rendering and Web Audio API
- **Architecture**: Local client-server model (both running on localhost)

## Project Structure

```
local-talking-avatar/
├── launch.py                 # Root convenience launcher
├── package.json              # Root npm scripts for easy management
├── README.md                 # Main documentation
├── SETUP.md                  # Comprehensive setup guide
├── .gitignore                # Git ignore patterns
│
├── backend/                  # Python TTS backend
│   ├── assets/
│   │   └── phoneme_map.json  # Phoneme-to-viseme mapping (ARPABET → 0-13)
│   ├── requirements.txt      # Python dependencies (TTS, Flask, etc.)
│   ├── tts_server.py         # Main Flask server with TTS synthesis
│   ├── setup_script.py       # Installation validation and dependency checking
│   └── launch_script.py      # Automated launcher for both backend/frontend
│
└── frontend/                 # Web frontend application
    ├── index.html            # Main application page
    ├── package.json          # Frontend dependencies (live-server)
    ├── css/style.css         # Application styling (glassmorphism design)
    └── js/                   # JavaScript modules (ES6)
        ├── App.js            # Main orchestrator - coordinates all components
        ├── AvatarController.js   # 3D avatar rendering and morph targets
        ├── TTSController.js      # Communication with TTS backend
        ├── AudioPlayer.js        # Web Audio API playback and timing
        └── LipSyncController.js  # Real-time phoneme-to-viseme synchronization
```

## Architecture & Data Flow

### 1. Text-to-Speech Pipeline
```
User Input → TTSController → Flask Server → Coqui TTS → Audio + Phoneme Timings
```

### 2. Audio & Lip Sync Pipeline
```
Base64 Audio → AudioPlayer (Web Audio API) → Real-time Playback
Phoneme Timings → LipSyncController → Viseme Mapping → AvatarController → 3D Morph Targets
```

### 3. Component Communication
- **App.js**: Central orchestrator that initializes and coordinates all components
- **TTSController**: HTTP requests to Flask backend (`http://localhost:5000`)
- **AudioPlayer**: Manages audio decoding, playback, and timing queries
- **LipSyncController**: Real-time synchronization using `requestAnimationFrame`
- **AvatarController**: Three.js scene management and morph target animation

## Key Technical Details

### Backend (Python)
- **Flask Server**: Runs on `localhost:5000` with CORS enabled
- **TTS Engine**: Coqui TTS with model `tts_models/en/ljspeech/tacotron2-DDC`
- **Endpoints**:
  - `GET /health` - Server health check
  - `POST /synthesize` - Text synthesis with phoneme timing
  - `GET /phoneme-map` - Phoneme-to-viseme mapping
- **Audio Format**: Base64-encoded WAV files for web compatibility
- **Phoneme Extraction**: Simplified character-based mapping (placeholder for proper forced alignment)

### Frontend (JavaScript)
- **Three.js**: WebGL 3D rendering with PBR materials and lighting
- **Web Audio API**: Low-latency audio playback with precise timing
- **ES6 Modules**: Clean modular architecture with proper imports/exports
- **Avatar Model**: Procedural 3D head with 14 morph targets for visemes
- **Lip Sync**: 60 FPS animation with smooth interpolation between visemes

### Phoneme-to-Viseme Mapping
- **Standard**: Uses ARPABET phoneme symbols
- **Visemes**: 14 mouth shapes (0-13) covering all English speech sounds
- **Examples**:
  - Viseme 0: Open vowels (AH, AA)
  - Viseme 5: Bilabials (B, P, M)
  - Viseme 9: Sibilants (S, Z)
  - Viseme 13: Silence/neutral

## Component Responsibilities

### App.js (Main Controller)
- Application initialization and lifecycle management
- UI event handling (speak button, sliders, text input)
- Error handling and status updates
- Component coordination and cleanup

### AvatarController.js (3D Rendering)
- Three.js scene setup (camera, lighting, renderer)
- Procedural avatar creation (head, eyes, mouth, shoulders)
- Morph target animation for lip sync
- Idle animations (breathing, subtle head movement)
- Real-time rendering loop at 60 FPS

### TTSController.js (Backend Communication)
- HTTP communication with Flask TTS server
- Text validation and preprocessing
- Phoneme timing processing
- Error handling and retry logic
- Default phoneme mapping fallback

### AudioPlayer.js (Audio Management)
- Web Audio API context management
- Base64 audio decoding and buffering
- Precise playback timing for lip sync
- Volume control and audio effects
- Playback state management

### LipSyncController.js (Synchronization)
- Real-time phoneme-to-viseme mapping
- Smooth transitions between mouth shapes
- Audio timing queries and phoneme lookup
- Blend shape weight calculations
- Frame-accurate synchronization

## Important Implementation Notes

### Browser Storage Restriction
- **NEVER use localStorage or sessionStorage** - not supported in Claude.ai artifacts
- All state management uses React state or JavaScript variables
- Data persists only during the session

### Performance Considerations
- Target 60 FPS for smooth avatar animation
- Efficient morph target updates using Three.js
- Minimal DOM manipulation during playback
- Web Audio API for low-latency audio

### Error Handling Patterns
- Graceful degradation when TTS server unavailable
- User-friendly error messages in status bar
- Fallback phoneme mapping when server map fails
- Input validation for text length and content

### Development Workflow
1. **Backend Development**: Run `python tts_server.py` from `backend/`
2. **Frontend Development**: Run `npm start` from `frontend/`
3. **Full Testing**: Use `python launch_script.py` from `backend/`
4. **Validation**: Run `python setup_script.py` from `backend/`

## Configuration Points

### TTS Model Selection
- Default: `tts_models/en/ljspeech/tacotron2-DDC`
- Change in `backend/tts_server.py` → `TTSController.__init__()`
- Models auto-download on first use

### Phoneme Mapping Customization
- Edit `backend/assets/phoneme_map.json`
- Maps ARPABET phonemes to viseme indices (0-13)
- Used for lip sync accuracy

### Avatar Customization
- Currently uses procedural geometry in `AvatarController.js`
- Can be replaced with glTF loader for custom 3D models
- Requires 14 morph targets for proper lip sync

## Known Limitations & Future Improvements

### Current Limitations
- Simplified phoneme extraction (character-based, not true forced alignment)
- Procedural avatar only (no realistic human model included)
- Single voice/model support
- No emotion expression system

### Potential Enhancements
- Integration with Montreal Forced Alignment for accurate phoneme timing
- Support for multiple TTS voices and languages
- Realistic 3D avatar models with facial expressions
- Emotion and gesture systems
- Voice cloning capabilities
- Mobile app version

## Dependencies & System Requirements

### Python Backend
- Python 3.8+
- Coqui TTS (neural networks)
- Flask + Flask-CORS
- NumPy, SoundFile for audio processing
- 4GB+ RAM for TTS models

### Frontend
- Modern browser with WebGL support
- Web Audio API support
- ES6 module support
- No external JavaScript dependencies (uses CDN for Three.js)

### Development Tools
- Node.js 14+ (for development server)
- npm (for frontend package management)
- Git (for version control)

This project demonstrates a complete local AI application with real-time audio-visual synchronization, suitable for educational purposes, privacy-conscious applications, or as a foundation for more advanced avatar systems.