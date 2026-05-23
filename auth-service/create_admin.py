"""
Run once to create the admin account.
Usage: docker compose exec auth-service python create_admin.py
"""
import os, sys
os.environ.setdefault("FLASK_APP", "app.py")

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    existing = User.query.filter_by(email="admin@shopsphere.com").first()
    if existing:
        print("Admin account already exists")
        sys.exit(0)

    admin = User(
        email    = "admin@shopsphere.com",
        password = generate_password_hash("Admin@123"),
        role     = "admin",
        name     = "ShopSphere Admin",
        phone    = "0000000000",
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin account created successfully")
    print("Email:    admin@shopsphere.com")
    print("Password: Admin@123")