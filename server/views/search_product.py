from flask import Blueprint, jsonify, request
from service.product_service import find_product_by_name_and_brand_with_retriever

search_product_route = Blueprint('search_product', __name__)

@search_product_route.route('/search-products', methods=['GET'])
def search_products():
    product = request.args.get('product')
    brand = request.args.get('brand')
    
    if not product or not brand:
        return jsonify({"error": "Both product and brand parameters are required"}), 400
        
    products = find_product_by_name_and_brand_with_retriever(product, brand)
    # Update the response to include image_url
    return jsonify([{
        "product": p["product"], 
        "brand": p["brand"],
        "image_url": p.get("image_url", "")  # Include image_url in the response
    } for p in products])

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(search_product_route, **options) 