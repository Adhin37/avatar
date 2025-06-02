#!/usr/bin/env python3
"""
Setup and Validation Script for Local Talking Avatar
Checks dependencies, validates installation, and provides setup assistance
"""

import sys
import subprocess
import importlib
import os
import json
import platform
import shutil
from pathlib import Path

class SetupValidator:
    """Validates and assists with application setup"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_messages = []
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        else:
            self.success_messages.append(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
            return True
    
    def check_required_packages(self):
        """Check if required Python packages are installed"""
        required_packages = {
            'TTS': 'Coqui TTS engine',
            'torch': 'PyTorch for neural networks',
            'flask': 'Web server framework',
            'flask_cors': 'CORS support',
            'soundfile': 'Audio file processing',
            'numpy': 'Numerical computing'
        }
        
        missing_packages = []
        
        for package, description in required_packages.items():
            try:
                importlib.import_module(package)
                self.success_messages.append(f"✓ {package} ({description}) is installed")
            except ImportError:
                missing_packages.append(package)
                self.errors.append(f"✗ {package} ({description}) is missing")
        
        if missing_packages:
            self.errors.append("Install missing packages with: pip install -r requirements.txt")
            return False
        
        return True
    
    def check_optional_packages(self):
        """Check optional packages that enhance functionality"""
        optional_packages = {
            'librosa': 'Advanced audio processing',
            'phonemizer': 'Improved phoneme extraction',
            'matplotlib': 'Visualization tools'
        }
        
        for package, description in optional_packages.items():
            try:
                importlib.import_module(package)
                self.success_messages.append(f"✓ {package} ({description}) is available")
            except ImportError:
                self.warnings.append(f"◉ {package} ({description}) not installed (optional)")
    
    def check_node_npm(self):
        """Check if Node.js and npm are available for development server"""
        try:
            node_version = subprocess.check_output(['node', '--version'], 
                                                 stderr=subprocess.DEVNULL).decode().strip()
            npm_version = subprocess.check_output(['npm', '--version'], 
                                                stderr=subprocess.DEVNULL).decode().strip()
            
            self.success_messages.append(f"✓ Node.js {node_version} and npm {npm_version} available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.warnings.append("◉ Node.js/npm not found (optional for development server)")
            self.warnings.append("  You can still use Python's built-in server: python -m http.server")
            return False
    
    def check_project_structure(self):
        """Validate project file structure"""
        required_files = [
            'tts_server.py',
            'requirements.txt',
            'backend/assets/phoneme_map.json',
            'frontend/index.html',
            'frontend/js/App.js',
            'frontend/js/AvatarController.js',
            'frontend/js/TTSController.js',
            'frontend/js/AudioPlayer.js',
            'frontend/js/LipSyncController.js'
        ]
        
        missing_files = []
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.success_messages.append(f"✓ {file_path} exists")
            else:
                missing_files.append(file_path)
                self.errors.append(f"✗ {file_path} is missing")
        
        if missing_files:
            self.errors.append("Some required project files are missing")
            return False
        
        return True
    
    def check_phoneme_map(self):
        """Validate phoneme mapping file"""
        phoneme_map_path = 'backend/assets/phoneme_map.json'
        
        try:
            with open(phoneme_map_path, 'r') as f:
                phoneme_map = json.load(f)
            
            # Check for required phonemes
            required_phonemes = ['AH', 'B', 'S', 'SIL']
            missing_phonemes = [p for p in required_phonemes if p not in phoneme_map]
            
            if missing_phonemes:
                self.warnings.append(f"◉ Phoneme map missing: {missing_phonemes}")
            else:
                self.success_messages.append(f"✓ Phoneme map contains {len(phoneme_map)} entries")
            
            return True
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.errors.append(f"✗ Invalid phoneme map: {e}")
            return False
    
    def check_system_resources(self):
        """Check system resources for TTS requirements"""
        import psutil
        
        # Check available RAM
        total_ram = psutil.virtual_memory().total / (1024**3)  # GB
        available_ram = psutil.virtual_memory().available / (1024**3)  # GB
        
        if total_ram < 4:
            self.warnings.append(f"◉ Low RAM: {total_ram:.1f}GB (4GB+ recommended)")
        else:
            self.success_messages.append(f"✓ Sufficient RAM: {total_ram:.1f}GB total, {available_ram:.1f}GB available")
        
        # Check disk space
        disk_usage = psutil.disk_usage('.')
        free_space = disk_usage.free / (1024**3)  # GB
        
        if free_space < 2:
            self.warnings.append(f"◉ Low disk space: {free_space:.1f}GB (2GB+ recommended)")
        else:
            self.success_messages.append(f"✓ Sufficient disk space: {free_space:.1f}GB available")
    
    def test_tts_functionality(self):
        """Test TTS engine functionality"""
        try:
            from TTS.api import TTS
            
            # Try to initialize a simple model
            print("Testing TTS engine (this may take a moment for first-time setup)...")
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            
            # Test synthesis
            test_text = "Hello world"
            wav = tts.tts(text=test_text)
            
            if wav and len(wav) > 0:
                self.success_messages.append("✓ TTS engine working correctly")
                return True
            else:
                self.errors.append("✗ TTS engine test failed")
                return False
                
        except Exception as e:
            self.errors.append(f"✗ TTS engine error: {e}")
            return False
    
    def create_assets_directory(self):
        """Create assets directory if it doesn't exist"""
        assets_dir = Path('assets')
        if not assets_dir.exists():
            assets_dir.mkdir()
            self.success_messages.append("✓ Created assets directory")
    
    def validate_frontend_assets(self):
        """Check if frontend assets are properly accessible"""
        frontend_dir = Path('frontend')
        if not frontend_dir.exists():
            self.errors.append("✗ Frontend directory not found")
            return False
        
        # Check if JavaScript modules are using proper import/export
        js_files = ['App.js', 'AvatarController.js', 'TTSController.js', 
                   'AudioPlayer.js', 'LipSyncController.js']
        
        for js_file in js_files:
            js_path = frontend_dir / 'js' / js_file
            if js_path.exists():
                try:
                    with open(js_path, 'r') as f:
                        content = f.read()
                    
                    if 'export' in content:
                        self.success_messages.append(f"✓ {js_file} uses ES6 modules")
                    else:
                        self.warnings.append(f"◉ {js_file} may not be properly exported")
                        
                except Exception as e:
                    self.warnings.append(f"◉ Could not validate {js_file}: {e}")
        
        return True
    
    def run_full_validation(self):
        """Run complete validation suite"""
        print("🔍 Validating Local Talking Avatar Setup...")
        print("=" * 50)
        
        # Create assets directory if needed
        self.create_assets_directory()
        
        # Core validations
        self.check_python_version()
        self.check_required_packages()
        self.check_optional_packages()
        self.check_project_structure()
        self.check_phoneme_map()
        self.validate_frontend_assets()
        
        # System checks
        try:
            import psutil
            self.check_system_resources()
        except ImportError:
            self.warnings.append("◉ psutil not available - skipping system resource check")
        
        # Optional tools
        self.check_node_npm()
        
        # Print results
        self.print_results()
        
        # TTS test (optional, can be slow)
        if len(self.errors) == 0:
            test_tts = input("\n🧪 Test TTS engine? (may download models) [y/N]: ").lower().strip()
            if test_tts == 'y':
                self.test_tts_functionality()
                self.print_results()
        
        return len(self.errors) == 0
    
    def print_results(self):
        """Print validation results"""
        if self.success_messages:
            print("\n✅ Success:")
            for msg in self.success_messages:
                print(f"  {msg}")
        
        if self.warnings:
            print("\n⚠️ Warnings:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\n❌ Errors:")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "=" * 50)
        
        if self.errors:
            print("❌ Setup validation failed. Please fix the errors above.")
            print("\n💡 Quick fixes:")
            print("  • Install Python dependencies: pip install -r requirements.txt")
            print("  • Check Python version: python --version")
            print("  • Verify project files are in the correct locations")
        else:
            print("✅ Setup validation successful!")
            print("\n🚀 To start the application:")
            print("  1. Run: python tts_server.py")
            print("  2. In another terminal: cd frontend && npm start")
            print("  3. Open: http://localhost:3000")


def main():
    """Main setup script entry point"""
    validator = SetupValidator()
    
    print("🎭 Local Talking Avatar - Setup Validator")
    print(f"Python {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    success = validator.run_full_validation()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
