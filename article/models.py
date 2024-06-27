from django.db import models

# Create your models here.
class Articles(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Section(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    body = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    body = models.TextField()
    author = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title