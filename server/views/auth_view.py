from flask import Blueprint, jsonify, request, make_response
from service.auth import AuthService
from functools import wraps

auth_view = Blueprint('auth_view', __name__)
auth_service = AuthService()

def handle_auth_error(func):
    """Decorator to handle authentication errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper

@auth_view.route('/register', methods=['POST'])
@handle_auth_error
def register():
    """Register a new user with email and password"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    result = auth_service.register_user(email, password, cookie_id)
    return jsonify(result)

@auth_view.route('/login', methods=['POST'])
@handle_auth_error
def login():
    """Login with email and password"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    result = auth_service.login_user(email, password, cookie_id)
    return jsonify(result)

@auth_view.route('/google-login', methods=['POST'])
@handle_auth_error
def google_login():
    """Login with Google OAuth token"""
    data = request.get_json()
    token = data.get('token')
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not token:
        return jsonify({"error": "Google token is required"}), 400
        
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    result = auth_service.google_login(token, cookie_id)
    
    return jsonify(result)

@auth_view.route('/logout', methods=['POST'])
@handle_auth_error
def logout():
    """Logout user"""
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    # Update cookie info in S3 to mark as logged out
    cookie_data = {
        "is_logged_in": False
    }
    auth_service.cookie_service.save_cookie_data(cookie_id, cookie_data)
    
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    })

@auth_view.route('/verify', methods=['GET'])
@handle_auth_error
def verify_auth():
    """Verify if user is authenticated"""
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not cookie_id:
        return jsonify({"error": "Not authenticated"}), 401
        
    user_email = auth_service.verify_cookie(cookie_id)
    if not user_email:
        return jsonify({"error": "Not authenticated as user email not found"}), 401
        
    return jsonify({
        "status": "success",
        "authenticated": True,
        "user_email": user_email
    })

def register(app, options=None):
    """Register the blueprint with the app"""
    if options is None:
        options = {}
    app.register_blueprint(auth_view, url_prefix='/auth', **options) 