from flask import Flask
from flask_cors import CORS
from views import product_view, search_product, chat_view, auth_view, recent_chat_view

app = Flask(__name__)
CORS(app, resources={  
    r"/recent-chats": {"origins": ["http://localhost:3000"]},
    r"/search-products": {"origins": ["http://localhost:3000"]},
    r"/start-chat": {"origins": ["http://localhost:3000"]},
    r"/product-suggestions": {"origins": ["http://localhost:3000"]},
    r"/chat": {"origins": ["http://localhost:3000"]},
    r"/auth/*": {"origins": ["http://localhost:3000"]},
    r"/chat/*": {"origins": ["http://localhost:3000"]}
})

# Register routes
product_view.register(app, {})
search_product.register(app)
chat_view.register(app)
auth_view.register(app)
recent_chat_view.register(app)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
