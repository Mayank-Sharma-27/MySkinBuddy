from flask import Flask
from flask_cors import CORS
from views import product_view, search_product, chat_view

app = Flask(__name__)
CORS(app)

# Register routes
product_view.register(app)
search_product.register(app)
chat_view.register(app)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
