from django.urls import path
from .views import GenerateSearch, HomePage, ChatPage, ChatPageDetail
from article.views import SearchArticle

app_name = "gemini"
urlpatterns = [
    path("", GenerateSearch.as_view(), name="generate_search"),
    # The frontend calls some of these without a trailing slash; register both
    # spellings so APPEND_SLASH cannot turn a POST/DELETE into a broken redirect.
    path("home", HomePage.as_view(), name="home"),
    path("home/", HomePage.as_view(), name="home"),
    path("chat/", ChatPage.as_view(), name="chat"),
    path("chat/<int:id>", ChatPageDetail.as_view(), name="chat_detail"),
    path("chat/<int:id>/", ChatPageDetail.as_view(), name="chat_detail"),
    path("search/", SearchArticle.as_view(), name="search_article"),
]
