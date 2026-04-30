from app.extensions import db
from datetime import datetime

class UserInteraction(db.Model):
    __tablename__ = "user_interactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    interaction_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)