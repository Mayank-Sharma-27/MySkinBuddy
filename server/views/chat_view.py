from flask import Blueprint, jsonify, request, Response, stream_with_context
from service.product_chat import initialize_chat, handle_chat_message
from service.chat_service import get_total_message_count
from service.auth import AuthService
import json
import asyncio

auth_service = AuthService()

chat_view = Blueprint('chat_view', __name__)

def check_message_limit(cookie_id: str) -> dict:
    """Helper function to check if user has reached message limit"""
    user_email = auth_service.verify_cookie(cookie_id)
    if not user_email:
        message_count = get_total_message_count(cookie_id)
        if message_count >= 10:
            return {
                'error': 'Message limit reached',
                'requires_login': True,
                'message': 'Please login to continue chatting'
            }
    return None

@chat_view.route('/check-message-limit', methods=['GET'])
def get_message_limit_status():
    try:
        cookie_id = request.headers.get('X-Cookie-ID')
        if not cookie_id:
            return jsonify({'error': 'Cookie ID is required'}), 400
            
        limit_status = check_message_limit(cookie_id)
        if limit_status:
            return jsonify(limit_status), 403
            
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Error checking message limit: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_view.route('/start-chat', methods=['POST'])
def start_chat():
    try:
        data = request.get_json()
        cookie_id = request.headers.get('X-Cookie-ID')
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        if not cookie_id:
            return jsonify({'error': 'Cookie ID is required'}), 400
            
        chat_data = initialize_chat(cookie_id, product_id)
        
        return jsonify({
            'status': 'success',
            'chat_data': chat_data
        })
        
    except Exception as e:
        print(f"Error in start_chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_view.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        cookie_id = request.headers.get('X-Cookie-ID')
        product_id = data.get('product_id')
        user_message = data.get('message')
        print(f"Received message: {user_message}")
        
        if not all([cookie_id, product_id, user_message]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Use the shared helper function to check message limit
        limit_status = check_message_limit(cookie_id)
        if limit_status:
            return jsonify(limit_status), 403
        
        print("Generating response")
        def generate():
            try:
                for chunk in handle_chat_message(cookie_id, product_id, user_message):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_view.route('/chat-history/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    try:
        history = get_chat_history(cookie_id, chat_id)
        return jsonify(history)
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return jsonify({"error": str(e)}), 500

@chat_view.route('/chat/<chat_id>/history', methods=['GET'])
def get_chat_history(chat_id):
    try:
        cookie_id = request.headers.get('X-Cookie-ID')
        if not cookie_id:
            return jsonify({'error': 'Cookie ID is required'}), 400

        # Get chat data using chat service
        chat_data = get_chat(cookie_id, chat_id)
        
        if not chat_data:
            return jsonify({'error': 'Chat not found'}), 404

        return jsonify({
            'status': 'success',
            'chat_history': chat_data.get('chat_history', []),
            'preloaded_context': chat_data.get('preloaded_context', '')
        })

    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return jsonify({'error': str(e)}), 500

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(chat_view, **options) 