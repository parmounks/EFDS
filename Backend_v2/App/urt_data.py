import logging
from math import radians, cos, sin, sqrt, atan2
from flask import Flask, jsonify, render_template, request
from flask_mail import Mail, Message
import requests
import pandas as pd
import folium
import schedule
import threading
import time
import io
import os, psycopg2
from datetime import datetime, timedelta

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# Initialize Flask App
app = Flask(__name__, template_folder='templates')

# Logging Configuration (Suppress Terminal Logs)
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("fire_detection.log"),  # Save logs to a file
        logging.NullHandler()  # Suppress logs in the terminal
    ]
)

# NASA FIRMS API URL
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/e710ccc1baf9bf0673a8f3f40192e73f/VIIRS_SNPP_NRT/-145.4190,39.5975,-48.2010,85.1925/2"

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
    return psycopg2.connect(
        dbname="efds_main",
        user="postgres",
        password=os.environ.get("DB_PASSWORD"),
        host="34.121.207.94", 
        port="5432"
    )


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
        df["color"] = df["confidence"].apply( lambda x: "red" if x >= 80 else "orange" if x >= 50 else "yellow"  )
        fire_data = df.to_dict(orient="records")
        
        generate_fire_map(df)  # Generate the fire map
        check_and_send_alerts(df)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching fire data: {e}")



# Generate Fire Map with Dark Mode Option
def generate_fire_map(df, mode='light'):
    logging.info("Generating interactive fire map...")

    # Ensure templates directory exists
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)  # Create the missing directory
        logging.info("Created 'templates' directory.")

    # Set the tile layer based on mode
    fire_map = folium.Map(location=[60, -95], zoom_start=4, tiles=None)

    if mode == 'dark':
        # Use CartoDB Dark Matter tiles for dark mode
        folium.TileLayer(
            tiles="CartoDB dark_matter",
            attr="CartoDB",
            name="Dark Mode"
        ).add_to(fire_map)
    else:
        # Use default tiles for light mode
        folium.TileLayer(
            tiles="OpenStreetMap",  # You can use any other tile style here
            attr="OpenStreetMap",
            name="Light Mode"
        ).add_to(fire_map)

    # Add fire locations as CircleMarkers
    for _, row in df.iterrows():
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])
            marker_color = row.get("color", "gray")  # fallback to gray if not found
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.6,
                popup=f"Fire at ({lat}, {lon})\nConfidence: {row.get('confidence', 'N/A')}\nAcquired: {row.get('acq_date', 'N/A')} {row.get('acq_time', 'N/A')}"
            ).add_to(fire_map)
        except ValueError: 
            logging.warning(f"Skipping invalid fire data: {row}")

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

def generate_localized_map(lat, lon, fires=None, radius_km=15, filename=None):
    """
    Creates an interactive folium map centered at user location with optional fire markers.
    Saves the map as an HTML file in templates/generated_maps.
    """
    from math import cos, radians

    lat = float(lat)
    lon = float(lon)
    fires = fires or []

    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * abs(cos(radians(lat))) + 0.0001)

    min_lat = lat - delta_lat
    max_lat = lat + delta_lat
    min_lon = lon - delta_lon
    max_lon = lon + delta_lon

    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=8)

    # Bounding box
    folium.Rectangle(
        bounds=[[min_lat, min_lon], [max_lat, max_lon]],
        color="blue", fill=False, weight=2, tooltip=f"{radius_km} km Radius"
    ).add_to(m)

    # User marker
    folium.Marker(
        location=[lat, lon],
        popup="Your Location",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    # Fire markers
    for fire_lat, fire_lon in fires:
        folium.CircleMarker(
            location=[fire_lat, fire_lon],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.6,
            popup=f"Fire at ({fire_lat}, {fire_lon})"
        ).add_to(m)

    # Save map
    map_dir = "templates/generated_maps"
    os.makedirs(map_dir, exist_ok=True)
    filename = filename or f"map_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
    filepath = os.path.join(map_dir, filename)
    m.save(filepath)

    return filename


# Send email alert
def send_email_alert(email, fire_locations):
    fire_list = "\n".join([f"• Fire at ({lat}, {lon})" for lat, lon in fire_locations])
    subject = "🔥 Alert: Fire(s) Detected Near You"

    # Find user coordinates
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        logging.error(f"No location data found for {email}")
        return

    user_lat, user_lon = float(result[0]), float(result[1])

    # Generate personalized map
    safe_filename = email.replace('@', '_at_').replace('.', '_')
    map_filename = f"{safe_filename}_map.html"
    generate_localized_map(user_lat, user_lon, fire_locations, filename=map_filename)

    # Public link to user-specific map
    map_link = f"https://efds-backend-71702513350.us-central1.run.app/map/{map_filename}"

    body = (
        f"Dear user,\n\n"
        f"The following fires have been detected within {ALERT_RADIUS_KM} km of your location:\n\n"
        f"{fire_list}\n\n"
        f"🗺️ View your personalized fire map here:\n{map_link}\n\n"
        f"Stay safe,\nEFDS Team"
    )

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

@app.route("/map/<map_name>")
def serve_user_map(map_name):
    return render_template(f"generated_maps/{map_name}")

# Route to Display Fire Map with Dark Mode Toggle
@app.route("/fire-map", methods=["GET"])
def fire_map():
    mode = request.args.get('mode', 'light')  # Default to 'light' mode if no mode is specified
    # Fetch the latest fire data from the global 'fire_data' variable
    df = pd.DataFrame(fire_data)
    generate_fire_map(df, mode)
    return render_template("fire_map.html")


# Background scheduler
def start_scheduler():
    schedule.every(10).minutes.do(fetch_fire_data)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background thread for local testing
threading.Thread(target=start_scheduler, daemon=True).start()

@app.route("/trigger-fetch", methods=["GET"])
def trigger_fire_fetch():
    try:
        fetch_fire_data()
        return jsonify({"status": "Fire data fetched successfully."}), 200
    except Exception as e:
        logging.error(f"Failed to fetch fire data manually: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return "OK", 200

# Run Flask App
if __name__ == "__main__":
    fetch_fire_data()
    port = int(os.environ.get("PORT", 7080))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
