from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=50)
    bio = models.TextField()

class SocialMedia(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    url = models.URLField()


