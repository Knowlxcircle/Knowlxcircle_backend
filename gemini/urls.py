from django.urls import path
from .views import GenerateSearch

app_name = "gemini"
urlpatterns = [
    path("", GenerateSearch.as_view(), name="generate_search"),
]
