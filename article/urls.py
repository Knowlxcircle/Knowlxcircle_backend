from django.urls import path
from .views import HandleArticle, HandleSection, HandleComment, HandleFullArticle, HandleGeminiArticle, GetArticles, SearchArticle

app_name = "article"
urlpatterns = [
    path("title/", HandleArticle.as_view(), name="handle_article"),
    path("section/", HandleSection.as_view(), name="handle_section"),
    path("comment/", HandleComment.as_view(), name="handle_comment"),
    path("gemini/", HandleGeminiArticle.as_view(), name="handle_gemini"),
    # The frontend deletes via .../gemini/<id> with no trailing slash; both
    # variants are registered so APPEND_SLASH cannot redirect the DELETE away.
    path("gemini/<int:id>", HandleGeminiArticle.as_view(), name="handle_gemini_detail"),
    path("gemini/<int:id>/", HandleGeminiArticle.as_view(), name="handle_gemini_detail_slash"),
    path("articles/", GetArticles.as_view(), name="get_articles"),
    # Used to be named "handle_article" as well, which collided with title/.
    path("articles/<int:id>/", HandleFullArticle.as_view(), name="handle_full_article"),
    path("articles/<int:id>", HandleFullArticle.as_view(), name="handle_full_article_no_slash"),
    path("search/", SearchArticle.as_view(), name="search_article"),
    path("search", SearchArticle.as_view(), name="search_article_no_slash"),
]
