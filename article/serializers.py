from rest_framework import serializers

from .models import Articles, Section, Comment

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = "__all__"

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"