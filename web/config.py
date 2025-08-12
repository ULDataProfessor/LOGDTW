#!/usr/bin/env python3
"""
Configuration for LOGDTW2002 Flask application
"""

import os
from pathlib import Path


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
    DEBUG = False
    TESTING = False

    # Game-specific settings
    GAME_SAVE_DIRECTORY = "web_saves"
    MAX_SECTORS = 1000
    AUTO_SAVE_INTERVAL = 300  # seconds

    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SECRET_KEY = "dev-secret-key"


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production")


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SECRET_KEY = "testing-key"
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
