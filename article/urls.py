from django.urls import path
from .views import HandleArticle

app_name = "article"
urlpatterns = [
    path("handle/", HandleArticle.as_view(), name="handle_article"),
]