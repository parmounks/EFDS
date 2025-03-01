from flask import Blueprint, request, jsonify, send_file
from PIL import Image
from io import BytesIO
import requests
from app.config import BASE_URL, LAYER, FORMAT, CRS, PROVINCE_BBOX, WIDTH, HEIGHT

get_image_bp = Blueprint('get_image', __name__)

@get_image_bp.route('/get_image', methods=['GET'])
def get_image():
    """
    Endpoint to fetch a satellite image for a specific date and selected region.
    """
    # Retrieve the 'date' parameter from the query string
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Please provide a valid date in the format YYYY-MM-DD."}), 400

    # Retrieve the 'region' parameter from the query string
    region = request.args.get('region')
    if not region:
        return jsonify({"error": "Please provide a region."}), 400

    # Normalize the region name: replace underscores with spaces and convert to lowercase
    normalized_region = region.replace('_', ' ').lower()

    # Check if the normalized region exists in the PROVINCE_BBOX dictionary
    if normalized_region not in PROVINCE_BBOX:
        available_regions = ', '.join(PROVINCE_BBOX.keys())
        return jsonify({
            "error": f"Invalid region '{region}'. Available regions are: {available_regions}."
        }), 400

    # Define parameters for the WMS request
    params = {
        'service': 'WMS',
        'request': 'GetMap',
        'version': '1.3.0',
        'layers': LAYER,
        'styles': '',
        'format': FORMAT,
        'transparent': 'false',
        'height': HEIGHT,
        'width': WIDTH,
        'crs': CRS,
        'bbox': PROVINCE_BBOX[normalized_region],  # Use the bounding box for the selected region
        'time': date_str
    }

    try:
        # Make the request to the WMS server with a timeout
        response = requests.get(BASE_URL, params=params, timeout=10)  # Timeout after 10 seconds
        response.raise_for_status()

        # Measure the response time
        response_time = response.elapsed.total_seconds()
        print(f"Response time: {response_time} seconds")

        # Check if the response contains an image
        if 'image' not in response.headers.get('Content-Type', ''):
            return jsonify({"error": "The response is not a valid image."}), 400

        # Open the image from the response content
        image = Image.open(BytesIO(response.content))
        img_io = BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)

        # Send the image file in the response
        return send_file(img_io, mimetype='image/jpeg')

    except requests.exceptions.Timeout:
        return jsonify({"error": "The request timed out. Please try again later."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
