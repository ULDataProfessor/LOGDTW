#!/usr/bin/env python3
"""
Production-ready runner for LOGDTW2002 Flask application
Supports development, production, and deployment configurations
"""

import os
import sys
import signal
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path for game module imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def setup_logging(debug=False):
    """Configure logging for the application"""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    log_dir = current_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / f'logdtw-{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    return logging.getLogger('LOGDTW2002')

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def setup_virtual_environment():
    """Setup virtual environment if needed"""
    venv_path = parent_dir / 'venv'
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("Already running in virtual environment")
        return True
    
    # Check if venv exists
    if not venv_path.exists():
        logger.info("Creating virtual environment...")
        import subprocess
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True, capture_output=True)
            logger.info(f"Virtual environment created at {venv_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False
    
    # Activate virtual environment
    if os.name == 'nt':  # Windows
        activate_script = venv_path / 'Scripts' / 'activate.bat'
        python_exe = venv_path / 'Scripts' / 'python.exe'
    else:  # Unix/macOS
        activate_script = venv_path / 'bin' / 'activate'
        python_exe = venv_path / 'bin' / 'python'
    
    if python_exe.exists():
        logger.info("Virtual environment found, please activate it manually:")
        if os.name == 'nt':
            logger.info(f"  {venv_path}\\Scripts\\activate")
        else:
            logger.info(f"  source {venv_path}/bin/activate")
        logger.info("Then run this script again.")
        return False
    
    return True

def install_requirements():
    """Install required packages"""
    requirements_files = [
        current_dir / 'requirements-web.txt',
        parent_dir / 'requirements.txt'
    ]
    
    # Find requirements file
    requirements_file = None
    for req_file in requirements_files:
        if req_file.exists():
            requirements_file = req_file
            break
    
    if not requirements_file:
        logger.warning("No requirements file found, creating basic one...")
        basic_requirements = """Flask==3.0.0
Werkzeug==3.0.1
Jinja2==3.1.2
itsdangerous==2.1.2
colorama==0.4.6
pyfiglet==1.0.2
rich==13.7.0"""
        
        web_req_file = current_dir / 'requirements-web.txt'
        web_req_file.write_text(basic_requirements)
        requirements_file = web_req_file
        logger.info(f"Created basic requirements file: {requirements_file}")
    
    # Check if packages are installed
    missing_packages = []
    required_packages = ['flask', 'werkzeug', 'jinja2']
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
        logger.info(f"Installing from: {requirements_file}")
        
        import subprocess
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install requirements: {e}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            logger.info("Please install manually:")
            logger.info(f"  pip install -r {requirements_file}")
            return False
    else:
        logger.info("All required packages are already installed")
        return True

def check_environment():
    """Validate environment and dependencies"""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, got {sys.version}")
    
    # Setup virtual environment
    if not setup_virtual_environment():
        issues.append("Virtual environment setup failed")
    
    # Install requirements
    if not install_requirements():
        issues.append("Requirements installation failed")
    
    # Check required modules
    try:
        import flask
        logger.info(f"Flask version: {flask.__version__}")
    except ImportError:
        issues.append("Flask not installed - please run: pip install -r requirements-web.txt")
    
    # Check game modules
    try:
        from game.player import Player
        from game.world import World
        logger.info("Game modules loaded successfully")
    except ImportError as e:
        logger.warning(f"Game modules not available: {e}")
        logger.info("Running in basic web mode")
    
    # Check directories
    required_dirs = ['templates', 'css', 'js', 'web_saves', 'logs']
    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    if issues:
        logger.error("Environment issues found:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    
    return True

def get_config():
    """Get configuration from environment variables"""
    config = {
        'host': os.environ.get('HOST', '127.0.0.1'),
        'port': int(os.environ.get('PORT', 5000)),
        'debug': os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes'),
        'threaded': os.environ.get('THREADED', 'True').lower() in ('true', '1', 'yes'),
        'processes': int(os.environ.get('PROCESSES', 1)),
        'secret_key': os.environ.get('SECRET_KEY'),
        'env': os.environ.get('FLASK_ENV', 'development')
    }
    
    # Production safety checks
    if config['env'] == 'production':
        if not config['secret_key']:
            logger.error("SECRET_KEY must be set for production!")
            sys.exit(1)
        if config['debug']:
            logger.warning("Debug mode enabled in production - this is not recommended!")
    
    return config

def run_development_server(app, config):
    """Run Flask development server"""
    logger.info("Starting development server...")
    app.run(
        host=config['host'],
        port=config['port'],
        debug=config['debug'],
        threaded=config['threaded'],
        use_reloader=False  # Avoid double startup
    )

def run_production_server(app, config):
    """Run production server with Gunicorn if available"""
    try:
        import gunicorn.app.wsgiapp as wsgi
        
        # Gunicorn configuration
        gunicorn_config = {
            'bind': f"{config['host']}:{config['port']}",
            'workers': config['processes'] or 2,
            'worker_class': 'sync',
            'worker_connections': 1000,
            'timeout': 30,
            'keepalive': 2,
            'preload_app': True,
            'accesslog': str(current_dir / 'logs' / 'access.log'),
            'errorlog': str(current_dir / 'logs' / 'error.log'),
            'loglevel': 'info',
            'capture_output': True
        }
        
        logger.info("Starting Gunicorn production server...")
        
        # Create Gunicorn app
        class GunicornApp(wsgi.WSGIApplication):
            def init(self, parser, opts, args):
                return gunicorn_config
            
            def load(self):
                return app
        
        GunicornApp().run()
        
    except ImportError:
        logger.warning("Gunicorn not available, falling back to Flask development server")
        logger.warning("For production, install gunicorn: pip install gunicorn")
        run_development_server(app, config)

def main():
    """Main entry point"""
    global logger
    
    # Parse command line arguments
    production_mode = '--production' in sys.argv or os.environ.get('FLASK_ENV') == 'production'
    force_setup = '--setup' in sys.argv or '--install' in sys.argv
    
    # Setup logging
    logger = setup_logging(debug=not production_mode)
    
    # Show help if requested
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
LOGDTW2002 Flask Web Server

Usage:
    python run.py [options]

Options:
    --production    Run in production mode with Gunicorn
    --setup         Force virtual environment and requirements setup
    --install       Same as --setup
    --help, -h      Show this help message

Environment Variables:
    HOST            Server host (default: 127.0.0.1)
    PORT            Server port (default: 5000)
    DEBUG           Enable debug mode (default: False)
    SECRET_KEY      Flask secret key (required for production)
    FLASK_ENV       Environment mode (development/production)

Examples:
    python run.py                    # Development server
    python run.py --production       # Production server
    python run.py --setup           # Force setup and install
    
For first-time setup:
    1. python run.py --setup
    2. Activate virtual environment: source ../venv/bin/activate
    3. python run.py
        """)
        sys.exit(0)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Force setup if requested
    if force_setup:
        logger.info("🔧 Force setup mode enabled")
        logger.info("Setting up virtual environment and dependencies...")
        
        # Don't fail on environment check in setup mode
        check_environment()
        
        logger.info("✅ Setup completed!")
        logger.info("Next steps:")
        logger.info("1. Activate virtual environment: source ../venv/bin/activate")
        logger.info("2. Run the server: python run.py")
        sys.exit(0)
    
    # Environment check
    if not check_environment():
        logger.error("❌ Environment check failed!")
        logger.info("💡 Try running with --setup to automatically install dependencies:")
        logger.info("   python run.py --setup")
        sys.exit(1)
    
    # Get configuration
    config = get_config()
    
    # Import app after environment check
    try:
        from app import app
        
        # Apply configuration
        if config['secret_key']:
            app.secret_key = config['secret_key']
        
        app.config['DEBUG'] = config['debug']
        
    except ImportError as e:
        logger.error(f"Failed to import Flask app: {e}")
        sys.exit(1)
    
    # Display startup information
    logger.info("🚀 LOGDTW2002 Flask Web Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {config['env']}")
    logger.info(f"Host: {config['host']}")
    logger.info(f"Port: {config['port']}")
    logger.info(f"Debug: {config['debug']}")
    logger.info(f"Threaded: {config['threaded']}")
    if production_mode:
        logger.info(f"Workers: {config['processes']}")
    logger.info("=" * 60)
    logger.info("Game Features:")
    logger.info("  • Space Trading Simulation")
    logger.info("  • Dynamic Galaxy Generation")
    logger.info("  • Real-time Combat System")
    logger.info("  • Market Economics")
    logger.info("  • Mission System")
    logger.info("=" * 60)
    logger.info(f"Web Interface: http://{config['host']}:{config['port']}")
    logger.info(f"API Documentation: http://{config['host']}:{config['port']}/api/")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        if production_mode:
            run_production_server(app, config)
        else:
            run_development_server(app, config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
