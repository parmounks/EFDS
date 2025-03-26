from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import requests
from io import BytesIO
import os
from flask_cors import CORS
import logging

# --- Logging Configuration ---
logging.basicConfig(filename='model_detect.log', level=logging.DEBUG)

# --- Disable GPU if running on non-GPU environment (e.g. Cloud Run) ---
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)

# --- Load Model ---
MODEL_PATH = "fire_detection_model.h5"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
model = load_model(MODEL_PATH)
logging.info("Model loaded successfully.")

# --- NASA GIBS API Settings ---
GIBS_BASE_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
PROVINCE_BBOX = {
    "ONTARIO": "-95,41,-74,57",
    "BRITISH COLUMBIA": "-139,48,-114,60",
    "ALBERTA": "-120,48,-110,60"
}

# --- Image Fetch and Preprocessing ---
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

    logging.debug(f"Fetching image for {province} on {date}")
    response = requests.get(GIBS_BASE_URL, params=params)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize((32, 32))
        img_array = np.array(img) / 255.0
        img_array = img_array.reshape((1, 32, 32, 3))
        return img_array, None
    else:
        logging.error(f"NASA API failed: {response.text}")
        return None, f"Failed to fetch image from NASA GIBS: {response.text}"

# --- Health Check ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "EFDS model server is running!"})

# --- Fire Prediction Endpoint ---
@app.route("/", methods=["POST"])
def predict():
    data = request.json
    province = data.get("province")
    date = data.get("date")

    if not province or not date:
        logging.warning("Province or date missing in request")
        return jsonify({"error": "Province and date are required."}), 400

    province = province.strip().upper()
    img_array, error = fetch_nasa_image(province, date)
    if error:
        return jsonify({"error": error}), 500

    prediction = model.predict(img_array)
    logging.info(f"Prediction for {province} on {date}: {prediction.tolist()}")

    return jsonify({
        "province": province,
        "date": date,
        "prediction": prediction.tolist()
    })

# --- Entry Point ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)
