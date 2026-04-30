from flask import Flask
from app.config import Config
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.recommendation_routes import recommendation_bp
    app.register_blueprint(recommendation_bp, url_prefix="/api/recommendations")

    @app.route("/")
    def home():
        return {"status": "ShopSphere Recommendation Service Running"}

    return app