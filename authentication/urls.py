from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, LoginView, RegisterMember
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('register-member/', RegisterMember.as_view(), name='register_member'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]