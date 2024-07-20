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
    
class ImageArticle(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/")
    caption = models.CharField(max_length=100)
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
    
class ArticleStamp(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    count_view = models.IntegerField(default=0)
    count_comment = models.IntegerField(default=0)
    time_view = models.DateTimeField(auto_now=True)
    time_exit = models.DateTimeField(auto_now=True)
    visited_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class ArticleSentiment(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=50, default="neutral", choices=[("positive", "positive"), ("negative", "negative"), ("neutral", "neutral")])
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    