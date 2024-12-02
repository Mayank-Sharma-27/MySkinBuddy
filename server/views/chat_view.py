from flask import Blueprint, jsonify, request, Response, stream_with_context
from service.product_chat import initialize_chat, handle_chat_message

chat_view = Blueprint('chat_view', __name__)

@chat_view.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.get_json()
    product = data.get('product')
    brand = data.get('brand')
    
    if not product or not brand:
        return jsonify({"error": "Product and brand are required"}), 400
        
    try:
        chat_id = initialize_chat(product, brand)
        return jsonify({
            "chat_id": chat_id,
            "message": f"👋 Hello! I'm SkinBuddy! Ask me anything about {brand}'s {product}!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_view.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    message = data.get('message')
    
    if not chat_id or not message:
        return jsonify({"error": "Chat ID and message are required"}), 400
        
    try:
        def generate():
            for token in handle_chat_message(chat_id, message):
                yield f"data: {token}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(chat_view, **options) 