from flask import Blueprint, jsonify, request
from service.user_profile import UserProfileService
from service.auth import AuthService
from functools import wraps

user_profile_view = Blueprint('user_profile_view', __name__)
user_profile_service = UserProfileService()
auth_service = AuthService()

def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            cookie_id = request.headers.get('X-Cookie-ID')
            if not cookie_id:
                return jsonify({"error": "Not authenticated"}), 401
                
            user_email = auth_service.verify_cookie(cookie_id)
            if not user_email:
                return jsonify({"error": "Not authenticated"}), 401
                
            return func(user_email, *args, **kwargs)
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper

@user_profile_view.route('/profile', methods=['POST'])
@require_auth
def save_profile(user_email):
    """Save user profile information"""
    try:
        data = request.get_json()
        skin_type = data.get('skin_type')
        skin_issues = data.get('skin_issues', [])
        additional_info = data.get('additional_info', '')
        location = data.get('location', '')
        
        if not skin_type:
            return jsonify({"error": "Skin type is required"}), 400
            
        result = user_profile_service.save_user_info(
            user_email=user_email,
            skin_type=skin_type,
            skin_issues=skin_issues,
            additional_info=additional_info,
            location=location
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error saving profile: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@user_profile_view.route('/profile', methods=['GET'])
@require_auth
def get_profile(user_email):
    """Get user profile information"""
    try:
        user_info = user_profile_service.get_user_info(user_email)
        if not user_info:
            return jsonify({
                "skin_type": "",
                "skin_issues": [],
                "additional_info": "",
                "location": ""
            })
        return jsonify(user_info)
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def register(app, options=None):
    """Register the blueprint with the app"""
    if options is None:
        options = {}
    app.register_blueprint(user_profile_view, **options) 