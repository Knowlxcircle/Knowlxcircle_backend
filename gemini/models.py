from django.db import models


def _truncate(value, limit=80):
    """Short, safe representation for __str__ (bodies can be many KB)."""
    text = (value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


# Create your models here
class Prompt(models.Model):
    prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return _truncate(self.prompt)


class GeminiResponse(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return _truncate(self.response)
