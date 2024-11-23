from flask import Flask, jsonify
from flask_cors import CORS
from views import product_view
from views.product_view import register

# app instance
app = Flask(__name__)
CORS(app)


register(app, options={})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
