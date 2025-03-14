import jwt
import pytest
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from genaibackend.users.authentication import JWTAuthentication
from genaibackend.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser", password="password")


@pytest.fixture
def valid_token(user):
    payload = {"user_id": user.id}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


@pytest.fixture
def expired_token(user, mocker):
    mocker.patch("jwt.decode", side_effect=jwt.ExpiredSignatureError)
    payload = {"user_id": user.id}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


@pytest.fixture
def invalid_token():
    return "invalid.token.value"


def test_jwt_authenticate_valid_token(valid_token, user, rf):
    request = rf.get("/")
    request.META["HTTP_AUTHORIZATION"] = f"Bearer {valid_token}"
    auth = JWTAuthentication()
    authenticated_user, _ = auth.authenticate(request)
    assert authenticated_user == user


def test_jwt_authenticate_missing_header(rf):
    request = rf.get("/")
    auth = JWTAuthentication()
    assert auth.authenticate(request) is None


def test_jwt_authenticate_invalid_format(rf):
    request = rf.get("/")
    request.META["HTTP_AUTHORIZATION"] = "InvalidTokenFormat"
    auth = JWTAuthentication()
    with pytest.raises(
        AuthenticationFailed, match="Authorization header must be Bearer token"
    ):
        auth.authenticate(request)


def test_jwt_authenticate_expired_token(expired_token, rf):
    request = rf.get("/")
    request.META["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"
    auth = JWTAuthentication()
    with pytest.raises(AuthenticationFailed, match="Token has expired"):
        auth.authenticate(request)


def test_jwt_authenticate_invalid_token(invalid_token, rf):
    request = rf.get("/")
    request.META["HTTP_AUTHORIZATION"] = f"Bearer {invalid_token}"
    auth = JWTAuthentication()
    with pytest.raises(AuthenticationFailed, match="Invalid token"):
        auth.authenticate(request)
