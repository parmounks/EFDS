from flask import Blueprint

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
def home():
    return '''
    <html>
        <head>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                }
                h1 {
                    font-size: 36px;
                    margin-bottom: 10px;
                }
                form {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                }
                input, button, select {
                    margin-top: 10px;
                    padding: 10px;
                    font-size: 16px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                button {
                    background-color: #007BFF;
                    color: white;
                    cursor: pointer;
                    border: none;
                }
                button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to AI-BASED EFDS!</h1>
            <p>Please select a date to view the fire detection image:</p>
            <form action="/get_image" method="get">
                <label for="date">Select Date:</label>
                <input type="date" id="date" name="date" required>

                <label for="region">Select Province:</label>
                <select id="region" name="region">
                    <option value="ontario">Ontario</option>
                    <option value="british_columbia">British Columbia</option>
                    <option value="alberta">Alberta</option>
                    <option value="quebec">Quebec</option>
                    <option value="manitoba">Manitoba</option>
                    <option value="saskatchewan">Saskatchewan</option>
                    <option value="newfoundland_and_labrador">Newfoundland and Labrador</option>
                    <option value="new_brunswick">New Brunswick</option>
                    <option value="nova_scotia">Nova Scotia</option>
                    <option value="prince_edward_island">Prince Edward Island</option>
                    <option value="northwest_territories">Northwest Territories</option>
                    <option value="nunavut">Nunavut</option>
                    <option value="yukon">Yukon</option>
                </select>

                <button type="submit">View Image</button>
            </form>
        </body>
    </html>
    '''
