from flask import Blueprint, jsonify, request, Response, stream_with_context
from service.product_chat import initialize_chat, handle_chat_message
from service.product_chat import get_chat_history
import json

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
        
        def generate():
            try:
                current_response = ""
                header_sent = False
                
                for chunk in handle_chat_message(cookie_id, chat_id, message):
                    print(f"\n=== Debug - Chunk Type: {type(chunk)} ===")
                    print(f"Debug - Raw chunk content: {chunk}")
                    
                    if isinstance(chunk, dict):
                        print(f"Debug - Dict keys: {chunk.keys()}")
                        if chunk.get('type') == 'final':
                            print(f"Debug - Final chunk detected with sources: {chunk.get('sources', [])}")
                            formatted_response = {
                                'content': current_response,
                                'sources': chunk.get('sources', []),
                                'type': 'final'
                            }
                            print(f"Debug - Sending final formatted response: {formatted_response}")
                    else:
                        # For regular content chunks
                        content = str(chunk)
                        print(f"Debug - Processing content chunk: {content[:50]}...")
                        
                        # Clean up content and handle headers
                        if not header_sent and "###" in content:
                            content = content.split("###")[-1].strip()
                            header_sent = True
                        elif header_sent and "###" in content:
                            content = content.split("###")[-1].strip()
                        elif "Main Response:" in content:
                            # Skip duplicate "Main Response:" text
                            content = content.replace("Main Response:", "").strip()
                        
                        # Only add new content
                        if content.strip():
                            formatted_response = {
                                'content': content
                            }
                            yield f"data: {json.dumps(formatted_response)}\n\n"
                    
                    if isinstance(chunk, dict) and chunk.get('type') == 'final':
                        yield f"data: {json.dumps(formatted_response)}\n\n"
                
            except Exception as e:
                print(f"Error in generate: {str(e)}")
                yield f"data: {json.dumps({'content': f'Error: {str(e)}' })}\n\n"
        
        response = Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Content-Type': 'text/event-stream',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Access-Control-Allow-Origin': '*'
            }
        )
        return response
        
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

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(chat_view, **options) 