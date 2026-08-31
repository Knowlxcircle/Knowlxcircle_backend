from django.contrib import admin
from .models import Articles, Section, Comment, ArticleStamp, ArticleSentiment, ImageArticle, ArticleCircleAssociate
# Register your models here.


@admin.register(Articles)
class ArticlesAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "published", "created_at")
    list_filter = ("published",)
    search_fields = ("title", "author")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "order")
    list_filter = ("article",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "author", "created_at")
    search_fields = ("author",)


@admin.register(ArticleStamp)
class ArticleStampAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "count_view", "count_comment", "time_view", "time_exit")


@admin.register(ArticleSentiment)
class ArticleSentimentAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "sentiment", "score", "created_at")
    list_filter = ("sentiment",)


@admin.register(ImageArticle)
class ImageArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "caption", "order")


@admin.register(ArticleCircleAssociate)
class ArticleCircleAssociateAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "circle")
