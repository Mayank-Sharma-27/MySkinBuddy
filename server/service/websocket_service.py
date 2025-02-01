from flask_socketio import SocketIO, emit, join_room, leave_room
from service.product_chat import handle_chat_message
from service.chat_service import get_recent_chat
import json
from datetime import datetime

# Initialize SocketIO with proper CORS settings
socketio = SocketIO(
    cors_allowed_origins=["http://localhost:3000", "https://myskinbuddy.com"],
    async_mode=None,  # Let it choose the best mode automatically
    cors_credentials=True
)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('join_chat')
def handle_join_chat(data):
    """Handle client joining a specific chat room"""
    try:
        print(f"Join chat request received: {data}")
        cookie_id = data.get('cookie_id')
        product_id = data.get('product_id')
        if not cookie_id or not product_id:
            print("Missing required parameters for join_chat")
            emit('error', {'message': 'Missing required parameters'})
            return

        room = f"{cookie_id}_{product_id}"
        join_room(room)
        print(f"Client joined room: {room}")
        
        # Get recent chat history
        chat_data = get_recent_chat(cookie_id, product_id)
        print(f"Sending chat history: {chat_data}")
        emit('chat_history', chat_data)
        
    except Exception as e:
        print(f"Error joining chat: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Handle client leaving a chat room"""
    print(f"Leave chat request received: {data}")
    cookie_id = data.get('cookie_id')
    product_id = data.get('product_id')
    if cookie_id and product_id:
        room = f"{cookie_id}_{product_id}"
        leave_room(room)
        print(f"Client left room: {room}")

@socketio.on('chat_message')
def handle_message(data):
    """Handle incoming chat messages"""
    try:
        print(f"Chat message received: {data}")
        cookie_id = data.get('cookie_id')
        product_id = data.get('product_id')
        message = data.get('message')
        
        if not all([cookie_id, product_id, message]):
            print("Missing required parameters for chat_message")
            emit('error', {'message': 'Missing required parameters'})
            return

        room = f"{cookie_id}_{product_id}"
        print(f"Processing message in room: {room}")
        
        # Process message and stream response
        try:
            for chunk in handle_chat_message(cookie_id, product_id, message):
                print(f"Received raw chunk: {chunk}")
                if chunk and chunk.startswith('data: '):
                    try:
                        chunk_data = json.loads(chunk[6:])  # Remove 'data: ' prefix
                        print(f"Parsed chunk data: {chunk_data}")
                        emit('message', chunk_data, room=room)
                        print(f"Emitted message: {chunk_data}")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing chunk JSON: {e}")
                        continue
                else:
                    print(f"Skipping invalid chunk format: {chunk}")
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            emit('error', {
                'type': 'error',
                'content': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }, room=room)
            
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        emit('error', {'message': str(e)})