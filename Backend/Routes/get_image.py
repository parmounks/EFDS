from flask import Blueprint, request, jsonify, send_file
from app.services.fetch_image import fetch_latest_image, cached_image
from PIL import Image
from io import BytesIO
import requests
import datetime
from app.config import BASE_URL, LAYER, FORMAT, CRS, BBOX, WIDTH, HEIGHT

get_image_bp = Blueprint('get_image', __name__)

@get_image_bp.route('/get_image', methods=['GET'])
def get_image():
    """
    Endpoint to fetch a live or specific-date satellite image.
    """
    image_type = request.args.get('type', 'live').lower()  # Default to 'live'

    if image_type == 'live':
        # Use today's date for the live request
        date_str = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        print(f"Processing live image request for date: {date_str}")

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
            'bbox': BBOX,
            'time': date_str
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=60)
            response.raise_for_status()

            # Check if the response contains a valid image
            if 'image' not in response.headers.get('Content-Type', ''):
                print("Error: The response does not contain a valid image.")
                return jsonify({"error": "The response is not a valid image"}), 400

            # Process the image
            image = Image.open(BytesIO(response.content))
            if image.mode == 'RGBA':
                print("Converting live image from RGBA to RGB.")
                image = image.convert('RGB')

            img_io = BytesIO()
            image.save(img_io, 'JPEG')
            img_io.seek(0)

            # Cache the image for future live requests
            global cached_image
            cached_image = img_io

            return send_file(img_io, mimetype='image/jpeg')

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"HTTP error occurred: {e}"}), 500
        except Exception as err:
            return jsonify({"error": f"An error occurred: {err}"}), 500

    elif image_type == 'specific':
        # Specific date request logic remains unchanged
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({"error": "Please provide a valid date for specific date option"}), 400

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
            'bbox': BBOX,
            'time': date_str
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=60)
            response.raise_for_status()

            if 'image' not in response.headers.get('Content-Type', ''):
                return jsonify({"error": "The response is not a valid image"}), 400

            image = Image.open(BytesIO(response.content))
            img_io = BytesIO()
            image.save(img_io, 'JPEG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"HTTP error occurred: {e}"}), 500
        except Exception as err:
            return jsonify({"error": f"An error occurred: {err}"}), 500

    else:
        return jsonify({"error": "Invalid image type. Choose 'live' or 'specific'."}), 400
