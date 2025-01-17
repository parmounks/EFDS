from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "AI_model": "active",
        "Google_Cloud": "connected",
        "database": "connected"
    })
