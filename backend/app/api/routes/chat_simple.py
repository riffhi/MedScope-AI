from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/health", methods=["GET"])
def health():
    """Chat service health check"""
    return jsonify({"status": "Chat service is running"})

@chat_bp.route("/test", methods=["GET"])
def test():
    """Test chat endpoint"""
    return jsonify({"message": "Chat endpoint working"})
