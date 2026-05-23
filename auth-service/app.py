from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User
from dotenv import load_dotenv
import os, time, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://admin:admin@postgres:5432/shopsphere")
app.config["JWT_SECRET_KEY"]          = os.getenv("JWT_SECRET", "change-me-before-deploy")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 hours

db.init_app(app)
jwt = JWTManager(app)

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

time.sleep(5)
with app.app_context():
    db.create_all()
    # Migration: add vendor_status column if missing
    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS vendor_status VARCHAR"))
        db.session.commit()
    except Exception as e:
        print(f"[Migration] vendor_status: {e}")
        db.session.rollback()


def send_email(to, subject, html_body):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print(f"[Email] Skipped (no credentials): {subject} → {to}")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = to
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.sendmail(EMAIL_ADDRESS, to, msg.as_string())
        print(f"[Email] Sent '{subject}' → {to}")
    except Exception as e:
        print(f"[Email] Failed: {e}")


@app.route("/hello")
def hello():
    return jsonify({"message": "Auth Service running"})


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    for field in ["email", "password", "name", "phone"]:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    role           = data.get("role", "customer")
    vendor_status  = None

    # Vendors start as pending — role stays "customer" until approved
    if role == "vendor":
        vendor_status = "pending"
        role          = "customer"   # demoted until admin approves

    user = User(
        email         = data["email"],
        password      = generate_password_hash(data["password"]),
        role          = role,
        vendor_status = vendor_status,
        name          = data["name"],
        phone         = data["phone"],
    )
    db.session.add(user)
    db.session.commit()

    resp = {"message": "Account created successfully"}
    if vendor_status == "pending":
        resp["vendor_status"] = "pending"
    return jsonify(resp), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    # Pending vendors can log in as customers but get a warning
    if user.vendor_status == "pending":
        return jsonify({"error": "Your vendor application is still under review. You can log in as a customer once approved."}), 403

    if user.vendor_status == "rejected":
        return jsonify({"error": "Your vendor application was rejected. Contact support for more information."}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role":  user.role,
            "email": user.email,
        }
    )
    return jsonify({
        "token":    token,
        "role":     user.role,
        "email":    user.email,
        "user_id":  str(user.id),
        "name":     user.name,
        "phone":    user.phone,
        "has_address": bool(user.address and user.city and user.pincode),
    })


@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "user_id": str(user.id),
        "email":   user.email,
        "role":    user.role,
        "name":    user.name    or "",
        "phone":   user.phone   or "",
        "address": user.address or "",
        "city":    user.city    or "",
        "state":   user.state   or "",
        "pincode": user.pincode or "",
        "has_address": bool(user.address and user.city and user.pincode),
    })


@app.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    if "name"    in data: user.name    = data["name"]
    if "phone"   in data: user.phone   = data["phone"]
    if "address" in data: user.address = data["address"]
    if "city"    in data: user.city    = data["city"]
    if "state"   in data: user.state   = data["state"]
    if "pincode" in data: user.pincode = data["pincode"]

    db.session.commit()
    return jsonify({
        "message":     "Profile updated",
        "has_address": bool(user.address and user.city and user.pincode),
    })


@app.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin only"}), 403

    users = User.query.all()
    return jsonify([{
        "user_id": str(u.id),
        "email":   u.email,
        "role":    u.role,
        "name":    u.name  or "",
        "phone":   u.phone or "",
    } for u in users])


# ── Vendor approval endpoints ──────────────────────────────────────────────────

@app.route("/admin/vendors/pending", methods=["GET"])
@jwt_required()
def list_pending_vendors():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin only"}), 403

    pending = User.query.filter_by(vendor_status="pending").all()
    return jsonify([{
        "user_id": str(u.id),
        "email":   u.email,
        "name":    u.name  or "",
        "phone":   u.phone or "",
    } for u in pending])


@app.route("/admin/vendors/<user_id>/approve", methods=["POST"])
@jwt_required()
def approve_vendor(user_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin only"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role          = "vendor"
    user.vendor_status = "approved"
    db.session.commit()

    send_email(
        user.email,
        "🎉 Your ShopSphere vendor application has been approved!",
        f"""
        <div style="font-family:sans-serif;max-width:560px;margin:auto;padding:32px">
          <h2 style="color:#B2456E">Welcome to ShopSphere, {user.name or 'Vendor'}!</h2>
          <p>Great news — your vendor application has been <strong>approved</strong>.</p>
          <p>You can now log in and start listing your products on ShopSphere.</p>
          <a href="http://localhost/login"
             style="display:inline-block;margin-top:16px;padding:12px 28px;background:#B2456E;color:white;border-radius:8px;text-decoration:none;font-weight:bold">
            Log in as Vendor →
          </a>
          <p style="margin-top:24px;color:#888;font-size:13px">ShopSphere Team</p>
        </div>
        """
    )
    return jsonify({"message": "Vendor approved and notified"})


@app.route("/admin/vendors/<user_id>/reject", methods=["POST"])
@jwt_required()
def reject_vendor(user_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin only"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.vendor_status = "rejected"
    db.session.commit()

    send_email(
        user.email,
        "Update on your ShopSphere vendor application",
        f"""
        <div style="font-family:sans-serif;max-width:560px;margin:auto;padding:32px">
          <h2 style="color:#552619">ShopSphere Vendor Application</h2>
          <p>Hi {user.name or 'there'},</p>
          <p>Unfortunately, your vendor application was <strong>not approved</strong> at this time.</p>
          <p>You can continue using ShopSphere as a customer. If you have questions, please contact our support team.</p>
          <p style="margin-top:24px;color:#888;font-size:13px">ShopSphere Team</p>
        </div>
        """
    )
    return jsonify({"message": "Vendor rejected and notified"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
