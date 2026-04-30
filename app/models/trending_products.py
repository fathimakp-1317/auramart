from app.extensions import db

class TrendingProduct(db.Model):
    __tablename__ = "trending_products"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float)