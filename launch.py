#!/usr/bin/env python3
"""
Convenience launcher for Local Talking Avatar
Redirects to the main launch script in the backend directory
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point - redirect to backend launcher"""
    # Get the backend directory path
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    launch_script = backend_dir / 'launch_script.py'
    
    if not launch_script.exists():
        print("❌ Backend launch script not found!")
        print(f"Expected: {launch_script}")
        print("\nPlease ensure you have the complete project structure.")
        sys.exit(1)
    
    print("🚀 Starting Local Talking Avatar...")
    print(f"Redirecting to: {launch_script}")
    print()
    
    try:
        # Execute the backend launch script
        result = subprocess.run([sys.executable, str(launch_script)], 
                              cwd=str(backend_dir))
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()