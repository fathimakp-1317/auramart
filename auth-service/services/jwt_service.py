import jwt
import datetime
import os

SECRET = os.getenv("SECRET_KEY")

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return data
    except:
        return None