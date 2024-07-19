from django.urls import path
from .views import HandleArticle, HandleSection, HandleComment, HandleFullArticle, HandleGeminiArticle, GetArticles

app_name = "article"
urlpatterns = [
    path("title/", HandleArticle.as_view(), name="handle_article"),
    path("section/", HandleSection.as_view(), name="handle_section"),
    path("comment/", HandleComment.as_view(), name="handle_comment"),
    path("gemini/", HandleGeminiArticle.as_view(), name="handle_gemini"),
    path("articles/<int:id>/", HandleFullArticle.as_view(), name="handle_article"),
    path("articles/", GetArticles.as_view(), name="get_articles"),
]
