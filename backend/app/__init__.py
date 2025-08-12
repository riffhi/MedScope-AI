from flask import Flask
from flask_cors import CORS
from .core.config import settings
import os

def create_app():
    app = Flask(__name__)
    
    # Basic CORS configuration
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Ensure upload and log directories exist
    upload_dir = getattr(settings, 'UPLOAD_DIR', './uploads')
    log_file = getattr(settings, 'LOG_FILE', './logs/medbot.log')
    
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Import and register blueprints
    from .api.routes.auth_simple import auth_bp
    from .api.routes.reports_simple import reports_bp
    from .api.routes.analysis_simple import analysis_bp
    from .api.routes.chat_simple import chat_bp
    from .api.routes.scan_report import scan_bp
    from .api.routes.visualization_3d import visualization_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')
    app.register_blueprint(chat_bp, url_prefix='/api/v1/chat')
    app.register_blueprint(scan_bp, url_prefix='/api/v1/scan')
    app.register_blueprint(visualization_bp, url_prefix='/api/v1/visualization')

    @app.route("/")
    def root():
        return {
            "message": "MedScope AI API",
            "version": "1.0.0",
            "status": "running"
        }

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}

    return app