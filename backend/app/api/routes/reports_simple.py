from flask import Blueprint, request, jsonify

reports_bp = Blueprint('reports', __name__)

@reports_bp.route("/health", methods=["GET"])
def health():
    """Reports service health check"""
    return jsonify({"status": "Reports service is running"})

@reports_bp.route("/test", methods=["GET"])
def test():
    """Test reports endpoint"""
    return jsonify({"message": "Reports endpoint working"})
