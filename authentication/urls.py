from django.urls import path
from .views import Login, SignUp

app_name = "authentication"
urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("signup/", SignUp.as_view(), name="signup"),
]