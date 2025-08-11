from flask import Flask
from flask_cors import CORS
from .core.config import settings
from .core.database import db
from .api.routes.auth_simple import auth_bp
from .api.routes.reports_simple import reports_bp
from .api.routes.analysis_simple import analysis_bp
from .api.routes.chat_simple import chat_bp
from .models import Base
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    # Ensure upload and log directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": settings.ALLOWED_ORIGINS}})
    db.init_app(app)

    with app.app_context():
        Base.metadata.create_all(bind=db.engine)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')
    app.register_blueprint(chat_bp, url_prefix='/api/v1/chat')

    @app.route("/")
    def root():
        return {
            "message": "MedBOT API",
            "version": "1.0.0",
            "status": "running"
        }

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}

    return app