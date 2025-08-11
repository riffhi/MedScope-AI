from flask import Blueprint, request, jsonify

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route("/health", methods=["GET"])
def health():
    """Analysis service health check"""
    return jsonify({"status": "Analysis service is running"})

@analysis_bp.route("/test", methods=["GET"])
def test():
    """Test analysis endpoint"""
    return jsonify({"message": "Analysis endpoint working"})
