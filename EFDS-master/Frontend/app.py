from flask import Flask, request, jsonify, render_template, url_for
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__, template_folder='templates')

# Database configuration
DATABASE = 'subscribe.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'parmounk@gmail.com'
app.config['MAIL_PASSWORD'] = 'bcmn kuhj cmjx kint' 
app.config['MAIL_DEFAULT_SENDER'] = 'parmounk@gmail.com'

mail = Mail(app)

@app.route('/')
def home():
    return render_template('mainPage.html')

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
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
            print(f"Failed to send email: {str(e)}")  # Log the error
            return jsonify({"message": f"Subscription successful, but email failed: {str(e)}"}), 201

        return jsonify({
            "message": "Subscription successful! Check your email.",
            "redirect": url_for('home')
        }), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Print full error in terminal
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
        conn.commit()

    app.run(debug=True)
