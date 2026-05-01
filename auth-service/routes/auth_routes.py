from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from app.services.jwt_service import create_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing data"}), 400

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"})


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data.get("email")).first()

    if not user or user.password != data.get("password"):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_token(user.id)

    return jsonify({"token": token})