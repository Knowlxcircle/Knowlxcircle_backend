from gemini.models import GeminiResponse, Prompt
from rest_framework import serializers

class GeminiResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeminiResponse
        fields = "__all__"
    
class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = "__all__" 