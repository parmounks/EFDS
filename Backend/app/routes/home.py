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
                }
                h1 {
                    font-size: 48px;
                }
                form {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                input, button {
                    margin-top: 10px;
                    padding: 10px;
                    font-size: 18px;
                }
            </style>
            <script>
                function toggleDateInput() {
                    var specificDateInputs = document.getElementById('specificDateInputs');
                    if (document.getElementById('specific').checked) {
                        specificDateInputs.style.display = 'block';
                    } else {
                        specificDateInputs.style.display = 'none';
                    }
                }
            </script>
        </head>
        <body>
            <h1>Welcome to AI-BASED EFDS!</h1>
            <p>Select "Live" to view the latest image or "Specific Date" to choose a date:</p>
            <form action="/get_image" method="get">
                <label>
                    <input type="radio" name="type" value="live" id="live" onclick="toggleDateInput()" checked>
                    Live
                </label>
                <label>
                    <input type="radio" name="type" value="specific" id="specific" onclick="toggleDateInput()">
                    Specific Date
                </label>

                <div id="specificDateInputs" style="display: none;">
                    <label for="date">Date:</label>
                    <input type="date" id="date" name="date">
                </div>

                <button type="submit">View Image</button>
            </form>
        </body>
    </html>
    '''
