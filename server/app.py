from flask import Flask, jsonify
from flask_cors import CORS
from views import product_view, search_product, chat_view, auth_view, recent_chat_view
import boto3
import os
import datetime

app = Flask(__name__)
CORS(app, resources={  
    r"/recent-chats": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/search-products": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/start-chat": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/product-suggestions": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/chat": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/auth/*": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/check-message-limit": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/chat/*": {"origins": ["http://localhost:3000", "https://myskinbuddy.com"]},
    r"/health": {"origins": ["*"]}
})

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

# Register routes
product_view.register(app, {})
search_product.register(app)
chat_view.register(app)
auth_view.register(app)
recent_chat_view.register(app)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
