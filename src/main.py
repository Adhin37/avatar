"""
Avatar Lip Sync Application
Main application window and entry point.
"""

import sys
from core.app_window import AppWindow

def main():
    """Initialize and run the application"""
    try:
        app = AppWindow()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 