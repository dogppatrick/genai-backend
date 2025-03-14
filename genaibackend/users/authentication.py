import jwt
from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Authorization header must be Bearer token")

        token = parts[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user = User.objects.get(id=payload["user_id"])
        return (user, None)


class JWTBearerAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "genaibackend.users.authentication.JWTAuthentication"
    name = "JWTAuth"

    def get_security_definition(self, generator):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
