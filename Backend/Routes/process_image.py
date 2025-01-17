from flask import Blueprint, request, jsonify

process_image_bp = Blueprint('process_image', __name__)

@process_image_bp.route('/process_image', methods=['POST'])
def process_image():
    data = request.get_json()
    if 'image_data' in data:
        return jsonify({"status": "Image processed", "processing_time": "2 seconds"})
    else:
        return jsonify({"error": "Image data not provided"}), 400
