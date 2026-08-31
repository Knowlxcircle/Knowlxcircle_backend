from rest_framework import serializers

from .models import Articles, Section, Comment


class ArticleSerializer(serializers.ModelSerializer):
    """Read/write serializer for Articles.

    The field list is explicit (it used to be ``__all__``) so the payload the
    frontend receives can never change just because a column was added.  The
    views run every create/update through here, which is what turns a missing
    title or a non-integer order into a 400 instead of a 500.
    """

    class Meta:
        model = Articles
        fields = ["id", "title", "author", "created_at", "updated_at", "published"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "article", "body", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        # An empty section body has always been storable; keep it that way.
        extra_kwargs = {"body": {"allow_blank": True}}


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "article", "body", "author", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"body": {"allow_blank": True}}
