from flask import Blueprint, request, jsonify
import datetime

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    if not data or 'location' not in data:
        return jsonify({"error": "Location data missing"}), 400
    return jsonify({
        "status": "Alert sent",
        "location": data['location'],
        "alert_type": data.get('alert_type', 'SMS'),
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
