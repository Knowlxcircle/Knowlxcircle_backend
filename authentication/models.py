from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=50, blank=True, default="")
    bio = models.TextField(blank=True, default="")

    def __str__(self):
        if self.user_id:
            return self.user.get_username()
        return f"Member {self.pk}"

class SocialMedia(models.Model):
    # NOTE: the column is called "user" but it points at Member; renaming the
    # field would mean a migration plus an API change, so only the reverse
    # accessor is corrected here.
    user = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="social_media")
    platform = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return f"{self.platform}: {self.username}"
