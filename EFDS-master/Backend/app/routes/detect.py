from flask import Blueprint, request, jsonify
import datetime

detect_bp = Blueprint('detect', __name__)

@detect_bp.route('/detect', methods=['POST'])
def detect_fire():
    data = request.get_json()
    if 'image_data' in data:
        return jsonify({
            "status": "Fire detected",
            "location": {"latitude": 50.123, "longitude": -114.456},
            "confidence": 0.9,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    else:
        return jsonify({"error": "Image data not provided"}), 400
