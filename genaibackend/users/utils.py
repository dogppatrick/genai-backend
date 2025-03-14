from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings


def generate_jwt(user):
    expiration = datetime.now(UTC) + timedelta(days=1)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": expiration,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token
