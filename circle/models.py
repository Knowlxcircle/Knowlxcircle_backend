from django.conf import settings
from django.db import models


# Create your models here.
class Circle(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name or f"Circle {self.pk}"

class CircleMember(models.Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="circle_memberships"
    )
    role = models.CharField(max_length=50, blank=True, default="member")

    class Meta:
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(fields=["circle", "user"], name="unique_circle_member"),
        ]

    def __str__(self):
        return f"CircleMember {self.pk} ({self.role or 'member'})"
    
class MemberSentiment(models.Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="sentiments")
    sentiment = models.CharField(max_length=50, default="neutral")
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return self.sentiment or "neutral"
