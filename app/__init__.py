from flask import Flask
from app.services.scheduler import init_scheduler

def create_app():
    app = Flask(__name__)

    # Initialize background scheduler
    init_scheduler()

    # Register routes
    with app.app_context():
        from app.routes import register_routes
        register_routes(app)

    return app
