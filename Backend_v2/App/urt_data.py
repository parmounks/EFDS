from flask import Flask, jsonify, render_template
import requests
import pandas as pd
import folium
import schedule
import threading
import time
import io

# Initialize Flask App
app = Flask(__name__)

# NASA FIRMS API URL (VIIRS S-NPP Near Real-Time Data for Canada)
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/e710ccc1baf9bf0673a8f3f40192e73f/VIIRS_SNPP_NRT/-150,40,-49,79/1"

# In-memory storage for fire data
fire_data = []

# Function to fetch and process NASA FIRMS fire data
def fetch_fire_data():
    global fire_data
    print("Fetching latest VIIRS fire data from NASA FIRMS...")

    try:
        response = requests.get(FIRMS_URL)
        response.raise_for_status()  # Raise an error for bad responses (e.g., 404, 500)

        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))

        # Debugging: Print column names in the CSV
        print("CSV Columns:", df.columns.tolist())

        # Ensure required columns exist
        required_columns = {"latitude", "longitude", "bright_ti4", "confidence"}
        if not required_columns.issubset(df.columns):
            print(f"Error: Missing required columns {required_columns - set(df.columns)}")
            return

        # Convert confidence from categorical ('l', 'n', 'h') to numeric
        confidence_mapping = {"l": 30, "n": 60, "h": 90}  
        df["confidence"] = df["confidence"].map(confidence_mapping).fillna(50)  

        # Store fire data in memory
        fire_data = df.to_dict(orient="records")
        print(f"Fire data updated: {len(fire_data)} records.")

        # Generate the interactive fire map
        generate_fire_map(df)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA FIRMS data: {e}")

# Function to generate an interactive fire map
# Function to generate an interactive fire map
def generate_fire_map(df):
    print("Generating interactive fire map...")
    fire_map = folium.Map(location=[60, -95], zoom_start=4)  # Centered on Canada

    for row in df.itertuples():
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=3,
            color="red" if row.confidence > 80 else "orange",
            fill=True,
            fill_color="red" if row.confidence > 80 else "orange",
            fill_opacity=0.6,
            popup=f"""
                <b>Brightness:</b> {row.bright_ti4}<br>
                <b>Confidence:</b> {row.confidence}<br>
                <b>Fire Size:</b> {getattr(row, 'frp', 'N/A')} MW<br>
                <b>Acquired:</b> {getattr(row, 'acq_date', 'N/A')} {getattr(row, 'acq_time', 'N/A')}
            """,
            tooltip=f"🔥 Fire at ({row.latitude}, {row.longitude})\nBrightness: {row.bright_ti4}\nSize: {getattr(row, 'frp', 'N/A')} MW\nAcquired: {getattr(row, 'acq_date', 'N/A')} {getattr(row, 'acq_time', 'N/A')}"
        ).add_to(fire_map)

    fire_map.save("templates/fire_map.html")
    print("Fire map updated successfully.")

# API Route to Get Fire Data
@app.route("/api/fire-data", methods=["GET"])
def get_fire_data():
    return jsonify(fire_data)

# Route to Display Fire Map
@app.route("/", methods=["GET"])
def fire_map():
    return render_template("fire_map.html")

# Background scheduler to fetch data every 10 minutes
def start_scheduler():
    schedule.every(10).minutes.do(fetch_fire_data)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background thread for scheduler
threading.Thread(target=start_scheduler, daemon=True).start()

# Run Flask App
if __name__ == "__main__":
    fetch_fire_data()  # Run initially
    app.run(host="0.0.0.0", port = 6000, debug=True)
