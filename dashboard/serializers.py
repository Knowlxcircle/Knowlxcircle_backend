from rest_framework import serializers

from .models import Dashboard


class DashboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Dashboard
        fields = (
            "id",
            "name",
            "description",
            "user",
            "username",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
