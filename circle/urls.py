from django.urls import path
from .views import HandleCircle

app_name = "circle"
urlpatterns = [
    path("handle/", HandleCircle.as_view(), name="handle_circle"),
]