from flask import Flask, request, jsonify, render_template, url_for
from flask_mail import Mail, Message
import psycopg2
import requests
import os

app = Flask(__name__, template_folder='templates')
DB_PASSWORD = "Fitweball"

# --- Database connection using PostgreSQL ---
def get_db_connection():
    return psycopg2.connect(
        dbname="efds_main",
        user="postgres",
        password=os.environ.get("DB_PASSWORD"), 
        host="34.121.207.94", 
        port="5432"
    )

# --- Email configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yorkefds@gmail.com'
app.config['MAIL_PASSWORD'] = 'yyfx aqof hzou cssp' 
app.config['MAIL_DEFAULT_SENDER'] = 'yorkefds@gmail.com'

mail = Mail(app)

@app.route('/')
def home():
    return render_template('mainPage.html')
@app.route('/next')
def nextStep():
    return render_template('nextStep.html')

@app.route('/about')
def about():
    return render_template('AboutUs.html')

@app.route('/test')
def test_page():
    return render_template('testpage2.html')

@app.route('/capstone')
def capstone_page():
    return render_template('capstoneTest.html')

@app.route('/predict_fire', methods=['POST'])
def proxy_predict():
    data = request.json
    try:
        response = requests.post("https://efds-model-71702513350.us-central1.run.app/", json=data) 
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'GET':
        return render_template('login.html')

    try:
        data = request.form
        email = data.get('email')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not email or not latitude or not longitude:
            return jsonify({"message": "Email and location are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO subscribers (email, latitude, longitude) VALUES (%s, %s, %s)',
            (email, latitude, longitude)
        )
        conn.commit()
        conn.close()

        try:
            msg = Message(
                "Welcome to Our Platform!",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            msg.body = (
                f"Hello,\n\n"
                f"Thank you for subscribing to EFDS!\n\n"
                f"You have subscribed for alerts in: Latitude: {latitude}, Longitude: {longitude}\n\n"
                f"Stay safe,\nThe EFDS Team"
            )
            mail.send(msg)
        except Exception as e:
            return jsonify({"message": f"Subscription successful, but email failed: {str(e)}"}), 201

        return jsonify({
            "message": "Subscription successful! Check your email.",
            "redirect": url_for('home')
        }), 201

    except Exception as e:
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500


@app.route('/save_selection', methods=['POST'])
def save_selection():
    try:
        data = request.json  
        province = data.get('province')
        selected_date = data.get('date')

        if not province or not selected_date:
            return jsonify({"message": "Both province and date are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO user_selections (province, date) VALUES (%s, %s)',
            (province, selected_date)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Selection saved successfully!"}), 201

    except Exception as e:
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

@app.route('/send_test_email', methods=['POST'])
def send_test_email():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"message": "Email is required"}), 400

        msg = Message(
            subject="EFDS Test Alert",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
        )
        msg.body = (
            f"Hi there,\n\n"
            f"This is a one-time test email from EFDS.\n"
            f"No information has been saved — this is just for demo purposes.\n\n"
            f"Stay safe,\nThe EFDS Team"
        )
        mail.send(msg)

        return jsonify({"message": "Test email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to send email: {str(e)}"}), 500


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create subscribers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            latitude TEXT,
            longitude TEXT
        )
    ''')

    # Create user_selections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_selections (
            id SERIAL PRIMARY KEY,
            province TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/health')
def health():
    return "OK", 200

# --- Flask App Entry Point ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

