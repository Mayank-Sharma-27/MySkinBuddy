from flask import Blueprint, jsonify, request
from service.images_service import ImagesService

images_view = Blueprint('images_view', __name__)
images_service = ImagesService()
@images_view.route('/upload-image', methods=['POST'])
def get_upload_url():
    data = request.get_json()
    image_information = data.get('image_information')
    if not data:
        return jsonify({"error": "No data provided"}), 400
        

    
    if not image_information:
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        
        return jsonify(images_service.get_image_urls(image_information))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@images_view.route('/get-data-from-image', methods=['POST'])
def search_products_with_image():
    data = request.get_json()
    image_information = data.get('image_information')
    
    if not image_information:
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        result = images_service.find_product_with_image(image_information)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def register(app, options=None):
    if options is None:
        options = {}
    app.register_blueprint(images_view, **options, url_prefix='/api') 
    
    