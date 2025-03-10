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

# Initialize Flask App
app = Flask(__name__, template_folder='templates')

# Logging Configuration
logging.basicConfig(level=logging.INFO)

# NASA FIRMS API URL (VIIRS S-NPP Near Real-Time Data for all of Canada)
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/e710ccc1baf9bf0673a8f3f40192e73f/VIIRS_SNPP_NRT/-141,41,-52,83/2"

# In-memory storage for fire data
fire_data = []
ALERT_RADIUS_KM = 15  # 15 km alert radius

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yorkefds@gmail.com'
app.config['MAIL_PASSWORD'] = 'yyfx aqof hzou cssp' 
app.config['MAIL_DEFAULT_SENDER'] = 'yorkefds@gmail.com'

mail = Mail(app)

# Haversine function to calculate the distance between two lat/lon points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  

# Function to fetch user locations from database
def fetch_user_locations():
    conn = sqlite3.connect("/home/capstoneheroes/EFDS-AI/EFDS-master/Frontend/subscribe.db")
    cursor = conn.cursor()

    cursor.execute("SELECT email, latitude, longitude FROM subscribers")
    user_locations = [(row[0], float(row[1]), float(row[2])) for row in cursor.fetchall()]

    conn.close()
    logging.info(f"🔍 User Locations Fetched: {user_locations}")
    return user_locations  

# Function to check which users should receive fire alerts
def check_fire_alert(fire_lat, fire_lon, user_locations):
    alert_users = []
    for email, user_lat, user_lon in user_locations:
        distance = haversine(user_lat, user_lon, fire_lat, fire_lon)
        if distance <= ALERT_RADIUS_KM:
            alert_users.append((email, fire_lat, fire_lon))
    return alert_users  

# Function to fetch and process NASA FIRMS fire data
def fetch_fire_data():
    global fire_data
    logging.info("Fetching latest VIIRS fire data from NASA FIRMS for all of Canada...")

    try:
        response = requests.get(FIRMS_URL)
        response.raise_for_status()  

        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))

        logging.info(f"Total Fire Records: {len(df)}")

        if df.empty:
            logging.warning("No fire data found! Check the API or parameters.")
            return  

        required_columns = {"latitude", "longitude", "bright_ti4", "confidence"}
        if not required_columns.issubset(df.columns):
            logging.error(f"Error: Missing required columns {required_columns - set(df.columns)}")
            return

        confidence_mapping = {"l": 30, "n": 60, "h": 90}
        df["confidence"] = df["confidence"].map(confidence_mapping).fillna(50)

        user_locations = fetch_user_locations()
        all_alert_users = []

        for _, row in df.iterrows():
            fire_lat, fire_lon = float(row["latitude"]), float(row["longitude"])
            alert_users = check_fire_alert(fire_lat, fire_lon, user_locations)

            for email, lat, lon in alert_users:
                all_alert_users.append((email, lat, lon, row["acq_date"], row["acq_time"]))

        fire_data = df.to_dict(orient="records")
        logging.info(f"ALERTS: {len(all_alert_users)} fires detected near user locations!")

        for email, fire_lat, fire_lon, acq_date, acq_time in all_alert_users:
            send_fire_alert_email(email, fire_lat, fire_lon, acq_date, acq_time)

        generate_fire_map(df)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching NASA FIRMS data: {e}")

def send_fire_alert_email(email, fire_lat, fire_lon, acq_date, acq_time):
    """Send an email alert when a fire is detected near a subscriber."""
    with app.app_context():  # Ensures Flask-Mail works correctly
        try:
            msg = Message(
                "🔥 Fire Alert: Wildfire Detected Near Your Location",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )

            msg.body = (f"Hello,\n\n"
                        f"A wildfire has been detected near your subscribed location.\n\n"
                        f"🔥 Fire Details:\n"
                        f"- **Location**: Latitude {fire_lat}, Longitude {fire_lon}\n"
                        f"- **Detected On**: {acq_date} at {acq_time}\n\n"
                        f"Please take necessary precautions and stay updated with local authorities.\n\n"
                        f"Stay safe,\n"
                        f"The EFDS Team")

            mail.send(msg)
            logging.info(f"✅ Fire alert email sent to {email}")

        except Exception as e:
            logging.error(f"❌ Failed to send fire alert email to {email}: {str(e)}")

# Function to generate an interactive fire map
def generate_fire_map(df):
    logging.info("Generating interactive fire map...")
    fire_map = folium.Map(location=[60, -95], zoom_start=4)

    for _, row in df.iterrows():
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color="red" if row.get("alert", 0) == 1 else "orange",
                fill=True,
                fill_color="red" if row.get("alert", 0) == 1 else "orange",
                fill_opacity=0.6,
                popup=f"Brightness: {row['bright_ti4']}\nConfidence: {row['confidence']}\nAcquired: {row.get('acq_date', 'N/A')} {row.get('acq_time', 'N/A')}",
                tooltip=f"🔥 Fire at ({lat}, {lon})"
            ).add_to(fire_map)
        except ValueError:
            logging.warning(f"Skipping invalid fire data: {row}")

    fire_map.save("templates/fire_map.html")
    logging.info("Fire map updated successfully.")

@app.route("/api/fire-data", methods=["GET"])
def get_fire_data():
    return jsonify(fire_data)

@app.route("/", methods=["GET"])
def fire_map():
    return render_template("fire_map.html")

def start_scheduler():
    schedule.every(10).minutes.do(fetch_fire_data)
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=start_scheduler, daemon=True).start()

if __name__ == "__main__":
    fetch_fire_data()
    app.run(host="0.0.0.0", port=6000, debug=True)