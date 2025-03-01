from flask import Blueprint, request, jsonify

# Define a new Blueprint
endpoint_bp = Blueprint('endpoint', __name__)

@endpoint_bp.route('/endpoint', methods=['POST'])
def endpoint():
    """
    Example endpoint that accepts JSON data and returns a processed response.
    """
    data = request.get_json()

    if not data or 'key' not in data:
        return jsonify({"error": "Invalid input, 'key' is required"}), 400

    # Example: Process input and return a response
    response = {"message": f"Received {data['key']}"}
    return jsonify(response), 200
