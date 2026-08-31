from django.db import models
from circle.models import Circle
# Create your models here.
class Articles(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    author = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Article {self.pk}"

class Section(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    body = models.TextField()
    order = models.IntegerField(db_index=True)
    # null=True so the field can be added to an existing table without an
    # interactive one-off default and without a NOT NULL backfill.
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["article", "order"], name="section_article_order_idx"),
        ]

    def __str__(self):
        return f"{self.article.title} #{self.order}"

class ImageArticle(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/")
    caption = models.CharField(max_length=100)
    order = models.IntegerField()

    def __str__(self):
        return self.caption

class Comment(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    body = models.TextField()
    author = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    # null=True: see the note on Section.created_at.
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.author

class ArticleStamp(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    count_view = models.IntegerField(default=0)
    count_comment = models.IntegerField(default=0)
    time_view = models.DateTimeField(auto_now=True)
    # time_exit used to be auto_now as well, which made it identical to
    # time_view and impossible to record an actual exit.
    time_exit = models.DateTimeField(null=True, blank=True)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["article"], name="unique_stamp_per_article"),
        ]

    def __str__(self):
        return self.article.title

class ArticleSentiment(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=50, default="neutral", choices=[("positive", "positive"), ("negative", "negative"), ("neutral", "neutral")])
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.title

class ArticleCircleAssociate(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["article", "circle"], name="unique_article_circle"),
        ]

    def __str__(self):
        return self.article.title
