from flask import Blueprint, jsonify, request
from service.product_service import find_product_with_retriever, get_product_suggestions, find_product_with_llm_query

search_product_route = Blueprint('search_product', __name__)

@search_product_route.route('/search-products', methods=['GET'])
def search_products():
    
    product = request.args.get('product')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    is_descriptive_search = request.args.get('is_descriptive_search', False)
    
    
    if not product:
        return jsonify({"error": "Product parameter is required"}), 400
    
    if is_descriptive_search:
        products = find_product_with_llm_query(product, offset=offset, limit=limit)
    else:
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