from flask import Blueprint, request, jsonify
from app.config import set_bbox, CITY_BBOX

set_region_bp = Blueprint('set_region', __name__)

@set_region_bp.route('/set_region', methods=['POST'])
def set_region():
    """
    Route to set the region for the application.
    Accepts a city name and updates the BBOX for that city.
    """
    data = request.get_json()

    # Get the city name from the request
    city = data.get('city', '').lower()
    
    if not city or city not in CITY_BBOX:
        return jsonify({
            "error": "Invalid or missing city. Available cities are: " + ", ".join(CITY_BBOX.keys())
        }), 400

    # Update the BBOX for the city
    set_bbox(city)
    return jsonify({
        "message": f"Region set to {city.title()}",
        "bbox": CITY_BBOX[city]
    })
