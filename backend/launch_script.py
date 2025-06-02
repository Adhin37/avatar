#!/usr/bin/env python3
"""
Launch Script for Local Talking Avatar
Starts both TTS server and frontend development server
"""

import subprocess
import sys
import time
import os
import signal
import threading
import webbrowser
from pathlib import Path

class AvatarLauncher:
    """Manages launching and coordination of avatar application components"""
    
    def __init__(self):
        self.tts_process = None
        self.frontend_process = None
        self.should_stop = False
        
        # Get project root (parent of backend directory)
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent
        self.frontend_dir = self.project_root / 'frontend'
        
    def check_dependencies(self):
        """Quick dependency check before launch"""
        try:
            import flask
            import TTS
            print("✓ Core dependencies found")
            return True
        except ImportError as e:
            print(f"❌ Missing dependencies: {e}")
            print("Please run: pip install -r backend/requirements.txt")
            return False
    
    def start_tts_server(self):
        """Start the TTS backend server"""
        print("🚀 Starting TTS server...")
        
        try:
            # Change to backend directory for TTS server
            tts_server_path = self.backend_dir / 'tts_server.py'
            
            self.tts_process = subprocess.Popen(
                [sys.executable, str(tts_server_path)],
                cwd=str(self.backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor TTS server startup in background thread
            def monitor_tts():
                for line in iter(self.tts_process.stdout.readline, ''):
                    if line.strip():
                        print(f"TTS: {line.strip()}")
                        if "TTS Server ready!" in line:
                            print("✅ TTS server is ready")
                        if "Starting server on" in line:
                            print("✅ TTS server started successfully")
            
            threading.Thread(target=monitor_tts, daemon=True).start()
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Check if process is still running
            if self.tts_process.poll() is None:
                return True
            else:
                print("❌ TTS server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start TTS server: {e}")
            return False
    
    def start_frontend_server(self):
        """Start the frontend development server"""
        print("🌐 Starting frontend server...")
        
        if not self.frontend_dir.exists():
            print(f"❌ Frontend directory not found: {self.frontend_dir}")
            return False
        
        # Try npm start first, fall back to Python server
        try:
            # Check if package.json exists and npm is available
            if (self.frontend_dir / 'package.json').exists():
                try:
                    subprocess.check_output(['npm', '--version'], stderr=subprocess.DEVNULL)
                    print("📦 Using npm development server...")
                    
                    self.frontend_process = subprocess.Popen(
                        ['npm', 'start'],
                        cwd=str(self.frontend_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    # Monitor frontend server
                    def monitor_frontend():
                        for line in iter(self.frontend_process.stdout.readline, ''):
                            if line.strip() and not line.startswith('npm'):
                                print(f"Frontend: {line.strip()}")
                    
                    threading.Thread(target=monitor_frontend, daemon=True).start()
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("⚠️ npm not available, falling back to Python server")
                    raise FileNotFoundError("npm not found")
                    
            else:
                raise FileNotFoundError("package.json not found")
                
        except (FileNotFoundError, Exception):
            # Fall back to Python's built-in server
            print("🐍 Using Python development server...")
            
            self.frontend_process = subprocess.Popen(
                [sys.executable, '-m', 'http.server', '3000'],
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        
        # Wait for frontend server to start
        time.sleep(2)
        
        if self.frontend_process and self.frontend_process.poll() is None:
            print("✅ Frontend server started successfully")
            return True
        else:
            print("❌ Frontend server failed to start")
            return False
    
    def open_browser(self):
        """Open the application in the default browser"""
        print("🌐 Opening browser...")
        
        try:
            webbrowser.open('http://localhost:3000')
            print("✅ Browser opened to http://localhost:3000")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print("Please manually open: http://localhost:3000")
    
    def wait_for_servers(self):
        """Wait for both servers to be ready"""
        print("⏳ Waiting for servers to initialize...")
        
        max_wait = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.should_stop:
                return False
                
            # Check if both processes are still running
            tts_running = self.tts_process and self.tts_process.poll() is None
            frontend_running = self.frontend_process and self.frontend_process.poll() is None
            
            if tts_running and frontend_running:
                print("✅ Both servers are running")
                return True
            
            time.sleep(1)
        
        print("❌ Timeout waiting for servers to start")
        return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print("\n🛑 Shutdown signal received...")
            self.should_stop = True
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Clean up running processes"""
        print("🧹 Cleaning up...")
        
        if self.tts_process:
            try:
                self.tts_process.terminate()
                self.tts_process.wait(timeout=5)
                print("✅ TTS server stopped")
            except subprocess.TimeoutExpired:
                self.tts_process.kill()
                print("⚠️ TTS server force killed")
            except Exception as e:
                print(f"⚠️ Error stopping TTS server: {e}")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend server stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("⚠️ Frontend server force killed")
            except Exception as e:
                print(f"⚠️ Error stopping frontend server: {e}")
    
    def run(self):
        """Main launch sequence"""
        print("🎭 Local Talking Avatar Launcher")
        print("=" * 40)
        print(f"Project root: {self.project_root}")
        print(f"Backend dir: {self.backend_dir}")
        print(f"Frontend dir: {self.frontend_dir}")
        print("=" * 40)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Quick dependency check
        if not self.check_dependencies():
            return False
        
        try:
            # Start TTS server
            if not self.start_tts_server():
                print("❌ Failed to start TTS server")
                return False
            
            # Start frontend server
            if not self.start_frontend_server():
                print("❌ Failed to start frontend server")
                self.cleanup()
                return False
            
            # Wait for servers to be ready
            if not self.wait_for_servers():
                print("❌ Servers failed to start properly")
                self.cleanup()
                return False
            
            # Open browser
            self.open_browser()
            
            print("\n" + "=" * 40)
            print("🎉 Local Talking Avatar is running!")
            print("📱 Frontend: http://localhost:3000")
            print("🔧 TTS API: http://localhost:5000")
            print("⌨️  Press Ctrl+C to stop")
            print("=" * 40)
            
            # Keep the script running
            while not self.should_stop:
                time.sleep(1)
                
                # Check if processes are still alive
                if self.tts_process and self.tts_process.poll() is not None:
                    print("❌ TTS server stopped unexpectedly")
                    break
                    
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend server stopped unexpectedly")
                    break
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            return True
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    launcher = AvatarLauncher()
    
    # Show usage instructions
    print("This script will start both the TTS backend and frontend servers.")
    print("Make sure you have installed all dependencies first:")
    print("  pip install -r backend/requirements.txt")
    print("  cd frontend && npm install")
    print()
    
    # Ask for confirmation
    response = input("Start the Local Talking Avatar application? [Y/n]: ").strip().lower()
    if response and response not in ['y', 'yes']:
        print("Cancelled.")
        return
    
    print()
    success = launcher.run()
    
    if success:
        print("👋 Thanks for using Local Talking Avatar!")
    else:
        print("❌ Application failed to start properly")
        print("💡 Try running backend/setup_script.py first to check for issues")
        sys.exit(1)


if __name__ == "__main__":
    main()