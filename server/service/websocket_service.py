from flask_socketio import SocketIO, emit, join_room, leave_room
from service.chat_service import ChatService
from service.product_chat import ProductChat
import json
from datetime import datetime

# Initialize SocketIO with proper CORS settings
socketio = SocketIO(
    cors_allowed_origins=["http://localhost:3000", "https://myskinbuddy.com"],
    async_mode=None,  # Let it choose the best mode automatically
    cors_credentials=True,
    logger=True,  # Enable logging
    engineio_logger=True  # Enable engine.io logging
)

chat_service = ChatService()
product_chat = ProductChat()

@socketio.on('connect')
def handle_connect():
    print("🔌 Client connected")
    socketio.emit('connection_established', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 Client disconnected")

@socketio.on('join_chat')
def handle_join_chat(data):
    """Handle client joining a specific chat room"""
    try:
        print(f"📥 Join chat request received: {data}")
        cookie_id = data.get('cookie_id')
        product_id = data.get('product_id')
        if not cookie_id or not product_id:
            print("❌ Missing required parameters for join_chat")
            socketio.emit('error', {
                'type': 'error',
                'message': 'Missing required parameters'
            })
            return

        room = f"{cookie_id}_{product_id}"
        join_room(room)
        print(f"✅ Client joined room: {room}")
        
        try:
            # Initialize chat and get history
            chat_data = product_chat.initialize_chat(cookie_id, product_id)
            print(f"📜 Raw chat data: {chat_data}")
            
            # Format chat history messages
            if chat_data and chat_data.get('chat_history'):
                formatted_history = []
                for msg in chat_data['chat_history']:
                    formatted_msg = {
                        'type': 'message',
                        'id': str(datetime.utcnow().timestamp()),
                        'content': msg.get('content', ''),
                        'isUser': msg.get('role') == 'user',
                        'timestamp': msg.get('timestamp', datetime.utcnow().isoformat()),
                        'isLoading': False
                    }
                    formatted_history.append(formatted_msg)
                chat_data['chat_history'] = formatted_history
            
            print(f"📜 Formatted chat data: {chat_data}")
            
            # Emit initial chat data to the specific room
            socketio.emit('chat_history', chat_data, room=room)
            
            # Send a welcome message if there's no history
            if not chat_data.get('chat_history'):
                welcome_message = {
                    'type': 'message',
                    'id': str(datetime.utcnow().timestamp()),
                    'content': f"Hello! I'm your skincare assistant. How can I help you today?",
                    'isUser': False,
                    'timestamp': datetime.utcnow().isoformat(),
                    'isLoading': False
                }
                socketio.emit('message', welcome_message, room=room)
            
        except Exception as e:
            print(f"❌ Error getting chat history: {str(e)}")
            socketio.emit('error', {
                'type': 'error',
                'message': f'Failed to load chat history: {str(e)}'
            }, room=room)
        
    except Exception as e:
        print(f"❌ Error joining chat: {str(e)}")
        socketio.emit('error', {
            'type': 'error',
            'message': str(e)
        })

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Handle client leaving a chat room"""
    try:
        print(f"📤 Leave chat request received: {data}")
        cookie_id = data.get('cookie_id')
        product_id = data.get('product_id')
        if cookie_id and product_id:
            room = f"{cookie_id}_{product_id}"
            leave_room(room)
            print(f"✅ Client left room: {room}")
    except Exception as e:
        print(f"❌ Error leaving chat: {str(e)}")

@socketio.on('chat_message')
def handle_message(data):
    """Handle incoming chat messages"""
    try:
        print(f"💬 Chat message received: {data}")
        cookie_id = data.get('cookie_id')
        product_id = data.get('product_id')
        message = data.get('message')
        
        if not all([cookie_id, product_id, message]):
            print("❌ Missing required parameters for chat_message")
            socketio.emit('error', {
                'type': 'error',
                'message': 'Missing required parameters'
            })
            return

        room = f"{cookie_id}_{product_id}"
        print(f"🔄 Processing message in room: {room}")
        
        try:
            # Echo back the user's message first
            user_message = {
                'type': 'message',
                'id': str(datetime.utcnow().timestamp()),
                'content': message,
                'isUser': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            socketio.emit('message', user_message, room=room)
            print(f"📤 Emitted user message: {user_message}")
            
            # Process message through product chat
            accumulated_response = ""
            message_id = str(datetime.utcnow().timestamp())
            
            for response in product_chat.handle_message(
                cookie_id=cookie_id,
                product_id=product_id,
                message=message
            ):
                print(f"📤 Processing response chunk: {response}")
                if response.get('type') == 'assistant_chunk':
                    accumulated_response += response['content']
                    # Update the assistant message
                    message_data = {
                        'type': 'message',
                        'id': message_id,
                        'content': accumulated_response,
                        'isUser': False,
                        'timestamp': datetime.utcnow().isoformat(),
                        'isLoading': True
                    }
                    socketio.emit('message', message_data, room=room)
                    print(f"📤 Emitted assistant chunk: {message_data}")
                elif response.get('type') == 'done':
                    # Send the final message
                    message_data = {
                        'type': 'message',
                        'id': message_id,
                        'content': accumulated_response,
                        'isUser': False,
                        'timestamp': datetime.utcnow().isoformat(),
                        'isLoading': False
                    }
                    socketio.emit('message', message_data, room=room)
                    print(f"📤 Emitted final assistant message: {message_data}")
            
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
            socketio.emit('error', {
                'type': 'error',
                'message': f'Failed to process message: {str(e)}'
            }, room=room)
            
    except Exception as e:
        print(f"❌ Error handling message: {str(e)}")
        socketio.emit('error', {
            'type': 'error',
            'message': str(e)
        })