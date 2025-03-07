from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import requests
from io import BytesIO
import concurrent.futures

app = Flask(__name__)

# Load the trained model
MODEL_PATH = "/home/capstoneheroes/EFDS-AI/Backend_v2/Model/fire_detection_model.h5"  
model = load_model(MODEL_PATH)

# NASA GIBS API base URL
GIBS_BASE_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

# Mapping of provinces to their bounding boxes (latitude/longitude coordinates)
PROVINCE_BBOX = {
    "Ontario": "-95,41,-74,57",
    "British Columbia": "-139,48,-114,60",
    "Alberta": "-120,48,-110,60"
    # Add other provinces as needed
}

# Function to fetch and preprocess the satellite image
def fetch_nasa_image(province, date):
    if province not in PROVINCE_BBOX:
        return None, f"Province '{province}' not supported."
    
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "LAYERS": "VIIRS_SNPP_CorrectedReflectance_TrueColor,MODIS_Combined_Thermal_Anomalies_All",  # Change if needed
        "STYLES": "",
        "CRS": "EPSG:4326",
        "BBOX": PROVINCE_BBOX[province],
        "WIDTH": "512",
        "HEIGHT": "512",
        "FORMAT": "image/png",
        "TRANSPARENT": "TRUE",
        "TIME": date
    }
    
    response = requests.get(GIBS_BASE_URL, params=params)
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize((32, 32))  # Resize for model
        img_array = np.array(img) / 255.0  # Normalize
        img_array = img_array.reshape((1, 32, 32, 3))  # Reshape for CNN input
        return img_array, None
    else:
        return None, f"Failed to fetch image from NASA GIBS: {response.text}"

# API endpoint to process the request
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    province = data.get("province")
    date = data.get("date")
    
    if not province or not date:
        return jsonify({"error": "Province and date are required."}), 400
    
    img_array, error = fetch_nasa_image(province, date)
    if error:
        return jsonify({"error": error}), 500
    
    prediction = model.predict(img_array)
    return jsonify({"province": province, "date": date, "prediction": prediction.tolist()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
