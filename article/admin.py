from django.contrib import admin
from .models import Articles, Section, Comment, ArticleStamp, ArticleSentiment, ImageArticle
# Register your models here.

admin.site.register(Articles)
admin.site.register(Section)
admin.site.register(Comment)
admin.site.register(ArticleStamp)
admin.site.register(ArticleSentiment)
admin.site.register(ImageArticle)
