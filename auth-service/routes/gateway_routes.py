from flask import Blueprint

gateway_bp = Blueprint("gateway", __name__)

@gateway_bp.route("/")
def home():
    return {"message": "Auth service is running"}