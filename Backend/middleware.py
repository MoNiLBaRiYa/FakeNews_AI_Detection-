"""Custom middleware for Flask application."""
from functools import wraps
from flask import session, jsonify, request
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """
    Decorator to require login for routes.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "Protected content"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_json(f):
    """
    Decorator to validate JSON request body.
    
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json
        def endpoint():
            data = request.json
            return jsonify(data)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            request.get_json()
        except Exception as e:
            logger.error(f"Invalid JSON: {e}")
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def log_request(f):
    """
    Decorator to log incoming requests.
    
    Usage:
        @app.route('/api/endpoint')
        @log_request
        def endpoint():
            return "Response"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"{request.method} {request.path} - IP: {request.remote_addr}")
        return f(*args, **kwargs)
    return decorated_function
