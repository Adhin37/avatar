# 🔧 Setup Guide - Local Talking Avatar

This guide will help you set up and run the Local Talking Avatar application with the new backend/frontend structure.

## 📁 Project Structure Overview

```
local-talking-avatar/
├── 🚀 launch.py              # Convenience launcher (run from project root)
├── 📦 package.json           # Root package.json with npm scripts
├── 📖 README.md              # Main documentation
├── ⚙️ SETUP.md               # This setup guide
├── 🚫 .gitignore             # Git ignore patterns
│
├── 🔧 backend/               # Python backend services
│   ├── 📊 assets/
│   │   └── phoneme_map.json  # Phoneme-to-viseme mapping
│   ├── 📋 requirements.txt   # Python dependencies
│   ├── 🎤 tts_server.py      # TTS Flask server
│   ├── ✅ setup_script.py    # Validation and setup
│   └── 🚀 launch_script.py   # Backend launcher
│
└── 🎨 frontend/              # Web frontend application
    ├── 🌐 index.html         # Main HTML page
    ├── 📦 package.json       # Frontend dependencies
    ├── 🎨 css/
    │   └── style.css         # Application styles
    └── 📜 js/
        ├── App.js            # Main application controller
        ├── AvatarController.js   # 3D avatar rendering
        ├── TTSController.js      # TTS communication
        ├── AudioPlayer.js        # Audio playback
        └── LipSyncController.js  # Lip synchronization
```

## 🚀 Quick Start (Automated)

### Option 1: Root Level Launch (Easiest)

1. **Navigate to project root**:
   ```bash
   cd local-talking-avatar
   ```

2. **Install all dependencies**:
   ```bash
   npm run setup
   ```

3. **Launch the application**:
   ```bash
   npm start
   # or
   python launch.py
   ```

### Option 2: Backend Launch Script

1. **Navigate to backend directory**:
   ```bash
   cd local-talking-avatar/backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Validate setup** (recommended):
   ```bash
   python setup_script.py
   ```

4. **Launch the application**:
   ```bash
   python launch_script.py
   ```

## 🔧 Manual Setup (Step by Step)

### Step 1: Python Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Validate backend setup**:
   ```bash
   python setup_script.py
   ```

5. **Test TTS server**:
   ```bash
   python tts_server.py
   ```
   
   Look for: `TTS Server ready!` and `Starting server on http://localhost:5000`

### Step 2: Frontend Setup

1. **Open new terminal** and navigate to frontend:
   ```bash
   cd ../frontend
   ```

2. **Install Node.js dependencies** (optional):
   ```bash
   npm install
   ```

3. **Start frontend server**:
   
   **Option A: Using npm**:
   ```bash
   npm start
   ```
   
   **Option B: Using Python**:
   ```bash
   python -m http.server 3000
   ```

### Step 3: Access Application

Open your browser to: `http://localhost:3000`

## 🐛 Troubleshooting

### Backend Issues

**TTS Server won't start**:
```bash
cd backend
python setup_script.py  # Check for issues
```

**Missing dependencies**:
```bash
pip install -r requirements.txt
```

**Port 5000 in use**:
```bash
# Check what's using port 5000
netstat -an | grep 5000
# or
lsof -i :5000
```

### Frontend Issues

**Frontend won't start**:
```bash
cd frontend
# Try Python server instead of npm
python -m http.server 3000
```

**JavaScript module errors**:
- Ensure you're accessing via `http://localhost:3000` (not `file://`)
- Check browser console for detailed error messages

### Path Issues

**Wrong directory errors**:
- Backend commands must run from `backend/` directory
- Frontend commands must run from `frontend/` directory
- Root launcher can run from project root

**File not found**:
```bash
# Verify project structure
ls -la backend/
ls -la frontend/
```

## 🔄 Development Workflow

### Starting Development

1. **Terminal 1 - Backend**:
   ```bash
   cd backend
   python tts_server.py
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd frontend
   npm start
   ```

### Code Changes

- **Backend changes**: Restart `tts_server.py`
- **Frontend changes**: Refresh browser (or use live-reload with npm)

### Testing

**Test TTS endpoint**:
```bash
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: