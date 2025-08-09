#!/usr/bin/env python3
"""
Production runner for LOGDTW2002 Flask application
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for game module imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from app import app

if __name__ == '__main__':
    # Configuration from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting LOGDTW2002 Flask Web Server")
    print("=" * 50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)
