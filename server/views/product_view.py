from flask import Blueprint, jsonify, request
from service import product_service

product_view = Blueprint('product_view', __name__)


@product_view.route("/api/get_product_details/", methods=['GET'])
def get_product():
    product_url = request.args.get('url')

    json = product_service.get_product_details(product_url)
    return jsonify({
        'product': json
    })


def register(app, options):
    # Register the blueprint with the Flask app
    app.register_blueprint(product_view, **options, url_prefix='/api')
