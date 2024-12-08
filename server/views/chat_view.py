from flask import Blueprint, jsonify, request, Response, stream_with_context
from service.product_chat import initialize_chat, handle_chat_message
from service.product_chat import get_chat_history

chat_view = Blueprint('chat_view', __name__)

@chat_view.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.get_json()
    product = data.get('product')
    brand = data.get('brand')
    cookie_id = request.headers.get('X-Cookie-Id')
    
    if not product or not brand:
        return jsonify({"error": "Product and brand are required"}), 400
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    try:
        chat_id = initialize_chat(cookie_id, product, brand)
        initial_message = f"👋 Hello! I'm  {brand}'s {product}! you can ask me anything and I will 
        try to help you!"
        
        return jsonify({
            "chat_id": chat_id,
            "message": initial_message
        })
    except Exception as e:
        print(f"Error in start_chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@chat_view.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    message = data.get('message')
    cookie_id = request.headers.get('X-Cookie-ID')
    
    if not chat_id or not message:
        return jsonify({"error": "Chat ID and message are required"}), 400
    
    if not cookie_id:
        return jsonify({"error": "Cookie ID is required"}), 400
        
    try:
        # Save the user message first
        
        def generate():
            accumulated_response = ""
            for token in handle_chat_message(cookie_id, chat_id, message):
                accumulated_response += token
                yield f"data: {token}\n\n"
            
            # Save the complete assistant respon
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(chat_view, **options) 