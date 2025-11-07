from flask import Flask
from app.config import Config

def create_app():
    """Factory function to create Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import main_bp
    from app.auth_routes import auth_bp
    from app.management_routes import management_bp
    from app.batch_routes import batch_bp
    from app.dashboard_routes import dashboard_bp
    from app.report_routes import report_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(management_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(report_bp)
    
    return app
