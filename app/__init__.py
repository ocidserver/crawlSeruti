from flask import Flask
from app.config import Config

def create_app():
    """Factory function to create Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
