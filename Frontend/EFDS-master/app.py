<<<<<<< HEAD
from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from flask import Flask, request, jsonify, render_template, url_for 
import sqlite3

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

    data = request.form
    email = data.get('email')
    locations = data.get('selected_locations')  # Corrected field name

    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subscribers (email, locations) VALUES (?, ?)', (email, locations))
        conn.commit()
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

    # Send welcome email
    try:
        msg = Message(
            "Welcome to Our Platform!",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.body = (f"Hello,\n\nThank you for subscribing! "
                        f"We're excited to have you on board.\n\n"
                        f"You have subscribed for alerts in the following locations: {locations}\n\n"
                        f"Stay safe, and thank you for trusting EFDS to be part of your safety network.\n\n"
                        f"Best regards,\n"
                        f"The EFDS Team")
        mail.send(msg)
    except Exception as e:
        return jsonify({"message": f"Subscription successful, but email failed: {str(e)}"}), 201

    return jsonify({
        "message": "Subscription successful! Check your email.",
        "redirect": url_for('home') }), 201
if __name__ == '__main__':
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                locations TEXT
            )
        ''')
        conn.commit()
=======
from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from flask import Flask, request, jsonify, render_template, url_for 
import sqlite3

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

    data = request.form
    email = data.get('email')
    locations = data.get('selected_locations')  # Corrected field name

    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subscribers (email, locations) VALUES (?, ?)', (email, locations))
        conn.commit()
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

    # Send welcome email
    try:
        msg = Message(
            "Welcome to Our Platform!",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.body = (f"Hello,\n\nThank you for subscribing! "
                        f"We're excited to have you on board.\n\n"
                        f"You have subscribed for alerts in the following locations: {locations}\n\n"
                        f"Stay safe, and thank you for trusting EFDS to be part of your safety network.\n\n"
                        f"Best regards,\n"
                        f"The EFDS Team")
        mail.send(msg)
    except Exception as e:
        return jsonify({"message": f"Subscription successful, but email failed: {str(e)}"}), 201

    return jsonify({
        "message": "Subscription successful! Check your email.",
        "redirect": url_for('home') }), 201
if __name__ == '__main__':
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                locations TEXT
            )
        ''')
        conn.commit()
>>>>>>> 46bb4dc (Frontend update cloud)
    app.run(debug=True)