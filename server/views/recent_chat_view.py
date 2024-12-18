from flask import Blueprint, jsonify, request
from service.recent_chats_service import get_recent_chats

recent_chat_view = Blueprint('recent_chats', __name__)

@recent_chat_view.route('/recent-chats', methods=['GET'])
def get_recent_chats_view():
    try:
        cookie_id = request.headers.get('X-Cookie-ID')
        if not cookie_id:
            return jsonify({'error': 'Cookie ID is required'}), 400

        # Get limit from query params, default to 5
        limit = request.args.get('limit', default=5, type=int)
        
        # Get recent chats
        recent_chats = get_recent_chats(cookie_id, limit)
        
        seen = set()
        unique_chats = []
        for chat in recent_chats:
            product_key = (chat['product'], chat['brand'])
            if product_key not in seen:
                seen.add(product_key)
                unique_chats.append(chat)
        
        # Filter only required fields
        simplified_chats = [{
            'chat_id': chat['chat_id'],
            'product': chat['product'],
            'brand': chat['brand'],
            'image_url': chat.get('image_url', '')
        } for chat in unique_chats]
        
        return jsonify({
            'status': 'success',
            'chats': simplified_chats
        })

    except Exception as e:
        print(f"Error in recent chats endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(recent_chat_view, **options)    