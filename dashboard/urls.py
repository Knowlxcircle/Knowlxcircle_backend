from django.urls import path
from .views import HandleDashboard

app_name = "dashboard"
urlpatterns = [
    path("handle/", HandleDashboard.as_view(), name="handle_dashboard"),
]