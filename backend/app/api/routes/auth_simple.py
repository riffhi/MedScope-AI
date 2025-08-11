from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/health", methods=["GET"])
def health():
    """Auth service health check"""
    return jsonify({"status": "Auth service is running"})

@auth_bp.route("/test", methods=["GET"])
def test():
    """Test auth endpoint"""
    return jsonify({"message": "Auth endpoint working"})
