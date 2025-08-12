#!/usr/bin/env python3
"""
Startup script for LOGDTW2002 Web Server
Activates virtual environment and runs the Flask web application
"""

import os
import sys
import subprocess


def main():
    """Start the web server"""
    print("Starting LOGDTW2002 Web Server...")

    # Get current directory (web/) and parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # Check if virtual environment exists
    venv_path = os.path.join(parent_dir, "venv")
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path])

    # Determine the correct activation script and python executable
    if os.name == "nt":  # Windows
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        python_exe = os.path.join(venv_path, "bin", "python")

    # Check if web requirements exist, create if not
    web_requirements = os.path.join(current_dir, "requirements-web.txt")
    if not os.path.exists(web_requirements):
        print("Creating web requirements file...")
        requirements_content = """Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.1
Jinja2==3.1.2
itsdangerous==2.1.2
colorama==0.4.6
rich==13.7.0"""
        with open(web_requirements, "w") as f:
            f.write(requirements_content)

    # Check if Flask is available
    try:
        import flask

        print("✓ Flask found")
    except ImportError:
        print("Installing web dependencies...")
        subprocess.run([python_exe, "-m", "pip", "install", "-r", web_requirements])

    # Check if Flask-SQLAlchemy is available
    try:
        import flask_sqlalchemy

        print("✓ Flask-SQLAlchemy found")
    except ImportError:
        print("Installing Flask-SQLAlchemy...")
        subprocess.run([python_exe, "-m", "pip", "install", "Flask-SQLAlchemy"])

    # Check if game dependencies are available
    try:
        parent_requirements = os.path.join(parent_dir, "requirements.txt")
        if os.path.exists(parent_requirements):
            import rich
            import colorama

            print("✓ Game dependencies found")
    except ImportError:
        if os.path.exists(parent_requirements):
            print("Installing game dependencies...")
            subprocess.run([python_exe, "-m", "pip", "install", "-r", parent_requirements])

    # Create necessary directories
    required_dirs = ["templates", "css", "js", "web_saves", "logs"]
    for dir_name in required_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✓ Created directory: {dir_name}")

    # Run the Flask web application
    print("🚀 Launching LOGDTW2002 Web Server...")
    print("=" * 40)
    print("Web interface: http://localhost:5002")
    print("API endpoints: http://localhost:5002/api/")
    print("=" * 40)
    print("Press Ctrl+C to stop the server")

    app_path = os.path.join(current_dir, "app.py")
    subprocess.run([python_exe, app_path])


if __name__ == "__main__":
    main()
