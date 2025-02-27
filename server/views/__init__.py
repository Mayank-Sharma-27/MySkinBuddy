from flask import Flask
from views import product_view, search_product, chat_view, auth_view, recent_chat_view, user_profile_view, images_view

def register_views(app: Flask):
    """Register all blueprints/views with the Flask application."""
    
    product_view.register(app, {})
    search_product.register(app)
    chat_view.register(app)
    auth_view.register(app)
    recent_chat_view.register(app)
    user_profile_view.register(app)
    images_view.register(app)


