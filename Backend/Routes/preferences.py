from flask import Blueprint, request, jsonify

preferences_bp = Blueprint('preferences', __name__)

@preferences_bp.route('/user/preferences', methods=['POST', 'PUT'])
def user_preferences():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "User ID is required"}), 400
    return jsonify({
        "status": "User preferences updated" if request.method == 'PUT' else "User registered",
        "user_id": data['user_id'],
        "preferences": data.get("preferences", {})
    })
