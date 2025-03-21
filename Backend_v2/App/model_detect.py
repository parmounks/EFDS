from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import requests
from io import BytesIO
import os

# Disable GPU if CUDA is unavailable
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

app = Flask(__name__)

# Load the trained model once
MODEL_PATH = "/home/capstoneheroes/EFDS-AI/Backend_v2/Model/fire_detection_model.h5"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

model = load_model(MODEL_PATH)

# NASA GIBS API base URL
GIBS_BASE_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

# Mapping of provinces to their bounding boxes
PROVINCE_BBOX = {
    "ONTARIO": "-95,41,-74,57",
    "BRITISH COLUMBIA": "-139,48,-114,60",
    "ALBERTA": "-120,48,-110,60"
}

# Function to fetch and preprocess the satellite image
def fetch_nasa_image(province, date):
    if province not in PROVINCE_BBOX:
        return None, f"Province '{province}' not supported."

    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "LAYERS": "VIIRS_SNPP_CorrectedReflectance_TrueColor,MODIS_Combined_Thermal_Anomalies_All",
        "STYLES": "",
        "CRS": "EPSG:4326",
        "BBOX": PROVINCE_BBOX[province],
        "WIDTH": "512",
        "HEIGHT": "512",
        "FORMAT": "image/png",
        "TRANSPARENT": "TRUE",
        "TIME": date
    }

    # Debugging NASA API request
    print(f"Fetching NASA GIBS image from: {GIBS_BASE_URL}")
    print(f"Request Parameters: {params}")

    response = requests.get(GIBS_BASE_URL, params=params)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize((32, 32))  # Resize for model
        img_array = np.array(img) / 255.0  # Normalize
        img_array = img_array.reshape((1, 32, 32, 3))  # Reshape for CNN input
        return img_array, None
    else:
        print(f"NASA GIBS API request failed: {response.text}")
        return None, f"Failed to fetch image from NASA GIBS: {response.text}"

# Health Check Route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "EFDS Get Image is running!"})

# API Endpoint for Fire Prediction
@app.route("/", methods=["POST"])
def predict():
    data = request.json
    province = data.get("province")
    date = data.get("date")

    if not province or not date:
        return jsonify({"error": "Province and date are required."}), 400
    province = province.strip().upper()
    img_array, error = fetch_nasa_image(province, date)
    if error:
        return jsonify({"error": error}), 500

    # Make prediction
    prediction = model.predict(img_array)

    return jsonify({"province": province, "date": date, "prediction": prediction.tolist()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
