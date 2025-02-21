from flask import Blueprint, jsonify, request
from service.product_service import find_product_with_retriever, get_product_suggestions
from service.message_limit_service import check_message_limit

search_product_route = Blueprint('search_product', __name__)

@search_product_route.route('/search-products', methods=['GET'])
def search_products():
    
    product = request.args.get('product')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    
    if not product:
        return jsonify({"error": "Product parameter is required"}), 400
        
    products = find_product_with_retriever(product, offset=offset, limit=limit)
    return jsonify(products)
    
@search_product_route.route('/product-suggestions', methods=['GET'])
def product_suggestions_route():
    
    query = request.args.get('q', '')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))
    
    suggestions = get_product_suggestions(query, offset=offset, limit=limit)
    return jsonify(suggestions)

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(search_product_route, **options, url_prefix='/api') 