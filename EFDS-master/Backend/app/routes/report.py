from flask import Blueprint, jsonify

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['GET'])
def report():
    return jsonify({
        "fire_events": [
            {
                "location": {"latitude": 49.2827, "longitude": -123.1207},
                "confidence": 0.87,
                "timestamp": "2024-10-31T12:00:00Z",
                "alert_status": "sent"
            },
            {
                "location": {"latitude": 51.0486, "longitude": -114.0708},
                "confidence": 0.92,
                "timestamp": "2024-10-31T14:30:00Z",
                "alert_status": "pending"
            }
        ]
    })
