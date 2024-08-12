from django.db import models
import article.models
from authentication.models import User


# Create your models here.
class Circle(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CircleMember(models.Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.role
    
class MemberSentiment(models.Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=50)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.sentiment
    
