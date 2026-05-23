from fastapi import Header, HTTPException
import jwt, os

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-before-deploy")

def verify_token(authorization: str = Header(None)):
    """
    Validates the Bearer token from the Authorization header.
    Returns the decoded JWT payload: { sub, role, email }
    Raises 401 if missing, malformed, or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Format must be: Bearer <token>")

    try:
        payload = jwt.decode(parts[1], JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
