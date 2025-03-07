from flask import Flask, request, jsonify, render_template, url_for
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__, template_folder='templates')

# Database configuration
DATABASE = 'subscribe.db'

def get_db_connection():
    """Establish a connection to the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yorkefds@gmail.com'
app.config['MAIL_PASSWORD'] = 'ztgg frvo xxui flrk' 
app.config['MAIL_DEFAULT_SENDER'] = 'yorkefds@gmail.com'

mail = Mail(app)

@app.route('/')
def home():
    """Render the main page."""
    return render_template('mainPage.html')

@app.route('/test')
def test_page():
    """Render the test page where the user selects a province and date."""
    return render_template('testPage.html')

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """Handle user subscriptions, including email notifications."""
    if request.method == 'GET':
        return render_template('login.html')

    try:
        data = request.form
        email = data.get('email')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not email:
            return jsonify({"message": "Email is required"}), 400

        if not latitude or not longitude:
            return jsonify({"message": "Location data is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subscribers (email, latitude, longitude) VALUES (?, ?, ?)', 
                       (email, latitude, longitude))
        conn.commit()
        conn.close()

        # Send welcome email
        try:
            msg = Message(
                "Welcome to Our Platform!",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )

            msg.body = (f"Hello,\n\n"
                        f"Thank you for subscribing to our Early Fire Detection System (EFDS) platform! "
                        f"We're excited to have you on board.\n\n"
                        f"You have subscribed for alerts in the following location: Latitude: {latitude}, Longitude: {longitude}\n\n"
                        f"Stay safe, and thank you for trusting EFDS to be part of your safety network.\n\n"
                        f"Best regards,\n"
                        f"The EFDS Team")

            mail.send(msg)
            print("Email sent successfully!")  # Debugging message

        except Exception as e:
            print(f"Failed to send email: {str(e)}")  
            return jsonify({"message": f"Subscription successful, but email failed: {str(e)}"}), 201

        return jsonify({
            "message": "Subscription successful! Check your email.",
            "redirect": url_for('home')
        }), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Print full error in terminal
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

@app.route('/save_selection', methods=['POST'])
def save_selection():
    """Receive user-selected province and date and store them in the database."""
    try:
        data = request.json  
        province = data.get('province')
        selected_date = data.get('date')

        if not province or not selected_date:
            return jsonify({"message": "Both province and date are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_selections (province, date) VALUES (?, ?)', (province, selected_date))
        conn.commit()
        conn.close()

        return jsonify({"message": "Selection saved successfully!"}), 201

    except Exception as e:
        return jsonify({"message": f"Internal Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

      
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                latitude TEXT,
                longitude TEXT
            )
        ''')

      
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                province TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')

        conn.commit()

    app.run(debug=True)
