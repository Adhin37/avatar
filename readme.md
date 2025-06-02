# 🗣️ Talking 3D Avatar

A self-contained application that displays a realistic, animated avatar capable of speaking any text with synchronized lip movements and facial expressions. All processing happens on your machine without any cloud dependencies or internet connectivity requirements.

![Avatar Demo](https://via.placeholder.com/800x400/4a90e2/ffffff?text=3D+Avatar+with+Facial+Expressions)

## ✨ Features

- **🎭 Realistic 3D Avatar**: Head and shoulders with advanced facial expressions
- **🗣️ Neural Text-to-Speech**: High-quality female voice using Coqui TTS
- **👄 Advanced Lip Sync**: Accurate mouth movements with coarticulation and emotional modulation
- **😊 Facial Expression System**: Real-time emotion display with 6 basic emotions plus micro-expressions
- **👁️ Eye Tracking**: Mouse-controlled eye movement with smooth interpolation
- **🎭 Context Awareness**: Automatic emotion detection from text content
- **🔄 Idle Animations**: Natural breathing, blinking, and subtle movements
- **🔒 100% Local**: No internet connection required during operation
- **⚡ Real-time Performance**: 60 FPS animation with adaptive quality
- **🎛️ Advanced Controls**: Fine-tuning for expressions, speech, and behaviors
- **📱 Responsive Design**: Works on desktop and mobile browsers

## 🏗️ Architecture

- **Backend**: Python Flask server with Coqui TTS engine
- **Frontend**: HTML5/CSS3/JavaScript with Three.js for 3D rendering
- **Audio**: Web Audio API for low-latency playback and precise timing
- **3D Rendering**: Advanced lighting, PBR materials, and post-processing effects
- **Lip Sync**: Phoneme-to-viseme mapping with emotional modulation and coarticulation
- **Facial Expressions**: 14 visemes + comprehensive emotional expression system

## 📁 Project Structure

```bash
local-talking-avatar/
├── README.md                     # This file
├── launch.py                     # Convenience launcher
├── package.json                  # Project metadata and scripts
├── .gitignore                    # Git ignore patterns
├── backend/                      # Backend services
│   ├── assets/
│   │   └── phoneme_map.json      # Phoneme to viseme mapping
│   ├── requirements.txt          # Python dependencies
│   ├── tts_server.py            # TTS backend server
│   ├── setup_script.py          # Setup validation script
│   └── launch_script.py         # Application launcher
└── frontend/                     # Frontend application
    ├── index.html               # Main application page
    ├── package.json             # Frontend dependencies
    ├── css/
    │   ├── style.css            # Base application styling
    │   └── enhanced-style.css   # Advanced UI components
    └── js/
        ├── App.js               # Main application controller
        ├── AvatarController.js  # 3D avatar with facial expressions
        ├── TTSController.js     # TTS communication
        ├── AudioPlayer.js       # Advanced audio playback
        ├── LipSyncController.js # Advanced lip synchronization
        └── EmotionAnalyzer.js   # Text emotion analysis
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 14+** with npm (optional, for development server)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **4GB+ RAM** (for TTS models)
- **2GB+ disk space** (for dependencies and models)

### Installation

1. **Clone or download** this project to your local machine

2. **Install Python dependencies**:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Install frontend development server** (optional):

   ```bash
   cd frontend
   npm install
   ```

### Running the Application

#### Option 1: Automated Launch (Recommended)

1. **Run the launch script**:

   ```bash
   python launch.py
   ```

   This will automatically:
   - Start the TTS server
   - Start the frontend server
   - Open your browser to the application

#### Option 2: Manual Launch

1. **Start the TTS server**:

   ```bash
   cd backend
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

3. **Open your browser** and navigate to:
   - `http://localhost:3000`

## 🎮 Usage

### Basic Operation

1. **Wait for initialization**: The avatar will load and the status will show "Ready to speak!"

2. **Enter text**: Type your message in the text area (up to 1000 characters)

3. **Adjust settings** (optional):
   - **Context**: Select the conversation context (greeting, question, etc.)
   - **Emotion**: Choose quick emotions or let auto-detection work
   - **Expression Intensity**: Control how pronounced expressions are
   - **Speech Speed**: 0.5x to 2.0x normal speed
   - **Volume**: 0% to 100%

4. **Click "Speak"**: The avatar will synthesize speech and animate with facial expressions

5. **Stop anytime**: Click "Stop" to interrupt playback

### Advanced Features

#### Facial Expressions

- **6 Basic Emotions**: Happy, Sad, Angry, Surprised, Fearful, Disgusted
- **Micro-expressions**: Subtle emotional hints during idle time
- **Expression Blending**: Smooth transitions between emotional states
- **Context-aware Emotions**: Automatic emotion selection based on text content

#### Eye Tracking

- **Mouse Tracking**: Enable to have the avatar's eyes follow your mouse cursor
- **Smooth Movement**: Natural eye movement with interpolation
- **Idle Behavior**: Random eye movements during pauses

#### Advanced Lip Sync

- **Coarticulation**: Natural mouth movements influenced by neighboring sounds
- **Emotional Modulation**: Lip movements affected by current emotional state
- **Adaptive Sync**: Performance optimization based on system capabilities

#### Context System

- **Auto-detection**: Analyzes text to determine context (greeting, question, etc.)
- **Emotion Mapping**: Each context has associated emotional responses
- **History Tracking**: Maintains context awareness throughout conversation

### Keyboard Shortcuts

- **Ctrl+Enter**: Start speaking (while text area is focused)
- **Escape**: Stop speaking
- **1-6**: Quick emotion selection (Neutral, Happy, Sad, Surprised, Angry, Fearful)

### Preset Messages

Use quick message buttons for common scenarios:

- **👋 Greeting**: "Hello! How are you doing today?"
- **😊 Happy**: "I'm so happy to see you! This is wonderful!"
- **❓ Question**: "Can you help me understand this better?"
- **😔 Apology**: "I'm sorry, but something went wrong."
- **🤔 Thinking**: "Let me think about this for a moment..."
- **👋 Farewell**: "Thank you and have a great day!"

## ⚙️ Configuration

### TTS Models

The application uses Coqui TTS models. The default model (`tts_models/en/ljspeech/tacotron2-DDC`) will be downloaded automatically on first use.

To use a different model, edit `backend/tts_server.py`:

```python
# Change the model name in TTSController.__init__()
self.model_name = "tts_models/en/ljspeech/glow-tts"
```

Available models can be listed with:

```bash
tts --list_models
```

### Phoneme Mapping

Customize lip sync by editing `backend/assets/phoneme_map.json`. Each phoneme maps to a viseme index (0-13):

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

Replace the procedural avatar in `frontend/js/AvatarController.js` with glTF loading:

```javascript
// In loadAvatar() method
const loader = new THREE.GLTFLoader();
const gltf = await loader.loadAsync('path/to/your/avatar.glb');
```

Ensure your model has the required blend shapes:

- 14 visemes for lip sync (viseme_0 through viseme_13)
- Basic emotions (happy, sad, angry, surprised, fearful, disgusted)
- Facial features (eyeBlinkLeft, eyeBlinkRight, eyebrowRaise, etc.)

### Expression Tuning

Adjust facial expression parameters in the avatar controller:

```javascript
// Expression blending speed (0.01 - 1.0)
this.expressionBlendSpeed = 0.08;

// Emotion decay rate (how quickly emotions fade)
this.emotionDecayRate = 0.95;

// Idle animation settings
this.idleSystem.blinkInterval = 3000; // milliseconds
this.idleSystem.breathingIntensity = 0.02;
```

## 🔧 Development

### Project Setup

1. **Validate installation**:

   ```bash
   cd backend
   python setup_script.py
   ```

2. **Run development servers**:

   ```bash
   python launch.py
   ```

### Adding New Features

The modular architecture makes it easy to extend:

- **New TTS engines**: Modify `backend/tts_server.py` and `TTSController` class
- **Avatar improvements**: Update `frontend/js/AvatarController.js` class  
- **Audio effects**: Extend `frontend/js/AudioPlayer.js` class
- **Lip sync enhancements**: Modify `frontend/js/LipSyncController.js` class
- **New emotions**: Add to `EmotionAnalyzer.js` and avatar expression system

### Code Style

- **JavaScript**: ES6+ modules, async/await, descriptive names
- **Python**: PEP 8 compliant, type hints where appropriate
- **No inline comments**: Self-documenting code with JSDoc comments only above functions
- **Modular design**: Each component handles a single responsibility

### Testing

Test the TTS server:

```bash
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "speed": 1.0}'
```

Test avatar expressions via browser console:

```javascript
// Set emotion
window.setEmotion('happy', 0.8);

// Set context
window.setContext('greeting');

// Analyze text emotion
window.analyzeEmotion('I am so excited!');

// Get system status
window.getSystemStatus();
```

## 🐛 Troubleshooting

### Common Issues

**TTS Server won't start**:

- Check Python version: `python --version` (need 3.8+)
- Install missing dependencies: `pip install -r backend/requirements.txt`
- Check port 5000 isn't in use: `netstat -an | grep 5000`

**Avatar won't load**:

- Check browser console for JavaScript errors
- Ensure WebGL is supported: visit `about:support` (Firefox) or `chrome://gpu` (Chrome)
- Try a different browser

**Facial expressions not working**:

- Check if Three.js loaded correctly
- Verify avatar model has proper morph targets
- Check browser console for WebGL errors

**Lip sync issues**:

- Verify TTS server is responding: visit `http://localhost:5000/health`
- Check browser console for timing errors
- Ensure audio is playing correctly first

**Performance issues**:

- Close other browser tabs
- Reduce system load
- Enable adaptive quality in avatar settings
- Try lower expression intensity

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
4. **Lip Sync** → Advanced phoneme-to-viseme mapping with coarticulation

### 3D Rendering Pipeline

- **Engine**: Three.js with WebGL 2.0
- **Lighting**: Physically-based with multiple light sources
- **Materials**: PBR with subsurface scattering simulation
- **Animation**: Morph targets for facial expressions and visemes
- **Performance**: 60 FPS target with adaptive quality management

### Facial Expression System

1. **Text Analysis** → Emotion detection and context awareness
2. **Expression Mapping** → Emotion to facial morph target conversion
3. **Blending** → Smooth transitions between expressions
4. **Modulation** → Lip sync influenced by current emotional state
5. **Idle Behavior** → Natural micro-expressions and movements

### Lip Sync Algorithm

1. **Phoneme Extraction** from TTS engine with timing data
2. **Viseme Mapping** using phonetic rules and context
3. **Coarticulation** → Natural mouth shape transitions
4. **Emotional Modulation** → Expression-influenced lip movements
5. **Real-time Application** → 60 FPS synchronized animation

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Submit a pull request

### Ideas for Contributions

- Additional TTS engine support (Festival, eSpeak, etc.)
- More realistic avatar models with better blend shapes
- Advanced emotion system with more nuanced expressions
- Voice cloning capabilities
- Mobile app version
- VR/AR support
- Multi-language support

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Coqui TTS** team for the excellent neural TTS engine
- **Three.js** contributors for the powerful 3D graphics library
- **Mozilla** for Web Audio API standards
- **ARPABET** phoneme standard for speech processing
- **OpenAI** for inspiration in conversational AI interfaces

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Run the setup validation: `python backend/setup_script.py`
3. Search existing GitHub issues
4. Create a new issue with:
   - System information (OS, browser, hardware)
   - Browser details and WebGL support status
   - Console error messages
   - Steps to reproduce the issue

### Advanced Debugging

Enable debug mode in the interface for detailed expression and timing information. You can also use browser console commands:

```javascript
// Get detailed status
console.log(window.getSystemStatus());

// Monitor expression states
setInterval(() => {
    if (window.app && window.app.avatarController) {
        console.log(window.app.avatarController.getExpressionStates());
    }
}, 1000);

// Check lip sync status
if (window.app && window.app.lipSyncController) {
    window.app.lipSyncController.logCurrentTiming();
}
```

---

**Built with ❤️ for realistic human-AI interaction** - Enjoy your advanced talking avatar!
