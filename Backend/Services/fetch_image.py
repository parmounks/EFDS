import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import datetime
from app.config import BASE_URL, LAYER, FORMAT, CRS, BBOX, WIDTH, HEIGHT

cached_image = None

def fetch_latest_image():
    """
    Fetch the latest image from NASA GIBS WMS, process it, and cache it for future use.
    """
    global cached_image
    date_str = datetime.datetime.utcnow().strftime('%Y-%m-%d')

    # Define the request parameters
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
        print(f"Fetching live image for date {date_str} with BBOX: {BBOX}")
        response = requests.get(BASE_URL, params=params, timeout=60)
        response.raise_for_status()  # Raise an HTTPError for bad HTTP responses

        # Check if the response contains an image
        if 'image' not in response.headers.get('Content-Type', ''):
            print("Error: The response does not contain a valid image. Inspecting content...")
            print(f"Response content (first 500 chars): {response.text[:500]}")
            return

        # Load the image
        try:
            image = Image.open(BytesIO(response.content))
        except UnidentifiedImageError:
            print("Error: The response content could not be identified as an image.")
            return

        # Convert to RGB if necessary
        if image.mode == 'RGBA':
            print("Image mode is RGBA, converting to RGB.")
            image = image.convert('RGB')

        # Save the image to a memory buffer
        cached_image = BytesIO()
        image.save(cached_image, 'JPEG')
        cached_image.seek(0)
        print("Image successfully fetched, processed, and cached.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.Timeout:
        print("Error: The request to fetch the image timed out.")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"Unexpected error during image fetch: {err}")
