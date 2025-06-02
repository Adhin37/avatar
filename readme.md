# 🗣️ Local Talking Avatar

A **fully local**, self-contained application that displays a realistic, animated female avatar capable of speaking any text with synchronized lip movements. All processing happens on your machine without any cloud dependencies or internet connectivity requirements.

![Avatar Demo](https://via.placeholder.com/800x400/4a90e2/ffffff?text=Avatar+Speaking+Demo)

## ✨ Features

- **🎭 Realistic 3D Avatar**: Head and shoulders with physically-based rendering
- **🗣️ Neural Text-to-Speech**: High-quality female voice using Coqui TTS
- **👄 Real-time Lip Sync**: Accurate mouth movements synchronized to speech
- **🔒 100% Local**: No internet connection required during operation
- **⚡ Real-time Performance**: 30+ FPS animation with low-latency audio
- **🎛️ User Controls**: Adjustable speech speed and volume
- **📱 Responsive Design**: Works on desktop and mobile browsers

## 🏗️ Architecture

- **Backend**: Python Flask server with Coqui TTS engine
- **Frontend**: HTML5/CSS3/JavaScript with Three.js for 3D rendering
- **Audio**: Web Audio API for low-latency playback and timing
- **Lip Sync**: Phoneme-to-viseme mapping with smooth interpolation

## 📁 Project Structure

```
local-talking-avatar/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── tts_server.py            # TTS backend server
├── assets/
│   └── phoneme_map.json     # Phoneme to viseme mapping
├── frontend/
│   ├── index.html           # Main application page
│   ├── package.json         # Frontend dependencies
│   └── js/
│       ├── App.js           # Main application controller
│       ├── AvatarController.js    # 3D avatar rendering
│       ├── TTSController.js       # TTS communication
│       ├── AudioPlayer.js         # Audio playback
│       └── LipSyncController.js   # Lip synchronization
└── docs/                    # Additional documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 14+** with npm (for development server)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **4GB+ RAM** (for TTS models)
- **2GB+ disk space** (for dependencies and models)

### Installation

1. **Clone or download** this project to your local machine

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend development server** (optional):
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the TTS server**:
   ```bash
   python tts_server.py
   ```
   
   Wait for the message: `TTS Server ready!` and `Starting server on http://localhost:5000`

2. **Start the frontend** (choose one method):
   
   **Option A: Using npm (recommended)**:
   ```bash
   cd frontend
   npm start
   ```
   
   **Option B: Using Python's built-in server**:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   
   **Option C: Using any local web server**:
   - Serve the `frontend/` directory on any port
   - Open `index.html` in your browser

3. **Open your browser** and navigate to:
   - `http://localhost:3000` (if using npm or Python server)
   - Or open `frontend/index.html` directly in your browser

## 🎮 Usage

1. **Wait for initialization**: The avatar will load and the status will show "Ready to speak!"

2. **Enter text**: Type your message in the text area (up to 1000 characters)

3. **Adjust settings** (optional):
   - **Speech Speed**: 0.5x to 2.0x normal speed
   - **Volume**: 0% to 100%

4. **Click "Speak"**: The avatar will synthesize speech and animate lip movements

5. **Stop anytime**: Click "Stop" to interrupt playback

### Keyboard Shortcuts

- **Ctrl+Enter**: Start speaking (while text area is focused)
- **Escape**: Stop speaking

## ⚙️ Configuration

### TTS Models

The application uses Coqui TTS models. The default model (`tts_models/en/ljspeech/tacotron2-DDC`) will be downloaded automatically on first use.

To use a different model, edit `tts_server.py`:

```python
# Change the model name in TTSController.__init__()
self.model_name = "tts_models/en/ljspeech/glow-tts"
```

Available models can be listed with:
```bash
tts --list_models
```

### Phoneme Mapping

Customize lip sync by editing `assets/phoneme_map.json`. Each phoneme maps to a viseme index (0-13):

```json
{
  "AH": 0,  // Open mouth (ah)
  "B": 5,   // Lips together (b, p, m)
  "S": 9,   // Sibilant (s, z)
  "SIL": 13 // Silence/neutral
}
```

### Avatar Customization

To use a custom 3D avatar:

1. Replace the procedural avatar in `AvatarController.js` with glTF loading:
```javascript
// In loadAvatar() method
const loader = new THREE.GLTFLoader();
const gltf = await loader.loadAsync('path/to/your/avatar.glb');
```

2. Ensure your model has 14 blend shapes for visemes 0-13

## 🔧 Development

### Adding New Features

The modular architecture makes it easy to extend:

- **New TTS engines**: Modify `TTSController` class
- **Avatar improvements**: Update `AvatarController` class  
- **Audio effects**: Extend `AudioPlayer` class
- **Enhanced lip sync**: Modify `LipSyncController` class

### Code Style

- **JavaScript**: ES6+ modules, async/await, descriptive names
- **Python**: PEP 8 compliant, type hints where appropriate
- **Comments**: Comprehensive documentation for all public methods

### Testing

Test the TTS server:
```bash
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "speed": 1.0}'
```

## 🐛 Troubleshooting

### Common Issues

**TTS Server won't start**:
- Check Python version: `python --version` (need 3.8+)
- Install missing dependencies: `pip install -r requirements.txt`
- Check port 5000 isn't in use: `netstat -an | grep 5000`

**Avatar won't load**:
- Check browser console for JavaScript errors
- Ensure WebGL is supported: visit `about:support` (Firefox) or `chrome://gpu` (Chrome)
- Try a different browser

**No audio playback**:
- Check browser audio permissions
- Try clicking in the page first (Chrome autoplay policy)
- Check system volume and browser tab audio settings

**Lip sync not working**:
- Verify TTS server is responding: visit `http://localhost:5000/health`
- Check browser console for timing errors
- Ensure audio is playing correctly first

**Performance issues**:
- Close other browser tabs
- Reduce system load
- Try a lower speech speed setting

### System Requirements

**Minimum**:
- 4GB RAM, dual-core CPU
- Integrated graphics with WebGL support
- 2GB free disk space

**Recommended**:
- 8GB+ RAM, quad-core CPU
- Dedicated graphics card
- SSD storage

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | 80+     | ✅ Full support |
| Firefox | 75+     | ✅ Full support |
| Safari  | 13+     | ✅ Full support |
| Edge    | 80+     | ✅ Full support |

## 📚 Technical Details

### Audio Pipeline

1. **Text Input** → TTS synthesis with phoneme timing
2. **Base64 Audio** → Web Audio API decoding  
3. **Playback** → Real-time timing queries
4. **Lip Sync** → Phoneme-to-viseme mapping

### 3D Rendering

- **Engine**: Three.js with WebGL renderer
- **Lighting**: Physically-based with multiple light sources
- **Animation**: Morph targets for facial expressions
- **Performance**: 60 FPS target with LOD optimization

### Lip Sync Algorithm

1. **Phoneme Extraction** from TTS engine
2. **Timing Alignment** with audio samples
3. **Viseme Mapping** using phonetic rules
4. **Smooth Interpolation** between mouth shapes
5. **Real-time Application** to 3D model

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Ideas for Contributions

- Additional TTS engine support (Festival, eSpeak, etc.)
- More realistic avatar models
- Emotion expression system
- Voice cloning capabilities
- Mobile app version
- Performance optimizations

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Coqui TTS** team for the excellent TTS engine
- **Three.js** contributors for the 3D graphics library
- **Mozilla** for Web Audio API documentation
- **ARPABET** phoneme standard for speech processing

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with:
   - System information
   - Browser details
   - Console error messages
   - Steps to reproduce

---

**Built with ❤️ for the community** - Enjoy your local talking avatar!