import secrets
SECRET_KEY = secrets.token_hex(24);


# NASA GIBS WMS endpoint for high-resolution imagery
BASE_URL = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'
LAYER = 'VIIRS_SNPP_CorrectedReflectance_TrueColor'
FORMAT = 'image/jpeg'
CRS = 'EPSG:4326'  # coordinates type: longitude and latitude
WIDTH = 7600  # in pixels
HEIGHT = 7600  # in pixels

# Default bounding box (Canada-wide)
BBOX = '41.675,-141.002,83.233,-52.619'  # Covers all of Canada

# Dictionary of province and territory bounding boxes
# Coordinates format: "province/territory": "south_latitude,west_longitude,north_latitude,east_longitude"
PROVINCE_BBOX = {
    "alberta": "48.997,-120.000,60.000,-110.000",
    "british columbia": "48.306,-139.060,60.000,-114.034",
    "manitoba": "49.000,-102.000,60.000,-89.000",
    "new brunswick": "44.450,-69.050,48.070,-63.754",
    "newfoundland and labrador": "46.555,-67.805,60.373,-52.619",
    "northwest territories": "60.000,-136.500,83.233,-102.000",
    "nova scotia": "43.420,-66.410,47.030,-59.700",
    "nunavut": "51.000,-141.002,83.233,-61.000",
    "ontario": "41.675,-95.156,56.850,-74.340",
    "prince edward island": "45.950,-64.450,47.080,-61.980",
    "quebec": "45.000,-79.800,62.000,-57.100",
    "saskatchewan": "49.000,-110.000,60.000,-102.000",
    "yukon": "59.982,-141.002,69.652,-123.865"
}

# Function to update BBOX dynamically for a selected province/territory
def set_bbox(province):
    global BBOX
    province_lower = province.lower()
    if province_lower in PROVINCE_BBOX:
        BBOX = PROVINCE_BBOX[province_lower]
        print(f"BBOX updated to {BBOX} for province/territory: {province.title()}")
    else:
        print(f"Province/Territory {province} not found. Using default BBOX: {BBOX}")