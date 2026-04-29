from app.extensions import db
from datetime import datetime

class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)