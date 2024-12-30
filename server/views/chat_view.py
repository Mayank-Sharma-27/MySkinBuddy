from flask import Blueprint, jsonify, request, Response, stream_with_context
from service.product_chat import initialize_chat, handle_chat_message
import json

chat_view = Blueprint('chat_view', __name__)

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
        
        if not all([cookie_id, product_id, user_message]):
            return jsonify({'error': 'Missing required parameters'}), 400

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