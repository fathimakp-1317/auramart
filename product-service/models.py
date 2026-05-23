from sqlalchemy import Column, String, Float, Integer, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from database import Base
import uuid

class Category(Base):
    __tablename__ = "categories"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name        = Column(String, nullable=False)
    parent_id   = Column(String, nullable=True)

class Product(Base):
    __tablename__ = "products"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name         = Column(String, nullable=False)
    description  = Column(String, default="")
    price        = Column(Float, nullable=False)
    vendor_id    = Column(String, nullable=False)
    category_id  = Column(String, nullable=True)
    stock        = Column(Integer, default=0)
    avg_rating   = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    images       = Column(Text, default="[]")   # JSON array of base64 strings, 1–3
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class Review(Base):
    __tablename__ = "reviews"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, nullable=False)
    user_id    = Column(String, nullable=False)
    user_name  = Column(String, nullable=False)
    title      = Column(String, nullable=False)
    comment    = Column(Text, nullable=False)
    rating     = Column(Integer, nullable=False)   # 1–5
    photo_urls = Column(Text, default="[]")        # JSON-encoded list, optional
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("product_id", "user_id", name="uq_review_product_user"),
    )
