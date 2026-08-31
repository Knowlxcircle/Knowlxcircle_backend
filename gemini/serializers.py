from gemini.models import GeminiResponse, Prompt
from rest_framework import serializers


class GeminiResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeminiResponse
        # Explicit rather than "__all__" so a future model field cannot silently
        # widen the public API surface. Same names/order as "__all__" emits today.
        fields = ("id", "prompt", "response", "created_at", "updated_at")


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ("id", "prompt", "created_at", "updated_at")
