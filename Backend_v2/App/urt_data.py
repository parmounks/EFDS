import sqlite3  
import logging
from math import radians, cos, sin, sqrt, atan2
from flask import Flask, jsonify, render_template
from flask_mail import Mail, Message
import requests
import pandas as pd
import folium
import schedule
import threading
import time
import io
import os
from datetime import datetime, timedelta

# Initialize Flask App
app = Flask(__name__, template_folder='templates')

# Logging Configuration (Suppress Terminal Logs)
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("fire_detection.log"),  # Save logs to a file
        # logging.NullHandler()  # Suppress logs in the terminal
    ]
)

# NASA FIRMS API URL
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/e710ccc1baf9bf0673a8f3f40192e73f/VIIRS_SNPP_NRT/-141,41,-52,83/2"

fire_data = []
ALERT_RADIUS_KM = 15  # 15 km alert radius
last_alert_time = {}  # Dictionary to track last alert time per email

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yorkefds@gmail.com'
app.config['MAIL_PASSWORD'] = 'yyfx aqof hzou cssp' 
app.config['MAIL_DEFAULT_SENDER'] = 'yorkefds@gmail.com'

mail = Mail(app)

# Haversine function to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect("/home/capstoneheroes/EFDS-AI/EFDS-master/Frontend/subscribe.db")
    conn.row_factory = sqlite3.Row
    return conn

# Fetch user locations
def fetch_user_locations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, latitude, longitude FROM subscribers")
    user_locations = [(row[0], float(row[1]), float(row[2])) for row in cursor.fetchall()]
    conn.close()
    return user_locations  

# Fetch and process fire data
def fetch_fire_data():
    global fire_data
    logging.info("Fetching latest fire data...")
    try:
        response = requests.get(FIRMS_URL)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        if df.empty:
            logging.warning("No fire data found!")
            return  
        df["confidence"] = df["confidence"].map({"l": 30, "n": 60, "h": 90}).fillna(50)
        fire_data = df.to_dict(orient="records")
        
        generate_fire_map(df)  # Generate the fire map
        check_and_send_alerts(df)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching fire data: {e}")

# Generate Fire Map
def generate_fire_map(df):
    logging.info("Generating interactive fire map...")

    # Ensure templates directory exists
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)  # Create the missing directory
        logging.info("Created 'templates' directory.")

    fire_map = folium.Map(location=[60, -95], zoom_start=4)

    for _, row in df.iterrows():
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color="red",
                fill=True,
                fill_opacity=0.6,
                popup=f"🔥 Fire at ({lat}, {lon})\nAcquired: {row.get('acq_date', 'N/A')} {row.get('acq_time', 'N/A')}"
            ).add_to(fire_map)
        except ValueError:
            logging.warning(f"⚠️ Skipping invalid fire data: {row}")

    # Save the fire map
    map_path = os.path.join(templates_dir, "fire_map.html")
    fire_map.save(map_path)
    logging.info("Fire map updated successfully.")

# Check for fires near users and send alert
def check_and_send_alerts(df):
    global last_alert_time
    user_locations = fetch_user_locations()
    fire_locations = [(row["latitude"], row["longitude"]) for row in df.to_dict(orient="records")]
    now = datetime.now()

    for email, user_lat, user_lon in user_locations:
        if email in last_alert_time and now - last_alert_time[email] < timedelta(hours=24):
            continue  # Skip if email was sent within last 24 hours
        
        nearby_fires = [(lat, lon) for lat, lon in fire_locations if haversine(user_lat, user_lon, lat, lon) <= ALERT_RADIUS_KM]
        
        if nearby_fires:
            send_email_alert(email, nearby_fires)
            last_alert_time[email] = now

# Send email alert
def send_email_alert(email, fire_locations):
    fire_list = "\n".join([f"🔥 Fire detected at ({lat}, {lon})" for lat, lon in fire_locations])
    subject = "⚠️Alert: Fire(s) Near Your Location"
    body = f"Dear user,\n\nThe following fires have been detected within {ALERT_RADIUS_KM} km of your location:\n\n{fire_list}\n\nStay safe,\nEFDS Team"
    with app.app_context():
        try:
            msg = Message(subject, recipients=[email], body=body)
            mail.send(msg)
            logging.info(f"Alert sent to {email}")
        except Exception as e:
            logging.error(f"Failed to send alert to {email}: {e}")

# API Route to Get Fire Data
@app.route("/fire-data", methods=["GET"])
def get_fire_data():
    return jsonify(fire_data)

# Route to Display Fire Map
@app.route("/fire-map", methods=["GET"])
def fire_map():
    return render_template("fire_map.html")

# Background scheduler
def start_scheduler():
    schedule.every(2).minutes.do(fetch_fire_data)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background thread
threading.Thread(target=start_scheduler, daemon=True).start()

# Run Flask App
if __name__ == "__main__":
    fetch_fire_data()
    app.run(host="0.0.0.0", port=6000, debug=True, use_reloader=False)