from django.urls import path
from .views import GenerateSearch, HomePage, GETAPIKEY

app_name = "gemini"
urlpatterns = [
    path("", GenerateSearch.as_view(), name="generate_search"),
    path("home", HomePage.as_view(), name="home"),
    path("getapikey", GETAPIKEY.as_view(), name="getapikey")
]
