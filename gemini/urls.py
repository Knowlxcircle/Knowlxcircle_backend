from django.urls import path
from .views import GenerateSearch, HomePage, ChatPage, ChatPageDetail

app_name = "gemini"
urlpatterns = [
    path("", GenerateSearch.as_view(), name="generate_search"),
    path("home", HomePage.as_view(), name="home"),
    path("chat/", ChatPage.as_view(), name="chat"),
    # path("getapikey", GETAPIKEY.as_view(), name="getapikey")
    path("chat/<int:id>", ChatPageDetail.as_view(), name="chat")
]
