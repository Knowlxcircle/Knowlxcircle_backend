from rest_framework import serializers

from .models import Circle, CircleMember, MemberSentiment

class CircleSerializer(serializers.ModelSerializer):
    # A blank description is accepted today, so keep it optional; only the name
    # is genuinely required.
    description = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = Circle
        fields = "__all__"

class CircleMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = CircleMember
        fields = ("id", "circle", "user", "username", "role")

class MemberSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberSentiment
        fields = ("id", "circle", "sentiment", "score", "created_at")
