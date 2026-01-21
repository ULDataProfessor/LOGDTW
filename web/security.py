"""
Security utilities for the web application
Includes rate limiting, CSRF protection, and input validation
"""
from functools import wraps
from flask import request, jsonify, session, g
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import secrets
import re


# Simple in-memory rate limiter (for production, use Redis or similar)
_rate_limit_storage = defaultdict(list)


def rate_limit(max_requests=60, window_seconds=60, per_ip=True):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        per_ip: If True, rate limit per IP address; if False, per session
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get identifier (IP or session)
            if per_ip:
                identifier = request.remote_addr or 'unknown'
            else:
                identifier = session.get('session_id', 'anonymous')
            
            # Clean old entries
            now = datetime.now()
            cutoff = now - timedelta(seconds=window_seconds)
            _rate_limit_storage[identifier] = [
                timestamp for timestamp in _rate_limit_storage[identifier]
                if timestamp > cutoff
            ]
            
            # Check rate limit
            if len(_rate_limit_storage[identifier]) >= max_requests:
                return jsonify({
                    'success': False,
                    'message': f'Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.'
                }), 429
            
            # Add current request
            _rate_limit_storage[identifier].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# CSRF token management
def generate_csrf_token():
    """Generate a CSRF token"""
    return secrets.token_urlsafe(32)


def get_csrf_token():
    """Get or create CSRF token for current session"""
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    return session['csrf_token']


def require_csrf(f):
    """Decorator to require CSRF token for POST/PUT/DELETE requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Get token from header or form data
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token') or request.json.get('csrf_token') if request.is_json else None
            
            session_token = session.get('csrf_token')
            
            if not token or not session_token or token != session_token:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or missing CSRF token'
                }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # CSP: Allow data URIs for images, Google Fonts for styles, and self for everything else
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response


# Input validation functions
def validate_sector_number(sector):
    """Validate sector number"""
    try:
        sector_int = int(sector)
        return 1 <= sector_int <= 1000
    except (ValueError, TypeError):
        return False


def validate_quantity(quantity):
    """Validate item quantity"""
    try:
        qty_int = int(quantity)
        return qty_int > 0 and qty_int <= 10000  # Reasonable upper limit
    except (ValueError, TypeError):
        return False


def validate_item_name(item_name):
    """Validate item name (prevent injection)"""
    if not item_name or not isinstance(item_name, str):
        return False
    
    # Allow alphanumeric, spaces, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', item_name):
        return False
    
    # Length check
    if len(item_name) > 100:
        return False
    
    return True


def validate_string_input(text, max_length=1000, allow_empty=False):
    """Validate string input"""
    if not isinstance(text, str):
        return False
    
    if not allow_empty and not text.strip():
        return False
    
    if len(text) > max_length:
        return False
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'data:text/html',
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower):
            return False
    
    return True


def sanitize_input(text):
    """Sanitize user input"""
    if not isinstance(text, str):
        return str(text) if text is not None else ''
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    return text


def validate_json_structure(data, required_fields=None, optional_fields=None):
    """Validate JSON structure"""
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
    
    if optional_fields:
        for field in data:
            if field not in (required_fields or []) and field not in optional_fields:
                return False, f"Unknown field: {field}"
    
    return True, None


# Rate limiter instance (for use with Flask-Limiter if available)
rate_limiter = None

# CSRF protection instance
csrf_protection = None
