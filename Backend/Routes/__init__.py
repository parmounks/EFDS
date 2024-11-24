def register_routes(app):
    from app.routes.home import home_bp
    from app.routes.get_image import get_image_bp
    from app.routes.detect import detect_bp
    from app.routes.alert import alert_bp
    from app.routes.preferences import preferences_bp
    from app.routes.process_image import process_image_bp
    from app.routes.health import health_bp
    from app.routes.report import report_bp
    from app.routes.set_region import set_region_bp
    from app.routes.endpoint import endpoint_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(get_image_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(process_image_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(set_region_bp)
    app.register_blueprint(endpoint_bp)
