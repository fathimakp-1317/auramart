from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes.auth_routes import auth_bp
from .routes.gateway_routes import gateway_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(gateway_bp)

    return app