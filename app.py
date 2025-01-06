from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
import sqlite3

app = Flask(__name__)

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
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'parmounk@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'bcmn kuhj cmjx kint'     # App password
app.config['MAIL_DEFAULT_SENDER'] = 'parmounk@gmail.com'

mail = Mail(app)

@app.route('/')
def home():
    return render_template('webframe.html')  # Main page

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')

        if email:
            # Save email to the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
            conn.commit()
            conn.close()

            # Send welcome email
            try:
                msg = Message(
                    "Welcome to Our Platform!",
                    sender="parmounk@gmail.com",  # Explicit sender
                    recipients=[email]
                )
                msg.body = f"Hello,\n\nThank you for subscribing to our platform! We're excited to have you on board. Stay tuned for updates and notifications."
                mail.send(msg)
            except Exception as e:
                return jsonify({"message": f"Subscription successful, but email sending failed: {str(e)}"}), 201

            return jsonify({"message": "Subscription successful! Check your email for a welcome message."}), 201

        return jsonify({"message": "Email is required"}), 400

    # If it's a GET request, serve the signup page
    return render_template('login.html')

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL
        )
        ''')
        conn.commit()

    app.run(debug=True)
