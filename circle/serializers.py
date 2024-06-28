from rest_framework import serializers

from .models import Circle, CircleMember

class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = "__all__"

class CircleMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleMember
        fields = "__all__"