from flask import Blueprint, jsonify, request, Response, stream_with_context
from service.product_chat import initialize_chat, handle_chat_message
from service.product_chat import get_chat_history
from service.cookie_service import CookieService
import json

chat_view = Blueprint('chat_view', __name__)
cookie_service = CookieService()

@chat_view.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.get_json()
    product = data.get('product')
    brand = data.get('brand')
    cookie_id = request.headers.get('X-Cookie-Id')
    image_url = data.get('image_url')
    print(f"Starting chat for {product} from {brand} with image url {image_url}")
    
    if not product or not brand:
        return jsonify({"error": "Product and brand are required"}), 400
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    try:
        chat_id = initialize_chat(cookie_id, product, brand, image_url)
        initial_message = f"👋 Hello! I'm  {brand}'s {product}! you can ask me anything and I will try to help you!"
        
        return jsonify({
            "chat_id": chat_id,
            "message": initial_message
        })
    except Exception as e:
        print(f"Error in start_chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@chat_view.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        cookie_id = request.headers.get('X-Cookie-ID')
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        response_content = ""
        sources = []
        
        message_count = cookie_service.update_message_count(cookie_id)
    
        if message_count > 5:
            cookie_data = cookie_service.get_cookie_data(cookie_id)
            if not cookie_data or not cookie_data.get('isLoggedIn'):
                return jsonify({
                    'type': 'auth_required',
                    'message': 'To continue chatting, please sign up or log in. This helps us provide you with a better experience and save your chat history.',
                    'messageCount': message_count
                }), 403
        
        for chunk in handle_chat_message(cookie_id, chat_id, message):
            if isinstance(chunk, dict) and chunk.get('type') == 'final':
                sources = chunk.get('sources', [])
            else:
                content = str(chunk)
                if "###" in content:
                    content = content.split("###")[-1].strip()
                elif "Main Response:" in content:
                    content = content.replace("Main Response:", "").strip()
                    
                if content.strip():
                    response_content += content
        
        return jsonify({
            'content': response_content,
            'sources': sources
        })
        
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