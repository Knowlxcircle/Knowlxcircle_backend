from django.urls import path
from .views import HandleCircle, CreateCircle, JoinCircle, GetAllCircle, GetCircle, AssociateCircle

app_name = "circle"
urlpatterns = [
    path("handle/", HandleCircle.as_view(), name="handle_circle"),
    path("create/", CreateCircle.as_view(), name="create_circle"),
    path("join/", JoinCircle.as_view(), name="join_circle"),
    path("circles/", GetAllCircle.as_view(), name="get_all_circles"),
    path("circles/<int:id>/", GetCircle.as_view(), name="get_circles"),
    path("associate/", AssociateCircle.as_view(), name="associate_circle"),
]