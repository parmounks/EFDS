from flask import Blueprint, request, jsonify, session
from app.config import PROVINCE_BBOX

set_region_bp = Blueprint('set_region', __name__)

@set_region_bp.route('/set_region', methods=['GET', 'POST'])
def set_region():
    """
    Route to set the region for the application.
    Accepts a province name from the query string (GET) or request body (POST).
    """
    # Retrieve the province from query parameters or JSON request body
    province = request.args.get("province", "").lower() or \
               (request.get_json(silent=True) or {}).get("province", "").lower()

    if not province or province not in PROVINCE_BBOX:
        return jsonify({
            "error": "Invalid or missing province. Available regions are: " + ", ".join(PROVINCE_BBOX.keys())
        }), 400

    # Store the selected province in the session
    session['province'] = province

    return jsonify({
        "message": f"Region set to {province.title()}",
        "bbox": PROVINCE_BBOX[province]
    })
