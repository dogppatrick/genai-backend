from rest_framework import serializers

from .models import BaseModel


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = tuple()

    def create(self, validated_data):
        new_instance, _ = self.Meta.model.objects.get_or_create(**validated_data)
        return new_instance
