from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    occupation = models.CharField(max_length=50)
    bio = models.TextField()

class SocialMedia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    url = models.URLField()


