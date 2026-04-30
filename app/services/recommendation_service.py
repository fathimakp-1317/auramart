from flask import Blueprint, request, jsonify
from app.services.recommendation_service import RecommendationService

recommendation_bp = Blueprint("recommendation", __name__)
service = RecommendationService()

@recommendation_bp.route("/<int:user_id>", methods=["GET"])
def get_recommendations(user_id):
    return jsonify(service.get_user_recommendations(user_id))


@recommendation_bp.route("/interaction", methods=["POST"])
def add_interaction():
    return jsonify(service.add_interaction(request.json))


@recommendation_bp.route("/trending", methods=["GET"])
def get_trending():
    return jsonify(service.get_trending_products())