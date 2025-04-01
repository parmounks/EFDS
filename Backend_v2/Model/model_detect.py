from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import requests
from io import BytesIO
import os, folium
from datetime import datetime, timedelta 
from flask_cors import CORS
import logging

# --- Logging Configuration ---
logging.basicConfig(filename='model_detect.log', level=logging.DEBUG)

# --- Disable GPU if running on non-GPU environment (e.g. Cloud Run) ---
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# --- Flask App Setup ---
app = Flask(__name__, static_folder='static', template_folder='templates')
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
    "ONTARIO": "40.9210,-96.2010,57.6190,-73.2990",
    "BRITISH COLUMBIA": "48,-139,60,-114",
    "ALBERTA": "48,-120,60,-110"

}

# --- Image Fetch and Preprocessing ---
def fetch_nasa_image(province, date):
    if province not in PROVINCE_BBOX:
        return None, f"Province '{province}' not supported."

    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "LAYERS": "VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1",
        "STYLES": "default",
        "CRS": "EPSG:4326",
        "BBOX": PROVINCE_BBOX[province],
        "WIDTH": "512",
        "HEIGHT": "512",
        "FORMAT": "image/png",
        "TRANSPARENT" : "FALSE",
        "TIME": date
    }

    logging.debug(f"Fetching image for {province} on {date}")
    response = requests.get(GIBS_BASE_URL, params=params)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_dir = "static/nasa_images"
        os.makedirs(img_dir, exist_ok=True)
        filename = f"{province}_{date}.png".replace(" ", "_")
        img_path = os.path.join(img_dir, filename)
        img.save(img_path)

        img = img.resize((32, 32))
        img_array = np.array(img) / 255.0
        img_array = img_array.reshape((1, 32, 32, 3))

        return img_array, f"/static/nasa_images/{filename}"
    else:
        logging.error(f"NASA API failed: {response.text}")
        return None, f"Failed to fetch image from NASA GIBS: {response.text}"

# --- Fire Map Generation ---
def generate_fire_map_from_csv(df, province, date):
    bbox = list(map(float, PROVINCE_BBOX[province].split(",")))
    min_lat, min_lon, max_lat, max_lon = bbox
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    fire_map = folium.Map(location=[center_lat, center_lon], zoom_start=5)

    for _, row in df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        confidence = row["confidence"]

        color = "red" if confidence >= 80 else "orange" if confidence >= 50 else "yellow"

        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"Confidence: {confidence}"
        ).add_to(fire_map)

    map_dir = "static/maps"
    os.makedirs(map_dir, exist_ok=True)
    filename = f"{province}_{date}_firemap.html".replace(" ", "_")
    map_path = os.path.join(map_dir, filename)
    fire_map.save(map_path)

    return f"/static/maps/{filename}"

def get_firms_url(province, date, days_back):
    lat1, lon1, lat2, lon2 = map(float, PROVINCE_BBOX[province].split(","))
    min_lat, max_lat = sorted([lat1, lat2])
    min_lon, max_lon = sorted([lon1, lon2])
    bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    return f"{FIRMS_API_BASE}/{FIRMS_API_KEY}/VIIRS_SNPP_NRT/{bbox}/{days_back}", (min_lon, min_lat, max_lon, max_lat)


def fetch_firms_data(url, bbox):
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_csv(BytesIO(response.content))
    print("=== Raw FIRMS CSV Data ===")
    print(df.head())  # or df.to_string()
    if df.empty:
        logging.warning("No fire data found!")
        return pd.DataFrame()

    # Confidence score transformation
    df["confidence"] = df["confidence"].map({"l": 30, "n": 60, "h": 90}).fillna(50)

    # Filter based on BBOX
    min_lon, min_lat, max_lon, max_lat = bbox
    filtered = df[
        (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat) &
        (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)
    ]

    # Only high confidence fires
    high_conf = filtered[filtered["confidence"] >= 50]
    return high_conf


# --- Home Route ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "EFDS model server is running!"})

# --- Basic Prediction JSON API ---
@app.route("/", methods=["POST"])
def predict():
    data = request.json
    province = data.get("province")
    date = data.get("date")

    if not province or not date:
        return jsonify({"error": "Province and date are required."}), 400

    province = province.strip().upper()
    img_array, image_url_or_error = fetch_nasa_image(province, date)

    if img_array is None:
        return jsonify({"error": image_url_or_error}), 500

    prediction = model.predict(img_array)
    logging.info(f"Prediction for {province} on {date}: {prediction.tolist()}")

    return jsonify({
        "province": province,
        "date": date,
        "prediction": prediction.tolist()
    })

# --- Detection Result Page ---
FIRMS_API_KEY = "e710ccc1baf9bf0673a8f3f40192e73f" 
FIRMS_API_BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

@app.route("/detect", methods=["GET"])
def detect():
    province = request.args.get("province")
    date = request.args.get("date")

    if not province or not date:
        return jsonify({"error": "Province and date are required."}), 400

    province = province.strip().upper()
    img_array, image_url_or_error = fetch_nasa_image(province, date)

    if img_array is None:
        return jsonify({"error": image_url_or_error}), 500

    try:
        today = datetime.utcnow().date()
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        days_back = max((today - selected_date).days, 1)

        firms_url, bbox = get_firms_url(province, date, days_back)
        logging.debug(f"FIRMS URL: {firms_url}")

        fire_df = fetch_firms_data(firms_url, bbox)
        no_fires = fire_df.empty
        map_url = generate_fire_map_from_csv(fire_df, province, date)

    except Exception as e:
        logging.error(f"Failed to fetch or process FIRMS data: {e}", exc_info=True)
        return jsonify({"error": "Could not fetch FIRMS data."}), 500

    return render_template("response.html",
                           image_url=image_url_or_error,
                           map_url=map_url,
                           no_fires=no_fires)


@app.route('/health')
def health():
    return "OK", 200

# --- Run Flask App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
