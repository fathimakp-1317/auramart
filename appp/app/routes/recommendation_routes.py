from app.models import UserInteraction, Recommendation, TrendingProduct
from app.extensions import db

class RecommendationService:

    def get_user_recommendations(self, user_id):
        recs = Recommendation.query.filter_by(user_id=user_id).all()
        return [{"product_id": r.product_id, "score": r.score} for r in recs]

    def add_interaction(self, data):
        interaction = UserInteraction(
            user_id=data["user_id"],
            product_id=data["product_id"],
            interaction_type=data.get("interaction_type", "view")
        )
        db.session.add(interaction)
        db.session.commit()
        return {"message": "Interaction added"}

    def get_trending_products(self):
        trending = TrendingProduct.query.order_by(
            TrendingProduct.score.desc()
        ).limit(10).all()

        return [{"product_id": t.product_id, "score": t.score} for t in trending]