#!/usr/bin/env python3
"""
Startup script for LOGDTW2002
Activates virtual environment and runs the game
"""

import os
import sys
import subprocess


def main():
    """Start the game"""
    print("Starting LOGDTW2002...")

    # Check if virtual environment exists
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])

    # Determine the correct activation script
    if os.name == "nt":  # Windows
        activate_script = os.path.join("venv", "Scripts", "activate")
        python_exe = os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        activate_script = os.path.join("venv", "bin", "activate")
        python_exe = os.path.join("venv", "bin", "python")

    # Check if dependencies are installed
    try:
        import rich
        import colorama

        print("✓ Dependencies found")
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"])

    # Run the game
    print("Launching LOGDTW2002...")
    subprocess.run([python_exe, "main.py"])


if __name__ == "__main__":
    main()
