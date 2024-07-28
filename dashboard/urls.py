from django.urls import path
from .views import HandleDashboard, GetDashboard

app_name = "dashboard"
urlpatterns = [
    path("handle/", HandleDashboard.as_view(), name="handle_dashboard"),
    path("get/", GetDashboard.as_view(), name="get_dashboard")
]