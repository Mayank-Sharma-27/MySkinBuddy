from flask import Blueprint, jsonify, request
from service.recent_chats_service import get_recent_chats, get_all_chats

recent_chat_view = Blueprint('recent_chats', __name__)

@recent_chat_view.route('/recent-chats', methods=['GET'])
def get_recent_chats_view():
    try:
        cookie_id = request.headers.get('X-Cookie-ID')
        if not cookie_id:
            return jsonify({'error': 'Cookie ID is required'}), 400
        limit = request.args.get('limit', default=5, type=int)
        recent_chats = get_recent_chats(cookie_id, limit)
        return jsonify({
            'status': 'success',
            'chats': recent_chats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@recent_chat_view.route('/all-chats', methods=['GET'])
def get_all_chats_view():
    try:
        cookie_id = request.headers.get('X-Cookie-ID')
        if not cookie_id:
            return jsonify({'error': 'Cookie ID is required'}), 400
        all_chats = get_all_chats(cookie_id)
        return jsonify({'status': 'success', 'chats': all_chats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(recent_chat_view, **options, url_prefix='/api')    