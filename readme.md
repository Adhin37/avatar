# Avatar Lip Sync App

A Python application that synchronizes avatar lip movements with audio playback. The app allows users to upload an avatar image and audio file, then generates lip sync animations based on the audio content.

## Features

- Upload and display avatar images
- Drag and drop or browse for audio files
- Real-time lip sync animation based on audio content
- Playback controls with waveform visualization
- Responsive UI with modern design
- Support for various audio formats (WAV, MP3, OGG)

## System Requirements

- Windows 10/11 or Linux
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

## Installation Instructions

### Option 1: Windows Native Installation

#### 1. Install Python

1. Download Python from the [official website](https://www.python.org/downloads/)
2. Run the installer and make sure to check "Add Python to PATH"
3. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

#### 2. Install Required Packages

1. Open Command Prompt and navigate to the project directory:
   ```
   cd path\to\avatar
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Option 2: WSL (Windows Subsystem for Linux) Installation

#### 1. Install WSL

1. Open PowerShell as Administrator and run:
   ```
   wsl --install
   ```
2. Restart your computer
3. Complete the Ubuntu setup by creating a username and password

#### 2. Install Python in WSL

1. Open Ubuntu terminal and update package lists:
   ```
   sudo apt update
   sudo apt upgrade
   sudo apt-get install pulseaudio pulseaudio-utils
   ```

2. Install Python and pip:
   ```
   sudo apt install python3 python3-pip
   ```

3. Verify installation:
   ```
   python3 --version
   pip3 --version
   ```

#### 3. Install Required Packages in WSL

1. Navigate to the project directory:
   ```
   cd /mnt/c/Projects/avatar
   ```

2. Install the required packages:
   ```
   pip3 install -r requirements.txt
   ```

### Option 3: Linux Native Installation

#### 1. Install Python

1. Update package lists:
   ```
   sudo apt update
   sudo apt upgrade
   ```

2. Install Python and pip:
   ```
   sudo apt install python3 python3-pip
   ```

3. Verify installation:
   ```
   python3 --version
   pip3 --version
   ```

#### 2. Install Required Packages

1. Navigate to the project directory:
   ```
   cd path/to/avatar
   ```

2. Install the required packages:
   ```
   pip3 install -r requirements.txt
   ```

## Running the Application

1. Navigate to the project directory:
   ```
   cd path/to/avatar
   ```

2. Run the application:
   ```
   python src/main.py
   ```
   or
   ```
   python3 src/main.py
   ```

## Usage

1. **Load an Avatar**: The application will automatically load the default avatar. You can replace it by dragging and dropping a new image onto the avatar area.

2. **Load Audio**: Drag and drop an audio file onto the drop zone or click to browse for a file.

3. **Playback Controls**: Use the playback controls to play, pause, and seek through the audio while watching the avatar's lip sync animation.

4. **Adjust Settings**: Use the settings menu to adjust lip sync sensitivity and other parameters.

## Troubleshooting

### Audio Device Issues

If you encounter audio device errors:

1. **Windows**: Make sure your audio drivers are up to date. Right-click the speaker icon in the taskbar, select "Open Sound settings", and check for updates.

2. **WSL**: WSL may have limited audio support. Consider using the Windows native installation for better audio support.

3. **Linux**: Check your audio configuration with:
   ```
   aplay -l
   ```
   Make sure your user has permission to access audio devices.

### Python Package Issues

If you encounter issues with Python packages:

1. Try upgrading pip:
   ```
   python -m pip install --upgrade pip
   ```

2. Install packages individually if the requirements file fails:
   ```
   pip install numpy librosa sounddevice soundfile pillow tkinterdnd2 pygame
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Librosa](https://librosa.org/) for audio processing
- [Pillow](https://python-pillow.org/) for image processing
- [TkinterDnD2](https://github.com/pmgagne/tkinterdnd2) for drag and drop functionality
- [Pygame](https://www.pygame.org/) for audio playback