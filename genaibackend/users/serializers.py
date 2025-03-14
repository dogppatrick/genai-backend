from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=200)
    password = serializers.CharField(required=True, max_length=200)


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
