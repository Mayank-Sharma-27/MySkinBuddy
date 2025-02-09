from flask import Flask, jsonify
from flask_cors import CORS
from service.websocket_service import socketio
from views import register_views
import boto3
import os
import datetime

# Create the Flask application instance
app = Flask(__name__)

# Update CORS configuration with HTTPS origins
allowed_origins = [
    "http://localhost:3000",                    # Local development
    "https://myglowpal.com",                    # Production HTTPS
    "https://www.myglowpal.com",                # Production HTTPS with www
    "http://myskinbuddy-alb-1865825031.us-east-1.elb.amazonaws.com"  # ALB direct access
]

# Configure CORS with updated origins
CORS(app, resources={  
    r"/recent-chats": {"origins": allowed_origins},
    r"/search-products": {"origins": allowed_origins},
    r"/start-chat": {"origins": allowed_origins},
    r"/product-suggestions": {"origins": allowed_origins},
    r"/chat": {"origins": allowed_origins},
    r"/auth/*": {"origins": allowed_origins},
    r"/profile": {"origins": allowed_origins},
    r"/check-message-limit": {"origins": allowed_origins},
    r"/chat/*": {"origins": allowed_origins},
    r"/health": {"origins": "*"},  # Health check can remain open
    r"/api/*": {"origins": allowed_origins}
}, 
supports_credentials=True,  # Add this if you're using cookies
methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly specify allowed methods
allow_headers=["Content-Type", "Authorization", "X-Cookie-ID"])  # Explicitly specify allowed headers

# Register all views/routes
register_views(app)

# Initialize SocketIO with the Flask app
socketio.init_app(app)

@app.route('/health')
def health_check():     
    try:
        # Test AWS connectivity
        s3 = boto3.client('s3')
        s3.list_buckets()
        return jsonify({
            'status': 'healthy',
            'aws_connectivity': True,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'aws_connectivity': False,
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
