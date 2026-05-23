import jwt
from django.conf import settings
from rest_framework.response import Response


def verify_token(request):
    """
    Extracts and validates Bearer JWT from Authorization header.
    Returns (payload, None) on success.
    Returns (None, Response) on failure — the view should return that Response immediately.
    """
    auth = request.headers.get("Authorization", "")
    parts = auth.split(" ")

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None, Response(
            {"error": "Authorization header must be: Bearer <token>"},
            status=401
        )

    try:
        payload = jwt.decode(parts[1], settings.JWT_SECRET, algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, Response({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return None, Response({"error": "Invalid token"}, status=401)
