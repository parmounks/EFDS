from flask import Blueprint, request, jsonify
from app.config import set_bbox, CITY_BBOX

set_region_bp = Blueprint('set_region', __name__)

@set_region_bp.route('/set_region', methods=['GET', 'POST'])
def set_region():
    """
    Route to set the region for the application.
    Accepts a city name from the query string (GET) or request body (POST).
    """
    city = request.args.get('city', '').lower() or request.get_json(silent=True).get('city', '').lower()
    
    if not city or city not in CITY_BBOX:
        return jsonify({
            "error": "Invalid or missing city. Available regions/cities are: " + ", ".join(CITY_BBOX.keys())
        }), 400

    set_bbox(city)
    return jsonify({
        "message": f"Region set to {city.title()}",
        "bbox": CITY_BBOX[city]
    })