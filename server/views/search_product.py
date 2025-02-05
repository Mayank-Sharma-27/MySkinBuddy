from flask import Blueprint, jsonify, request
from service.product_service import find_product_with_retriever, get_product_suggestions
from service.message_limit_service import check_message_limit

search_product_route = Blueprint('search_product', __name__)

@search_product_route.route('/search-products', methods=['GET'])
def search_products():
    cookie_id = request.headers.get('X-Cookie-ID')
    
    # Check message limit
    limit_status = check_message_limit(cookie_id)
    if limit_status:
        return jsonify(limit_status), 403
    
    product = request.args.get('product')
    
    if not product:
        return jsonify({"error": "Both product and brand parameters are required"}), 400
        
    products = find_product_with_retriever(product)
    # Update the response to include image_url
    return jsonify([{
        "product": p["product"], 
        "brand": p["brand"],
        "image_url": p.get("image_url", "")  # Include image_url in the response
    } for p in products])
    
@search_product_route.route('/product-suggestions', methods=['GET'])
def product_suggestions_route():
    cookie_id = request.headers.get('X-Cookie-ID')
    
    # Check message limit
    limit_status = check_message_limit(cookie_id)
    if limit_status:
        return jsonify(limit_status), 403
    
    query = request.args.get('q', '')
    max_suggestions = int(request.args.get('max', '5'))
    
    suggestions = get_product_suggestions(query, max_suggestions)
    # Format response to match search_products format
    formatted_suggestions = [{
        "product": suggestion["value"]["product"],
        "brand": suggestion["value"]["brand"],
        "image_url": suggestion["image_url"],
        "product_id": suggestion["product_id"]
    } for suggestion in suggestions]
    
    return jsonify(formatted_suggestions)

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(search_product_route, **options, url_prefix='/api') 