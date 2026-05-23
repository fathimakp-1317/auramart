from database import db
import uuid

class User(db.Model):
    __tablename__ = "users"

    id       = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email    = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role     = db.Column(db.String, default="customer")

    # vendor_status: None=customer, "pending"=awaiting approval, "approved"=active vendor, "rejected"=rejected
    vendor_status = db.Column(db.String, nullable=True)

    # Profile fields
    name     = db.Column(db.String, nullable=True)
    phone    = db.Column(db.String, nullable=True)
    address  = db.Column(db.String, nullable=True)
    city     = db.Column(db.String, nullable=True)
    state    = db.Column(db.String, nullable=True)
    pincode  = db.Column(db.String, nullable=True)
