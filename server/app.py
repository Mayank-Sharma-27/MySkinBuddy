from flask import Flask, jsonify
from flask_cors import CORS
from service.websocket_service import socketio
from views import register_views
import boto3
import os
import datetime

# Create the Flask application instance
app = Flask(__name__)

# Configure CORS globally with all necessary settings
CORS(app, resources={  
    r"/recent-chats": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/search-products": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/start-chat": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/product-suggestions": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/chat": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/auth/*": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/profile": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/check-message-limit": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/chat/*": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/health": {"origins": ["*"]}
})

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
